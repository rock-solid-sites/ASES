---
title: Empirical Assurance Selection — Experimental Candidate
program: ASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
related_documents:
  - testing/experiments/2026-11-cross-project-pilot.md
  - testing/lessons/2026-11-cross-project-lessons.md
last_updated: 2026-11-19
---

# Choose an assurance technique by the claim it can falsify

**Status:** candidate distilled from the November 2026 pilots, **not** an accepted ASES-wide method. The active [realization/assurance selection method](../../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md) governs. The [draft ASES Testing and Assurance Method](https://github.com/rock-solid-sites/ASES/pull/4) must be reconciled rather than duplicated when this candidate is reviewed.

## Technique selection (heuristic, not mandatory gates)

| Claim or risk | First discriminating experiment | Add more only if the evidence gap remains |
| --- | --- | --- |
| A value, conversion, validation or pure invariant is wrong | Deterministic case near a consequential boundary, independent expected value, good/bad controls | Generated properties for combinations and overlooked branches; monitor semantic outcomes and oracle fidelity |
| Correctness depends on ordered transitions | Small independent state model and one known-bad history | Generated operation histories, shrinking, replay and transition/category checks |
| Commit/rollback or crash recovery must preserve durable invariants | Real file-backed storage, reopen and precisely placed injected failure | Separate processes and SIGKILL at specified pre/post-COMMIT windows; **do not** infer power-loss or other backend guarantees |
| Duplicate or conflicting writers contend for authority | Two truly separate processes against the same durable state, assert exact effects and response statuses | Repeated bounded schedules/linearization analysis; input seed alone does not fix concurrent scheduling |
| User input crosses a provider, checkout or deployed browser boundary | Compare actual public/read-only source contract with input-to-output mapping; exercise true browser/prebooking boundary | Broader cases or controlled write tests **only with operator authority**; DOM unit tests cannot establish provider acceptance |
| Review may reveal a semantic gap not cheaply executable | Source-pinned, bounded independent review with explicit hypotheses | Reproduce each finding with a discriminating test; track factual false positives, failures, truncation, invocation count and unknown cost |

**Stop without inventing evidence:** if claim provenance, environment, permission, expected behavior, oracle independence or decisive observation is absent, report `UNTESTABLE`, `INCONCLUSIVE`, or `BLOCKED`. An unobservable claim is not a failed product. A passing green runner is not universal proof.

## Minimum review of the instrument

- Pin **which object was tested**: existing source, candidate implementation, test-only mutant, source-level shell, simulated provider, or actual provider interaction.
- Pair a compliant control with a controlled violation when valid and possible. A known-bad mutant failing is **test sensitivity**, not proof that the production object has the bug.
- Verify the independent oracle's own edge cases; signed zero, division basis and scope of identifiers are examples where the test can be wrong.
- For generated tests, record semantic classes exercised; fail or qualify a run that happens not to reach required cases. Counts are not completeness.
- Distinguish *durable effects*, *caller acknowledgment*, *provider settlement* and *authorized access*. A positive result at one layer does not inherit to another.
- Keep a reproducible minimal input, seed/shrink path where available, exact source/lock and CI evidence. Retain full logs only if a compact replay/pointer is insufficient for independent verification.
- For model reviews, distinguish **invoked**, **complete output retained**, **source-correct**, and **independently reproduced**. Approved retries are extra invocations; a timeout is not a completed report.

## Candidate delivery rule

An experiment is worth retaining only if it yields a checkable observation and one of: a more discriminating test, a narrower claim, a rejected oracle assumption, an improved failure boundary, a reduced resource cost, or a sound decision to avoid extra assurance machinery.

The method itself remains under review in Work Notes `WNASES-10`. Do not promote this text by linking to it from active skills as an instruction.
