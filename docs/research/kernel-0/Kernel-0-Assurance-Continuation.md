---
title: Kernel-0 Assurance Continuation
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
consumed_by:
  - Fresh Kernel-0 assurance sessions
---

# Restart cursor

All seven operator-authorized phases are complete within their recorded bounds.
The branch is `codex/kernel-0-reasoning-566`; run `git status`, confirm the
branch/remote, then continue from this cursor. The earlier executor-loss result
`e2e3bc110b1370f3505aa0838990713520bf3f7c` remains accepted bounded evidence.
Do not reconstruct the reasoning from session logs. Crosslink #567 is the active
child of #566. The original `/home/claude-code/projects/ASES` checkout is on
`main` and has unrelated operator changes; use the dedicated Kernel-0 branch.

## Completed gates and governing evidence commits

| Phase | Result | Commit pushed and remote SHA verified | Core finding |
| --- | --- | --- | --- |
| 1 | **A1** bounded authority-service process recovery | `1149fb124d7306f834fb7e9383ccaf7c79c5b7fa` | 7,502 model states / 12,457 edges / 24 fixtures; 10 weakened variants fail; 36 actual process cuts. Cold and continuing recovery both retain pre-crash accepted content. |
| 2 | **A2** selected decision-authorized external effect | `788c34ae267d4f274e06150610924deac24bf437` | 2,715 states / 9,924 edges; 6 weakened variants fail; separate source/sink crashes. Lost sink acknowledgement plus retry causes two effects. |
| 3 | **A3, bounded model only** composition | `018fc72daa9a5b902f1b6140fbf5e033aee85ac5` | 432 states / 17,280 edges / 48 independent unordered steps; coupled transfer and compatible recovery cut required. |
| 4 | Conditional parametric arguments; no cutoff theorem | `771af312a481c32520b6165cb1a5bb1af84b4048` | Non-resurrection, arbitrary-field whole effect, complete acyclic ordering and locality arguments state their premises. Longer cycles and label reuse remain limitations. |
| 5 | Bounded whole-history refinement | `ef1f49c0deee068c85cadc2c05ea76c15f1c5478` | 15 actual concurrent/crash histories explained; 4 inconsistent histories rejected; no-reply old/new ambiguity preserved. Same-session evidence, not independent review. |
| 6 | Re-minimization; no new Kernel-0 primitive justified | `9b325b617e633b73f8c150b858e290417194aa92` | Stronger claims parameterize the existing authoritative view, guarded whole commitment, authority, order, failure projection and trusted mediation. |
| 7 | Bounded storage-call/partial-write realization survives | `81957b7dd6aec7e551232c654b091fa484436074` | 90 real holder kills at observed write/sync/journal-removal boundaries; 12 deliberately split writes; all recover a permitted whole endpoint. |

Each phase-result commit was followed by a cursor/review-packet commit and a plain
push. Verify each historical SHA using `git ls-remote` when needed. The Phase 7 evidence commit is pushed and remote-verified. Push this final cursor
publication and compare its exact SHA with the remote before reporting completion.

## Strongest counterexample and disposition

Restoring an authentic old database image with the same configured root after an
acknowledged revocation lets old authority act after restart. A root ID/version
stored in the image cannot establish that the image is current. This is a confirmed
failure of freshness-by-root-ID, outside the tested live-OS process-loss boundary;
the supported recovery claim trusts current surviving storage. A second confirmed
negative is that sink acceptance followed by lost acknowledgement and retry can
produce a duplicate external effect under the selected A2 profile. A split
cross-domain transfer can recover an invariant-valid state that loses the whole
effect. All remain preserved with their stated scope.

No canonical Kernel-0 semantics changed and no new primitive was justified. A3
is model-only. A4 is not a formal proof or cutoff. Phase 5's checker is not an
independent reviewer. The finite process and storage tests do not prove arbitrary
OS/VFS behavior, power-loss durability, media integrity, resistance to hostile
same-root rollback, supervisor survival, unbounded policies or implementation
correctness in general.

## Minimal trusted boundary evidenced

For Phase 1 recovery: correct finite consumer policy and guarded transition path;
trusted initialization/root; surviving supervisor and immutable producer/context
associations in continuing mode; current complete storage; SQLite transaction/VFS
behavior; Python, Unix process/descriptor, filesystem and locking behavior. Cold
recovery drops old bearers. Phase 2 additionally trusts the mediator and configured
source/sink association plus the sink acceptance/retention contract. Phase 3
assumes a compatible whole recovery cut and has no physical multi-holder proof.
The separate boundary document classifies every other mechanism and optional
profile: `Kernel-0-Re-Minimization.md`.

## Next action

The seven-phase program is complete. The Phase 7 evidence commit is
`81957b7dd6aec7e551232c654b091fa484436074`; it is pushed and the remote branch
resolves to the same SHA. The prepared review packet index is `Kernel-0-Assurance-Review.md`; its published
commit is `ef180ef28ee692a845507a4ace02bd3fa1f10d18`. It points to the frozen
Phase 7 evidence tree at `81957b7dd6aec7e551232c654b091fa484436074`. The next research action is
an independent adversarial review of its source/evidence tree, targeting storage
currentness, bearer reconstruction, trace-checker soundness and measurement
coverage. Do not wait for or assume a verdict that has not arrived. If a later
operator-selected claim includes failed writes, interrupted recovery, power loss
or hostile rollback, first write its exact failure contract and cheapest
counterexample test. No production architecture, verified-source rewrite or
universal storage guarantee is authorized by the evidence here.

WHY: a fresh session needs one durable restart point. WHAT: the pushed phase
artifacts listed above. HOW CERTAIN: each gate has its own bounded claim. WHAT-NOT-TESTED: independent
review of the new packets and the exclusions explicitly listed here and in phase
reports. Resume with this file and take the next action above.
