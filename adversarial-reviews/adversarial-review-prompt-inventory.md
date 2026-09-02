---
title: Adversarial Review Prompt Inventory
program: ASES
layer: Methodology
document_type: Research Protocol
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - AGENTS.md
  - docs/standards/Documentation Standard.md
consumed_by:
  - Adversarial review operators
related_documents:
  - adversarial-reviews/README.md
last_updated: 2026-09-02
---

# Adversarial Review Prompt Inventory

Reusable prompt templates for independent, evidence-first reviews. The fixed
comparison core below must be copied verbatim into every comparable reviewer
dispatch. Identical wording makes model-quality comparisons meaningful; the
model identity, exact model ID, provider, run/session ID, timestamps, and
delivery outcome must be recorded separately as run metadata.

## Fixed comparison core — use verbatim

```text
READ-ONLY ADVERSARIAL REVIEW. Do not edit, commit, or push. Review the stated
project and commit against the stated objective and scope. Distrust every
claim, summary, change log, test name, and prior verdict; rederive each claim
from the repository and evidence. Build a claim-evidence matrix. For every
important claim, design and execute the cheapest discriminating test that could
falsify it, and actively try to break the code or reasoning. Distinguish a
reproduced blocker from a plausible limitation and from a live-only unknown.
Cite precise file:line evidence. Verify repository cleanliness. Do not infer
live success from mocks. Report PASS, CONDITIONAL, or FAIL, list blockers and
minimum remediation, and state what was not tested.
```

## Dispatch fields

Fill these fields before appending the fixed core:

```text
PROJECT: <repository/path and project identity>
COMMIT: <exact commit hash under review>
OBJECTIVE: <one-sentence acceptance objective>
SCOPE: <files, interfaces, and exclusions>
COMPARISON_SET: <other model/run IDs, if this is a comparison wave>
```

## Required report shape

1. **Run metadata:** reviewer name, exact provider/model ID, run/session ID,
   start/end UTC, delivery status, tool/runtime versions, and whether the run
   was independent or a recheck.
2. **Verdict:** exactly one of PASS, CONDITIONAL, or FAIL, with a one-sentence
   basis.
3. **Claim-evidence matrix:** claim; source file:line; supporting evidence;
   falsifying test; observed result; certainty; status.
4. **Cheapest falsifiers executed:** command or fixture, expected failure
   signal, actual result, and residual uncertainty.
5. **Findings:** separate reproduced blockers, plausible limitations, and
   live-only unknowns. Do not upgrade a limitation or unknown to a blocker
   without reproduction.
6. **Cleanliness and mutation check:** repository status before/after and
   confirmation that no files, commits, or remotes were changed.
7. **Remediation and non-tested surface:** minimum fix for each blocker and an
   explicit list of what the review could not test.

## Optional specialist modules

Append only modules relevant to the task; keep the fixed core unchanged.

### Data completeness / export

Trace expected, discovered, attempted, succeeded, failed, and written counts.
Attack pagination termination, duplicate IDs, omitted/id-less entries, partial
failures, raw-field preservation, checksum/manifest claims, and empty-result
false-complete paths. Prove that the artifact and report agree.

### Authentication / security

Test missing, expired, malformed, and unauthorized credentials; token scope and
redaction; origin/permission boundaries; retries after auth failure; and
whether sensitive data is persisted or sent to an unintended endpoint.

### Pagination / state machines

Enumerate initial, progress, terminal, repeated/cyclic, opaque, malformed, and
rate-limited states. Test every supported cursor shape and verify that a
missing or contradictory continuation signal fails closed.

### Browser / runtime

Check browser API availability, same-origin behavior, memory growth, cancellation
and refresh behavior, download permissions, object URL cleanup, and operator
visible progress/errors. Distinguish mocked runtime behavior from a real browser.

### Documentation / operator usability

Follow the instructions as a fresh operator. Check that prerequisites,
scope/count expectations, success criteria, failure recovery, privacy warnings,
and artifact locations are explicit and consistent with the implementation.

## Comparison discipline

Use the fixed core verbatim across reviewers and vary only the specialist lens
or task fields. Record model identity and run metadata even when a dispatch
fails before producing a verdict. A provider/client error is a non-delivery
outcome, not evidence about model reasoning. Contradictory runtime evidence and
written verdicts must both be preserved and explicitly reconciled; do not
silently select the more convenient account.

