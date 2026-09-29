---
updated: 2026-09-29
---

# Sentinel Orchestration

This page is the current ASES guide for **Crosslink Sentinel**, the long-running poll/triage/dispatch tier.

For kickoff and swarm operation, model selection, operator approval, timeouts, review gates, and shared verification policy, use the canonical sources instead:

- `.crosslink/knowledge/agent-orchestration-playbook.md`
- `.crosslink/knowledge/model-discipline.md`
- `AGENTS.md`

Those sources take precedence over this page. Sentinel-specific guidance here must not be used to reintroduce an implicit model default, blanket kickoff/swarm timeout, deprecated wrapper, or other policy that conflicts with them.

## When Sentinel applies

Use Sentinel for autonomous maintenance driven by external signals rather than for an ordinary bounded implementation task. The existing configuration is shaped around GitHub issue labels such as:

- `agent-todo: replicate`
- `agent-todo: fix`

Sentinel follows a poll → deduplicate → triage → dispatch → collect → report loop. It is distinct from kickoff (one bounded task) and swarm (multi-phase coordinated work).

**Current repository state:** Sentinel is disabled in `.crosslink/hook-config.json` as of 2026-09-29. This page documents the tier; it does not activate it.

## Core CLI surface

The retained Crosslink command surface is:

```bash
# One-shot / preview
crosslink sentinel run
crosslink sentinel run --dry-run
crosslink sentinel run --label "agent-todo: fix"

# Persistent mode
crosslink sentinel watch
crosslink sentinel watch --interval 5

# Observe / stop
crosslink sentinel status
crosslink sentinel history
crosslink sentinel history --limit 20 --json
crosslink sentinel stop
```

Where a Sentinel command supports an explicit `--model` override, the model must still satisfy the current model-discipline and operator-approval rules. Do not copy a model ID from historical documentation.

## Signal handling

The historical Sentinel contract distinguishes at least these two label-driven tasks:

| Signal | Label | Intended scope | Verification intent |
|---|---|---|---|
| Bug replication | `agent-todo: replicate` | reproduce in tests; do not silently turn replication into a fix | local/discriminating evidence |
| Bug fix | `agent-todo: fix` | implementation plus relevant tests | CI-grade evidence where configured |

The exact enabled labels and runtime behavior are controlled by the current `sentinel` configuration and implementation, not by this table.

## Deduplication

The preserved Sentinel design uses multiple safeguards against redispatching the same signal:

1. source-level filtering;
2. an in-memory seen set;
3. a persistent database uniqueness constraint;
4. a durable issue/comment marker check.

If implementation or configuration no longer provides one of these mechanisms, the implementation/configuration wins and this page must be updated; do not infer a guarantee from prose alone.

## Retry and exhaustion

The Sentinel design supports an initial dispatch, a cooldown, and a bounded escalation/retry path. Exhausted work is intended to become a triage item rather than disappear silently.

Timeouts, models, retry counts, cooldowns, and escalation behavior are configuration/runtime values. Read them from the live configuration and current implementation; do not treat historical examples as defaults.

## Configuration authority

Sentinel configuration lives under `sentinel` in `.crosslink/hook-config.json`. The current file records, among other things:

- whether Sentinel is enabled;
- polling interval;
- maximum concurrent agents;
- source labels;
- default-agent settings;
- escalation settings.

### Unresolved configuration hazard

As of 2026-09-29, the repository config contains both a nested `sentinel.default_agent.model` value and a separate dotted top-level `"sentinel.default_agent.model"` key with a different value.

This document does **not** decide which wins. Before Sentinel is enabled, the effective precedence must be verified against the current Crosslink implementation and the duplicate representation reconciled. Until then, no model value in `.crosslink/hook-config.json` should be treated as standing operator authorization.

## Relationship to the canonical playbook

The canonical playbook owns:

- kickoff vs swarm vs Sentinel tier selection;
- explicit model selection and verification;
- operator-gated launches;
- task-matched runtime ceilings;
- startup/liveness verification;
- review and merge discipline.

This page owns only the Sentinel-specific poll/triage/dedup/retry surface.

## Historical source

This page was extracted from `docs/crosslink-subagent-orchestration.md` during Stage 3 documentation reconciliation. The old page mixed useful Sentinel material with obsolete kickoff/swarm instructions such as an implicit `opus` default and blanket one-hour timeout. The old path remains as a redirect for retrieval safety, but its former operational examples are no longer authoritative.
