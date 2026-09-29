# Design: `free-model-labels.ts` — OpenCode Free-Model Picker Annotation Plugin

**Status:** Implemented
**Date:** 2026-09-28
**Author:** Implementation session (OpenCode Zen free-tier catalog work)
**Canonical Location:** `.opencode/design/free-model-labels-design.md`
**Target Implementation:** `.opencode/plugins/free-model-labels.ts`
**Research basis:** `~/.local/share/opencode-docs/free-models.md` (host-local, not committed)

---

## 1. Overview

`free-model-labels.ts` annotates the OpenCode model picker so that each entry
carries its provider, free status, tool-calling support, and evidence freshness.
It exists because model names are not unique across providers, and because the
same weights behave differently depending on which provider serves them.

**This is an implementation-layer plugin.** It is bound to OpenCode, TypeScript,
and a specific catalog schema. It is deliberately kept out of methodology and
research documents: the reasoning is recorded here as reasoning, not promoted to
project direction.

### The problem, stated precisely

In the catalog this plugin reads, 58 model names appear on more than one
provider, and `nemotron-3-ultra` alone resolves to five refs across four
providers whose tool-calling support differs:

| exact ref | provider | tool calls |
|---|---|---|
| `opencode/nemotron-3-ultra-free` | OpenCode Zen | **yes** (measured) |
| `nvidia/nvidia/nemotron-3-ultra-550b-a55b` | NVIDIA NIM | **no** (measured) |
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | unverified (inferred) |
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b` | OpenRouter (paid) | unverified |
| `ollama-cloud/nemotron-3-ultra` | Ollama Cloud | unverified |

So availability belongs to **(model, route)**, never to the model alone. Measured
on 2026-09-28, on one host, in the same minute: `opencode/space-bunny-free`
served normally while `openrouter/stealth/space-bunny-alpha` returned
`Rate limit exceeded: free-models-per-day-stealth`. Same model, opposite
outcomes, decided entirely by which provider the ref named.

### Why a plugin rather than a document

A document helps only if it is read *before* the wrong mapping forms. A picker
entry is read at the moment the choice is made, so the disambiguation goes where
the decision happens. This is not hypothetical: two agents confused OpenCode Zen
with OpenRouter while a document spelling the difference out was available to
them.

## 2. Key properties

| Property | Value |
|---|---|
| Derives all model facts from the catalog at runtime | Yes — no table of model facts in source |
| Annotates only; removes nothing by default | Yes — removals require explicit opt-in |
| xAI/Grok prohibition hard-coded and non-configurable | Yes — see §2.1 |
| Zen whitelist configurable | Yes — empty by default |
| Filesystem writes inside the transform | None — the catalog is read once, before it |
| Network calls | None |
| Fails open | Yes — any catalog problem leaves the list untouched |
| New TypeScript errors introduced | 0 (verified against the repo's `tsconfig.json`) |

### 2.1 The xAI prohibition is an invariant, not a preference

**xAI/Grok is strictly and permanently forbidden, and this plugin inherits that
prohibition.** It is hard-coded in source and is deliberately NOT
environment-driven. If a future edit makes it configurable, the prohibition is no
longer a prohibition.

**INVARIANT: if any xAI or Grok entry appears in the model list, the plugin is
broken.** It is not a preference the operator changed, and not a new upstream
model. It means the catalog transform threw, the editor API changed shape, or
this guard was edited. Treat the appearance of a grok or xai entry as a canary
that the transform is not doing its job.

This is categorically different from the two configurable removals, and the
distinction is the point:

| | xAI/Grok | `HIDE_PROVIDERS` | `ZEN_WHITELIST` |
|---|---|---|---|
| Nature | Invariant | Tidiness preference | Volatile snapshot |
| Configurable | **Never** | Yes, default empty | Yes, default empty |
| If it drifts | Something is broken | A choice changed | A stale list |
| Wrong by default | Unacceptable | Acceptable | Acceptable |

**Both a provider-id block and a model-pattern sweep are required.** A
provider-only block is not sufficient. As of 2026-09-28 the catalog contains no
dedicated `xai` provider at all — the xAI models surface on *other* providers,
as `opencode-go/grok-4.5` and `openrouter/x-ai/grok-4.5`. The pattern sweep runs
over the whole active model collection regardless of provider, and that is what
closes the hole. The provider-id list remains as a forward-looking net in case a
first-party xAI provider is ever added.

### Why the Zen whitelist is configurable but the ban is not

The Zen free set is documented as free *for a limited time* and changes
underneath any list pinned in source. A hardcoded whitelist is a snapshot that
goes quietly stale, and a stale whitelist removes models the operator still
wants — a silent, one-directional failure. The original working copy hardcoded 8
model ids; here the list is environment-driven and empty by default, so a host
opts in and can update it without editing this file.

That is the distinction in one line: **a list that changes is configuration; a
rule that does not is code.**

## 3. Configuration

All optional. With none set, the plugin annotates and removes nothing.

| Variable | Purpose | Default |
|---|---|---|
| `OPENCODE_FREEMODELS_CATALOG` | Catalog JSON path | `~/.local/share/opencode-docs/free-models.json` |
| `OPENCODE_FREEMODELS_HIDE_PROVIDERS` | Comma-separated provider ids to remove for tidiness | empty |
| `OPENCODE_FREEMODELS_ZEN_WHITELIST` | Comma-separated model ids to keep on `opencode` | empty (keep all) |

**No variable can lift the xAI prohibition.** There is deliberately no
`OPENCODE_FREEMODELS_FORBIDDEN_*` escape hatch; the guard is code, not
configuration. Verified: the prohibition blocks 6/6 xAI and Grok model ids and
mislabels 0/8 unrelated ones with no configuration set, with
`HIDE_PROVIDERS=xai`, and with `ZEN_WHITELIST=grok-4.5` — an attempt to keep the
model by whitelist loses to the ban, which is the correct precedence.

## 4. Expected catalog shape

The plugin reads a JSON document that carries a self-describing `$contract`
object. The plugin checks that every key it relies on is documented there, and
refuses the document otherwise — a catalog that no longer documents the fields
this code was written against is not half-understood, it is ignored.

```jsonc
{
  "$contract_version": 2,
  "$contract": { "free": "…", "tools": "…", "tools_confidence": "…",
                 "free_verified_on": "…", "tools_verified_on": "…" },
  "freshness": { "tools_ttl_hours": 168, "availability_ttl_hours": { "google": 6 } },
  "providers": [
    { "id": "opencode", "name": "OpenCode Zen", "default_ttl_hours": 72,
      "volatility": "medium",
      "models": [ { "id": "nemotron-3-ultra-free", "free": true, "tools": "yes",
                    "tools_confidence": "measured", "tools_verified_on": "2026-09-28T20:03:04Z",
                    "free_verified_on": "2026-09-28T20:03:04Z",
                    "free_ttl_hours": 72, "tools_ttl_hours": 168 } ] }
  ]
}
```

`free` is `true | false | <reason string>`; a reason string means *not* free, in
the provider's own words (`"gated"`, `"congested"`). `tools_confidence` is
`measured | inferred | untested`; `inferred` means deduced from a different
route and never probed here, so it renders as unknown rather than as a pass.

**The catalog is not committed to this repository.** It is dated empirical data
about a moving target that decays within hours, and committing it would put a
claim in the repository that nobody would update. The plugin degrades cleanly
without one.

## 5. Verification performed

- `npx tsc --noEmit` against the repository `tsconfig.json` (`strict: true`):
  8 errors before adding the file, 8 after. **Zero new errors.** The 8 are
  pre-existing (4 in `crosslink-guard.ts`, 4 in `rtk-guard.ts`) and were left
  alone as out of scope.
- Degradation: absent file, non-JSON, zero-byte, missing `$contract`, empty
  `$contract`, and `providers` of the wrong type — all return `null`, none throw.
- Configuration surface with nothing set: `HIDE_PROVIDERS`, `FORBIDDEN_MODEL_PATTERNS`
  and `ZEN_WHITELIST` all empty; `isForbiddenModel` returns false for everything.
- Configuration surface when set: `/grok(-|\.|$)/` matches `opencode-go/grok-4.5`
  and does not match `google/gemini-3.5-flash` or `openai/gpt-oss-20b`.
- Labels derived from the real catalog: 108 entries.

## 6. What was not tested

- **The rendered TUI picker.** The plugin appends to `draft.name`, and the picker
  was confirmed to use `model.name` as the entry title, but the rendered picker
  was not observed. A user should look at it once.
- **A live `draft.name` from a running OpenCode** in this repository. No OpenCode
  session was started against the ASES configuration, so end-to-end behaviour
  inside this repo is unverified.
- **Concurrent plugin interaction.** The three existing plugins are guards; this
  one annotates. No test covers ordering against them.
- **The catalog's own maintenance tooling** (probe, commit, apply) lives
  host-local and is not part of this repository.

## 7. One trap worth recording

`editor.model.update()` in OpenCode v2 **creates** an entry that is absent from
the draft. Annotating a model that a removal pass just deleted therefore
silently resurrects it. Every update must be preceded by a `editor.model.get()`.
This was demonstrated, not assumed: with the guard removed and JSON rows added
for a banned model, the model reappeared in the list. The guard is load-bearing.
