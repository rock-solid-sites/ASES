---
title: Harness Reuse — Sandbox→Validation→Policy→Execution (530)
program: EDASES
layer: Research
document_type: Guide
status: Active
authority: Derived
canonical_repository: edases
issue: 530
---

# Harness Reuse (530)

`corpus-530` reuses `research/capability-schema-validation/harness/` verbatim — no new state-machine, policy, lifecycle, discovery, pooling, or idle-timeout added.

```
model (sees minimal OR full per prompt) → sandbox (exact stable ID ∈ allowed, no fuzzy) → runtime validation (authoritative.json Draft-07, 0.1.0, jsonschema 4.26.0) → version check → typed error {code, field, constraint, got, schema_version} → policy (only if validation:pass) → execution (only if both pass) → output validation (for D4)
```

Relevant files:
- `harness/sandbox.py` — `Sandbox.check(op_id)` exact match only (Test D4).
- `harness/runtime.py` — `Runtime.validate()`, `validate_output()`, `Harness.call()` with trace ordering.
- `harness/error-codes.md` — 9 codes; D1-D4 distinguishable by code.
- `harness/run.py` — `--smoke`, `--measure-tokens`, `--op/--args` ad-hoc.

Corpus-specific wiring:
- Authoritative schemas for live A/B: `corpus-530/schemas/authoritative.json` (17 ops).
- Minimal for model: `corpus-530/schemas/minimal.json` (stable ID + ≤20w summary + names/types + required/optional + enum literals; hidden constraints omitted).
- Validation: `python harness/run.py --smoke` with corpus-530 schemas path, or `corpus-530/harness-bridge/run.py` shim.

No new harness state added; live runner logs under `corpus-530/measurements/logs/`.

