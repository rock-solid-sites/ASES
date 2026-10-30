---
title: Phase I F3 — Authority-Holder Loss, Surviving Attachment
program: ASES / EDASES
document_type: Bounded Implementation Packet
status: Proposed; requirements frozen for this narrow experiment only
authority: Derived / Non-canonical
compiled: 2026-10-30
target_branch: research/phase-i-protected-work-unit-f3-20261029
target_commit: ad44b3ff93477cc694a5b0771c3b867afdfde620
---
# Implementation Packet — F3 authority-holder loss

## Objective and boundary
One falsifiable host experiment: when the actual authority holder for the existing **single protected read attachment** disappears, can an untrusted, still-running activity be prevented from initiating a **new** protected read through every route claimed by this small configuration, while already-granted CPU-only computation continues?

This is a test of a single engine-loss path and selected effect; it is **not** F3 lifecycle closure, durable accepted-content recovery, general confinement, D3 quiescence, or arbitrary external-effect/sink correctness. Fail-closed D1 evidence applies only to the selected read attachment. D2 is not thereby established for arbitrary outward effects; disclose all enabled outward routes, otherwise disable them in the fixture.

Do not assume that a process exit, a revoked flag, a closed socket, or Landlock alone proves full containment. Determine the actual concrete acceptance boundary. Retain the frozen Kernel and Work Unit requirements; new mechanisms are not automatically new Kernel primitives.

## Pinned evidence / reuse map
- **F3** target: `research/phase-i-protected-work-unit-f3-20261029` @ `ad44b3ff93477cc694a5b0771c3b867afdfde620`, particularly `exp3/RESULT.md` and `exp3/mediator_revocation.py`. Preserve and adapt its successful per-operation mediator authorization test and negative inherited-file-descriptor control. This is a reusable narrow *candidate*, not the selected system architecture.
- **F1** model: `research/phase-i-work-unit-f1-20261029` @ `d227a22b9bbc0732881bf58f6933ce46fddc08fa`, `docs/research/phase-i-f1/Phase-I-F1-Targeted-Run.md`. Abstract engine stop/recovery, stale-holder and C13 cases supply applicable behavior only. They assume trustworthy currentness, storage, source/route exclusion and abstract atomic boundaries.
- **F2** fixtures: `research/phase-i-hostile-fixtures-f2-20261029` @ `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`, `docs/architecture/core-substrate/fixtures-f2/COVERAGE.md`. T05 is prepared-only for real engine-loss/retained routes/CPU continuation; T03, T20, T24 are model-only. T18 use-current is prepared-only and is not selected for this test.
- **Normative definition:** canonical Work Unit A–L, provisional Kernel-0 semantics, Phase I closure C1–C13 and `docs/architecture/core-substrate/Phase-I-Verification.md` F2/F3 (read from `codex/execution-engine-roadmap`). Do not promote fixture choices into ontology.
- **Method:** `docs/methodology/ASES Bounded Project Build Method.md` and `Implementation Realization and Assurance Selection Method.md`. Because this is a disposable feasibility fixture, the existing Python harness may be reused; any maintained engine or runtime requires the full, exclusion-first realization process and applicable language-safety gates. No production realization choice is frozen here.

## Frozen behavior and discriminating observations
Name the concrete actors: authority holder H, mediation/enforcement point M (may or may not be the same process), untrusted activity W, protected object R, trusted loss observation L, and per-request admission point A. Record whether H/M are separate, where current authorization is held, which process and policy can revoke it, and when a read becomes authorized. Use a single logical holder: no multi-holder takeover.

1. **Positive baseline:** W remains confined and executes useful CPU-only work; through its declared narrow attachment, an explicitly granted request reads the known sentinel from R while H is alive.
2. **Real failure:** terminate H using an actual process-loss event, confirm its death independently, and record the observable ordering/cut. Do not substitute an explicit `REVOKED` control message for H's disappearance. If H also is M, test the resulting lost mediation path. If M survives H, test whether M actually loses the authority to admit the next request without relying solely on a stale cached grant.
3. **Post-loss negative:** with W still active, initiate a new read *strictly after* the trusted observed loss boundary through any surviving attachment socket. No new protected bytes may be delivered. A well-identified refusal or disconnection is acceptable for this narrow fixture. If loss cannot be detected/ordered at the enforcement point, report the missing trust premise or counterexample; do not fabricate instant death detection.
4. **Route challenges:** reattempt direct target and symlink access; enumerate/passively inspect relevant inherited or accidentally passed FDs, duplicate socket endpoints, descendants, IPC, filesystem aliases and reachable credentials. Mark each route **disabled / completely mediated / observed bypass / untested or excluded from the claim**. An enabled route that permits an otherwise forbidden post-loss read defeats the claimed boundary. Preserve the separate deliberate preopened-FD negative control from exp3; do not pass that FD into W in the positive configuration.
5. **Positive continuation:** demonstrate W continues a CPU-only operation on previously granted resources after H loss without any protected read succeeding. No unconditional termination is required. Already-returned bytes cannot be revoked, and in-flight operations initiated *before* L need a separately declared effect/authorization contract; do not count them as post-loss requests.
6. **Counterexample sensitivity:** deliberately weaken the exact enforcement point (e.g., allow a surviving mediator to honor stale authority) in a separate disposable configuration. Confirm the same test can detect an unauthorized new protected read rather than merely showing a failing request due to a missing fixture, closed unrelated path, or broken setup. Preserve mutation conditions and observed traces.

An accepted result requires both a nonvacuous pre-loss success and a post-loss denial with untrusted W still running. If the selected configuration cannot provide those observations, return a concrete obstruction and stop.

## F1/F2 reconciliation: which claims this slice does and does not advance
| Source obligation | Existing evidence | Required new physical evidence | Exclusions |
| --- | --- | --- | --- |
| F1 C6 / Work Unit C,H; F2 T05 | Abstract stop/seal, stale-generation checks; T05 prepared-only | H actually dies; W stays alive; fresh selected capability attempt fails | Physical source identity for arbitrary Work Units, entire lifecycle, durable content |
| F1 C13 / F2 T24 | Abstract ordered AC changes and policy inconsistencies | Identify real policy/enforcer, who can change it, and whether a partial/unsupported change fails closed for this selected route | General Linux policy update/revalidation and all existing handles |
| F2 T03/T20 | Abstract old source / overlapping holders | Show where any old holder or live channel remains actionable after H death, and limit claim to demonstrated exclusion | Host partitions, arbitrary multi-holder failover |
| F2 T18 / T19 | Abstract sink ordering and lost reply | No new sink is selected | Use-current sink ordering, exactly-once delivery |
| F1 C5/C7 / F2 T07–T10 | Abstract accepted x/y, two-loss and image/currentness witnesses | Not a goal of this slice | Physical accepted-byte recovery, rollback/power-loss resistance |
| Kernel timing | Event/cut fixture leaves request capture/publication atomic | No kernel timing claim made here | Physical timing reduction |

The F2 runner must remain independent of the F3 implementation. Translate only the relevant T05 observations into a host-test adapter once the concrete route exists; preserve its original expected outcome. Run T03/T20/T24 as targeted controls where supported, marking remaining elements untested. Do not report 'T01–T24 pass' from abstract replays.

## Environment, evidence, and stop condition
- All changes and execution on the existing VPS isolated F3 worktree; Git main and B/C/A worktrees untouched. No production permission, service, network, credential, `sudo` or host policy changes. Keep the existing untracked `exp1/run/` preserved; classify outputs before staging.
- Use bounded disposable fixtures, bounded runtime/memory, exact command lines, tool/kernel versions, real PIDs/process outcomes, event ordering, logs, source SHAs and positive/negative test observations. Avoid uncontrolled brute-force scans.
- Save the actual evidence and a route inventory. Record **confirmed / failed / inconclusive / not tested**; distinguish the authority-holder death event, mediator death, control-message revocation and request failure. Distinguish check outcomes from premises.
- Commit meaningful progress at most every five minutes when changed and push to the **existing F3 research branch**, verifying the remote SHA. Update the Crosslink task for F3 if available.
- **Stop** with (a) one reproducible bounded nonvacuous engine-loss exclusion witness meeting the declared route contract, or (b) a precise counterexample/missing trust premise. Do not expand into a general proxy, process supervisor, recovery engine, scheduler, UI or complete F3 lifecycle without a new bounded packet.
- Independent cross-family F5 review is **not** performed by the builder, and this packet/process history must not be copied wholesale into clean-room review.
