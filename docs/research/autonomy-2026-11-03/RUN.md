# Autonomous Phase I research run — 2026-11-03

Research evidence and coordination checkpoint; no methodology adoption or Phase I acceptance.

Started approximately 19:31 UTC; requested window ends approximately 00:31 UTC November 4, subject to platform capacity. No authoritative remaining-quota measurement is exposed. Workspace initially contained HMS; ASES cloned separately. Main pinned at `e63ff28d98dd2c59d22d026d3f538263600278fa`; proposals pinned at `f8c700af1451f8545129aba466204867d344f12a`. Main remains untouched.

## Starting inventory

Read current AGENTS, ORIENTATION, ORCHESTRATOR, Compact Prompt, launch routes, bounded-build and realization-selection methodology. November 2 proposals are guidance only. Their proposed role splits, gates, archive schemas and ontology changes are not adopted.

| Stream | Source branch / revision | Starting evidence status / source artifact |
| --- | --- | --- |
| Kernel-0 timing | research/phase-i-kernel0-timing-20261029 / 9d0ecf1edbb7eb00e8ace4b2a4cf3e8ae65973c2 | Partial: event-cut 151-state fixture, capture/publication still atomic. `docs/research/kernel-0/timing-reduction/CHECKPOINT.md`, `evidence/inherited-state-2026-10-30.md` |
| F1 | research/phase-i-work-unit-f1-20261029 / d227a22b9bbc0732881bf58f6933ce46fddc08fa | Partial: finite contexts/mutations; binding/durability/remaining obligations/F5 unresolved. `docs/research/phase-i-f1/CHECKPOINT.md` |
| F2 | research/phase-i-hostile-fixtures-f2-20261029 / 8b3c7e06aaab97122d2fcdaf2ee891e62667154b | Partial: 46 histories, 16 mutations; T18 use-current prepared only. `docs/architecture/core-substrate/fixtures-f2/COVERAGE.md` |
| F2 host bridge packet | planning/ases-phase-i-f2-t05-host-bridge-20261030 / da72ed0d97f0e3adb1225cab2cd0dfa6b8eb415f | Selected T05 host subprofile only; not aggregate acceptance |
| F3 L5 | research/f3-l5-lifecycle-integration-20261031 / b49e1f66ddd91e501794f6c9381e1e96c19b096c | Partial integrated witness. `research/phase-i-protected-work-unit-f3/lifecycle/l5/INTEGRATED-RESULT.md` |
| L5 prior review | review/f3-l5-independent-verification-20261031 / f1e843ead51df1a776b51e3501b0cb946c71371d | PARTIAL; `research/phase-i-protected-work-unit-f3/lifecycle/l5/VERIFICATION-SYNTHESIS.md` |
| Lifecycle plan | planning/ases-phase-i-work-unit-lifecycle-20261030 / 415a03fe660f902cfffed6662d1a5982416ee9da | L6/L7, overall F4/F5 unexecuted; `research/phase-i-protected-work-unit-f3/IMPLEMENTATION-PACKET-LIFECYCLE.md`; `docs/architecture/core-substrate/Phase-I-Verification.md` |

Read-only inventory worker inspected all fetched refs and path histories: no later remote continuation of these streams found at startup. This is a bounded repository search, not proof no unpublished work exists. Main lacks the advanced F1/Work Unit directories. Historical failed/invalid fixtures remain historical evidence; no outcomes rewritten.

## Dispatch provenance and isolation

Caller: native Codex task delegation surface, cloud container, `/workspace/ASES` clone. Exact routes selected in caller configuration; real returned messages/artifacts establish execution, not child self-identification. No VPS, new provider purchase, credential transfer, or paid fallback used. Luna/Terra are same-family evidence; no cross-family review is claimed. Native tools replace inapplicable OpenCode/tmux liveness probes; observed messages and advancing commits are checked.

| Task | Caller-selected route | Owned area / output branch | Status |
| --- | --- | --- | --- |
| frontier_inventory | gpt-6-luna / high | read-only source inventory | Complete; incorporated above |
| kernel_timing | gpt-6.1-terra / high | /workspace/ases-kernel; research/autonomy-20261103-kernel | First parent-projection counterexample committed/pushed cbd0e22c1; next bounded pair/deadline discriminator underway |
| f1_obligations | gpt-6.1-terra / high | /workspace/ases-f1; research/autonomy-20261103-f1 | Current generation vs source binding discriminator underway |
| f3_source_review | gpt-6.1-terra / high | /workspace/ases-f3-review; review/autonomy-20261103-f3 | Fresh context; prior results withheld until first verdict. Native Landlock check blocked ENOSYS; policy-only discriminator underway |
| cross_layer | gpt-6-luna / high | /workspace/ases-cross-layer; research/autonomy-20261103-cross-layer | T18 concrete sink acceptance/currentness discriminator underway |
| evidence_audit | gpt-6-luna / high | read-only working evidence | In-flight/proposal reconciliation audit underway |

The orchestrator checkpoint is this branch `research/autonomy-20261103-run`. Worker branches retain their source ancestry; they will not be merged into main or into each other automatically.

## Live queue / resume cursor

1. Preserve and review first tranches: Kernel parent dependency/mask oracle, F1 source binding, L5 source route review, T18 sink currentness.
2. Kernel: repair fallible instrument with preserved RED control; bounded event cuts separating capture/publication if justified.
3. F3: isolate ancestor state/activation defects before L6. Host confinement is BLOCKED in this environment if Landlock remains unavailable; policy tests cannot close F3.
4. F4: smallest real pre/post durable acceptance crash cut with cold recovery and mixed-state negative control, reuse existing machinery.
5. L6/L7 only if governing dependencies permit; otherwise preserve boundary and continue independent experiment.
6. Clean fresh-context fixed-claim checks on pinned new artifacts, with same-family qualification.

Every consequential result must retain source/command, prediction, controls, bounds, actual observations/raw output, limitations, interpretation and next discriminator. Finite search is not unbounded proof. Expected mutation rejection differs from accidental test failure. Captured evidence is not automatically independently archived/recoverable evidence.

## Checkpoint — 19:55 UTC (subsequent to initial inventory)

Operator reported a concurrency error and directed fewer subagents. The native agent inventory then showed only the root active. Resumed with exactly two workers, no child dispatch: `kernel_continue` and `assurance_continue`, both caller-selected `gpt-6.1-terra/high`. Other working branches are preserved and idle. No claim is made that the error was caused by memory pressure or any particular component. Memory observation at 19:41 showed about 9 GiB available, without swap; that snapshot is not a concurrency-capacity guarantee.

| Result / branch | Pinned checkpoint | Evidence and qualification |
| --- | --- | --- |
| Kernel / research/autonomy-20261103-kernel | 3b6b880e265b189b551204be6510809bb60f2b1c | Pair scan: 26 rights-only mismatches, 4 rights+parents, 0/8 rights+parents+data comparable cases; bounded only. Parent selector, decoder traversal and inner deadline fixed separately. Whole capture/publication controls distinguish mixed/split mutations. Partial visibility plus blind stale remainder has no serial witness; constituent controls separate the causes. Currentness partition: 20 schedules, 120 steps, 140 counted cuts, 60 serial candidates; current rule all witnessed, stale rule 7 unwitnessed pre-revoke reads. `docs/research/kernel-0/timing-reduction/evidence/*result-2026-11-03.md` and raw logs. Frozen semantic oracle reused, no independent semantics/RTL/physical timing assurance. |
| F1 / research/autonomy-20261103-f1 | 9ca53bb3c98d644c8ac65948e6bf14f2489e0feb | Abstract source binding: 8 states/12 attempt edges, 0 baseline vs 4 mutant violation edges. Unix descriptor transfer retains connection PID but per-message credentials distinguish senders. Proxy test shows direct peer identity does not identify ultimate initiator; proxy prohibition not inferred. One actual executor+holder SIGKILL/reap and fresh-process retained-content continuity witness. `docs/research/phase-i-f1/*Experiment.md`, raw JSON and preregs. Synthetic authority association, Linux identity and local process-loss scope remain assumptions, not F1/F3 closure. |
| Cross-layer / research/autonomy-20261103-cross-layer | a71786ba958b6add8b2bfac3a1c29f1060c8f784 | `research/phase-i-t18-sink-order-20261103/`: T18 local sink 9 assertions; ordered acceptance rejects stale request and permits precommitted exact obligation; detached-check mutant admits stale effect. F4 26 assertions: preaccept kill 0 effects, durable-before-ACK kill 1 exact cold-recovered effect without ACK, normal ACK 1, early-ACK mutant ACK/0, truncated record rejected. No retry/exactly-once, power-loss, F3 or arbitrary sink claim. Initial NUL-in-argv failure and resulting defunct orphan disclosed in artifacts; no live orphan execution claimed. |
| F3 review / review/autonomy-20261103-f3 | c2c117568858fb179d7bb61e04ade42f7728e12f | Source verdict: D-only active/sealed check misses ancestor state. Dynamic policy counterexample, no reachable manager exploit claim. Native Landlock positive blocked ENOSYS. Original raw stdout absent; exact probe/inputs and separately labeled corroboration output preserved under `research/phase-i-protected-work-unit-f3/reviews/evidence-autonomy-20261103-f3/`. |
| F3 patch / research/autonomy-20261103-f3-policy | aea04ae45 | Ancestor active/sealed guard patched with positive and unsafe controls. Authentic stale manager-state replay stress counterexample retained; current published-record guard and sealed activation checks added under single-holder/no-concurrent-writer assumption. Activation positive routed through manager. `research/phase-i-protected-work-unit-f3/lifecycle/l5/` result/prereg/raw records. Authorized-grant exception and native host confinement remain unsupported/blocked; no L6/F3 acceptance. |
| Kernel isolated check / review/autonomy-20261103-kernel-pairs | 23a49c77fe3b334622c7e1a374cd2b0fc34918ef | Fresh-context source/independent execution check of 0d54fa63a; paired scanner logic and deadline behavior corroborated. Historical parent probe fails on repaired source; original-revision replay/instructions subsequently preserved. Same-family operational check, not cross-family formal review. Report includes reproduction output. |
| In-flight audit / review/autonomy-20261103-evidence | c81ec439e | `research/evidence-audit/inflight-evidence-snapshot-2026-11-03.md`: source/claim/digest checks, proposal qualification, raw preservation limits and observed status transitions. Digest matching verifies local bytes, not independent execution or complete archive recovery. |

These checkpoints were committed and pushed by their owners; final remote SHA verification remains part of closeout. No experimental branches were merged. Historical 402 provider logs in inherited L5 artifacts belong to prior work, not current-run dispatch.

Current next selection: Kernel coherent multi-field observation across publication cuts; F1 strongest remaining currentness/recovery/resource obligation discriminator. L6 native acceptance remains blocked by the indispensable host-enforcement premise. Restart from this index plus the latest worker branch evidence, without treating old CHECKPOINT prose as the newest result.
