---
title: "EDASES Topic: UI Design"
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard
  - EDASES Phase 4 Retrospective

related_documents:
  - research-programs/execution-engine-ui/EDASES-execution-engine-summary.md
  - research/execution-engine-ui/synthesis/execution-engine-ui-synthesis.md

consumed_by:
  - research-programs/execution-engine-ui/

last_updated: 2026-08-10
---

# EDASES topic: UI design

## Retrospective

### 1. Context

This discussion began with a practical problem encountered while working on EDASES: as the research expanded across multiple projects, repositories, AI conversations, and development activities, managing the work through CLI interfaces became increasingly difficult.

The proposed solution was a visual frontend that could eventually become the interface for the EDASES execution engine, while also being immediately useful as a project-status and research-navigation tool.

The initial concept was a visual flow-chart-like interface in which:

* the overall EDASES project forms the primary context;
* the three EDASES layers have gated information passage between them;
* repositories connect to the broader development environment;
* repositories expose active projects;
* projects expose their work through project-management views;
* individual nodes can link to the relevant OpenCode sessions;
* research, hypothesis testing, reviews, and project outcomes can be connected to the work that produced them.

The discussion subsequently clarified that this should not be treated as a conventional project-management application. The frontend is ultimately intended to expose a much larger execution and knowledge system.

---

# 2. Existing EDASES architecture relevant to the UI

The supplied canonical documents establish three distinct layers:

```text
EDASES
Research Programme
        │
        ▼
ASES
Methodology
        │
        ▼
Execution Engine
Implementation
```

EDASES asks what has been learned, ASES defines how software engineering should be performed, and the Execution Engine implements that methodology.

The documents emphasize that higher abstraction layers must not depend upon lower ones. Research must remain independent of implementation, while implementation derives from methodology.

This became important during the discussion because the proposed UI is ultimately associated with the execution engine, but the research question about the UI belongs at the EDASES research layer.

The execution engine is therefore **two layers below EDASES**, not another component of EDASES research itself.

The frontend research should determine whether particular representations and technologies are suitable; it should not prematurely define the implementation of ASES.

---

# 3. What the frontend is intended to become

The long-term system is not an AI assistant.

The supplied execution-engine description characterizes it as a software engineering system that coordinates:

* humans;
* AI models;
* knowledge;
* verification;
* methodology;
* engineering state.

The engineering process itself is the primary product.

The intended relationship is:

```text
Principal
    ↓
Engineering Methodology
    ↓
Execution Engine
    ↓
AI Roles + Verification + Knowledge
    ↓
Software
```

LLMs are execution resources rather than the architectural centre.

The engine controls workflow, governance, verification, evidence, and lifecycle, while LLMs perform planning, reasoning, implementation, and review.

The system is expected to orchestrate engineering artefacts rather than merely conversations or agents.

Likely artefacts include:

* requirements;
* architectural decisions;
* risks;
* experiments;
* evidence;
* verification artefacts;
* implementation tasks.

Each artefact can have state, ownership/role, dependencies, evidence, and verification status.

This distinction became central to understanding the UI.

---

# 4. Initial frontend concept

The initial proposed interface was described as something like a flow chart.

The top-level project would expose the three EDASES layers with gated information passage.

Repositories would connect to other development repositories on the VPS to expose:

* shared code;
* tooling;
* methodology;
* AI knowledge;
* hypothesis-testing plans;
* reviews;
* post-project evaluation.

A repository node could be opened to reveal its active projects.

A project node could then open into its own project-management chart containing information such as:

* stages;
* projects;
* time allocated;
* time actually taken;
* blocking versus non-blocking work;
* other standard project-management information.

The interface would initially provide useful visual status even before the underlying state-machine execution engine existed.

The eventual objective is for this visualization to become the frontend of the full state-machine system.

---

# 5. Canonical source of truth

The overall EDASES project uses the committed Git repository as its canonical source of truth.

Projects inside repositories are less standardized at present, but standardizing their representation is a future objective.

A repository can contain multiple projects.

The smallest operational unit discussed for the visual representation is a **subtask**, although the precise hierarchy remains somewhat open and is informed by Crosslink.

The frontend therefore needs to accommodate a hierarchy along the lines of:

```text
Repository
    └── Project
            └── Stage
                    └── Task
                            └── Subtask
```

This is a working representation rather than a finalized schema.

---

# 6. Relationship to Crosslink

Crosslink is relevant because it already provides concepts for coordinating work across repositories and agents.

The intended frontend should build on that conceptual territory rather than independently inventing another task-management model.

Repositories are not simply source-code locations. They provide access to projects, tooling, and AI-development infrastructure.

However, repositories are not necessarily the ultimate root of the system.

A major conclusion of the discussion was that **EDASES should remain canonical**.

Projects brought under the EDASES umbrella should provide feedback to EDASES because EDASES is specifically concerned with learning about human-AI interaction and successful software development.

Thus the relationship is better understood as:

```text
EDASES
   │
   ├── Research
   │
   ├── Findings
   │
   └── Projects / Development Activities
             │
             ├── Repository A
             ├── Repository B
             └── Repository C
```

The repositories provide evidence and activity to the research programme rather than becoming the conceptual root of the system.

The Crosslink archive referenced during the discussion was not directly inspectable in the available file tooling, so no additional Crosslink-specific claims should be treated as established by this retrospective beyond what was explicitly discussed.

---

# 7. OpenCode sessions

Actual work is currently performed through OpenCode.

The frontend should eventually provide links from relevant work nodes to the OpenCode sessions that performed the work.

The session itself is not necessarily intended to become permanent knowledge.

Instead, as long as the session remains accessible, it should be findable because some questions may only be answerable by inspecting the original session.

This is especially important because AI-agent harnesses can lose conversations or make them difficult to retrieve.

Research summaries of conversations are therefore first-class objects, but they cannot exist independently of the conversations that produced them.

The intended relationship is approximately:

```text
Work artefact
      │
      ├── Research summary
      │
      └── OpenCode session
                │
                └── original reasoning
```

The summary provides compact reusable context.

The session provides the deeper provenance when the summary is insufficient.

---

# 8. The distinction between project management and knowledge graphs

A question arose over whether describing the system as a knowledge graph was actually meaningfully different from project management.

The conclusion was that conventional project-management systems can be viewed as limited knowledge graphs, but their primary model is generally **work and workflow**.

For example:

```text
Project
    ├── Epic
    │     ├── Story
    │     └── Task
    └── Milestone
```

EDASES requires a broader representation.

Its graph needs to represent relationships such as:

```text
Observation
      │
      ▼
Finding
      │
      ▼
Methodology
      │
      ▼
Requirement
      │
      ▼
Implementation
      │
      ▼
Verification
```

alongside work relationships.

Tasks are therefore one class of engineering artefact rather than the fundamental object of the system.

The EDASES architecture explicitly states that the project is organized around engineering reasoning rather than source code and that observations, assumptions, findings, decisions, challenges, and validations form the knowledge structure.

The resulting characterization was:

> The system is not primarily a project-management tool or primarily a knowledge graph. It is a runtime for software engineering that needs to expose both.

---

# 9. State machines

The execution-engine research material provided during the discussion clarified the role of state machines.

State machines provide deterministic workflow while permitting probabilistic reasoning within states.

The engine controls:

* workflow;
* governance;
* verification;
* evidence;
* lifecycle.

LLMs control:

* planning;
* reasoning;
* implementation;
* review.

Two different representations are expected to be necessary:

### Statecharts

Statecharts model artefact lifecycles.

Example:

```text
Requirement

Proposed
   ↓
Clarified
   ↓
Accepted
   ↓
Implemented
   ↓
Verified
   ↓
Operational
```

### Workflow graphs

Workflow graphs model execution.

Example:

```text
Requirement
    ↓
Architecture
    ↓
Implementation
    ↓
Verification
```

The discussion established that these should not be conflated.

---

# 10. State machines versus the broader EDASES representation

A traditional state machine answers primarily:

> What state is this object in?

The EDASES system must also answer:

> Why did it get here?

A conventional transition might therefore look like:

```text
Draft ──► Approved
```

whereas EDASES requires the transition to carry provenance:

```text
Draft
   │
   ▼
Transition
   ├── Evidence
   ├── Assumptions validated
   ├── Review summary
   ├── Approver
   ├── Conversation
   ├── Verification
   └── Timestamp
   │
   ▼
Approved
```

The transition is therefore potentially an engineering artefact in its own right.

The system is consequently not merely a sophisticated state machine.

It potentially combines:

```text
State graph
"What state?"

Workflow graph
"What happens next?"

Knowledge graph
"What do we know?"

Version graph
"How did this evolve?"
```

These may ultimately be different views over the same underlying artefacts.

This is consistent with the supplied execution-engine research direction, which explicitly identifies statecharts, workflow graphs, knowledge persistence, evidence tracking, and lifecycle management as separate concerns.

---

# 11. Artefact-specific lifecycles

The discussion rejected the idea that every artefact should necessarily share one universal state machine.

Instead, different artefact types may have different lifecycles.

Illustrative examples discussed were:

```text
Requirement
Proposed → Clarified → Accepted → Implemented → Verified → Operational
```

```text
Experiment
Planned → Running → Completed → Analysed
```

```text
Decision
Proposed → Accepted → Superseded
```

```text
Risk
Identified → Mitigated → Closed
```

```text
Project
Planning → Active → Review → Complete
```

These are examples rather than established EDASES state definitions.

The important architectural question is whether the engine should support a registry of artefact-specific lifecycle definitions rather than one enormous global state machine.

Hierarchical state machines, including systems such as XState, became relevant because artefacts can have their own lifecycles while participating in larger project lifecycles.

---

# 12. Versioning became a central requirement

The discussion established that artefacts should be versioned rather than simply overwritten.

This aligns directly with the purpose of EDASES: new agents are frequently asked to perform zero-context tasks and need the minimum information necessary to succeed without wasting context on irrelevant history.

A useful example is:

```text
Plan A — v1
    │
    ├── rejected
    │
    ├── because Assumption X failed
    │
    ▼
Evidence / Experiment
    │
    ▼
Plan B — v2
    │
    └── based on revised assumption Y
```

The objective is not merely to preserve a textual history.

The system should make the reasoning behind change traversable.

A future agent should be able to determine:

* what currently exists;
* why it exists;
* what alternatives were rejected;
* why they were rejected;
* what evidence caused the change;
* whether previously rejected alternatives might become relevant again.

This should allow an agent to retrieve the minimum relevant historical context rather than consuming an entire conversation transcript.

---

# 13. Context reconstruction

This became one of the strongest conceptual conclusions of the discussion.

Most agent systems primarily optimize **context injection**:

```text
Conversation
    ↓
Summary
    ↓
Next agent
```

EDASES has a potentially different objective:

> **Context reconstruction.**

The underlying engineering history is represented as structured artefacts and relationships:

```text
Artefact v1
    │
    ├── based on Assumption A
    ├── supported by Evidence E1
    └── produced by Session S12
            │
            ▼
        Rejected
            │
            ├── reason:
            │      Assumption A falsified
            │
            ▼
        Artefact v2
            │
            ├── based on Assumption B
            └── references relevant history
```

The new agent does not necessarily need the old conversation.

It needs the relevant engineering state and rationale.

This led to a sharper possible research objective:

> Minimize the amount of historical information an agent must consume to perform a task correctly while preserving the ability to reconstruct the engineering rationale on demand.

This is potentially measurable through:

* token consumption;
* task completion;
* correctness;
* interruption recovery;
* principal oversight effort;
* verification coverage;
* cognitive load.

These metrics are consistent with the execution-engine research material supplied during the discussion.

---

# 14. Conversation versus knowledge

A further distinction emerged:

```text
Conversation
      │
      ▼
Observations
      │
      ▼
Evidence
      │
      ▼
Findings
      │
      ▼
Decisions
      │
      ▼
Artefact revisions
```

The conversation is therefore potentially **provenance**, rather than the canonical state of the engineering system.

This is significant because the system should not become dependent on the continued existence of any particular LLM conversation.

A conversation can explain how an artefact came into existence, but the artefact's structured state and relationships should remain usable independently.

At the same time, original sessions should remain discoverable while they are still available, because summaries cannot necessarily answer every future question.

---

# 15. Historical state and deletion

Project history matters, but not everything needs to remain permanently active.

The discussion specifically identified the value of preserving the rationale for deletion or removal.

For example:

```text
Task deleted

Reason:
Duplicate of Task #142

Decision:
2026-07-12

Author:
Agent

Approved by:
Human
```

This suggests that historical provenance is more important than indiscriminately preserving every transient object.

The system therefore needs to distinguish between:

* current active state;
* historical versions;
* superseded artefacts;
* removed artefacts;
* the rationale for transitions and removal.

This does not establish that EDASES should use event sourcing; that remains an open architectural question.

---

# 16. Proposed frontend views

The discussion converged on the possibility that one underlying information model could support several complementary views.

### Execution view

The operational view:

```text
Repository
    ↓
Project
    ↓
Stage
    ↓
Task
    ↓
Subtask
```

### State view

The lifecycle of the selected artefact:

```text
Current State

Accepted

History
    Proposed
    Clarified
    Accepted

Allowed transitions
    → Rejected
    → Implemented
```

### Evidence view

Evidence associated with an artefact:

```text
Requirement

Evidence
    ├── Conversation Summary
    ├── Experiment
    ├── Decision
    ├── Review
    └── Verification
```

### Knowledge view

Relationships between engineering knowledge:

```text
Observation
    │
    └── supports
            ↓
          Finding
            │
            └── informs
                    ↓
                Requirement
```

These should be considered views over a shared model rather than necessarily separate systems.

---

# 17. Node information

The frontend should expose different information depending on the selected representation.

The user specified that if information exists, it should appear differently depending on whether the user is looking at a node or a project-management chart based on that node.

The initial candidate node information included:

* status;
* current stage;
* blocking/non-blocking status;
* owner;
* confidence;
* elapsed versus estimated time;
* active OpenCode session.

The precise visible fields remain open.

---

# 18. Graph interaction

The preferred interaction model is a zoomable graph.

The user is open to React Flow after briefly reviewing its homepage.

Performance is the primary constraint.

The environment is an 8 GB VPS, and the tool should ideally remain usable on even smaller systems.

The user therefore prefers existing systems over building a custom graph engine.

The graph should support navigation through large amounts of information without requiring everything to be rendered simultaneously.

The exact mechanism for achieving this remains an open research question.

---

# 19. Repository/project relationships

Repositories and projects are distinct concepts.

A repository may contain multiple projects.

Projects may eventually span multiple repositories.

The user initially indicated that a project could currently have one parent context, while acknowledging that this may be a mistake and remains an open topic.

This is therefore an unresolved data-model question:

> Can an artefact belong to multiple contexts simultaneously, or should it have exactly one canonical parent?

The question matters for research summaries, evidence, hypotheses, and other objects that may logically relate to multiple projects.

---

# 20. Research summaries and hypotheses

Research summaries of conversations are first-class objects.

They must remain linked to the conversation that produced them.

The user specifically clarified that a research summary needs to be reviewable from the node to which it relates.

Hypotheses were discussed more carefully.

The user does not want the system's conceptual model to simply store a hypothesis as an isolated object.

Instead, the important information is:

* reasoning leading to the hypothesis;
* the test performed;
* results of the test.

This again reinforces the emphasis on reasoning and evidence rather than merely storing labels.

---

# 21. EDASES as feedback recipient

Projects brought under the EDASES umbrella should feed information back into EDASES.

The purpose of this relationship is specifically to learn about human-AI interaction and successful software development.

Thus, project activity is not merely execution data.

It can become research evidence.

Conceptually:

```text
External Development Project
        │
        ├── execution
        ├── failures
        ├── successes
        ├── agent interactions
        └── verification outcomes
                    │
                    ▼
                 EDASES
                    │
                    ▼
               Research
                    │
                    ▼
                 ASES
```

This is consistent with the canonical architecture's statement that implementation experience can generate new research questions while research findings can revise methodology.

---

# 22. MVP direction

The discussion concluded that the first implementation should **not** attempt to build the execution engine.

The MVP should instead be a research instrument.

Its purpose would be to determine whether existing open-source components can be composed into a visual execution environment that represents:

* engineering artefacts;
* state;
* reasoning;
* evidence;
* version history;

while meeting the project's performance constraints.

The MVP should be deliberately throwaway.

If existing components prove adequate, that is a research result.

If they prove inadequate, that is also a research result.

---

# 23. Candidate MVP artefacts

A minimal prototype could initially contain only:

```text
Repository
Project
Artefact
Version
Evidence
Conversation Summary
```

The prototype should support:

* graph navigation;
* opening a node;
* inspecting versions;
* inspecting evidence;
* inspecting conversation summaries;
* following supersedes relationships;
* displaying current state.

The initial prototype should **not** attempt to implement:

* AI orchestration;
* full workflow execution;
* multi-user support;
* permissions;
* distributed execution;
* plugin architecture;
* scheduler implementation;
* custom graph rendering;
* other execution-engine infrastructure.

The purpose is to test the information representation, not to build the production runtime.

---

# 24. Research hypotheses

Several concrete hypotheses emerged.

### H1 — Artefact abstraction

Engineering artefacts are a more useful primary abstraction than repositories.

### H2 — Context reduction

Versioned artefacts and explicit provenance reduce the amount of context required for zero-context agents.

### H3 — Interruption recovery

Explicit provenance improves an agent's ability to resume interrupted work.

### H4 — Unified representation

A shared graph can represent execution, reasoning, evidence, and version history without becoming unusable.

### H5 — Existing graph UI

Existing graph libraries are sufficient for the required visualization.

### H6 — Existing statechart technology

Existing statechart libraries are sufficient for artefact lifecycle representation.

### H7 — Existing persistence technology

Existing graph or relational technologies can naturally represent artefacts, versions, evidence, provenance, and supersession without excessive schema complexity.

### H8 — Execution representation

Explicit execution graphs may improve software engineering outcomes for non-programmer principals compared with conversational orchestration.

The execution-engine research material suggested potential metrics including software quality, principal oversight effort, verification coverage, interruption recovery, token efficiency, task completion, and cognitive load.

---

# 25. Technology research areas

The proposed research should examine existing systems rather than assume that bespoke infrastructure is required.

Candidate areas identified during the discussion included:

### Graph UI

* React Flow
* Cytoscape
* ELK.js
* AntV X6
* JointJS
* Rete.js

Questions include:

* graph performance;
* hierarchical graphs;
* expandable nodes;
* incremental rendering;
* virtualization;
* integration with PM views;
* maintenance status.

### State machines

* XState
* Stately
* SCXML
* hierarchical statecharts

Questions include:

* independent artefact lifecycles;
* state inspection;
* persistence;
* versionable state definitions;
* visual tooling.

### Workflow engines

* Temporal
* LangGraph
* Burr
* Camunda
* BPMN

Questions include:

* whether they provide execution infrastructure or impose unwanted workflow semantics;
* which components are reusable;
* how closely their models align with EDASES.

### Knowledge/data layer

Candidate technologies discussed included:

* Neo4j;
* Memgraph;
* Kuzu;
* PostgreSQL;
* SQLite;
* vector-enabled persistence where appropriate.

Questions include whether these systems naturally model:

* artefacts;
* versions;
* evidence;
* provenance;
* supersession;
* state.

### Engineering methodologies

Potential sources for existing concepts included:

* SEMAT Essence;
* OMG SPEM;
* ArchiMate;
* OpenProject;
* Jira-style project representations.

The purpose is to avoid reinventing concepts that already exist.

---

# 26. Research should be question-driven

A significant methodological conclusion was that subagents should not simply be assigned technologies.

Instead of:

> Research React Flow.

the task should be:

> Determine whether existing graph frameworks can represent EDASES engineering artefacts and their relationships without substantial customization.

Technology-specific agents can then investigate React Flow, Cytoscape, X6, and others as evidence toward that question.

This makes synthesis about the research question rather than about competing products.

---

# 27. Proposed research questions

The initial research plan converged on questions such as:

### RQ1

Can existing graph frameworks represent engineering artefacts and their relationships without substantial customization?

### RQ2

Can hierarchical statechart frameworks model independent artefact lifecycles?

### RQ3

Can existing workflow engines provide useful execution infrastructure without imposing workflow semantics that conflict with EDASES?

### RQ4

Can existing persistence technologies naturally represent artefacts, versions, evidence, provenance, and supersession?

### RQ5

Can one frontend expose execution, state, evidence, and version-history views over the same underlying information?

### RQ6

Can an agent successfully recover and perform a task using artefact history instead of the original conversation history?

RQ6 is especially important because it directly tests the context-reconstruction objective.

---

# 28. Proposed research-agent workflow

The intended research process was:

```text
Orchestrator
      │
      ▼
Research Subagents
      │
      ├── research
      ├── web search
      ├── source analysis
      └── prototype spikes
      │
      ▼
Reports saved to repository
      │
      ▼
Synthesizing Agent
      │
      ▼
Research Synthesis
      │
      ▼
Adversarial Reviewer
      │
      ├── PASS
      │
      └── FAIL
      │
      ▼
Orchestrator
      │
      ▼
Human
```

The orchestrator should read only the passing synthesis report when communicating the research outcome to the human.

The original reports remain available for provenance and review.

---

# 29. Report structure

A common report format was proposed:

```text
Question

Scope

Evidence

Findings

Rejected Options

Unknowns

Confidence

References
```

Subagents should provide evidence rather than prematurely converting evidence into project direction.

The synthesizer should:

* read the reports;
* identify agreements;
* identify disagreements;
* identify unsupported claims;
* identify remaining uncertainties;
* cite the underlying reports;
* avoid additional research unless explicitly tasked to do so.

The reviewer should inspect both the original reports and synthesis and determine whether the synthesis:

* accurately represents the reports;
* invents claims;
* omits conflicting evidence;
* properly labels uncertainty.

The reviewer should return PASS or FAIL rather than silently becoming another synthesizer.

---

# 30. OpenCode operating constraints

The planned research will be conducted through OpenCode using an OpenCode Go subscription.

The orchestrator should not be GLM-5.x or Kimi K2.7 Code as the primary model.

Those models may be used for bounded tasks where no other available agent is reasonably expected to accomplish the task.

The free OpenCode Zen subagents can perform:

* research;
* web searches;
* coding;
* source analysis;
* prototype work;
* bounded investigations.

Token expenditure is therefore not the primary optimization target.

**Linear elapsed time is.**

This favors aggressive parallelization of independent research tasks.

The intended pattern is:

```text
Orchestrator
    │
    ├── Agent A ──┐
    ├── Agent B ──┤
    ├── Agent C ──┤
    ├── Agent D ──┤
    └── Agent E ──┘
                  │
                  ▼
              Synthesis
                  │
                  ▼
               Review
```

Synthesis and review remain sequential because they depend on the completed research set.

---

# 31. The orchestrator's role

The orchestrator should not perform the research itself unless necessary.

Its role is to:

1. establish the research questions;
2. divide them into bounded independent investigations;
3. launch subagents;
4. collect their reports;
5. invoke synthesis;
6. invoke adversarial review;
7. reject failed synthesis;
8. return only validated research to the human.

This preserves the orchestrator as a coordinator rather than allowing it to become the primary researcher.

The approach also matches the broader EDASES principle that independent reasoning is valuable when independent judgement is required and that consensus should emerge through evidence rather than repetition.

---

# 32. Research should include the orchestration process itself

An additional conclusion was that the research workflow can itself become an EDASES experiment.

Useful measurements could include:

* total elapsed time;
* number of parallel agents;
* number of research reports;
* synthesis failures;
* review failures;
* synthesis revisions;
* token consumption by stage;
* time spent waiting on sequential stages;
* human review effort.

This would allow EDASES to learn whether the research methodology itself is efficient and reliable.

The goal is therefore not simply to discover a suitable UI architecture.

The process should also produce evidence about how EDASES can efficiently conduct its own research.

---

# 33. Current conceptual model

By the end of the discussion, the emerging model was approximately:

```text
                         EDASES
                    Research Programme
                           │
              ┌────────────┴────────────┐
              │                         │
         Research                     Projects
              │                         │
              │                    Repositories
              │                         │
              │                      Projects
              │                         │
              │                       Stages
              │                         │
              │                        Tasks
              │                         │
              │                      Subtasks
              │                         │
              │                  OpenCode Sessions
              │
              └──────────────┐
                             │
                       Research Evidence
                             │
                     ┌───────┴────────┐
                     │                │
                  Findings        Methodology
                                      │
                                      ▼
                                    ASES
                                      │
                                      ▼
                              Execution Engine
```

The visual frontend is therefore not simply a project dashboard.

It is expected eventually to provide multiple views into the state, execution, provenance, knowledge, and evolution of engineering artefacts managed by the execution engine.

---

# 34. Outstanding research questions

The following remain deliberately unresolved:

* What is the exact canonical artefact hierarchy?
* Can artefacts have multiple parents or contexts?
* What should be the precise relationship between repositories and projects?
* Which artefacts require lifecycles?
* Which lifecycle definitions should be standardized?
* Should transitions themselves be immutable artefacts?
* How much history should be retained?
* What deletion/archival model best preserves rationale?
* Should the underlying persistence model be graph-oriented, relational, event-oriented, or hybrid?
* Can existing graph UI components handle the required scale on an 8 GB VPS?
* How should large graphs be virtualized or progressively loaded?
* How should execution, state, evidence, knowledge, and version views share one underlying model?
* Can existing state-machine tooling provide sufficient functionality?
* Can existing workflow infrastructure be reused without contaminating the methodology layer?
* Can an agent actually perform better with structured version/provenance context than with conversation summaries?
* What is the minimum context required for successful zero-context task execution?
* Which parts of the final system belong to ASES methodology versus execution-engine implementation?

These should remain research questions until evidence is available.

---

# 35. Final direction

The strongest conclusion from the discussion is that the frontend should initially be treated as an **EDASES research instrument for testing representations of engineering state and reasoning**, not as the beginning of the execution engine implementation.

The central hypothesis is not merely:

> Can we make a useful visual project manager?

It is closer to:

> Can engineering work be represented as versioned, stateful, evidence-linked artefacts in a way that allows humans and zero-context AI agents to recover the minimum necessary context, execute work reliably, and reconstruct the reasoning behind changes when required?

The UI is valuable because it makes that representation observable.

The eventual execution engine is valuable because it can make the representation executable.

The research programme remains above both.

That separation preserves the project's established architecture: EDASES develops research, ASES defines methodology, and the execution engine implements methodology.
