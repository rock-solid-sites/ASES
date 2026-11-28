# Kernel-0 research

**Current requirements input:** [Kernel-0 Evidence Packet](Kernel-0-Evidence-Packet.md). This is the deliberately neutral requirements/adequacy packet, not a complete Kernel ontology, primitive vocabulary or implementation. Its contents remain unchanged during the November documentation reconciliation.

For current architectural intent and non-goals, see the [Execution Engine Vision](../../architecture/Execution%20Engine%20Vision.md). For implementation history, November experimental PRs, remaining Work Unit adequacy tests and original rejected designs, see the [Engine Architecture and Experiment History](../../historical/Engine%20Architecture%20and%20Experiment%20History.md).

The [September reasoning-session decision record](Kernel-0-Reasoning-Session-Decision-Record.md) explains the historical open-derivation protocol; it is not a current launch assignment. Preserve clean-room separation for new open derivations: do not include candidate designs, reviewer conclusions or historical implementation paths unless necessary to the requested task. Actual dispatch requires the current task-relevant skills and authorization, not September model/host assumptions.

## Experimental findings

The owner experiments give executable witnesses for local handover, content continuity and reply-level isolation. The distributed protocols give conditional proofs about gates, voters and holders. The containment studies identify family-wide counterexamples to inferring authority from structurally valid trees. None selects an engine implementation. The relevant result depends on what the consumer can observe and which restrictions must survive loss.

### One handover and its recovery

- [Tenure reuse and delayed admission](Tenure-reuse-and-delayed-admission.md) gives a conditional lower bound on safe identifier reuse, a bounded schedule experiment, and the resulting Work Unit owner verification obligation.
- [One handover across resource owners](One-handover-across-resource-owners.md) derives a two-resource witness for a failed Work Unit handover and checks a conditional construction for repeated replacements over a fixed set of resources.
- [Checking a history across repeated handovers](Repeated-handover-histories.md) gives a complete decision procedure for an ordered succession with known local orders, and a lower bound on the number of observations needed to explain some failures.
- [When can split authorities publish a handover separately?](When-split-authorities-can-publish-separately.md) derives exactly which observation surfaces must switch together under a one-replacement contract.
- [When must Work Unit handover order be fixed?](When-handover-order-must-be-fixed.md) separates ordinary history checking from a witnessed, prefix-preserving cut and gives a late-decision counterexample.
- [Which gates must fence a handover?](Which-gates-must-fence.md) gives a certificate for barriers on partially completed writes, a selection complexity bound, and controls for cached approvals.
- [Changing the set of resource owners at handover](Changing-the-set-of-resource-owners.md) extends the arbitrary-member proof to joins and removals, including delayed activation at an owner that never opened.
- [Aborting a handover without reviving obsolete votes](Abortable-handover-and-catch-up.md) proves abort and direct catch-up first for fixed membership, then for a changing voter set, including a counterexample to simply conjoining the two prior invariants.
- [Which resource owners must a recovered selector fence?](Fencing-after-membership-rollback.md) proves an observation limit under rollback and gives an admission-closure alternative to exact membership recovery.
- [When is an earlier gate snapshot safe to resume?](Recovering-a-gate-with-votes-in-flight.md) derives an exact recovery threshold for one genuine gate rollback with old summaries and escaped votes still deliverable.

### Accepted contents, retries and observations

- [Native owner selection rollback](Native-owner-selection-rollback-result.md) exercises three genuine F3 selection cuts and demonstrates F4 historical success with unresolved owner settlement.
- [What does the native owner actually acknowledge?](Native-acceptance-and-recovery-boundaries.md) maps the protected-witness question onto the pinned native source and identifies where exact retry, F3 currentness and W5/W6 diverge.

- [A local owner witness for activation, replacement and replay](Local-owner-admission-and-replay.md) exercises W5/W6-shaped local histories at process-loss cuts on either side of the actual append commit.
- [What a receipt reveals across Work Unit scopes](What-a-receipt-reveals.md) tests reply-level isolation in the local owner and checks scope-relative receipts across the same crash windows.
- [What must survive replacement to answer an old retry?](Receipt-retention-after-replacement.md) counts distinguishable histories with identical application bytes and verifies conditional reclamation under a prefix-release contract.
- [What must remain recoverable when an old admission path is closed?](Custody-at-an-admission-closed-cut.md) derives final-extent binding and an availability criterion that keeps fences and custody proofs independent.
- [What evidence shows that accepted contents survive handover?](Surviving-content-at-handover.md) separates version and storage custody from a checkable recovery certificate, and derives exact domain-loss bounds for linear contents.
- [Transferring the accepted prefix between local resource owners](Transferring-the-accepted-prefix.md) exercises ten process-loss cuts in a three-database handover, including recovery after the outgoing store becomes unavailable.
- [Where can a Work Unit acknowledge an append that must survive rollback?](Committing-to-a-surviving-cut.md) tests protected decision ordering, exact retry and separate surviving custody under process loss and owner-image restore.
- [Which holders may release immutable Work Unit contents after a handover?](Retaining-immutable-content-across-attempts.md) proves a repeated storage-promise protocol and produces complete data-loss histories for two weakened receipt or release rules.

### Nested Work Units and managerial authority

- [When can Work Unit containment express managerial authority?](Authority-without-containment.md) characterizes single-subtree scope policies, bounds the cost of using multiple subtrees, and checks a direct policy with independent cross-cutting vetoes.
- [Which withdrawals must still work after a Work Unit moves?](Reparenting-and-surviving-withdrawals.md) distinguishes point-in-time scope from retained withdrawal power and derives the greatest safe policy under partial visibility.
- [When can sealed Work Units change parents independently?](Concurrent-moves-of-sealed-Work-Units.md) gives an exact compressed check for every mixture of parent edits and a constructive safe serial schedule when the target containment tree is valid.
- [What authority becomes visible during a batch of Work Unit moves?](Authority-in-mixed-containment-trees.md) checks every possible containment path and proves that an arbitrarily large set of moves can require one observable publication even when all intermediate structures are trees.
- [How hard is it to find a safe order for Work Unit moves?](Ordering-policy-preserving-relocations.md) proves NP-completeness with fixed containment filters, and gives a greedy algorithm with a deadlock certificate for a tractable subclass.
- [How much independent seal state must a Work Unit retain?](How-much-seal-state-survives.md) derives the exact future-observable quotient of independently asserted and jointly releasable vetoes, including a counterexample under authority reconfiguration.
- [Which changes of managerial authority preserve a compact seal record?](Seal-state-under-policy-evolution.md) gives an exact migration test, a cross-policy counterexample and a complexity result for permitted upgrade paths.

### Decision cost and trusted evidence

- [Which capacity promises can disconnected Work Units honor together?](Disconnected-resource-allowances.md) derives an exact check for fixed independent allowances under shared linear budgets and identifies a limit on definitive global denials.
- [How much shared headroom can a Work Unit keep private?](Privacy-and-shared-capacity.md) proves a reply-level conflict between exact pooled admission and concealment, and characterizes the minimum disclosure for bounded underuse.
- [Which observations must be revalidated at commitment?](Minimum-revalidation-at-commit.md) derives sufficient commit-time observations from possible interference, with decision-table checks for the local owner and an adaptive-read lower bound.
- [How much currentness evidence must survive a Work Unit rollback?](How-much-currentness-must-survive.md) gives matching stamp encodings and lower bounds for whole, per-owner and block recovery with authentic ancestral candidates.
- [Can a progress stamp reconstruct which prepared Work Unit updates committed?](Reconstructing-a-cut-from-prepared-updates.md) counts indistinguishable committed cuts under partial order and exhibits two different acknowledgments with identical recovered SQLite files.
- [Can an online owner maintain the minimum recovery stamp?](Maintaining-a-recovery-stamp-online.md) proves that replayable cumulative updates can force full version-vector state behind a much smaller validation result.

## Verification and open boundary

A fresh checkout of public main at 54ad041 replayed all 24 Python research scripts in this directory, including the two preceding studies. All exited successfully. A subsequent clean-checkout replay also passed the 25th script, which checks the online stamp lower bound against all common update suffixes in the bounded state graph. [Online replay source](https://github.com/rock-solid-sites/ASES/tree/1ca52e1385bd86bf250ba6d3b7f3245c112bda82/docs/research/kernel-0)

Z3 4.13.3 and cvc5 1.4.2 each returned the expected answers on all six SMT-LIB files: 31 unsatisfiable positive obligations and 12 satisfiable controls. This was a repeat execution on the same host, not independent model authorship or engine conformance testing. Exact commands and bounded coverage are in the individual studies. [Replayed source](https://github.com/rock-solid-sites/ASES/tree/54ad0418803eae03019031005c3447fca9963f7e/docs/research/kernel-0)

The strongest local content witness uses three separate SQLite stores and ten interruption points. General distributed conformance still requires a real owner to authenticate issuing scopes, enumerate every writable and destructive alias, and preserve both authority and accepted material under its declared failure model. The online maintenance result identifies when repeatable notifications force the full version vector to survive behind a compact validation result. An implementation must still establish how acknowledged publications and the trusted updater agree across process or storage failure.

## Foundational research checkpoint, 2026-11-28

These results are experimental research from the public main baseline [f443e20](https://github.com/rock-solid-sites/ASES/tree/f443e20640c8a458da244fcc590f0fd0733126df/docs/research/kernel-0). They evaluate separate clauses of proposed Kernel and Work Unit contracts.

| Demonstrated within its stated model | Load-bearing condition |
| --- | --- |
| Exact pooled admission distinguishes frozen headroom. A bounded-underuse disclosure has a tight minimum alphabet. | Observe terminal outcomes and support the declared request amounts. The conservative alternative must back its public allowance. |
| An implementation can pass every completed handover history check while deciding old acceptance after the replacement reply. | The completed-history interface hides the decisive event. A complete effect-bound witness or a replacement reply binding the accepted cut changes what can be verified. |
| Fresh numbering and the resumed selector's local view do not give outgoing-member availability. A census or old-enable closure certificate supports a different recovery contract. | Every independent old admission path is accounted for. The effect-closure alternative assumes participation and custody are addressed separately. |
| A protected adoption decision preceded by surviving staging preserves exact retry and committed bytes in the rollback fixture. | The protected decision and selected bytes actually survive the modeled loss. All authoritative replies and reads derive from that decision. |
| One tree node per managerial scope expresses exactly laminar extents. A direct scope relation supports crossing extents in the local Work Unit fixture. | Stable unique resource identities and independent veto semantics. The single-subtree restriction is an architectural choice. |

The triad is a candidate way to describe these duties. The examples give no argument that a triad, a separate native attachment object, or containment-derived authority is required. They also give no full sufficiency proof for the existing primitives. Test authority at the effect boundary, visibility across observers, and continuity across the declared failure projection. The same status label or named transition can satisfy one of these contracts and fail another.

**Clean-checkout replay.** From git tree `8f36011c2abf48431587011ab9440cff88a91331`, Python 3.12.14 ran all 32 research scripts, including the five new ones. The earlier fixed-membership rollback also passed its separate two-gate/two-attempt run. Z3 4.13.3 and the cvc5 1.4.2 wheel (library version `1.4.2-modified`) agreed on all seven unchanged SMT-LIB files: 36 expected unsatisfiable obligations and 14 expected satisfiable controls per solver. The documentation audit passed 20 unit checks and classified all five new reports Experimental / Derived without warnings. These checks replay the models and fixtures. They establish neither native-owner correspondence nor physical durability.

**Research frontier.** The protected decision and the staged reference are the next conformance seam. For a pinned native owner, identify the real authoritative append, replacement, first consequential observation and recovery decision. Check the two orders around replacement plus loss after durable acceptance and before any reply. Verify exact bytes, the stable old receipt, and rejection of a fresh old request against the owner's own effects. If any relevant effect lies outside the protected decision, first establish what authoritative evidence can survive. The distributed continuation asks whether an issuance certificate is complete across crash and publication, and whether the same gate may be omitted from admission fencing while remaining necessary for custody. The architectural continuation compares a tree-based candidate with direct scoped authority on the same public histories, including crossing scopes where they are required.

**Procedure provenance.** The research started under public workflow-orchestration v1.0.9. Its v1.0.10 and the experiment-admission procedure appeared on main during the run and were retrieved during consolidation. These local milestones have git checkpoints and retrospective evidence. No prospective revision-bound admission under the newly published procedure is claimed. Use its [current decision and experiment procedure](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md#experiment-and-decision-admission) for the next separate experiment.
