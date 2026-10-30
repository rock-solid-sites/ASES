# Bounded builder handoff — dedicated ASES plugin monorepo

**Status:** M1 migration preparation packet; name and scope agreed, source audit still incomplete. Builder: VPS agent using authenticated `rock-solid-sites` GitHub CLI. This is a bounded repo-creation/migration task, not permission to redesign the ASES methodology or deploy production changes.

## Objective

Create `rock-solid-sites/ases-plugins` with the four staged documents at repository root, import verified in-scope existing plugin/connector sources and records without disrupting working installations, and establish reproducible builds, manifests and end-to-end acceptance fixtures.

## Required initial inputs

- Source audit: `rock-solid-sites/ASES/staging/ases-plugins/SOURCE-AUDIT-2026-10-30.md`
- This staging directory: `rock-solid-sites/ASES/staging/ases-plugins/`
- Existing source inventory: `rock-solid-sites/rss-tools/mcp/REGISTRY.md`, `rss-tools/mcp/`, `rss-tools/atproto-thread-reader/`
- ASES Workflow release source: `rock-solid-sites/ASES/plugins/ases-workflow/` and `ASES/skills/`
- Crosslink MCP pending design: `rock-solid-sites/rss-tools` branch `draft/crosslink-mcp-gates-20261029`
- Installed plugin metadata and available current client tests; do not infer installed status from source alone.

## Requirements and exclusions

- Preserve existing deployments, tunnels, plugin IDs, identities, secrets and credentials locations. Never commit credentials or overwrite a live endpoint.
- Keep canonical ASES methodology skills in ASES; plugin bundles are pinned copies with source provenance.
- Distinguish actual executable source from connector records, skill text, deployed Worker code and plugin package metadata.
- Preserve provenance and migration trace for every imported component.
- No migration of unrelated `rss-tools` general-purpose agent infrastructure without explicit scope decision.
- No automatic silent plugin upgrade; release changes are versioned, reviewed and reversible.
- No success claim from installation, file availability, discovery alone or CLI-only tests. Exact-client end-to-end behavior is mandatory.
- Avoid unnecessary framework or architectural choices; use requirement-first exclusion and evidence before choosing realization.
- Commit frequently; push branch at session end; document any blocked capability rather than silently substituting a different account or route.

## Work units and acceptance

**A. Audit:** inspect actual files, refs, package metadata, deployed/installed IDs and existing tests. Produce machine-readable inventory with status, canonical owner, source SHA, license, security boundary, evidence and gaps. Do not invent missing source.

**B. Create and scaffold:** create the repository under the authenticated `rock-solid-sites` identity; copy these four staged root docs; add minimal project structure and source references. Verify repo read/write and branch push.

**C. Import:** move or import verified sources and connector records with history/provenance; preserve old repositories and pointer links. Keep retired Strategy Code Graph retired and pending Crosslink MCP pending.

**D. Verification:** implement reproducible package parity and version-drift checks and preserve existing runtime evidence; add initially red client acceptance fixtures for future runtime work. Do not require repairing pre-existing invocation failures to accept M1 migration. Test only safe read-only canaries initially. Tests blocked by missing client access remain BLOCKED.

**E. Report:** list exact repo URL, commits, imported paths, unchanged live deployments, test evidence, failures, unverified assumptions and minimal residual actions. Do not claim cutover until independently demonstrated.

## Immediate stop/escalation conditions

Stop and report if authenticated repo creation fails, required source is unavailable, the existing production configuration would be altered, credentials would need copying, canonical authority conflicts, or a client acceptance gate cannot be observed. Resolve only bounded technical defects locally; return strategic scope changes for decision.

## Remaining pre-execution decisions

Destination name and scope are settled: `rock-solid-sites/ases-plugins`; ChatGPT plugins, packaged compatible skills, custom MCP connectors, source, release tooling and tests. Exclude general Crosslink/OpenCode utilities and preserve canonical ASES methodology in ASES. Audit unresolved source/provenance before declaring M1 complete. Other decisions should be resolved by inspection or cheapest discriminating tests, not additional operator questionnaires.
