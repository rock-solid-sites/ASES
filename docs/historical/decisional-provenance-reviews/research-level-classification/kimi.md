# Kimi Research Level Classificaion

---

## 1. Proposed Taxonomy

### EDASES (Fundamental Research)

| Code | Question | Rationale |
|:---|:---|:---|
| **A** | Authority Boundary Comparison | What authority *means* in a system with probabilistic workers is foundational. The comparison across systems is empirical research to establish general principles. |
| **B** | Execution Trust | The epistemology of agent claims—what can ever be authoritative from a probabilistic participant—is fundamentally true about these systems. |
| **D** | Merge / Integration Authority | Who can declare collective correctness safe is a question about the nature of distributed trust, not merely merge-queue mechanics. |
| **E** | Agent Systems as Distributed Systems + Probabilistic Participants | Establishing whether this problem space is genuinely novel or inherited is meta-research about the field's boundaries. |
| **F** | Skeleton Factory / Minimum Viable Architecture | Determining which complexity is fundamental versus accidental is research into the essential nature of agentic software engineering. |
| **G** | Context Hydration vs. Context Injection | Whether discoverability itself constitutes an authority boundary is a foundational question about the nature of context and capability. |
| **H** | Model Capability Matrix as Architectural Control | Whether heterogeneous redundancy functions as a reliability mechanism is a research hypothesis about correlated failure modes, not just routing policy. |
| **I** | Substrate Failure and Self-Repair Limits | The hypothesis that "an agent should not repair its own authority substrate" touches on self-reference, recursion, and the limits of bootstrapped trust—core EDASES questions. |
| **J** | Human Design vs. Model-Driven Architectural Emergence | This is meta-research about how to distinguish genuine necessity from generated complexity. Whether "architectural compression" should be a research hypothesis, methodological rule, or design discipline is itself a research question. |
| **K** | Distributed-System Prior Art | Identifying which problems are genuinely novel versus already solved is a fundamental epistemological mapping of the problem space. |
| **N** | State / Durable Execution Boundary | What is the correct unit of durable state, and what constitutes "enduring truth" versus execution, is ontological research about the nature of work. |
| **P** | Verification and Review Architecture | What kinds of confidence exist and how they relate to review types is epistemological research about the nature of evidence. |

### ASES (Methodology)

| Code | Question | Rationale |
|:---|:---|:---|
| **C** | Execution/Substrate Restart Survivability | While implementation details are execution-level, what *state should* survive and what recovery policies should apply are methodological choices about durable versus ephemeral state. |
| **L** | Liveness and Progress | How to distinguish process existence from meaningful progress, what stall detection methodology should apply, and what progress representations should be required—these are methodological conventions. |
| **M** | Crosslink / Work Substrate | What the work items, dependencies, lifecycle, evidence, and review *should* be represented in the durable substrate is a methodology question. Where Crosslink ends and Engine state begins is a methodological boundary. |
| **O** | RPC / Process Boundary | Where methodology boundaries should be drawn between components, what should cross them as RPC versus event versus direct operation—these are architecture methodology choices. The distinction between methodological need and particular protocol is explicitly methodological. |

### Execution (Tooling/Runtime)

| Code | Question | Rationale |
|:---|:---|:---|
| *(No questions are purely Execution-level)* | All current inventory questions contain fundamental or methodological components. However, several questions have *strong* execution secondary dimensions (see decompositions below). |

---

## 2. Clusters That Should Be Combined

### Cluster 1: E + K → "The Novelty Problem"
**E** and **K** address the same underlying question from complementary angles. **E** asks which problems are qualitatively different because the worker is an LLM; **K** asks which established technologies already solve these problems. They should be merged into a single research track: *"What is genuinely novel about agentic distributed systems, and what can be inherited?"*

### Cluster 2: M + N → "The State Ontology Problem"
**M** and **N** are two lenses on the same fundamental issue: what is the durable state of work, what is its unit, and where do enduring truths end versus ephemeral execution artifacts? **M** asks what the substrate *should* represent; **N** asks what *is* durable versus ephemeral. Together they form a complete research question about the ontology of work state.

### Cluster 3: A + B + I + P → "The Trust, Authority, and Evidence Complex"
**A** (boundary comparison), **B** (execution trust), **I** (substrate failure/repair), and **P** (verification architecture) are manifestations of the same deeper problem: *how does trust operate in systems where workers are probabilistic and their claims are not self-verifying?* They should be treated as a single research program with sub-investigations: boundaries (A), epistemology (B), self-reference/recursion (I), and typology (P).

---

## 3. Questions That Should Be Decomposed Across Levels

### A. Authority Boundary Comparison
Should be three questions:
- **EDASES**: What constitutes legitimate authority in agentic systems with probabilistic participants? What are the fundamental types of authority (graph, execution, verification, completion, configuration)?
- **ASES**: By what methodology should each authority type be constrained (e.g., mandatory review, capability restrictions, policy enforcement)?
- **Execution**: Which authority constraints should be mechanically enforced (hooks, gates, state machines) versus which are policy-based?

### B. Execution Trust
Should be three questions:
- **EDASES**: Can a probabilistic worker's claim ever be epistemically authoritative? What is the nature of execution evidence? What state can be "directly established" versus "externally established"?
- **ASES**: What methodology transforms an untrusted agent result into an accepted result (review stages, evidence requirements, confidence thresholds)?
- **Execution**: What state transformations and verification pipelines enforce this methodology?

### C. Execution/Substrate Restart Survivability
Should be three questions:
- **EDASES**: What *should* survive restart (enduring truth versus reconstructible state)? What is the minimal durable state required for continuity?
- **ASES**: What recovery policies apply (admission control, quota parking, doom-loop prevention)? How should reconciliation methodology work?
- **Execution**: How is durable state persisted, recovered, and reconciled mechanically?

### D. Merge / Integration Authority
Should be three questions:
- **EDASES**: What does it mean for individually verified changes to be "collectively safe"? Who or what can legitimately declare this, and on what epistemic basis?
- **ASES**: What integration methodology (Refinery, Bors, merge queues, stacked changes, cross-cutting tests) establishes this confidence?
- **Execution**: What machinery implements the chosen methodology?

### G. Context Hydration vs. Context Injection
Should be three questions:
- **EDASES**: Is discoverability an authority boundary? What is the minimum epistemic context for reliable complex execution?
- **ASES**: What context contracts, scoped access, and pre-coding grounding should be standard methodology?
- **Execution**: How are capability restrictions, path allowlists, and hydration policies mechanically enforced?

### L. Liveness and Progress
Should be three questions:
- **EDASES**: What is the fundamental distinction between process existence, session health, tool activity, state transition, meaningful progress, and terminal completion? Are some of these essentially the same or genuinely distinct?
- **ASES**: What methodology detects and represents stalls, infinite loops, repeated failures, and pathological non-progress? What progress evidence is required?
- **Execution**: Which progress indicators are mechanically enforced (heartbeats, timeouts, state transition requirements) versus inferred?

### M + N. Crosslink / Work Substrate + State/Durable Execution Boundary (merged cluster)
Should be three questions:
- **EDASES**: What is the correct ontology of work (identity, lifecycle, evidence, results)?
- **ASES**: What work substrate methodology (Crosslink responsibilities versus Execution Engine state) best implements this ontology?
- **Execution**: How are work items, dependencies, parent/child relationships, locks, and worktrees mechanically represented and maintained?

### O. RPC / Process Boundary
Should be three questions:
- **EDASES**: What is the fundamental nature of authority boundaries in systems with probabilistic unreliable workers?
- **ASES**: Where should methodological boundaries be drawn between components (what should be RPC versus event versus durable state versus direct operation)?
- **Execution**: What protocol/implementation pattern satisfies the methodological requirements across process failure and restart?

### P. Verification and Review Architecture
Should be three questions:
- **EDASES**: What kinds of confidence exist (builder self-check, semantic, independent, adversarial, integration, final acceptance)? How do they relate?
- **ASES**: What review types are required for what work categories? How should review diversity and complementary weaknesses be methodology?
- **Execution**: How is verification evidence represented in durable state rather than informal conversation?

---

## 4. Important Missing Research Questions

### Missing 1: The Human Authority Interface
The inventory assumes agent systems operate with human oversight, but never explicitly asks: **What is the fundamental nature of human authority in agentic software engineering?** When must human judgment be irreducible (what only humans can authorize), and when is human approval merely a slow, expensive mechanical check? This is distinct from "agent authority"—it is about the *human* as a participant with finite attention and context.

### Missing 2: The Composition of Verification
If work item A is verified, and work item B depends on A, does verifying B require re-verification of A? **How does verification compose across dependency boundaries?** This is implicit in D but distinct: D is about *merge* (parallel independent changes); this is about *composition* (serial dependent changes).

### Missing 3: The Epistemology of Stateless Workers
Agents are stateless across sessions. **What are the fundamental implications of the fact that every session is a fresh reasoning process with no memory?** This underlies context loss, knowledge loss, and reasoning loss mentioned in the project goal but is not explicitly interrogated as a research question. It asks: is reliable agentic software engineering possible when the worker has no persistent epistemic state?

### Missing 4: Token Economics and Coordination Cost
The project goal mentions "excessive token expenditure on coordination" as a failure mode, but no research question asks: **What is the fundamental tradeoff between coordination cost (tokens spent on verification, review, and context) and reliability?** Is there a theoretical minimum coordination cost for trustworthy outcomes, or is the relationship qualitative?

### Missing 5: Semantic versus Syntactic Verification Boundary
What can be *mechanically* verified (type systems, tests, linting) versus what *requires* model judgment (architectural appropriateness, user intent, cross-cutting concerns)? **Where is the boundary between formal verification and model-based verification, and what does this boundary imply for methodology?**

---

## 5. Proposed Reduced Set of Fundamental Research Tracks

The 16 questions (14 after merging M+N and E+K) can be reduced to **7 fundamental tracks**:

### Track 1: The Trust, Authority, and Evidence Ontology
*(A, B, D, I, P)*

The deepest stratum: What can a system trust from a probabilistic worker? What evidence transforms an untrusted claim into accepted truth? Who can declare what (completion, integration, substrate repair), and what happens when the substrate itself fails? This is the epistemological foundation.

### Track 2: The State and Durability Ontology
*(C, M+N, O)*

What is the correct unit and representation of enduring state? Where does durable truth end and ephemeral execution begin? How should state cross process boundaries and survive restart? This is the ontological foundation.

### Track 3: The Novelty and Inheritance Problem
*(E + K)*

What is genuinely novel about agentic software engineering versus inherited from distributed systems, workflow engines, and orchestration? What prior art applies, where does it stop being sufficient, and what layer is genuinely new? This is the epistemological foundation determining what must be invented versus adapted.

### Track 4: Liveness, Progress, and Detection
*(L)*

What is the fundamental distinction between activity and progress? How should stalls, loops, and pathological non-progress be detected and represented? This is the dynamical foundation.

### Track 5: Context, Capability, and Bounding
*(G + H)*

What context is minimum necessary, and is discoverability itself an authority boundary? Can heterogeneous model capability differences be used as a reliability mechanism? This is the control foundation.

### Track 6: Architectural Minimality and Compression
*(F + J)*

What is the minimum viable architecture? How to distinguish deliberate necessity from model-generated complexity? What compression rules prevent mechanism accumulation? This is the methodological foundation.

### Track 7: Work Integration and Composition
*(D + Missing 2)*

How do independently produced changes and serially dependent changes safely combine? What does "collectively correct" mean, and who can declare it? This is the integrative foundation.

---

## 6. Strongest Argument Against the Three-Level Separation

The strongest argument against the EDASES → ASES → Execution separation is that **it assumes a unidirectional, waterfall-like relationship from truth → methodology → machinery, when in practice these layers co-evolve through epistemic feedback loops.**

Specifically:

**The implementation constraints of the Execution Engine determine what methodology is even possible.** For example, whether verification can be represented as durable state (an Execution capability) determines whether verification methodology can be "evidence-based" or must remain "conversation-based." The document's central design principle—that agents should not be trusted with authority that can be mechanically enforced—presupposes an Execution Engine capable of such enforcement. But if the Engine cannot implement certain enforcement, the ASES methodology must adapt, which changes what EDASES research hypotheses are testable.

**The distinction between "fundamentally true" and "methodology following from it" is often indistinguishable.** Many questions in the inventory (particularly J, O, and aspects of A and M) are about *how to distinguish* these very categories. If EDASES research produces "architectural principles" that are actually methodology choices in disguise, then the separation collapses. The document itself acknowledges this ambiguity when asking whether architectural compression should be "research hypothesis, methodological rule, or design discipline."

**The three-level model does not account for the bootstrap problem.** How do we know our EDASES research is correct without implementing it (Execution) and testing it? And how do we implement without methodology (ASES) to guide implementation? The levels cannot be developed sequentially; they must co-evolve, which means the boundaries are permeable and perhaps arbitrary.

**Finally, the model omits a fourth necessary layer: *Epistemology* or *Validation.*** There is no layer for "How do we know our EDASES research is true?" or "What constitutes falsification of an architectural principle?" Without this layer, the three-level model risks untestable speculation at the EDASES level being passed down as unexamined assumptions to ASES and Execution.

---

## 7. Areas of Expected Disagreement

### Disagreement Area 1: The Nature of Authority Questions
Researchers with distributed systems backgrounds will likely classify **A**, **D**, and **I** as *Execution* or *ASES* questions about merge queues, state machines, and recovery protocols. Researchers with philosophy of science or epistemology backgrounds will classify them as *EDASES* questions about the nature of trust and evidence. This is the deepest fault line in the inventory.

### Disagreement Area 2: Whether State Durability Is Fundamental or Implementation
Whether **C**, **M**, and **N** are about "what state *should* be durable" (EDASES/ASES) versus "how to persist and recover state" (Execution) will split systems researchers (who see state management as solved engineering) from philosophers of technology (who see the durable/ephemeral distinction as ontological).

### Disagreement Area 3: Model Heterogeneity as Research or Engineering
**H** will be disputed between researchers who view model selection as a purely empirical performance/cost optimization problem (Execution/ASES) and those who view it as a hypothesis about correlated failure modes and verification quorums (EDASES). This maps to whether "model capability matrix" is seen as routing table or architectural control.

### Disagreement Area 4: Context Bounding as Prompt Engineering versus Authority Philosophy
**G**—particularly whether "discoverability is an authority boundary"—will be seen by implementation-focused researchers as a prompt engineering problem (how to write better context limits, ASES) and by theory-focused researchers as a fundamental question about the relationship between knowledge access and capability (EDASES).

### Disagreement Area 5: Liveness as Health Checks versus Philosophical Agency
**L** will divide those who see "distinguishing process existence from meaningful progress" as a DevOps monitoring problem (Execution: implement better health checks, timeouts, heartbeats) from those who see it as a question about the nature of agency and action in stateful systems (EDASES: what does it mean for a process to be "doing something" versus "merely existing"?).

### Disagreement Area 6: Architectural Compression as Methodological Discipline or Unnecessary Meta-Theory
**J** will be viewed by practitioners as navel-gazing that impedes progress (why do we need a rule about when to add mechanisms? Just don't add them) and by systematizing theorists as the most important safeguard against complexity collapse (the essential methodological rule preventing Gas Town's tendency toward feature creep).

These six areas of disagreement are not signs of weakness in the three-level model—they are where the classification system itself is most brittle under independent analysis.