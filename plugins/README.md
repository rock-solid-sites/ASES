# ChatGPT Plugin Records

This directory stores reproducible source records for the private ChatGPT plugins used by ASES-related tooling.

These files are **repo-local deployment records, not an OpenAI plugin-import schema**. They intentionally exclude tunnel IDs, API keys, bearer tokens, and other environment-specific secrets.

Each plugin record captures:
- the user-facing/plugin namespace identity;
- the MCP backend and connection mode;
- the expected model-facing tool surface;
- relevant operational constraints;
- the reconstruction procedure;
- links to any model-facing skill maintained in this repository.

Current records:
- `strategy-code-graph/connector-record.json` — legacy GitNexus-backed read-only structural-code plugin.
- `cgrmcp/connector-record.json` — CodeGraph-backed repository-research plugin.

The ChatGPT plugin object itself is created in **Settings → Developer → Plugins** with **Connection: Tunnel** and bound to the corresponding OpenAI Secure MCP Tunnel. Tunnel IDs and runtime credentials must remain outside Git.
