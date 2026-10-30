# ASES Plugins — staging root

**Status:** pre-migration design workspace. **Destination:** `rock-solid-sites/ases-plugins`, to be created by the VPS builder after the design and inventory are settled. This directory is NOT the new canonical source for existing tools.

## Purpose

Develop, package, test, release and maintain ChatGPT skills/plugins and custom MCP connectors using ASES methodology. A plugin is not accepted merely because its files exist, it registers, or its tools can be invoked manually. Acceptance is the intended user-facing behavior through the real client.

## Read first

1. [AGENTS.md](AGENTS.md) — required operating instructions for builders and reviewers
2. [DESIGN-AND-ASSURANCE.md](DESIGN-AND-ASSURANCE.md) — end-to-end behavior, state applicability, realization and release gates
3. [INVENTORY-AND-MIGRATION.md](INVENTORY-AND-MIGRATION.md) — existing tools, authority and staged migration
4. [SOURCE-AUDIT-2026-10-30.md](SOURCE-AUDIT-2026-10-30.md) — source evidence, installed App distinctions and migration gates
5. [BUILD-PACKET.md](BUILD-PACKET.md) — bounded implementation and handoff for the VPS builder

The four files are designed to become root-level files in the destination repository. The canonical ASES methodologies remain in `rock-solid-sites/ASES/docs/methodology/`; do not fork their meaning here.

## Proposed structure (subject to the build packet's necessity and source audit)

- `plugins/<id>/`: plugin packaging, manifests, release metadata, invocation fixtures and acceptance results
- `connectors/<id>/`: MCP implementations or pinned external source references, client configuration templates, connector records, tests and deployment notes
- `skills/`: packaged copies or links/manifests referencing their authoritative skill source
- `tests/`: shared end-to-end canaries, protocol/client fixtures and conformance checks
- `releases/`: immutable release manifests, source hashes, client compatibility and rollback records
- `docs/`: detailed design decisions and investigations; foundational instructions stay at root

Avoid building generic frameworks, duplicate registries, or a new orchestration engine without a demonstrated requirement.

## Authority and migration boundary

Until the destination is created, validated and explicitly designated authoritative:
- `rock-solid-sites/ASES/skills/` remains canonical for ASES methodology skills.
- `rock-solid-sites/rss-tools/mcp/` remains canonical for existing MCP connector records and current implementation pointers.
- Existing installed ChatGPT plugin releases and live tunnel/deployment settings remain untouched.
- `rock-solid-sites/ASES/plugins/ases-workflow/` remains the existing ASES Workflow release record.

Migration must preserve history or provenance, identifiers, ownership, secret boundaries and rollback paths. Do not remove old locations before the new end-to-end route passes.

## Status

This staging directory records design and migration requirements. It is not a deployed plugin, active MCP server, tested release, or authorization to modify production connectors.
