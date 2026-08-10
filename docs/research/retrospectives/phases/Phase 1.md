---
title: "EDASES Phase 1 Retrospective"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - charters/Charter v1.md
  - research-programs/Operational Research Program v1.md
  - assumption-registers/Assumption Register v1.md
  - core-system-prompts/Core System Prompt v1.md
  - research-handoffs/Research Handoff 1.md
  - research-addenda/Research Addendum 01.md

consumed_by:
  - EDASES Phase 2 Retrospective

supersedes: []

superseded_by:
  - EDASES Phase 2 Retrospective

last_updated: 2026-08-10
---

# EDASES Phase 1 Retrospective

## Purpose

This retrospective captures the conceptual work completed during the first phase of the EDASES (Evidence-Driven Agentic Software Engineering System) research project. Rather than designing software immediately, Phase 1 focused on reframing the problem, identifying assumptions, extracting evidence from prior projects, and establishing the research methodology that will guide future work.

The most significant outcome of this phase is that EDASES is no longer viewed primarily as a coding harness project. It has evolved into a research program investigating how a non-programmer principal can direct an AI workforce to produce high-quality software through organizational design, verification, and accumulated knowledge.

---

## Initial Question

The project began with a relatively narrow engineering question:

> Which existing coding harness should become the foundation of a unified AI development environment?

The primary candidates were:

* OpenCode
* OpenClaudia
* CodeWhale

The initial assumption was that the project would largely consist of selecting the strongest harness and importing useful features from the others. OpenCode was viewed as the likely base because of its existing provider support, large ecosystem, multiple interfaces, and relative maturity; OpenClaudia and CodeWhale were treated mainly as sources of features to port in.

---

## Major Reframing

By the end of Phase 1, the central question had become:

> What kind of organizational system is required to allow a non-programmer principal to reliably direct AI agents in software development?

This shifted the project's center of gravity away from code generation and toward:

* Organizational design
* Knowledge persistence
* Verification
* Capability management
* Principal oversight

Harnesses became one subsystem rather than the architectural foundation. Most existing coding harnesses assume a Human Developer ↔ AI Assistant ↔ Repository model. EDASES increasingly assumes a Principal → Organization → Agents → Verification → Outcomes model. The project is not primarily concerned with making coding easier — it's concerned with enabling effective software production without requiring the principal to function as a software developer.

---

## Most Important Insight: Progressive Externalization

The strongest pattern identified across historical projects was not model improvement — it was workflow evolution through progressively externalizing knowledge.

### Observed progression

1. Chat conversations
2. Session notes
3. CLAUDE.md files
4. Structured handoffs
5. Git-versioned retrospectives
6. Issue tracking
7. Crosslink
8. Multi-agent coordination
9. Multi-model organizations

Each stage moved critical project knowledge further away from conversational memory and into durable organizational systems.

### Working hypothesis

> Project success improves as knowledge is externalized into persistent organizational infrastructure.

Crosslink emerged as an important implementation of this principle, but the principle itself appears broader than any individual tool. Initially Crosslink was viewed simply as an issue tracker; later it was reinterpreted as evidence of a broader organizational pattern. The likely finding is not "Crosslink improves projects" but "persistent organizational structures improve projects" — Crosslink is one implementation of that principle. This distinction matters because it shifts attention from tools to underlying mechanisms.

---

## Evolution of Development Practice

Historical projects demonstrated a clear evolution in how software was produced.

### Generation 1 — Conversational Development

* Claude web chat
* Manual copy/paste into terminals
* Minimal persistence
* High coordination overhead

### Generation 2 — Execution-Centered Development

* Claude Code
* Live feedback loops
* Working development environments
* Reduced execution friction

### Generation 3 — Documentation-Centered Development

* CLAUDE.md
* Project conventions
* Architecture documents
* Persistent institutional memory

### Generation 4 — Organizational Development

* Structured issue tracking
* Chainlink
* Crosslink
* Agent coordination through shared project state

### Generation 5 — Specialized Agent Organizations

* Behavioral modes
* Multi-agent swarms
* Multi-model routing
* Role specialization

The progression suggests that improvements in organizational structure produced larger productivity gains than improvements in individual models.

---

## Principal-Led Software Engineering

One of the foundational ideas clarified during this phase is that EDASES is **not** attempting to teach non-programmers how to read code.

Instead, it seeks to reduce the amount of trust required in implementation.

### Traditional model

Trust developers because implementation is opaque.

### EDASES model

Trust verification because implementation becomes secondary.

This distinction led to the introduction of **Verification Accessibility** as a core principle. The goal is not to teach principals to read code — it is to provide verification artifacts that make code inspection unnecessary whenever practical. The principal's responsibility becomes evaluating whether software satisfies requirements, not evaluating how it was implemented.

---

## Organizational Intelligence

A major realization was that roles are more fundamental than models.

### Historical workflow

* Opus handled planning and coordination.
* Sonnet handled implementation.
* Later, DeepSeek handled bounded feature work.
* Crosslink coordinated shared task state.

The important observation was not that one model was superior. It was that stable organizational **roles** emerged independently of model choice — though natural emergence does not imply optimality. The roles that emerged may be path-dependent, shaped as much by which tools happened to be available as by any underlying organizational logic. This remains an active area of research rather than a settled finding.

Underlying this is a practical reality: models, providers, costs, and capabilities all change continuously, so static model recommendations are insufficient. The project will likely require capability registries, ongoing benchmarking, dynamic routing, and longitudinal capability tracking. Roles should be stable; model assignments should remain flexible.

### Working hierarchy

Task → Role → Capability Requirements → Model Selection

This became one of the central architectural principles of EDASES.

---

## Harnesses Reconsidered

The project originally assumed one existing harness would become the foundation.

By the end of Phase 1, that assumption had been suspended.

### Existing harness philosophy

Human programmer ↔ AI assistant ↔ Repository

### Emerging EDASES philosophy

Principal → Organization → Roles → Agents → Verification → Outcomes

This reframing introduced new research questions: Do existing coding harness architectures actually align with EDASES requirements? Should a coding harness be the foundation of EDASES at all, or merely one subsystem within a larger organizational platform? Both remain unresolved.

---

## Verification as Organizational Infrastructure

Verification was reframed from a quality-control activity into organizational infrastructure.

Rather than asking whether agents write good code, the project began asking:

* Can software be evaluated without reading code?
* Can verification replace trust?
* Can formal methods become economically viable because agents absorb the complexity?

Thermite became important not because of its language, but because it represents a different philosophy of software production. It was initially treated as a future enhancement, but its real significance is that it potentially shifts software evaluation from trust in implementation to verification of behavior — which aligns directly with the project's non-programmer-principal objective.

---

## Evidence Before Experimentation

Another major shift was methodological.

The project originally assumed it would begin by running experiments.

Instead, it became clear that a substantial body of evidence already exists.

### Existing evidence sources

* 50+ session notes
* Git-versioned retrospectives
* CLAUDE.md evolution
* Crosslink databases
* Project conventions
* Completed software projects
* Architecture pivots
* Multi-model workflows

This transformed Phase 0 of the research program into **Historical Evidence Extraction** rather than exploratory experimentation.

---

## The TripN / Beds24 Case Study

The strongest operational evidence discussed was the TripN ecosystem — a five-site Astro deployment including a Beds24 hostel booking integration.

### Key observations

* WordPress proved difficult for agents.
* The architecture pivoted to Astro.
* Development accelerated substantially.
* More ambitious design work became feasible.
* The project was completed in approximately two months.

The important finding was not that Astro is universally superior. It was that **framework compatibility with agent workflows** appears to have a profound effect on project outcomes. As of Phase 1, this evidence supports a "Tested" classification rather than "Strong Evidence" — the pattern held in one substantial case but hasn't yet been stress-tested across enough independent projects to call it confirmed. This remains an active research area.

A related, separable observation is that agent productivity appears environment-dependent in a broader sense: framework and technology selection dramatically affect agent effectiveness, and human developer preferences don't necessarily align with what makes agents productive. Technologies popular among human developers may not be optimal choices for AI agents. This opened several adjacent research directions — agent-native engineering, framework evaluation, language evaluation, and verification-oriented technology selection — that go beyond the single Astro/WordPress data point.

---

## Principal Experience

A significant realization was that UX is not secondary for non-programmers.

Instead, it becomes one of the primary engineering concerns.

Rather than optimizing for developer preference, EDASES optimizes for operational effectiveness.

Metrics proposed during Phase 1 include:

* Time to situational awareness
* Decision latency
* Recovery after long absences
* Trust calibration
* Oversight cost
* Verification comprehension

This established **Principal Experience (PX)** as a formal research domain.

---

## Documents Produced

Phase 1 resulted in the first coherent documentation set for EDASES.

### Core documents

* Core System Prompt
* EDASES Charter
* Research Program
* Assumption Register

### Supporting documents

* Research Handoff
* Architectural Addendum

Together these establish mission, methodology, evidence standards, research priorities, and organizational philosophy.

---

## Assumptions Reclassified

Several assumptions evolved substantially during discussion.

### Strengthened

* Structured project state outperforms chat history.
* Knowledge should persist independently of sessions.
* Role specialization emerges naturally as complexity grows.
* Model selection should follow role definition.

### Newly introduced

* Verification Accessibility
* Progressive Externalization
* Harness Strategy
* Organizational Intelligence

### Still unresolved

* Minimum effective role set
* Optimal information flow
* Framework vs. model impact
* Whether role emergence reflects genuine organizational logic or path-dependence on available tooling
* Whether any existing harness architecture is sufficient

---

## What Changed Most

### Original mental model

```text
Harness
├── Routing
├── Verification
└── UI
```

### End-of-phase mental model

```text
Principal
│
├── Organizational Layer
│   ├── Roles
│   ├── Crosslink
│   └── Workflow
│
├── Knowledge Layer
│   ├── Documentation
│   ├── Evidence
│   └── Memory
│
├── Capability Layer
│   ├── Registry
│   └── Routing
│
├── Verification Layer
│   ├── Thermite
│   ├── Testing
│   └── Review
│
├── Execution Layer
│   ├── OpenClaudia
│   ├── OpenCode
│   └── Other Harnesses
│
└── Principal Layer
    ├── Oversight
    ├── Reporting
    └── Decision Support
```

The addition of an explicit Principal Layer reflects the weight given to Principal Experience elsewhere in this retrospective — oversight and reporting are architectural concerns, not just usability polish. This represents the single largest conceptual shift of Phase 1.

---

## Lessons Learned

### 1. Organization matters more than expected.

The largest productivity gains came from improvements in coordination and knowledge management rather than code generation itself.

### 2. Verification changes the role of the principal.

The objective is not to eliminate technical rigor, but to make rigor inspectable without implementation expertise.

### 3. Models are increasingly interchangeable.

Stable organizational roles appear more durable than any individual model — though this needs to be weighed against the possibility that observed roles are path-dependent rather than optimal.

### 4. Historical projects are a research dataset.

The existing corpus is valuable enough to justify a dedicated evidence-extraction phase before new experimentation.

### 5. Harnesses may be replaceable components.

The enduring value of EDASES is likely to reside above the execution layer, in organizational design and verification systems.

---

## Open Questions Entering Phase 2

1. What organizational structure consistently emerges across historical projects?
2. What is the minimum effective role architecture?
3. Which information flows produce the highest-quality outcomes?
4. Can verification accessibility be measured objectively?
5. Do existing harnesses satisfy EDASES requirements, or does the project require a fundamentally new architecture?
6. Can capability registries continuously adapt to rapidly changing model ecosystems?
7. Can formal verification become economically viable at scale in agent-led software engineering?
8. How much does framework choice matter relative to model choice?

---

## Phase 1 Outcome

Phase 1 did not produce a coding harness.

It produced something more valuable: a coherent research framework grounded in operational experience rather than intuition.

The project now has a clear distinction between:

* **How models should reason** (System Prompt)
* **What the project exists to achieve** (Charter)
* **How evidence will be gathered** (Research Program)
* **What is known and unknown** (Assumption Register)

Most importantly, the project's defining insight is no longer "AI can write software."

It is that software engineering itself can be reorganized around evidence, verification, and organizational learning, enabling non-programmer principals to direct increasingly capable AI workforces with progressively less dependence on implementation-level trust.