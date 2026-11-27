# Kernel-0 research

**Current requirements input:** [Kernel-0 Evidence Packet](Kernel-0-Evidence-Packet.md). This is the deliberately neutral requirements/adequacy packet, not a complete Kernel ontology, primitive vocabulary or implementation. Its contents remain unchanged during the November documentation reconciliation.

For current architectural intent and non-goals, see the [Execution Engine Vision](../../architecture/Execution%20Engine%20Vision.md). For implementation history, November experimental PRs, remaining Work Unit adequacy tests and original rejected designs, see the [Engine Architecture and Experiment History](../../historical/Engine%20Architecture%20and%20Experiment%20History.md).

The [September reasoning-session decision record](Kernel-0-Reasoning-Session-Decision-Record.md) explains the historical open-derivation protocol; it is not a current launch assignment. Preserve clean-room separation for new open derivations: do not include candidate designs, reviewer conclusions or historical implementation paths unless necessary to the requested task. Actual dispatch requires the current task-relevant skills and authorization, not September model/host assumptions.

[Tenure reuse and delayed admission](Tenure-reuse-and-delayed-admission.md) gives a conditional lower bound on safe identifier reuse, a bounded schedule experiment, and the resulting Work Unit owner verification obligation.

[One handover across resource owners](One-handover-across-resource-owners.md) derives a two-resource witness for a failed Work Unit handover and checks a conditional construction for repeated replacements over a fixed set of resources.

[Checking a history across repeated handovers](Repeated-handover-histories.md) gives a complete decision procedure for an ordered succession with known local orders, and a lower bound on the number of observations needed to explain some failures.

[Changing the set of resource owners at handover](Changing-the-set-of-resource-owners.md) extends the arbitrary-member proof to joins and removals, including delayed activation at an owner that never opened.

[Which gates must fence a handover?](Which-gates-must-fence.md) gives a certificate for barriers on partially completed writes, a selection complexity bound, and controls for cached approvals.

[A local owner witness for activation, replacement and replay](Local-owner-admission-and-replay.md) exercises W5/W6-shaped local histories at process-loss cuts on either side of the actual append commit.

[Which withdrawals must still work after a Work Unit moves?](Reparenting-and-surviving-withdrawals.md) distinguishes point-in-time scope from retained withdrawal power and derives the greatest safe policy under partial visibility.

[What must survive replacement to answer an old retry?](Receipt-retention-after-replacement.md) counts distinguishable histories with identical application bytes and verifies conditional reclamation under a prefix-release contract.

[Which capacity promises can disconnected Work Units honor together?](Disconnected-resource-allowances.md) derives an exact check for fixed independent allowances under shared linear budgets and identifies a limit on definitive global denials.

[What a receipt reveals across Work Unit scopes](What-a-receipt-reveals.md) tests reply-level isolation in the local owner and checks scope-relative receipts across the same crash windows.

[Aborting a handover without reviving obsolete votes](Abortable-handover-and-catch-up.md) proves abort and direct catch-up first for fixed membership, then for a changing voter set, including a counterexample to simply conjoining the two prior invariants.

[Which observations must be revalidated at commitment?](Minimum-revalidation-at-commit.md) derives sufficient commit-time observations from possible interference, with decision-table checks for the local owner and an adaptive-read lower bound.

[When is an earlier gate snapshot safe to resume?](Recovering-a-gate-with-votes-in-flight.md) derives an exact recovery threshold for one genuine gate rollback with old summaries and escaped votes still deliverable.

[When can sealed Work Units change parents independently?](Concurrent-moves-of-sealed-Work-Units.md) gives an exact compressed check for every mixture of parent edits and a constructive safe serial schedule when the target containment tree is valid.

[What authority becomes visible during a batch of Work Unit moves?](Authority-in-mixed-containment-trees.md) checks every possible containment path and proves that an arbitrarily large set of moves can require one observable publication even when all intermediate structures are trees.

[How hard is it to find a safe order for Work Unit moves?](Ordering-policy-preserving-relocations.md) proves NP-completeness with fixed containment filters, and gives a greedy algorithm with a deadlock certificate for a tractable subclass.

[What evidence shows that accepted contents survive handover?](Surviving-content-at-handover.md) separates version and storage custody from a checkable recovery certificate, and derives exact domain-loss bounds for linear contents.

[Transferring the accepted prefix between local resource owners](Transferring-the-accepted-prefix.md) exercises ten process-loss cuts in a three-database handover, including recovery after the outgoing store becomes unavailable.

[Which holders may release immutable Work Unit contents after a handover?](Retaining-immutable-content-across-attempts.md) proves a repeated storage-promise protocol and produces complete data-loss histories for two weakened receipt or release rules.
