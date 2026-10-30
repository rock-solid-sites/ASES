---
title: Phase I — Bounded End-to-End Work Unit Lifecycle
document_type: Implementation Packet
authority: Derived / Non-canonical
status: FROZEN for this bounded experiment; NOT F3 acceptance
compiled: 2026-10-30
source_branch: research/phase-i-protected-work-unit-f3-20261029
source_commit: 04600b1b45e6510665bdc3108db9d51f6b2f8c56
---
# F3 next slice: one integrated protected Work Unit lifecycle

## Objective and precise completion
Build the smallest **nonvacuous, live, end-to-end witness** that connects the existing Kernel/Work Unit semantics and real host enforcement: create empty parent P and child C; explicitly grant supported access; accept exact bounded bytes x; replace an executing activity and reuse x; lose the authority holder; recover x **cold, sealed** from protected records; explicitly activate fresh authorized execution; accept distinct y; move sealed C from P to Q without gaining latent authority; read accepted data after activation; dispose accepted dependents; remove C following a current dependency check.

This is **one declared single-holder/single-host/supported-attachment profile**, not full F1, F2, F3, F4 or F5 closure. A reproducible counterexample to an indispensable premise is a valid stopping result. Avoid a general runtime, scheduler, orchestration service, new Kernel primitive, external sink, or cross-host claims.

The canonical meaning is in:
- \`codex/execution-engine-roadmap:docs/architecture/core-substrate/Phase-I-Verification.md\` §4 (F3) and §5 (F4), and \`Phase-I-Closure.md\` §§2–4, 7 (especially required operations and D1/D2 vs D3).
- \`docs/methodology/ASES Bounded Project Build Method.md\` and \`Implementation Realization and Assurance Selection Method.md\`.
- F1 @ \`d227a22b9bbc0732881bf58f6933ce46fddc08fa\`, \`docs/research/phase-i-f1/Phase-I-F1-Targeted-Run.md\`; F2 @ \`5fb690d4ba7544a4a7eb5fce9ca1e54485543d64\`, \`fixtures-f2/COVERAGE.md\`.
Do not copy frozen semantics into invented local definitions. Inspect and reconcile the exact source revisions before implementation.

## Starting evidence: preserve and reuse
- Existing F3 @ \`04600b1b45e6510665bdc3108db9d51f6b2f8c56\`. \`exp3/RESULT.md\` demonstrates explicit per-operation revocation using a Landlock-confined worker and mediator; \`authority-loss/REPORT.md\`, \`authority_loss.py\`, and \`run.json\` demonstrate one H=M fail-closed loss with actual SIGKILL/reap, retained socket, denied direct/symlink and no-op write opens, and **392,488 counted CPU iterations**. The surviving stale-mediator mutant returns forbidden bytes and is detected.
- Preserve the existing \`exp1/run/\` untracked artifacts and recovery snapshots. Never promote the temporary fixture or its Python harness into a chosen maintained architecture solely because it exists.
- F1's x/y, storage commit and two modeled recoveries are **abstract evidence**. F2 has **46 abstract replays**, **16 discriminating mutations**, and T05 prepared-only; none is concrete lifecycle assurance. Treat F1/F2 branches as read-only inputs.
- Use one logical current authority/commitment holder. Precisely identify where authoritative policy, independent accepted data, live external access-control policy and current source binding reside. A durable object must not be rebuilt out of an executor's cache or the test oracle.

## Required behavior and state distinctions
1. **Empty first:** Establish P and C as bounded, *inactive* Work Units, with no inherited grant, process-borne authority or accepted content. Create Q before the move only under an explicit authorized operation. Separate creator, manager, current execution ingress and ancestor ceilings.
2. **Grant and accept:** Establish explicit effective read and (where supported) write permissions under both ancestor and child; deny at least one missing-path-grant use. Accept exact byte strings x and y through a guarded whole operation, retaining content and recorded accepted identity/provenance outside any worker's mutable process state. Distinguish accepting bytes from presenting a candidate and from publishing an external effect. Do not call merely writing a file "accepted."
3. **Replacement:** W1 succeeds with authorized access to x; replacement creates W2 with newly current ingress, W2 can read x. A retained old W1 endpoint/request must fail after the replacement commit. If the old process is killed for this witness, that is not proof of fencing arbitrary surviving old routes; record the assumption and a targeted negative control if available.
4. **Engine loss and sealed recovery:** Actually terminate the selected authority/mediator process; keep the worker alive long enough to demonstrate safe CPU-only continuation and denial of a new affected protected operation. Stop all routes that depend on a dead holder under the declared profile. Then destroy/reconstruct the selected holder process **without restoring test-runner oracle variables**, independently read the protected records, validate their supported policy meaning and exact accepted x bytes, reconstruct inactive/sealed C before any use. If the available local storage cannot establish currentness, remain sealed and report obstruction rather than granting historic bearers.
5. **Fresh activation and y:** Only a newly and explicitly authorized management transition creates a fresh route; old ingress remains denied. Activate, read x, and accept distinct y; verify both accepted results and a whole recoverable current state. Record whether the covered failure class is process death, OS crash, or stronger durability; do not infer power-loss durability.
6. **Move without widening:** Seal C and move it from P to more permissive Q as one authorized whole effect, preserving C's identity, x/y contents and appropriate descendant/latent ceilings. After newly authorized activation, verify a previously prohibited write/use is **still denied** despite Q being permissive and that a specifically permitted read succeeds. A static "both sealed have no rights" comparison is not sufficient; test post-activation rights.
7. **Disposition/removal:** Explicitly dispose protected accepted dependent bytes under the declared logical-storage (not physical-erasure) guarantee, refuse an early removal while durable dependents exist, then remove the empty boundary only after a current complete dependency check. Refuse stale empty observations.

## Concrete enforcement and evidence contract
For each actual effect, identify the actor and enforcer, authoritative state reference, authorization check, physical route, protected storage change, and whole-commit/acknowledgment boundary. Whole changes have one visible abstract result; private preparation and rejected transitions are stuttering steps. Specify exact responsibility for handling partial writes, failed sync/commit, malformed/unsupported records and lost replies. If a candidate persistent mechanism is selected, compare it against the minimum alternative and justify it under the project's exclusion-first realization method; preserve existing useful code when safer than rewriting.

**Route inventory:** filesystem paths/aliases, open/inherited FDs, SCM_RIGHTS/descriptor passing, child processes, local or network IPC, credentials, shared memory, external sinks, and the live OS access-control policy. Classify each as disabled, completely mediated with a tested bypass attempt, or outside the expressly declared trust boundary. For *every enabled protected route*, attempt an unauthorized action after revocation or loss; no success allowed. Do not claim "full confinement" while enabled routes remain unevaluated. The safe baseline H=M prevents use by process death; it does not solve a surviving stale mediator. If another mediator must survive, require a concrete currentness/fencing mechanism and test it, or stop.

**Evidence:** pinned source SHAs, actual commands, version and kernel details, deterministic reference observations, exact x/y hashes and readbacks, authority-commit and storage-commit ordering, fresh/old ingress identifiers, PID/loss evidence, process-independent recovery, success/denial controls, status per route, timeout/memory bounds, raw host traces and mutations. A zero-effect implementation cannot pass; at least one authorized effect must succeed both before replacement and after fresh recovery.

**Host safety:** confined disposable lab fixture on established 8 GB VPS; no sudo, production policy, host network, real secrets, unmanaged destructive tests, main checkout edits, or cross-worktree mutation. Limit concurrent heavy model/proof runs and apply verified host-side five-minute Git checkpoints. Keep work in original F3 research branch, push and verify origin SHA.

## Minimal live acceptance sequence / stopping gates
| Gate | Required observation / failure control | Stop if |
| --- | --- | --- |
| L0 | Candidate mechanism and exact supported route, storage/commit/currentness premises written down; independent test expectation fixed | A declared indispensable trusted enforcement route cannot be supplied |
| L1 | Empty P/C; missing-grant denial; authorized x accepted and exact bytes read from independent holder | Acceptance is only metadata or worker-owned |
| L2 | W1 replaced; W2 reads x; old retained ingress denied | Stale W1 can still cause selected protected effect |
| L3 | H killed/reaped; CPU-only continuation; selected protected effect denied; cold recovery reads x sealed without test-oracle state | Old route remains usable, lost bytes are silently fabricated, or historical state auto-activates |
| L4 | Fresh authorization/activation; x read, y accepted; hashes and whole commitment checked | Activation bootstraps from history or y tears/inconsistent |
| L5 | Sealed move P→Q; no latent widening after activation; positive permitted read | Child gains previously forbidden authority |
| L6 | Early dependent removal denied; explicit content disposition; current empty removal succeeds | Stale empty check strands an object or discards accepted bytes |
| L7 | Small deliberate mutations expose at least one stale route, missing acceptance, early ack or lost content; host history mapped to one consistent F1 abstract explanation | Detector passes vacuously or needs incompatible abstract orders |

**Stopping condition:** One fully reproducible L0–L7 witness *for its declared profile*, **or** the first concrete counterexample / unresolved host trust premise that prevents claiming the next gate. If stopped early, preserve passed gates and counterexample with restart cursor. Even L0–L7 success is *not F3 complete*: T01–T24 broader trace coverage and F4 crash-cut/whole-history enumeration remain separate gates.

## Independent F2/F4 bridge, not a builder self-review
Keep F2 expectations on their pinned branch and adapt a **read-only** trace adapter for relevant T01, T02, T05–T12, T20, T23–T24 portions only when the new host endpoints exist. Record selected profile support and mark unsupported scenarios not-tested rather than changing expectations. A separate verifier must inspect evidence and run selected tests without trusting builder self-reports. Future clean-room F5 gets a pinned artifact, declared claims and canonical definitions—not this implementation packet or builder history.