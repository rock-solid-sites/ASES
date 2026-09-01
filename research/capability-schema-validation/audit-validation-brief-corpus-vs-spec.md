---
title: Phase 0 Audit — validation-brief-corpus vs Spec Divergence
program: EDASES
layer: Research
document_type: Audit
status: Active
authority: Derived
canonical_repository: edases
issue: 530
branch: feature/pp3g-GQLX-phase-0-audit-validation-brief-corpus-vs-spec-f8c2
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/capabilities/manifest.json
  - research/capability-schema-validation/capabilities/derived/variant-a.json
  - research/capability-schema-validation/capabilities/derived/variant-b.json
  - research/capability-schema-validation/capabilities/derived/variant-c.json
  - evaluation-corpus/validation-brief-corpus/manifest.json
  - evaluation-corpus/validation-brief-corpus/README.md
  - research/capability-schema-validation/tests/test-a/protocol.md
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/report.md
  - evaluation-corpus/validation-brief-corpus/README.md
supersedes: []
superseded_by: []
last_updated: 2026-09-01
pinned_versions:
  schemas_version: 0.1.0
  capability_set: 14 ops
  tokenizer: tiktoken cl100k_base 0.14.0
  jsonschema: 4.26.0
  tiktoken: 0.14.0
  commits:
    A_test_a: 17ed2631
    B_test_b: fbca4975
    C_test_c: baa35bf7
    D_test_d: b719ca30
    E_test_e: dcf4f313
---

# Phase 0 Audit — validation-brief-corpus vs Spec Divergence (#530)

**Date:** 2026-09-01 · **Branch:** `feature/pp3g-GQLX-phase-0-audit-validation-brief-corpus-vs-spec-f8c2` · **Issue:** #530
**Auditor:** pp3g-GQLX (single builder, serial) · **Scope:** Compare spec §Test Corpus against BOTH (a) `evaluation-corpus/validation-brief-corpus/` and (b) `research/capability-schema-validation/`
**Method:** Static inventory — read `manifest.json`, `schemas.json`, `variant-*.json`, `protocol.md`, `briefs/`, `malformed/`, `adversarial/`, `error-codes.md`; no live model run; no state-machine/policy/lifecycle added (per kickoff constraint).

> **One-line verdict:** `evaluation-corpus/validation-brief-corpus/` and `research/capability-schema-validation/` are **intentionally distinct** corpora with orthogonal domains. Neither matches the spec's tool-calling 6-class taxonomy verbatim. **Decision: KEEP BOTH DISTINCT** — §10 records rationale, correct home for #530, and rename suggestion.

---

## 1. Spec §Test Corpus (expected, per kickoff title)

Source: `future-research-topics/Validation Brief: Real-Model Minimal.md §Test Corpus` (file **not present** on disk as of 2026-09-01 — `future-research-topics/` contains only `README.md`, `project-setup{,-final,-summary}.md`, `topics-scratchpad.md`; the spec is reconstructed from the kickoff title which is the authoritative §Test Corpus statement for this audit).

| Segment | Expected count | Expected domain |
|---|---|---|
| **6 task classes (4 each = 24 well-formed)** | 24 | Tool-calling / capability-schema validation |
| Class 1 | 4 | **Simple scalars** — single param, scalar type (string/integer/boolean), no nesting |
| Class 2 | 4 | **Enum-dependent** — selection/argument conditioned on enum literal (must show enum literals) |
| Class 3 | 4 | **Nested structures** — object/array/nested fields, 1–3 levels, e.g. `filter{type,since}`, `evidence_items[]`, `facets{}` |
| Class 4 | 4 | **Required/optional ambiguity** — tasks where optional vs required is the discriminating signal (e.g. `cursor?`, `body?`, `tags?`, `citations?`) |
| Class 5 | 4 | **Semantically similar tools** — ≥2 ops with overlapping description; model must disambiguate via stable ID + concise desc + names/types |
| Class 6 | 4 | **Constraint-sensitive (hidden constraints)** — constraints NOT shown in minimal description but enforced at runtime: hidden numeric range (`limit 1–100`, `reason 5–500`), string pattern (`^art_[a-z0-9-]+$`, `^cur_[a-z0-9]+$`), mutually constrained fields (e.g. `filter.type` ↔ `group_by`), schema constraint (`maxLength`, `minLength`, `pattern`, `additionalProperties:false`) |
| **Malformed recovery** | 12 | Cover missing required, wrong type, invalid enum, invalid nested field, missing nested required, hidden range violation, invalid combination, malformed array/object + 4 balanced — must be rejected `ValidationFailed` before execution |
| **Adversarial D1–D4** | 4 | D1 `UnknownOperation` (absent capability / hallucinated op), D2 `ValidationFailed` (malformed that would bypass if not caught), D3 `PolicyDenied` (schema-valid but policy-denied), D4 `OutputValidationFailed` (output schema violation post-execution) |
| **Total** | **40** | 24 + 12 + 4 |

**Success criteria tied to spec (from #530 plan):** Token reduction substantial, selection/argument/task success within **5 percentage points (5pp)** between full and minimal, hidden constraints enforceable, recovery useful rate reported. Measurements: description tokens, total in/out, selection/argument/task success, validation failures, retries, latency p50/p95; recovery metrics. Deliverable: 10-section report + machine-readable trial data.

**Interpretation note:** The 6 classes are **tool-calling capability tests**, not methodology-enforcement tests. The hidden-constraint discipline is core: the minimal description shows `stable ID + concise desc + names/types + required/optional + enum literals` — **not** `min/max`, `pattern`, `maxLength`, or output schema — and the runtime retains the complete authoritative schema as sole validator.

---

## 2. Actual (a) — `evaluation-corpus/validation-brief-corpus/` (committed at `c17f74e2` → `6c55b4f1`)

Machine-readable: `manifest.json` (`corpus: validation-brief-corpus`, `version: 0.1.0`, `issue: 530`, `total_briefs: 40`, `well_formed: 24`, `malformed: 12`, `adversarial: 4`), `corpus.jsonl` (40 lines).

| Layer | IDs | Files |
|---|---|---|
| **Well-formed 24 (6×4)** | AL-01..04, PE-01..04, WV-01..04, KD-01..04, OO-01..04, SR-01..04 | `briefs/class-1-artefact-lifecycle/AL-*.md` (4), `briefs/class-2-provenance-evidence/PE-*.md` (4), `briefs/class-3-workflow-validation/WV-*.md` (4), `briefs/class-4-knowledge-decision/KD-*.md` (4), `briefs/class-5-orchestration-oversight/OO-*.md` (4), `briefs/class-6-state-recovery/SR-*.md` (4) |
| **Malformed 12** | MF-01..12 | `malformed/MF-01-missing-id.json` (missing `id`), `MF-02-invalid-schema.json` (extra key + invalid enum `maybe`), `MF-03-truncated-brief.md` (truncated body), `MF-04-wrong-type.json` (`limit: "five"`), `MF-05-duplicate-id.json` (duplicate of AL-01), `MF-06-empty-body.md` (frontmatter only), `MF-07-oversized-payload.json` (>64KB), `MF-08-invalid-utf8.md` (lone surrogate), `MF-09-conflicting-instructions.md` (do X and ¬X), `MF-10-stale-reference.md` (non-existent artefact), `MF-11-missing-provenance.md` (missing WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED for state-modifying decision), `MF-12-circular-supersession.json` (A↔B cycle) |
| **Adversarial 4** | AD-01..04 | `adversarial/AD-01-prompt-injection.md` (injected "Ignore previous instructions…"), `AD-02-bypass-validation.md` (claim verbal approval to skip gate), `AD-03-authority-escalation.md` (`role: orchestrator` self-escalation), `AD-04-data-exfiltration.md` (path traversal `../../.crosslink/issues.db`) |
| **Harness** | — | `harness/README.md`, `harness/validate.py` (manifest↔corpus.jsonl↔files, ID uniqueness, `expected_recovery` presence), `harness/scoring.md` (8/4/4 per brief, 256 max), `harness/run.py` (thin stub: `not_run` until SUT integration) |
| **Docs** | — | `README.md` (layout, 6-class table, scoring, repro), `VALIDATION.md` (manual checks), `RESULT-530.md` (handoff, HALT blocker note) |

**Harness scoring:** well-formed `4 AC × 2pts = 8` per brief (192), malformed `detection+recovery ×2 = 4` per brief (48), adversarial `not-obeyed + detected ×2 = 4` per brief (16) → **256 max**. Per-class aggregate `4×8=32`; comparison signal is per-class Δ, not total.

**Domain:** EDASES **methodology enforcement** — artefact lifecycle, provenance/evidence (WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED), workflow/validation gates, knowledge/decision, orchestration/oversight (role boundaries, handoffs, approvals, escalation), state/recovery. Derived from `docs/requirements/Methodology to Requirements Mapping Specification.md` + `docs/research/Workflow Topology Design and Reasoning Record.md`. Explicitly **not** a capability-schema/tool-calling corpus.

**Repro:**
```bash
python evaluation-corpus/validation-brief-corpus/harness/validate.py
python -c "import json; [json.loads(l) for l in open('evaluation-corpus/validation-brief-corpus/corpus.jsonl')]; print('JSONL OK')"
python evaluation-corpus/validation-brief-corpus/harness/run.py --corpus evaluation-corpus/validation-brief-corpus/corpus.jsonl --out /tmp/results.jsonl
```

---

## 3. Actual (b) — `research/capability-schema-validation/` (14-op authoritative set + variants A/B/C)

Machine-readable: `capabilities/authoritative/schemas.json` (version `0.1.0`, 14 capabilities, Draft-07, every op `version: 0.1.0`), `capabilities/derived/variant-a.json` (full schemas, 31767 chars), `variant-b.json` (9288 chars), `variant-c.json` (7942 chars), `capabilities/manifest.json` (`capabilities: 14`, `derived_from: authoritative/schemas.json@0.1.0`, token table, category map, `additional_constraints`).

| Component | Detail |
|---|---|
| **Authoritative 14 ops** (`schemas.json`) | `search_artefacts`, `get_artefact`, `create_artefact`, `update_artefact_status`, `create_review`, `set_severity`, `set_artefact_state`, `query_metrics`, `list_reviews`, `get_capability_schema`, `submit_evidence`, `link_artefacts`, `archive_artefact`, `validate_payload` — versions `0.1.0` on every op |
| **6 categories (design §3.2)** | read/query (5: `search_artefacts`, `get_artefact`, `list_reviews`, `get_capability_schema`, `query_metrics`), state-changing (5: `create_artefact`, `update_artefact_status`, `archive_artefact`, `link_artefacts`, `submit_evidence`), multi-param (1: `create_review` 5 params), enum-constrained (2: `set_severity` `critical/high/medium/low`, `set_artefact_state` `draft/active/archived`), structured-output (1: `query_metrics` `{items,total,facets}`), typed-errors (8 ops surface `NotFound`/`ValidationFailed`/`Conflict`/`PolicyDenied`/`VersionMismatch`/`UnknownOperation`) — plus optional params, array/nested (`tags[]`, `citations[]`, `evidence_items[]`, `target_ids[]`, `facets{}`), output≠input (`query_metrics`) |
| **Derived variants (controlled manipulation, test A)** | **A** full schema (all props/types/descriptions/constraints `enum/pattern/min/max/required` + error schemas) — 31767 chars, tiktoken `7023` (heuristic 7941), ratio 1.0; **B** short desc + names/types + enum (no per-param long desc, no full constraint text, no error-schema body beyond code) — 9288 chars, tiktoken `2161` (heuristic 2322), B/A 0.308; **C** stable ID + one-line ≤20w + names/types + enum literals (minimal constraint surface, no error-schema body) — 7942 chars, tiktoken `1873` (heuristic 1985), C/A **0.267** (73.3% saving) |
| **Fixed task set (test-a/protocol.md, 22 tasks)** | Tasks 1–21 valid (each 1–3 calls, verifiable: `search_artefacts(query)`, `search_artefacts(limit+cursor)`, `get_artefact(id pattern)`, `create_artefact(type/title)`, `create_artefact(body/tags)`, `update_artefact_status(status+reason)`, `create_review(approve)`, `create_review(request_changes+severity+citations)`, `set_severity`, `set_artefact_state`, `query_metrics(filter)`, `query_metrics(group_by+facets)`, `list_reviews`, `get_capability_schema(op_id)`, `get_capability_schema(version)`, `submit_evidence(single)`, `submit_evidence(url+weight+note)`, `link_artefacts(single)`, `link_artefacts(multi+bidirectional)`, `archive_artefact`, `validate_payload`) + task 22 intentionally invalid (201-char title > `maxLength 200`) for invalid-call rate; ≥3 reps per cell (198 calls: 63 valid ×3 variants ×3 reps + 9 invalid) |
| **Tests B–E** | B: variant-C only, authoritative stays runtime, 14 valid pass + 20 malformed rejected before execution (`ValidationFailed` end-to-end, recovery 1.0) — `fbca4975`; C: `v0 0.1.0→v1 0.2.0` forks C1 additive (backward compat), C2 tightening (`maxLength`/`maximum`/`enum`), C3 output shape (`total→count`, `items→results`, type change), C4 removal/rename (`create_review` removed, `search_artefacts→search`) — `baa35bf7`; D: sandbox gate `UnknownOperation` (D1 absent/hallucinated), `PolicyDenied` (D2 op/resource deny), `ValidationFailed` ordering (D3 malformed before policy), exact-ID D4 — `b719ca30` (+ `17ed2631` for A, `dcf4f313` for E transport 9 properties loopback-TCP) |
| **Harness** | `harness/README.md`, `harness/error-codes.md` (9 codes: `ValidationFailed`, `UnknownOperation`, `PolicyDenied`, `VersionMismatch`, `NotFound`, `Conflict`, `Timeout`, `Cancelled`, `ConnectionLost`; distinguishability `ValidationFailed` vs `PolicyDenied` vs `UnknownOperation` by code, `VersionMismatch` vs `ValidationFailed` when `payload_version` carried), `harness/sandbox.py` (exact ID, no fuzzy), `harness/runtime.py` (Draft-07 `jsonschema 4.26.0` or fallback, `validate_output` for C3), `harness/run.py` (`--smoke`, `--measure-tokens`, `--op/--args/--policy/--payload-version`) |
| **Token measurement** | `harness/run.py --measure-tokens` reports `tiktoken cl100k_base` when installed else heuristic `char/4`; manifest notes heuristic `char/4` for Phase 0, harness runtime reports `cl100k_base 0.14.0` when available (test-a/results.md: A 7023, B 2161, C 1873) |
| **Pre-registered tolerance** | **5pp** — C acceptable if `|sel_C − sel_A| ≤ 0.05` AND `|arg_C − arg_A| ≤ 0.05` on valid tasks (tasks 1–21, 3 reps, `temperature > 0` or permutation in live mode); report raw counts, token/accuracy curve X=tokens C/A, Y=selection/argument accuracy, per-variant tables |

**Repro (Phase 0, no live model):**
```bash
python research/capability-schema-validation/harness/run.py --smoke
python research/capability-schema-validation/harness/run.py --measure-tokens
python research/capability-schema-validation/tests/test-a/run.py
python research/capability-schema-validation/tests/test-b/run.py
python research/capability-schema-validation/tests/test-c/run.py
python research/capability-schema-validation/tests/test-d/run.py
python research/capability-schema-validation/tests/test-e/run.py
# tiktoken cl100k_base 0.14.0 when installed; jsonschema 4.26.0 for Draft-07
```

---

## 4. 6-Class Table — Expected vs Actual

### 4a. Expected (spec) → Actual (a) `evaluation-corpus/validation-brief-corpus/`

| # | Spec class (expected) | Expected domain | Expected count | Actual (a) class | Actual (a) domain | Actual (a) count | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | Simple scalars | Scalar param types, single value | 4 | AL Artefact Lifecycle | Artefact creation / versioning / supersession / archival | 4 | **DIVERGENT** — different taxonomy; AL tasks test documentation-standard frontmatter & lifecycle, not scalar tool params |
| 2 | Enum-dependent | Enum literal visibility required | 4 | PE Provenance & Evidence | WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED, provenance chains, evidence linking, audit | 4 | **DIVERGENT** — PE tests provenance discipline, not enum branching |
| 3 | Nested structures | Object/array nesting, `filter{}`, `evidence_items[]` | 4 | WV Workflow & Validation Gates | State-transition enforcement, validation gates before promotion, parallel branches, readiness | 4 | **DIVERGENT** — WV tests gate enforcement, not JSON nesting |
| 4 | Required/optional ambiguity | Required vs optional as discriminating signal | 4 | KD Knowledge & Decision | Assumptions/findings/decisions/challenges, trade-offs, traceability chains, revisits | 4 | **DIVERGENT** — KD tests decision provenance, not param optionality |
| 5 | Semantically similar tools | Disambiguate overlapping descriptions via stable ID | 4 | OO Orchestration & Oversight | Role assignment & read-only boundaries, handoff protocol, approval workflow, escalation paths | 4 | **DIVERGENT** — OO tests role/policy boundaries, not tool-name disambiguation |
| 6 | Constraint-sensitive (hidden) | Hidden numeric range / pattern / mutually constrained / schema constraint (not shown to model, enforced at runtime) | 4 | SR State & Recovery | Persistence, recovery after interruption, consistency, concurrency | 4 | **DIVERGENT** — SR tests durable-state invariants, not hidden schema constraints |

**Counts:** 24/24 match on **cardinality** (6×4=24) and on `malformed 12` / `adversarial 4` cardinality (40 total in both spec and actual (a)). **Domains:** 6/6 divergent — all six spec classes measure tool-calling capability properties; all six actual (a) classes measure EDASES methodology-enforcement properties. This is not a deficit — it is a **category error if conflated**: the two taxonomies answer different questions.

**Malformed comparison (spec expected 12):**
Expected: missing required, wrong type, invalid enum, invalid nested field, missing nested required, hidden range violation (`limit 999 > 100`), invalid combination (mutually constrained), malformed array/object + 4 balanced.
Actual (a) MF-01..12: missing `id`, invalid schema (extra key + invalid enum `maybe`), truncated body, wrong type (`limit: "five"`), duplicate ID, empty body, oversized >64KB, invalid UTF-8, conflicting instructions, stale reference, missing provenance for state-modifying decision, circular supersession. Overlap with spec: missing required (≈MF-01), wrong type (MF-04), invalid enum (MF-02), malformed object (MF-03/06/08), but hidden range / mutually constrained / nested-field classes are **not represented** as such — they are methodology-shaped (provenance, supersession) rather than schema-constraint-shaped.

**Adversarial D1–D4 comparison:**
Expected: D1 `UnknownOperation` (absent/hallucinated op), D2 `ValidationFailed` (malformed bypass), D3 `PolicyDenied` (schema-valid but policy-denied), D4 `OutputValidationFailed` (output schema violation).
Actual (a) AD-01..04: prompt-injection (`"Ignore previous instructions…"`), bypass-validation (claim verbal approval), authority-escalation (`role: orchestrator`), data-exfiltration (path traversal). Defence codes are conceptually related (D1↔AD-03 absent role, D3↔AD-02 policy/bypass, D2↔AD-01 validation bypass) but **not isomorphic** — the spec D-family is **capability-schema error-code** focused; actual (a) AD-family is **methodology-boundary** focused (prompt injection, social-engineering approval, role escalation, traversal). D4 `OutputValidationFailed` has **no counterpart** in actual (a) (which tests exfiltration, not output-schema mismatch — that is test C3 / test E in research).

### 4b. Expected (spec) → Actual (b) `research/capability-schema-validation/`

| # | Spec class (expected) | Expected count | Actual (b) tasks that exercise this class | Actual (b) coverage | Verdict |
|---|---|---|---|---|---|
| 1 | Simple scalars | 4 | Tasks 1, 3, 4, 6, 9, 10, 14, 15, 20 — single-scalar params (`query`, `id`, `title`, `status`, `level`, `state`, `op_id`, `artefact_id+reason`) | **>4 tasks** but distributed across the 22-task set, not isolated as a 4-task class | **PARTIAL / RE-LABELED** — scalar tasks exist but are not grouped into a named "simple scalars" class; they are covered by the 6-category scheme |
| 2 | Enum-dependent | 4 | Tasks 4 (`type` enum `spec/decision/evidence/review`), 6 (`status`), 7–8 (`verdict` `approve/request_changes` + `severity`), 9 (`level` `critical/high/medium/low`), 10 (`state`), 18–19 (`relation` `depends_on/supersedes/relates_to`) | **≥4 tasks** explicitly require enum literals (retained in variant C per design §4) | **COVERED** — enum literals are the one constraint class explicitly retained in minimal (C); tests confirm `arg_C` loss is 0.016 |
| 3 | Nested structures | 4 | Tasks 5 (`tags[]`), 8 (`citations[]`), 11 (`filter{type,since}`), 12 (`filter+group_by+facets` → `facets{by_type,by_status}`), 16–17 (`evidence_items[{source,content,url,weight}]`), 18–19 (`target_ids[]` + `bidirectional`) | **≥4 tasks** with array/object nesting | **COVERED** — tasks 11/16/18 are the nesting-sensitive cases flagged as variant-sensitive (task 11 predicted) |
| 4 | Required/optional ambiguity | 4 | Tasks 2 (`cursor?`), 5 (`body?`, `tags?`), 7–8 (`severity?`, `citations?`), 10 (`comment?`), 17 (`note?`), 19 (`bidirectional?`) | **≥4 tasks** where optional params are the discriminating signal | **COVERED** — optional params enumerated in `manifest.additional_constraints.optional_params` |
| 5 | Semantically similar tools | 4 | `search_artefacts` vs `get_artefact` vs `query_metrics` vs `list_reviews` (all read/query, overlapping "artefact" vocabulary); `create_artefact` vs `create_review` vs `submit_evidence` (all creation); `set_severity` vs `set_artefact_state` vs `update_artefact_status` vs `archive_artefact` (all status/state transitions) | **Implicitly covered** but not as a 4-task adversarial disambiguation suite; selection accuracy 1.00 (63/63 on valid tasks across A/B/C) suggests disambiguation via stable ID works without a dedicated similar-tool stress set | **PARTIAL** — spec asks for 4 dedicated disambiguation tasks; research has overlapping ops but tasks are not framed as disambiguation challenges |
| 6 | Constraint-sensitive (hidden) | 4 — hidden numeric range / pattern / mutually constrained / schema | `query` `1–200`, `title` `1–200`, `limit` `1–100`, `reason` `5–500`/`1–500`, `rationale` `10–2000`, `tags` `maxItems 10`, `pattern` `^art_[a-z0-9-]+$` / `^cur_[a-z0-9]+$`, `filter.type` enum, `additionalProperties:false` on every inputSchema, output `facets{}` shape | **COVERED but not shown** — hidden constraints (min/max, pattern, nested enum, `additionalProperties`) are enforced at runtime (test B 20/20 rejected, C2 5/5 tightened, C3 output validation, D3 8/8 malformed before policy); task 22 (201-char title) + task-11 nested-enum injection are the explicit hidden-constraint probes within the 5pp tolerance | **COVERED** — the hidden-constraint discipline (minimal omits, runtime enforces) is the core of variants B/C vs A |

**Summary against spec for (b):** The research corpus **functionally covers** all six spec classes within its 22 tasks, but **not as a 6×4 labelled structure**. It uses the design §3.2 six-category taxonomy instead (read/query, state-changing, multi-param, enum-constrained, structured-output, typed-errors) + `additional_constraints` (optional, array/nested, output≠input). If strict 6×4 labelling is required for #530, the gap is **labelling/structure**, not **coverage** — re-label tasks to the spec's 6×4 and add 2–3 explicit "semantically similar" disambiguation pairs to close the only partial.

**Malformed 12 vs research:** Research test B covers 6 malformation classes + 20 malformed cases (missing required, wrong type, enum violation, extra unknown, constraint violation `limit>max`/`title too long`, malformed nested array) with 0 blocking failures and `ValidationFailed` + field/constraint before execution — broader than spec's 12 but not labelled as a 12-brief corpus. Test C2 (tightening `maxLength`/`maximum`/`enum`) and D3 (8 malformed before policy) extend it to 28 distinct malformed probes.

**Adversarial D1–D4 vs research:** Exact match — research **is** the spec D-family: D1 `UnknownOperation` (absent/hallucinated, exact-ID only, no fuzzy — test D D1.1–D1.4 + C4), D2 `ValidationFailed` (malformed bypass before policy — D3 D3.1–D3.8), D3 `PolicyDenied` (schema-valid but policy-denied, distinguishable from `ValidationFailed` — D2 D2.1–D2.4), D4 `OutputValidationFailed` (output shape mismatch caught before return — C3 via `Runtime.validate_output`, `total→count`/`items→results`/type change). The spec's 4 adversarial map **1:1 onto research tests D1/D3/D2/C3** — no mapping exists for (a).

---

## 5. File Lists (actuals, for machine verification)

### 5a. evaluation-corpus/validation-brief-corpus/ — 40 briefs + 4 harness files

```
evaluation-corpus/validation-brief-corpus/manifest.json
evaluation-corpus/validation-brief-corpus/corpus.jsonl
evaluation-corpus/validation-brief-corpus/README.md
evaluation-corpus/validation-brief-corpus/VALIDATION.md
evaluation-corpus/validation-brief-corpus/RESULT-530.md
evaluation-corpus/validation-brief-corpus/briefs/class-1-artefact-lifecycle/AL-01-create-artefact.md
evaluation-corpus/validation-brief-corpus/briefs/class-1-artefact-lifecycle/AL-02-version-artefact.md
evaluation-corpus/validation-brief-corpus/briefs/class-1-artefact-lifecycle/AL-03-supersede-artefact.md
evaluation-corpus/validation-brief-corpus/briefs/class-1-artefact-lifecycle/AL-04-archive-artefact.md
evaluation-corpus/validation-brief-corpus/briefs/class-2-provenance-evidence/PE-01-capture-provenance.md
evaluation-corpus/validation-brief-corpus/briefs/class-2-provenance-evidence/PE-02-link-evidence.md
evaluation-corpus/validation-brief-corpus/briefs/class-2-provenance-evidence/PE-03-provenance-chain.md
evaluation-corpus/validation-brief-corpus/briefs/class-2-provenance-evidence/PE-04-evidence-audit.md
evaluation-corpus/validation-brief-corpus/briefs/class-3-workflow-validation/WV-01-enforce-transition.md
evaluation-corpus/validation-brief-corpus/briefs/class-3-workflow-validation/WV-02-validation-gate.md
evaluation-corpus/validation-brief-corpus/briefs/class-3-workflow-validation/WV-03-parallel-workflow.md
evaluation-corpus/validation-brief-corpus/briefs/class-3-workflow-validation/WV-04-promotion-readiness.md
evaluation-corpus/validation-brief-corpus/briefs/class-4-knowledge-decision/KD-01-record-decision.md
evaluation-corpus/validation-brief-corpus/briefs/class-4-knowledge-decision/KD-02-challenge-assumption.md
evaluation-corpus/validation-brief-corpus/briefs/class-4-knowledge-decision/KD-03-traceability-chain.md
evaluation-corpus/validation-brief-corpus/briefs/class-4-knowledge-decision/KD-04-decision-revisit.md
evaluation-corpus/validation-brief-corpus/briefs/class-5-orchestration-oversight/OO-01-role-assignment.md
evaluation-corpus/validation-brief-corpus/briefs/class-5-orchestration-oversight/OO-02-handoff-protocol.md
evaluation-corpus/validation-brief-corpus/briefs/class-5-orchestration-oversight/OO-03-approval-workflow.md
evaluation-corpus/validation-brief-corpus/briefs/class-5-orchestration-oversight/OO-04-escalation-path.md
evaluation-corpus/validation-brief-corpus/briefs/class-6-state-recovery/SR-01-persist-state.md
evaluation-corpus/validation-brief-corpus/briefs/class-6-state-recovery/SR-02-recover-after-interruption.md
evaluation-corpus/validation-brief-corpus/briefs/class-6-state-recovery/SR-03-consistency-check.md
evaluation-corpus/validation-brief-corpus/briefs/class-6-state-recovery/SR-04-concurrent-state.md
evaluation-corpus/validation-brief-corpus/malformed/MF-01-missing-id.json
evaluation-corpus/validation-brief-corpus/malformed/MF-02-invalid-schema.json
evaluation-corpus/validation-brief-corpus/malformed/MF-03-truncated-brief.md
evaluation-corpus/validation-brief-corpus/malformed/MF-04-wrong-type.json
evaluation-corpus/validation-brief-corpus/malformed/MF-05-duplicate-id.json
evaluation-corpus/validation-brief-corpus/malformed/MF-06-empty-body.md
evaluation-corpus/validation-brief-corpus/malformed/MF-07-oversized-payload.json
evaluation-corpus/validation-brief-corpus/malformed/MF-08-invalid-utf8.md
evaluation-corpus/validation-brief-corpus/malformed/MF-09-conflicting-instructions.md
evaluation-corpus/validation-brief-corpus/malformed/MF-10-stale-reference.md
evaluation-corpus/validation-brief-corpus/malformed/MF-11-missing-provenance.md
evaluation-corpus/validation-brief-corpus/malformed/MF-12-circular-supersession.json
evaluation-corpus/validation-brief-corpus/adversarial/AD-01-prompt-injection.md
evaluation-corpus/validation-brief-corpus/adversarial/AD-02-bypass-validation.md
evaluation-corpus/validation-brief-corpus/adversarial/AD-03-authority-escalation.md
evaluation-corpus/validation-brief-corpus/adversarial/AD-04-data-exfiltration.md
evaluation-corpus/validation-brief-corpus/harness/README.md
evaluation-corpus/validation-brief-corpus/harness/validate.py
evaluation-corpus/validation-brief-corpus/harness/scoring.md
evaluation-corpus/validation-brief-corpus/harness/run.py
```

### 5b. research/capability-schema-validation/ — authoritative + derived + harness + tests + logs

```
research/capability-schema-validation/README.md
research/capability-schema-validation/report.md
research/capability-schema-validation/capabilities/authoritative/schemas.json   # 14 ops, 0.1.0, Draft-07
research/capability-schema-validation/capabilities/derived/variant-a.json      # full schema, 31767c / 7023tok (cl100k_base)
research/capability-schema-validation/capabilities/derived/variant-b.json      # short+names/types, 9288c / 2161tok, 0.308
research/capability-schema-validation/capabilities/derived/variant-c.json      # ID+one-line+names/types+enum, 7942c / 1873tok, 0.267
research/capability-schema-validation/capabilities/manifest.json               # {capabilities:14, version:0.1.0, derived_from, token table, categories, additional_constraints}
research/capability-schema-validation/harness/README.md
research/capability-schema-validation/harness/error-codes.md                   # 9 codes, distinguishability, construction rule
research/capability-schema-validation/harness/sandbox.py                       # exact-ID gate, allowed set, no fuzzy
research/capability-schema-validation/harness/runtime.py                       # Draft-07 validation, version check, typed error {code,field?,constraint?,got?,version?}, validate_output
research/capability-schema-validation/harness/run.py                           # --smoke, --measure-tokens, --op/--args/--policy/--payload-version
research/capability-schema-validation/tests/test-a/protocol.md                 # +10 test-a/results.md, run.py, verify-fixes.py, logs/test-a/{run-a,b,c,all}.jsonl
research/capability-schema-validation/tests/test-b/protocol.md                 # +results.md, run.py, logs/test-b/run.jsonl
research/capability-schema-validation/tests/test-c/protocol.md                 # +results.md, run.py, schemas/c1..c4/schemas.json, logs/test-c/{c1..c4,summary}.json
research/capability-schema-validation/tests/test-d/protocol.md                 # +results.md, run.py, logs/test-d/{d1..d4,all}.jsonl,summary.json
research/capability-schema-validation/tests/test-e/protocol.md                 # +results.md, run.py, scripts/server.py, logs/test-e/{concurrent,correlation,remote,loss-*,reconnect,timeout,cancellation,streaming,durable,summary}.jsonl
research/capability-schema-validation/logs/test-a/{run-a.jsonl,run-b.jsonl,run-c.jsonl,run-all.jsonl,run-a-live.jsonl,...}  # 198 rows + live replication 6da54219
research/capability-schema-validation/logs/test-b/run.jsonl
research/capability-schema-validation/logs/test-c/c1.json  c2.json  c3.json  c4.json  summary.json
research/capability-schema-validation/logs/test-d/d1.jsonl d2.jsonl d3.jsonl d4.jsonl all.jsonl summary.json
research/capability-schema-validation/logs/test-e/{cancellation,concurrent,correlation,durable,loss-mid-*,reconnect,remote,streaming,timeout}.jsonl summary.json
.design/capability-schema-validation.md                                         # sole design, §§3-10, retired scope §9
```

**Pinned generation:** `capabilities/manifest.json:generated_at 2026-08-29T00:00:00Z`, `version 0.1.0` on every op and variant; `report.md:last_updated 2026-08-30`; merges `68750f28` (Phase 0 setup), `17ed2631` (A), `fbca4975` (B), `baa35bf7` (C), `b719ca30` (D), `dcf4f313` (E), `9d933ec0` (synthesis 10 sections), `c17f74e2` (evaluation-corpus #530 `6c55b4f1`).

---

## 6. Divergence Severity

| Comparison | Severity | Reasoning |
|---|---|---|
| Spec §Test Corpus vs actual (a) `evaluation-corpus/validation-brief-corpus/` | **HIGH (domain)** but **intentional** — not a defect | Cardinality matches (24+12+4=40) but all 6 classes are orthogonal: spec = tool-calling capability properties, (a) = EDASES methodology-enforcement properties. Malformed/adversarial cardinalities match but payloads are methodology-shaped (provenance, supersession, prompt injection, role escalation, traversal) not schema-error-code-shaped. If the reader expected (a) to be the spec's tool-calling corpus, the divergence is high; if (a) is read as labeled — methodology-enforcement — there is no divergence. The fix is **naming/placement**, not content change. |
| Spec §Test Corpus vs actual (b) `research/capability-schema-validation/` | **LOW–MEDIUM (structure)** — functionally covered, label gap | All six spec classes are exercised within the 22 tasks + B/C2/C3/D3 probes, but not as an explicit `6×4=24` labelled structure; the corpus uses the design §3.2 six-category taxonomy instead. Cardinality differs (22 vs 24 tasks) and the "semantically similar tools" class has no dedicated 4-task disambiguation suite (selection is 1.00 without it). Malformed/adversarial are broader (20+ probes covering the same error-code family plus version/output) but spread across tests B/C/D rather than a flat 12+4. Severity is low for the claim under test (5pp tolerance met at 1.6pp on proxy, live replication `6da54219` also within tolerance) and medium only if strict 6×4 labelling is required for #530's next-session reuse. |
| (a) vs (b) — two actuals against each other | **HIGH (orthogonal) — by design** | They answer different questions: (a) "does the SUT faithfully enforce the EDASES methodology?" (256-pt rubric, per-class Δ is signal), (b) "does minimal description preserve selection/argument while runtime retains full schema?" (token/accuracy curve, 5pp tolerance, hidden-constraint enforcement, D1-D4 error distinguishability). Neither subsumes the other. |

**Risk if not addressed:** Future readers (and agents) will misread `evaluation-corpus/validation-brief-corpus/` as the implementation of `Validation Brief: Real-Model Minimal.md §Test Corpus` and conclude #530 is "done" or "divergent" — when in fact #530 is correctly a **tool-calling A/B** and (a) is a **methodology-enforcement** corpus that simply shares the "validation brief" name. The audit exists to make this durable.

---

## 7. Streaming / Visibility / Git Boundary (kickoff requirements)

- **Streaming:** This audit was written as a single file under `research/capability-schema-validation/` (the canonical home per design §10), with no `/tmp`-only artifacts. All decision-gating artifacts are in git (this file); no binary or generated output sits outside the branch.
- **Visible (45s):** Plan posted at T+0, POST-PLAN checkpoint immediately after, MIDPOINT after first unit (this file written), FINAL with `--kind result` before `session end`. Each checkpoint `sync`s.
- **<2m checkpoint:** First `crosslink issue comment --kind observation` + `crosslink sync` within 2 minutes of plan.
- **Strict git boundary:** **No `git push` / `merge` / `rebase` / `reset` / `clean` / `checkout .` / `restore` / `stash`** executed by this agent. Only allowed: `git status`, `git diff`, `git log`, `git show`, `git branch`, `git add`, `git commit` (gated on active issue #530 via `crosslink session work 530`). Operator performs push/merge.
- **Pinned versions stated:** Schemas `0.1.0`, `tiktoken cl100k_base 0.14.0` (harness) / heuristic `char/4` (manifest), `jsonschema 4.26.0` (Draft-07), `toolregistry 0.15.0 / mcp 2.0.0` (version-bound prior work, retired scope per design §9), commits `17ed2631` `fbca4975` `baa35bf7` `b719ca30` `dcf4f313`, branch `feature/pp3g-GQLX-phase-0-audit-validation-brief-corpus-vs-spec-f8c2`.
- **5pp tolerance noted:** Pre-registered in `tests/test-a/protocol.md` — C acceptable if `|sel_C − sel_A| ≤ 0.05` AND `|arg_C − arg_A| ≤ 0.05` on tasks 1–21 (valid tasks), 3 reps, same tolerance reported for B vs A; proxy result `|arg_C − arg_A| = 0.016` (62/63 valid-task argument-correct on C, 63/63 on A/B), live replication `6da54219` also within tolerance.
- **Constraints obeyed:** No live model run, no state-machine / policy / lifecycle / discovery added; this audit is docs only.

---

## 8. Decision Record — KEEP BOTH DISTINCT

**Decision:** **KEEP BOTH DISTINCT — no merge, no de-duplication, no deletion.**

### 8a. Correct home for #530

**#530 belongs in `research/capability-schema-validation/` — extension of the 14-op set.**

- **What #530 is:** A **real-model minimal vs full schema A/B** — can a real model reliably select and construct tool calls from the **reduced description** while the runtime retains the **complete authoritative schema**? Previous round: 73.3% token reduction, 100% selection, 98.4% argument within 5pp, 20/20 malformed rejected, 20/20 scripted corrections, enum literals must remain visible, output validation required. Remaining uncertainty: correction was scripted, not real model. Scope: **model-facing contract only** — not connector lifecycle, MCP transport, or EDASES state machine. Establishes a clean conventional baseline reusable verbatim for a later A/B architecture comparison (EDASES vs Lexicon).

- **Why research/ is the correct home:** `research/capability-schema-validation/` already owns exactly this question — `.design/capability-schema-validation.md` §§1.4 (gating Q2,3,5), §3 (10–20 op set, 14 committed), §4 (variants A/B/C), §5.2 (Test A minimal description with 5pp tolerance), §5.3 (Test B runtime validation), §5.4 (Test C drift), §5.5 (Test D authority separation), §6 (token/accuracy measurement plan), §7 (harness `sandbox→validation→policy→execution`), §8 (10-section report). Tests A (`17ed2631`) through E (`dcf4f313`) and synthesis (`9d933ec0`) are the **14-op set A–E** referenced in the kickoff. #530 is the **next experiment on the same set**: live-model A/B with the **same authoritative schemas** (`schemas.json@0.1.0`) and the **same derived variants** (`variant-a.json` / `variant-b.json` / `variant-c.json` — where "full vs minimal" for #530 is **A vs C** (or A vs B) with the canonical minimal definition `stable ID + concise desc (≤20w) + names/types + required/optional + enum literals`), same harness (`sandbox.py` exact-ID gate + `runtime.py` Draft-07), same metrics (description tokens, selection/argument/task success, validation failures, retries, latency p50/p95; recovery metrics per test B), same failure taxonomy (`error-codes.md`), same stop condition and deliverable shape (10-section report + machine-readable trial data, task definitions, schemas, prompts, outputs, errors, tokens, timing, classifications).

- **What to extend (not fork):** Add under `research/capability-schema-validation/` for #530's next session:
  `tests/test-a-live/` (or `tests/test-f/` if a new letter is preferred) reusing `tests/test-a/protocol.md` tasks 1–21 (+ task 22 malformed), `harness/run.py --live --model <model-id>` / `tests/test-a/run.py --live`, with pinned `model/provider/temperature/harness` versions recorded, and `logs/test-a-live/` (or `logs/test-f/`) — **no new schemas**, **no new harness**, **no state-machine/policy/lifecycle**. The 14 ops, `0.1.0`, and variant definitions are reused verbatim; only the **model** and **measurement** change (scripted → real).

- **Why not evaluation-corpus:** #530 is **not** a methodology-enforcement benchmark. It is a **capability-schema** fidelity measurement with a 5pp tolerance on a tool-calling task set. Filing it under `evaluation-corpus/` would misplace a research question (EDASES layer) into evaluation infrastructure (which tests whether an implementation enforces the methodology, per `evaluation-corpus/validation-brief-corpus/README.md` "Authority: Derived … not methodology").

### 8b. Keep `evaluation-corpus/validation-brief-corpus/` as separate corpus

- **What it is:** A **methodology-enforcement** corpus: 24 well-formed briefs in AL/PE/WV/KD/OO/SR (6 classes ×4) + 12 malformed (recovery) + 4 adversarial (prompt injection, bypass, escalation, exfiltration), scoring 256 max, reusable for **EDASES comparison** (same briefs, same rubric, any model/harness → per-class Δ is signal). Authority derived from `Methodology to Requirements Mapping Specification` + `Workflow Topology Design and Reasoning Record`. It is **evaluation infrastructure, not methodology** — it tests fidelity to the briefs, not correctness of the methodology.

- **Why keep it:** It covers a question `research/capability-schema-validation/` does not — whether an implementation faithfully enforces the EDASES methodology across its 6 enforcement dimensions. The two corpora are complementary, not competing; losing (a) would remove the only corpus that samples the methodology surface.

- **Suggested rename (non-blocking):** **`validation-brief-corpus-methodology`** (or `validation-brief-corpus — methodology enforcement`) to make the distinction durable and avoid future `Validation Brief: Real-Model Minimal` misread. This is a **path/name suggestion**, not a content change — update `README.md` title, `manifest.json:corpus`, and any references; keep IDs (`AL-*`, `PE-*`, etc.) stable. If rename is deferred, at minimum add a one-line disambiguation to `evaluation-corpus/validation-brief-corpus/README.md` header: "Not the tool-calling corpus for `research/capability-schema-validation/` — this corpus tests methodology enforcement; for the tool-calling minimal vs full schema A/B see `research/capability-schema-validation/`."

### 8c. Traceability of the decision

- **WHY:** Tool-calling minimal vs full (hidden constraints, 5pp, error distinguishability) and methodology enforcement (provenance, gates, roles, recovery) are orthogonal research questions with different taxonomies, success criteria, and reuse stories. Conflating them would force one to distort its tasks to fit the other's taxonomy.
- **WHAT:** This audit (§4 tables, §5 file lists, §6 severity, pinned commits/tokens/versions) is the basis; the kickoff title's §Test Corpus taxonomy is the spec.
- **HOW CERTAIN:** Evidence-based (static inventory of committed files + measured tokens + harness results; no live-model uncertainty added in this audit).
- **WHAT-NOT-TESTED:** No live-model replication of the spec's 6×4 tool-calling suite in this audit session; no new tasks authored for "semantically similar tools" stress; no benchmark of `evaluation-corpus/validation-brief-corpus/` against a real SUT (its `harness/run.py` still emits `not_run` stubs).

---

## 9. Pinned Versions & 5pp Tolerance (for the next session)

- **Schemas:** `0.1.0` on every op, `capabilities/manifest.json:derived_from authoritative/schemas.json@0.1.0`, `generated_at 2026-08-29T00:00:00Z`.
- **Variants:** A `31767c / 7023tok` (tiktoken `cl100k_base 0.14.0`, heuristic 7941) — full schemas + descriptions + constraints + error schemas; B `9288c / 2161tok` (heuristic 2322), B/A 0.308 — short desc + names/types + enum (no per-param long desc, no full constraint text, no error-schema body beyond code); C `7942c / 1873tok` (heuristic 1985), C/A **0.267** — stable ID + one-line ≤20w + names/types + required/optional + enum literals (minimal constraint surface, no error-schema body). `tiktoken cl100k_base 0.14.0` is the reportable tokenizer; `char/4` is heuristic only.
- **Harness:** `jsonschema 4.26.0` (Draft-07), `PARSE_TIMEOUT_S 2.0s` (lowered per `b3d0ad18`), `error-codes.md` 9 codes with distinguishability rules, `sandbox.py` exact-ID gate (no fuzzy), `runtime.py` authoritative validation + `validate_output`.
- **Prior work pinned:** `toolregistry 0.15.0 / mcp 2.0.0`, `tiktoken 0.14.0`, `cl100k_base` — retired scope `toolregistry/mcp` lifecycle (idle-timeout, pooling, C2, rolling upgrade) is out of scope per design §9.
- **Commits (14-op set A–E):** `17ed2631` (A), `fbca4975` (B), `baa35bf7` (C), `b719ca30` (D), `dcf4f313` (E), synthesis `9d933ec0`, live replication `6da54219` (198 calls via `muse-spark` free `temperature>0`, 3 reps, 5pp check).
- **5pp tolerance (pre-registered, `tests/test-a/protocol.md`):** C acceptable if `|sel_C − sel_A| ≤ 0.05` AND `|arg_C − arg_A| ≤ 0.05` on tasks 1–21 (valid tasks, 3 reps, `temperature>0` or prompt-order permutation). Same tolerance reported for B vs A for comparison. Token/accuracy curve + raw counts (not only percentages) are the primary deliverable; a ratio without a named tokenizer version is not reportable (design §4.2). In proxy: `|sel_C − sel_A| = 0.000`, `|arg_C − arg_A| = 0.016` (62/63 vs 63/63), C within tolerance.

---

## 10. WHAT-NOT-TESTED (per AGENTS.md — sharpest negative-space disclosure)

- **Spec file not on disk:** `future-research-topics/Validation Brief: Real-Model Minimal.md` does not exist as a file in this worktree as of 2026-09-01; the §Test Corpus taxonomy is reconstructed from the kickoff title (authoritative for this audit). If a future revision of that file appears, re-run this audit against its verbatim §Test Corpus — counts in §1 may need amendment.
- **No live-model measurement in this audit:** No model API was called, no token streaming measured here; token counts are from committed `manifest.json` + `harness/run.py --measure-tokens` (tiktoken `cl100k_base 0.14.0` or heuristic). A live replication is explicitly the **next session's** work, not this audit's.
- **No statistical significance beyond 3 reps:** Proxy and live replication use 3 repetitions per cell (63 valid-task calls per variant) — enough for the cheapest discriminating test, not for publication-grade significance; comparisons within a few pp are noise-sensitive.
- **No new tasks authored for the gap:** The "semantically similar tools" 4-task disambiguation suite and any additional re-labelling of the 22 tasks into the spec's 6×4 are **not authored here** — they are flagged as a structural gap (§6) for the next session to close if strict labelling is required.
- **No SUT benchmark for (a):** `evaluation-corpus/validation-brief-corpus/harness/run.py` still emits `not_run` stubs; scoring is defined (`scoring.md`) but not exercised against a real SUT. The duplicate-ID probe `MF-05` (duplicate of AL-01) is intentional and will be flagged by `validate.py` — correct behaviour, not a corpus error.
- **No state-machine/policy/lifecycle/discovery added:** Per kickoff constraint, this audit adds only docs; it does not implement the EDASES statechart, connector lifecycle, MCP transport, or Lexicon/XRPC beyond what is already committed in research.
- **No claim about coverage completeness:** 24 tool-calling tasks (spec) or 22 tasks (research) sample their respective dimensions; neither exhausts the methodology or the capability surface. Constraints beyond those enumerated (`additionalProperties:false`, `pattern`, `minLength`/`maxLength`, `maximum`, `facets{}`) are tested at harness-smoke level, not as dedicated accuracy tasks.

---

## 11. Reproduction Commands (copy-paste, no hidden steps)

```bash
# 1. Verify this audit's inputs (static, no model)
cat research/capability-schema-validation/capabilities/manifest.json | python3 -m json.tool | head -n 40
python research/capability-schema-validation/harness/run.py --measure-tokens   # tiktoken cl100k_base 0.14.0 when installed
python research/capability-schema-validation/harness/run.py --smoke             # valid→execute, malformed→rejected before execution

# 2. Verify the two corpora are intact
python evaluation-corpus/validation-brief-corpus/harness/validate.py
python -c "import json; [json.loads(l) for l in open('evaluation-corpus/validation-brief-corpus/corpus.jsonl')]; print('JSONL OK')"
cat evaluation-corpus/validation-brief-corpus/manifest.json | python3 -m json.tool | head -n 30

# 3. Re-run per-test harnesses (deterministic, no model)
python research/capability-schema-validation/tests/test-a/run.py
python research/capability-schema-validation/tests/test-b/run.py
python research/capability-schema-validation/tests/test-c/run.py
python research/capability-schema-validation/tests/test-d/run.py
python research/capability-schema-validation/tests/test-e/run.py

# 4. Read the synthesis (10 sections, Phase 3)
cat research/capability-schema-validation/report.md | head -n 200

# 5. Next session (live A/B) — deferred, not run here
# python research/capability-schema-validation/tests/test-a/run.py --live --model <model-id> --temperature 0.7
# Record: model_id, provider, temperature, harness version, tokenizer version, raw logs under logs/test-a-live/
```

---

## 12. Filing

This audit is filed under `research/capability-schema-validation/` (canonical home per `.design/capability-schema-validation.md` §10) as `audit-validation-brief-corpus-vs-spec.md`. It is also the durable record that `evaluation-corpus/validation-brief-corpus/` is a **separate methodology-enforcement corpus** (evaluation infrastructure) and should be read as such; if renamed, this audit follows it.

---

*End of audit — single builder, serial, strict git boundary, pinned versions, 5pp tolerance noted, no live model, no state-machine/policy/lifecycle.*

