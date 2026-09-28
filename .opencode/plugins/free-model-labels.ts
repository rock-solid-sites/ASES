/**
 * Free Model Labels — OpenCode Native TypeScript Plugin
 *
 * Annotates the model picker with each model's provider, free status, tool-calling
 * support and evidence freshness, so a model can be chosen with its real
 * capabilities visible instead of inferred from its name.
 *
 * WHY THIS EXISTS
 *
 * Model names are not unique across providers. In the catalog this plugin reads,
 * 58 names appear on more than one provider, and `nemotron-3-ultra` alone resolves
 * to five refs across four providers whose tool-calling support differs — one is
 * tool-capable, one is measurably tool-blind. Availability belongs to
 * (model, route), not to the model: on 2026-09-28 the same model served normally
 * via one provider and returned `Rate limit exceeded: free-models-per-day-stealth`
 * via another, in the same minute on the same host.
 *
 * A document does not fix this. A doc has to be read *before* the wrong mapping
 * forms. The picker entry is read at the moment the choice is made, so the
 * disambiguation goes there:
 *
 *     Nemotron 3 Ultra Free      · OpenCode Zen   · tools OK
 *     Nemotron 3 Ultra 550B      · NVIDIA NIM     · NO tool calls
 *     Nemotron 3 Ultra 550B      · OpenRouter     · tools unverified (inferred)
 *
 * TWO PROPERTIES THIS FILE IS BUILT AROUND
 *
 * 1. DERIVE, NEVER HARDCODE. Every provider name, free status, tool verdict and
 *    staleness figure is read from the catalog at runtime. There is deliberately
 *    no table of model facts in this file. The catalog is re-verified on a
 *    schedule and changes without anyone editing this plugin, so a hardcoded list
 *    would be a claim that decays silently. Adding a row to the catalog changes
 *    the picker with no edit here.
 *
 * 2. ANNOTATE, NEVER REMOVE. Model availability on a free tier is a moving
 *    target, and redundancy across providers is worth keeping as a fallback. This
 *    plugin's job is to make a choice legible, not to take choices away. Removals
 *    are available but OFF by default (see the configuration block) because a
 *    provider ban or a model whitelist is a *host* policy decision, not something
 *    a shared plugin should impose.
 *
 * SAFETY
 *
 *   - The catalog is read once, before the transform. The transform does no I/O:
 *     no writes, no network, no processes.
 *   - Any problem reading or interpreting the catalog yields `null` and the model
 *     list is left exactly as the catalog built it. Fail open, always.
 *   - `editor.model.update()` CREATES an entry that is absent from the draft, so
 *     every update is preceded by a `get()`. Without that guard, annotating a
 *     model that a removal just deleted silently resurrects it.
 *
 * CONFIGURATION (all optional; with none set this plugin only annotates)
 *
 *   OPENCODE_FREEMODELS_CATALOG       catalog JSON path
 *                                     default ~/.local/share/opencode-docs/free-models.json
 *   OPENCODE_FREEMODELS_HIDE_PROVIDERS  comma-separated provider ids to remove
 *   OPENCODE_FREEMODELS_FORBIDDEN_MODELS  comma-separated case-insensitive substrings
 *                                     or /regex/ to remove
 *   OPENCODE_FREEMODELS_ZEN_WHITELIST   comma-separated model ids to keep on the
 *                                     `opencode` provider; empty means keep all
 *
 * @module free-model-labels
 */

import { readFileSync } from "node:fs"
import { homedir } from "node:os"
import { join } from "node:path"

/* ------------------------------------------------------------------ config */

const envList = (name: string): string[] =>
  (process.env[name] ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)

/** Providers removed from the model list. Empty unless a host opts in. */
export const HIDE_PROVIDERS: string[] = envList("OPENCODE_FREEMODELS_HIDE_PROVIDERS")

/** Case-insensitive substrings or /regex/ whose matches are removed. */
export const FORBIDDEN_MODEL_PATTERNS: RegExp[] = envList("OPENCODE_FREEMODELS_FORBIDDEN_MODELS").map(
  (raw) => {
    const asRegex = /^\/(.*)\/([a-z]*)$/.exec(raw)
    try {
      // `i` is appended to any operator-supplied flags rather than passed as a
      // third argument: RegExp takes only (pattern, flags), and
      // case-insensitivity is the point of the match.
      const flags = (asRegex?.[2] ?? "") + "i"
      return asRegex ? new RegExp(asRegex[1]!, flags) : new RegExp(escape(raw), "i")
    } catch {
      // A malformed pattern must not take down model selection.
      return /$^/
    }
  },
)

export const isForbiddenModel = (name: string): boolean =>
  FORBIDDEN_MODEL_PATTERNS.some((re) => re.test(name))

function escape(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

/** Model ids kept on the `opencode` provider. Empty means keep everything. */
export const ZEN_WHITELIST: string[] = envList("OPENCODE_FREEMODELS_ZEN_WHITELIST")

/** The verified free-model catalog. Overridable so the failure path is testable. */
export const FREEMODELS_PATH: string =
  process.env.OPENCODE_FREEMODELS_CATALOG ||
  join(homedir(), ".local/share/opencode-docs/free-models.json")

/* ------------------------------------------------------------------ labels */

/**
 * The `$contract` keys this file reads. A document that no longer documents all
 * of them is not the document this code was written against, so it is ignored
 * rather than half-understood. This is a schema key list, not model data.
 */
const CONTRACT_FIELDS = [
  "free",
  "tools",
  "tools_confidence",
  "free_verified_on",
  "tools_verified_on",
]

const SEP = "\u0000"
const labelKey = (providerID: string, id: string): string => providerID + SEP + id

/** First positive finite number, else 0. TTLs are per-model or per-class. */
function hours(...values: unknown[]): number {
  for (const value of values)
    if (typeof value === "number" && Number.isFinite(value) && value > 0) return value
  return 0
}

/** "3h" / "2.1d" -- compact enough for a one-line picker entry. */
function age(ms: number): string {
  const h = ms / 3_600_000
  return h < 48 ? `${Math.round(h)}h` : `${(h / 24).toFixed(1)}d`
}

/** Ms past a TTL, or 0 when fresh -- or when there is no TTL to be past. */
function overdue(verifiedOn: unknown, ttlHours: number, now: number): number {
  if (!ttlHours) return 0
  const at = typeof verifiedOn === "string" ? Date.parse(verifiedOn) : Number.NaN
  if (!Number.isFinite(at)) return 0
  const elapsed = now - at
  return elapsed > ttlHours * 3_600_000 ? elapsed : 0
}

/**
 * One catalog row -> the suffix appended to the catalog's own model name.
 * Empty string when the row has nothing worth showing.
 */
function labelFor(provider: any, row: any, freshness: any, now: number): string {
  if (!provider || typeof provider.id !== "string" || !row || typeof row.id !== "string") return ""
  // Provider in full, never a bare short name. Fall back to the id only if unnamed.
  const name =
    typeof provider.name === "string" && provider.name.trim() ? provider.name.trim() : provider.id

  const parts: string[] = [name]

  // free: true | false | reason string. A reason means NOT free, in the provider's
  // own words. free:true adds nothing here -- being annotated at all means the row
  // is in the verified-free catalog.
  if (row.free !== true) {
    const reason = typeof row.free === "string" ? row.free : row.free_reason
    parts.push(typeof reason === "string" && reason ? `NOT free (${reason})` : "NOT free")
  }

  // tools, measured on this row's own serving path, not on the weights. Most rows
  // have never been probed, so say so rather than letting an unprobed row read as
  // a verdict: an untested claim that looks settled is the failure this exists to
  // prevent.
  const verdict =
    row.tools === "yes" ? "tools OK" : row.tools === "no" ? "NO tool calls" : "tools unverified"
  const toolsStale = overdue(
    row.tools_verified_on,
    hours(row.tools_ttl_hours, freshness?.tools_ttl_hours),
    now,
  )
  let tools = verdict
  if (verdict === "tools unverified") {
    tools += row.tools_confidence === "inferred" ? " (inferred, not probed here)" : " (unprobed)"
  } else if (toolsStale) {
    tools += ` (stale ${age(toolsStale)})`
  } else if (
    typeof row.tools_verified_on !== "string" ||
    !Number.isFinite(Date.parse(row.tools_verified_on))
  ) {
    tools += " (undated)"
  }
  parts.push(tools)

  // Availability, against the provider's volatility class.
  const freeStale = overdue(
    row.free_verified_on,
    hours(row.free_ttl_hours, provider.default_ttl_hours, freshness?.availability_ttl_hours?.[provider.id]),
    now,
  )
  if (row.free === true && freeStale) parts.push(`free stale ${age(freeStale)}`)

  return " · " + parts.join(" · ")
}

/**
 * Read the catalog and return `${providerID}\u0000${id}` -> label suffix, or null if
 * it cannot be used. Never throws: a plugin that throws must not be able to take
 * down model selection.
 */
export function loadFreeModelLabels(
  path: string = FREEMODELS_PATH,
  now: number = Date.now(),
): Map<string, string> | null {
  try {
    const doc = JSON.parse(readFileSync(path, "utf8"))
    if (!doc || typeof doc !== "object") return null
    if (!doc.$contract || typeof doc.$contract !== "object") return null
    if (!CONTRACT_FIELDS.every((field) => typeof doc.$contract[field] === "string")) return null
    if (!Array.isArray(doc.providers)) return null

    const labels = new Map<string, string>()
    for (const provider of doc.providers) {
      if (!provider || typeof provider.id !== "string" || !Array.isArray(provider.models)) continue
      for (const row of provider.models) {
        const suffix = labelFor(provider, row, doc.freshness, now)
        if (!suffix) continue
        // Catalog ids and upstream model ids differ per provider (nvidia rows
        // carry their own prefix, openrouter rows carry ":free"), so index both
        // spellings. Exact matches only: a fuzzy match here would put a free
        // label on a paid route.
        labels.set(labelKey(provider.id, row.id), suffix)
        labels.set(labelKey(provider.id, `${provider.id}/${row.id}`), suffix)
      }
    }
    return labels.size > 0 ? labels : null
  } catch {
    return null
  }
}

/** Suffix for one catalog entry, or "" when the catalog has no row for it. */
function lookupLabel(labels: Map<string, string>, model: any): string {
  const pid = model?.providerID
  if (typeof pid !== "string") return ""
  const candidates = [
    model.modelID,
    model.id,
    model.modelID && `${pid}/${model.modelID}`,
    model.id && `${pid}/${model.id}`,
  ]
  for (const id of candidates) {
    if (typeof id !== "string") continue
    const hit = labels.get(labelKey(pid, id))
    if (hit) return hit
  }
  return ""
}

/* ------------------------------------------------------------------ plugin */

/**
 * Register the policy. Call from setup(); registrations are disposed
 * automatically when the plugin unloads.
 */
export async function applyModelPolicy(ctx: any): Promise<void> {
  // In this beta, provider.list() exposes empty per-provider model maps. The
  // separate async model.list() API is the authoritative catalog of model IDs.
  const result = await ctx.catalog.model.list()
  const models: any[] = Array.isArray(result) ? result : result?.data
  if (!Array.isArray(models)) throw new Error("Unexpected catalog.model.list() result")

  // Read the label source once, before the transform. The transform itself does no
  // I/O at all: no writes, no network, no processes.
  const labels = loadFreeModelLabels()

  await ctx.catalog.transform((editor: any) => {
    try {
      for (const { provider } of editor.provider.list()) {
        if (HIDE_PROVIDERS.includes(provider.id)) editor.provider.remove(provider.id)
      }

      for (const model of models) {
        const modelID = model.id ?? model.modelID
        if (!modelID) continue
        if (isForbiddenModel(modelID)) {
          editor.model.remove(model.providerID, modelID)
          continue
        }
        if (ZEN_WHITELIST.length && model.providerID === "opencode" && !ZEN_WHITELIST.includes(modelID)) {
          editor.model.remove(model.providerID, modelID)
        }
      }

      // Annotate, never remove. The picker shows `model.name` as the entry title,
      // so appending here is what reaches the agent at choice time.
      if (labels && typeof editor?.model?.get === "function" && typeof editor?.model?.update === "function") {
        for (const model of models) {
          const suffix = lookupLabel(labels, model)
          if (!suffix) continue
          const modelID = model.id ?? model.modelID
          if (!modelID) continue
          // editor.model.update() CREATES an entry that is absent from the draft,
          // so never call it for a model the removals above just deleted.
          if (!editor.model.get(model.providerID, modelID)) continue
          editor.model.update(model.providerID, modelID, (draft: any) => {
            const base = String(draft?.name || model.name || modelID).trim()
            if (!base || base.endsWith(suffix)) return
            draft.name = base + suffix
          })
        }
      }
    } catch {
      // Fail open. This file must not be able to break model selection, so a
      // throw here is swallowed and the untransformed list stands.
    }
  })
}

export default {
  id: "opencode.free-model-labels",
  async setup(ctx: any) {
    await applyModelPolicy(ctx)
  },
}
