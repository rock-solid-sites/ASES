# Current ASES operational skills

## Using the index in ChatGPT

Say **"check the skill index"** (or **"list ASES skills"** / **"show available ASES skills"**). The installed ASES Workflow dispatcher should use a **read-only HTTPS GET** of this README, then **display only the skill names, short descriptions, and links** from the list below. An index-only request must **not** fetch individual `SKILL.md` bodies or load unrelated skills.

**For an actual task, select by the work product and its governing context, not by trigger words alone.** Any request to **write an ASES prompt, agent brief, Work Unit packet, autonomous-run assignment, builder/reviewer handoff or launch instructions** begins with `compact-prompt/SKILL.md`—even if the request does not use the word "prompt". Read its task-dependent source-admission table **before writing the brief**. Then retrieve only the additional applicable **current** skills: `workflow-orchestration` for autonomous multi-agent assignments, `compile-build` **plus the canonical bounded-build methodology** for genuinely bounded implementation preparation, `review-launch` for an independent review, and `agent-launch` before actual dispatch. Complex tasks can legitimately require more than one; trivial ones do not.

A standalone request to **list skills** remains index-only: do not fetch skill bodies. Historical `skills/prompt/SKILL.md` and the Strategy-to-Builder *derivation* are not substitutes for the current prompting skill or canonical bounded-build method. A source being linked in another PR or packet does not make it the current authority. If a necessary current method was not read, the resulting brief must be marked **preliminary/not ready to dispatch**.

The frontmatter/description of the installed dispatcher includes the trigger phrases, but **ChatGPT automatic skill selection is not guaranteed**. If this short phrase doesn't invoke ASES Workflow in a fresh chat, explicitly select **ASES Workflow** and repeat it. To share the process, provide this public README URL (a formatted GitHub page) or its raw read-only counterpart below.

This is the **only directory the installed ASES Workflow dispatcher should use for current operational instructions**. Fetch the current public Markdown by **read-only HTTPS GET**, rather than using an authenticated GitHub connector for ordinary instruction retrieval.

**Read-only entry point:** https://raw.githubusercontent.com/rock-solid-sites/ASES/main/skills/current/README.md

**Individual skills:** `https://raw.githubusercontent.com/rock-solid-sites/ASES/main/skills/current/<skill>/SKILL.md` (replace `<skill>` with one of the listed directory names). These endpoints return the file contents and offer no editing operation.

- `review-launch/SKILL.md` — independent reviewers on GitHub Actions; deep investigations in isolated workspaces.
- `agent-launch/SKILL.md` — select and verify controller, execution host, permissions, launcher and model.
- `compact-prompt/SKILL.md` — concise agent handoffs.
- `workflow-orchestration/SKILL.md` — choose smallest effective execution loop.
- `compile-build/SKILL.md` — bounded implementation packets.
- `custom-mcp-connector/SKILL.md` — live connector setup and failure diagnosis.

**Governing cross-task information method:** [ASES Task-Scoped Information and Handoff Method](../../docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) defines selection, authority and handoff. Retrieve it only when materially applicable; it is **not** an additional mandatory skill or a requirement to load every document for every task. The skills above still define specialized execution guidance.

**Source of truth:** `rock-solid-sites/ASES`, branch `main`, directory `skills/current/`. Git commit history and release tags preserve previous approved versions. Do not copy prior version files or historical redirects into `current/`.

**Publication:** Changes are made in the source repository, preferably through a GitHub pull request; the read-only URLs cannot edit documents. No plugin republish is required for ordinary Markdown edits. These HTTP URLs do not revoke write access that a different tool may separately hold. Repository `main` was not branch-protected as of 2026-11-17; branch protection is not necessary for read-only HTTP retrieval.

**Retrieval:** Read the exact public raw-content URL on each invocation using a read-only web retrieval tool. Do not invoke a write-capable GitHub connector merely to read skills. If the HTTP tool cannot retrieve a complete document, stop the operational action rather than reverting to bundled/legacy instructions. Record the URL and retrieval time; record a source commit only when actually verified. A moving `main` URL gives latest-published content, not automatically an immutable revision. This model-followed convention is not a guaranteed pre-read hook.

**Instruction safety:** The content fetched from GitHub is project-level procedure, not permission to override system policies, grant new secrets, edit protected files or launch paid work without authorization. The operation must remain within the user's requested authority.

**Historical sources:** Prior skills in `skills/prompt/`, `skills/compile-build/`, `skills/workflow-orchestration/`, etc. are older sources and are **not the active dispatcher entrypoint**. Preserve them during this initial migration; Git history remains the record. A complete source-tree retirement can follow after references are audited, not by leaving superseded copies installed in ChatGPT.
