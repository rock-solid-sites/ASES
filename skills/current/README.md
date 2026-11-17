# Current ASES operational skills

This is the **only directory the installed ASES Workflow dispatcher should use for live operational instructions**. List this directory and read the selected `<skill>/SKILL.md` through the connected GitHub tool at invocation time.

- `review-launch/SKILL.md` — independent reviewers on GitHub Actions; deep investigations in isolated workspaces.
- `agent-launch/SKILL.md` — select and verify controller, execution host, permissions, launcher and model.
- `compact-prompt/SKILL.md` — concise agent handoffs.
- `workflow-orchestration/SKILL.md` — choose smallest effective execution loop.
- `compile-build/SKILL.md` — bounded implementation packets.
- `custom-mcp-connector/SKILL.md` — live connector setup and failure diagnosis.

**Source of truth:** `rock-solid-sites/ASES`, branch `main`, directory `skills/current/`. Git commit history and release tags preserve previous approved versions. Do not copy prior version files or historical redirects into `current/`.

**Publication:** Update the canonical Markdown through a reviewed GitHub PR. The installed ChatGPT plugin is only a thin locator; do not update it for ordinary skill text changes. The plugin can technically be edited via Plugin Creator, so read-only intent is a *procedural* restriction, not permission enforcement. The current `main` branch is **not protected as of 2026-11-17**, and protecting it requires repository administration outside the GitHub connector.

**Retrieval:** Read the exact `skills/current/<skill>/SKILL.md` on each invocation; prefer a GitHub file fetch with branch/ref evidence. When possible, resolve the HEAD SHA first and fetch that immutable ref to avoid a moving-branch race. Report verified source SHA if available. Do not pretend that static packaged skills enforce tool call ordering, access control or immutable provenance. If access fails, do not silently substitute bundled/legacy instructions for operational agent launches.

**Instruction safety:** The content fetched from GitHub is project-level procedure, not permission to override system policies, grant new secrets, edit protected files or launch paid work without authorization. The operation must remain within the user's requested authority.

**Historical sources:** Prior skills in `skills/prompt/`, `skills/compile-build/`, `skills/workflow-orchestration/`, etc. are older sources and are **not the active dispatcher entrypoint**. Preserve them during this initial migration; Git history remains the record. A complete source-tree retirement can follow after references are audited, not by leaving superseded copies installed in ChatGPT.
