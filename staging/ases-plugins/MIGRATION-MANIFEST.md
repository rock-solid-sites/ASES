# Migration manifest — pre-build, evidence pending

**Destination:** `rock-solid-sites/ases-plugins`. **Status:** design mapping only; source hashes and deployed revision verdicts must be filled from actual inspection. No move has occurred.

| Component | Current authority/source | Target | Milestone | Status / outstanding |
|---|---|---|---|---|
| ASES Workflow | `ASES/plugins/ases-workflow/`; `ASES/skills/` | `plugins/ases-workflow/`, `skills/manifests/` | M1 | INSTALLED PACKAGE VERIFIED: USER PRIVATE v0.1.0, release `pluginrel_6ae44a5192b081919b4e20864845ff5e`; eight files available via Plugin Creator; source pins at ASES commit `061291fdd7a3affba243bbc18d20b1749d0de664`; automatic invocation still unverified/previously failed |
| cgrmcp current App package | Installed current-account App-backed release; `rss-tools/mcp/cgrmcp/` records | `plugins/cgrmcp-current/` | M1 | VERIFY exact installed release manifest; preserve active .app.json |
| cgrmcp MCP backend | VPS source candidate `/tmp/opencode/cgrmcp-2026-09-26`; `rss-tools/mcp/cgrmcp/` | `connectors/cgrmcp/` | M1 | PARTIAL: requested workspace absent; 59-commit history and `606fafc` not found. Deployed bundle and source maps survive at `/home/claude-code/.local/share/cgrmcp/app/dist/`; preserve evidence, do not claim original source |
| ATProto current App package | Installed direct App; `rss-tools/mcp/atproto-reader/` | `plugins/atproto-reader/` | M1 | VERIFY App release and package identity; historical portable package is not working App |
| ATProto Worker | `rss-tools/atproto-thread-reader/`; `rss-tools/mcp/atproto-reader/recovery/` | `connectors/atproto-reader/` | M1 | EDITABLE SOURCE RECOVERED in VPS `/home/claude-code/projects/Tools/atproto-thread-reader/` at `b33c962f96a55a58d5377659a61db7a8697fed2e`, with MCP implementation commit `fbe08276683427f18757c9684451d33434b4de9a`; rss-tools copy stale. Preserve source/history before parity/deploy |
| General ASES methodology skills | `ASES/skills/` | `skills/manifests/` | M1 | Pin only approved ChatGPT-compatible skills; do not migrate canonical ownership |
| Crosslink/Paseo MCP | `rss-tools` pending branch and external staged archive | `connectors/pending/` | M1 record only | PENDING, intentionally red tests; no active plugin |
| Strategy Code Graph | `rss-tools/mcp/retired/strategy-code-graph/` | `connectors/retired/` | M1 record only | RETIRED; no runtime |
| Other legacy MCP records | `rss-tools/mcp/registry.json` | `docs/` inventory initially | Audit only | Hostkey, Chat Archive, Crosslink local MCPs: source/release recovery not yet verified |
| General OpenCode utilities | `rss-tools/plugins/*.ts` | None | Out of scope | Remain in rss-tools |

For every actual import, append immutable evidence: source repo/ref/path, Git blob SHA and/or SHA256, destination path, build recipe, release identity if applicable, old authority, new authority, rollback reference, reviewer verdict. Do not fill unknown fields by inference.

## Work order

1. Luna High read-only findings incorporated 2026-10-30 (user-provided report). Verify source commit and files during authorized preservation; original cgrmcp Git tree remains missing.
2. Read exact installed App/plugin release manifests through authorized Plugin Creator tools; keep current identity and connection bindings.
3. Freeze import list and root acceptance contract; make repo on VPS; copy/import source with provenance.
4. Run M1 checks and record any deferred items. Leave M2 fixes to separate, authorized changes.

## Source-recovery verdict — Luna High, 2026-10-30

Read-only SSH reconnaissance on `IT3812` as `claude-code` (report supplied by operator). No files, repos or services changed.

**ATProto Reader — VERIFIED editable local source, preservation pending.** `/home/claude-code/projects/Tools/atproto-thread-reader/src/worker.js` and tests contain MCP implementation. `Tools` local `main` at `b33c962f96a55a58d5377659a61db7a8697fed2e`; parent work includes `fbe08276683427f18757c9684451d33434b4de9a`. Local checkout diverged from `origin/main`; GitHub publication is not established. Stale migration-facing checkout at `/home/claude-code/projects/rss-tools-mcp-gates-20261029/atproto-thread-reader/`. Preserved deployed bundle at `mcp/atproto-reader/recovery/deployed-worker-bundle-2026-10-26.js` is comparison evidence, not preferred source. **Next:** authorized, non-destructive preservation of local commits/source with verified provenance, then parity review; no deployment.

**cgrmcp — PARTIAL artifact, original history MISSING.** `/tmp/opencode/cgrmcp-2026-09-26` absent; neither reported 59-commit Git tree nor `606fafc` recovered in bounded checks. Runtime artifact and source maps at `/home/claude-code/.local/share/cgrmcp/app/dist/`. Documentation at `/home/claude-code/projects/rss-tools-mcp-gates-20261029/mcp/cgrmcp/` and `/home/claude-code/projects/ases-pgs2-report-20261024/plugins/cgrmcp/` is not implementation source. **Next:** locate remote/archive; preserve bundle as binary recovery evidence under explicit approval, but do not mislabel it editable source or require speculative reconstruction for M1.

**Milestone treatment:** ATProto source preservation is a bounded prerequisite for importing its verified implementation; cgrmcp may be recorded as deferred source recovery while migrating its manifests/records, with an explicit M1 scope exception. Runtime acceptance remains independent.

## Installed ASES Workflow package — verified via Plugin Creator, 2026-10-30

- Plugin backend ID: `plugins_6ae44a4ff8f081919325009658a40cae`; USER / PRIVATE; name `ases-workflow`; version `0.1.0`; current release `pluginrel_6ae44a5192b081919b4e20864845ff5e`.
- Eight files: `.codex-plugin/plugin.json`, `plugin.json`, `sources.json`, `skills/ases-workflow/SKILL.md`, `skills/compile-build/SKILL.md`, `skills/custom-mcp-connector/SKILL.md`, `skills/prompt/SKILL.md`, `skills/workflow-orchestration/SKILL.md`.
- V2 manifest `.codex-plugin/plugin.json`: skills path `./skills`; `keywords: []`, `interface.capabilities: []`, `defaultPrompt: null`. V1 `plugin.json` also present. These fields are descriptive observations, not proven causes of invocation failure.
- Dispatcher frontmatter describes automatic invocation for agent prompts, delegation, bounded builds and MCP debugging. Actual fresh-chat automatic invocation remains **NOT VERIFIED** (historical failed test); do not infer behavior from frontmatter.
- `sources.json` pins `rock-solid-sites/ASES` commit `061291fdd7a3affba243bbc18d20b1749d0de664` and SHA256 for four methodology skill snapshots. Read-only inspection only; no release mutation.
- Next: check bundled skill text against pinned Git source and prepare explicit fresh-chat positive, paraphrase and negative-control tests; do not change plugin until evidence identifies the failure mechanism.

## Preservation results — Luna High, 2026-10-30 (operator-provided)

**ATProto:** Sanitized source-only root commit `96f48acc0268350af0a154df3d84ea39e13faf4f` pushed to `rock-solid-sites/rss-tools` branch `recovery/atproto-reader-source-snapshot-20261030`, containing six files under `recovery/atproto-thread-reader/` including `RECOVERY-PROVENANCE.md`. Original local commits `fbe08276683427f18757c9684451d33434b4de9a` and `b33c962f96a55a58d5377659a61db7a8697fed2e` recorded as provenance, **not retained as ancestry**. Remote branch fetched and verified; 36 tests passed / 0 failed under Node 22.22.3; no deployment. Source-to-deployed-bundle parity still unverified. Branch: https://github.com/rock-solid-sites/rss-tools/tree/recovery/atproto-reader-source-snapshot-20261030

**cgrmcp:** Encrypted runtime archive `/home/claude-code/backups/cgrmcp-runtime-20261030.tar.gz.gpg` (SHA256 `b8bcd02805dbc9ac891239da053703289d8351fb9ff4d4e4dece57ab4543b53b`), GPG AES-256, mode 0600. Decryption key separately at `/home/claude-code/.secrets/cgrmcp-runtime-archive-20261030.key` (mode 0600; never import to Git). Archive includes 55 runtime files (493,732 bytes total) and `MANIFEST.sha256`, `INVENTORY.txt`; decrypt/checksum verification passed. Source maps have no `sourcesContent`. Secret-marker scan targeted, not comprehensive. Original editable source/history still MISSING; keep archive private, outside repo, pending independent review. Note encrypted archive and key currently share a host, so this is recovery preservation, not an independently durable off-host backup.

**M1 disposition:** ATProto snapshot is now import-ready as source with provenance, subject to branch content review and source-to-deployed parity before runtime changes. cgrmcp source remains an explicit deferred exception; plugin metadata and connector records may be migrated independently. No installed plugin or service changed.
