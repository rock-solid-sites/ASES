<!-- Project-Specific Rules -->
<!-- Add rules specific to your project here. Examples: -->
<!-- - Don't modify the /v1/ API endpoints without approval -->
<!-- - Always update CHANGELOG.md when adding features -->
<!-- - Database migrations must be backward-compatible -->
\n- **Agent Behavior:** See `AGENTS.md` for rules regarding clean-room agent sessions and fallback behaviors. Never silently substitute an agent if a subagent tool fails.
\n- **Abstraction Boundaries:** This repository has three layers — EDASES (research), ASES (methodology), Execution Engine (implementation). Do not introduce implementation concepts into research documents or methodology documents. See `AGENTS.md` and `ARCHITECTURE.md`.
\n- **Research Programme:** The execution-engine UI research programme is complete. Read `research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md` before making implementation decisions. Open items are Crosslink issues #14–#21.
\n- **Canonical Documents:** When conflicts arise, prefer canonical documents (those with `authority: Canonical` in frontmatter) over derived documentation. See `ORIENTATION.md` for the full list.
