Task task:docs: Correct the synthetic documentation note without affecting unrelated sections.

Use rule:docs-verify (source:docs@docs-r4): DOC_VERIFY: verify the exact edited section and source revision.
Evidence evidence:doc-note (source:doc-observation@obs-r2), certainty observed-fixture: Documentation note inspected at its synthetic source.
WHAT-NOT-TESTED: DOC_RUNTIME_NOT_TESTED.

Deliver docs/study-guide.md at git:synthetic-docs-branch.
MODEL_LAUNCH=none. FALLBACK=none.
