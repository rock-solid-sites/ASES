---
title: Harness — Capability/Schema Validation
program: EDASES
layer: Research
document_type: Guide
status: Draft
authority: Derived
canonical_repository: edases
depends_on:
  - .design/capability-schema-validation.md
  - research/capability-schema-validation/capabilities/authoritative/schemas.json
  - research/capability-schema-validation/harness/error-codes.md
consumed_by:
  - research/capability-schema-validation/tests/**
---

# Harness

Standalone runnable harness implementing the architecture from `.design/capability-schema-validation.md` §7:

```
model (sees variant C only)
  │
  ▼
sandbox (preselected surface gate — checks op_id ∈ allowed set)
  │
  ▼
runtime validation boundary (authoritative schema — JSON Schema)
  │  ├─ schema validation (types, required, enums, patterns, constraints)
  │  ├─ version check (payload version ≡ authoritative version for drift tests)
  │  └─ typed error construction {code, field?, constraint?, got?, version?}
  ▼
policy boundary (deny-list / role check — only reached if schema validation passed)
  │
  ▼
execution (only reached if both boundaries passed)
```

## Files

* `sandbox.py` — `Sandbox` class; checks `op_id ∈ allowed set`; exact match only, no fuzzy matching.
* `runtime.py` — `Runtime` + `Harness` classes; authoritative JSON Schema validation (via `jsonschema` Draft7 if installed, else minimal fallback), version check, typed error codes, policy check, simulated execution.
* `error-codes.md` — single taxonomy: `ValidationFailed`, `UnknownOperation`, `PolicyDenied`, `VersionMismatch`, `NotFound`, `Conflict`, `Timeout`, `Cancelled`, `ConnectionLost`.
* `run.py` — CLI entry point.

## Quick start

```bash
# from repo root, after checkout of feature branch feature/pp3g-1eHz-phase-0-setup-for-498-capability-set-10-20-ops-be69

# smoke gate: valid→execute, malformed→rejected before execution
python research/capability-schema-validation/harness/run.py --smoke

# token/char measurement for variants A/B/C (reports tokenizer version)
python research/capability-schema-validation/harness/run.py --measure-tokens
# or
python -m research.capability-schema-validation.harness.run --measure-tokens

# single ad-hoc call
python research/capability-schema-validation/harness/run.py --op search_artefacts --args '{"query":"hello","limit":5}'
python research/capability-schema-validation/harness/run.py --op get_artefact --args '{"id":"art_abc-123"}'
python research/capability-schema-validation/harness/run.py --op search_artefacts --args '{"query":"hi"}' --policy '{"deny":["search_artefacts"]}'

# drift test: version mismatch
python research/capability-schema-validation/harness/run.py --op get_artefact --args '{"id":"art_abc"}' --payload-version 0.2.0
```

## Logging

Every call returns `{op_id, arguments, validation_result, error, executed, result, latency_ms, version, trace}` where `trace` records `sandbox → validation → policy → execution` ordering for boundary-separation audit (Test D).

* `executed == false` for every expected-rejection case (sandbox or validation or policy rejection).
* `executed == true` only if all three boundaries passed.
* `error.code` distinguishes the failing boundary; a generic rejection with the wrong code is a failure of the test.

## Dependencies

* Python 3.10+ (harness uses stdlib only for core path).
* `jsonschema` (optional but recommended for full Draft-07 validation): `pip install jsonschema`.
  Without it, a minimal fallback validates required/types/enums/patterns/min/max — sufficient for smoke but not for full output-schema validation.
* `tiktoken` (optional, for token measurement): `pip install tiktoken`. Without it, `char/4` heuristic is reported and flagged as heuristic.

## What the harness must NOT do (§7.3)

* Must not silently reshape, coerce, or retry calls before runtime validation sees them.
* Must not expose authoritative schema text to the model path (the exposure check in Test B would then be tautologically failed).

## Reproduction

See `research/capability-schema-validation/README.md` for the full reproduction entry point covering harness + per-test harnesses.
