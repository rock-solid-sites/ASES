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

**P4 — Environmental perturbation on concurrent in-memory reservations (new stateful substrate).**
- [Experimental technique and interpretation rules](ENVIRONMENTAL-PERTURBATION-EXPERIMENTAL.md); [frozen P4 plan](P4-PREREGISTERED-PLAN-2026-11-02.md); [P4 observed results](P4-RESULTS-2026-11-02.md).
- GitLab CI `3015717109`: 120 trials covering four competing-request scenarios, two languages, normal runs, measured critical-section delays, and deliberately stale snapshots. Safe Rust/Haskell implementations preserved all tested invariants; known stale-snapshot faults were detected in capacity/spend/idempotency controls.
- A 1.2-second **single-core** CPU contender was measured as effective; five before/after samples per language showed slowed execution but no failed tested invariants. Process crash recovery and disk/network fault injection are **NOT_TESTED**.
- **Complete original P4 CI artifact ZIP is preserved outside GitLab**, [Base64 archive](evidence/p4-gitlab-3015717109-original-artifacts.zip.b64) + [SHA-256 provenance](evidence/p4-gitlab-3015717109-archive-manifest.json), with source ZIP hash independently recomputed after GitHub archival. This does not retroactively complete P1/P3 archives.

[Independent-review packet](INDEPENDENT-REVIEW-PACKET-2026-11-01.md) is ready for an actual separate reviewer; drafting it and source-first checking by the builder are **not** independent verification.

## Method conclusions still pending

The two distinct substrates (with a third pilot within the admission substrate) show targeted assurance benefit and measurable low-cost fault-discrimination. They do not show that a universal fixed red/green/mutation process is beneficial. Evaluate comparative review effectiveness and overhead with separate reviewers, and solve external artifact retention and real-world monitoring-cadence gaps before considering promotion. The authorized decision is **DEFER**.
