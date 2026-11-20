---
title: Real-Work Field Trial - Prompt Methodology Source Admission
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-20
---

# WNASES-22 field trial: relevant source existed but was not selected

**Scope:** Observed real coordination incident in a different ASES conversation on 2026-11-20. The user shared the assistant's admission and requested correction in this chat; no other chat was edited or a model launched. This is a natural operational observation, not an independent or blinded test.

## Observed failure

A five-hour autonomous engineering launch brief (Astra 6.2 parent directing predominantly Luna subagents; parent orchestrates/reviews and does not independently read code/search; Terra excluded) was prepared after consulting current `compact-prompt`, `workflow-orchestration`, `agent-launch` and earlier draft PR #45's `PACKETS.md`. The author **had not read all task-relevant active preparation methodology** before claiming an ASES-compiled launch brief. On questioning, the assistant downgraded it to a preliminary draft and suggested reading the older `skills/prompt/SKILL.md` and the historical Strategy-to-Builder derivation.

**Grounded source defect:** At the observed ASES main revision `03c5b954f4eaee0f11e4bdd57d0bd8e07d5233de`, `skills/current/compact-prompt/SKILL.md` was a 15-line compressed instruction, `skills/current/README.md` explicitly chose that skill alone for builder-prompt requests with further skills optional, and the current source-selection contract did not clearly classify "autonomous engineering assignment" as a prompt-production request. The active `docs/methodology/ASES Bounded Project Build Method.md` existed, but its pre-build compilation requirements were not guaranteed to be read when a **frozen Implementation Packet** was actually being prepared. The older 330-line `skills/prompt/SKILL.md` and research derivation are **not current operational prompting authorities**.

**Failure class:** selected skill != selected governing method. The missing edge was task/work-product -> applicable source, not file existence, a need for a permanent graph, or a demand to restore historical root/startup documents.

## Distinct real task-view cases

| Case | Actual goal | Minimum relevant context | Unnecessary context | Evidence/status |
| --- | --- | --- | --- | --- |
| A — simple navigation/method-selection document correction | Correct the source-selection entrypoint and mark incomplete prompts honestly | Current skills index, current `compact-prompt`, `workflow-orchestration` and `compile-build` texts; canonical bounded-build method only to verify the *referenced active method* | Full historical T3/Crosslink prompt skill, old Strategy-to-Builder derivation, unrelated provider inventories, a new task graph service | Exact active source paths inspected. **PR #73** merges four current-source Markdown changes; a small ten-item static selection check passed. No model dispatch |
| B — five-hour autonomous engineering launch brief | Parent orchestrates/reviews; subagents do investigation/implementation/testing under explicit model authorization; no Terra | Current `compact-prompt` plus `workflow-orchestration`; `agent-launch` before dispatch; `review-launch` for independent reviewer work. For **each sufficiently specified bounded implementation unit** also read `compile-build` and the full current canonical bounded-build method | Old `skills/prompt/SKILL.md`, research derivation as governing rules, legacy Crosslink/VPS instructions, the entire ASES docs archive. Parent should not consume all worker implementation details | **Before:** launch draft admitted incomplete. **After:** published selector defines this required context set; original external-chat brief has NOT been rewritten or retested |

**Important conditional:** The five-hour time window alone does not make the whole campaign a bounded build. An open-ended integration campaign begins with recon/orchestration; only work units with sufficiently settled behavior, interfaces and test obligations qualify for pre-build compilation. Reading the full canonical build method is a prerequisite **when claiming a compiled Implementation Packet**, not a mandatory ritual for all delegation prompts.

## Corrective source changes

[ASES PR #73](https://github.com/rock-solid-sites/ASES/pull/73), merge commit [`8963c160a2e9`](https://github.com/rock-solid-sites/ASES/commit/8963c160a2e93a58c30e710300184a3da98238bd), updates:

- `skills/current/README.md`: route "task packet", "autonomous launch", "handoff" and "agent brief" through `compact-prompt` even without the word "prompt"; select other sources by actual task kind.
- `skills/current/compact-prompt/SKILL.md` v1.1.0: task-dependent source selection, explicit current authority, and a "PRELIMINARY / NOT READY TO DISPATCH" gate when a required current method is unread.
- `skills/current/compile-build/SKILL.md` v1.0.1: actual read of full canonical method before claiming a bounded build is compiled.
- `skills/current/workflow-orchestration/SKILL.md` v1.0.1: autonomous orchestration briefs must consult the prompt skill, with conditional compilation per worker unit.

A ten-item **source-content check** passed before merge; this is *not* a runnable agent or model-behavior test. The actual user-report incident supplies the observable failure; the commit supplies the repaired source-level route.

## Topology interpretation and next falsifier

The field case supports **task-dependent context admission**. It does *not* support a graph database or persistent resolver: a compact skill index plus explicit source-selection rules can express the missing edge. It also establishes a limitation of purely manual prompting: unless the task classification is performed consistently, a compact packet can omit a method even while all sources are available.

**Still unverified:** whether a newly started ChatGPT chat automatically selects the installed ASES Workflow plugin; whether it reads the updated `compact-prompt` when no keyword "prompt" appears; and whether it fetches the canonical method when genuinely compiling a bounded implementation packet. The installed dispatcher is a model-followed locator; GitHub Markdown changes are not a deterministic pre-read hook. These require a separate fresh-chat behavioral test, with actual retrieval evidence and a checked prompt, not merely a green text-inspection check.

**Proposed next test:** In a fresh ChatGPT conversation, ask naturally for a five-hour autonomous ASES assignment without saying "prompt" or naming a skill; record which `skills/current` files were actually retrieved, whether compilation was appropriate and the exact canonical document read. Fail if older prompt/derivation documents are presented as current authority or the brief claims fully compiled with unread prerequisites. Repeat for a trivial documentation handoff to verify selectivity. No API-paid model launch is needed to run this selection test.

## WHAT-NOT-TESTED

No model executed the launch brief. No actual change was made in the other active chat. No ChatGPT auto-skill-selection probability was measured, no authenticated provider queried and no restored legacy agent/start document tested. PR #72 remains a draft research proposal; PR #73 is a published operational instruction correction. No Luna run was queued or used for this field case.
