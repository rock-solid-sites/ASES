# ASES Skills

Operational skills are stored one skill per directory:

```text
skills/
  <skill-name>/
    SKILL.md
```

`SKILL.md` is the model-facing operational procedure. Stable project meaning and methodology remain in canonical documentation and are referenced by path rather than duplicated into skills.

Current skills:

- `prompt/SKILL.md` — compile compact, high-signal prompts and context selections.
- `atproto-reader/SKILL.md` — retrieve readable public ATProto/Bluesky records through the Thread Reader Worker.
- `compile-build/SKILL.md` — compile bounded software work into a frozen Implementation Packet and residual build prompt.
- `cgrmcp/SKILL.md` — historical pointer; current public GitHub CodeGraph research uses the [GitHub Actions + B2 Skill](https://github.com/rock-solid-sites/ases-plugins/blob/main/skills/codegraph-actions-repository-research/SKILL.md) installed through the ChatGPT plugin. The old cgrmcp MCP is preserved for explicit legacy diagnostics only.

Skill-related design notes, derivations, evaluations and evidence belong under `docs/research/`, not in `skills/`.

Legacy Claude-era skill/style material is archived under `docs/historical/skills/` and is not active procedure.

Add a new skill only when repeated use demonstrates a stable operational procedure distinct from canonical methodology or project knowledge.

## Restored Library skills

- [Workflow Orchestration](workflow-orchestration/SKILL.md) — provisional coordination skill.
- [Custom MCP Connector](custom-mcp-connector/SKILL.md) — connector setup and troubleshooting skill.
- [Compact Prompt](compact-prompt/SKILL.md) — distinct Library variant retained alongside the existing `skills/prompt/SKILL.md`.
- [Ontology Reviewer](ontology-reviewer/Ontology-Reviewer-Role.md) — role, proposal, review-skill connection, and dated-as-older archived drafts.

The archived drafts are preserved as history; they are not promoted as the current role definition.
