Task task:review: Prepare a bounded synthetic review handoff using the approved local review rule.

Apply rule:checkpoint from source:shared@shared-r7: REMOTE_CHECKPOINT: record a durable position before handoff.
For rule:review-route from source:shared@shared-r7, apply approved decision:local-review from source:project@local-r3, authorized by synthetic-operator, as a complete replacement: LOCAL_REVIEW_ROUTE: route this review through the project-approved workflow. Exclude the replaced upstream instruction from this task view.
Evidence evidence:review-note from source:review-observation@review-obs-r1 is uncertain-fixture: Reviewer transport and model-visible context are not verified.
WHAT-NOT-TESTED: REVIEW_RUNTIME_NOT_TESTED.

Deliver reports/review-readiness.md to worknotes:synthetic-WNASES-22.
MODEL_LAUNCH=none. FALLBACK=none.
