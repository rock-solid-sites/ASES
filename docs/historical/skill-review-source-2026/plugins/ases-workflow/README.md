# ASES Workflow plugin (source)

Canonical skills live at `skills/prompt/SKILL.md`, `skills/compile-build/SKILL.md`, `skills/workflow-orchestration/SKILL.md`, and `skills/custom-mcp-connector/SKILL.md` in this repository.

## Dispatch contract

When asked to prepare a builder, reviewer, recon or orchestrator prompt, use `prompt` unconditionally. Consult `workflow-orchestration` when the next work mode is uncertain; consult `compile-build` for substantial bounded implementations that benefit from a frozen Implementation Packet. Use `custom-mcp-connector` only for MCP setup/debugging. Avoid imposing compilation on trivial changes.

## Release and update contract

The repository is authoritative; plugin bundles are immutable, pinned snapshots, not live imports. At packaging time record source commit SHA, file paths, SHA-256 content hashes and plugin release version. On startup or use, a supported connector may compare these values against GitHub; otherwise use a scheduled GitHub Action. A detected mismatch reports **update available**, not an automatic replacement. Review changes, build a new release, run skill-discovery and behavioral tests in a fresh ChatGPT conversation, then activate. Preserve rollback information and do not mutate an in-flight session.

## Acceptance tests

1. Natural-language request for a trivial builder prompt invokes prompt construction without unnecessary planning.
2. A substantial bounded build uses compile-build when appropriate and emits an Implementation Packet and compact residual prompt.
3. A request with unresolved constraints routes to reconnaissance or strategy rather than fabricating settled requirements.
4. A custom MCP failure invokes the staged fault rubric, canary and evidence record.
5. Confirm skill visibility and actual selection in a fresh chat; successful plugin creation alone is insufficient.

No persistent service or automatic updater is implemented by this README.
## First private release

Version 0.1.0: https://chatgpt.com/plugins/plugins_6ae44a4ff8f081919325009658a40cae

Sources are pinned in `sources.json`. Weekly checks run through `.github/workflows/ases-workflow-skill-drift.yml`. Checks only report differences; release updates remain explicit. Skill invocation must be verified in a fresh chat.
