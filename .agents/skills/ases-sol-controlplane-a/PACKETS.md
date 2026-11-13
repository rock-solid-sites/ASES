---
title: "PACKETS"
version: 0.3.1-experimental
status: experimental
authority: run-scoped
run_id: ASES-SOL-CTRL-A-20261113
supersedes_revision: eaf0d2c5092c1c1627e1ef79188378d1237f3e37
---

# Luna compilation workflow: strategy-to-builder, compact-prompt and separate verification

**Primary receives only short decision packets.** Source reconnaissance and packet preparation are subagent work.

Canonical method (worker reads targeted sections, not indiscriminately):
- `docs/methodology/ASES Bounded Project Build Method.md` — normal governing bounded build workflow and Implementation Packet.
- `docs/research/pre-build-compilation/Strategy-to-Builder Integration Packet Method - Derivation.md` — research derivation; preserve project meaning and freeze only known decisions.
- `skills/prompt/SKILL.md` — **current compact-prompt draft v0.5**, the explicit reference for this run. The older `skills/compact-prompt/SKILL.md` v0.1 is superseded and given a distinct legacy skill identity on this experiment branch; consult `VERSIONING.md`. Resolve by explicit path, identity and version—not by filename alone.
- `skills/workflow-orchestration/SKILL.md` — selective mode choice and handoff.
- `AGENTS.md`, `ORIENTATION.md` and frozen Phase I/Kernel source: consult as relevant to the *worker's assigned scope*.

## Luna packet compiler

A reconnaissance worker inspects relevant actual code, tests, source pins, interface choices and failed witnesses, then proposes an Implementation Packet: required state, acceptance invariant, reuse paths, exact files/interfaces, allowed neighbors and red controls, trust boundary, unresolved decisions, independent verification handoff, source hashes. **Sol must freeze decisive verification obligations before a builder starts.** The packet is a strategy-to-builder artifact, never a verdict.

Do not freeze exploratory uncertainties as facts. Ask the parent **only** the decisions that genuinely control a builder's choices. The parent receives a <=250-word decision packet, NOT the whole Implementation Packet. All long context stays in Git/Work Notes.

After parent decision, an implementation worker receives a short task along these lines:

> Implement the frozen packet at [exact path/ref]. Reuse the named source interfaces; do not reinterpret authority. Run the red baseline, green neighbors and negative controls, preserve raw evidence/source pins, commit to a dedicated draft PR and record the result in Work Notes. Escalate only a demonstrated contradiction that requires an architectural decision.

Builder should make few independent design decisions. After builder completion, dispatch a **different Luna verifier** with only the frozen problem/contract, target revision, required interfaces and allowed tools. Keep the builder's hypotheses, tests, initial failures and proposed expected answers out of the verifier's prompt. The verifier creates independent red/green and edge-case probes where practical, checks executable behavior and records its own uncertainty. A same-family verifier is not a heterogeneous review. For a separate external-family reviewer, select accounts from the full registry using `PROVIDER-SELECTION.md`, then use the two-tier route in `REVIEW-ROUTES.md`: tool-free model invocation for static falsification when possible, or a verified sandbox/OpenCode launcher for runnable investigations. This is **not** delegated through Projektor/Work Notes. A review route must be demonstrated before its verdict is claimed; independent CI remains a separate obligation. **Sol compares builder and verifier packets against the obligations and decides acceptance; it never delegates that decision to the builder.**

## Return packet format (<=250 words per worker)

`ROLE / CLAIM:` builder or independent verifier, and the frozen invariant being evaluated.

`VERDICT:` the worker's evidence-based result; only Sol issues final ACCEPT/REVISE/UNVERIFIED.

`OBSERVED:` the smallest executable witness / negative control / relevant environment, with before/after result.

`CHANGED:` exact code interface or invariant.

`UNKNOWN:` material limits and blockers; never claim unexecuted checks as green.

`REFS:` commit SHA, PR, local test command, Work Notes log (details stored, not pasted).

`INDEPENDENCE:` for verifier, declare sources seen and whether builder output was withheld; same-family limitations remain.

`NEXT:` one task Sol may delegate next.

## No parent data-plane exceptions by convenience

If the child needs a shell, API, log, code read, CI status, Git, metadata or file hash, the child obtains it. If a command fails, the child resolves ordinary instrumentation faults and returns evidence. A parent request for another long diff or manual confirmation is a prompt-compression failure; have a worker condense it or design a deciding experiment.
