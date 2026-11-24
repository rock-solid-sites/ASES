---
name: custom-mcp-connector
version: 1.0.1
description: Diagnose custom ChatGPT MCP integrations using live client discovery and the smallest discriminating tests.
status: current
---

# Custom MCP connector diagnostics

Treat the current ChatGPT Plugins UI, connected tool catalog and actual client-originated behavior as more authoritative than dated UI notes. Diagnose registration, activation, transport, OAuth, authorization, tool discovery, execution and persistence as separate boundaries. A package installing successfully is not proof of MCP registration or an end-to-end working tool.

Use the [operational MCP connection runbook](https://github.com/rock-solid-sites/ases-plugins/blob/main/docs/CHATGPT-MCP-CONNECTION-RUNBOOK.md) for detailed evidence gates. Check the actual client surface and existing route before declaring a missing feature or building replacement infrastructure. Separate ChatGPT registration/consent from upstream authentication and resource scopes; a working HTTP or CLI probe does not establish ChatGPT execution. Change one variable at a time, stop retries that add no evidence, and corroborate the actual request through the intended backend when material. Prefer read-only canaries, then authorized disposable writes. Preserve identities, existing connections and secret boundaries; do not create a new tunnel or server without a demonstrated need. Record PASS/FAIL/BLOCKED/NOT TESTED accurately with the next smallest discriminating check.

Use `skills/current/agent-launch/SKILL.md` only when real execution is necessary. Do not substitute historical VPS/Crosslink commands for observed current infrastructure.
