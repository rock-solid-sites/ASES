---
title: "Cross-environment agent coordination: cost of a blanket Git push gate"
program: EDASES
layer: Research
document_type: Field Observation
status: For Review
authority: Experimental
canonical_repository: ases
date: 2026-10-28
related_documents:
  - EDASES-topic-Git-Based-Engineering-Systems.md
  - ../../../../docs/ORCHESTRATOR.md
  - ../../../../AGENTS.md
---

# Field observation — push gates obstruct cross-environment coordination

**Date:** 2026-10-28  
**Case:** IT3812 / `rock-solid-sites/vps-runbook` backup reconciliation and recovery documentation  
**Status:** Observed workflow problem; proposed change is an **experiment**, not a global ASES policy decision.

## Operator observation

The existing **operator gate on every `git push`** initially appeared practical as a safety measure. In a workflow spanning ChatGPT, Windows-launched agents, the remote VPS, GitHub and Crosslink, however, it became a coordination obstacle: agent work was difficult to share, inspect and continue from another execution environment.

**Question for ASES:** Has the permission model incorrectly coupled **publishing a non-main review branch** with **integrating that branch into authoritative `main`** (and, where applicable, deploying it)?

This is a concrete candidate for reviewing the granularity and placement of human approval gates.

## Evidence and sequence

1. **Existing general policy.** At the observation date, [ASES `AGENTS.md`](https://github.com/rock-solid-sites/ASES/blob/main/AGENTS.md) says pushes require approval immediately before each push. [The orchestrator contract](https://github.com/rock-solid-sites/ASES/blob/main/docs/ORCHESTRATOR.md) says pushing is the operator's job. The VPS runbook's former Crosslink global rules and hook config additionally blocked ordinary `git push`.
2. **Multi-environment work.** A Windows-launched investigation accessed Hostkey VPS IT3812 but saved some recovery/backup evidence on Windows rather than in the canonical VPS work area. A later agent transferred redacted findings into the VPS runbook and pushed a review branch. Its local Crosslink issue was closed, but hub synchronization remained unverified because `crosslink/hub` was missing. The mislocated files and hub-sync failure are **separate observed problems**; the push gate is not proven to have caused them.
3. **Shared review need.** ChatGPT could independently read the [pushed backup reconciliation branch](https://github.com/rock-solid-sites/vps-runbook/tree/docs/it3812-backup-reconciliation-20261028), including evidence summaries and manifests, without needing access to the Windows workspace, VPS shell, or agent-local process. Before the push, work spread across separate machines and local tracker state was not equivalently available to all participants.
4. **Local countermeasure.** The operator approved an exception for `vps-runbook`: work and durable evidence originate on IT3812; sanitized findings are committed on a named **non-`main`** branch and can be pushed without a separate approval per push; integration to `main` remains operator-approved after inspection. The implementation is on [`policy/it3812-vps-branch-workflow-20261028`](https://github.com/rock-solid-sites/vps-runbook/tree/policy/it3812-vps-branch-workflow-20261028), at commit [`0b7cf279`](https://github.com/rock-solid-sites/vps-runbook/commit/0b7cf279c4e9f5041df733d42b8f4ab9036a1b7a).
5. **Limit of present evidence.** The new VPS-side branch policy and executable pre-push hook were committed remotely; the active VPS checkout's hook activation and a fresh agent's compliance **had not yet been demonstrated** at the time of this note. GitHub `main` was reported unprotected, so the local hook is not a server-side enforcement boundary.

## Mechanism to investigate

A **commit** is local to the repository copy. A **push of a task branch** makes it reachable to other agents, reviewers and environments. A **merge to `main`** changes the integrated, authoritative version. A **deployment/release** may be a separate high-impact action or may be triggered automatically by particular pushes.

If all pushes require the human to intervene, the operator becomes a synchronous data-transfer coordinator rather than only a decision and approval authority. This can create:

- Delayed or missing remote checkpoints and reduced cross-environment visibility.
- Agents whose handoffs depend on an inaccessible machine, stale checkout or agent-local state.
- Extra manual transfer/push operations and provenance ambiguity.
- Inability to review or resume the latest work from ChatGPT/GitHub even though local commits exist.

These are **plausible causal mechanisms**, not a measured attribution for the IT3812 mislocated-file event. Some push targets may trigger deployment, publish sensitive material or overwrite shared refs; those must not inherit blanket permission.

## Candidate review principle (not yet canonical)

**Gate high-consequence state transitions at the boundary they actually cross, rather than every operation that enables observation and coordination.** For ordinary development repositories this may mean:

| Operation | Candidate policy | Critical guard |
|---|---|---|
| Local commits | Autonomous within task scope | Traceability, scoped issue, checkpointing |
| Push to dedicated review/task branch | Pre-authorized, frequent | Named non-main branch, no force/delete, secret scan/redaction, explicit remote/refspec |
| Merge to protected `main` | Explicit operator approval after review | Verified diff, tests, relevant independent review |
| Production deployment, credential/infra mutation | Separate explicit gate | Side-effect-specific authorization and rollback |
| Push where push itself deploys or exposes data | Treat as consequential, not harmless | Repo-specific trigger and data classification |

A local pre-push hook is defense-in-depth, **not a complete security boundary**. The review must address server-side branch protections, API/connector writes that bypass local hooks, push-triggered CI/deploys, policy inheritance, secrets, and attackers or agents deliberately bypassing hooks.

## Proposed evaluation

Compare two otherwise similar sessions that involve at least two independent execution environments:

- **A: blanket push approval.** Commit locally, require human permission for every publication.
- **B: branch-only publication.** Agents can publish non-main branches autonomously; `main` integration and external side effects require distinct approval.

Measure: time until a second agent can inspect the latest work; operator interventions; successful handoffs; stale/missing checkpoints; duplicate work; provenance and artifact recovery; unintended writes to `main`; secret exposure; CI/deploy side effects; recovery after an interrupted agent or failed network connection.

Also test negative cases: attempts to push `main`, delete or force-update refs, push secret-bearing artifacts, push from the wrong checkout, and pushes that indirectly trigger a deployment. Verify **effective** enforcement, not just checked-in hook configuration.

## Decision boundary and follow-up

This observation **does not amend** ASES `AGENTS.md`, `docs/ORCHESTRATOR.md`, the execution engine, or Crosslink's global authorization rules. It is evidence for a future process and security review. Review whether to introduce **per-repository / per-ref / per-side-effect** push permissions, and whether the separate operator merge/deploy gates provide the intended security without preventing remote evidence sharing.

Related program: [Git-Based Engineering Systems retrospective](EDASES-topic-Git-Based-Engineering-Systems.md), especially agent coordination/lifecycle, Git-native engineering memory, and Experiment F.
