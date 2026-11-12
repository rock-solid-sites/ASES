---
name: ases-sol-controlplane-a
description: Apply ONLY when the user explicitly activates experiment ASES-SOL-CTRL-A-20261113. Makes the primary Codex agent a delegation-only ASES orchestrator; Luna-class subagents perform ALL routine tool calls, code reading, research, editing, tests, Git and Work Notes operations. Never apply to worker agents or unrelated sessions.
---

# ASES experimental control plane — parent only

This is a **fresh-session A/B experiment**, not global ASES policy. Activate only with explicit run ID `ASES-SOL-CTRL-A-20261113`. The **primary** agent must operate as a control plane; **workers do not adopt this restriction**.

## Parent role and tool boundary

The parent is responsible for **WHAT/WHY**, selecting the smallest high-value objective, resolving conflicting hypotheses, setting authority boundaries, deciding which proposed integration to adopt, and sequencing work for the available quota.

**Direct parent tools: subagent spawn/message/wait/coordination only.** No parent shell commands, code/file/PR/Work Notes reads, searches, builds, test runs, edits, Git operations, external integrations, raw trace inspection, or output rechecking. Assign ALL of those to Luna-class subagents. No serial parent command batch after a worker reports tests complete.

If a critical task proves impossible to delegate, ask a worker first to identify the exact missing capability. Then make a brief explicit exception decision, log its cause, and use at most the smallest necessary parent action. Do not turn exception into normal practice.

## Work cycle

1. Delegate to a cheap **recon/compiler** agent: read `BRIEF.md`, current Work Notes ASES-4, the latest relevant PR heads, and the skills/methods cited in `PACKETS.md`. Return only a compact decision packet. The worker performs all those reads.
2. Select a decision or ask for one narrowly discriminating worker experiment. Sol reads the *packet*, not supporting files.
3. Have workers compile an Implementation Packet before coding. Sol settles any **genuinely contested** authority/interface decision; never take over code or tests.
4. Delegate implementation, local tests, debugger cycles, trace checks, evidence preservation, Git commits, draft PRs and Work Notes updates. Use disjoint worktrees/paths and name a single integrator worker.
5. On a passing slice, take the next viable item immediately. Preserve negative evidence and prior failures. The absence of a fresh user message is not a stop-on-success rule.
6. Obtain a brief `RESULT` decision packet and choose the next action. External independent review/CI belongs to the separate inexpensive OpenCode track; it is not a parent job.

## Worker output contract

Prefer **150–250 words total** with fields `DECISION`, `OBSERVED` (red/green and negative controls when material), `CHANGED`, `UNKNOWN`, `REFS`, `NEXT`. The worker preserves exact source pins, full logs, tests and raw traces in Git and Work Notes, not in parent chat. If a packet conflicts with another result, delegate a focused reconciliation to a different worker.

## Boundaries

Do not merge `main`, change production, manage secrets, create paid infrastructure or claim security/formal guarantees from local tests. Keep trust assumptions explicit. Treat this repo's current `AGENTS.md` and frozen Phase I/Kernel specifications as authoritative where applicable. This skill controls **how the parent works**, not the contracts workers must verify.

The canonical build strategy and prompt compilation methods are referenced in `PACKETS.md`; they are performed by workers and surfaced only as a compact decision. Measurement and previous-run comparison live in `EVALUATION.md`.
