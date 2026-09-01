---
title: 5pp Tolerance — Real-Model Minimal vs Full (530)
program: EDASES
layer: Research
document_type: Specification
status: Active
authority: Derived
canonical_repository: edases
issue: 530
depends_on:
  - research/capability-schema-validation/corpus-530/tasks.json
  - research/capability-schema-validation/corpus-530/schemas/authoritative.json
  - research/capability-schema-validation/tests/test-a/protocol.md
---

# 5pp Tolerance (530)

## Pre-registered acceptance

Minimal is **acceptable** if on the 24 well-formed tasks (6×4), ≥3 repetitions, temperature>0 or prompt-order permutation:

```
| selection_success_minimal − selection_success_full | ≤ 0.05
| argument_success_minimal  − argument_success_full  | ≤ 0.05
```

Same tolerance reported for `task_success`. Raw counts (not only percentages) and token/accuracy curve (X = description_tokens minimal/full, Y = selection/argument success) are primary deliverables; a ratio without named tokenizer version (`tiktoken cl100k_base 0.14.0`) not reportable.

Prior proxy: B vs A `|sel|=0.000, |arg|=0.000`; C vs A `|sel|=0.000, |arg|=0.016` within tolerance (17ed2631, 6da54219 live replication).

## Recovery gate

≥60% of typed rejections correctly recovered within 1 retry (design §5.3) — recorded before run, not inferred post hoc. Expose check: was `field+constraint+got+message` sufficient without full schema excerpt?

## Scope

Valid tasks only; malformed 12 and adversarial 4 reported separately (validation failures, retries, latency p50/p95; recovery tokens/one-retry/multi-retry). Hidden constraints (numeric range, pattern/format, mutually constrained, additionalProperties/maxLength) enforced at runtime; minimal omits them — violation surfaces as `ValidationFailed`/`OutputValidationFailed` with distinct codes.

