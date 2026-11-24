---
title: ASES Documentation Navigation and Authority Index
version: 1.0.12
program: ASES
layer: Methodology
document_type: Guide
status: Active
authority: Derived
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/ASES Task-Scoped Information and Handoff Method.md
related_documents:
  - docs/architecture/Task-Scoped Information Architecture Decision 2026-11-21.md
last_updated: 2026-11-24
---

# ASES documentation: current sources, history and status

**Use this page as a human navigation index, not as an instruction to load every document.** ASES tasks select information at the point of use, as defined by the [canonical Task-Scoped Information and Handoff Method](methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md). Source authority is established by current metadata, owner and decisions, **not** by a filename, repository location, discoverability, or a generated graph.

## Current governing sources

| Scope | Source | Governs |
| --- | --- | --- |
| Documentation metadata | [Documentation Standard](standards/Documentation%20Standard.md) and [Documentation Taxonomy](standards/Documentation%20Taxonomy.md) | Authority, classification, relationship metadata |
| General orchestration and reasoning | [AI Orchestration Guide](methodology/AI%20Orchestration%20Guide.md) | Evidence-based reasoning, role boundaries, review and validation principles |
| ASES coordination | [Task-Scoped Information and Handoff Method](methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) | Current source admission, effective task views, evidence/provenance |
| Architecture decision | [Accepted Task-Scoped Information ADR](architecture/Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md) | Agreed format-independent choices and non-goals |
| Execution requirements and architecture | [Methodology to Requirements Mapping](requirements/Methodology%20to%20Requirements%20Mapping%20Specification.md) and [Execution Engine Vision](architecture/Execution%20Engine%20Vision.md) | Current intended authority/continuity and higher-level responsibility boundaries; not deployment claims |
| Bounded builds | [ASES Bounded Project Build Method](methodology/ASES%20Bounded%20Project%20Build%20Method.md) | Applied only when an Implementation Packet is genuinely compiled |
| Implementation choice | [Realization and Assurance Selection Method](methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md) | Requirements-first selection, language constraints, bounded upstream-reuse exception |
| State modeling | [State-Model Applicability and Reuse Method](methodology/State-Model%20Applicability%20and%20Reuse%20Method.md) | Task-specific model suitability; verify separately adopted VSDD sources |
| Upstream customization | [Software Customization and Upstream Compatibility Method](methodology/Software%20Customization%20and%20Upstream%20Compatibility%20Method.md) | Preserve upstream compatibility, use the smallest supported local difference |
| Review methods | [AI Orchestration Guide: review modes and provenance](methodology/AI%20Orchestration%20Guide.md#review-modes-and-provenance) and [Clean Room Execution Guide](methodology/Clean%20Room%20Execution%20Guide.md) | Distinct exploratory and conformance modes; verified review provenance and isolation |
| Operational agent tasks | [Current skills index](../skills/current/README.md) | Selectively retrieved task-specific prompting, orchestration, launch and review instructions |
| Execution authorization | [Current agent-launch skill](../skills/current/agent-launch/SKILL.md) | Exact provider/model/account/funding route; no unauthorized fallback |
| Research evidence | [Agent information topology research](../research/agent-information-topology/greenfield-task-context/README.md) | Accepted decision's evidence; remains non-normative |

Other documents under `docs/methodology/`, `docs/standards/`, `docs/requirements/`, `docs/architecture/`, `docs/research/`, `research/` and other repository-owned paths are **not automatically retired or endorsed** by this shortlist. Inspect their own metadata and current owner before applying them.

## Full document inventory and reconciliation

- [Generated current-document index](CURRENT-DOCUMENTS-INDEX.md) lists every **declared-active/current** repository-owned Markdown/MDX document found by the read-only scanner, with observed authority, version and diagnostics.
- [Complete machine inventory](current-documents.json) records in-scope source paths, observed frontmatter, missing explicit versions, duplicate declared-active canonical identities and broken relative links. File metadata is **not automatically corrected**.
- [Inventory source and regression tests](../scripts/docs_audit/inventory.py) define the coverage; [GitHub Actions](../.github/workflows/docs-status-inventory.yml) publishes a fresh diagnostic artifact and summary after relevant changes.
- **Tracking:** Work Notes WNASES-9 owns the exhaustive metadata/version/collision audit and limited repairs. Projektor ASES-5 owns any *derived* documentation/relationship projection, not a new canonical store. Newly found material conflicts remain open until verified, not quietly downgraded by an index script.

An entry reading `Active` in a historical file is **not a certificate of current runtime correctness**. Unversioned, invalid-identity or cross-repository-mirrored documents must be explicitly reviewed; do not assign fabricated past versions or treat a generated source digest as approval.

**First explicit reviewed revisions:** The four ASES-owned methods for bounded builds, realization selection, state-model applicability and upstream customization have dated document revisions `2026-11-24.1`. These are newly declared versions of the reviewed documents, not reconstructed historical release numbers or new validation of every referenced research claim. The state-model method explicitly separates current applicability guidance from unresolved adoption of the historical derived VSDD artifacts.

**Core prompt consolidation:** The two earlier EDASES core prompt iterations are historical. Their still-useful reasoning principles are consolidated in the current AI Orchestration Guide. Neither historical prompt is an operational startup requirement.

**Skill consolidation:** Current operational skills retain the applicable prompt and review principles. The old skill variants, proposed ontology-review role variants and v0.1.0 pinned-copy packaging machinery are preserved in [Skill and Review Design History](historical/Skill%20and%20Review%20Design%20History.md), not active discovery. The old pinned-copy drift workflow was retired because the current dispatcher retrieves selected current sources at use time; actual automatic invocation remains unverified.

**Engine research navigation:** [Kernel-0 neutral requirements](research/kernel-0/Kernel-0-Evidence-Packet.md) constrain substrate research without freezing a realization. The [Engine Architecture and Experiment History](historical/Engine%20Architecture%20and%20Experiment%20History.md) separates earlier proposals and reviews from the current November prototype stacks and prepared test packets. Experimental reports are evidence, not adopted architecture.

**Capability evaluation and routing:** The EDASES [Evaluation Framework](research/frameworks/Evaluation%20Framework.md), [AI Evaluation Protocol](research/protocols/AI%20Evaluation%20Protocol.md) and [AI Capability Registry Specification](research/registry/AI%20Capability%20Registry%20Specification.md) address distinct questions: outcomes, evidence generation, and descriptive observations. These are locally retained EDASES-owned sources; upstream currency/version has not been verified and their bodies are preserved. The [Model Routing Matrix](research/registry/Model-Routing-Matrix.md) is an active derived capability-tracking register for tentative task matching. Its dated qualitative profiles synthesize cumulative observations, not definitive selection guarantees, current entitlement or dispatch authorization. The [historical Harness Capability Matrix](research/registry/Harness-Capability-Matrix.md) retains dated framework comparisons, not present deployment claims. Apply the current agent-launch and review-launch skills; verify present exact route, authorization and entitlement independently. The [Resource Solver reconciliation](research/Resource%20Solver%20Specification%20Reconciliation%202026-11-02.md) is experimental control-plane research, not an adopted gate or a second account registry. The eleven dated model-feedback records are historical local observations, with original bodies retained. [Capability Observation and Failure Attribution History](historical/Capability%20Observation%20and%20Failure%20Attribution%20History.md) maps their specific qualifications and November stream diagnostics; observed route failure is not proof of intrinsic model failure. The [Hookability Matrix](research/registry/Hookability-Matrix.md) is historical only, retaining the old intended intervention points and mechanism analysis; its former hook priorities and maintenance are not current requirements. The [Failure Matrix](research/registry/Failure-Matrix.md) remains an active derived failure-evidence register: its current interpretation maps cumulative observations and proposed failure cases to transferable prevention/detection semantics and existing governing sources, while retaining the original hook priorities as historical. It is not a current implementation backlog or runtime assurance claim. **Testing and assurance:** [Current authority, proposals and empirical evidence map](research/Testing%20and%20Assurance%20Source%20Map.md). Current governing methods remain distinct from the unadopted testing/debugging proposals and experimental testing laboratory; the pinned source map records ownership, overlap, demonstrated results and the pending independent promotion gate. No second active method or skill.

**Knowledge, provenance and terminology:** The [provenance-pivot synthesis](research/syntheses/Research%20Synthesis%20-%20Architectural%20Pivot.md) preserves the original reasoning, early research drafts, historical assumption-register iterations and fresh-session failure evidence, with links to the current conceptual and task-scoped decisions. [Canonical Terminology](standards/Canonical%20Terminology.md) and [Levels of Abstraction](standards/Concept%20-%20Levels%20of%20Abstraction.md) retain their conceptual role; neither prescribes storage or deployed enforcement. The [knowledge-index prototype](../scripts/knowledge_index/README.md) is merged experimental research only (ASES-19/WNASES-16 benchmark pending), distinct from the documentation inventory, chat archive and current source ownership.

**Capability/schema validation research:** The [existing research index](../research/capability-schema-validation/README.md) now distinguishes #498 proxy and loopback experiments, the single-model live Corpus 530 report, and preserved prospective next-wave scaffolding. The 71.0% description-token reduction is not equivalent to preserved task intent: strict expected-argument accuracy fell outside the five-point threshold even though harness-valid arguments remained within it. Frozen experimental files remain unchanged; no runtime adoption or model dispatch follows.

**Earlier research plans and proposals:** The [early research-topic and plan disposition](../future-research-topics/README.md) connects the Architecture Validation Plan hypotheses and early five-role setup designs to current research, existing owners and superseded implementation assumptions. The scratchpad is not the canonical topic registry or a task queue. Proposals remain subject to their own evidence and adoption decisions; preserve unresolved questions, do not revive outdated mechanisms. The July [session audit plan](research/session-audit-plan.md) is historical only, not permission to delete archived sessions or backups.

## Legacy and supersession

The old root `AGENTS.md` is now a **thin compatibility adapter** with active current links. Mandatory `SESSION-START.md`, `docs/SESSION-END.md`, and `docs/ORCHESTRATOR.md` have been retired as operational instructions. The dated `docs/methodology/Agent Model Launch Routes.md` is a deprecated redirect to the current launch skill.

These paths remain stable for inbound links, but do **not** authorize old Crosslink commands, IT3812/VPS routes, paid model substitutions or mandatory session rituals. The old repository-local OpenCode, Claude and Crosslink configuration bundle has been moved outside auto-discoverable root paths into the historical archive as a unit, not selectively stripped of permission controls for use. No default launcher is thereby authorized. See the [historical harness decision and evidence guide](historical/Harness%20Setup%20and%20Permission%20Design%20History.md) for why it was built, source snapshots, rejected approaches and unresolved questions. Current execution uses explicitly verified task-specific routes. Historical text is preserved at pinned Git revisions in each redirect. Runtime auto-loading of any file is separately measurable; neither this index nor the architecture decision asserts it has been tested.

## Ownership of decisions and state

GitHub retains the canonical technical source, versioned decisions and reproductions; Work Notes retains agent work packets/verified positions; Projektor retains human decisions and planning. A derived index can help discover relationships without becoming a fourth authoritative system or copying private material into public ASES.
