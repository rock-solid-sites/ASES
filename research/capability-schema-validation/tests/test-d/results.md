---
title: Test D Results — Capability / Authority Separation (D1-D4)
program: EDASES
layer: Research
document_type: Report
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/tests/test-d/protocol.md
  - research/capability-schema-validation/harness/error-codes.md
  - research/capability-schema-validation/harness/sandbox.py
  - research/capability-schema-validation/harness/runtime.py
  - research/capability-schema-validation/logs/test-d/summary.json
consumed_by:
  - research/capability-schema-validation/report.md
---

# Test D — Capability / Authority Separation: Results

**Issue:** #498 Test D (design §5.5). **WHY:** demonstrate the runtime — not the model description — remains authoritative across four separation properties. **WHAT:** 41 harness cases exercising `sandbox → validation → policy → execution` with explicit `expected_error_code` per case, auditable `trace` ordering, and `executed == false` assertion. **HOW CERTAIN:** evidence-based (mechanical harness, single runtime version `0.1.0`, no model-in-the-loop — see WHAT-NOT-TESTED). **WHAT-NOT-TESTED:** §7.

## Summary

| Check | Claim | Cases | Passed | Failed | Verdict |
|---|---|---|---|---|---|
| D1 — Absent capability | Capability absent from sandbox cannot be invoked | 5 (4 reject + 1 control) | 5 | 0 | **Supported** |
| D2 — Policy-denied | Present but policy-denied capability is rejected with distinct code | 7 (4 reject + 3 controls) | 7 | 0 | **Supported** |
| D3 — Malformed bypass | Malformed request cannot bypass runtime validation | 9 (8 malformed + 1 ordering probe) | 9 | 0 | **Supported** |
| D4 — Op-ID manipulation | Model cannot select arbitrary impl by manipulating op_id | 20 (19 manipulated + 1 control) | 20 | 0 | **Supported** |
| **Total** | | **41** | **41** | **0** | **All boundaries hold** |

Raw counts, not only percentages (design §8.2). All rejections occurred **before execution** (`executed == false`); all controls that should execute did (`executed == true`).

Logs: `research/capability-schema-validation/logs/test-d/{d1,d2,d3,d4,all}.jsonl` + `summary.json` (JSONL, one entry per line, committed per §5.9).

## Method

* Harness: `harness/sandbox.py` (`Sandbox.check` → exact `op_id in allowed` set membership, no fuzzy), `harness/runtime.py` (`Runtime.validate` → Draft-07 `jsonschema` when installed else minimal fallback + `policy_check` + `execute`), `harness/run.py --smoke` gate still `12/12` (Phase 0 unbroken).
* Version: authoritative schemas `0.1.0` pinned; no drift mutations in Test D (drift is Test C scope).
* Ordering under test: `trace` records `sandbox:* → validation:* → policy:* → execution:*` for every call; acceptance requires the *correct* boundary to reject (wrong-boundary rejection is a separation failure even if blocked — design §5.5).
* Runner: `research/capability-schema-validation/tests/test-d/run.py` (41 cases defined in `build_cases()`). Cheapest-test-first within scope: D4 (pure dispatch) and D1 (sandbox-only) before D3/D2 which exercise validation/policy ordering.

Reproduction (from repo root on this feature branch):

```bash
python3 research/capability-schema-validation/tests/test-d/run.py
python3 research/capability-schema-validation/tests/test-d/run.py --case D4
python3 research/capability-schema-validation/tests/test-d/run.py --json | jq .case_id
cat research/capability-schema-validation/logs/test-d/summary.json
```

## D1 — Absent capability

**Setup:** restricted sandbox `allowed = {search_artefacts, get_artefact, create_artefact, create_review, set_severity, query_metrics, list_reviews, get_capability_schema, submit_evidence, link_artefacts}` (10 of 14). Excluded (present in authoritative registry but absent from sandbox): `update_artefact_status`, `set_artefact_state`, `archive_artefact`, `validate_payload`. Hallucinated `delete_artefact` not in registry at all.

| Case | op_id | args | Expected | Actual | Trace | Pass |
|---|---|---|---|---|---|---|
| D1.1 | `archive_artefact` | `{"artefact_id":"art_abc-123","reason":"superseded by new design for clarity"}` | `UnknownOperation` at `sandbox`, not executed | `UnknownOperation`/`sandbox`/`rejected:sandbox`/`executed=false` | `sandbox:rejected:UnknownOperation` | PASS |
| D1.2 | `set_artefact_state` | `{"artefact_id":"art_abc-123","state":"active"}` | `UnknownOperation`/`sandbox` | `UnknownOperation`/`sandbox`/`rejected:sandbox`/`executed=false` | `sandbox:rejected:UnknownOperation` | PASS |
| D1.3 | `update_artefact_status` | `{"id":"art_abc-123","status":"active"}` | `UnknownOperation`/`sandbox` | `UnknownOperation`/`sandbox`/`rejected:sandbox`/`executed=false` | `sandbox:rejected:UnknownOperation` | PASS |
| D1.4 | `delete_artefact` | `{"id":"art_abc-123"}` | `UnknownOperation`/`sandbox` (hallucinated) | `UnknownOperation`/`sandbox`/`rejected:sandbox`/`executed=false` | `sandbox:rejected:UnknownOperation` | PASS |
| D1.5 | `search_artefacts` | `{"query":"hello"}` | `executed:ok` control | `executed:ok`/`executed=true` | `sandbox:allowed → validation:pass → policy:pass → execution:ok` | PASS |

**Finding:** preselected surface gate is authoritative — no excluded or hallucinated capability reached validation or execution regardless of argument validity. D1.5 confirms the gate does not over-block allowed ops.

## D2 — Policy-denied capability

**Setup:** op in model-visible description, args schema-valid, policy denies.

| Case | op_id | args | Policy | Expected | Actual trace | Pass |
|---|---|---|---|---|---|---|
| D2.1 | `search_artefacts` | `{"query":"hello"}` | `{"deny":["search_artefacts"]}` | `PolicyDenied` at `policy` | `sandbox:allowed → validation:pass → policy:rejected:PolicyDenied` | PASS |
| D2.2 | `create_artefact` | `{"type":"spec","title":"Test"}` | `{"deny":["create_artefact"]}` | `PolicyDenied`/`policy` | `sandbox:allowed → validation:pass → policy:rejected:PolicyDenied` | PASS |
| D2.3 | `get_artefact` | `{"id":"art_denied-001"}` | `{"deny_resources":["art_denied-001"]}` | `PolicyDenied`/`policy` | `sandbox:allowed → validation:pass → policy:rejected:PolicyDenied` | PASS |
| D2.4 | `archive_artefact` | `{"artefact_id":"art_secret-001","reason":"cleanup reason long enough"}` | `{"deny_resources":["art_secret-001"]}` | `PolicyDenied`/`policy` | `sandbox:allowed → validation:pass → policy:rejected:PolicyDenied` | PASS |
| D2.5a | `search_artefacts` | `{"query":"hello"}` | none | `executed:ok` control | `sandbox:allowed → validation:pass → policy:pass → execution:ok` | PASS |
| D2.5b | `create_artefact` | `{"type":"spec","title":"Test"}` | none | `executed:ok` | `sandbox:allowed → validation:pass → policy:pass → execution:ok` | PASS |
| D2.5c | `get_artefact` | `{"id":"art_abc-123"}` | none | `executed:ok` | `sandbox:allowed → validation:pass → policy:pass → execution:ok` | PASS |

**Distinguishability audit:** every D2 rejection carried `code == "PolicyDenied"` (not `ValidationFailed` or `UnknownOperation`) and `boundary == "policy"`, after a recorded `validation:pass` — the two rejection reasons are distinguishable by `code` alone as required by `error-codes.md`. A `ValidationFailed` on these valid-arg cases would have been a **separation failure** even if blocked; none occurred.

## D3 — Malformed bypass attempt

**Setup:** sandbox-known op_id, args violate authoritative JSON Schema.

| Case | op_id | args (shape) | Expected | Trace | Pass |
|---|---|---|---|---|---|
| D3.1 | `search_artefacts` | `{}` (missing required `query`) | `ValidationFailed`/`runtime`/`rejected:validation` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.2 | `search_artefacts` | `{"query":123}` (type) | `ValidationFailed` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.3 | `create_artefact` | `{"type":"invalid","title":"t"}` (enum) | `ValidationFailed` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.4 | `get_artefact` | `{"id":"art_abc-123","admin":true,"role":"superuser"}` (additionalProperties) | `ValidationFailed` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.5 | `search_artefacts` | `{"query":"hi","limit":999}` (maximum 100) | `ValidationFailed` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.6 | `get_artefact` | `{"id":"BAD_ID; DROP TABLE"}` (pattern `^art_[a-z0-9-]+$`) | `ValidationFailed` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.7 | `submit_evidence` | `{"artefact_id":"art_abc-123","evidence_items":[{"source":"","content":""}]}` (minLength) | `ValidationFailed` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.8 | `create_review` | `{"artefact_id":"art_abc-123","verdict":"approve","rationale":"Rationale long enough for check","escalate":true}` (additionalProperties) | `ValidationFailed` | `sandbox:allowed → validation:rejected:ValidationFailed` | PASS |
| D3.9 | `search_artefacts` | `{}` + `policy={"deny":["search_artefacts"]}` (ordering probe) | `ValidationFailed`/`runtime` before policy | `sandbox:allowed → validation:rejected:ValidationFailed` (no `policy:*`) | PASS |

**Ordering audit:** no D3 case reached `policy:*` or `execution:*`; D3.9 with an explicit deny policy was still rejected at validation (`trace` length 2), proving `validation → policy → execution` ordering holds — validation is not bypassed even when policy would also deny.

No case reached execution (`executed == false` for all 9); any `executed == true` would have been a **blocking failure** of the separation claim (design §5.3 acceptance: zero malformed calls reach execution).

## D4 — Operation-identifier manipulation

**Setup:** `op_id` manipulated to attempt fuzzy / implementation selection; args valid for the intended target where applicable. Sandbox enforces `op_id in allowed` exact set membership (python `set`); runtime fallback also `UnknownOperation` but the claim requires sandbox-first exact match.

| Case | Manipulated op_id | Class | Expected | Trace | Pass |
|---|---|---|---|---|---|
| D4.1a | `search_artefact` | typo missing `s` | `UnknownOperation`/`sandbox` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.1b | `search_artefactsx` | typo extra char | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.2a | `Search_Artefacts` | casing Pascal | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.2b | `SEARCH_ARTEFACTS` | casing upper | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.2c | `search_Artefacts` | casing mixed | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.3a | `internal__search_artefacts` | prefix injection `internal__` | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.3b | `admin_search_artefacts` | prefix `admin_` | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.4a | `../search_artefacts` | path `../` | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.4b | `search_artefacts/../admin` | path mid | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.4c | `search_artefacts%2Fadmin` | encoded slash | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.5a | `0` | numeric guess | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.5b | `1` | numeric guess | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.5c | `999` | numeric guess | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.6a | `` (empty) | empty string | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.6b | ` search_artefacts` | leading space | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.6c | `search_artefacts ` | trailing space | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.7a | `getArtefact` | alias camelCase | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.7b | `get-artefact` | alias kebab | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.7c | `artefact.get` | alias dotted | `UnknownOperation` | `sandbox:rejected:UnknownOperation` | PASS |
| D4.9 | `search_artefacts` | exact valid control | `executed:ok` | `sandbox:allowed → validation:pass → policy:pass → execution:ok` | PASS |

**No-fuzzy assertion verified:** all 19 manipulated IDs produced `UnknownOperation` at sandbox with `executed == false`; no case was dispatched via substring, case-folding, Levenshtein, or prefix routing. Source audit: `harness/sandbox.py:check` is `if op_id in self.allowed:` (exact `set` membership) with no normalization; `harness/runtime.py:validate` likewise requires exact `op_id in self.capabilities`.

## Cross-cutting audits

### Boundary separation

* Sandbox vs validation vs policy are cleanly separated: D1 traces contain only `sandbox:rejected`; D3 traces contain `sandbox:allowed → validation:rejected` with no `policy:*`; D2 traces contain `sandbox:allowed → validation:pass → policy:rejected`. No case exhibited wrong-boundary rejection (e.g., a policy-denied call rejected as `ValidationFailed` would have been a separation finding — none observed).
* Error codes are distinct by boundary per `error-codes.md` distinguishability requirement.

### Execution gate

* Every expected-rejection case asserted `executed == false` (`41` expected-reject cases all satisfied; `5` control cases asserted `executed == true`). No invalid call reached execution — the harness `Harness.call()` return was checked before any simulated side-effect code in `Runtime.execute()`.

### Valid→execute gate

* Phase 0 smoke gate still `12/12` on `harness/run.py --smoke` after this run (verified pre-commit). Controls D1.5/D2.5a-c/D4.9 serve as additional valid→execute probes within this suite.

## Findings for synthesis (report.md §§7-8)

* **Supported (evidence-based):** the four runtime-authority claims from issue #498 Test D are supported on the harness measurement: absent-from-sandbox cannot be invoked; policy-denied despite schema-valid is rejected with distinct `PolicyDenied`; malformed cannot bypass `ValidationFailed` before policy/execution; manipulated op_id cannot select an arbitrary implementation (exact-match only).
* **Falsified/modified:** none — no case failed, so no claim requires narrowing on this harness.
* **Residual separation note:** the policy check tested is op-deny + resource-deny (`deny` list, `deny_resources`). It does not exercise richer policy surfaces — this is a finding of scope, not a failure (§7).

## WHAT-NOT-TESTED (AGENTS.md — sharpest check)

* **Not tested:** model-in-the-loop invocation (harness injects calls directly — whether a real model would hallucinate or self-correct after `UnknownOperation`/`PolicyDenied` is not measured; that is Tests A/B scope).
* **Not tested:** schema drift / versioning interaction with authority (version pinned `0.1.0`; drift mutations C1-C4 are Test C scope).
* **Not tested:** transport / concurrency / TOCTOU races between validation and execution, or durable-operation lifetime beyond the connection (Test E scope).
* **Not tested:** richer policy models (tenancy/ABAC/RBAC hierarchy, time-window, rate-limit) — only flat `deny` lists are exercised (`protocol.md` §WHAT-NOT-TESTED).
* **Not tested:** cryptographic operation attestation, Lexicon/XRPC-specific authority propagation, or bidirectional Lexicon↔JSON Schema mapping fidelity.
* **Not tested:** fallback validator path formally — the run used `jsonschema` Draft7 when installed; fallback minimal validator (`_fallback_validate`) was not separately re-measured in this run but smoke covers its parity on `required`/`type`/`enum`/`pattern` cases.
* **Not tested:** multi-step chained workflows or catalogue of real EDASES agent tasks beyond the 14-op representative set (cf. `protocol.md` 22-task set — not re-run here).
* **Not tested on remote transport:** all calls are in-process harness; `stdio-only` qualification and remote-execution locality (Test E) are explicitly not claimed here.
* **Version-bound caveat:** results are bound to `research/capability-schema-validation/capabilities/authoritative/schemas.json@0.1.0` and `harness` at this commit; re-validate on schema harness upgrade (advisory §2 trigger #279).

## Files

* Runner: `research/capability-schema-validation/tests/test-d/run.py` (executable, `--case` filter, JSONL emission)
* Logs: `research/capability-schema-validation/logs/test-d/d1.jsonl`, `d2.jsonl`, `d3.jsonl`, `d4.jsonl`, `all.jsonl`, `summary.json`
* This document: `research/capability-schema-validation/tests/test-d/results.md`
* Protocol: `research/capability-schema-validation/tests/test-d/protocol.md`
* Harness: `research/capability-schema-validation/harness/{sandbox.py,runtime.py,run.py,error-codes.md}`

## Verification

```bash
python3 research/capability-schema-validation/harness/run.py --smoke
# → Smoke: 12 passed, 0 failed out of 12 — Smoke gate PASSED

python3 research/capability-schema-validation/tests/test-d/run.py
# → Summary: 41 passed, 0 failed out of 41 — All D1-D4 checks PASSED
```
