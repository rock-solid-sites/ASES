---
date: 2026-11-03
status: prospective before implementation
type: ASES local experimentation preregistration
scope: cgrmcp version-scoped migration, compatibility guard and cost/retention optimization controls
authority: research; no production merge/deployment
---
# cgrmcp versioned store and migration — pretest hypotheses

The earlier CodeGraph 1.6.0 indexed Go fzf graph lost 14 type-to-method `contains` relationships that were present in two independent fresh builds. Version-isolated 1.6.2 on the same source did not reproduce that loss. In the code review, **existing cgrmcp manifest lookup and `repo_open` cache short-circuit recognize repository + commit, not the index engine**. An in-place package upgrade can therefore serve an older `ready` graph with an incompatible newer engine.

This round tests safe isolation and honest retrieval, not yet claims that v1.6.2 is universally correct.

## Hypotheses, alternatives and discriminating controls

| ID | Hypothesis | Cheapest falsifier |
| --- | --- | --- |
| V1 | New version-scoped store roots separate registries, immutable snapshots, mirrors, locks and tmp without rewriting legacy data | Same URL/commit under two engine-version scopes gives independent registries; legacy directory tree and DB hash unchanged; no inherited ready lookup |
| V2 | Explicitly checking ready snapshot engine identity prevents stale graph reads even in a mistakenly shared legacy root | Manually inject ready manifest for 1.6.0 into a 1.6.2 SnapshotManager; `repo_open` and `resolveSnapshot` refuse it, `repo_status` remains factual and no writes/renames occur |
| V3 | A `CGRMCP_VERSIONED_STORE=1` opt-in can be pure, deterministic and fail-closed on unknown/malformed versions and symlinked paths | Invalid version refuses startup before `initStore`; benign normal version produces only an isolated child path, legacy path untouched |
| V4 | A fresh version-scoped 1.6.2 store indexes and serves repo MCP calls correctly; restored fresh stores continue after restart | Two-commit smoke + version scope + restart, independent graph and source oracle, old legacy path untouched |
| V5 | Index reuse is not always cheapest and often increases retained DB pages; dedup solves different bytes than compute | Compare `full init` vs `sync+backup` and source hardlink dedup (if safe) with actual allocated bytes, time, changed-file ratio and disk peak; never infer a universal speedup from 3 small real projects |
| V6 | Exact executing binary/package identity matters; configuration may lie about actual executable | Mismatched explicit version/engine version denied or verified at startup; test custom executable rejected for unsafe reuse |
| V7 | A promoted versioned store cannot accidentally inherit old manifest and cache evidence | Clean room + adversarial pre-populated mismatched manifest; network-independent synthetic fixtures and local restart assert no cross-version reuse |

## Implementation choices frozen

- **No migration by copying old SQLite indexes across CodeGraph versions.** Use an empty, opt-in, version-qualified store; keep old store intact for rollback and read-only verification.
- Use conservative `snapshot_not_ready` error for an incompatible ready index, with `details.reason=engine_mismatch`; never rewrite a ready manifest or misreport it as new-engine ready. An explicit `repo_open` cached lookup must also reject it. `repo_status` may still truthfully describe old metadata.
- Prefix/suffix versioned stores without route collision, e.g. `<configured base>/engine-scopes/codegraph-v1.6.2`. Validate strictly bounded version strings and prevent symlinked scope path components. Do not expose absolute paths in tool errors.
- Production remains on its current package/store; test and document development-only 1.6.2 as a separate exact dependency/lock step if feasible. Do not rely on a `package.json` string for an explicitly overridden executable.
- The red Go 1.6.0 graph test is preserved as negative evidence; 1.6.2 is a separate scope. The existing ASES testing/debugging ontology is applied locally, not adopted as a general Processor contract.

## Stop conditions

No branch merge if a stale `ready` graph can be queried with incompatible engine, if old store files change during scoped startup, if migration leaves an accessible partial-ready manifest, if version identity cannot be attested, if new scope can be accessed through an unverified symlink, or if the E2E test crosses store boundaries inadvertently. Preserve failed CI runs and exact command/version/commit inputs, classify fixture errors separately. GitHub artifact retention is not an independent archive (`ARCHIVE_NOT_VERIFIED`).
