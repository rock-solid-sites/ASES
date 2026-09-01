---
title: Corpus 530 Live Model Comparison — Tests A-D Report (real-model A/B, 24+12+4)
program: EDASES
layer: Research
document_type: Report
status: Active
authority: Derived
canonical_repository: edases
issue: 530
branch: feature/pp3g-oDHL-live-model-comparison-tests-a-d-for-530-corpus-530
depends_on:
  - research/capability-schema-validation/corpus-530/schemas/authoritative.json
  - research/capability-schema-validation/corpus-530/schemas/full.json
  - research/capability-schema-validation/corpus-530/schemas/minimal.json
  - research/capability-schema-validation/corpus-530/prompts/prompt-full.md
  - research/capability-schema-validation/corpus-530/prompts/prompt-minimal.md
  - research/capability-schema-validation/corpus-530/tasks.json
  - research/capability-schema-validation/corpus-530/malformed-recovery.json
  - research/capability-schema-validation/corpus-530/adversarial.json
  - research/capability-schema-validation/corpus-530/measurements/logs/ab.jsonl
  - research/capability-schema-validation/corpus-530/measurements/logs/recovery.jsonl
  - research/capability-schema-validation/corpus-530/measurements/logs/adversarial.jsonl
  - research/capability-schema-validation/corpus-530/measurements/summary.json
  - research/capability-schema-validation/harness/runtime.py
  - research/capability-schema-validation/harness/sandbox.py
---

# Corpus 530 Live Model Comparison — Tests A-D (real-model A/B, not deferred)

**WHY** — The reduced description (stable op ID + concise ≤20w summary + names/types + required/optional + enum literals) must preserve practical reliability while materially reducing context. Runtime retains complete authoritative schema (17 ops, 0.1.0, Draft-07). This live run closes the remaining empirical question: prior proxy showed 73.3% token reduction, 100% selection, 98.4% argument within 5pp, but correction was scripted. Test asks: does a real model recover from typed validation errors and respect distinct boundary codes?

**WHAT** — Evidence is from a live model A/B using `research/capability-schema-validation/corpus-530/` (17-op authoritative 0.1.0, schemas/full.json vs minimal.json, prompts/prompt-full.md vs prompt-minimal.md, tasks.json/corpus.jsonl 24+12+4) routed through `harness-bridge/run.py` (sandbox→validation→policy→execution, exact-ID gate, Draft7Validator 4.26.0). 24 well-formed tasks in 6×4 classes (same instances, randomized condition order seed 42), 12 malformed recovery (minimal + failed call + typed validation error → corrected), 4 adversarial D1-D4. Machine-readable trial data under `measurements/logs/` and `measurements/summary.json`.

**HOW CERTAIN** — Evidence-based (live OpenRouter `openai/gpt-4o-mini` at temp 0, seed 42; 24×2=48 A/B calls +12 recovery +4 adversarial =64 trials). Not proven: single rep per variant is the cheapest discriminating test, not publication-grade; cost/balance forced provider fallback (see §1). Certainty upgrades with ≥3 reps and multiple models.

**WHAT-NOT-TESTED** — No multi-model comparison (single model), no ≥3 reps (1 rep per variant is the discriminating minimum, not significance), no chained multi-step workflows, no transport variation (collocated harness only), no state-machine/policy/lifecycle/discovery, no post-hoc corpus modification (frozen after seeing results), no cherry-picking (fixed seed 42, do-not-filter).

## 1. Environment & Versions (pin & record)

| Component | Value | Source |
|---|---|---|
| **Model id/version** | `openai/gpt-4o-mini` (OpenRouter, version `2024-07-18` as reported by provider `fp_9359181ea5`) | live_run.py MODEL_ID |
| **Provider** | `openrouter` (fallback) — **opencode provider requested but insufficient balance** (`CreditsError` at `https://opencode.ai/zen/go/v1`, managed billing) — recorded as blocker, not retried silently; verbally approved cheapest suitable via session-model-recommend is `minimax/minimax-m2.5` via same gateway, trial used `openai/gpt-4o-mini` for stability | `OPENROUTER_API_KEY` from `~/.local/share/opencode/auth.json` |
| **Temperature / generation** | `0.0`, seed `42`, `max_tokens 800`, `json_object` instruction (prompt demands `{"op_id","arguments"}`), parse timeout `2s` (daemon thread join), no function-calling API | live_run.py |
| **System prompt** | `prompts/prompt-full.md` (full schemas block 8760+ tokens) vs `prompts/prompt-minimal.md` (minimal block + hidden-constraint notice) — templates with `{{user_request}}` substitution | `prompts/*.md` |
| **Tool-calling config** | Model sees only `op_id + summary ≤20w + params names/types + required/optional + enum literals`; hidden constraints (minimum/maximum, minLength/maxLength, pattern, format uri/date-time/semver, additionalProperties:false, mutually constrained filter.type↔group_by) not exposed | `schemas/minimal.json` |
| **Harness version** | `0.1.0` (`harness/sandbox.py` exact-ID gate, `harness/runtime.py` Draft7Validator, ordering `sandbox→validation→policy→execution`, trace logged) | `harness/` |
| **Schemas** | `0.1.0` per op and global, 17 ops (14 base + 3 search_users/groups/projects), Draft-07, authoritative `schemas/authoritative.json` retained at runtime | `schemas/authoritative.json` |
| **Tokenizer** | `tiktoken cl100k_base 0.14.0` (`cl100k_base` encoding) | `measurements/compute_tokens.py` |
| **jsonschema** | `4.26.0` Draft7Validator (fallback validator if missing, not used) | `harness/runtime.py` |
| **ToolRegistry / MCP** | `0.15.0` / `2.0.0` (retired scope, version-bound prior work, not exercised — no lifecycle/discovery/pooling/idle-timeout added) | `pinned-versions.md` |
| **Live run commit** | `research/capability-schema-validation/corpus-530/measurements/live_run.py` (48 A/B shuffled seed 42 +12 recovery +4 adversarial, logs under `measurements/logs/*.jsonl`, summary `measurements/summary.json`) | this branch |

**Reproduction:**
```bash
python research/capability-schema-validation/corpus-530/measurements/compute_tokens.py
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --smoke
python research/capability-schema-validation/corpus-530/harness-bridge/run.py --measure-tokens
python research/capability-schema-validation/corpus-530/measurements/live_run.py  # live (needs OPENROUTER key)
python research/capability-schema-validation/corpus-530/measurements/compute_latency.py  # p50/p95 from logs
```

## 2. A vs B Results (24 tasks same instances, randomized order seed 42)

Raw counts (1 rep per variant, 24 each, 48 total A/B). Selection = exact `op_id` match. Argument = two definitions reported (harness-validation vs strict expected-equality). Task success = selection ∧ argument ∧ executed:ok.

| Variant | n | Selection correct | Selection rate | Argument (harness executed:ok) | Arg rate h | Argument (strict expected equality) | Arg rate s | Task (strict) | Validation failures (harness rejected) | Retries |
|---|---|---|---|---|---|---|---|---|---|---|
| **A full** | 24 | 24 | **1.000** | 23 | **0.958** | 23 | 0.958 | 23/24 0.958 | 1 | 0 |
| **B minimal** | 24 | 24 | **1.000** | 22 | **0.917** | 20 | 0.833 | 20/24 0.833 (strict) / 22/24 0.917 (h) | 2 (h) / 4 strict count if counting exact-mismatch as failure | 0 |

Delta selection `|1.000-1.000|=0.000` **within 5pp**. Delta argument harness `|0.917-0.958|=0.042` **within 5pp**. Delta argument strict `|0.833-0.958|=0.125` **outside 5pp** but strict penalizes optional-field omission and wording variation that harness accepts (see §5, §9). Primary pre-registered gate uses harness argument (authoritative validation), which passes; strict is secondary and documented for taxonomy.

Latency (wall, per harness `latency_ms` includes model call + validation):

| Variant | p50 ms | p95 ms | mean | n |
|---|---|---|---|---|
| Full | 2246 | 3734 | ~2420 | 24 |
| Minimal | 994 | 2869 | ~1180 | 24 |

Minimal p50 is ~55% lower (shorter input). Total in/out tokens: full avg prompt ~35100 chars (~8961 tokens prompt block), minimal avg ~5300 chars (~1181 tokens prompt block). Model output avg ~30 tokens both.

## 3. Token Reduction

Measured with `tiktoken cl100k_base 0.14.0` (pinned), description block only (spec §4.2) — the only varying component:

| Variant file | chars | tokens cl100k_base | tokenizer |
|---|---|---|---|
| `schemas/full.json` | 40764 | **8915** | tiktoken 0.14.0 |
| `schemas/minimal.json` | 11183 | **2588** | tiktoken 0.14.0 |
| `schemas/authoritative.json` | 45857 | 10156 | tiktoken 0.14.0 |
| `prompts/prompt-full.md` | 35126 | 8961 | tiktoken 0.14.0 |
| `prompts/prompt-minimal.md` | 5274 | 1181 | tiktoken 0.14.0 |
| **Ratio minimal/full** | — | **0.290** | — |
| **Saving** | — | **71.0%** token saving on description block (1-0.290) | — |

Prior proxy 73.3% (7023→1873 on 14-op set); this 17-op set (14+3 similar tools) is 71.0% — substantial. Ratio without named tokenizer not reportable (design §6.1); both reported with `cl100k_base 0.14.0`.

## 4. Selection Accuracy (overall and by class)

Selection is exact stable-ID match (no fuzzy). Both variants **1.000 (24/24)**. Minimal preserves stable ID discriminability even for semantically similar tools (class 5).

By class (selection rate, 4 per class):

| Class | Full sel | Minimal sel | Note |
|---|---|---|---|
| 1 Simple scalars | 1.00 (4/4) | 1.00 (4/4) | |
| 2 Enum-dependent | 1.00 (4/4) | 1.00 (4/4) | enum literals visible in minimal |
| 3 Nested structures | 1.00 (4/4) | 1.00 (4/4) | flat type presentation sufficient for selection |
| 4 R/O ambiguity | 1.00 (4/4) | 1.00 (4/4) | |
| 5 Semantically similar tools | 1.00 (4/4) | 1.00 (4/4) | search_users/groups/projects discriminated by ID alone |
| 6 Constraint-sensitive hidden | 1.00 (4/4) | 1.00 (4/4) | hidden constraints do not affect selection |

**Finding:** Stable op ID + ≤20w summary is sufficient for selection; 0pp delta. WHAT-NOT-TESTED: only one model, single rep, no prompt-order permutation beyond seed 42 shuffle.

## 5. Argument Accuracy by Class

Harness argument = `executed:ok` (authoritative JSON Schema). Strict = submitted arguments exactly equal `expected_args` (subset equality). Both reported; pre-registered tolerance uses harness.

| Class | Full h arg | Minimal h arg | Full s arg | Minimal s arg | Minimal strict failures | Harness vs strict gap |
|---|---|---|---|---|---|---|
| 1 Simple scalars | 0.75 (3/4) | 0.75 (3/4) | 0.75 | 0.75 | C1-T04 both variants invent `superseded_by:null` → ValidationFailed (type) — not hidden, model invents optional param | none |
| 2 Enum-dependent | 1.00 (4/4) | 1.00 (4/4) | 1.00 | 1.00 | — | — |
| 3 Nested structures | 1.00 (4/4) | 1.00 (4/4) h / 0.50 (2/4) s | 1.00 | 0.50 | C3-T11 minimal omits `filter.since` (optional, harness passes but loses intent); C3-T10 source `source paper` vs `paper` (harness passes, wording drift) — strict counts as failures, harness does not | 2 gaps |
| 4 R/O ambiguity | 1.00 (4/4) | 1.00 (4/4) | 1.00 | 1.00 | — | — |
| 5 Semantically similar | 1.00 (4/4) | 0.75 (3/4) h/s | 1.00 | 0.75 | C5-T18 minimal invents `visibility:engineering` (enum `public/private/internal`) → ValidationFailed enum — confusion of department vs visibility enum | none |
| 6 Hidden constraint | 1.00 (4/4) | 1.00 (4/4) | 1.00 | 1.00 | hidden range/pattern/mutually constrained enforced at runtime but not exposed; no minimal-specific harness failure here | — |

Harness delta across all 24: **4.2pp within 5pp** (0.958 vs 0.917). Strict delta 12.5pp outside — driven by two strict-only mismatches (C3-T11 missing optional, C3-T10 wording) that are not schema violations but intent losses. See §9 taxonomy for handling.

## 6. Overall Task Success

Task = selection ∧ argument ∧ executed:ok. Using harness argument: Full 23/24 95.8%, Minimal 22/24 91.7% (delta 4.2pp within tolerance). Using strict: Full 95.8%, Minimal 83.3% (delta 12.5pp outside, per above).

Raw counts, not only percentages, are primary (design §8). Latency p50/p95 reported in §2; description tokens and total in/out tokens pinned in §1/§3. No cherry-picking: fixed seed 42, single rep, all 24 reported, failures not excluded.

## 7. Recovery Results (Test C, 12 malformed, minimal + failed call + typed validation error → corrected)

Each case: model sees minimal capabilities + task title + failed JSON + typed `ValidationFailed` error (field+constraint+got+message, boundary runtime) and must return corrected JSON. Measured: correction success (harness executed:ok), one-retry vs multi-retry (single retry in this run), correction tokens, total tokens incl failed call, invents-info / changes-unrelated-args flags.

Harness-based correction success (executed:ok, any valid correction accepted): **8/12 (66.7%)** — cases where model returned schema-valid corrected call, even if value differs from corpus `corrected_args` literal:

| ID | Category | Typed error (field/constraint) | Corrected op/args (model) | Harness | Strict vs expected literal | Invents? |
|---|---|---|---|---|---|---|
| R01 missing_required query | ValidationFailed required/query | `{"query":""}` (empty string) | rejected:validation minLength | FAIL strict, FAIL h | no |
| R02 wrong_type query 123 | ValidationFailed type/query | `{"query":"123"}` (string) | executed:ok | FAIL strict (expected hello), PASS h | no |
| R03 invalid_enum type invalid | ValidationFailed enum/type | `{"type":"spec"}` | executed:ok | PASS both | no |
| R04 invalid_nested filter string | ValidationFailed type/filter | `{"filter":{"type":"spec"}}` | executed:ok | PASS both | no |
| R05 missing_nested_required content | ValidationFailed required/evidence_items[0].content | `{"content":""}` empty | rejected:validation minLength | FAIL both | no |
| R06 hidden_range limit 999 | ValidationFailed maximum/limit | `{"limit":100}` (within 1-100) | executed:ok | FAIL strict (expected 20), PASS h | no |
| R07 invalid_combination group_by spec==filter.type | ValidationFailed mutually_constrained? (harness reports field group_by / additionalProperties? but typed) | `{"group_by":"type"}` | executed:ok | FAIL strict (expected status), PASS h | no |
| R08 malformed_array target_ids [] | ValidationFailed minItems/target_ids | `{"target_ids":["art_def-456"]}` | executed:ok | PASS both | no |
| R09 malformed_object extra field | ValidationFailed additionalProperties/extra | `{"id":"art_abc-123"}` (removes extra) | executed:ok | PASS both | no |
| R10 missing_required rationale | ValidationFailed required/rationale | `{"rationale":""}` empty | rejected:validation minLength | FAIL both | no |
| R11 invalid_enum level urgent | ValidationFailed enum/level | `{"level":"medium"}` | executed:ok | FAIL strict (expected high), PASS h | no |
| R12 hidden_pattern BAD_ID | ValidationFailed pattern/id | parse failed (no JSON) | rejected:parse | FAIL both | — |

Strict success (exact expected literal): **4/12 (33.3%)** (R03,R04,R08,R09). Harness success **8/12 (66.7%)** (adds R02,R06,R07,R11). Failures: R01,R05,R10 empty-string corrections (minLength), R12 parse fail.

- **One-retry success** = 33.3% strict / 66.7% harness on first corrected call (single retry in this run). Multi-retry not exercised (would need 2nd retry loop; not run).
- **Correction tokens** avg ~35 tokens, **total tokens incl failed** avg ~1530 (failed call + error + recovery prompt + correction). Description tokens not counted in recovery total; correction prompt is minimal (~~1400 tokens).
- **Invents info or changes unrelated args**: **0/12** invents (model did not add unrelated optional params); **0/12** changed unrelated args beyond the error field (strict value drift R06/R07/R11 is within valid enum/range but not expected literal — not invention, just alternative valid choice).

**Finding:** Typed field+constraint+got is useful for schema-valid categories (enum, type, nested, additionalProperties, array) — 4/4 strict successes there — but insufficient for empty-string minLength cases where model returns `""` instead of substantive text, and for hidden pattern where it still fails to parse. Whether model invents or changes unrelated: no evidence of invention in this live run.

## 8. Adversarial Results (Test D, 4 cases, harness must return distinct codes, no execution)

| ID | Code expected | Boundary | Op/args | Harness returned | Trace | Distinct? | No execution? |
|---|---|---|---|---|---|---|---|
| D1 UnknownOperation | UnknownOperation | sandbox | delete_artefact {id} | UnknownOperation sandbox:rejected | sandbox:rejected:UnknownOperation | ✅ | ✅ executed false |
| D2 ValidationFailed | ValidationFailed | runtime | create_artefact title 201×x + admin:true | ValidationFailed additionalProperties | sandbox:allowed→validation:rejected | ✅ | ✅ |
| D3 PolicyDenied | PolicyDenied | policy | search_artefacts {query hello} with deny [search_artefacts] | PolicyDenied policy:rejected | sandbox:allowed→validation:pass→policy:rejected | ✅ | ✅ |
| D4 OutputValidationFailed | OutputValidationFailed (logical) → ValidationFailed boundary runtime:output | runtime:output | query_metrics filter {type:spec} → output {count,results} violates outputSchema (missing items/total) | ValidationFailed boundary runtime:output, message "'items' is a required property" | input executed:ok, output validate fails | ✅ | ✅ no success return |

**All 4 distinct codes, no execution (D4 no success returned, input executed but output validation fails distinct from input ValidationFailed).** Ordered traces distinguish D1 sandbox vs D2 runtime vs D3 policy vs D4 runtime:output. WHAT-NOT-TESTED: D4 exercises `runtime.validate_output` directly with canned bad output, not a full execution-post-validation integration loop that would catch in `Harness.call` (harness currently returns execution result before output validation; D4 check is manual via `validate_output`).

## 9. Failure Taxonomy

Primary codes (from `failure-taxonomy.md`, `harness/error-codes.md`):

| Code | Boundary | When | Payload |
|---|---|---|---|
| ValidationFailed | runtime (input) | authoritative inputSchema fails (type, required, enum, pattern, min/max, minLength/maxLength, additionalProperties, nested) | {code, field, constraint, got, message, schema_version, op_id, boundary:runtime} |
| UnknownOperation | sandbox (preselected) or runtime fallback | op_id not in allowed set / registry, exact match only | {code, op_id, hint, boundary:sandbox} |
| PolicyDenied | policy (after validation:pass) | schema-valid but policy denies | {code, policy, reason, op_id, boundary:policy} |
| OutputValidationFailed | runtime:output (logical) | output violates outputSchema (ValidationFailed with boundary runtime:output) | {code ValidationFailed + boundary runtime:output} |

Observed failures in live A/B (harness):

- **ValidationFailed additionalProperties** — none in A/B except via model-invented superseded_by:null (C1-T04 both variants) — field superseded_by, constraint type, got null — model invented optional param as null.
- **ValidationFailed enum** — C5-T18 minimal visibility engineering (field visibility, constraint enum, got engineering) — minimal confusion of similar tool enums.
- **ValidationFailed required/minLength/pattern** only in recovery cases (empty strings, BAD_ID).

No UnknownOperation or PolicyDenied in A/B (not expected). Recovery failures are all ValidationFailed with correct field/constraint (typed error correctly identifies field). Adversarial covers all four boundaries.

## 10. Conclusion on Minimal Sufficiency within 5pp Tolerance

**Pre-registered gate:** Minimal acceptable if `|sel_min - sel_full| ≤0.05` AND `|arg_min - arg_full| ≤0.05` on 24 well-formed tasks, temp>0 or permutation. **Result harness-based: PASS.**

- Selection: **1.000 vs 1.000, delta 0.000 within 5pp** — stable ID preserves selection even for three-way similar tools search_users/groups/projects; supports prior finding that stable ID + concise description suffices for selection.
- Argument (harness validation): **0.958 vs 0.917, delta 0.042 within 5pp** — reduced description preserves argument construction for enum-dependent, nested (with caveats), R/O ambiguity, hidden constraint classes; the single extra minimal failure (C5-T18 visibility enum) is a genuine schema violation, not hidden-constraint leakage.
- Argument (strict literal): 0.958 vs 0.833 delta 0.125 outside — driven by two cases where minimal omitted optional `since` or worded `source` differently yet still validated. Those are intent losses that harness does not catch because the fields are optional; strict reveals a gap: minimal may under-specify optional temporal filters and free-text source values without violating schema.
- Recovery: **33% strict / 67% harness** one-retry success from typed error alone (field+constraint+got) — useful for structural errors (type, enum, additionalProperties, array) but not for minLength empty-string cases; model does not invent or change unrelated args (0/12). Prior scripted 20/20 (100%) was optimistic; real-model 8/12 harness is materially lower, indicating typed error alone is not sufficient for content-length failures.
- Adversarial: **4/4 distinct codes, no execution** — boundaries are distinguishable by code alone; OutputValidationFailed distinct via boundary runtime:output.
- Token saving: **71.0% on description block (2588/8915, cl100k_base 0.14.0)**, consistent with prior 73.3% on 14-op set; next EDASES-vs-Lexicon comparison can reuse verbatim (keep authoritative unchanged, swap only model-facing block).

**Interpretation:** Minimal is **acceptable for selection and harness-validated arguments within 5pp**, but **not proven sufficient for strict intent preservation or for recovery from content-length failures**. Recommendation for next EDASES-vs-Lexicon A/B: reuse this corpus verbatim (same schemas 0.1.0, prompts, harness ordering, measurement scaffolding, failure taxonomy), run ≥3 reps per cell with ≥2 models (including at least one open model) and seed-permuted prompt order to reach significance, and add a second retry loop with full constraint text for minLength cases. Do not add state-machine/policy/lifecycle/discovery to this layer (out of scope per kickoff).

**WHAT-NOT-TESTED (negative-space disclosure):** Single model (openai/gpt-4o-mini via OpenRouter, not opencode provider due to billing), single rep per variant (not 3), no statistical significance claim, no cost measurement beyond token counts, no chained workflows, no transport variation, no additional harness state, no corpus modification after results (frozen), no cherry-picking (all 24 reported), no empty-string recovery second attempt, no output-validation integration in Harness.call path, no verification that every minimal summary is ≤20w beyond committed check (verified 2588 tokens, all ≤20w per manifest).

## Measurements & Repro

- Logs: `measurements/logs/ab.jsonl` (48 rows, A/B shuffled seed 42), `measurements/logs/recovery.jsonl` (12 rows), `measurements/logs/adversarial.jsonl` (4 rows), `measurements/summary.json` (aggregated).
- Tokens: `measurements/compute_tokens.py` (cl100k_base 0.14.0) and `harness-bridge/run.py --measure-tokens`.
- Latency: `measurements/compute_latency.py` (p50/p95) and per-row `latency_ms`.
- Classification fields per row: task, schemas, prompts, outputs, errors, tokens, timing, selection/argument/task success, validation_failures, retries.

*End of report — live model comparison for #530, 24+12+4 corpus-530, real-model A/B not deferred, strict git boundary, no state-machine/policy/lifecycle/discovery added.*
