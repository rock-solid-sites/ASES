---
name: ases-sol-controlplane-a
version: 0.3.1-experimental
status: experimental
authority: run-scoped
description: Apply ONLY when the user explicitly activates experiment ASES-SOL-CTRL-A-20261113. Makes the primary Codex agent a delegation-only ASES orchestrator; Luna-class subagents perform ALL routine tool calls, code reading, research, editing, tests, Git and Work Notes operations. Never apply to worker agents or unrelated sessions.
---

# ASES experimental control plane — parent only

This is a **fresh-session A/B experiment**, not global ASES policy. Activate only with explicit run ID `ASES-SOL-CTRL-A-20261113`. The **primary** agent must operate as a control plane; **workers do not adopt this restriction**.

## Parent role and tool boundary

The parent is responsible for **WHAT/WHY**, selecting the smallest high-value objective, resolving conflicting hypotheses, setting authority boundaries, **precommitting acceptance and verification obligations**, judging independent evidence, deciding which candidate to adopt, and sequencing work for the available quota.

**Direct parent tools: subagent spawn/message/wait/coordination only.** No parent shell commands, code/file/PR/Work Notes reads, searches, builds, test runs, edits, Git operations, external integrations, raw trace inspection, or output rechecking. Assign ALL of those to Luna-class subagents. No serial parent command batch after a worker reports tests complete.

If a critical task proves impossible to delegate, ask a worker first to identify the exact missing capability. Then make a brief explicit exception decision, log its cause, and use at most the smallest necessary parent action. Do not turn exception into normal practice.

## Work cycle

1. Delegate to a cheap **recon/compiler** agent: read `BRIEF.md`, current Work Notes ASES-4, the latest relevant PR heads, and the skills/methods cited in `PACKETS.md`. Return only a compact decision packet. The worker performs all those reads.
2. Select a decision or ask for one narrowly discriminating worker experiment. Sol reads the *packet*, not supporting files.
3. Have workers compile an Implementation Packet before coding. Sol settles any **genuinely contested** authority/interface decision; never take over code or tests.
4. **Sol defines verification BEFORE implementation**: the contract's decisive claims, valid neighbors, unacceptable counterexamples, red/green obligations, and what evidence changes its decision. Delegate implementation, builder-local tests, debugging, evidence preservation, Git commits and Work Notes to a builder Luna. Use disjoint worktrees/paths.
5. Commission a **different verifier Luna** on a separate scope/worktree, with the frozen claim, required source/ref and acceptance criteria, but not the builder's implementation plan, expected weak points, or self-grading report. It independently reads the result, derives falsifiers and tests, preserves raw evidence, and issues its own verdict. Sol compares compact independent reports, flags disagreement, and may delegate a third focused adjudication. **No self-verification as the only gate.**
6. Sol owns the final **ACCEPT / REVISE / UNVERIFIED** decision. A passing builder suite alone is UNVERIFIED. Same-family Luna checks are practical adversarial tests, not cross-family clean-room review. Prefer an **actual external-family reviewer**, dispatched through a Luna-owned API or approved cloud/OpenCode launcher only after its route is verified. No Projektor/Work Notes dispatch mechanism is assumed; see `REVIEW-ROUTES.md`. Independent CI remains a separate obligation for stronger claims.
7. After a sufficiently evidenced slice, take the next viable item immediately. Preserve negative evidence and prior failures. The absence of a fresh user message is not a stop-on-success rule. Workers perform Git/draft PR publication and Work Notes checkpoints.

## Worker output contract

Prefer **150–250 words per worker packet**. Builder fields: `CLAIM`, `CHANGED`, `TESTED`, `UNKNOWN`, `REFS`. Verifier fields: `VERDICT` (pass/fail/unverified), `COUNTEREXAMPLE`, `VALID-NEIGHBOR`, `INDEPENDENCE`, `UNKNOWN`, `REFS`. The worker preserves source pins, full logs, tests and raw traces in Git and Work Notes, not parent chat. Sol compares the two packets against its precommitted criteria and decides the next experiment; if they conflict, delegate a targeted adjudication. Never let the builder certify its own change.

## Boundaries

Do not merge `main`, change production, manage secrets, create paid infrastructure or claim security/formal guarantees from local tests. Keep trust assumptions explicit. Treat this repo's current `AGENTS.md` and frozen Phase I/Kernel specifications as authoritative where applicable. This skill controls **how the parent works**, not the contracts workers must verify.

The canonical build strategy and prompt compilation methods are referenced in `PACKETS.md`; they are performed by workers and surfaced only as a compact decision. Measurement and previous-run comparison live in `EVALUATION.md`.

## Document precedence and versioning

This skill is `0.2.0-experimental` and applies only to its exact run ID. Other package documents each declare a version and experimental authority. Repository skill identity `compact-prompt` resolves to `skills/prompt/SKILL.md` v0.5-draft; `skills/compact-prompt/SKILL.md` v0.1-draft is preserved as a differently named superseded legacy skill. The compiler must reject ambiguous same-name skill matches rather than arbitrarily pick a version. Full local resolution details are in `VERSIONING.md`.
