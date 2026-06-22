# ASES

EDASES (Evidence-Driven Agentic Software Engineering System) research, charters, and methodology documentation.

A research archive and organizational memory system supporting evidence-driven, agent-assisted project execution.

## Knowledge Flow

The repository is designed to support the following traceability chain:

```text
Source
    ↓
Observation
    ↓
Finding
    ↓
Assumption
    ↓
Decision
    ↓
Outcome
```

This chain enables:
- Evidence lineage from source materials through to decisions and outcomes
- Reasoning traceability at every stage of the research process
- Organizational memory that persists across sessions and agents
- Future research synthesis grounded in documented evidence
- Agent-assisted retrieval of contextually relevant knowledge

## Repository layout

Each document type lives in its own folder. Folder name = document type.

```
ASES/
├── README.md
├── sources/                                  # External materials used during research
│   ├── papers/                               # Research papers and published studies
│   ├── repositories/                         # Repository reviews and codebase analyses
│   ├── methodologies/                        # Methodology analyses and process documents
│   ├── communities/                          # Community discussions and collaborative inputs
│   └── historical-projects/                  # References to prior projects and legacy work
├── observations/                             # Atomic observations extracted from sources
├── findings/                                 # Conclusions derived from observations
├── syntheses/                                # Higher-level integration across findings
├── evaluation-corpus/                        # Artifacts for evaluating methodologies and architectures
├── adversarial-reviews/                      # Critical evaluations and stress tests of the methodology
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

### New Directories (Knowledge Traceability)

These directories were added to extend the repository's support for evidence-driven research:

- **`sources/`** — Catalogs external materials (papers, repositories, methodologies, communities, historical projects) used as evidential foundations
- **`observations/`** — Stores atomic, evidence-linked observations extracted from sources, avoiding interpretation where possible
- **`findings/`** — Stores conclusions derived from one or more observations, representing interpreted results
- **`syntheses/`** — Stores higher-level integration across multiple findings and sources (reviews, comparisons, analyses)
- **`evaluation-corpus/`** — Stores artifacts used to evaluate candidate methodologies, architectures, and processes (research infrastructure)

## Filename conventions

- The folder name carries the document type, so filenames inside a folder generally keep only the version, variant, or distinguishing descriptor (e.g. `Charter v1.md`, `Operational Testbed Charter v1.md`).
- Versions use the format `v1`, `v2`, etc. The project does **not** use the `v0.1` convention; the earliest charter is `v1`.
- Bundle-internal files (in `handoff-bundle/`) use lowercase-kebab-case filenames, no numeric prefix.

## Notes

- **`specifications/Hospitality Management Suite Specification.md`** also lives in `projects/HMS/`. The ASES copy is a reference — it belongs in the EDASES research repo because the Hospitality Management Suite is the operational testbed for EDASES. The `projects/HMS/` copy is the active project document. Both are intentional; do not delete either.
