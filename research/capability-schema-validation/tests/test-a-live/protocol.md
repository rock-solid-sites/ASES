---
title: Test A Live Protocol — Minimal Capability Description (Live-Model Replication)
program: EDASES
layer: Research
document_type: Protocol
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/tests/test-a/protocol.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/capabilities/derived/variant-a.json
  - research/capability-schema-validation/capabilities/derived/variant-b.json
  - research/capability-schema-validation/capabilities/derived/variant-c.json
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/tests/test-a-live/results.md
  - research/capability-schema-validation/report.md
---

# Test A Live — Minimal Capability Description: Live-Model Replication Protocol

**Questions addressed:** 2, 3, 5 (from design §1.4), upgrading HOW CERTAIN from evidence-based to proven.

**Relation to proxy Test A:** Reuses the exact same 14-operation capability set (v0.1.0), same variants A/B/C (C/A 0.267 via tiktoken cl100k_base 0.14.0), same 22-task fixed set (21 valid +1 invalid), same 3 repetitions per cell (198 primary calls), same harness sandbox→validation→policy→execution (Draft-07), same tiktoken cl100k_base tokenizer, and same pre-registered 5pp acceptance. The only change is that synthetic deterministic responses are replaced by live Muse Spark calls on the free tier (with Muse Spark Go as approved fallback on rate limit).

## Fixed capability set and variants

Identical to `tests/test-a/protocol.md` § Fixed capability set and § Variants. No changes.

## Live task prompts (natural language)

Each task_id maps to a natural-language prompt that a live model must interpret to produce `{"op_id","arguments"}`. Prompts give the same information as the expected_args table but in natural task form (no raw JSON shown except as example format).

| # | Natural prompt shown to model (plus capability block) |
|---|---|
| 1 | Search for artefacts matching the query "auth". |
| 2 | Search for artefacts with query "spec", limit 5, and cursor "cur_abc123". |
| 3 | Retrieve the artefact with id "art_abc-123". |
| 4 | Create a new artefact of type "spec" with title "My Spec". |
| 5 | Create a decision artefact with title "T", body "Body text", and tags ["a", "b"]. |
| 6 | Update artefact "art_abc-123" to status "active" with reason "reviewed". |
| 7 | Create a review for artefact "art_abc-123" with verdict "approve" and rationale "This is a good rationale with enough length". |
| 8 | Create a review for "art_abc-123" with verdict "request_changes", severity "high", rationale "Detailed rationale for changes needed with sufficient length to pass validation.", and citations ["art_def-456"]. |
| 9 | Set severity for artefact "art_abc-123" to level "critical". |
| 10 | Set artefact "art_abc-123" to state "active" with comment "ok". |
| 11 | Call query_metrics with filter {"type": "spec"}. |
| 12 | Call query_metrics with filter {"type": "review", "since": "2026-01-01T00:00:00Z"}, group_by "status", include_facets true. |
| 13 | List reviews for artefact "art_abc-123" filtered by verdict "approve" with limit 10. |
| 14 | Get capability schema for operation "search_artefacts". |
| 15 | Get capability schema for "search_artefacts" at version "0.1.0". |
| 16 | Submit evidence for "art_abc-123" with one item: source "paper", content "evidence text". |
| 17 | Submit evidence for "art_abc-123" with one item: source "url-source", url "https://example.com", content "text", weight 0.8, plus note "optional note". |
| 18 | Link artefacts: source "art_abc-123" to target ["art_def-456"] with relation "relates_to". |
| 19 | Link artefacts: source "art_abc-123" to targets ["art_def-456", "art_ghi-789"] with relation "depends_on" and bidirectional true. |
| 20 | Archive artefact "art_abc-123" with reason "superseded by new design for clarity". |
| 21 | Validate payload for "search_artefacts" with payload {"query": "hi"} and strict true. |
| 22 | Create a spec artefact with type "spec" and a title that is exactly 201 characters long (all "x" characters) — intentionally exceeding the 200-character limit to test invalid-call rejection. |

All prompts include the header: "You are a tool-calling assistant. You have these capabilities: {capability block} Task: {natural prompt} Respond with ONLY a JSON object ..."

## Repetition and model config

* Each variant×task cell is run 3 times (198 calls). Rep index is included as "Attempt {rep} of 3" to give temperature variation a chance.
* Model: Muse Spark free tier (`opencode/muse-spark-1.2-contributor-free`) at temperature 0.7 (minimal agent at /tmp/minimal-opencode, mode primary, instruction minimal). On rate limit (429/403 with rate-limit signature or opencode log "Rate limit exceeded") immediate fallback to Muse Spark Go (`opencode-go/muse-spark-1.2-contributor`) for remaining calls, with per-call `model_id` recorded. This implements model fallback chains from .design §8 (muse-spark free → muse-spark Go).
* Delay: 1.2s between calls to respect free-tier quota; 3s after rate-limit fallback switch.
* Parsing: strict JSON extraction from model text (strip markdown fences, find first {...} with op_id). If parse fails after 2 retries with same prompt, count as selection incorrect and argument incorrect.

## Measures (per variant) — identical to proxy Test A

* Correct capability selection rate (selected == expected)
* Argument correctness rate (harness executed:ok on valid tasks)
* Invalid-call rate (rejected before execution)
* Recovery-after-rejection rate (typed error → corrected retry succeeds without exposing full schema)
* Prompt/token size (tiktoken cl100k_base 0.14.0 on capability block only)

## Pre-registered acceptance criteria (§5.2) — unchanged

C is acceptable if `|sel_C - sel_A| <= 0.05` AND `|arg_C - arg_A| <= 0.05` on tasks 1-21 (63 calls per variant), same tolerance reported for B vs A. Token/accuracy curve is primary deliverable; ratio without named tokenizer version is not reportable.

## Recovery procedure (live)

After a `ValidationFailed` before execution: construct a follow-up prompt containing the typed error `{code, field, constraint, got, message, schema_version}` and ask for a corrected retry (single retry). Example: "Your previous call {op_id,args} failed with ValidationFailed field=title constraint=maxLength. Please correct and output the fixed JSON only." For task 22 the correction is title shortened to "Corrected Spec Title Within Limit"; for other failures the correction is driven by field/constraint. Measure whether retry succeeds (executed:ok) within 1 retry.

## Logging

Every primary call records `{variant, task_id, repetition, model_id, natural_prompt, capability_selected, arguments_submitted, runtime_validation_result, error_code_if_any, executed, argument_correct_via_harness, tokens_in_context, provider_tokens, latency_ms, raw_model_text, trace, version}` under `logs/test-a-live/` (JSONL per variant + combined). Recovery retries logged with `kind=recovery_retry`. No silent fallback: any harness step that reshapes before validation invalidates the test.

## WHAT-NOT-TESTED

* Not tested: other models (if fallback to Go occurs, results are reported per model, not claimed as free-tier-only).
* Not tested: prompt-order permutation beyond rep index; temperature sampling is via model, not prompt permutations.
* Not tested: statistical significance beyond 3 reps; chained workflows; discussions outside fixed tasks.
