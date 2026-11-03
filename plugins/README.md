# ChatGPT plugin records — migrated

**Canonical custom MCP source and connector records now live in [rock-solid-sites/rss-tools](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp).** This directory is retained only for migration pointers and Git history. Do not update duplicate connector specifications here.

- [cgrmcp](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp/cgrmcp): canonical [connector record](https://github.com/rock-solid-sites/rss-tools/blob/main/mcp/cgrmcp/connector-record.json) and [skill](https://github.com/rock-solid-sites/rss-tools/blob/main/mcp/cgrmcp/SKILL.md)
- [Strategy Code Graph](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp/retired/strategy-code-graph): **RETIRED**, superseded by cgrmcp
- [ATProto Reader](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp/atproto-reader): active-development record and source links

Prior versions of these files remain available in this repository's Git history. **These records are not OpenAI plugin-import schemas.** Runtime tunnel IDs and credentials must not be committed.

## Explicit operator-directed planning dossier (non-runtime exception)

- [GitLab pipeline schedule control](gitlab-schedule-control/README.md) is an **experimental, agent-oriented problem/requirements/architecture record** placed here by direct operator request on 2026-11-03. It does **not** reverse the migration above or establish a deployed/installed plugin. Its eventual canonical MCP implementation and connector records, if approved, belong in [rss-tools/mcp](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp), not duplicated in ASES.
