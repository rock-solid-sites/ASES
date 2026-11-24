---
title: Testing and Assurance Source Map
version: 2026-11-24.1
program: ASES
layer: Research
document_type: Guide
status: Active
authority: Derived
canonical_repository: ases
last_updated: 2026-11-24
---

# Testing and assurance: current authority, experimental methods and evidence

This is a navigation and disposition record, not a second testing method, skill, adoption decision or independent review. The original objective is to improve testing as an empirical engineering practice. Preserve findings that change a future test; avoid chronology for its own sake, duplicative suites, and gratuitous gates. Current evidence and pending promotion work have distinct owners.

## Current governing sources

| Question | Current source | Scope |
| --- | --- | --- |
| What is being built and verified? | [Bounded Project Build Method](../methodology/ASES%20Bounded%20Project%20Build%20Method.md) | Bounded requirements, implementation packet and appropriate verification, not a new testing lifecycle |
| Which guarantees and assurance mechanisms are appropriate? | [Realization and Assurance Selection Method](../methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md), [State-Model Applicability and Reuse Method](../methodology/State-Model%20Applicability%20and%20Reuse%20Method.md) | Falsifiable constraints first; model adequacy and realization conformance distinct; state modeling conditional; VSDD only where adopted |
| How do we reason, review and retain evidence? | [AI Orchestration Guide](../methodology/AI%20Orchestration%20Guide.md), [Clean Room Execution Guide](../methodology/Clean%20Room%20Execution%20Guide.md), [task-scoped method](../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md), [current skills](../../skills/current/README.md) | Cheapest meaningful falsifier, independent provenance, exploratory/conformance distinction, no anchoring, actual authorization, durable checkpoints |
| How is research evaluated? | [EDASES Review Methodology](EDASES%20Review%20Methodology.md), [Evaluation Framework](frameworks/Evaluation%20Framework.md), [AI Evaluation Protocol](protocols/AI%20Evaluation%20Protocol.md) | Retained upstream-owned research sources, upstream currency unverified; distinct from ASES dispatch procedures |

The [Repository Review Checklist](Repository%20Review%20Checklist.md) retains useful review questions about abstraction, consistency, traceability and evidence. The former fixed startup-file list is not a current requirement. Reviewers should not receive an anchoring list of expected defects when independent discovery is the question.

## Pending methods, overlap and disposition

| Source | Useful distinct purpose | Status and disposition |
| --- | --- | --- |
| [Testing and Assurance Method](https://github.com/rock-solid-sites/ASES/blob/d5e543036ccb1a220a5ffecbce256d2b27e11893/docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md) | Select and qualify evidence for a claim; test instrument sensitivity; preserve execution, interpretation and decision separately | Draft PR [#4](https://github.com/rock-solid-sites/ASES/pull/4), pinned November proposal. Not an adopted global method. Integrate accepted improvements once independently reviewed; no competing skill. |
| [Debugging and Fault Isolation Method](https://github.com/rock-solid-sites/ASES/blob/d5e543036ccb1a220a5ffecbce256d2b27e11893/docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md) | Start from a deviation, separate causal hypotheses, choose cheapest discriminator, verify the original acceptance surface | Same draft bundle; practical use in diagnostics is evidence, not adoption. No new mandatory phase. |
| [Broad adversarial review proposal](https://github.com/rock-solid-sites/ASES/blob/d5e543036ccb1a220a5ffecbce256d2b27e11893/docs/proposals/2026-11-02-testing-debugging-ontology/broad-adversarial-review-principles.md) | Deep independent discovery of unforeseen failure classes versus targeted claim falsification; depth proportional to consequences | Current guide already governs independence, reasoning and review modes. The proposed broad default, its incremental value and detailed procedure remain to be evaluated under ASES-7; do not reintroduce two permanent ontology roles. |
| [Guarantee-driven testing research](Guarantee-Driven%20Testing%20and%20Goal-Substitution%20Resistance.md) | Object-first attributable claim → evidential question → technique; resist optimizing for defect/test counts | Experimental EDASES framework, not a universal gate design or mandatory test stack. |
| [Provisional red–green note](../PROVISIONAL-RED-GREEN-VERIFICATION-NOTE-2026-11-01.md) and [Resource Solver record](Resource%20Solver%20Red%20Green%20Mutation%20Verification%202026-11-01.md) | Focused behavioral RED before minimal repair; GREEN and scoped mutation controls | Project-provisional scope. Thirteen targeted retrospective mutation kills are not original red-before-green evidence, a comprehensive score, or proof of production readiness. Universal mutation obligations remain undecided. |
| [Empirical testing laboratory](https://github.com/rock-solid-sites/ASES/blob/5a1ba2cff4439bdaafa0ed2c29ff6a4caef04a02/testing/README.md), [selection candidate](https://github.com/rock-solid-sites/ASES/blob/5a1ba2cff4439bdaafa0ed2c29ff6a4caef04a02/testing/methods/selection-candidate.md), [cross-project pilot](https://github.com/rock-solid-sites/ASES/blob/2affc493a0296dcf80efc598a99e64631c333569/docs/research/Generated%20Property%20and%20Stateful%20Testing%20Cross-Project%20Pilot%202026-11-19.md) | Compare techniques, collect minimal counterexamples and transferable lessons, test actual incremental value | Draft PRs [#58](https://github.com/rock-solid-sites/ASES/pull/58), [#59](https://github.com/rock-solid-sites/ASES/pull/59), [#60](https://github.com/rock-solid-sites/ASES/pull/60); distinct source trees. WNASES-14 lab setup in review; WNASES-10 independent method review/promotion still pending. Do not merge or install the proposals on this map's authority. |

The [proposal bundle index](https://github.com/rock-solid-sites/ASES/blob/d5e543036ccb1a220a5ffecbce256d2b27e11893/docs/proposals/2026-11-02-testing-debugging-ontology/README.md) and [initial cross-conversation reconciliation](https://github.com/rock-solid-sites/ASES/blob/d5e543036ccb1a220a5ffecbce256d2b27e11893/docs/proposals/2026-11-02-testing-debugging-ontology/cross-conversation-reconciliation-2026-11-02.md) preserve earlier options, project responses and pilot interpretation. The proposed two named ontology roles and old integration patch are historical comparison material; the current design uses a conceptual review lens and distinct reasoning modes. Neither old role names nor earlier source-path assumptions should drive new integrations.

## Bounded empirical evidence already available

The [lab lessons](https://github.com/rock-solid-sites/ASES/blob/5a1ba2cff4439bdaafa0ed2c29ff6a4caef04a02/testing/lessons/2026-11-cross-project-lessons.md) retain nine transferable observations, not nine mandatory new rules. The [counterexample index](https://github.com/rock-solid-sites/ASES/blob/5a1ba2cff4439bdaafa0ed2c29ff6a4caef04a02/testing/counterexamples/README.md) leads to owner-repository evidence. Representative distinctions for a future promotion review:

| Observation | What it can inform | What it cannot establish |
| --- | --- | --- |
| Synthetic Kernel-0 witness: Hegel/proptest detected three deliberate mutants; real Rust Store follow-up: 120 generated histories per engine, bounded invariants and reopen checks | Qualify generators and oracles separately; exercise real implementation, preserve source and minimized replay | Kernel realization, universal engine winner, distributed concurrency or production safety |
| HMS generated reservation tests: 1,200 sampled cases without discrepancy and a detected negative control; finance signed-zero oracle rejected | Count relevant semantic classes and qualify the oracle; no discrepancy and rejected oracle are valid results | Live Beds24 or production finance assurance |
| HMS SQLite finance candidate: FX provenance loss and post-COMMIT false failure reproduced; [red](https://github.com/rock-solid-sites/HMS/actions/runs/44459787811) 11 pass/2 expected fail, [green](https://github.com/rock-solid-sites/HMS/actions/runs/44460235430) 18/18 | Distinguish committed effect, response, reopening and evidence identity; test exact failure windows | HMS deployed D1 or payment settlement; power loss; all interleavings |
| Trip'n read-only actual quote and bounded source guards, [CI](https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/44465080572) 16/16 protected tests | Establish external contract before encoding oracle; track search to selected to submitted guests | Browser/deployed/hosted checkout parity or every provider offer |
| Paseo [red](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570572887) 17/18 then [green](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44570781671) 18/18, fake CLI boundary | Independently compare all relevant observed identity/authority dimensions; isolate mismatch | Live CLI/provider behavior; missing runtime Thinking-field policy |
| HMS reviewer reports, failed first invocation and authorized retry; Paseo only one substantive report out of three invocations | Distinguish launch, transport, complete retained output, source-supported finding and independent reproduction | Reviewer consensus, method superiority or provider cost |
| [November stream diagnostic history](../historical/Capability%20Observation%20and%20Failure%20Attribution%20History.md) and [MCP case](Projektor%20MCP%20Registration%20Failure%20Case%202026-11-06.md) | Measure the actual fault boundary, distinguish monitor/setup defects from target failure; paired controls and original acceptance | A common root cause, general benchmark, or global debugging-method adoption |

These are source-reported scoped results, not fresh independent replays in this reconciliation. Generated tests, real code, deliberately synthetic fixtures, prototype implementations, read-only external observations and deployed behavior are different evidence categories. Preserve failed tests and negative findings at authorized durable destinations; distinguish CI status from archival success. The candidate language and detailed status schemas in research do not establish a universal evidence schema or mandatory retention cadence.

## Remaining promotion and research ownership

- **WNASES-10:** independent review of the *procedure*, not another chronological audit. Source-pin one controlled negative and one red→green repair, audit oracle and reviewer false positives, compare marginal value/cost to simpler tests, test transfer, recommend a bounded integration or rejection. Do not create a new competing skill.
- **WNASES-14:** testing laboratory setup and disposition, PR #60. Proposed permanent top-level testing/ home is still on the draft; its exact pinned content is discoverable here pending separately approved review/merge. A source pointer is not a claim of final publication.
- **ASES-7:** review breadth and evidence-first testing adoption, including actual canonical/skill consistency and evidence of improvement; not closed by these source-map edits.
- **WNASES-15:** Paseo transfer and remaining assurance boundaries; **WNASES-21 / ASES-21:** ongoing model-stream debugging; **WNASES-16 / ASES-19:** knowledge-index retrieval experiment, distinct from method promotion.
- Source evidence stays in the owning repositories. GitHub retains substantive research and decision rationale, Work Notes retains operational position, Projektor retains conceptual planning/decisions. No further execution or deployment is authorized by this map.

At the next promotion decision, recheck the actual heads and latest evidence. The pins here preserve the reviewed state, not a guarantee that it is the latest experimental result.
