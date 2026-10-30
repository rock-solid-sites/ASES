# Pre-build source audit — 2026-10-30

**Scope decision:** destination `rock-solid-sites/ases-plugins`; ChatGPT plugins, packaged ChatGPT-compatible skills, custom MCP connectors, source and release/test tooling. General Crosslink/OpenCode utilities remain in `rss-tools`. Canonical ASES methodology remains in `ASES`. Do not conflate OpenCode's `plugins/*.ts` with ChatGPT plugins.

**Evidence basis:** inspected current GitHub directory listings and `rss-tools/mcp/registry.json`, `rss-tools/mcp/CHATGPT-SKILLS-AUDIT-2026-10-30.md`, `ASES/skills/README.md`. Source and registry state are not a substitute for fresh client/runtime acceptance.

## Verified repository locations

| Component | Source evidence | Current condition / migration action |
|---|---|---|
| ASES Workflow | `ASES/plugins/ases-workflow/{README.md,sources.json,check_versions.py,dispatcher/SKILL.md}`; canonical `ASES/skills/{prompt,compile-build,workflow-orchestration,custom-mcp-connector}/` | Private v0.1.0 installed package exists but source tree and release build script are **not** checked into that directory; root dispatcher differs from packaged dispatcher. Recover package, manifest and builder reproducibly; record automatic invocation FAIL separately from migration acceptance |
| cgrmcp | `rss-tools/mcp/cgrmcp/{SKILL.md,connector-record.json,plugin/,tools/,RETROSPECTIVE-2026-10-27.md}` | Working current-account App-backed plugin connected via Secure MCP Tunnel; real four-tool ChatGPT invocations PASS on 2026-10-27. Executable editable server source still missing (last-known host-only); deployed bundle is not source. Do not reconstruct by assumption |
| cgrmcp skill packaging | `rss-tools/mcp/CHATGPT-SKILLS-AUDIT-2026-10-30.md` | Working App-backed plugin updated in place to v1.0.1 with `skills/cgrmcp-repository-research/SKILL.md`; .app.json unchanged; Plugin Creator read-back PASS and repo_open PASS. **Fresh-chat skill visibility/invocation unverified**. Older standalone cgrmcp v0.2.0 is distinct and should not replace it |
| ATProto Reader | `rss-tools/atproto-thread-reader/{src/worker.js,test/,package.json,wrangler.jsonc}`; `rss-tools/mcp/atproto-reader/{plugin/,connector-record.json,recovery/,RETROSPECTIVE-2026-10-26--27.md}` | Actual editable Worker source in Git; deployed v2 Worker is ahead of Git and recovery bundle exists. Current direct registered App `read_atproto` ChatGPT invocation PASS 2026-10-27; historical portable plugin is separate from working App. Preserve live Worker and App ID; reconcile source before deployment |
| ATProto skill packaging | `rss-tools/mcp/CHATGPT-SKILLS-AUDIT-2026-10-30.md` | Working App-backed package lacks the historical skill; skill port/update and fresh-chat discovery are separate pending changes, not migration prerequisites |
| Strategy Code Graph | `rss-tools/mcp/retired/strategy-code-graph/` | Retired predecessor, preserve historical record only |
| Crosslink/Paseo MCP | `rss-tools` branch `draft/crosslink-mcp-gates-20261029`; `rss-tools/mcp/registry.json` | Pending design and 12 red tests; `paseo-control` separate external artifact, not verified deployed. Import records as pending; do not represent as operational |
| Hostkey read-only | `rss-tools/mcp/registry.json` | External Worker ZIP; unauthorized response historically; provenance/source audit required before importing |
| Crosslink agent-prompt, knowledge, safe-fetch | `rss-tools/.mcp.json` pointers per registry | Three local legacy MCP servers with missing Git source; keep recovery inventory, not active ChatGPT packages |
| Chat Archive | `rss-tools/mcp/registry.json` | Old tunnel visible, implementation source unverified; recovery inventory only |
| ASES skills | `ASES/skills/` includes `prompt/` and separate `compact-prompt/` plus cgrmcp, atproto-reader, workflow and others | Both prompt variants exist; do not silently choose or merge. Audit frontmatter and current applicability before packaging. Preserve canonical authority in ASES |
| OpenCode plugins | `rss-tools/plugins/*.ts` including guards and dynamic-models | **Out of scope** unless a specific ChatGPT integration dependency is demonstrated |

## Critical architecture correction

The current `rss-tools` audit shows that a **working App-backed plugin** and an older **portable skills/MCP package** can be separate installations. Migrating files into a monorepo must not replace the active App registration. Prefer updating the *existing* connected App-backed package in place when adding app-specific skills, preserving `.app.json`, release identity and tunnel/Worker configuration. Keep generic methodology skills in skills-only plugin(s). Confirm exact compatibility and package schema from installed release and official documentation before implementation.

## Provenance and outstanding evidence

- Repository directory SHA listings confirm paths exist, not executable source parity, deployed revision or complete Git history.
- Capture exact repo commit SHA and file hashes during migration. Capture Plugin Creator release IDs, installed App identities, version and current manifest via authorized read-only tools; do not commit credentials.
- Audit the cgrmcp host/source, ATProto deployed-vs-Git delta, historical ChatGPT plugin archives, and any newly surfaced plugin projects before finalizing the import manifest.
- The latest `rss-tools/mcp/registry.json` is dated 2026-10-27; the skills audit is 2026-10-30 and supersedes some skill packaging status. Reconcile rather than copy either as unqualified current truth.
- Test user-facing automatic skill invocation in a **fresh conversation**. A read-back, manually loaded skill or successful MCP call is insufficient evidence of skill invocation.
- Preserve the working cgrmcp and ATProto connections. Never change deployed source/tunnels to perform repository migration.

## Scope and acceptance split

**Milestone M1 — repo migration:** canonical files and provenance imported; manifests/build checks reproducible; new repo read/write and CI pass; old references preserved; no production changes. May PASS even when a pre-existing skill invocation bug remains.

**Milestone M2 — runtime improvements:** ASES Workflow auto-invocation repair, cgrmcp skill fresh-chat activation, ATProto skill port, and any security/deployment changes. Each needs independent client-level acceptance and explicit release authorization.

**Not yet frozen:** executable cgrmcp source, deployed ATProto source reconciliation, complete installed-plugin inventory and exact release manifests. These are bounded audit gaps, not permission to guess or overwrite.
