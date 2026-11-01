# EDASES Testing and Assurance Method — Experiments (2026-11-01)

**Proposal authority:** DRAFT/Experimental, not adopted global policy. This folder is an empirical pilot package, not an additional universal project gate.

## Experiments and outcomes

**P1 — Synthetic resource-admission test-instrument qualification.**
- [Frozen plan](P1-PREREGISTERED-PLAN-2026-11-01.md).
- [Observed result](P1-RESULTS-2026-11-01.md).
- [Source-first cross-check](P1-SOURCE-FIRST-AUDIT-2026-11-01.md).
- CI: GitLab `3015307498`: four targeted mutations detected with positive/negative neighbors. **Partial** external archive only; 31 indexed files were not all independently copied. Independent reviewer **NOT_RUN**.

**P2 — Trip'n production-invariant monitor as unrelated substrate.**
- [Frozen prospective plan plus retrospective history disclosure](P2-PREREGISTERED-PLAN-2026-11-01.md).
- [Observed result and monitoring questions](P2-RESULTS-2026-11-01.md).
- CI: GitHub Actions `41348887554`, branch `TripN-Chill-Zone/tripn-astro@research/ases-assurance-p2-2026-11-01`. A mutation of the forbidden-content check **survived all six legacy self-tests**, while one newly qualified neighboring pair caught it. The monitor's 194 observed scheduled executions had a median 4.84-hour gap despite a configured 30-minute schedule.
- Native GitHub artifact: `13100187337`, SHA-256 `76193997d0481b4a84da0d8b80053980b0c46abb5164ab0e63deb7e5601af03c`; independently copied to persistent ASES Library `/ASES/Evidence/Tripn-P2-2026-11-01/tripn-p2-run-41348887554.zip`, same SHA-256 verified. Historical 196-run metadata and 9 job logs are separately in the **private** GitLab account (evidence commit `1b82716d94f1cf7548231d63b7e1a278e91a951f`). Not all historical raw job logs were archived.

**P3 — Cross-suite mutation sensitivity (same admission substrate as P1).**
- [Frozen plan](P3-PREREGISTERED-PLAN-2026-11-01.md).
- [Observed results and limits](P3-RESULTS-2026-11-01.md).
- [Structured raw evidence copied from GitLab CI](evidence/gitlab-3015407990-p3.json).
- GitLab CI `3015407990`: six compiled capacity/wallet/spend-cap mutants; **0/6** caught by P1's five controls, **6/6** by the inherited 1,025-case suite, **6/6** by the new six independent boundary inputs with valid neighbors retained. The full provider artifact archive has **not** been independently copied. This is a test-selection comparison, not a general mutation score.

[Independent-review packet](INDEPENDENT-REVIEW-PACKET-2026-11-01.md) is ready for an actual separate reviewer; drafting it and source-first checking by the builder are **not** independent verification.

## Method conclusions still pending

The two distinct substrates (with a third pilot within the admission substrate) show targeted assurance benefit and measurable low-cost fault-discrimination. They do not show that a universal fixed red/green/mutation process is beneficial. Evaluate comparative review effectiveness and overhead with separate reviewers, and solve external artifact retention and real-world monitoring-cadence gaps before considering promotion. The authorized decision is **DEFER**.
