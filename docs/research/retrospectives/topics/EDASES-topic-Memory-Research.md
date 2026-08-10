---
title: "EDASES Topic: Memory Research"
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
  - knowledge-architecture-research/Knowledge Architecture Research Phase-1 draft 1.md

consumed_by:
  - ASES knowledge architecture
  - knowledge-architecture-research/

last_updated: 2026-08-10
---

# EDASES topic: Memory Research

**Date:** 2026-08-09
**Status:** Research retrospective
**Scope:** Crosslink, Letta, Redis, Trajectory, artifact persistence, latent model state, and heterogeneous-model coordination

---

## 1. Context

EDASES is investigating how non-programmers can safely and effectively use heterogeneous AI systems to engineer software.

The project's architecture distinguishes:

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

The execution engine is intended to maintain engineering state, preserve reasoning and evidence, coordinate heterogeneous AI capabilities, and mechanically enforce the methodology.

A central architectural principle is that **reasoning is the primary engineering artefact**, rather than source code or conversational history alone. The project also treats epistemic relationships—observations, assumptions, findings, decisions, challenges and validations—as first-class knowledge.

This created an important research question:

> How should engineering memory and state be represented and persisted when work is performed by multiple AI agents, models, and harnesses?

The initial implementation context was Crosslink, a CLI issue tracker being used as part of the project. The discussion began by investigating whether other technologies, particularly Letta and Redis, might provide better or complementary forms of memory.

---

# 2. Crosslink as the Starting Point

Crosslink was identified as doing substantially more than conventional issue tracking in the current EDASES workflow.

Its relevant functions include:

* persistent session memory
* issue and task tracking
* multi-agent coordination
* distributed locking
* shared knowledge pages
* Git synchronization
* swarm orchestration
* workflow hooks
* session handoffs
* task dependencies
* persistent engineering state

This made Crosslink a useful practical solution, but also obscured an architectural distinction.

Crosslink is fundamentally **workflow-oriented**.

Its primary object is an engineering task or issue, with persistent memory supporting the completion and coordination of that work.

EDASES, however, is interested in a broader object:

> persistent engineering reasoning and knowledge.

This led to the initial decomposition:

```text
Crosslink
    │
    ├── work tracking
    ├── task dependencies
    ├── coordination
    ├── session continuity
    └── workflow enforcement
```

Crosslink therefore appeared to be an implementation of only part of the execution-engine problem rather than necessarily being the correct long-term memory architecture.

---

# 3. Initial Comparison: Crosslink, Letta and Redis

The first comparison established that Letta and Redis should not be considered interchangeable replacements for Crosslink.

## Crosslink

Crosslink is primarily concerned with **engineering workflow and operational state**.

It answers questions such as:

* What work needs to be done?
* What depends on what?
* Which agent is handling it?
* What is the current status?
* What information is needed to continue the work?

## Redis

Redis was characterized as **infrastructure rather than a memory model**.

It can provide:

* fast shared state
* caching
* pub/sub
* streams
* coordination primitives
* vector/search capabilities depending on configuration

But Redis does not itself define what constitutes an agent memory or engineering knowledge.

Using Redis would therefore mean designing an EDASES-specific memory model on top of it.

The likely role is runtime infrastructure rather than canonical engineering memory.

## Letta

Letta is much more explicitly memory-oriented.

Its core abstraction is persistent agent memory, including mechanisms for retaining information across interactions.

This made Letta conceptually closer to the EDASES research problem, but an important distinction emerged:

> Letta's memory model is primarily centered around the agent, whereas EDASES is interested in memory belonging to the engineering process.

That distinction matters because EDASES intends to coordinate heterogeneous agents rather than make one particular agent the owner of project knowledge.

---

# 4. First Architectural Decomposition

The discussion produced an initial division of responsibilities:

```text
Crosslink
    → engineering workflow
    → issues
    → milestones
    → dependencies
    → coordination

Letta
    → agent memory
    → reasoning persistence
    → learned/derived context

Redis
    → high-speed runtime state
    → coordination infrastructure

Git
    → canonical artifacts
    → documentation
    → durable history

Execution Engine
    → orchestration
    → epistemic relationships
    → methodology enforcement
    → traceability
```

This led to an important reframing.

The question should not be:

> Which memory product should replace Crosslink?

It should be:

> What kinds of state does EDASES actually need to preserve, and which subsystem should own each kind?

That question became the foundation for the rest of the research.

---

# 5. Letta Trajectory

The next significant development was Letta's Trajectory project.

Trajectory was identified as substantially more relevant to EDASES than a simple agent-memory comparison suggested.

The important property is that Trajectory normalizes agent sessions from different harnesses into a common representation.

The work discussed included support for harnesses such as:

* Claude Code
* Codex
* Letta Code

The resulting representation captures experience such as:

```text
user request
    ↓
agent reasoning
    ↓
tool call
    ↓
tool result
    ↓
agent reasoning
    ↓
...
```

This suggested a new abstraction:

> **Trajectory is an experience representation rather than merely a memory store.**

That is significant for EDASES because the project is explicitly concerned with heterogeneous AI systems.

Instead of each harness producing an isolated conversational history:

```text
Claude Code history
Codex history
OpenCode history
Letta history
```

a normalized trajectory layer could potentially provide:

```text
                 Agent Experience
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     Harness A      Harness B      Harness C
        │              │              │
        └──────────────┴──────────────┘
                       │
                 normalized
                  trajectory
```

This creates a potential portability layer between agent execution and persistent memory.

---

# 6. Trajectory Versus Immutable Evidence

An important qualification emerged.

Trajectory should not automatically be treated as the canonical evidence record.

Trajectory optimizes experience for subsequent agent consumption. In the Letta work discussed, the representation is deliberately more compact and token-efficient than preserving every possible piece of execution metadata.

That creates a distinction:

```text
Immutable Evidence
        │
        ├── complete execution records
        ├── tool results
        ├── Git history
        └── original artifacts
                │
                ▼
          Trajectory
        normalized experience
                │
                ▼
        Memory / Reflection
```

Trajectory is therefore best understood as a **derived representation of experience**.

The canonical record should remain sufficiently complete that a derived trajectory can be reconstructed or audited when necessary.

This distinction is particularly important for EDASES because the methodology requires traceability and explicit epistemic relationships.

A compressed representation optimized for memory consumption is not necessarily sufficient as proof of what happened.

---

# 7. Trajectory → Memory

Letta's broader work suggested a pipeline roughly resembling:

```text
Trajectory
    │
    ▼
Experience
    │
    ▼
Reflection / "Dreaming"
    │
    ▼
Persistent Memory
    │
    ▼
Future Agent Work
```

This is different from simply storing conversation history.

The system can potentially distinguish:

* what happened
* what was learned from it
* what should be remembered
* what should be supplied to a future agent

This is much closer to the EDASES problem of preserving engineering knowledge across context loss.

It also suggests that memory formation itself should be treated as a process that can introduce errors.

Potential EDASES research questions include:

* Does memory formation preserve the important reasoning?
* Does it introduce assumption drift?
* Can derived memories be traced back to evidence?
* Can a future agent distinguish evidence from interpretation?
* Can useful experience survive a change of model or harness?

---

# 8. Epistemic Knowledge Is Still a Separate Layer

Even Letta's memory model does not fully solve the EDASES problem.

EDASES explicitly identifies relationships such as:

```text
Observation
    ↓
Finding
    ↓
Decision
    ↓
Implementation
    ↓
Validation
```

and:

```text
Assumption
    ↓
Challenge
    ↓
Evidence
    ↓
Validation / Revision
```

Neither Crosslink nor Redis directly represents these relationships.

Letta gets closer to semantic memory but does not automatically provide an EDASES epistemic model.

This led to a more complete hierarchy:

```text
Raw execution
      │
      ▼
Experience / trajectory
      │
      ▼
Memory
      │
      ▼
Epistemic knowledge
      │
      ▼
Engineering state
      │
      ▼
Artifacts
```

The reverse relationship is also important:

```text
Engineering claim
      │
      ▼
Evidence
      │
      ▼
Trajectory / execution
      │
      ▼
Original event / artifact
```

The ability to move backward through this chain is essential for trustworthy engineering.

---

# 9. Git and Artifact Persistence

A Reddit discussion was then introduced concerning an agent system that abandoned building a dedicated database for its agents and instead relied heavily on Git.

The relevant insight was not that databases are inherently unnecessary.

The useful principle was:

> Do not build a specialized database merely to reproduce capabilities that Git already provides well.

Git already provides strong persistence for:

* artifacts
* version history
* diffs
* attribution
* branching
* synchronization
* rollback
* human inspection

This is particularly compatible with EDASES's emphasis on explicit, inspectable engineering knowledge.

The resulting distinction was:

```text
Git
    → durable artifacts and canonical history

Memory system
    → derived semantic/contextual memory

Trajectory
    → normalized experience

Workflow system
    → execution state and coordination
```

This prevents the execution engine from accumulating a monolithic database whose purpose is simply to remember everything.

The broader architectural lesson is:

> **Persistence does not imply a database.**

Different forms of state can have different natural persistence mechanisms.

---

# 10. Three Levels of Persistence

The research then expanded the concept of memory into at least three distinct levels.

## 10.1 Artifact persistence

This is the most explicit and portable layer.

```text
Git
files
documentation
issues
artifacts
```

It answers:

> What was produced?

Properties:

* highly inspectable
* durable
* versionable
* diffable
* relatively model-independent

## 10.2 Experiential / semantic persistence

This includes:

```text
Trajectory
Letta
memory stores
knowledge structures
```

It answers:

> What did the agent experience, learn, or retain?

Properties:

* more semantically useful
* potentially more compact
* useful for future agent context
* potentially lossy
* requires careful provenance

## 10.3 Computational-state persistence

This includes:

```text
KV cache
hidden state
latent representations
```

It answers:

> What internal computational state can be transferred so that another model can continue without reconstructing the context?

Properties:

* potentially extremely high fidelity
* highly efficient when compatible
* opaque
* model-dependent
* currently difficult to transfer across heterogeneous models

This third category emerged from the KV-cache research discussed next.

---

# 11. Cross-Model KV-Cache Transfer

The arXiv paper discussed was a preliminary 2026 paper investigating cross-model KV-cache transfer through learned mappings.

The core concept is:

```text
Model A
    │
    ▼
KV Cache A
    │
    │ learned mapping
    ▼
KV Cache B
    │
    ▼
Model B
```

Normally, changing models requires the new model to process the context again.

If the internal KV representation can be transformed into the target model's representation, the target model can potentially continue from transferred state.

The paper reported substantial prefill-speed improvements in its tested compatible model pairs, but the experiments were limited and some model pairs failed to transfer well.

The discussion therefore treated this as a **promising experimental capability rather than a dependable persistence primitive**.

---

# 12. Model Compatibility Is the Central Limitation

The KV-cache work currently depends strongly on compatibility between source and target models.

The discussion emphasized that the technique should not be treated as a general solution to heterogeneous-model memory.

At present, it is closer to:

```text
Model family A
      │
      ▼
transfer mapping
      │
      ▼
Compatible model family B
```

rather than:

```text
Any model
    │
    ▼
universal transferable internal state
    │
    ▼
Any other model
```

This creates an important contrast with Trajectory.

Trajectory attempts to preserve experience at an explicit, normalized layer.

KV transfer attempts to preserve implicit computational state.

Thus:

```text
Trajectory
    → more portable
    → more inspectable
    → less complete as raw internal state

KV cache
    → less portable
    → opaque
    → potentially much higher-fidelity continuation
```

EDASES should therefore not depend on KV transfer, but should track it as a potentially important future capability.

---

# 13. A Broader Memory Hierarchy

The combination of the above research suggested a useful conceptual hierarchy:

```text
                    Engineering Knowledge
                            │
                 decisions / findings /
                 assumptions / validation
                            ▲
                            │
                    Experience
                            │
              trajectories / tool results /
                    reasoning records
                            ▲
                            │
                      Context
                            │
                 tokens / KV cache /
                  internal model state
```

The lower levels contain more implicit information but are less portable and less inspectable.

The higher levels are more abstract and portable but necessarily discard some information.

This creates a fundamental trade-off:

> **The more faithfully a system preserves internal state, the less portable and inspectable that state tends to become.**

Conversely:

> **The more portable and inspectable the representation becomes, the more transformation and information loss may occur.**

This is potentially an important research dimension for EDASES.

---

# 14. Sakana Fugu and Multi-Model Coordination

The discussion then introduced Sakana AI's Fugu work and the research papers associated with it, particularly TRINITY and Conductor.

These systems are relevant not primarily because they are memory systems, but because they investigate **learned coordination of heterogeneous AI models**.

The traditional orchestration model is:

```text
Planner
   ↓
Coder
   ↓
Reviewer
```

with the topology and roles defined by humans.

The Fugu/TRINITY/Conductor direction instead attempts to learn:

* which agents to use
* which roles they should perform
* how agents should communicate
* what communication topology to use
* how to combine their outputs

This can be represented as:

```text
Task
  │
  ▼
Learned Coordinator
  │
  ├── selects models
  ├── assigns roles
  ├── establishes communication
  └── synthesizes results
```

This is highly relevant to EDASES because the project explicitly seeks effective coordination of heterogeneous AI capabilities.

---

# 15. Learned Orchestration Versus ASES

The research exposed a significant methodological tension.

The current EDASES direction emphasizes:

* explicit methodology
* bounded delegation
* execution state
* verification
* mechanical enforcement
* traceability

Learned orchestration instead looks like:

```text
Task
  ↓
Learned policy
  ↓
Emergent delegation
  ↓
Emergent communication
  ↓
Result
```

This does not necessarily mean one approach must replace the other.

Instead, learned orchestration can be treated as an **alternative execution policy** operating within the constraints of an EDASES execution engine.

A possible architecture is:

```text
             ASES Execution Engine
                     │
          ┌──────────┴──────────┐
          │                     │
   Hard methodology       Policy layer
     guarantees               │
          │             ┌──────┴──────┐
          │             │             │
          │         Explicit       Learned
          │         policy         policy
          │             │             │
          │         Crosslink     Fugu/etc.
          │
          └─────────────┬─────────────┘
                        │
                   Model pool
```

The execution engine would retain ownership of invariants such as permissions, evidence, state transitions, and methodological gates.

The orchestration policy would determine how permitted work is allocated among available capabilities.

This would allow EDASES to evaluate learned coordination without making a learned external system the authority over the methodology.

---

# 16. The Training-Budget Constraint

A critical constraint was then identified:

> **EDASES does not have the budget to train its own coordination model.**

This materially changes the practical interpretation of Fugu, TRINITY and Conductor.

TRINITY and Conductor demonstrate that learned coordination can be trained, but reproducing that training process requires substantial repeated model inference and/or reinforcement-learning or evolutionary optimization infrastructure.

Conductor in particular involves a trained coordinator model rather than merely a runtime prompt.

Therefore, the following is not currently a realistic EDASES implementation path:

```text
Train EDASES coordinator
        ↓
RL / evolutionary optimization
        ↓
Learn orchestration policy
```

Likewise, reproducing Sakana's training experiments is not currently a sensible project dependency.

The research remains valuable, but primarily as evidence about what learned orchestration can achieve.

---

# 17. Pretrained Coordinators Are a Different Question

The budget constraint does not eliminate learned orchestration entirely.

A pretrained coordinator could theoretically be consumed as an external capability:

```text
ASES execution engine
        │
        ▼
pretrained coordinator
        │
        ▼
heterogeneous model pool
```

This avoids the cost of training the coordinator ourselves.

However, this introduces another EDASES concern:

> If an external learned coordinator decides how engineering work should be performed, who controls the methodology?

A system such as Fugu may determine:

* which models to invoke
* how many agents to use
* what roles they receive
* how they communicate
* how their results are combined

That means the external coordinator effectively owns part of the execution policy.

This could conflict with EDASES's goal of mechanically executing ASES rather than allowing implementation technologies to redefine the methodology.

Therefore, learned coordinators are better treated as **pluggable orchestration policies or experimental capabilities**, not as the foundational authority of the execution engine.

---

# 18. Implications for the Model Capability Matrix

The Fugu/TRINITY/Conductor work also challenged a simplistic interpretation of model capability.

A static capability matrix might say:

```text
Model A → coding
Model B → reasoning
Model C → verification
```

Learned orchestration suggests that capability may instead be contextual:

```text
Model A
    → good at X
    → poor at Y
    → good at Z after context from B

Model B
    → useful for verification after A
    → useful for planning under another topology
```

Therefore, useful capability is potentially a function of:

```text
model
+ task
+ context
+ role
+ interaction
+ preceding agent outputs
```

This does not invalidate the planned EDASES model capability matrix.

Instead, it suggests that the matrix may eventually need to distinguish **intrinsic capability** from **capability in a particular orchestration context**.

This remains a research issue rather than a settled design.

---

# 19. Emerging Architectural Model

By the end of the discussion, the various technologies could be organized into a more coherent architecture:

```text
                         EDASES
                            │
                 Engineering Knowledge
                            │
                 ┌──────────┴──────────┐
                 │                     │
          Durable Evidence        Derived Memory
                 │                     │
                Git              Letta / memory
                 │                     │
                 └──────────┬──────────┘
                            │
                       Experience
                            │
                       Trajectory
                            │
                            ▼
                    Execution Engine
                            │
             ┌──────────────┼──────────────┐
             │              │              │
        Work State     Methodology    Orchestration
             │              │              │
        Crosslink       ASES rules     pluggable policy
                                            │
                                  ┌─────────┴─────────┐
                                  │                   │
                              Explicit            Learned
                              policy              policy
                                  │                   │
                             existing            Fugu-like
                             approach             systems
                                  │
                                  └─────────┬─────────┘
                                            │
                                      Model pool
                                            │
                              ┌─────────────┼─────────────┐
                              │             │             │
                           Model A       Model B       Model C
```

Redis remains a possible infrastructure component for fast shared runtime state and coordination, but it does not define the conceptual memory model.

KV-cache transfer sits below this architecture as a model-dependent optimization:

```text
Model A
   │
   ▼
KV state
   │
   ▼
compatible Model B
```

It should not be treated as the canonical memory mechanism.

---

# 20. Key Research Conclusions

Several conclusions emerged from the discussion.

## 20.1 "Memory" is not one problem

The original Crosslink-versus-Letta question was too coarse.

EDASES potentially needs to preserve several fundamentally different things:

1. **Artifacts**
2. **Engineering workflow state**
3. **Agent experience**
4. **Derived semantic memory**
5. **Epistemic knowledge**
6. **Latent computational state**

These should not automatically share one storage mechanism.

---

## 20.2 Crosslink is not necessarily wrong; it may simply be too broad a foundation

Crosslink is useful because it provides workflow and coordination capabilities.

The research does not establish that Crosslink should be removed.

Instead, it suggests that Crosslink may be only one subsystem of a larger execution architecture.

The important question is which of its current responsibilities should remain there.

---

## 20.3 Git is an important part of the memory architecture

Git should not be dismissed as merely source-code version control.

For EDASES it can potentially serve as durable, inspectable persistence for engineering artifacts and canonical knowledge.

A specialized memory database should not duplicate capabilities Git already provides well.

---

## 20.4 Trajectory may be an important missing abstraction

Trajectory introduces the possibility of a standardized **experience layer** between raw agent execution and persistent memory.

This is particularly valuable for EDASES because heterogeneous AI systems and harnesses are fundamental to the project.

The concept is:

```text
different harnesses
       ↓
normalized experience
       ↓
memory / analysis
```

This may ultimately be more architecturally important than Letta itself.

---

## 20.5 Letta is potentially a memory consumer rather than the canonical knowledge system

Letta can potentially consume trajectories and turn experience into useful persistent context.

That does not mean Letta should own the project's canonical engineering knowledge.

EDASES still needs explicit epistemic relationships and provenance.

---

## 20.6 KV transfer represents a fundamentally different kind of persistence

KV-cache transfer suggests that future systems may preserve not just explicit knowledge but portions of the model's internal computational state.

However, current research is model-dependent and preliminary.

It is therefore an experimental capability, not an EDASES architectural dependency.

---

## 20.7 Learned orchestration is a research variable, not currently an implementation foundation

Fugu, TRINITY and Conductor provide evidence that orchestration itself can be learned.

However:

* reproducing their training is beyond the project's current budget
* external learned coordinators introduce methodological-control concerns
* the execution engine should retain ownership of hard guarantees

The appropriate architectural abstraction is therefore a **pluggable orchestration policy**.

---

# 21. Resulting Research Questions

The discussion produced a set of research questions that appear more valuable than a simple technology comparison.

### Memory and persistence

* What information must survive an agent context reset?
* What information must survive a model change?
* What information must survive a harness change?
* What information must remain inspectable by a human?
* What information must be reconstructible from evidence?
* What can safely be derived rather than canonically stored?

### Trajectory

* Can a normalized trajectory provide sufficient cross-harness continuity?
* What information is lost during trajectory normalization?
* Can trajectory-derived memories be traced back to original evidence?
* How reliably can memory formation preserve engineering reasoning?

### Epistemic knowledge

* How should observations, assumptions, findings, decisions and validations be represented?
* Can memory systems preserve those relationships rather than merely preserving text?
* What constitutes sufficient provenance for an engineering claim?

### Model portability

* How much engineering continuity can survive a model switch?
* How much can survive a harness switch?
* Can explicit memory compensate for loss of latent state?
* Can latent state ever become sufficiently portable to matter architecturally?

### Orchestration

* Is explicit methodology superior to learned orchestration for particular engineering tasks?
* Can learned orchestration operate safely inside explicit methodological constraints?
* How does model capability change depending on role, context and interaction topology?
* Should the capability matrix represent contextual capability rather than only model-level capability?

### Cost

* Which capabilities can be obtained through existing pretrained models?
* Which require training?
* Which require expensive inference experimentation?
* Which can be implemented with ordinary infrastructure?
* Which research directions should be excluded because their compute requirements exceed the project's resources?

---

# 22. Current Architectural Position

The discussion does **not** establish a final memory architecture.

It does establish a stronger working hypothesis:

> EDASES should probably not have a single "memory system."

Instead, memory should be treated as a set of persistence layers with different guarantees.

A provisional model is:

```text
                 Canonical Knowledge
                         │
                   epistemic model
                         │
              ┌──────────┴──────────┐
              │                     │
        Durable Evidence       Derived Memory
              │                     │
             Git              Letta / similar
              │                     │
              └──────────┬──────────┘
                         │
                    Experience
                         │
                    Trajectory
                         │
                         ▼
                 Execution Engine
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      Work State     ASES State    Policy Layer
          │              │              │
      Crosslink      methodology    pluggable
                                    orchestrator
```

Redis can potentially support the runtime beneath these layers.

KV-cache transfer remains a future optimization at the latent-state layer.

Learned coordinators such as Fugu remain experimental policy options rather than foundational components.

---

# 23. Most Important Shift in Thinking

The most significant outcome of this research was a shift away from asking:

> "What should EDASES use for memory?"

toward:

> **"What kinds of continuity does EDASES need, and what representation provides the appropriate trade-off between fidelity, portability, inspectability, and cost?"**

That reframing makes the technologies easier to evaluate.

Crosslink, Letta, Redis, Git, Trajectory, KV-cache transfer and learned coordinators are no longer competing answers to one question.

They are potential solutions to **different continuity problems**.

The remaining research task is therefore to define those continuity requirements precisely before selecting implementation technologies.
