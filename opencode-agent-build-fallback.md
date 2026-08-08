---
title: "opencode agent: 'build' fallback (diagnostic)"
tags: ["opencode", "agent", "diagnostic", "guard"]
sources: []
contributors: ["OL2r"]
created: 2026-08-08
updated: 2026-08-08
---

# opencode agent resolution: why a session shows agent 'build'

A kickoff-launched session that reports 'chat.params agent: build' is NOT a truncated 'builder'. It is upstream opencode's built-in default primary agent, literally named 'build', selected by silent fallback.

## The mechanism

'opencode run --agent X' (packages/opencode/src/cli/cmd/run.ts, localAgent()) rejects any agent whose resolved mode is 'subagent':

- 'agent X is a subagent, not a primary agent. Falling back to default agent'
- returns undefined -> server resolves defaultAgent() -> built-in 'build' (hardcoded at packages/opencode/src/agent/agent.ts, name: 'build').

The agent name is never truncated; it round-trips correctly. The fallback target just happens to be named 'build'.

## Config source of truth

'.opencode/agents/*.md' frontmatter mode is merged AFTER opencode.json's agent section (packages/opencode/src/config/config.ts), so the .md mode wins. Kickoff-launchable primary roles must declare 'mode: primary' in the .md frontmatter; 'mode: subagent' forces the fallback.

## Was this a fork bug?

No. The #154 durable-silent-hang fork does not touch agent resolution (agent.ts / run.ts unchanged in the fork diff) and is not even installed on the live binary. Do not widen the guard or change the fork to fix this; fix the .md mode.

## Fix

Set 'mode: primary' in the role's .opencode/agents/<role>.md, then confirm the session agent via 'chat.params agent' in the guard log and the session DB.
