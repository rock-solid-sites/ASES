---
title: "EDASES Phase 4 Retrospective"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - docs/standards/Documentation Standard.md
  - docs/standards/Canonical Terminology.md
  - docs/standards/Documentation Taxonomy.md
  - ORIENTATION.md
  - ARCHITECTURE.md

consumed_by:
  - EDASES Phase 5 Retrospective

supersedes:
  - EDASES Phase 3 Retrospective

superseded_by:
  - EDASES Phase 5 Retrospective

last_updated: 2026-08-10
---

# EDASES phase 4

## Retrospective

### 1. Purpose of This Phase

This phase focused on consolidating the project's conceptual model and restructuring its documentation so that the repository accurately represented what EDASES, ASES and the eventual tooling are intended to be.

The phase began from the results of several parallel conversations in which multiple AI agents had independently examined the project and attempted to break a conceptual deadlock. Those conversations were conducted in parallel deliberately: there was no meaningful "earlier" or "later" conversation, and the agents were not intended to influence one another.

The central outcome was a clearer separation between:

* **EDASES** — the research programme.
* **ASES** — the methodology that the research programme is developing.
* **Tooling / Execution Engine** — software that implements and mechanically enforces the methodology.

The distinction became important enough that the project documentation and repository structure needed to be reorganised around it.

---

# 2. EDASES and ASES Were Established as Different Things

A major conclusion was that EDASES and ASES should no longer be treated as interchangeable names for the same project.

EDASES is the **research programme itself**.

ASES is the **methodology produced by that research**.

This was compared to the relationship between a research programme and a methodology such as Agile: a methodology should not inherently depend upon a particular technology or product.

ASES therefore should be capable of being applied using different:

* AI models
* AI providers
* orchestration systems
* development tools
* implementation strategies

Whether ASES eventually becomes associated with a particular GUI or software product is an implementation question, not a property of the methodology.

The name "Agentic Software Engineering System" was recognised as potentially sounding like a product rather than a methodology, but changing the name was deliberately deferred because it was not important to the immediate research and documentation work.

---

# 3. The Three-Layer Project Model

The project was subsequently understood as having three interdependent layers:

```text
EDASES
Research Programme
        ↓
ASES
Methodology
        ↓
Tooling / Execution Engine
Implementation
```

Each layer has a different responsibility.

### EDASES

Investigates what works.

Its outputs include research findings, conceptual models, evaluations and validated methodological ideas.

### ASES

Defines how agentic software engineering should be conducted.

It translates research findings into a methodology that is independent of particular implementation technologies.

### Tooling

Mechanically executes and enforces the methodology.

This includes the eventual execution engine and potentially the intermediate tooling required to make the methodology practical.

This distinction also clarified why the research products were naturally separating from the software implementation.

---

# 4. The Object of Interest Is Reasoning

An important conceptual shift from the earlier project model was that the object of interest is **reasoning rather than commits**.

Commits, files and other software artefacts are outputs of engineering reasoning.

The project therefore needs to preserve and reason about the knowledge that produces those artefacts, rather than treating the software history itself as the primary object.

This led to greater emphasis on:

* reasoning
* evidence
* assumptions
* decisions
* findings
* validation
* epistemic relationships

The project's knowledge architecture consequently became more important than simply tracking changes to source code.

---

# 5. Epistemic Relationships

The conversations identified **epistemic relationships** as a central concern.

The important question is not merely what pieces of information exist, but how they relate to one another.

Examples include relationships such as:

```text
Observation → Finding
Finding → Assumption
Evidence → Decision
Challenge → Finding
Validation → Promotion
```

These relationships provide the structure through which engineering reasoning can remain traceable.

This became one of the foundations for the emerging methodology.

---

# 6. Levels of Abstraction

Another major finding was that **levels of abstraction are the actual structure of the EDASES project**.

Questions can become effectively unanswerable when they are approached at the wrong level.

The project therefore developed an explicit abstraction progression:

```text
Research
    ↓
Methodology
    ↓
Requirements
    ↓
Architecture
    ↓
Implementation
```

The separation is not merely organisational.

Each level answers a different kind of question and should avoid importing assumptions from lower levels.

This led to the creation of:

**Concept: Levels of Abstraction**

This became one of the foundational documents of the revised documentation architecture.

---

# 7. Mechanization Became the Next Research Area

The discussions concluded that merely instructing humans and AI agents to follow a methodology is insufficient.

A methodology that depends upon continuous manual compliance is vulnerable to:

* human error
* AI error
* inconsistency
* forgotten procedures
* unnecessary cognitive overhead

The next major research and experimentation area therefore became **how to mechanize the methodology**.

This led to the idea of an **execution engine**: a system capable of enforcing methodological requirements mechanically rather than relying exclusively on instructions.

The engine should ultimately help:

* maintain engineering state
* preserve reasoning
* coordinate heterogeneous AI capabilities
* reduce human and AI error
* minimize token costs
* increase output speed
* provide verifiable safety and effectiveness at each step

The project question was consequently framed in practical software-engineering terms:

> How can we design a system that allows a non-programmer to use AI agents to design software that is verifiably safe and effective at every step, makes use of the large variety of models and tools available today, reduces token costs to a minimum, increases output speed, and mechanically reduces the possibility of human and AI error?

This replaced a more abstract framing that risked making the project appear applicable to arbitrary domains.

The project remains fundamentally about **software engineering**. Generalisation to other domains may eventually be possible, but it is not the present research objective.

---

# 8. Model Capability Became an Explicit Concern

The project also identified the need to document where different AI models excel and where they struggle.

The execution system should not assume that all models are interchangeable.

Instead, the system should be able to make use of a heterogeneous model ecosystem by matching capabilities to tasks.

This motivated the creation of the:

**AI Capability Registry**

The registry is intended to preserve evidence-based knowledge about the capabilities and limitations of models and tools.

This became part of the broader goal of using the available variety of AI systems rather than designing the methodology around a single model.

---

# 9. Evaluation Became a Critical Open Question

A significant unresolved question emerged during the discussions:

> How do we determine that the methodology produces a desired result rather than simply reproducing itself through excessive documentation and ritual?

This was recognised as a fundamental concern.

A methodology can appear rigorous while actually producing:

* unnecessary documentation
* procedural overhead
* ritual compliance
* additional tokens and latency
* no meaningful improvement in software quality or safety

The project therefore needs evaluation criteria tied to its actual objectives.

The practical objectives identified were:

* safety
* effectiveness
* model/tool utilization
* token efficiency
* execution speed
* mechanical reduction of human error
* mechanical reduction of AI error

This motivated the creation and refinement of:

* **Evaluation Framework**
* **AI Evaluation Protocol**
* **AI Capability Registry**

The exact empirical criteria and validation mechanisms remain an area for continued research.

---

# 10. The Documentation Architecture Was Rebuilt

The conceptual changes required substantial documentation restructuring.

A distinction was made between:

* documents that define foundational concepts
* repository-level orientation documents
* methodology documents
* tooling documents
* review documents
* operational documents

The goal was to prevent the repository from accumulating multiple competing descriptions of the same idea.

The project adopted the principle that canonical documents should define authoritative knowledge, while derived documents should reference rather than redefine that knowledge.

---

# 11. Foundational Documents Created

The following canonical documents were identified and created during this phase:

1. **Documentation Standard**
2. **Concept: Levels of Abstraction**
3. **Evaluation Framework**
4. **AI Evaluation Protocol**
5. **AI Capability Registry**
6. **AI Orchestration Guide**
7. **Methodology to Requirements Mapping Specification**
8. **Execution Engine Vision**
9. **Canonical Terminology**
10. **Documentation Taxonomy**
11. **EDASES Review Methodology**
12. **Repository Review Checklist**

The documents were deliberately given different roles rather than being treated as one large specification.

---

# 12. Documentation Standard

A documentation standard was created to define how canonical documents are structured and identified.

The metadata established during this process included concepts such as:

* title
* program
* layer
* document type
* status
* authority
* canonical repository
* dependencies
* consumers
* related documents
* superseded documents
* last updated

The project explicitly removed `review_frequency` and changed `last_reviewed` to `last_updated`.

The purpose was to make documentation housekeeping easier before the project potentially separates into multiple repositories.

---

# 13. Canonical Terminology

A **Canonical Terminology** document was added after it became clear that the project was developing a substantial vocabulary that would be difficult for subagents to apply consistently without an authoritative reference.

It defines terms including:

* EDASES
* ASES
* Execution Engine
* Research
* Methodology
* Requirement
* Architecture
* Implementation
* Observation
* Finding
* Assumption
* Decision
* Challenge
* Validation
* Evidence
* Epistemic Relationship
* Capability
* Orchestration
* State
* Promotion
* Traceability
* Abstraction Layer
* Canonical Document
* Derived Document

The purpose is to reduce terminology drift across agents and documentation.

---

# 14. Documentation Taxonomy

A further gap was identified between knowing **how to write a document** and knowing **what kind of document should exist**.

This resulted in the creation of **Documentation Taxonomy**.

The Documentation Standard answers:

> How should an individual document be written?

The Documentation Taxonomy answers:

> What kinds of documents exist, and where do they belong?

The taxonomy distinguishes categories including:

* top-level repository documents
* canonical documents
* methodology documents
* requirements documents
* architecture documents
* reference documents
* standards
* guides
* checklists
* experimental documents
* research records
* syntheses
* historical documents

This was intended to reduce documentation duplication and inappropriate creation of new document types.

---

# 15. README, ORIENTATION and AGENTS

The three principal top-level repository documents were redesigned to have distinct responsibilities.

## README.md

The README became the external project introduction.

It answers:

> What is this project?

It explains EDASES, ASES and the tooling relationship without attempting to reproduce the full methodology.

## ORIENTATION.md

A top-level `ORIENTATION.md` was established beside `README.md` and `AGENTS.md`.

Its purpose is to orient contributors and agents within the repository.

It answers:

> How is this project organised, and where should I begin?

## AGENTS.md

`AGENTS.md` was substantially rewritten.

The original document was heavily focused on:

* clean-room agent execution
* specific tooling workarounds
* native API fallbacks
* adversarial consensus

The revised document instead focuses on general agent operating rules:

* respect abstraction boundaries
* use canonical documents as authority
* preserve reasoning
* distinguish evidence from interpretation
* preserve independent reasoning where required
* handle tool failures explicitly
* avoid silently redefining project concepts

The specific native API clean-room procedure was removed from `AGENTS.md` because it was considered too implementation-specific.

---

# 16. ARCHITECTURE.md

A new top-level `ARCHITECTURE.md` was created.

It describes the architecture of the **project**, rather than the architecture of the eventual execution engine.

Its purpose is to explain why the repository is structured around:

```text
Research
    ↓
Methodology
    ↓
Requirements
    ↓
Architecture
    ↓
Implementation
```

It also documents the possibility that EDASES, ASES and implementation tooling may eventually be separated into different repositories.

This reinforced an important distinction:

* `ORIENTATION.md` explains how to navigate the project.
* `ARCHITECTURE.md` explains why it is structured that way.
* `AGENTS.md` explains how AI contributors should operate within it.

---

# 17. Review Methodology

The need for structured repository review was reconsidered during the phase.

Initially, two documents were proposed:

* Repository Review Guide
* Repository Review Checklist

The distinction was clarified.

The guide should not merely be a repository-specific manual. It should become a reusable research methodology.

It was therefore renamed:

**EDASES Review Methodology**

Its purpose is to define how EDASES artefacts and repositories are reviewed.

The methodology includes:

1. Orientation
2. Independent Analysis
3. Finding Generation
4. Synthesis
5. Human Decision

It explicitly establishes that:

> Consensus is evidence, not authority.

The associated **Repository Review Checklist** operationalizes the methodology for repository review.

The checklist covers:

* orientation
* canonical documentation
* abstraction
* consistency
* traceability
* architecture
* methodology
* recommendations
* final review

The distinction is:

* the review methodology defines how to reason about a review;
* the checklist ensures the operational review process does not omit important areas.

---

# 18. Clean Room Execution Was Reclassified

The final part of the phase exposed another important architectural distinction.

The **Clean Room Execution Guide** was initially written as a methodology-adjacent guide.

On further examination, this was considered the wrong abstraction.

The underlying principle belongs to methodology:

> Certain forms of evaluation require independent reasoning.

But the mechanism by which independent reasoning is achieved belongs to tooling.

The distinction became:

```text
EDASES
    Researches whether clean-room execution is useful

        ↓

ASES
    Defines when and why independent reasoning is required

        ↓

Tooling
    Implements clean-room execution for a particular environment
```

This means the Clean Room Execution Guide should ultimately be treated as **tooling documentation or executable tooling knowledge**, rather than as a canonical ASES methodology document.

---

# 19. Skills vs Tooling Documentation

The discussion then examined whether clean-room execution should be represented as a **skill**, particularly given the current use of OpenCode with an OpenCode Go subscription.

The important distinction was made between documentation and executable knowledge.

A human-readable guide explains how a capability works.

A skill can encode how an AI agent should actually perform that capability.

The emerging tooling structure was therefore:

```text
Tooling
├── Documentation
├── Skills
├── Templates
├── Scripts
└── Configuration
```

This reflects different forms of implementation:

* **Documentation** explains tooling.
* **Skills** operationalize methodology for an agent environment.
* **Templates** standardize inputs and outputs.
* **Scripts** perform automation.
* **Configuration** adapts the implementation to an environment.

Whether OpenCode's exact skill mechanism should be used remains an implementation question. The important architectural conclusion is that the methodology should not be coupled to whichever agent platform happens to be used at a given time.

---

# 20. Tooling Specifications

The final conceptual development of the phase was the recognition that there is a missing abstraction between methodology and implementation.

The emerging structure became:

```text
EDASES
Research
    ↓
ASES
Methodology
    ↓
Tooling Specifications
Platform-independent execution contracts
    ↓
Implementation
OpenCode skills
Claude Code skills
Scripts
Execution Engine
```

A **Tooling Specification** would define what a tooling capability must do without dictating how a particular platform implements it.

For example:

### EDASES

May establish that independent review improves evaluation quality.

### ASES

May establish that certain evaluations require independent reasoning.

### Tooling Specification

Defines the required interface and invariants for a clean-room review capability.

### Skill

Implements that capability for OpenCode.

### Execution Engine

May eventually implement the same capability internally, without relying on an individual skill.

This provides an API-like boundary between methodology and implementation.

It also makes the methodology portable across different agent environments.

---

# 21. The Emerging Tooling Architecture

The final model developed during the phase can therefore be represented as:

```text
                 EDASES
            Research Programme
                    │
                    ▼
                  ASES
               Methodology
                    │
                    ▼
        Tooling Specifications
      Platform-independent contracts
                    │
                    ▼
                Tooling
          ┌─────────┼─────────┐
          │         │         │
       Skills    Scripts   Templates
          │
          ▼
   Agent Platforms
   / Execution Engine
```

This is a refinement of the earlier three-layer model rather than a rejection of it.

The three principal project layers remain:

1. Research
2. Methodology
3. Tooling

The tooling layer itself now has an internal distinction between:

* specifications
* implementations

That distinction prevents the methodology from becoming coupled to a particular agent platform.

---

# 22. What Was Accomplished

The most important accomplishment of this phase was not the creation of individual documents.

It was the establishment of a coherent separation between:

```text
Research
What have we learned?

        ↓

Methodology
How should software engineering be performed?

        ↓

Tooling Specification
What must a system provide to execute the methodology?

        ↓

Tooling Implementation
How does a particular platform actually do it?
```

This resolves several earlier ambiguities simultaneously.

It explains:

* why EDASES and ASES are separate;
* why ASES should be technology-independent;
* why the execution engine is downstream of the methodology;
* why reasoning and epistemic relationships are central;
* why documentation must be organized by abstraction;
* why model capabilities need explicit evaluation;
* why mechanical enforcement is necessary;
* why skills should not become the methodology itself;
* and why tooling needs its own specification layer.

---

# 23. Remaining Questions

Several questions remain deliberately unresolved.

### Evaluation

The exact empirical criteria for determining that ASES produces better software engineering remain an active research question.

The project must demonstrate improvement in terms that matter to the stated objective rather than merely demonstrating compliance with its own procedures.

### Tooling Architecture

The exact architecture of the execution engine remains open.

The next step is to assess current tooling and state-of-the-art agent workflows before deciding how the mechanical system should be built.

### Skill Architecture

The exact relationship between ASES tooling specifications and platform-specific skills remains to be experimentally established.

OpenCode is the current practical environment, but the methodology should not become dependent upon it.

### Repository Separation

The project may eventually become multiple repositories:

```text
EDASES
ASES
Tooling / Execution Engine
```

The conceptual separation should be established before physical repository separation is necessary.

---

# 24. Transition to the Next Phase

The documentation work established the conceptual foundation required for adversarial repository review.

The immediate next step is therefore not additional conceptual expansion.

The repository should be reviewed against the new model.

Reviewers should determine whether:

* existing documents are still valid;
* terminology is consistent;
* abstraction boundaries are respected;
* outdated concepts remain;
* duplicate concepts exist;
* canonical relationships are correct;
* repository structure matches the documented architecture;
* implementation assumptions have leaked into methodology;
* methodology is sufficiently explicit to support future mechanization.

Only after that review should the project proceed into detailed investigation of existing tooling and state-of-the-art workflows for implementing the mechanical side of ASES.

The intended progression is therefore:

```text
Phase 1
Conceptual and documentation restructuring
        ↓
Phase 2
Adversarial repository validation
        ↓
Phase 3
Tooling and state-of-the-art research
        ↓
Execution Engine / Tooling Development
```

The central result of this phase is that EDASES is no longer best understood as a single software project.

It is a research programme developing a methodology, with a tooling layer that will eventually make that methodology mechanically executable.
