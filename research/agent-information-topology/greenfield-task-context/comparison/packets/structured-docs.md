# Task task:docs
Objective: Correct the synthetic documentation note without affecting unrelated sections.
Output: docs/study-guide.md
Durable result: git:synthetic-docs-branch

## Applicable instruction
- rule:docs-verify from source:docs@docs-r4
  DOC_VERIFY: verify the exact edited section and source revision.

## Evidence
- evidence:doc-note | source:doc-observation@obs-r2 | certainty=observed-fixture
- Claim: Documentation note inspected at its synthetic source.
- WHAT-NOT-TESTED: DOC_RUNTIME_NOT_TESTED

## Dispatch
MODEL_LAUNCH=none
FALLBACK=none
