# Destination structure and ownership contract

**Decision:** destination repository `rock-solid-sites/ases-plugins`. Scope: ChatGPT plugins, compatible packaged skills, custom MCP connectors, their implementation source or external references, tests, release tooling and records. This is the **target layout**, not a claim of migrated source.

```text
AGENTS.md
README.md
DESIGN-AND-ASSURANCE.md
INVENTORY-AND-MIGRATION.md
SOURCE-AUDIT-2026-10-30.md
BUILD-PACKET.md
TARGET-STRUCTURE.md
ACCEPTANCE-CONTRACT.md
MIGRATION-MANIFEST.md
plugins/
  ases-workflow/
  cgrmcp-current/
  atproto-reader/
connectors/
  cgrmcp/
  atproto-reader/
  pending/
  retired/
skills/
  manifests/
tests/
  fixtures/
  client-acceptance/
releases/
docs/
```

## Ownership and naming

- `plugins/<id>/` holds **source-controlled package inputs**, compatibility manifests, build recipe and plugin-specific tests. Do not assume a historical portable plugin is the current App-backed plugin. Preserve each real App identity; keep historical releases under `releases/` or documented history.
- `connectors/<id>/` holds actual MCP implementation source **only when verified**, connector schemas, security boundaries, tests and deployment notes. If source is unrecovered, store a provenance reference and explicit BLOCKED status, not a fabricated implementation.
- `skills/manifests/` records upstream canonical skill repository, path, commit/hash, package destination and client applicability. ASES methodology stays canonical in `ASES/skills/`; app-specific skill source may be owned here if no external canonical source exists. Do not silently merge `prompt/` with `compact-prompt/`.
- `tests/` contains reusable contract fixtures and test runners; client acceptance evidence must identify actual client, release, prompt, result and time. Do not store credentials or private conversations.
- `releases/` contains immutable manifests identifying package source tree, upstream skill pins, built artifact hashes, installed plugin/App identity and rollback pointer. No secrets or ephemeral tunnel IDs.
- `docs/` contains detailed research and decisions; root documents are the first-read contract.

## Canonicality transitions

Initially ASES owns ASES methodology, `rss-tools` owns existing connector records/source, and current installed App-backed plugins own their deployed release identity. After M1 verified import, explicitly update source-of-truth pointers in old repos. Never switch live deployment or installed plugin just because files were copied. Use a migration map with old/new path, SHA, authority state and rollback reference.

## Non-goals

No new orchestration engine, general-purpose plugin framework, OpenCode guard migration, automatic service/tunnel changes, or reconstruction of missing source under the migration milestone. Keep retired Strategy Code Graph historical and Crosslink/Paseo pending.
