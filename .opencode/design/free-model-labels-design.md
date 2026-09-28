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
| Filesystem writes inside the transform | None — the catalog is read once, before it |
| Network calls | None |
| Fails open | Yes — any catalog problem leaves the list untouched |
| New TypeScript errors introduced | 0 (verified against the repo's `tsconfig.json`) |

### Why removals are opt-in

Model availability on a free tier moves, and redundancy across providers is
worth preserving as a fallback. More importantly: a provider ban or a model
whitelist is a **host policy decision**, and a shared plugin should not impose
another machine's choices. The original working copy carried a hardcoded
provider-hide list, a grok ban, and an 8-entry Zen whitelist; those became
environment-driven configuration with empty defaults.

This is also a safety consideration. The Zen whitelist was a dated snapshot of
8 model ids. Had a new free Zen model appeared in the catalog before the
whitelist was updated, the interaction between the annotation and the removal
pass would have to be reasoned about on every catalog refresh. Empty-by-default
removes that coupling entirely.

## 3. Configuration

All optional. With none set, the plugin annotates and removes nothing.

| Variable | Purpose | Default |
|---|---|---|
| `OPENCODE_FREEMODELS_CATALOG` | Catalog JSON path | `~/.local/share/opencode-docs/free-models.json` |
| `OPENCODE_FREEMODELS_HIDE_PROVIDERS` | Comma-separated provider ids to remove | empty |
| `OPENCODE_FREEMODELS_FORBIDDEN_MODELS` | Comma-separated substrings or `/regex/flags` to remove | empty |
| `OPENCODE_FREEMODELS_ZEN_WHITELIST` | Comma-separated model ids to keep on `opencode` | empty (keep all) |

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
