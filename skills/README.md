# ASES Skills

**Active ChatGPT dispatcher source: [`skills/current/`](current/README.md).** The installed ASES Workflow plugin uses a **read-only HTTPS GET** of the current index, then retrieves only the task-relevant `SKILL.md` from its published read-only URL. Do not invoke an authenticated, write-capable GitHub connector merely to read instructions. Follow the [current index's retrieval and revision guidance](current/README.md); this navigation page does not define separate operational policy. The installed dispatcher is not a live GitHub mount and does not automatically repackage itself.

The former skill entrypoints listed below are retained for historical provenance and existing repository references. They are **not** the active dispatcher source; do not package their outdated copies into ChatGPT. Prior versions remain in Git history, while published current instructions are under `skills/current/`.


Operational skills are stored one skill per directory:

```text
skills/
  <skill-name>/
    SKILL.md
```

`SKILL.md` is the model-facing operational procedure. Stable project meaning and methodology remain in canonical documentation and are referenced by path rather than duplicated into skills.

Older source paths (not the current ChatGPT dispatcher):

- `prompt/SKILL.md` — compile compact, high-signal prompts and context selections.
- `atproto-reader/SKILL.md` — retrieve readable public ATProto/Bluesky records through the Thread Reader Worker.
- `compile-build/SKILL.md` — compile bounded software work into a frozen Implementation Packet and residual build prompt.


For public GitHub source exploration, the sole active CodeGraph Skill is [codegraph-actions-repository-research](https://github.com/rock-solid-sites/ases-plugins/blob/main/skills/codegraph-actions-repository-research/SKILL.md), installed through the ChatGPT plugin. The former `cgrmcp` active Skill/pointer was removed; its recoverable source is historical, not model-facing instructions.

**Skill retirement rule:** remove superseded `SKILL.md` files from active Skill directories and packaged releases. Do not leave redirects with obsolete names or duplicate procedures. Preserve technical history under docs/release manifests/Git history rather than in discoverable Skill locations.

Skill-related design notes, derivations, evaluations and evidence belong under `docs/research/`, not in `skills/`.

Legacy Claude-era skill/style material is archived under `docs/historical/skills/` and is not active procedure.

Add a new skill only when repeated use demonstrates a stable operational procedure distinct from canonical methodology or project knowledge.

## Restored Library skills

- [Workflow Orchestration](workflow-orchestration/SKILL.md) — provisional coordination skill.
- [Custom MCP Connector](custom-mcp-connector/SKILL.md) — connector setup and troubleshooting skill.
- [Compact Prompt](compact-prompt/SKILL.md) — distinct Library variant retained alongside the existing `skills/prompt/SKILL.md`.
- [Ontology Reviewer](ontology-reviewer/Ontology-Reviewer-Role.md) — role, proposal, review-skill connection, and dated-as-older archived drafts.

The archived drafts are preserved as history; they are not promoted as the current role definition.
