# Proposal: EDASES Execution Engine — State-Gated Durable Agentic Execution

**Status:** Draft for adversarial review
**Purpose:** Establish and test the architectural hypotheses underlying a purpose-built EDASES Execution Engine before implementation decisions become entrenched.

---

## 1. Executive Summary

EDASES increasingly points toward the need for a dedicated **Execution Engine**: a durable software system that provides authoritative execution state, mechanically enforced state transitions, observability, and coordination for agentic software engineering.

The central hypothesis is that **explicit state gating should be the architectural foundation of the engine**. Agents should remain responsible for engineering judgment, planning, implementation, review, recovery decisions, and other activities that require reasoning. The engine should instead mechanically enforce the invariants that should not depend on an agent remembering to follow instructions.

The current proposal is to investigate a **focused Rust Execution Engine**, assembled from existing components wherever practical, rather than assuming that EDASES needs to implement scheduling, timers, queues, persistence, or other infrastructure itself.

However, the need for a bespoke engine is itself a hypothesis. A parallel research program should systematically evaluate existing software—regardless of implementation language—against the EDASES requirements. An existing system that provides the required semantics would invalidate the assumption that a new engine needs to be built.

The immediate objective is therefore **not to implement the engine**, but to determine whether this architectural model is correct, what its minimum viable semantics are, and whether existing software can provide them.

---

# 2. Why This Hypothesis Emerged

Several independent lines of investigation have converged on the same problem.

## 2.1 Durable state should outlive the runtime

Investigation of Deno's [Celld](https://github.com/denoland/celld) and the discussion surrounding it highlighted a principle increasingly relevant to EDASES:

> The runtime is not the durable thing; the state is.

An agent process, TUI session, worker, worktree, or execution host should be disposable. The logical work and its important state should survive those things.

This connects directly to existing EDASES concerns around context loss, knowledge loss, reasoning loss, assumption drift, and architectural amnesia.

## 2.2 Crosslink demonstrates the practical value of an execution-management layer

Crosslink currently provides several capabilities EDASES already relies upon:

* issue/work-item management;
* isolated Git worktrees;
* worker/session management;
* persistent state;
* coordination between parallel work;
* execution-related metadata.

However, this does not imply that Crosslink itself is the eventual Execution Engine.

Its capabilities may instead reveal requirements for the engine. Some may be retained through integration, some may be reimplemented, and some may turn out not to be necessary once the underlying architecture is clarified.

Crosslink is therefore both an existing implementation and a useful empirical source of requirements.

## 2.3 Actual agent failures demonstrate the need

Recent agent execution has provided concrete evidence rather than hypothetical failure scenarios.

Examples include:

* agents entering extended reasoning loops without producing work;
* agents exceeding nominal execution budgets while apparently remaining active;
* checkpointing requirements not being applied despite existing documentation;
* orchestration monitoring relying on terminal output rather than authoritative work state;
* failed recovery attempts where an agent reported that workers had been relaunched when they had not actually been relaunched;
* worker-distribution problems;
* queue management problems;
* timer and loop problems;
* recovery and supervision problems.

These failures demonstrate that documentation and agent discipline alone are insufficient.

At the same time, previous attempts at aggressive programmatic enforcement—particularly killing agents after arbitrary time limits—demonstrated the opposite problem: **mechanical enforcement can itself be wrong if it encodes an inappropriate policy.**

The engine therefore needs to enforce **state and invariants**, rather than simply enforcing simplistic operational policies.

---

# 3. Existing Agentic Control Model

EDASES already has a substantial agentic control structure.

The intended model is approximately:

```text
                    Operator
                       │
                       ▼
                 Orchestrator
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          Workers             Auditors
             │                   │
             ▼                   ▼
          Git/code          observations +
                              analysis
             │                   │
             └─────────┬─────────┘
                       ▼
                    Reviewers
                       │
                       ▼
                  Orchestrator
                       │
                       ▼
                    Operator
```

This should not be replaced.

The problem is that important parts of this system currently depend on agents correctly observing, interpreting, and enforcing operational rules.

The proposed Execution Engine provides a deterministic substrate underneath this system.

---

# 4. Central Architectural Hypothesis

## H1 — State gating should be the core primitive of the Execution Engine

**Hypothesis:**

> EDASES can make a significant class of agent-execution failures mechanically preventable by representing execution as an explicit state machine and permitting only valid actions and transitions for the current state.

The engine should therefore not merely record:

```text
status = RUNNING
```

It should define:

```text
state
  → permitted actions
  → permitted transitions
  → required evidence
  → applicable policies
```

For example:

```text
RUNNING
 ├── checkpoint       allowed
 ├── report progress  allowed
 ├── request pause    allowed
 ├── complete         allowed
 └── merge            prohibited
```

Where:

```text
REVIEW_REQUIRED
 ├── approve          allowed
 ├── reject           allowed
 ├── request revision allowed
 └── merge            prohibited
```

The engine therefore becomes authoritative over **what may happen**, rather than attempting to replace agents in deciding **what should happen**.

### Why this hypothesis developed

Existing failures show that important behavior currently depends on agents remembering and applying process rules.

Explicit state gates can turn some of those rules into system invariants.

---

# 5. H2 — Durable execution state should be independent of workers

**Hypothesis:**

> Logical engineering work, execution state, and worker/runtime instances can be represented separately such that a worker, agent session, worktree, or engine process can disappear without destroying the logical execution.

Conceptually:

```text
Work Item
    │
    └── Execution
          │
          ├── Worker A
          ├── Worker B
          └── Worker C
```

The workers are replaceable.

The execution is durable.

The work item is longer-lived still.

This allows recovery to mean:

> attach a new worker to the existing execution

rather than:

> create another task and attempt to reconstruct what happened.

### Acceptance criteria

* Worker termination does not destroy execution state.
* A replacement worker can be associated with an existing execution.
* Engine restart does not require an agent to reconstruct the execution from memory.
* Execution identity remains stable across recovery.

---

# 6. H3 — The engine should distinguish authoritative observations from agent judgment

EDASES already has a useful conceptual separation:

* **Observations** come from the execution environment.
* **Claims** are primarily represented through durable work artifacts such as Git commits.
* **Judgments** are made by reviewer/auditor agents against plans and the codebase.
* **Final authority** remains with the human Operator.

The Execution Engine should reinforce this rather than duplicate it.

It should mechanically know things such as:

```text
worker exists
worker exited
hook fired
commit exists
worktree exists
heartbeat arrived
timer expired
state transition occurred
```

It should not accept:

```text
"I relaunched the worker."
"I completed the task."
"I'm making progress."
```

as authoritative merely because an agent said so.

This is particularly important because an actual recovery attempt demonstrated that an agent could report an intended action as though it had occurred.

### Acceptance criteria

An agent claim cannot advance authoritative execution state unless the corresponding transition is supported by an observable engine event or explicitly authorized state transition.

---

# 7. H4 — State gating should preserve agentic judgment

**Hypothesis:**

> Mechanical enforcement should constrain execution without replacing the Orchestrator, auditor, reviewer, or Operator's ability to make context-dependent decisions.

This means the engine should not automatically encode policies such as:

```text
30 minutes elapsed → kill worker
```

Instead:

```text
RUNNING
   │
   ├── expected progress → continue
   │
   ├── stale progress → ATTENTION_REQUIRED
   │
   ├── expected duration exceeded → ATTENTION_REQUIRED
   │
   └── worker disappeared → WORKER_UNAVAILABLE
```

The Orchestrator or auditor can then determine what should happen.

The engine guarantees that the condition exists and is visible. It does not necessarily determine the remedy.

### Acceptance criteria

* Exceeding a nominal time budget does not inherently require termination.
* An Orchestrator can explicitly continue a legitimately long-running execution.
* A stalled execution cannot silently remain indistinguishable from a healthy one.
* Recovery decisions can remain agentic.
* Human intervention remains representable.

---

# 8. H5 — Temporal-class concerns can be reduced to a smaller set of required primitives

EDASES needs to address many of the problems that systems such as Temporal address:

* durable execution;
* scheduling;
* queues;
* timers;
* worker assignment;
* retries;
* recovery;
* liveness;
* execution history;
* replay;
* cancellation;
* idempotency.

However, this does not imply that EDASES needs a general-purpose workflow engine.

**Hypothesis:**

> The semantics required by EDASES can be decomposed into a relatively small set of primitives, some of which can be provided by existing components rather than implemented by the EDASES engine.

Potential primitives include:

```text
durable state
atomic state transitions
execution history
worker ownership/leases
durable scheduled actions
worker lifecycle
event observation
Git/worktree integration
```

The research should determine whether this decomposition is sufficient.

### Important distinction

The requirement is not:

> "EDASES needs a timer library."

It is:

> "A scheduled state transition must not silently disappear because the process responsible for waiting for it disappeared."

Likewise, the requirement is not:

> "EDASES needs a queue."

It is:

> "Work that has been scheduled must have durable ownership, visibility, and recovery semantics."

This distinction prevents feature-driven overengineering.

---

# 9. H6 — A focused Rust application is the appropriate implementation boundary

**Implementation hypothesis:**

> If a dedicated Execution Engine is required, it is most likely best implemented as a purpose-built Rust application integrating existing infrastructure rather than as a collection of prompts, scripts, or an extension of a general-purpose agent harness.

Rust is an explicit architectural consideration because the proposed engine requires:

* reliable concurrency;
* process supervision;
* filesystem/worktree operations;
* durable state management;
* event processing;
* integration with Git;
* integration with agent runtimes;
* long-running service behavior.

Crosslink also provides existing evidence that this class of coordination system can be implemented effectively in Rust.

However, this hypothesis does **not** mean that EDASES should implement general infrastructure itself.

The desired boundary is:

```text
                 Rust Execution Engine
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
     Owns              Integrates        Delegates
       │                  │                  │
 state machine       OpenCode hooks       Git
 state gates         Crosslink            SQLite
 EDASES policies     workers              Rust crates
 execution model     auditors             OS primitives
 engine API          reviewers
```

The engine should own EDASES-specific semantics and delegate generic infrastructure whenever appropriate.

---

# 10. H7 — Existing software must be actively investigated before committing to a bespoke engine

**Hypothesis:**

> Existing systems may already provide enough of the required execution semantics that building a new engine would be unnecessary.

This is a falsifiable assumption.

The research must therefore include systems written in **any language**, not merely Rust.

Potential comparison categories include:

* durable execution systems;
* workflow engines;
* job/task orchestration systems;
* agent orchestration systems;
* state-machine libraries;
* developer-agent execution systems;
* distributed worker systems;
* Git/worktree-aware coordination systems.

Relevant examples already identified include Celld, Crosslink, and Temporal, but the research should not be restricted to those systems.

### Language is not the selection criterion

If an ideal system is found in another language, possible outcomes include:

1. use it directly;
2. integrate with it;
3. wrap it;
4. reimplement the relevant semantics in Rust;
5. conclude that Rust is not actually necessary.

An existing system satisfying the requirements is a valid outcome of the research and would falsify the assumption that EDASES needs to build an execution engine.

---

# 11. Existing-System Research Method

Existing systems should be evaluated against the **same semantic requirements**, rather than compared by feature count.

A preliminary comparison matrix might include:

| Requirement                | System A | System B | System C | Native prototype |
| -------------------------- | -------- | -------- | -------- | ---------------- |
| Explicit state gates       |          |          |          |                  |
| Durable execution identity |          |          |          |                  |
| Worker replacement         |          |          |          |                  |
| Durable timers             |          |          |          |                  |
| Durable scheduling         |          |          |          |                  |
| Execution history          |          |          |          |                  |
| Replay                     |          |          |          |                  |
| Git/worktree integration   |          |          |          |                  |
| Agent hooks                |          |          |          |                  |
| Orchestrator telemetry     |          |          |          |                  |
| Mechanical enforcement     |          |          |          |                  |
| Agent-controlled recovery  |          |          |          |                  |
| Human intervention         |          |          |          |                  |

Each capability must be evaluated semantically.

For example, a system providing "timeouts" does not necessarily satisfy the EDASES requirement if its timeout semantics always terminate the worker.

The output of this research should classify each system as:

* satisfies;
* partially satisfies;
* requires adaptation;
* semantically incompatible;
* unnecessary for EDASES.

---

# 12. H8 — The minimum viable engine may be substantially smaller than a general workflow system

A major research question is whether many apparently separate execution capabilities collapse into a small set of primitives.

A minimal prototype should therefore deliberately avoid adopting sophisticated infrastructure initially.

A candidate baseline is:

```text
Rust
+
SQLite
+
Git
+
OS process primitives
+
OpenCode hooks
+
Crosslink integration
```

The prototype would implement only:

```text
work
execution
state
transition
event
timer
worker
checkpoint
```

Existing crates should then be introduced when the prototype demonstrates that a particular capability creates meaningful complexity, correctness risk, or concurrency problems.

This creates an empirical build-vs-buy threshold rather than assuming that every infrastructure problem needs a specialized dependency.

---

# 13. Failure-Driven Experimental Program

The existing failures provide the initial test suite.

## Experiment 1 — Infinite agent loop

**Scenario:** Worker remains alive but produces no meaningful progress.

**Expected result:**

```text
RUNNING → ATTENTION_REQUIRED
```

The engine identifies the condition without automatically terminating the worker.

---

## Experiment 2 — Legitimately long execution

**Scenario:** Worker exceeds an expected duration but continues producing valid progress.

**Expected result:**

The execution remains viable, while the exceeded expectation becomes visible to the Orchestrator/auditor.

The engine does not impose arbitrary termination.

---

## Experiment 3 — Missing checkpoint

**Scenario:** Worker fails to produce an expected checkpoint.

**Expected result:**

The execution enters an explicit state requiring attention or investigation.

---

## Experiment 4 — Worker death

**Scenario:** Worker process disappears.

**Expected result:**

The engine detects the worker loss independently of the agent's claims and preserves the logical execution.

---

## Experiment 5 — False recovery claim

**Scenario:** Agent claims a worker has been relaunched when no worker was actually created.

**Expected result:**

The authoritative execution state remains unchanged because the required observable transition never occurred.

---

## Experiment 6 — Engine restart

**Scenario:** Kill and restart the Execution Engine.

**Expected result:**

Execution state, scheduled actions, ownership, and relevant history are reconstructed without asking agents to recreate the state from context.

---

## Experiment 7 — Duplicate recovery

**Scenario:** A worker is lost and recovery is attempted more than once.

**Expected result:**

The engine prevents accidental creation of conflicting or duplicate logical executions.

---

## Experiment 8 — Concurrent workers

**Scenario:** Multiple workers attempt to operate on the same logical work.

**Expected result:**

Ownership/state gates prevent invalid concurrent transitions.

---

## Experiment 9 — Replay

**Scenario:** Reconstruct an execution after the fact.

**Expected result:**

The engine can explain how the execution reached its current state from durable history.

---

# 14. Acceptance Criteria

The architectural hypothesis should be considered supported only if a prototype demonstrates the following.

### State integrity

* Invalid state transitions are mechanically rejected.
* Execution state has a durable identity.
* Engine restart does not lose authoritative state.
* Agent claims cannot silently create state transitions.

### Worker lifecycle

* Workers are replaceable.
* Worker loss does not destroy logical work.
* Recovery can attach a new worker to an existing execution.
* Worker ownership is explicit and queryable.

### Liveness and monitoring

* Process activity can be distinguished from meaningful execution progress.
* Stale executions become explicit states or conditions.
* Duration expectations can trigger attention without mandatory termination.
* The Orchestrator can query authoritative execution state.

### Durable execution

* Scheduled actions survive engine restart.
* Timer state survives engine restart.
* Pending work survives restart.
* Recovery does not depend on reconstructing agent conversation context.
* Execution history can reconstruct current state.

### Agentic control

* The engine enforces invariants rather than replacing engineering judgment.
* Auditors can consume authoritative execution information.
* Reviewers can evaluate actual durable work against plans and state.
* Operator intervention remains possible.

### Implementation

* EDASES-specific logic remains distinguishable from generic infrastructure.
* Existing Rust crates or external components are used where they materially reduce complexity.
* The engine does not become an unnecessary reimplementation of a general-purpose workflow system.

---

# 15. What Would Falsify the Proposal?

The proposal should be considered falsified or substantially revised if research demonstrates any of the following.

### State gating is not the right abstraction

If the necessary execution rules cannot be represented cleanly as states, transitions, and gates without creating an unmanageable state machine.

### Mechanical enforcement provides little benefit

If adding authoritative state and gates does not materially reduce the failure modes or monitoring burden observed in current systems.

### Existing software already satisfies the model

If an existing system provides the required semantics with acceptable integration cost, there is no justification for creating a bespoke engine merely for architectural purity.

### The engine becomes a second Temporal

If implementing the required infrastructure causes the EDASES engine to accumulate a large independent implementation of:

* distributed scheduling;
* durable workflow replay;
* queues;
* timers;
* retries;
* worker supervision;
* persistence;
* distributed coordination;

then existing infrastructure should be reconsidered.

### Agentic control is excessively constrained

If legitimate engineering workflows frequently require bypassing or violating state gates, the state model is probably wrong or too rigid.

### The Rust boundary is counterproductive

If another implementation language or existing system provides the required semantics substantially more effectively, the Rust implementation hypothesis should be reconsidered.

---

# 16. Explicit Non-Goals

This proposal does **not** currently establish that EDASES should:

* use Temporal;
* replace Crosslink;
* replace OpenCode;
* automatically terminate stalled agents;
* use SQLite;
* use event sourcing;
* implement its own queue;
* implement its own scheduler;
* implement its own timer system;
* implement distributed execution;
* use Rust at the expense of a clearly superior existing system;
* automate engineering judgment;
* replace auditors, reviewers, the Orchestrator, or the human Operator.

These are research questions or implementation choices, not settled architectural decisions.

The stronger current commitment is to investigate whether **state-gated durable execution** is the correct foundation.

---

# 17. Proposed Architecture

The current provisional architecture is:

```text
                         EDASES
                           │
                          ASES
                           │
                           ▼
                 ┌───────────────────┐
                 │   Orchestrator    │
                 │                   │
                 │ planning          │
                 │ prioritization    │
                 │ judgment          │
                 │ recovery choices  │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Rust Execution    │
                 │ Engine            │
                 │                   │
                 │ state machine     │
                 │ state gates       │
                 │ durable state     │
                 │ execution history │
                 │ policy            │
                 │ worker lifecycle  │
                 │ observability     │
                 └─────────┬─────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Workers        Auditor       Reviewer
             │             │             │
             ▼             │             │
          OpenCode         │             │
             │             └──────┬──────┘
             ▼                    │
            Git ◄─────────────────┘
             │
             ▼
        durable artifacts
```

With infrastructure potentially delegated to:

```text
Rust crates
SQLite
Git
OpenCode hooks
Crosslink
OS process primitives
```

The exact boundary between these components remains a research result rather than a design assumption.

---

# 18. Research Sequence

The proposed research should proceed in this order:

```text
Observed failures
       │
       ▼
Required invariants
       │
       ▼
State-machine model
       │
       ├──────────────────┐
       ▼                  ▼
Existing-system       Minimal native
research              prototype
       │                  │
       └────────┬─────────┘
                ▼
       Semantic comparison
                │
                ▼
        Architecture decision
                │
       ┌────────┴────────┐
       ▼                 ▼
Existing system       Focused Rust
sufficient            engine
       │                 │
       ▼                 ▼
Integrate            Implement
```

This order is intended to prevent implementation enthusiasm from determining the architecture prematurely.

---

# 19. Questions for Adversarial Review

The review should focus on attacking the hypotheses rather than polishing the proposed design.

### Problem definition

1. Are the observed failures actually symptoms of the same architectural problem?
2. Are we overgeneralizing from today's agent failures?
3. What important failure classes are missing?

### State machine

4. Is explicit state gating really the correct architectural center?
5. What execution semantics cannot be represented cleanly as state transitions?
6. Where could state gating become excessive bureaucracy?
7. What should be state, and what should remain ordinary metadata?

### Agentic architecture

8. Are we drawing the correct boundary between deterministic enforcement and agentic judgment?
9. Which decisions should never be mechanically automated?
10. Is the Orchestrator receiving the right information from the engine?

### Durable execution

11. What Temporal-like guarantees does EDASES actually require?
12. Which can be reduced to simpler primitives?
13. Which apparently necessary features are actually unnecessary?

### Existing software

14. What existing systems should be added to the comparison?
15. Is there already a system that satisfies the model closely enough?
16. Are we underestimating the cost of adapting an existing system?
17. Are we overestimating the cost of writing a focused engine?

### Rust

18. Is Rust actually the right implementation boundary?
19. Which portions should be delegated to existing Rust crates?
20. At what complexity threshold should a general-purpose execution framework be preferred?

### Falsification

21. What experiment would most efficiently disprove this architecture?
22. What evidence would convince us **not** to build the engine?

---

# 20. Desired Outcome of This Review

The goal of adversarial review is **not approval of this architecture**.

The desired outcome is a sharper set of hypotheses and experiments that can determine:

1. whether state-gated execution is the correct foundation for EDASES;
2. what execution semantics are actually required;
3. whether those semantics can be provided by existing software;
4. which components should be adopted rather than implemented;
5. whether a focused Rust engine is justified;
6. and, if so, what the smallest useful engine actually needs to contain.

The strongest possible outcome of this research is therefore not necessarily "we should build the proposed engine."

It is:

> **We can demonstrate, with explicit evidence, why EDASES should either adopt an existing execution system or build a focused Rust state-gated Execution Engine—and precisely what that system must guarantee.**
