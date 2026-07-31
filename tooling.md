---
title: "Server Tooling Catalog"
tags: ["tooling", "reference"]
sources: []
contributors: ["OL2r"]
created: 2026-07-09
updated: 2026-07-20
---

The canonical catalog of custom tooling available to AI agents on this server is at: /home/claude-code/projects/Tools/TOOLING.md

This covers: CLI wrappers (claude, opencode, crosslink-moe), crosslink CLI (issue, kickoff, swarm, sentinel, session, locks, sync, etc.), orchestration scripts (verify, cleanup, build/dev), OpenCode plugins (crosslink-guard.ts), MCP servers (agent-prompt, knowledge, safe-fetch), hooks (work-check, prompt-guard, post-edit, heartbeat, etc.), skills (21 total with trigger phrases), agent definitions (9 subagent types), knowledge pages (7 topics), rules (22 language + 3 tracking modes), and known-broken items.

**Memory management:** The `claude` wrapper (`/home/claude-code/.local/bin/claude`) auto-wraps tmux background sessions in systemd scopes with MemoryMax=3G. See [server-memory-management.md](server-memory-management.md) for details.
