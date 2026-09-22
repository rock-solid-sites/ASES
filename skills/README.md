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

Skill-related design notes, derivations, evaluations and evidence belong under `docs/research/`, not in `skills/`.

Legacy Claude-era skill/style material is archived under `docs/historical/skills/` and is not active procedure.

Add a new skill only when repeated use demonstrates a stable operational procedure distinct from canonical methodology or project knowledge.