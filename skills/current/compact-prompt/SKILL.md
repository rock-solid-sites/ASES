---
name: compact-prompt
version: 1.0.0
description: Write minimal, observable agent tasks without leaking unnecessary model identity or project history.
status: current
---

# Compact ASES prompts

Choose the one operation: reconnaissance, independent review, implementation, verification, bounded compilation, orchestration or synthesis. Supply (a) exact target and pinned source, (b) only necessary governing context, (c) approved execution route and capabilities as caller-side settings, (d) one observable completion condition and (e) evidence/stop criteria.

Preserve user-settled constraints. Refer to canonical project specifications instead of pasting an archive. Avoid sending previous builder explanations to independent reviewers unless the builder's claim itself is the test target. Never instruct the receiving agent to identify or assert its own model/provider/effort; verify that through launch configuration. Do not manufacture decomposition, new agents or lengthy output schemas.

For current execution paths use `skills/current/agent-launch/SKILL.md`; for actual reviewer launches use `skills/current/review-launch/SKILL.md`. Historical fuller prompt research remains in `skills/prompt/SKILL.md` and `docs/methodology/`, but it is not a live launch authority when it conflicts with current infrastructure.
