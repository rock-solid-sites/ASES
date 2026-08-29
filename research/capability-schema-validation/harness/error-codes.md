---
title: Error Code Taxonomy — Capability/Schema Validation Harness
program: EDASES
layer: Research
document_type: Reference
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
consumed_by:
  - research/capability-schema-validation/harness/*
  - research/capability-schema-validation/tests/**
---

# Error Code Taxonomy

Single source of truth for typed errors used by the harness (`sandbox.py` → `runtime.py` → execution). Every test (A-E) references these codes; a generic rejection with the wrong code is a failure of that check.

## Codes

| Code | Boundary | Meaning | Payload fields |
|---|---|---|---|
| `ValidationFailed` | Runtime validation | Arguments fail authoritative JSON Schema (type, required, enum, pattern, min/max, additionalProperties, nested) | `{code, field?, constraint?, got?, schema_version}` |
| `UnknownOperation` | Sandbox + Runtime dispatch | `op_id` not in authoritative registry or not exact stable ID match | `{code, op_id, hint?}` |
| `PolicyDenied` | Policy | Schema-valid call denied by runtime policy (role, tenancy, artefact ownership) | `{code, policy, reason, op_id}` |
| `VersionMismatch` | Runtime version check | Payload version does not match authoritative schema version (drift Tests C) | `{code, expected_version, actual_version, op_id}` |
| `NotFound` | Execution | Referenced resource does not exist (artefact, review) | `{code, resource_type?, resource_id?}` |
| `Conflict` | Execution | State/transition conflict (already archived, duplicate link, illegal transition) | `{code, expected_version?, actual_version?, reason?}` |
| `Timeout` | Transport | Per-request deadline exceeded | `{code, op_id, deadline_ms}` |
| `Cancelled` | Transport | Caller-initiated cancellation | `{code, op_id}` |
| `ConnectionLost` | Transport | Transport dropped mid-request or mid-idle | `{code, transport?, in_flight?}` |

## Distinguishability requirement

* `ValidationFailed` vs `PolicyDenied` vs `UnknownOperation` must be distinguishable by `code` alone (Test D acceptance).
* `VersionMismatch` must be distinguishable from generic `ValidationFailed` where the version check is exercised (Test C acceptance).
* `Timeout`/`Cancelled`/`ConnectionLost` are transport-bound and never returned from schema validation.

## Construction rule

Runtime validation boundary constructs `{code, field?, constraint?, got?, version?}` per the authoritative error schema before any policy or execution is reached. Policy boundary is reached only if `ValidationFailed` did not occur. Execution is reached only if neither validation nor policy rejected.

## WHAT-NOT-TESTED (per AGENTS.md)

* This taxonomy does not cover retry-classification nuances (retryable vs non-retryable) — those are inputs from `research/toolregistry-lazy-mcp/retry-classification/report.md`, not re-derived here.
* Transport error propagation fidelity (whether a `Timeout` at transport maps losslessly to caller-observed `Timeout`) is tested only in Test E, not here.
