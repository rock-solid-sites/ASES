# Task task:review
Objective: Prepare a bounded synthetic review handoff using the approved local review rule.
Output: reports/review-readiness.md
Durable result: worknotes:synthetic-WNASES-22

## Effective rules
- rule:checkpoint | source:shared@shared-r7
  REMOTE_CHECKPOINT: record a durable position before handoff.
- rule:review-route | source:shared@shared-r7 | overridden by decision:local-review
  LOCAL_REVIEW_ROUTE: route this review through the project-approved workflow.
  Replacement authority: source:project@local-r3 | authorized_by=synthetic-operator
  The original upstream rule body is excluded.

## Evidence and uncertainty
- evidence:review-note | source:review-observation@review-obs-r1 | certainty=uncertain-fixture
- Claim: Reviewer transport and model-visible context are not verified.
- WHAT-NOT-TESTED: REVIEW_RUNTIME_NOT_TESTED

## Dispatch
MODEL_LAUNCH=none
FALLBACK=none
