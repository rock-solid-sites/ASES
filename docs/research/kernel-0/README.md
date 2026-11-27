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
