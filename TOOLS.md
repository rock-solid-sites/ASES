# Available tools — quick session entry point

**Canonical inventory:** [docs/operations/tool-availability.json](docs/operations/tool-availability.json) (evidence-labeled, dated, no credentials).

For a fresh ASES conversation:
1. Read the inventory; it distinguishes **directly verified**, **connector-visible but untested**, **user-reported**, **configured but unexecuted**, and **historical** tools.
2. Check the capabilities of only the tools needed for this task. A connector used in an earlier chat may not be available in a fresh session.
3. Never infer paid-resource authorization, current free quotas, account balances, runner minutes, write rights, or backend connectivity from the inventory. Consult current provider observations and the separate provider-registry/funding policies.
4. When a tool becomes available/unavailable, update its status, evidence and verification date; use Git history to preserve what was previously believed.

As of 2026-11-01: **GitHub and GitLab repository MCP operations and GitLab shared-runner execution were verified** in ASES's Rust/Haskell evaluation. **GitHub Actions execution was not verified**; its workflow was committed. Other entries are explicitly scoped to their evidence.

Keep tokens, API keys, session URLs containing credentials, personal information and account secrets **out of this repository**. This file is a discovery index, not an authority or deployment manifest.
