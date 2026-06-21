# ASES

EDASES (Evidence-Driven Agentic Software Engineering System) research, charters, and methodology documentation.

## Repository layout

Each document type lives in its own folder. Folder name = document type.

```
ASES/
├── README.md
├── charters/                                 # Project charters (5)
├── assumption-registers/                     # Standing register of architectural assumptions (4)
├── assumption-to-decision-registers/         # Assumptions → decisions → outcomes traceability (1)
├── core-system-prompts/                      # Core system prompt iterations for EDASES agents (2)
├── knowledge-architecture-research/          # Phase-1 research drafts + reviewer responses (6)
├── research-programs/                        # Research program versions + the current operational one (4)
├── architecture-validation-plans/            # Plans for validating architectural assumptions (1)
├── specifications/                           # Specifications for systems used in / by EDASES (1)
├── research-addenda/                         # Research addenda (1)
├── research-handoffs/                        # Research-phase handoffs (1)
├── session-handoffs/                         # Session-level handoffs (1)
└── handoff-bundle/                           # Session handoff bundle: position, timeline, decisions, notes (5)
```

## Filename conventions

- The folder name carries the document type, so filenames inside a folder generally keep only the version, variant, or distinguishing descriptor (e.g. `Charter v1.md`, `Operational Testbed Charter v1.md`).
- Versions use the format `v1`, `v2`, etc. The project does **not** use the `v0.1` convention; the earliest charter is `v1`.
- Bundle-internal files (in `handoff-bundle/`) use lowercase-kebab-case filenames, no numeric prefix.

## Notes

- **`specifications/Hospitality Management Suite Specification.md`** also lives in `projects/HMS/`. The ASES copy is a reference — it belongs in the EDASES research repo because the Hospitality Management Suite is the operational testbed for EDASES. The `projects/HMS/` copy is the active project document. Both are intentional; do not delete either.
