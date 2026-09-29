# Gemini 3.6 FLash Research Level Classification

Determining the natural home for each open research question requires evaluating where the *inquiry itself* resides—not where the concrete code will eventually sit.

```
                                      THE BOUNDARY CASCADE
                                      
    +---------------------------------------------------------------------------------------+
    | EDASES (Research Invariants)                                                          |
    | What properties are fundamentally true about probabilistic execution?                 |
    +---------------------------------------------------------------------------------------+
                                                |  Formulates Invariants
                                                v
    +---------------------------------------------------------------------------------------+
    | ASES (Methodology & Protocols)                                                        |
    | How do humans and agents execute software development given those invariants?         |
    +---------------------------------------------------------------------------------------+
                                                |  Specifies Rules & States
                                                v
    +---------------------------------------------------------------------------------------+
    | Execution Engine (Enforcement Runtime)                                                |
    | How does deterministic software mechanically enforce those rules?                      |
    +---------------------------------------------------------------------------------------+

```

| ID | Item Name | Primary Level | Secondary Level | Classification Rationale |
| --- | --- | --- | --- | --- |
| **A** | Authority Boundaries | **EDASES** | ASES / Exec | Establishing what must be deterministic vs. probabilistic is a fundamental theory of safety; ASES defines the roles; Execution enforces via capabilities. |
| **B** | Execution Trust | **EDASES** | ASES | Epistemological question: What constitutes proof when a worker is non-deterministic? ASES specifies the required evidence payload. |
| **C** | Substrate Survivability | **Execution** | ASES | Solved via traditional distributed systems (durable execution logs); ASES defines business recovery semantics. |
| **D** | Merge / Integration | **ASES** | EDASES / Exec | A process protocol for semantic isolation, batching, and integration verification. EDASES provides the invariant that unit pass $\neq$ system pass. |
| **E** | Distributed Systems + LLMs | **EDASES** | Execution | Fundamental boundary mapping: Distinguishing traditional distributed safety properties from non-deterministic agent failure modes. |
| **F** | Minimum Viable Architecture | **EDASES** | ASES | Information architecture exercise to isolate essential primitives from historical implementation artifacts. |
| **G** | Context Hydration vs. Injection | **ASES** | Execution | Information architecture for worker performance and scoping. ASES sets context contract schemas; Execution enforces filesystem boundaries. |
| **H** | Model Capability as Control | **ASES** | EDASES | Multi-agent protocol design leveraging complementary failure modes. EDASES investigates underlying correlation of LLM errors. |
| **I** | Substrate Failure & Repair | **EDASES** | Execution | Core security invariant: Workers cannot mutate their own authority substrate. Execution engine contains the boundary enforcement. |
| **J** | Architectural Compression | **EDASES** | Methodology | Epistemological control mechanism to prevent prompt-engineering patchworks from masquerading as system architecture. |
| **K** | Prior Art / Distributed Systems | **Execution** | EDASES | Infrastructure selection (Temporal, Kubernetes). Research boundary determines where Temporal ends and agent non-determinism begins. |
| **L** | Liveness and Progress | **ASES** | Execution | ASES defines semantic progress (state changes); Execution monitors process/liveness indicators (heartbeats, tool events). |
| **M** | Crosslink Work Substrate | **Execution** | ASES | Physical data store for work items, states, and dependencies. ASES defines the work item lifecycle graph. |
| **N** | State / Durable Boundary | **EDASES** | Execution | Theoretical distinction between business domain state (durable) and worker runtime stack (ephemeral). |
| **O** | RPC / Process Boundary | **Execution** | ASES | System architecture, transport protocol selection, binary isolation, and network topology. |
| **P** | Verification & Review | **ASES** | EDASES | Verification workflow: builder $\rightarrow$ reviewer $\rightarrow$ integration. EDASES defines mathematical/logical conditions for confidence. |

---

### Question Decomposition Across Levels

The most critical analytical failure in system design is forcing a complex, multi-layered problem into a single abstraction layer. Six core questions must be formally split across all three levels:

```
                  SPLIT CONCERNS: THE TRIPLE DECOMPOSITION
                  
+-------------------------------------------------------------------------+
| TRUST & EVIDENCE (Questions B & P)                                      |
|  * EDASES: Can an untrusted probabilistic node assert completion?       |
|  * ASES: What evidence schemas prove a state transition?                |
|  * Execution: How are sandbox test runs mechanically captured/hashed?   |
+-------------------------------------------------------------------------+
                                     |
+-------------------------------------------------------------------------+
| SUBSTRATE REPAIR (Question I)                                          |
|  * EDASES: Is self-repair of authority substrates mathematically safe?  |
|  * ASES: What are the escalation paths when state is inconsistent?      |
|  * Execution: How to isolate state stores behind read-only interfaces?  |
+-------------------------------------------------------------------------+
                                     |
+-------------------------------------------------------------------------+
| INTEGRATION & MERGES (Question D)                                       |
|  * EDASES: Is isolated semantic correctness compositional?              |
|  * ASES: How do merge queues handle speculative parallel builds?        |
|  * Execution: How are isolated Git worktrees provisioned and merged?    |
+-------------------------------------------------------------------------+

```

#### 1. Trust, Evidence, & Completion (Questions B & P)

* **EDASES:** Can an untrusted, non-deterministic worker ever assert its own completion, or must completion be an external property evaluated over an evidence trace?
* **ASES:** What evidence schemas (test runs, linters, static analysis, multi-model consensus) are required to transition a work item from `In-Progress` to `Verified`?
* **Execution Engine:** How does the runtime intercept, isolate, run, and cryptographically hash test outputs so an agent cannot tamper with the evidence pipeline?

#### 2. Authority Substrate Invariants & Repair (Question I)

* **EDASES:** Does permitting a worker to repair its own authority substrate introduce an irreducible loop where agent hallucinations corrupt system state? (Invariant: *An actor cannot adjust its own constraints*).
* **ASES:** What are the human-in-the-loop and out-of-band escalation protocols when the state store and execution environment diverge?
* **Execution Engine:** How does the runtime enforce strict filesystem and RPC permission boundaries so that an agent process physically lacks write access to Crosslink/system configuration databases?

#### 3. Compositional Correctness & Integration (Question D)

* **EDASES:** Is local semantic correctness ($S_A$ passes unit tests, $S_B$ passes unit tests) compositional ($S_A \cup S_B$ passes system invariants), or does agentic development introduce unique cross-cutting failure patterns?
* **ASES:** What review and batching topology (e.g., speculative batch integration, independent reviewer assignment) guarantees convergence of concurrent agent work streams?
* **Execution Engine:** How are isolated Git worktrees, container environments, and speculative integration branches physically provisioned, tested, and destroyed?

#### 4. System Liveness vs. Semantic Progress (Question L)

* **EDASES:** What is the theoretical definition of progress in non-deterministic code transformation, and how do we distinguish stochastic exploration from a livelock?
* **ASES:** What state-machine rules detect pathological task expansion or cycles, and what are the operational policies for terminating an uncooperative session?
* **Execution Engine:** What deterministic metrics (token counts, tool-call repeat counters, process execution timeouts, state transition timers) monitor execution state?

#### 5. Context Hydration & Scoping (Question G)

* **EDASES:** Is context discovery an authority boundary (i.e., does granting broad context access implicitly grant unauthorized scope expansion authority)?
* **ASES:** How are explicit "Context Contracts" declared for work items, defining the minimal sub-graph of codebase and documentation an agent is allowed to read?
* **Execution Engine:** How are virtual filesystems, path allowlists, and vector/graph boundaries mechanically enforced during tool execution?

#### 6. Architectural Compression (Question J)

* **EDASES:** What set of formal invariants guarantees that system complexity remains minimal and prevents the accretion of ad-hoc prompt patches?
* **ASES:** What criteria must a new workflow state or role satisfy before being accepted into the methodology, rather than being expressed via existing state transitions?
* **Execution Engine:** How are state-machine schemas compiled into strict, statically typed configurations that reject unmapped state additions at runtime?

---

### Proposed Reduced Fundamental Research Tracks

The original 16 questions (A–P) contain structural redundancy. They can be compressed into **four fundamental, orthogonal research tracks**.

```
                           THE 4 FUNDAMENTAL RESEARCH TRACKS
                           
   Track 1: Epistemology of Probabilistic Execution (Questions B, P, E)
   +-----------------------------------------------------------------------+
   | Evidence schemas, untrusted completion, non-deterministic failure     |
   +-----------------------------------------------------------------------+
                                       |
   Track 2: Authority Topology & Mechanical Isolation (Questions A, I, G)
   +-----------------------------------------------------------------------+
   | Capability boundaries, context allowlists, non-self-repairing substrate|
   +-----------------------------------------------------------------------+
                                       |
   Track 3: Integration Geometry & Work-Graph State (Questions D, M, N, F)
   +-----------------------------------------------------------------------+
   | Compositional correctness, durable vs. ephemeral state, Crosslink     |
   +-----------------------------------------------------------------------+
                                       |
   Track 4: Liveness, Recovery, & Substrate Separation (Questions C, K, L, O, H, J)
   +-----------------------------------------------------------------------+
   | Ephemeral workers, durable logs, deterministic liveness, compression  |
   +-----------------------------------------------------------------------+

```

#### Track 1: Epistemology & Evidence of Probabilistic Execution

* **Core Question:** *How do we derive deterministic software guarantees from untrusted, probabilistic workers?*
* **Includes Questions:** B (Trust), P (Verification), E (Probabilistic Distributed Systems).
* **Focus:** Defining formal evidence, separating execution from validation, establishing multi-agent verification quorums, and treating LLM outputs strictly as *untrusted proposals*.

#### Track 2: Authority Topology & Structural Isolation

* **Core Question:** *Where are the absolute boundaries between non-deterministic cognitive agents and deterministic systems?*
* **Includes Questions:** A (Authority Boundaries), I (Substrate Repair), G (Context Scoping).
* **Focus:** Proving that cognitive agents must be sandboxed actors operating within deterministic constraints. Ensuring agents can never alter their own authority rules, context boundaries, or execution state engines.

#### Track 3: Integration Geometry & Work-Graph State Mechanics

* **Core Question:** *How is software engineering work modeled, decomposed, and safely merged without knowledge loss or semantic divergence?*
* **Includes Questions:** D (Merge/Integration), M (Crosslink Substrate), N (Durable vs. Ephemeral State), F (Minimum Architecture).
* **Focus:** The structural schema of software engineering. Separating persistent business domain state (the evolving codebase and work graph) from transient workspace environments. Resolving compositional correctness across concurrent work streams.

#### Track 4: Runtime Liveness, Recovery, & Infrastructure Separation

* **Core Question:** *How do traditional durable-execution patterns map onto agent workloads without polluting methodology with implementation details?*
* **Includes Questions:** C (Restart Recovery), K (Prior Art / Temporal), L (Liveness vs. Progress), O (Process Boundaries), H (Model Routing), J (Architectural Compression).
* **Focus:** Harnessing distributed systems infrastructure (Temporal, queues, container sandboxes) to enforce ASES rules mechanically, while ensuring the execution runtime remains completely agnostic of the software engineering methodology it hosts.

---

### Critical Analysis of the Three-Level Separation

While the EDASES $\rightarrow$ ASES $\rightarrow$ Execution Engine model provides clear boundaries, it carries structural risks that must be actively managed:

```
               POTENTIAL BREAKDOWN OF THE THREE-LEVEL MODEL
               
 [EDASES]  (Risk: Ivory Tower Ivory-Towering)
    |      Formulates abstract theories detached from actual model capabilities.
    v
 [ASES]    (Risk: Leakage & Bloat)
    |      Attempts to fix model failures by inventing speculative sub-roles,
    v      over-complicating the methodology.
 [EXEC]    (Risk: Silent Coupling)
           Engineers bypass ASES/EDASES to fix practical bugs, embedding
           methodology implicitly into runtime code.

```

#### Key Weaknesses & Counter-Arguments

1. **The Model Boundary Leakage (The "Capabilities Leak")**
* *The Problem:* EDASES assumes a clean boundary where "research invariants" are decoupled from model mechanics. In practice, the boundary between EDASES and ASES shifts when model capabilities evolve.
* *Example:* If model reasoning context expands dramatically or hallucination rates drop on structured outputs, an ASES methodological requirement (e.g., breaking a task into 5 fine-grained sub-tasks with intermediate verification steps) may become an unnecessary performance bottleneck. The three-level separation risks building rigid abstractions over a rapidly moving probabilistic foundation.


2. **The Risk of Methodological Bloat (Prompt Engineering as Architecture)**
* *The Problem:* ASES sits dangerously between high-level theory and low-level code. There is a strong temptation for researchers to solve Execution-level failures or model-capability limits by inventing elaborate ASES protocols (e.g., multi-agent debate loops, complex sub-agent hierarchies).
* *Result:* ASES becomes an over-engineered layer of prompt patterns rather than a lean, formal methodology.


3. **Execution Substrate Hidden Dictation**
* *The Problem:* The distinction dictates that *Execution Engine should not silently decide methodological questions*. However, standard distributed system runtimes (like Temporal or Kubernetes) enforce specific state, event, and retry semantics.
* *Result:* Trying to maintain a pure ASES methodology independent of the runtime can lead to building expensive abstraction layers over tooling that already solves these problems natively.



---

### Predicted Areas of Researcher Disagreement

When evaluating this framework across independent research teams, expect the strongest friction in three key areas:

```
                      PRIMARY RESEARCHER FRICTION POINTS
                      
         +----------------------------------------------------------+
         | 1. Is Context Hydration Security or Methodology?        |
         |    (EDASES Invariant vs. ASES Scoping vs. Exec Sandbox)  |
         +----------------------------------------------------------+
                                     |
         +----------------------------------------------------------+
         | 2. Who Holds Ultimate Integration Authority?            |
         |    (Deterministic Tests vs. LLM Semantic Reviewers)    |
         +----------------------------------------------------------+
                                     |
         +----------------------------------------------------------+
         | 3. Distributed Systems Abstraction Boundaries             |
         |    (Adopt Temporal as-is vs. Re-implement ASES Runtime)   |
         +----------------------------------------------------------+

```

1. **Context Boundary Allocation: Security Invariant (EDASES) vs. Prompt Strategy (ASES)**
* *The Split:* Pure systems researchers will argue that context scoping ($G$) is an **EDASES Invariant / Execution Capability** issue (agents *must not* read outside their assigned sandbox paths). Product/AI methodology researchers will argue it is an **ASES Context Strategy** issue (how to optimize prompt payloads to keep agents focused).
* *The Debate:* Is context restriction an authority boundary or merely a token-efficiency technique?


2. **Verification Authority: Deterministic Machinery vs. Heterogeneous LLM Quorums**
* *The Split:* Formal methods researchers will assert that **only deterministic test suites and static analysis** have authority ($B, P$), treating model reviewers as zero-authority proposal engines. Multi-agent researchers will counter that complex software properties (architectural alignment, maintainability, semantic intent) cannot be checked deterministically, requiring **heterogeneous LLM quorums** to hold genuine verification authority.
* *The Debate:* Can an LLM ever hold true verification authority, or must it remain an untrusted suggester indefinitely?


3. **Substrate Coupling vs. Re-invention (Question K)**
* *The Split:* Pragmatic infrastructure engineers will argue that EDASES/ASES should directly adopt existing distributed systems primitives (e.g., Temporal workflows *are* the execution state machine, Git worktrees *are* the isolation boundary). Methodological purists will argue that doing so tightly couples the theory to 2020s infrastructure primitives, obscuring the novel probabilistic failure modes unique to AI agents.
* *The Debate:* Where does standard distributed systems engineering end, and where does AI-agent-specific runtime architecture actually begin?