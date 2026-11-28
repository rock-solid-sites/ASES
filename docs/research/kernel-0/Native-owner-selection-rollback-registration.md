---
title: Native owner selection rollback — bounded experiment registration
version: 0.1.0
program: ASES
layer: Research
document_type: Experiment Registration
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Native-acceptance-and-recovery-boundaries.md
  - docs/research/kernel-0/Custody-at-an-admission-closed-cut.md
last_updated: 2026-11-28
---

# Native owner selection rollback — bounded experiment registration

**Parent and qualification.** WNASES-36, continuing Kernel-0 research. Decide whether the existing native recovery surface alone can recover a published request's *owner settlement* after selection rollback, or whether a surviving outcome index or a change at the owner boundary is necessary. Static analysis predicts a distinction. Native UID run-04 tests loss of the sink with the owner selection available. PR #98 tests the pending admission limit. Neither applies the selective owner rollback below. Reuse those captures for their own scopes. The new observation is whether the actual native restart, retry and reconciliation stack interprets the same published event differently depending on which genuine F3 record is selected. Necessity is **READY** for this narrow discriminator. Dispatch status is **BLOCKED** until the frozen revision has admission and authority under the current method. [Source and archived evidence](Native-acceptance-and-recovery-boundaries.md) · [Admission procedure](../../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md#experiment-and-decision-admission)

**Pinned input and exact matrix.** Use unmodified native semantics at public PR #38 head `0bd51a34700164a5eb77efe98158fa37d1a74e23`, with the existing local native test drivers and captured file layouts. Use one scope and one uniquely named F4 effect A. In each of three fresh disposable cases, issue A through the native authorization path and obtain a confirmed normal F4 success and owner settlement. Save the genuine selected-record identifiers before reservation, at owner-local with a sequence, and after settlement. Keep the F4 journal, the live publication witness, the F1/inventory stores, protected record files and owner directory identity fixed. With the sink and owner writer stopped, restore only the selector file to the named earlier state as a controlled fault. Keep all data and processes private to the fixture. Reopen the native owner and use one existing cold sink and the original exact retry. No synthetic settlement or success flag is allowed.

| Cell | Selected F3 owner image after interruption | Observation to record |
| --- | --- | --- |
| R0 control | Current settled record. Reopen without rollback. | Exact old A is observable and remains owner-settled, with one accepted event. |
| R1 | Genuine local record after the append and before settlement. | Determine whether A's exact retry returns a historical observation and advances the owner to published under the unchanged F4 witness. |
| R2 | Genuine record after establishing the sink attachment but before reserving A. | Determine whether the actual API distinguishes F4 historical acceptance from missing owner settlement. If it restores settlement, identify the authoritative recovery step and its evidence. |

A successful experiment records both planes even when the overall call returns an error. Record original/selected owner identity and content hash, F1/inventory identity, retained file set, exact accepted payload and sequence, F4 journal hash, witness revision and cut, native reply status/body, owner before/after state and event counts. The controls require original eligible effect and confirmed two-plane settlement before changing the selector. Preserve absent/unknown/disagreement outcomes. Any new accepted journal line, unjustified F3 settlement, or silent loss of a confirmed outcome is adverse evidence. R0 must pass before interpreting R1/R2. If a legitimate restore barrier cannot be observed from the existing method, classify that cell inconclusive and stop the affected branch.

**Dispositions.** If R1 repairs and R2 retains a separate unresolved owner state, native custody can reuse repair only from the proven local cut. Continue design work on authority evidence before reservation is lost. If both restore, identify and read back the actual evidence source before crediting a stronger guarantee. If R0 fails or original inputs cannot be bound, report the harness/source blocker. If neither restored image permits recovery, keep the narrower recovery claim and transfer the actual missing mechanism to design qualification. A repeat that only reproduces the already retained sink-loss test is insufficient. This trial does not cover W5/W6, witness restart, simultaneous host loss, destructive reclaim or distributed membership.

**Envelope and stop.** A single local, unprivileged Codex execution, one case at a time, with at most four launches of the three fixed fixture cases including one same-scope setup retry. Cap aggregate wall time at five minutes and writable artifacts at 128 MiB. Use only fresh local files and local test endpoints in an isolated worktree, no provider, service deployment, container privilege, production data or additional remote experiment. Stop immediately on source mismatch, unexpected access outside the fixture, budget exhaustion or a failed R0 that survives the setup retry. Preserve exact commands, source receipt, all observed outcomes and negative/inconclusive evidence in the research branch and publish the usable result as experimental under `docs/research/kernel-0/`. Owner/controller classification and execution authority are recorded against the SHA-256 of these exact bytes in the parent Work Notes record. This registration itself grants no admission.
