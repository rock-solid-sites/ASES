# EDASES Research-Level Classification: Independent Review

## Context

We are developing **EDASES**, a research program concerned with designing a methodology and execution system for reliable AI-assisted software engineering.

The project deliberately separates three levels:

### 1. EDASES — Research

EDASES is the research layer. It asks what is fundamentally true about agentic software engineering, what properties a trustworthy system must preserve, what problems are genuinely novel, and what principles or invariants should govern the design.

This is the level of:

* fundamental research questions;
* hypotheses;
* architectural principles and invariants;
* boundaries of trust and authority;
* distinctions between human, model, methodology, and machine authority;
* determining which problems are genuinely AI-agent-specific versus inherited from other fields;
* empirical programs intended to establish or falsify general claims.

EDASES should not prematurely commit to a particular implementation.

### 2. ASES — Methodology

ASES (Agentic Software Engineering System) is the methodology derived from the EDASES research.

It describes how software engineering should be conducted when AI agents are participants in the process: how work is represented, authorized, decomposed, executed, reviewed, verified, integrated, evidenced, and completed.

This is the level of:

* work and dependency models;
* agent roles and authority;
* evidence and verification protocols;
* review methodology;
* context management;
* integration methodology;
* model selection and reviewer diversity;
* recovery policies;
* human/model interaction;
* rules governing what agents may and may not do.

ASES should express methodology independently of the particular runtime used to implement it.

### 3. Execution Engine — Tooling / Runtime

The Execution Engine is the concrete system that mechanically enforces the ASES methodology.

It is responsible for things such as:

* state machines;
* durable execution state;
* process/session management;
* scheduling and queues;
* capability enforcement;
* hooks and gates;
* persistence;
* restart and recovery;
* Git/worktree operations;
* integration machinery;
* event streams;
* resource limits;
* deterministic enforcement.

The Execution Engine should not become the place where unresolved methodological or research questions are silently decided.

## Project Goal

The broader goal is to develop a system through which AI agents can produce software that is **verifiably trustworthy**, while reducing the major failure modes of current agentic software development.

The project is particularly concerned with:

* context loss;
* knowledge loss;
* reasoning loss;
* assumption drift;
* architectural amnesia;
* agents exceeding intended scope;
* agents incorrectly declaring completion;
* unreliable orchestration;
* state divergence;
* excessive token expenditure on coordination;
* inability to recover safely from failures;
* insufficient independent verification;
* and the difficulty of establishing trustworthy software outcomes when the workers themselves are probabilistic.

A central design principle emerging from the research is that **agents should not be trusted with authority that can instead be mechanically enforced by the surrounding system**. At the same time, we do not want to reinvent mature distributed-systems machinery unnecessarily.

The three-level EDASES → ASES → Execution distinction exists partly to keep these concerns at the correct abstraction level.

---

# Research Context

Recent research into Steve Yegge's Gas Town, its successor Gas City, and related systems produced a number of explicit research questions.

The Gas Town analysis identified several recurring architectural observations:

* work must outlive the agent session;
* executable state should imply permitted next actions;
* agents should not be responsible for enforcing properties that infrastructure can enforce;
* orchestration should not consume unnecessary model tokens;
* assignment, execution, and completion are distinct facts;
* state should have an authoritative representation;
* completion should require external evidence rather than self-report;
* recovery should be bounded and idempotent;
* pathological work-graph expansion is a real failure mode;
* process liveness does not imply work progress;
* supervision of agents by other agents creates recursive failure modes.

Gas City subsequently simplified some of Gas Town's machinery and introduced ideas around execution identity, scatter/gather policies, typed dispositions, and agent interfaces.

This research has also connected to earlier EDASES work involving Crosslink, execution state, liveness, RPC/RCP-style boundaries, model capability matrices, context hydration, and durable state.

We now have a collection of open questions. The purpose of this exercise is **not** to decide their answers. It is to determine how they should be organized across the three EDASES/ASES/Execution levels.

---

# Open Research Questions

## A. Authority Boundary Comparison

How do different agent systems constrain agent authority over:

* the work graph;
* execution state;
* assignment;
* verification;
* completion;
* and system configuration?

Which failures are prevented mechanically versus merely discouraged through prompts?

A useful decomposition may include:

* Graph Authority;
* Execution Authority;
* Verification Authority;
* Completion Authority;
* Enforcement Mechanism.

---

## B. Execution Trust

What should an agent system trust an agent to assert?

In particular:

* Can an agent's completion claim ever be authoritative?
* What constitutes execution evidence?
* What state can an agent establish directly?
* What must be established externally?
* How should verification transform an untrusted agent result into an accepted result?

This includes the broader question of how much authority should reside with the model versus the execution substrate.

---

## C. Execution/Substrate Restart Survivability

What state must survive an Execution Engine restart, and what state can legitimately be reconstructed?

How can the system avoid making the execution substrate a single point of catastrophic failure?

Relevant issues include:

* durable execution state;
* admission control;
* quota parking;
* doom-loop prevention;
* event attribution;
* restart recovery;
* reconciliation;
* state reconstruction.

---

## D. Merge / Integration Authority

How should independently produced changes be safely integrated when each change may be semantically correct in isolation but collectively incorrect?

This includes:

* Gas Town's Refinery;
* Bors-style batching;
* GitHub merge queues;
* stacked changes;
* integration testing;
* cross-cutting failures;
* and the distinction between semantic correctness of a work item and correctness of an integrated set of changes.

A deeper question is:

**Who has authority to declare that individually verified changes are collectively safe to integrate?**

---

## E. Agent Systems as Distributed Systems + Probabilistic Participants

Which coordination, recovery, scheduling, state, and liveness problems are ordinary distributed-systems problems?

Which become qualitatively different because the worker is an LLM?

Which are genuinely specific to AI-agent software engineering?

A working hypothesis is:

> LLM agent systems resemble conventional distributed systems containing non-authoritative, probabilistic participants whose claims about intent, state, progress, and completion cannot automatically be trusted.

This should be tested rather than assumed.

---

## F. Skeleton Factory / Minimum Viable Architecture

If we knew everything Gas Town discovered through its development and failure, but had to design a new system from scratch under ASES constraints, what is the **minimum architecture** we would build?

One proposed clean-room starting vocabulary is:

* Work Item;
* State Transition;
* Agent Session;
* Execution Evidence;
* Dependency;
* Artifact;
* Event;
* Policy.

The exercise should deliberately prohibit simply importing Gas Town terminology.

The purpose is to determine which complexity is fundamental and which was accidental or historical.

---

## G. Context Hydration vs. Context Injection

What is the minimum context required for an agent to execute complex work reliably?

How should the system prevent an agent from expanding a bounded task into an unbounded research or implementation exercise?

Potential mechanisms include:

* scoped file access;
* Crosslink query boundaries;
* explicit context contracts;
* pre-coding grounding;
* path allowlists;
* capability restrictions;
* context hydration policies.

The deeper question is whether **discoverability itself is an authority boundary**.

---

## H. Model Capability Matrix as Architectural Control

Can model capability differences be used as a reliability mechanism rather than merely as a cost/performance routing mechanism?

For example:

* one model performs construction;
* another performs independent review;
* another audits disagreements;
* reviewers are selected partly for complementary weaknesses.

The research question is whether heterogeneous model redundancy reduces correlated verification failures.

This includes the concept of a possible **verification quorum**.

---

## I. Substrate Failure and Self-Repair Limits

What happens when the system responsible for enforcing authority becomes inconsistent or unavailable?

For example:

* Crosslink state disagrees with Git;
* execution state disagrees with Crosslink;
* the Execution Engine itself is malfunctioning;
* an agent discovers the inconsistency.

Who is permitted to repair the authority substrate?

A particularly important hypothesis is:

> An agent should not become the ultimate authority for repairing the substrate that defines the agent's own authority.

This needs to be examined against realistic failure and recovery scenarios.

---

## J. Human Design vs. Model-Driven Architectural Emergence

How can EDASES distinguish deliberate architectural necessity from model-generated complexity?

This emerged from examining Gas Town's tendency to accumulate mechanisms in response to locally observed problems.

One proposed methodological response is **architectural compression**:

> Whenever a new mechanism is proposed, demonstrate why the requirement cannot be expressed as an existing state transition, deterministic mechanism, capability restriction, or simpler invariant.

The question is whether this should be a research hypothesis, an ASES methodological rule, or simply an architectural design discipline.

---

## K. Distributed-System Prior Art / Temporal / Kubernetes / MapReduce

Which parts of the EDASES problem have already been solved by established distributed-systems technologies?

In particular:

* durable workflows;
* scheduling;
* queues;
* timers;
* retries;
* reconciliation;
* state machines;
* event processing;
* resource isolation;
* recovery;
* orchestration.

Where do these systems stop being sufficient because their workers are trusted software components whereas EDASES workers are probabilistic agents?

The objective is to avoid reinventing mature solutions while identifying the genuinely novel layer.

---

## L. Liveness and Progress

How should an agent system distinguish:

* process existence;
* session health;
* tool activity;
* state transition;
* meaningful progress;
* and terminal completion?

How should stalls, infinite loops, repeated failures, and pathological non-progress be represented and detected?

What should be mechanically enforced versus inferred?

---

## M. Crosslink / Work Substrate

What should the durable work substrate represent?

Questions include:

* work items;
* identity;
* assignment;
* dependencies;
* parent/child relationships;
* lifecycle;
* evidence;
* results;
* review;
* completion;
* locks;
* worktrees;
* coordination.

Where should Crosslink's responsibilities end, and where should Execution Engine state begin?

---

## N. State / Durable Execution Boundary

What state is durable because it represents the enduring truth about work, and what state is ephemeral because it merely represents current execution?

This includes questions raised by Gas Town's distinction between durable Molecules and ephemeral Wisps, as well as earlier EDASES investigations into whether every work item should have its own database/state representation.

The deeper question is:

**What is the correct unit of durable state?**

---

## O. RPC / Process Boundary

Where should authority and state cross process boundaries?

What should be represented as:

* an RPC/API;
* an event;
* durable state;
* an ephemeral process;
* a plugin;
* or a direct local operation?

How should the system remain correct across process failure and restart?

This research should distinguish the methodological need for a boundary from the particular protocol or implementation chosen.

---

## P. Verification and Review Architecture

What kinds of review establish which kinds of confidence?

How should the system distinguish:

* builder self-check;
* semantic review;
* independent review;
* adversarial audit;
* integration verification;
* final acceptance?

Can verification be represented as explicit evidence and state rather than as an informal conversation between models?

---

# The Classification Exercise

Please independently analyze all of the questions above.

Do **not** assume that the provisional wording or grouping is correct.

For every question or closely related cluster, determine:

1. **Primary level**

   * EDASES
   * ASES
   * Execution

2. **Secondary level**, if the question genuinely spans layers.

3. **Whether multiple questions should actually be combined.**

4. **Whether one apparently unified question should instead be decomposed across the three levels.**

5. **Whether the question is actually a duplicate or manifestation of another question.**

6. **Whether an important question is missing.**

7. **Whether the current formulation is at the wrong abstraction level.**

Do not force every item into a unique category. If the correct answer is that one underlying question has three distinct formulations, show that explicitly.

For example, a question such as “How do we establish trustworthy completion?” might legitimately decompose into:

* **EDASES:** What constitutes trustworthy completion?
* **ASES:** What methodology establishes it?
* **Execution:** What mechanisms enforce it?

That decomposition is preferable to arbitrarily assigning the entire question to one level.

---

# What We Are Trying to Learn

The central purpose of this exercise is **not to produce the correct taxonomy from one person's perspective**.

We are going to compare several independent analyses.

We therefore particularly want you to identify:

### Convergence

Which topics naturally fall into the same level?

Which questions appear to be manifestations of a deeper common problem?

### Divergence

Which classifications are genuinely ambiguous?

Where could reasonable researchers disagree about whether something belongs to EDASES, ASES, or Execution?

### Missing structure

Does the three-level model leave important questions without a natural home?

Does any level appear overloaded?

Are there apparent research questions that are actually cross-level transformations of the same underlying problem?

### Compression

Can the entire inventory be reduced to a smaller number of fundamental research tracks?

For example, it may turn out that several apparently separate questions are all consequences of one deeper question about **authority, trust, and evidence**.

Do not assume this example is correct; determine independently whether such compression is warranted.

---

# Important Constraint

Do not classify a question according to where it happens to be implemented today.

The purpose of the EDASES → ASES → Execution separation is precisely to distinguish:

**what is fundamentally true → what methodology follows from it → what machinery enforces the methodology.**

A question about a Rust state machine may therefore belong at the EDASES level if the actual research question is about the fundamental semantics of state and authority.

Conversely, a question about “agent trust” may belong at the Execution level if the research has already been settled and the remaining issue is purely mechanical enforcement.

Judge the abstraction level of the **actual question**, not its current implementation.

---

# Desired Output

Produce:

1. **Your proposed EDASES / ASES / Execution taxonomy.**
2. **The clusters you believe should be combined.**
3. **Questions that should be decomposed across multiple levels.**
4. **The most important missing research questions you identify.**
5. **Your proposed reduced set of fundamental research tracks.**
6. **The strongest argument you can make against the current three-level separation, if you think it has a weakness.**
7. **The areas where you expect independent researchers to disagree most strongly.**

Do not attempt to design the final EDASES architecture.

This is a classification and research-framing exercise. The objective is to determine whether the three-level EDASES → ASES → Execution model independently emerges when researchers examine the same body of open questions, and whether independent researchers identify similar underlying connections between those questions.
