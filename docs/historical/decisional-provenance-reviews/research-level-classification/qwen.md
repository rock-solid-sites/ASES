# Qwen Research Level Classificaion

This independent review analyzes the 16 open research questions (A–P) through the lens of the EDASES (Research), ASES (Methodology), and Execution (Runtime) framework. 

The analysis reveals that while the three-level distinction is theoretically sound, several questions currently masquerade as single-level problems when they actually span all three layers. Furthermore, the current inventory lacks critical questions regarding economic constraints, human authority, and adversarial security.

Below is the structured classification and research-framing exercise.

---

### 1. Proposed EDASES / ASES / Execution Taxonomy

This section assigns a **Primary Level** (where the core research question lives) and a **Secondary Level** (where the implications must be enforced). It also notes if the question is currently formulated at the **wrong abstraction level** (e.g., using specific implementation names like "Crosslink" to ask fundamental ontological questions).

*   **A. Authority Boundary Comparison**
    *   **Primary:** EDASES (Fundamental invariants of agent authority vs. system authority).
    *   **Secondary:** Execution (Mechanical enforcement via capabilities/gates).
    *   **Abstraction Check:** Correctly framed as a boundary comparison, but needs decomposition (see Section 3).
*   **B. Execution Trust**
    *   **Primary:** EDASES (The epistemology of "truth" and "evidence" in a probabilistic system).
    *   **Secondary:** ASES (The methodology for transforming untrusted claims into accepted state).
*   **C. Execution/Substrate Restart Survivability**
    *   **Primary:** EDASES (The ontological minimum of durable work truth).
    *   **Secondary:** Execution (Durable state machines and event sourcing).
*   **D. Merge / Integration Authority**
    *   **Primary:** ASES (The methodology of integration and batching).
    *   **Secondary:** EDASES (The compositional correctness problem: does individual semantic correctness imply collective correctness?).
*   **E. Agent Systems as Distributed Systems + Probabilistic Participants**
    *   **Primary:** EDASES.
    *   **Secondary:** None. This is a pure theoretical framing question establishing the boundary of novelty.
*   **F. Skeleton Factory / Minimum Viable Architecture**
    *   **Primary:** EDASES (Identifying irreducible invariants).
    *   **Secondary:** ASES (Defining the core methodological vocabulary).
*   **G. Context Hydration vs. Context Injection**
    *   **Primary:** ASES (Methodology of context contracts and scope bounding).
    *   **Secondary:** EDASES (Is discoverability an epistemic authority boundary?).
*   **H. Model Capability Matrix as Architectural Control**
    *   **Primary:** EDASES (Hypothesis: Does probabilistic diversity reduce correlated failures?).
    *   **Secondary:** ASES (Methodology of verification quorums and reviewer routing).
*   **I. Substrate Failure and Self-Repair Limits**
    *   **Primary:** EDASES (The self-reference paradox: Can a probabilistic agent repair its deterministic authority substrate?).
    *   **Secondary:** Execution (Reconciliation and consensus mechanisms).
*   **J. Human Design vs. Model-Driven Architectural Emergence**
    *   **Primary:** EDASES (Is "architectural compression" a fundamental invariant?).
    *   **Secondary:** ASES (Methodological gates for admitting new mechanisms).
*   **K. Distributed-System Prior Art**
    *   **Primary:** EDASES. (Acts as a constraint on the lower levels, not a question for them).
*   **L. Liveness and Progress**
    *   **Primary:** ASES (Methodological definition of "meaningful progress" vs. "doom loops").
    *   **Secondary:** Execution (Heartbeats, token budgets, state metrics).
*   **M & N. Crosslink / Work Substrate & State / Durable Execution Boundary**
    *   *Note: These should be combined (see Section 2).*
    *   **Primary:** EDASES (The ontology of the Work Graph vs. Execution State).
    *   **Secondary:** Execution (Physical/logical boundary enforcement).
    *   **Abstraction Check:** Currently at the **wrong abstraction level**. Asking "Where should Crosslink end?" uses a specific implementation name to ask a fundamental ontological question. It must be rephrased as "What is the boundary between the enduring Work Graph and ephemeral Execution State?"
*   **O. RPC / Process Boundary**
    *   **Primary:** ASES (Methodology of component isolation and failure domains).
    *   **Secondary:** Execution (IPC/RPC implementation).
*   **P. Verification and Review Architecture**
    *   *Note: Closely related to B and H.*
    *   **Primary:** ASES (The verification pipeline).
    *   **Secondary:** EDASES (What constitutes mathematical/empirical proof in an agentic context?).

---

### 2. Clusters to Combine

The current list treats many symptoms as distinct diseases. The following clusters represent deeper, unified research problems:

1.  **Cluster 1: The Ontology of State, Time, and Durability (C, L, M, N)**
    *   *Underlying Problem:* What is the enduring truth of the work, how does it persist through time/failures, and how do we measure its progression? Questions M and N are essentially the same question (the boundary between work truth and execution ephemera). Question L (Liveness) is just the temporal measurement of this state.
2.  **Cluster 2: The Epistemology of Verification and Trust (B, H, P)**
    *   *Underlying Problem:* How do we transform probabilistic claims into trusted system state using evidence and diversity? Question B (Trust), H (Model Matrix), and P (Review Architecture) are all facets of the same problem: establishing confidence in non-deterministic outputs.
3.  **Cluster 3: Authority, Boundaries, and Composition (A, D, G, I, O)**
    *   *Underlying Problem:* Where do the edges of the agent end, how do we prevent authority leakage, and how do isolated units safely compose? Question D (Merge) and G (Context) are both about safely composing isolated scopes. Question I (Self-Repair) is about the boundary of the substrate itself.
4.  **Cluster 4: The Boundary of Novelty and Complexity (E, F, J, K)**
    *   *Underlying Problem:* What is genuinely unique to Agentic SE, what can we inherit from traditional Distributed Systems (DS), and how do we prevent architectural bloat?

---

### 3. Questions that Require Decomposition

Several questions appear unified but will fail if assigned to a single level. They must be explicitly decomposed to prevent "implementation leakage" (where Execution silently makes Research decisions).

**Example: Question D (Merge / Integration Authority)**
*   *EDASES Formulation:* Does individual semantic correctness imply collective correctness in probabilistic systems? (The compositionality problem).
*   *ASES Formulation:* What is the methodology for batching, stacking, and resolving cross-cutting semantic conflicts?
*   *Execution Formulation:* How do merge queues, worktrees, and CI pipelines mechanically gate integration?
*   *Critique:* Currently, this is often treated purely as an Execution problem (how to run Git merge queues). It must be elevated to EDASES because probabilistic workers introduce novel composition failures that deterministic DS tools cannot catch.

**Example: Question G (Context Hydration vs. Context Injection)**
*   *EDASES Formulation:* Is discoverability an epistemic authority boundary? (If an agent can search the codebase, does it inherently have authority to change it?)
*   *ASES Formulation:* What is the methodology for context contracts, scope bounding, and grounding?
*   *Execution Formulation:* How are vector DB queries, file system allowlists, and tool restrictions mechanically enforced?

---

### 4. Missing Research Questions

The current inventory is heavily focused on state, authority, and verification, but misses critical dimensions of system viability:

1.  **The Economics of Trust (Cost/Verification Tradeoff):**
    *   *Missing Question:* Verification costs tokens, time, and compute. What is the optimal economic boundary where the cost of verification exceeds the cost of failure? How does the system dynamically route work to "cheap/fast" vs. "expensive/verified" paths based on risk?
2.  **Human Authority and Escalation Mechanics:**
    *   *Missing Question:* The documents mention human/model interaction, but where is the explicit research on *when and how* authority is transferred back to a human? How does the system mechanically prevent the human from becoming a bottleneck or a rubber stamp for agent claims?
3.  **Adversarial Context and Security Boundaries:**
    *   *Missing Question:* Agents ingest external context (docs, web, user prompts). How does the system formally model and mechanically prevent prompt injection or context poisoning from altering the authority substrate?
4.  **Long-Term Architectural Drift (Semantic Regression):**
    *   *Missing Question:* Individual merges might pass verification, but over months, the codebase may lose its original architectural invariants. How does the system detect and prevent macro-level semantic drift that bypasses local verification checks?

---

### 5. Reduced Fundamental Research Tracks

The 16 questions can be compressed into four core research tracks that cover the entire problem space without redundancy:

*   **Track 1: The Ontology of Agentic State and Truth**
    *   *Scope:* What is durable? What is progress? What is evidence? (Combines C, L, M, N).
*   **Track 2: Authority, Boundaries, and Composition**
    *   *Scope:* Where are the trust boundaries? How do we merge? Who repairs the substrate? (Combines A, D, G, I, O).
*   **Track 3: Epistemic Verification and Diversity**
    *   *Scope:* How do we prove correctness using probabilistic redundancy and structural checks? (Combines B, H, P).
*   **Track 4: The Boundary of Novelty vs. Distributed Systems**
    *   *Scope:* What is genuinely new here, what is prior art, and how do we enforce architectural compression? (Combines E, F, J, K).

---

### 6. The Strongest Argument Against the Three-Level Separation

**The "Waterfall of Abstraction" vs. "The Probabilistic Feedback Loop"**

The primary weakness of the EDASES → ASES → Execution model is that it implies a top-down, sequential flow of design: Research discovers invariants, Methodology designs workflows, and Execution builds machinery.

In deterministic systems, this works. In Agentic SE, the **Execution layer is not a deterministic enforcer; it is a probabilistic environment.** When the Execution engine encounters a novel state or an edge case not covered by ASES, it cannot just fail deterministically; it often must invoke a model to resolve the ambiguity. This means the Execution layer is actively doing ASES (methodology generation) and EDASES (research/discovery) on the fly.

Furthermore, you cannot fully define ASES without empirical data from Execution. The boundaries are highly porous. A strict 3-level separation risks creating:
1.  **Execution Leakage:** Where the runtime silently makes methodology decisions via hardcoded fallbacks because the ASES spec was incomplete.
2.  **Methodological Bloat:** Where ASES designs complex workflows that Execution cannot reliably enforce due to model non-determinism.

*Recommendation:* The model must explicitly allow for a **bottom-up empirical feedback loop** where Execution failures directly drive EDASES hypothesis generation, rather than treating the levels as a strict hierarchy.

---

### 7. Areas of Expected Disagreement

Independent researchers analyzing this problem space will likely clash most strongly in the following areas:

1.  **The "Flaky Node" Debate (Questions E & K):**
    *   *Traditional DS Engineers* will argue that LLMs are just "flaky nodes with high latency" and that 90% of this is solved by Temporal/Kafka/MapReduce (pushing everything to Execution).
    *   *AI Researchers* will argue that non-determinism, reasoning failures, and semantic hallucinations require entirely new EDASES paradigms that DS tools cannot handle.
2.  **The Definition of "Completion" (Questions B & L):**
    *   *Deterministic Advocates* will argue completion is a mechanical state (tests pass, state transition fires).
    *   *Semantic Advocates* will argue completion is a semantic state (the agent believes the intent is fulfilled, evidenced by artifacts), requiring much heavier verification machinery.
3.  **Self-Repair and Autonomy (Question I):**
    *   Researchers will strongly disagree on whether an agent should *ever* be allowed to repair its own substrate. Some will demand strict deterministic substrates (zero agent authority for repair), while others will advocate for agentic self-healing with human oversight.
4.  **The Location of "Context" (Question G):**
    *   Is context management an **Execution** problem (vector DBs and prompt builders) or an **EDASES** problem (the epistemic boundaries of the agent)? This determines whether context limits are hard-coded in the runtime or dynamically negotiated via methodology.