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

**P5 — Comparative crash recovery: conventional restart testing versus checkpoint-qualified SIGKILL.**
- [Preregistered hypotheses](P5-PREREGISTERED-PLAN-2026-11-02.md), [observed results and method comparison](P5-RESULTS-2026-11-02.md), and [blind reviewer packet](P5-REVIEWER-PACKET-2026-11-02.md).
- GitLab CI `3015833489`, both Rust and Haskell: ordinary restart/idempotency checks detected deliberate duplicate commits but **missed premature ACK before journal fsync**; five milestone-specific kills per point detected the missing committed transaction in each language. The correct variants passed all tests.
- The conventional approach took a combined 72.184 ms across six tests; qualified approach 540.005 ms (adds 90 real SIGKILL recovery checks). The earlier failed CI run exposed a **mistaken fixture expectation**, not an implementation bug; it is preserved without retroactive rewriting.
- The **two full native CI artifact ZIPs**, failed and successful, are independently preserved and SHA-256 verified: [original archive manifest](evidence/P5-ARCHIVES-MANIFEST-2026-11-02.json). No sudden power loss, storage crash, or production transaction was tested. Independent review remains **NOT_RUN**.

**P6 — Evidence semantics: execution, individual assertions, instrument quality, interpretation, archive and authority.**
- [Preregistered P6 plan](P6-PREREGISTERED-PLAN-2026-11-02.md), [experimental typed event contract](EVIDENCE-EVENT-CONTRACT-EXPERIMENTAL-2026-11-02.md), [P6 results](P6-RESULTS-2026-11-02.md), and [validator / replay harness](evidence_semantics_p6.py).
- [GitLab CI 3016049098](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/pipelines/3016049098): opened and rehashed both original P5 CI archives, accepted **3/3** legitimate evidence records, rejected **16/16** invalid controls. The corrected P5 job remains a valid green suite **despite expected RED assertions in the planted mutants**.
- The [first P6 run 3016045716](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/pipelines/3016045716) failed due to a bad assertion-aggregation assumption; it was not counted as an application defect. Both original P6 CI ZIPs are [independently archived and SHA-256 verified](evidence/P6-ARCHIVE-MANIFEST-2026-11-02.json).
- The schema is research-only: field presence does not authenticate reviewer independence, human authority or semantic truth; no canonical method changed.

**P7 — Source-first P5 evidence reconstruction and ontology role benchmark qualification.**
- [Frozen P7 plan](P7-PREREGISTERED-PLAN-2026-11-02.md), [results and caveats](P7-RESULTS-2026-11-02.md), [review dispatch protocol](P7-REVIEW-EXECUTION-PROTOCOL-2026-11-02.md).
- Original P5 failed and corrected ZIPs reopened, SHA-256/CRC checked, assertion outcomes and five-fold crash-point results recomputed from raw per-check fields. P5 fixture correction source diff exactly one line (`charge=50` to `charge=90`, cap 80); **mechanical source-first reconstruction is NOT model-independent human/agent review**.
- [Six unlabeled cases](../ontology-benchmark-p7/blind-cases.json), key privately sealed before execution, [GitLab P7 CI 3016096124](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/pipelines/3016096124): simple deterministic syntax-control baseline found **2/4** planted conceptual defects with **0/2** false positives; **7/7** malformed input checks detected. This is NOT ordinary reviewer performance.
- Original Conformance packet had result-hint traces. Corrected [Conformance packet v2](../ontology-benchmark-p7/conformance-review-packet-v2.json) and separate [Design packet](../ontology-benchmark-p7/design-review-packet.json) passed [post-hoc GitLab packet qualification 3016118845](https://gitlab.com/rock-solid-sites-group/rock-solid-sites-project/-/pipelines/3016118845): **2/2 valid, 6/6 invalid**.
- [Public redacted P7 machine evidence](../ontology-benchmark-p7/evidence/p7-machine-result-redacted.json) contains no individual benchmark labels; original complete sealed ZIP **6,199 bytes** preserved and SHA-256 verified in private `rock-solid-sites/foundation-ASES@research/ases-p7-sealed-evidence-2026-11-02`. [Original post-hoc packet CI ZIP](../ontology-benchmark-p7/evidence/p7-cleanroom-packet-qualification-original-ci.zip.b64) also independently retained and hash-verified.
- **Real ordinary/model Design/model Conformance review evaluations: NOT_RUN.** Model-family route, independent reviewer reconstruction and role added value remain to be measured; PR #4 stays draft.

[Independent-review packet](INDEPENDENT-REVIEW-PACKET-2026-11-01.md) is ready for an actual separate reviewer; drafting it and source-first checking by the builder are **not** independent verification.

## Method conclusions still pending

The experiments span admission controls, a real monitoring workflow, in-memory concurrency and durable-journal interruption prototypes, and show targeted assurance benefit and measurable low-cost fault-discrimination. They do not show that a universal fixed red/green/mutation process is beneficial. Evaluate comparative review effectiveness and overhead with separate reviewers, and solve external artifact retention and real-world monitoring-cadence gaps before considering promotion. The authorized decision is **DEFER**.
