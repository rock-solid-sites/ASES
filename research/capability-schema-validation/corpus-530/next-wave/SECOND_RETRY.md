---
title: Second-Retry Harness for Recovery — minLength/Pattern Empty-String Failures
program: EDASES
layer: Research
document_type: Specification
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Second-Retry Harness — Recovery (minLength/pattern empty-string)

**WHY** — Live recovery showed `0 invents` but 3/12 empty-string corrections (`""`) for `minLength` failures (R01 query, R05 content, R10 rationale) that still fail validation, and one parse failure for pattern. The first retry gave only `field+constraint+got+message` (e.g., `field:"evidence_items.0.content", constraint:"minLength", message:"'' should be non-empty"`). That is *structurally* typed but *content-insufficient* — the model does not know what substantive text to supply.

**WHAT** — This scaffold adds a **second retry** that, *only* when the first retry fails with **constraint ∈ {minLength, pattern, minItems-pattern-like} and `got=="\"\""` (empty string)**, re-prompts with **full constraint text** for that single field: `field`, `constraint`, `message`, **plus a similar valid example** drawn from the corpus — *without exposing the full JSON Schema* (`type`, `required`, `additionalProperties`, `enum`, other fields, other ops remain hidden). The authoritative `schemas/authoritative.json` stays runtime truth.

**HOW CERTAIN** — Scaffolding only (no live call). Checkable: trigger predicate, example picker, and prompt builder are unit-tested via `--self-test`.

**WHAT-NOT-TESTED** — No live second-retry evidence yet; the example picker is lexical-similar, not semantic; no full schema is ever leaked in this harness.

## Scope of trigger

Second retry fires **iff** all of:

1. First recovery attempt returned `ValidationFailed` (boundary `runtime`) with `constraint` in trigger set and `got` is empty string (`""` or `'""'` after json.dumps).
2. `got` JSON-dumped equals `""` (i.e., `got == '""'` or `args_corrected[field_last_segment] == ""`).
3. Or: `got` is empty-ish single-JSON-field string with length 0.

Trigger set:

- `minLength` (primary — observed R01,R05,R10)
- `pattern` with empty string (edge — empty fails `^art_...` or similar)
- `minItems` is **not** triggered on empty string alone (array empty is `[]`, not `""`) — kept out; left to first retry.

**Do not trigger** on: `type`, `enum`, `required`, `maximum`, `additionalProperties`, `format` unless got is `""` — and even then only if the failing field's value is `""`.

## What the second retry exposes (and does not)

Allowed to expose — for the **single failing field only**:

- Field path (`field`, e.g., `query`, `evidence_items.0.content`, `rationale`)
- Constraint name (`constraint`, e.g., `minLength`)
- Runtime message (`message`, e.g., `"'' should be non-empty"` or `"'BAD_ID' does not match '^art_[a-z0-9-]+$'"` but only when got is `""`; for pattern+empty, message will still reference pattern)
- **One similar valid example** for that field — picked from `malformed-recovery.json#corrected_args` or `tasks.json#expected_args` that shares the same field path — e.g., for `query` → `"hello"`, for `evidence_items.0.content` → `"evidence text from experiment"` (from `C3-T10`), for `rationale` → `"This rationale has enough length to pass hidden minLength ten"` (from `C2-T06`) or `"Rationale with enough length for validation"` (from `R10` corrected).

Not exposed (remain hidden as in minimal):

- Full `authoritative.json` or any other op's schema
- Other fields/constraints for the same op (only the failing field's constraint sentence)
- Numeric ranges (unless the failing constraint is minLength and message leaks `minLength 1` — that leaks minimally as constraint length but not the full range block; acceptable because it is the failed field's own constraint)
- Patterns for other fields; `additionalProperties:false`; mutually constrained rules; enum lists for other ops

**Invariant:** The second-retry prompt contains at most ~3 new sentences beyond the first retry's typed error: (1) constraint sentence for field, (2) valid example, (3) instruction to supply substantive non-empty text. No JSON Schema excerpt.

## Prompt construction (deterministic)

First retry prompt (already in `live_run.py`) — minimal capabilities + task title + failed JSON + `typed_error {field, constraint, got, message}` + instruction "Fix ONLY the fields indicated…".

Second retry prompt appends:

```
## Second Retry — Full Constraint for Field "{field}"

The previous correction failed with empty string.

- Field: "{field}"
- Constraint: {constraint}
- Runtime message: {message}
- Example valid value for this field (from corpus, not schema):
  {example_json_or_string}

Instruction: Replace the empty string for field "{field}" with a substantive, non-empty value matching the example's shape (do NOT copy the example verbatim if it contains a specific identifier; generate a plausible value of similar shape). Keep all other fields unchanged; do not invent unrelated params. Respond with JSON {{"op_id":"...","arguments":{{...}}}}.
```

Example picker (deterministic, no LLM):

- Lookup table (built at init from `malformed-recovery.json` and `tasks.json`):
  - `query` → `"hello"` (R01 corrected)
  - `id` / `artefact_id` / `source_id` / `target_ids` items → `"art_abc-123"` (C1-T02), `"art_def-456"` (C2-T07), `"art_valid-001"` (C6-T22)
  - `evidence_items.*.content` / `content` → `"evidence text from experiment"` (C3-T10) or `"evidence text"` (R05 expected corrected)
  - `rationale` → `"This rationale has enough length to pass hidden minLength ten"` (C2-T06)
  - `reason` → `"superseded by new design for clarity"` (C1-T04)
  - `title` → `"My Spec"` or `"Short title"` (C2-T05, C6-T24)
  - generic fallback if field unknown: `"valid non-empty text"` (length >1)

## Logging

Each second retry logs a row under `next-wave/measurements/second_retry/logs/` (and also aggregated in `measurements/logs/recovery.jsonl` with `retry_number=2`):

- `first_retry_error` (ValidationFailed typed)
- `second_retry_prompt_tokens` (cl100k_base 0.14.0 count of appended constraint text)
- `second_retry_raw_output`, `op_corrected`, `args_corrected`, `parse_error`
- `second_retry_validation_result`, `second_retry_error`, `second_retry_executed`
- `second_retry_success` (harness `executed:ok`), `invents_info`, `changes_unrelated`

Schema: `measurements/second_retry/schema.json`.

## Invariants & non-goals

- **No full-schema exposure:** Verified by `second_retry.py --check-examples` — prompted text never contains `"$schema"`, `"inputSchema"`, `"additionalProperties"`, or a JSON Schema block.
- **Deterministic enrichment only:** No model call in enrichment itself; model is called only with enriched prompt.
- **Preserves first-retry trace:** Second retry row links `parent_id` to first retry row `id` (R01,R05,R10…).
- **Out of scope:** This layer does not add state-machine/policy/lifecycle/discovery; it enriches only the validation error for content-length failures.

## Reproduction (scaffolding only — no live run)

```bash
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --self-test
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --check-examples
# dry-run enrichment for observed R01,R05,R10 empty-string failures (no model call)
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --dry-enrich --field query --constraint minLength --got '""'
python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --dry-enrich --field evidence_items.0.content --constraint minLength --got '""'
```

## Dependencies

- `../../malformed-recovery.json` (corrected_args examples)
- `../../tasks.json` (expected_args examples)
- `../../schemas/authoritative.json` (authoritative truth, never exposed verbatim here)
- `../../failure-taxonomy.md` (ValidationFailed codes)
- Pinned versions: tiktoken 0.14.0 cl100k_base, jsonschema 4.26.0, harness 0.1.0, schemas 0.1.0.
