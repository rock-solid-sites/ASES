# Acceptance contract — independent gates

**Rule:** A passing migration is not evidence of a working skill, and a working MCP is not evidence that editable source has been preserved. Each claim is independently testable. Record PASS, FAIL, BLOCKED or NOT TESTED with timestamp and evidence; never coerce BLOCKED to PASS.

## M1 — repository and provenance migration

- New private repository exists under the agreed identity, root documents present, read/write/branch push verified.
- For each imported component: source repository, exact commit and path, license if known, destination, content hash, canonical owner and migration method recorded. Unknowns explicitly BLOCKED.
- Plugin package build can be reproduced from checked-in inputs plus pinned external sources. Artifact manifest and release identity parity checked without exposing credentials.
- Shared tests and static checks run; existing source references/redirect docs preserved. No live connection, Worker, tunnel or plugin release changed.
- Migration may PASS with specific components explicitly excluded or BLOCKED, but never claim those components migrated. Full-scope M1 acceptance requires every in-scope asset accounted for and either imported or explicitly deferred by approved manifest.

## M2 — plugin runtime and functional improvements (separate releases)

**ASES Workflow:** fresh conversation, plugin installed/eligible, original failure prompt plus paraphrases and negative controls; record whether workflow was selected and applied. A manually loaded skill is not a pass for automatic invocation.

**cgrmcp-current:** preserve active App ID and .app.json; validate current read-only MCP four-tool behavior when a runtime change is proposed. Fresh-chat visibility and invocation of newly packaged repository-research skill is separate from MCP health.

**ATProto Reader:** preserve active direct App and deployed Worker; source reconciliation and security tests before any deployment. New skill packaging must pass fresh-chat discovery/invocation separately from `read_atproto` tool calls.

**Crosslink/Paseo:** retain intentionally red gates and PENDING state; do not claim deployed.

## Required evidence schema

Each test observation records: `test_id`, `milestone`, `component`, `claim`, `client_or_runner`, `release_or_commit`, `timestamp`, `expected`, `observed`, `status`, `evidence_reference`, `limitations`. Avoid invented telemetry or assertions about hidden platform selection.

## Release and security invariants

- Do not silently change a connected App, deployment endpoint, tunnel, bearer handling or canonical skill source.
- No credentials, private conversation exports, runtime-key files or sensitive request logs in Git.
- Runtime security is mechanically enforced at the server/transport boundary, not by skill instructions.
- Any externally controlled client transition with no test access is BLOCKED, not waived.
- Rollback points and version identities recorded before an authorized runtime change.
