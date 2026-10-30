# Inventory, provenance and migration

**Status:** evidence-based starting inventory; not proof of live health. Audit exact sources, revisions, installed releases and deployments before migration. Destination repository name is not yet fixed.

## Assets and current authority

| Asset | Existing source / record | Known state | Destination handling |
|---|---|---|---|
| ASES Workflow plugin | `ASES/plugins/ases-workflow/`; four canonical skills in `ASES/skills/` | Private v0.1.0 plugin created; eight package files verified; natural-language auto-invocation FAILED in a fresh chat | Import package/release record and tests; keep methodology skills authoritative in ASES, pin copies in releases; repair discovery before accepting v0.1.1 |
| cgrmcp / CodeGraph | `rss-tools/mcp/cgrmcp/` registry/skill/connector record; installed private `cgrmcp-current` plugin | Plugin package exists; executable source may be outside GitHub; VPS/tunnel end-to-end health not established in recent work | Audit source and live topology; migrate canonical connector record and verified source; retain private tunnel, read-only bounds and recovery path |
| ATProto Reader | `rss-tools/mcp/atproto-reader/` and `rss-tools/atproto-thread-reader/` | Plugin package exists; Cloudflare Worker API path documented; MCP path and deployed-source parity need verification | Preserve deployed source provenance and current endpoint; avoid overwriting deployed code with an older recovery copy; test API and MCP separately |
| Strategy Code Graph | `rss-tools/mcp/retired/strategy-code-graph/` | RETIRED; superseded by cgrmcp | Preserve historical/retirement record only, not as active connector |
| Crosslink/Paseo MCP design | `rss-tools` branch `draft/crosslink-mcp-gates-20261029` | Design, permissions, retrospective and 12 intentionally RED acceptance tests; deployment not proven | Import as pending project only after review; do not label implemented or move it into active registry |
| General ASES skills | `ASES/skills/` | Canonical methodology skills; plugin bundles may contain pinned copies | Reference and package by manifest, not duplicate canonical ownership |
| Other `rss-tools` utilities | `rss-tools/TOOLING.md` and related directories | Broader agent-tooling library, not all ChatGPT plugins | Inventory only; migrate assets in scope rather than wholesale repo contents |

## Source and deployment rules

- Distinguish source, connector configuration, plugin packaging, installed release, active tunnel, deployment and actual client invocation; they may live in different places.
- Inventory exact commit SHA, path, license, external service, plugin/release ID, credential location (not value), runtime endpoint type, owner, operational status, tests and rollback before any move.
- Use one authority for each source file and connector record. Move authority only after a verified cutover; maintain pointers from prior locations.
- Preserve Git history/provenance where practical, otherwise document source commit and copy/migration method.
- Do not migrate secrets, local authentication caches, ephemeral tunnel IDs, machine-specific paths or production state into Git.
- Existing working connections stay untouched until the replacement path is independently verified. A copy is not a migration.
- Do not delete or retire the current source until provenance, package build, client invocation and rollback pass.

## GitHub creation constraint

Recent ChatGPT-originated GitHub repository creation attempts returned `403 Resource not accessible by integration` or were blocked. Existing-repository edits worked. The VPS `gh` route was subsequently authenticated as `rock-solid-sites`. Therefore stage here and let the VPS builder create the destination repo using the established authorized route; do not spend time retrying a known failing ChatGPT creation permission without changed evidence.

## Migration sequence

1. Audit sources and live installed releases; classify each asset ACTIVE, UNVERIFIED, PENDING, RETIRED or OUT OF SCOPE.
2. Freeze the destination root documents and acceptance contract before implementation.
3. Create a dedicated repository from this staging root; transfer exact source with provenance and preserve references to canonical ASES skills.
4. Add source-hash manifests, reproducible package builds, drift detection and initially red client acceptance fixtures.
5. Verify source/package parity and tests, then real ChatGPT-originated invocation against each claimed capability.
6. Record the new canonical authority and update old-repo pointers only after cutover; keep rollback and avoid breaking installed plugins.
7. Do not claim full migration complete while an asset's executable source, deployment or client invocation remains unverified.

## Decisions requiring evidence

The final repository name, which parts of `rss-tools` are actually in scope, whether plugin source can be fully recovered, and whether the client provides deterministic skill selection remain to be resolved during source audit or targeted tests. Do not treat any as implicitly settled.
