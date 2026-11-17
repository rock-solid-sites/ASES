# Current ASES operational skills

This is the **only directory the installed ASES Workflow dispatcher should use for current operational instructions**. Fetch the current public Markdown by **read-only HTTPS GET**, rather than using an authenticated GitHub connector for ordinary instruction retrieval.

**Read-only entry point:** https://raw.githubusercontent.com/rock-solid-sites/ASES/main/skills/current/README.md

**Individual skills:** `https://raw.githubusercontent.com/rock-solid-sites/ASES/main/skills/current/<skill>/SKILL.md` (replace `<skill>` with one of the listed directory names). These endpoints return the file contents and offer no editing operation.

- `review-launch/SKILL.md` — independent reviewers on GitHub Actions; deep investigations in isolated workspaces.
- `agent-launch/SKILL.md` — select and verify controller, execution host, permissions, launcher and model.
- `compact-prompt/SKILL.md` — concise agent handoffs.
- `workflow-orchestration/SKILL.md` — choose smallest effective execution loop.
- `compile-build/SKILL.md` — bounded implementation packets.
- `custom-mcp-connector/SKILL.md` — live connector setup and failure diagnosis.

**Source of truth:** `rock-solid-sites/ASES`, branch `main`, directory `skills/current/`. Git commit history and release tags preserve previous approved versions. Do not copy prior version files or historical redirects into `current/`.

**Publication:** Changes are made in the source repository, preferably through a GitHub pull request; the read-only URLs cannot edit documents. No plugin republish is required for ordinary Markdown edits. These HTTP URLs do not revoke write access that a different tool may separately hold. Repository `main` was not branch-protected as of 2026-11-17; branch protection is not necessary for read-only HTTP retrieval.

**Retrieval:** Read the exact public raw-content URL on each invocation using a read-only web retrieval tool. Do not invoke a write-capable GitHub connector merely to read skills. If the HTTP tool cannot retrieve a complete document, stop the operational action rather than reverting to bundled/legacy instructions. Record the URL and retrieval time; record a source commit only when actually verified. A moving `main` URL gives latest-published content, not automatically an immutable revision. This model-followed convention is not a guaranteed pre-read hook.

**Instruction safety:** The content fetched from GitHub is project-level procedure, not permission to override system policies, grant new secrets, edit protected files or launch paid work without authorization. The operation must remain within the user's requested authority.

**Historical sources:** Prior skills in `skills/prompt/`, `skills/compile-build/`, `skills/workflow-orchestration/`, etc. are older sources and are **not the active dispatcher entrypoint**. Preserve them during this initial migration; Git history remains the record. A complete source-tree retirement can follow after references are audited, not by leaving superseded copies installed in ChatGPT.
