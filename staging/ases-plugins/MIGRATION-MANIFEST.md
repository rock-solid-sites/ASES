# Migration manifest — pre-build, evidence pending

**Destination:** `rock-solid-sites/ases-plugins`. **Status:** design mapping only; source hashes and deployed revision verdicts must be filled from actual inspection. No move has occurred.

| Component | Current authority/source | Target | Milestone | Status / outstanding |
|---|---|---|---|---|
| ASES Workflow | `ASES/plugins/ases-workflow/`; `ASES/skills/` | `plugins/ases-workflow/`, `skills/manifests/` | M1 | PACKAGE SOURCE INCOMPLETE: recover v0.1.0 manifest, dispatcher and reproducible build |
| cgrmcp current App package | Installed current-account App-backed release; `rss-tools/mcp/cgrmcp/` records | `plugins/cgrmcp-current/` | M1 | VERIFY exact installed release manifest; preserve active .app.json |
| cgrmcp MCP backend | VPS source candidate `/tmp/opencode/cgrmcp-2026-09-26`; `rss-tools/mcp/cgrmcp/` | `connectors/cgrmcp/` | M1 | LUNA HIGH AUDIT PENDING: source Git history and commit `606fafc` |
| ATProto current App package | Installed direct App; `rss-tools/mcp/atproto-reader/` | `plugins/atproto-reader/` | M1 | VERIFY App release and package identity; historical portable package is not working App |
| ATProto Worker | `rss-tools/atproto-thread-reader/`; `rss-tools/mcp/atproto-reader/recovery/` | `connectors/atproto-reader/` | M1 | DEPLOYED SOURCE DRIFT; Luna audit pending, preserve recovery bundle |
| General ASES methodology skills | `ASES/skills/` | `skills/manifests/` | M1 | Pin only approved ChatGPT-compatible skills; do not migrate canonical ownership |
| Crosslink/Paseo MCP | `rss-tools` pending branch and external staged archive | `connectors/pending/` | M1 record only | PENDING, intentionally red tests; no active plugin |
| Strategy Code Graph | `rss-tools/mcp/retired/strategy-code-graph/` | `connectors/retired/` | M1 record only | RETIRED; no runtime |
| Other legacy MCP records | `rss-tools/mcp/registry.json` | `docs/` inventory initially | Audit only | Hostkey, Chat Archive, Crosslink local MCPs: source/release recovery not yet verified |
| General OpenCode utilities | `rss-tools/plugins/*.ts` | None | Out of scope | Remain in rss-tools |

For every actual import, append immutable evidence: source repo/ref/path, Git blob SHA and/or SHA256, destination path, build recipe, release identity if applicable, old authority, new authority, rollback reference, reviewer verdict. Do not fill unknown fields by inference.

## Work order

1. Merge Luna's **read-only** source findings into this manifest; distinguish verified editable source from bundles and archive references.
2. Read exact installed App/plugin release manifests through authorized Plugin Creator tools; keep current identity and connection bindings.
3. Freeze import list and root acceptance contract; make repo on VPS; copy/import source with provenance.
4. Run M1 checks and record any deferred items. Leave M2 fixes to separate, authorized changes.
