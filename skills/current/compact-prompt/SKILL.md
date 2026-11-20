---
name: compact-prompt
version: 1.1.0
description: Select current task-relevant ASES prompting and preparation methodology before drafting any agent handoff, launch brief, Work Unit packet, or autonomous engineering assignment.
status: current
---

# ASES task prompts: select governing context before compression

**Entry condition:** When the requested deliverable is an ASES prompt, task packet, autonomous-run launch brief, builder/reviewer brief, or instructions for another agent, read **this current skill before drafting**, even if the user never says the word "prompt". A short prompt is not evidence that the right methodology was considered. Source selection follows the **requested work**, not a fixed legacy document list or the duration of the run.

## Task-dependent source admission

| Requested work | Required current material **before finalizing** | What not to do |
| --- | --- | --- |
| Single bounded handoff / simple edit | This skill, plus the actual target and governing local constraints | Do not load every skill or compile a trivial task |
| Autonomous multi-agent engineering campaign, orchestrator assignment, or multi-hour delegation | This skill **and** `skills/current/workflow-orchestration/SKILL.md`; consult `skills/current/agent-launch/SKILL.md` for actual dispatch, model/host/funding authority | Duration alone does not imply a frozen build packet. Preserve requested orchestrator-only/worker boundaries; never have a receiving agent select its own model |
| **Substantial bounded implementation** where requirements, interfaces, tests and decisions can be settled before the builder works, or a request specifically for an Implementation Packet | This skill, `skills/current/compile-build/SKILL.md` **and the full current canonical** `docs/methodology/ASES Bounded Project Build Method.md` | Do not claim a compiled/frozen packet without reading and applying the canonical method. Do not give the builder an unfrozen design and call it compiled |
| Open-ended research or architecture-dependent implementation | This skill and the appropriate current workflow guidance; select a bounded reconnaissance/decision task first | Do not force pre-build compilation before relevant facts are known |
| Independent reviewer assignment | This skill and `skills/current/review-launch/SKILL.md`; select only the claim, evidence and clean-room context needed | Do not pass a builder's whole process packet to a blind reviewer |

**Composite tasks select the union of applicable current sources.** For example, a five-hour autonomous engineering campaign may need workflow orchestration for the parent and the canonical bounded-build method **only for independently bounded build units** within that campaign. Parent coordination instructions are not a substitute for a worker's implementation packet, and the worker's packet is not a reason to make the parent read code.

`skills/prompt/SKILL.md` (earlier T3/Crosslink-oriented prompting) and `docs/research/pre-build-compilation/Strategy-to-Builder Integration Packet Method - Derivation.md` (derivation evidence) are **not active prompting authority**. Historical PRs or packets referring to those paths do not require loading them for a current launch. The canonical bounded-build methodology remains active at the path above; do not confuse it with its non-normative derivation.

## Compilation checks

1. Identify the operation (orchestrate, recon, implement, verify, review, synthesize), exact target/source revision, receiver role, settled user constraints, source ownership, completion condition and evidence destination.
2. Check whether the task is exploratory or sufficiently bounded for pre-build compilation. If compilation applies, actually read the canonical method; reduce the builder's remaining design choices, reuse known mechanisms, preserve exact behavior and specify verification. If it does not apply, do not manufacture a packet.
3. Select only relevant governing rules and evidence. A source link, existing file or historical title is **not proof it was read**, current or authoritative. Expand context only where it could materially change execution.
4. Specify caller-side capabilities, approved provider/model/account/funding route and stop conditions for actual launches, using `skills/current/agent-launch/SKILL.md`. Never put the receiver's model identity in its prompt or delegate model choice to the receiver.
5. Render the smallest independently reviewable task: goal, selected context, boundaries, observable result, verification, durability and stop/escalation conditions. Use references to pinned canonical/project sources rather than transcribing unrelated history.
6. **Readiness gate:** If a task-relevant current source was not retrieved or a prerequisite decision remains unresolved, label the brief **PRELIMINARY / NOT READY TO DISPATCH** and name that specific gap. Do not claim the prompt is ASES-compiled merely because it is concise or because an obsolete source was consulted.

**Verification limit:** These are caller-followed source-selection rules, not a guaranteed automatic skill invocation or prompt-loader hook. Keep a brief source/revision receipt in the coordinating issue or launch record; do not clutter the receiving agent's prompt with all routing metadata.
