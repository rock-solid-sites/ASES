# ChatGPT plugin records — migrated

**Canonical custom MCP source and connector records now live in [rock-solid-sites/rss-tools](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp).** This directory is retained only for migration pointers and Git history. Do not update duplicate connector specifications here.

- [CodeGraph current operational procedure](https://github.com/rock-solid-sites/ASES/blob/main/skills/current/codegraph-actions-repository-research/SKILL.md): direct GitHub Actions/B2. No dedicated MCP.
- [Retired CodeGraph MCP records](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp/retired): historical only; not available operational routes.
- [ATProto Reader](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp/atproto-reader): active-development record and source links

Prior versions of these files remain available in this repository's Git history. **These records are not OpenAI plugin-import schemas.** Runtime tunnel IDs and credentials must not be committed.

## Current agent capability discovery

Use the [cross-connector capability index](https://github.com/rock-solid-sites/rss-tools/blob/main/mcp/CAPABILITIES.md) for basic functions, verified execution routes and known gaps in provider-managed and custom MCPs. GitLab on-demand CI already works directly from ordinary ChatGPT; schedule management remains a separate integration gap.

## Explicit operator-directed planning dossier (non-runtime exception)

- [GitLab pipeline schedule control](gitlab-schedule-control/README.md) is an **experimental, agent-oriented problem/requirements/architecture record** placed here by direct operator request on 2026-11-03. It does **not** reverse the migration above or establish a deployed/installed plugin. Its eventual canonical MCP implementation and connector records, if approved, belong in [rss-tools/mcp](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp), not duplicated in ASES.
