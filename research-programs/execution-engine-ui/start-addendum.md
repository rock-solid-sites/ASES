MVP Objective

Determine whether existing open-source components can be composed into a visual execution environment that represents engineering artefacts, state, reasoning, and version history with acceptable performance and usability, without requiring a bespoke graph engine.

Everything else is secondary.

Phase 1: Technology Survey (Parallel)

Each subagent owns one research area and produces an evidence-based recommendation rather than implementation.

Agent A — Graph UI

Research:

React Flow
Cytoscape
ElkJS integration
AntV X6
JointJS
Rete.js

Questions:

Can nodes contain expandable PM views?
Performance with 5k+ nodes?
Incremental rendering?
Hierarchical graphs?
Virtualization?
Active maintenance?

Deliverable:

Recommendation with measured trade-offs.

Agent B — State Machines

Research:

XState
Stately
SCXML
hierarchical statecharts

Questions:

Independent lifecycle per artefact?
Runtime state inspection?
Versionable definitions?
Visual tooling?
Persistence?

Deliverable:

Recommendation.

Agent C — Workflow Engines

Research:

Temporal
LangGraph
Burr
Camunda
BPMN

Questions:

Are they orchestration engines or execution engines?
Which assumptions conflict with EDASES?
Which parts are reusable?

Deliverable:

Gap analysis.

Agent D — Graph Database / Knowledge Layer

Research:

Neo4j
Memgraph
Kuzu
PostgreSQL + pgvector
SQLite + edge tables

Questions:

Can they naturally represent:

artefacts
versions
evidence
supersedes
provenance

without becoming painful?

Agent E — Existing Engineering Methodologies

Research:

SEMAT Essence
OMG SPEM
ArchiMate
OpenProject
Jira Advanced Roadmaps

Question:

What concepts already exist that should not be reinvented?

Phase 2: Synthesis

A different agent should read all reports and answer only:

Which assumptions have evidence?

Not

Which technology is best?

Phase 3: Prototype

Only after Phase 2.

The prototype should deliberately do very little.

I'd aim for only six object types:

Repository
Project
Artefact
Version
Evidence
Conversation Summary

Capabilities:

graph navigation
click node
inspect versions
inspect evidence
inspect conversation summary
follow supersedes links
show current state

Nothing more.

No AI.

No orchestration.

No automation.

No workflow execution.

Just prove the information model works.

Research hypotheses

I think these are the important ones.

H1

Engineering artefacts are a better primary abstraction than repositories.

H2

Versioned artefacts reduce context requirements for zero-context agents.

Measure:

tokens required
successful task completion
H3

Explicit provenance improves interruption recovery.

Measure:

Can a fresh agent resume work faster?

H4

One graph can represent execution, reasoning and version history without becoming unusable.

H5

Existing graph UI libraries are sufficient.

If false:

Build custom components.

H6

Existing statechart libraries are sufficient.

If false:

Build custom runtime.

H7

Existing graph databases model the relationships naturally.

If false:

Use a relational/event model instead.

What I would not research yet

I would explicitly postpone:

multi-user support
permissions
distributed execution
AI orchestration
plugin systems
scheduler implementation
custom graph rendering
CRDTs
event sourcing
microservices

None of those answer your current research questions.

One suggestion that follows directly from your documents: make the first prototype throwaway by design.

EDASES is a research programme whose output is methodology, not software. The prototype exists to validate or invalidate hypotheses about representation, interaction, and architecture—not to become the execution engine itself. If React Flow plus XState plus a graph database turns out to be sufficient, that's a result. If they prove fundamentally incompatible with your requirements, that's an equally valuable result because it narrows the research space with evidence rather than intuition. That approach is very consistent with the project's emphasis on evidence-driven evolution over implementation-first development.

Ж漢Δ

Correct. Execution is not 1 but 2 layers down from EDASES. Let's write a prompt, with the following practical considerations:


@Web search

I'm going to use this as a prompt to an orchestrator agent in the EDASES repo in Opencode. I'm using an Opencode Go subscription. I don't want GLM-5.x or Kimi K2.7 Code as the main orchestrator, but they can be used for bounded tasks no other agent can be expected to accomplish. I'll be using the free subagents from Opencode Zen to do all research, tasks, coding, web search and anything else that comsumes tokens. As they're free I don't care how many tokens they burn, but I care about how much actual linear time things take. Let's develop a new research plan, scoped to a new subfolder, examining whatever we need to know for this new project.

Actutal layout
orchestrator calls subagents, they research and save reports
subagents report back to synthesizing agent, reads and synthesizes reports
reviewer reads original reports and synthesis, provides pass/fail
orchestrator reads only the passing synthesize report back to me

How do you propose we do this given the tools available?

I would structure this as a research programme, not an implementation project. The orchestrator's job is to minimize your attention, not maximize parallelism.

The workflow you've described is already close to optimal:

Orchestrator
      │
      ▼
Research Subagents (parallel)
      │
      ▼
Repository of reports
      │
      ▼
Synthesizer
      │
      ▼
Reviewer (adversarial)
      │
      ▼
PASS / FAIL
      │
      ▼
Orchestrator
      │
      ▼
Human

I would make one significant change.

Instead of assigning subagents by technology ("research React Flow"), assign them by research question.

For example:

Question

Can existing graph libraries represent EDASES?

        │
        ├── React Flow investigator
        ├── Cytoscape investigator
        ├── X6 investigator
        └── JointJS investigator

The synthesizer answers the question, not "which library is best."

That fits EDASES' evidence-first philosophy much better.

I also think every subagent should produce the same report structure.

Question

Scope

Evidence

Findings

Rejected options

Unknowns

Confidence

References

No recommendations.

No implementation.

Only evidence.

That makes synthesis dramatically easier.

The synthesizer should have a very constrained responsibility.

Its prompt should effectively be:

Read all accepted reports.

Do not perform additional research.

Identify:

points of agreement
disagreements
unsupported claims
remaining uncertainties

Produce a research synthesis.

Every conclusion must cite one or more reports.

The reviewer should not judge whether the conclusion is correct.

It should answer:

Did the synthesizer accurately represent the reports?
Did it invent anything?
Did it omit conflicting evidence?
Are unsupported conclusions clearly labelled?

If yes:

PASS

Otherwise:

FAIL

This keeps review objective.

For this specific project, I would create a new research folder with a narrow scope.

research/
    execution-engine-ui/

        README.md

        hypotheses/

        reports/

        synthesis/

        review/

        prototype/

The objective isn't "build UI."

It's

Determine whether an execution-engine frontend can be assembled primarily from existing components while preserving EDASES methodology.

The first research questions I'd commission are:

RQ1

Can existing graph frameworks represent engineering artefacts and their relationships without substantial customization?

RQ2

Can hierarchical statechart frameworks model independent artefact lifecycles?

RQ3

Can existing workflow engines be used as execution infrastructure without imposing workflow semantics that conflict with EDASES?

RQ4

Can a graph database naturally represent:

artefacts
versions
evidence
provenance
supersession
state

without excessive schema complexity?

RQ5

Can one frontend expose four distinct views over the same data?

execution
state
evidence
version history

RQ6

Can an agent recover a task using only artefact history rather than conversation history?

This is the research question I'd prioritize because it directly tests one of EDASES' core hypotheses.

Regarding OpenCode specifically, I would leverage its strengths rather than fight them. OpenCode's documentation encourages specialized subagents, child sessions, and hidden internal agents that can be invoked automatically, making it well suited to this style of orchestration.

Given your constraints:

Use your preferred orchestrator model only for planning, delegation, synthesis, and communication with you.
Use Zen subagents aggressively for bounded research tasks, web searches, source analysis, and prototype spikes, since token cost is not the limiting factor.
Optimize for wall-clock time by maximizing parallel research while keeping synthesis and review strictly serial.

I would also avoid giving subagents open-ended prompts like "research graph libraries." Instead, bound every task with a specific research question, success criteria, expected deliverable, and explicit instruction to stop once those are satisfied. That tends to reduce both elapsed time and report size, making the synthesis phase much more reliable.

One final suggestion: treat the orchestration process itself as an EDASES experiment. Record metrics such as elapsed time, number of parallel agents, reports produced, review failures, synthesis revisions, and the amount of context consumed by the orchestrator. If this becomes your standard methodology for conducting EDASES research, those measurements become evidence for improving the methodology itself rather than just this particular frontend investigation. Ж研Λ