# Tooling Discovery Rule

Before using any custom tooling on this server, check the canonical catalog:

**Primary reference:** `/home/claude-code/projects/Tools/TOOLING.md`  
**Crosslink knowledge:** `crosslink knowledge show tooling`

This catalog documents every custom wrapper, script, plugin, skill, hook, agent definition, MCP server, and orchestration command available. If a tool you need isn't listed, it may not exist yet — proceed cautiously and document your findings.

Key tools every agent should know about:
- `claude` wrapper — translates Anthropic CLI to opencode run; you MUST use `--model provider/model` format
- `crosslink` — issue tracking, sessions, kickoff, swarm, sentinel
- `crosslink-moe` — parallel multi-model adversarial review orchestrator
- `crosslink-verify.sh` / `crosslink-cleanup.sh` — pre-merge verification pipeline (in ASES/scripts/)
