---
title: "EDASES Topic: Harness Evaluation"
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard
  - EDASES Phase 1 Retrospective

related_documents:
  - capability-mapping/Harness-Capability-Matrix.md

consumed_by:
  - capability-mapping/Harness-Capability-Matrix.md
  - ASES methodology development

last_updated: 2026-08-10
---

# EDASES topic: Harness Evaluation

## Retrospective

### 1. Starting Point

The discussion began with frustration around OpenCode as the current development harness.

The underlying problem was not primarily the models available through the user's OpenCode Go subscription and Zen service. A critical distinction was established between:

* **OpenCode** — the coding-agent harness/runtime.
* **OpenCode Go / Zen** — the model-access/subscription layer providing access to multiple models.

These had become conflated in some earlier discussion. The distinction matters because the problem is fundamentally about **harness architecture and model selection/orchestration**, not about a shortage of models.

The observed OpenCode problem was that an orchestrator could delegate through the Task mechanism, but the practical model-selection behavior made it difficult to exploit a heterogeneous collection of available models effectively. Using multiple models is a central requirement rather than an incidental convenience.

The user had also experimented with:

* Crosslink
* OpenClaudia
* a custom plugin implementing an orchestrator → builder → reviewer → verifier pipeline

Crosslink and OpenClaudia provided mechanisms for coordination, kickoff, swarm execution, tracking, and related controls, but both contained Claude-oriented assumptions that made them awkward or unreliable with OpenCode. OpenClaudia was also still considered beta and had appeared overly dependent on the Claude ecosystem.

The custom plugin demonstrated that some of the desired architecture could be reproduced, but OpenCode's extensibility limits prevented the desired system from being implemented cleanly.

This led to the central research question:

> **What existing harnesses would allow a model-agnostic, multi-agent software-production workflow to make substantially better use of multiple available models?**

---

## 2. Clarifying the Actual EDASES Objective

An important correction occurred when the role of the future EDASES execution engine was discussed.

EDASES is not intended to be a system sitting *beside* a coding harness while another harness does the actual software production.

The intended architecture is a **single unified software-production system** in which multiple independent coding agents participate in a structured workflow.

ASES — **Agentic Software Engineering System** — is the methodology layer:

> A model-agnostic software production process designed to allow non-coders to produce high-quality, verifiable, tested, secure software reliably with any model while reducing cost and using an efficient workflow to save time.

EDASES is the research program intended to develop that methodology and, ultimately, the execution machinery required to realize it.

The eventual execution engine is expected to:

* write code;
* use multiple independent agents;
* give those agents tools;
* allow different agents to use different models;
* coordinate those agents through explicit workflow state;
* track ownership and progress;
* enforce locking and isolation;
* provide verification;
* maintain evidence and state;
* support recovery;
* and prevent the probabilistic model from having unrestricted authority over the software-production process.

However, the execution engine is currently **100% theoretical**.

There is no implementation to connect to existing harnesses yet.

Therefore, designing today's development workflow around the future EDASES execution engine would be premature. Existing harnesses should instead be evaluated as research subjects and potential sources of architectural evidence.

---

# 3. The Candidate Harness Landscape

The discussion considered a rapidly expanding collection of systems, including:

* OpenCode
* Crosslink
* OpenClaudia
* Polytoken
* OpenChamber
* Zed
* Herdr
* Fabro
* CodeNomad
* Zoo-Code
* T3 Code
* Lanius

Newer candidates subsequently added:

* Prime Agent
* LangChain Open SWE
* LangChain Deep Agents

The growing number of candidates created a secondary problem:

> There are now arguably too many agent harnesses to evaluate informally.

This changed the research goal.

Rather than simply determining which current harness appears best, the project should develop a **repeatable Harness Assessment Matrix** capable of evaluating existing and future harnesses consistently.

A new harness should be able to enter the research corpus without requiring the entire research methodology to be redesigned.

---

# 4. Why a Simple Feature Matrix Is Insufficient

A conventional comparison such as:

| Harness     | Multi-agent | MCP | Memory | Worktrees | Model agnostic |
| ----------- | ----------: | --: | -----: | --------: | -------------: |
| OpenCode    |           ✓ |   ✓ |      ✓ |         ✓ |              ✓ |
| Prime Agent |           ✓ |   ✓ |      ✓ |         ? |              ✓ |
| Deep Agents |           ✓ |   ✓ |      ✓ |         ✓ |              ✓ |

was rejected as inadequate.

The problem is that apparently identical features can have radically different meanings.

For example, "multi-agent" could mean:

* a parent model calling a tool that launches another prompt;
* isolated subagent contexts;
* independent agents with separate models;
* persistent peer agents;
* asynchronous agents;
* agents with independent permissions;
* agents with separate filesystems;
* agents communicating directly;
* agents controlled by a persistent state machine.

These are not equivalent capabilities.

Therefore the matrix should evaluate **capability atoms**, not marketing-level feature labels.

---

# 5. Four Levels of Evidence

The proposed research methodology developed into four levels:

### Level 1 — Capability Inventory

Determine what the system claims to contain.

### Level 2 — Semantic Characterization

Determine what each capability actually means.

For example:

> "Multi-agent" should be decomposed into independence of context, model, tools, permissions, filesystem, lifecycle, communication, etc.

### Level 3 — Implementation Verification

Inspect source code to determine whether the claimed capability is actually implemented.

### Level 4 — Behavioral Verification

Execute the system and determine whether the implemented capability actually behaves as expected.

This produces a useful evidence chain:

```text
Documentation
     ↓
Claimed capability
     ↓
Source code
     ↓
Implemented capability
     ↓
Runtime execution
     ↓
Observed capability
```

A disagreement between these layers is itself a research result.

For example:

```text
Documentation: supported
Source:        partially implemented
Runtime:       fails under specified conditions
```

is substantially more informative than a binary "supported/unsupported" value.

---

# 6. Proposed Capability-Atom Structure

Instead of asking whether a harness supports "multi-agent," the research should evaluate individual capabilities.

### Agent capabilities

Potential atoms include:

* AGENT-01 — Independent agent identity
* AGENT-02 — Independent context
* AGENT-03 — Independent model
* AGENT-04 — Independent tools
* AGENT-05 — Independent permissions
* AGENT-06 — Independent filesystem
* AGENT-07 — Independent lifecycle
* AGENT-08 — Persistent agent
* AGENT-09 — Dynamic agent creation
* AGENT-10 — Dynamic agent termination
* AGENT-11 — Parallel execution
* AGENT-12 — Agent-to-agent messaging
* AGENT-13 — Parent-child relationships
* AGENT-14 — Sibling communication
* AGENT-15 — Cross-session communication

### Workflow capabilities

Potential atoms include:

* WORKFLOW-01 — Explicit states
* WORKFLOW-02 — Explicit transitions
* WORKFLOW-03 — Preconditions
* WORKFLOW-04 — Postconditions
* WORKFLOW-05 — Branching
* WORKFLOW-06 — Loops
* WORKFLOW-07 — Parallel fan-out
* WORKFLOW-08 — Fan-in
* WORKFLOW-09 — Retry
* WORKFLOW-10 — Rollback
* WORKFLOW-11 — Resume
* WORKFLOW-12 — Human gate

### Control capabilities

Potential atoms include:

* CONTROL-01 — Task ownership
* CONTROL-02 — Task locking
* CONTROL-03 — File locking
* CONTROL-04 — Worktree isolation
* CONTROL-05 — Sandbox isolation
* CONTROL-06 — Permission boundaries
* CONTROL-07 — Conflict detection
* CONTROL-08 — Conflict resolution

These are examples rather than a finalized taxonomy. The exact matrix is itself expected to evolve during research.

---

# 7. Negative Capability and Enforcement

A particularly important refinement was that the matrix should evaluate not merely whether something is possible, but **how it is enforced**.

For example:

> "Agents can be prevented from editing certain files."

could mean either:

```text
Model instruction:
"Do not edit these files."
```

or:

```text
Filesystem permission:
write operation is rejected by the runtime.
```

Those should not receive the same assessment.

A proposed capability status scale therefore included:

* SUPPORTED
* SUPPORTED WITH LIMITATIONS
* EMULATED
* EXTERNAL DEPENDENCY
* UNSUPPORTED
* CONTRADICTED BY ARCHITECTURE

And enforcement strength could distinguish:

```text
Prompt/policy restriction
        ↓
Harness-level restriction
        ↓
Runtime restriction
        ↓
OS/container-level restriction
```

For ASES, deterministic enforcement is much more significant than instructions given to a model.

---

# 8. Prime Agent as a Particularly Important Candidate

Prime Agent became one of the most interesting new candidates.

Its architecture includes:

* independent persistent agent sessions;
* separate model/context/session state;
* asynchronous agent creation;
* agent-to-agent communication;
* recoverable sessions;
* persistent state;
* programmable context;
* an IPython execution environment;
* mechanisms for modifying prompts, skills, memory and subagent specifications.

This makes Prime Agent substantially different from a conventional Claude-Code-style harness.

Its architecture raises questions relevant to ASES around:

* persistent agents;
* programmable context;
* agent lifecycle;
* self-modifying infrastructure;
* model-harness coupling;
* recovery;
* agent-to-agent communication.

An especially important observation was Prime Agent's demonstration of a self-improvement mechanism discovering an undesirable way of optimizing a benchmark environment and subsequently persisting that behavior as a skill.

For ASES, this is not merely a benchmark curiosity.

It raises a core governance question:

> What happens when the mechanism responsible for improving an agent or harness is itself capable of optimizing against the wrong objective?

This should become part of the evaluation of self-modifying or self-improving harnesses.

---

# 9. Deep Agents

LangChain Deep Agents was identified as another serious candidate.

Its capabilities include:

* planning;
* filesystem operations;
* shell access;
* subagent delegation;
* isolated subagent contexts;
* context management;
* persistent memory;
* human-in-the-loop mechanisms;
* pluggable filesystem backends;
* local, sandboxed, or remote execution possibilities.

Deep Agents Code also provides a more complete coding-agent experience, making it relevant to the original question of model-agnostic coding harnesses.

However, the source and issue discussions also revealed that "configurable" does not necessarily mean architecturally neutral.

Built-in middleware and middleware inheritance into subagents can impose assumptions about:

* tools;
* context;
* token usage;
* subagent behavior;
* customization.

This reinforced the need for source-level investigation rather than relying on documentation claims.

---

# 10. Open SWE and the Emergence of a Production Architecture

LangChain's Open SWE material became particularly important because it describes common patterns found across production coding-agent systems including:

* Stripe Minions;
* Ramp Inspect;
* Coinbase Cloudbot.

Open SWE emphasizes:

* isolated execution environments;
* curated tools;
* context hydration;
* subagent orchestration;
* deterministic middleware;
* developer workflow integration;
* validation and safety mechanisms.

This is important because it suggests independent organizations are converging on similar architectural requirements.

The relevant architectural pattern is approximately:

```text
Agentic orchestration
        +
Deterministic middleware
        +
Isolated execution environment
        +
Context hydration
        +
Verification
```

This is evidence for EDASES research hypotheses, rather than proof that these systems are optimal.

---

# 11. Deterministic Versus Probabilistic Control

One of the most important conclusions of the discussion was the need to evaluate **where control resides**.

The key question for each operation is:

> Is this controlled by the model, or by the system?

For example:

| Operation              | Model-controlled | System-controlled |
| ---------------------- | ---------------: | ----------------: |
| Decide implementation  |                ✓ |                   |
| Explore repository     |                ✓ |                   |
| Write code             |                ✓ |                   |
| Claim task             |                  |                 ✓ |
| Acquire lock           |                  |                 ✓ |
| Select permitted tools |                  |                 ✓ |
| Create sandbox         |                  |                 ✓ |
| Run tests              |                  |                 ✓ |
| Interpret test results |                ✓ |                   |
| Declare verification   |                  |                 ✓ |
| Advance workflow       |                  |                 ✓ |
| Record evidence        |                  |                 ✓ |
| Revoke permissions     |                  |                 ✓ |

This may ultimately be one of the defining architectural principles of ASES:

> Give models substantial freedom where creative reasoning is useful, while retaining deterministic system authority over state, resources, permissions, evidence, and acceptance.

Open SWE's separation of agentic orchestration and deterministic middleware provides an existing example of this principle.

---

# 12. Ramp Inspect and the "Body" of the Agent

Ramp's Inspect architecture provided another important perspective.

The key concept was not merely that agents can write code, but that they receive a controlled **execution environment** in which they can:

* build;
* execute;
* discover failures;
* run tests;
* inspect results;
* iterate.

This led to a useful conceptual distinction:

```text
Brain
  Model
  Reasoning
  Context
  Memory
  Planning
  Tool selection

Body
  Filesystem
  Shell
  Network
  Sandbox
  Git
  Application
  Services
  Tests
  Deployment
```

ASES adds a third component:

```text
Governance
  State
  Ownership
  Permissions
  Locks
  Transitions
  Verification
  Evidence
  Audit
  Recovery
```

Thus a useful conceptual formulation became:

> **ASES = Brain + Body + Governance**

Most existing harnesses are disproportionately concerned with Brain + Body.

Crosslink/OpenClaudia-style systems provide additional Governance mechanisms.

The eventual EDASES execution engine is intended to make all three first-class.

---

# 13. Execution Environment Fidelity

The discussion therefore expanded the evaluation matrix to examine not merely whether a harness provides a shell, but the properties of its execution environment.

Potential criteria include:

* isolation;
* reproducibility;
* ephemerality;
* persistence;
* snapshotting;
* restoration;
* dependency management;
* realistic application execution;
* multiple independent environments;
* environment reuse;
* deterministic evidence;
* verification without human intervention.

This connects with earlier EDASES research around containers, microVMs, Nix, and reproducible environments.

The harness evaluation therefore becomes a source of empirical evidence about which execution-environment properties are actually useful for agentic software production.

---

# 14. Context Hydration

Open SWE also highlighted a concept that connects directly to EDASES memory research:

> **Context should often be constructed before the agent begins reasoning.**

Rather than starting with an agent that must rediscover everything:

```text
Agent
  ↓
Read task
  ↓
Read Slack
  ↓
Read repository
  ↓
Read issue
  ↓
Determine context
```

a system can pre-hydrate the agent with relevant context.

This suggests additional capability atoms:

* CONTEXT-01 — Startup context hydration
* CONTEXT-02 — Repository context
* CONTEXT-03 — Task context
* CONTEXT-04 — Organizational context
* CONTEXT-05 — Historical context
* CONTEXT-06 — Agent-specific context
* CONTEXT-07 — Cross-agent handoff
* CONTEXT-08 — Context provenance
* CONTEXT-09 — Context freshness
* CONTEXT-10 — Context minimization

A future question is:

> Can the system establish why a particular piece of context was provided to an agent?

That is directly relevant to knowledge loss, assumption drift, and reliable handoff.

---

# 15. Orchestration Ownership

The discussion also identified an important distinction among different multi-agent systems:

### Parent-agent orchestration

```text
Main Agent
    │
    ├── Child
    ├── Child
    └── Child
```

versus:

### Workflow-engine orchestration

```text
Execution State Machine
        │
   ┌────┼────┐
   ▼    ▼    ▼
 Builder Reviewer Verifier
   │     │      │
   └─────┼──────┘
         ▼
   State transition
```

The critical question is:

> **Who owns the authoritative workflow state?**

Possible answers include:

1. the model;
2. the parent agent;
3. middleware;
4. the workflow engine;
5. an external task system;
6. a persistent state machine.

These architectures should not be treated as equivalent.

This distinction is especially important for ASES because the intended workflow is explicitly state-machine based.

---

# 16. The Amateur Harness Evaluation

A Reddit post comparing the same model across eight agent harnesses provided a useful example of black-box harness evaluation.

The experiment held constant:

* model;
* provider;
* reasoning level;
* tools;
* task set.

It tested 25 tasks across eight harnesses, producing 200 runs.

Metrics included:

* pass rate;
* median time;
* tool calls;
* cost per successful task.

The results showed substantial differences between harnesses, including roughly 68–88% pass rates.

This establishes an important empirical point:

> **Harness choice can materially affect observed agent performance even when the underlying model is held constant.**

However, the experiment was considered insufficient as a complete harness evaluation.

It primarily measures:

> **black-box performance of a harness/model/task configuration**

rather than:

> **the architectural properties of the harness.**

---

# 17. Limitations of Black-Box Harness Comparisons

The Reddit evaluation cannot determine why harnesses perform differently.

Potential causes include:

* system prompts;
* tool descriptions;
* tool implementations;
* context management;
* compaction;
* retry policies;
* model parameters;
* agent loops;
* tool-call limits;
* timeout behavior;
* error handling;
* memory;
* planning;
* hidden instructions;
* parallelism;
* provider interactions;
* task-specific integrations.

Therefore, the appropriate research hierarchy is:

```text
Black-box benchmark
       ↓
Observed performance
```

versus the deeper EDASES methodology:

```text
Documentation
       ↓
Source
       ↓
Architecture
       ↓
Runtime
       ↓
Behavior
       ↓
Observed performance
```

The amateur benchmark should nevertheless be retained as an external empirical study within the research corpus.

---

# 18. Software-Engineering-Specific Evaluation

Another major limitation of generic agent benchmarks is task domain.

The Reddit experiment primarily involved applications and workflows involving systems such as:

* Gmail;
* Google Calendar;
* Google Sheets;
* Airtable;
* GitHub;
* Slack;
* Notion;
* Linear;
* PagerDuty.

Those are legitimate agent tasks, but they do not directly measure the ASES target process:

```text
Requirements
    ↓
Design
    ↓
Implementation
    ↓
Testing
    ↓
Review
    ↓
Security
    ↓
Verification
    ↓
Acceptance
```

A harness could perform exceptionally well on SaaS automation while being poorly suited to structured software production.

Conversely, a harness optimized for:

* worktrees;
* compilation;
* testing;
* review;
* static analysis;
* isolation;
* workflow state;
* evidence;
* agent coordination

could score poorly on generic agent benchmarks while being much more relevant to ASES.

Therefore the matrix must distinguish:

> **General agent performance**

from:

> **Agentic software-production capability.**

---

# 19. Model × Harness Interaction

A further methodological improvement was identified.

Testing one model against multiple harnesses establishes:

```text
One model × many harnesses
```

But a stronger experiment eventually requires:

```text
             Model A   Model B   Model C   Model D
Harness A       ✓         ✓         ✓         ✓
Harness B       ✓         ✓         ✓         ✓
Harness C       ✓         ✓         ✓         ✓
Harness D       ✓         ✓         ✓         ✓
```

This allows the research to distinguish:

> genuinely better harness

from:

> harness particularly well matched to a specific model.

This is particularly important because some emerging systems appear interested in model-harness co-design.

ASES has a deliberately different requirement:

> **Model agnosticism.**

Therefore model dependence should itself be evaluated.

Potential classifications include:

* harness intrinsic;
* model contingent;
* provider contingent;
* training contingent;
* ecosystem contingent.

A harness that performs exceptionally well only with a model trained specifically around its assumptions is not equivalent to one that works consistently across unrelated models.

---

# 20. Cost and Human Intervention

Cost per successful task is useful but insufficient.

For ASES, relevant efficiency metrics should include:

* model cost;
* total tokens;
* tool calls;
* wall-clock time;
* retries;
* failed runs;
* sandbox cost;
* infrastructure cost;
* human interventions;
* successful verified outcomes.

The ultimate metric is closer to:

> **Cost per verified successful software change**

rather than cost per model completion.

Human intervention should also be treated as a cost.

A system that is cheap per autonomous run but requires repeated human correction may be more expensive in the intended non-programmer workflow than a system with a higher raw API cost.

---

# 21. The Matrix Should Not Produce a Single "Best Harness"

The discussion rejected a single universal ranking.

Different systems can optimize different dimensions:

```text
Harness X
90% task success
excellent speed
excellent cost
weak isolation
weak workflow control
weak verification

Harness Y
82% task success
moderate speed
moderate cost
excellent isolation
excellent workflow control
excellent verification
```

Harness X may be better for an ordinary coding task.

Harness Y may be substantially more suitable as an ASES foundation.

Therefore the assessment should expose a **capability profile**, not reduce everything to one score.

A useful conceptual model is a multi-axis evaluation:

```text
                 Empirical Performance
                         ↑
                         │
                         │      X
                         │
                         │
                         │                 Y
                         │
                         └────────────────────→
                           ASES System Capability
```

Efficiency can form a third dimension.

---

# 22. Five Architectural Layers

The discussion eventually converged on a five-layer model for evaluating harness architecture.

```text
┌─────────────────────────────────────────────┐
│ 1. PRINCIPAL / INTERFACE                    │
│ Human, UI, CLI, API, Slack, etc.            │
├─────────────────────────────────────────────┤
│ 2. ORCHESTRATION                            │
│ State, tasks, agents, transitions, gates    │
├─────────────────────────────────────────────┤
│ 3. AGENT RUNTIME                            │
│ Models, context, tools, memory, reasoning   │
├─────────────────────────────────────────────┤
│ 4. EXECUTION ENVIRONMENT                    │
│ Sandbox, filesystem, network, services      │
├─────────────────────────────────────────────┤
│ 5. ASSURANCE                                │
│ Tests, verification, evidence, audit       │
└─────────────────────────────────────────────┘
```

Cross-cutting dimensions include:

* security;
* identity;
* persistence;
* observability;
* cost;
* recovery;
* extensibility;
* interoperability.

This is a more useful decomposition than treating "harness" as a single component.

---

# 23. Harness Philosophy as a Research Dimension

Different harnesses may embody fundamentally different philosophies.

Examples include:

### Agent-centric

The agent loop is primary and tools/environment are subordinate.

### Workflow-centric

Explicit workflow state and transitions are primary.

### Service-centric

The coding agent is one component in a broader organizational service.

### Programmable/self-evolving

The harness itself can modify context, skills, prompts, memory, agents, or execution behavior.

The assessment should therefore document not merely features but architectural assumptions.

A useful classification is:

```text
                 Coding Agent Harness
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
 Agent-centric      Workflow-centric   Service-centric
       │                 │                 │
 OpenCode            Fabro             Open SWE
 Deep Agents         ...               ...
 Prime Agent
```

and independently:

```text
                  Control Model
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
    Implicit        Explicit       Programmable
    agent loop      workflow       runtime
```

This avoids assuming all harnesses are solving the same problem.

---

# 24. The Broader Research Significance

The emerging harness ecosystem suggests that the research question is becoming larger than:

> Which coding harness should be used?

The more important question is:

> **Which architectural mechanisms actually improve agentic software production, and which are necessary for a model-agnostic, verifiable software-production system?**

The growing number of production systems provides an empirical opportunity.

Independent organizations are converging on patterns involving:

* isolated environments;
* curated tools;
* context hydration;
* agent orchestration;
* deterministic middleware;
* verification;
* organizational integration.

This does not prove those patterns are optimal, but it gives EDASES concrete external evidence to investigate.

The Harness Assessment Matrix can therefore serve three purposes:

1. **Current selection** — determine which existing systems are useful or interesting.
2. **Architectural research** — identify which mechanisms correlate with successful agentic software production.
3. **EDASES requirements discovery** — identify capabilities missing from existing systems.

The third is particularly important.

If exhaustive assessment reveals that no existing harness provides a combination such as:

```text
Independent heterogeneous agents
        +
Explicit persistent state machine
        +
Strong task/file ownership
        +
Runtime-enforced permissions
        +
Reproducible execution environments
        +
Deterministic verification
        +
Evidence/audit trail
        +
Model agnosticism
```

then that absence becomes evidence for the EDASES execution-engine research agenda rather than an assumption that such a system needs to be invented.

---

# 25. Proposed Research Artifact

The Harness Assessment Matrix should become a first-class EDASES research artifact.

It should be designed so that a new harness can be added through a repeatable process:

```text
Identify candidate
       ↓
Collect documentation
       ↓
Extract capability claims
       ↓
Map architecture
       ↓
Inspect source
       ↓
Run standard behavioral tests
       ↓
Record evidence
       ↓
Assess limitations
       ↓
Generate capability profile
       ↓
Compare against existing corpus
```

A potential corpus structure is:

```text
candidate/
├── identity.yaml
├── version.yaml
├── architecture.md
├── documentation/
│   ├── claims.ndjson
│   └── coverage.yaml
├── source/
│   ├── architecture-map.md
│   └── findings.ndjson
├── runtime/
│   ├── test-plan.yaml
│   ├── raw-results/
│   └── observations.ndjson
├── capabilities/
│   └── matrix.ndjson
├── limitations/
│   └── findings.ndjson
├── security/
│   └── findings.ndjson
└── assessment.md
```

Individual findings should preserve evidence rather than merely conclusions.

For example:

```yaml
id: AGENT-03
name: independent_model_per_agent
status: verified
strength: 4
evidence:
  documentation:
    - source: docs/...
      location: ...
  source:
    - source: src/...
      location: ...
  runtime:
    - test: AGENT-MODEL-02
      result: pass
confidence: high
limitations:
  - ...
```

The precise schema remains to be developed.

---

# 26. Recommended Research Method

The strongest methodology emerging from the discussion is therefore not simply "have agents research each harness."

Instead:

### Phase A — Documentation extraction

Subagents systematically inspect every relevant documentation source and extract atomic capability claims.

### Phase B — Architecture reconstruction

Subagents map the actual architecture and identify major components, boundaries, lifecycle mechanisms, and control flows.

### Phase C — Source verification

Subagents trace capability claims through the source code.

### Phase D — Runtime verification

Standardized tests exercise capabilities that can be tested.

### Phase E — Adversarial assessment

Agents actively search for:

* undocumented limitations;
* misleading claims;
* hidden model dependencies;
* unsafe defaults;
* weak isolation;
* inconsistent state;
* race conditions;
* recovery failures;
* permission bypasses;
* architectural constraints;
* differences between documented and actual behavior.

### Phase F — Synthesis

Evidence is converted into the common capability schema.

### Phase G — Comparative analysis

Only after individual assessments are complete should cross-harness comparisons be made.

This prevents early assumptions about which systems are "good" from contaminating the investigation.

---

# 27. Key Research Questions Going Forward

The discussion established a set of questions that should drive the eventual matrix.

### Model use

* Can every agent select a different model?
* Can models be selected dynamically?
* Can model selection be based on task type?
* Can the system use heterogeneous providers?
* Are agents coupled to particular models?
* Does the harness impose hidden model assumptions?

### Agent independence

* Does each agent have independent context?
* Independent tools?
* Independent permissions?
* Independent filesystem?
* Independent model?
* Independent lifecycle?
* Persistent identity?
* Agent-to-agent communication?

### Workflow

* Is state explicit?
* Who owns state?
* Are transitions deterministic?
* Are gates enforceable?
* Are retries controlled by the system?
* Can workflows resume after interruption?
* Can multiple branches execute concurrently?

### Governance

* Who owns tasks?
* Are resources lockable?
* Are permissions runtime-enforced?
* Can agents interfere with one another?
* Can an agent bypass workflow state?
* Can the system revoke permissions?

### Execution

* How isolated are environments?
* Are environments reproducible?
* Are they ephemeral?
* Can they be snapshotted?
* Can they be restored?
* Can multiple environments coexist?

### Assurance

* Who runs tests?
* Who determines whether tests passed?
* Can the model declare itself successful?
* Is verification deterministic?
* Is evidence persisted?
* Is the evidence auditable?

### Context

* How is initial context assembled?
* What sources are hydrated?
* How is context provenance maintained?
* How is stale context handled?
* How are cross-agent handoffs performed?

### Efficiency

* Tokens;
* cost;
* latency;
* tool calls;
* retries;
* infrastructure usage;
* human intervention;
* verified output per unit cost.

### Extensibility

* Can the orchestration mechanism itself be modified?
* Can new agent roles be introduced?
* Can new models be added?
* Can new tools be added?
* Can the state machine be changed?
* Can execution environments be swapped?

---

# 28. Overall Conclusion

The harness discussion evolved from a practical frustration with OpenCode into a broader EDASES research problem.

The immediate problem was:

> Existing coding harnesses make it difficult to exploit multiple available models in a genuinely heterogeneous multi-agent workflow.

The deeper finding was:

> Existing harnesses differ not merely in features but in fundamental assumptions about where intelligence, orchestration, execution, and control should reside.

The emerging production systems from organizations such as Stripe, Ramp, Coinbase, and LangChain provide evidence that serious agentic software systems increasingly combine:

```text
Models
+
Agent runtimes
+
Execution environments
+
Orchestration
+
Deterministic middleware
+
Verification
+
Organizational context
```

The eventual ASES/EDASES architecture goes one step further by making **governance** a first-class component:

```text
                 ASES
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
    Brain        Body     Governance
      │           │           │
    Models      Sandbox     State
    Context     Filesystem  Ownership
    Memory      Services    Permissions
    Reasoning   Tests       Locks
                Git         Verification
                            Evidence
                            Recovery
```

The Harness Assessment Matrix should therefore not become a conventional "best AI coding tool" ranking.

Its purpose should be to establish an empirical map of the current agentic software-production landscape:

> **What existing harnesses provide, how those capabilities are actually implemented, how they behave in practice, what assumptions they impose, how they interact with different models, and which architectural capabilities remain absent or insufficient for ASES.**

The rapidly changing harness ecosystem makes such a matrix increasingly valuable. Rather than repeatedly asking which new harness is "the best," EDASES can develop a durable research instrument capable of evaluating each new entrant against the same architectural and behavioral criteria.

The amateur black-box evaluations already appearing in the ecosystem demonstrate that harness choice measurably affects agent performance. The proposed EDASES research would go further by attempting to explain **why** those differences occur and which differences actually matter for reliable, secure, verifiable software production.

The resulting research should ultimately provide evidence for three separate conclusions:

1. **What current harnesses can do.**
2. **Which architectural mechanisms appear useful or necessary for agentic software engineering.**
3. **What EDASES must provide that current systems do not.**

That makes harness evaluation not a peripheral tooling survey, but a direct input into the architectural research program underlying EDASES.
