# Muse Spark 1.2 Research Level Classification

# Independent Review: Classification of EDASES Research Questions A-P

## 1. Proposed Taxonomy

The provisional 16 questions are not at a uniform abstraction level. Most are **cross-level transformations** of a smaller set of underlying invariants, stated once at EDASES, methodologized at ASES, and enforced at Execution. Forcing a single primary level per letter is the error the exercise is designed to expose.

I classify by *the actual research question as formulated*, not current implementation.

| ID | Question | Primary Level | Secondary Level | Nature of Question |
|---|---|---|---|---|
| **A** | Authority Boundary Comparison | **EDASES -> ASES -> Execution** Decomposed | - | Taxonomy of 4 authorities + enforcement mechanism. Not one question but a **comparative framework** applied to all others. |
| **B** | Execution Trust | **EDASES** | ASES / Execution | Core invariant: what agent assertion can be authoritative. |
| **C** | Restart Survivability | **Execution** | ASES | Largely solved distributed systems problem + agent-specific reconciliation policy. |
| **D** | Merge / Integration Authority | **EDASES / ASES** | Execution | Integrates B, E, P. Collective safety cannot be derived from isolated correctness. |
| **E** | Distributed Systems + Probabilistic Participants | **EDASES** | - | Foundational ontological hypothesis. Tests whether EDASES exists as distinct field. |
| **F** | Skeleton Factory / Minimum Viable Architecture | **Meta - Cross-level synthesis** | EDASES | Exercise in compression; not a research question but a methodology for answering others. Prohibited vocabulary makes it EDASES-paradigmatic. |
| **G** | Context Hydration vs Injection | **ASES** | EDASES (principle) / Execution (mechanism) | Authority boundary applied to information. Discoverability as authority. |
| **H** | Model Capability Matrix as Architectural Control | **ASES** | EDASES (hypothesis: heterogeneous redundancy reduces correlated failure) | Empirical ASES policy question with EDASES falsifiable claim. |
| **I** | Substrate Failure and Self-Repair Limits | **EDASES** | ASES / Execution | Fundamental authority paradox: substrate cannot be repaired by subject. |
| **J** | Human Design vs Model-Driven Emergence | **EDASES (Research Governance)** | ASES (methodological rule) | Meta-research question about how research is done. Architectural compression principle. |
| **K** | Distributed-System Prior Art | **EDASES / ASES** | Execution | Boundary-drawing exercise: what we borrow vs what is novel due to probabilistic worker. |
| **L** | Liveness and Progress | **EDASES -> ASES -> Execution** Decomposed | - | Ontology of progress (EDASES) -> detection methodology (ASES) -> enforcement (Execution). |
| **M** | Crosslink / Work Substrate | **ASES / Execution Boundary** | - | Not a research question in current form; is an **implementation allocation** decision contingent on answers to N, C, I. |
| **N** | State / Durable Execution Boundary | **EDASES** | Execution | Fundamental: correct unit of durable state. Gas Town Molecules/Wisps is one instance. |
| **O** | RPC / Process Boundary | **Execution** | ASES | Almost entirely Execution engineering taxonomy. Methodological content is minimal once E is settled. |
| **P** | Verification and Review Architecture | **ASES** | EDASES / Execution | Typology of confidence -> evidence-based state machine. |

### Principle for classification:

> If the question asks `what is true about trust, authority, evidence, progress, or state independent of implementation?` -> **EDASES**
> If the question asks `how should work be represented, authorized, evidenced, reviewed, integrated, bounded to preserve those invariants with probabilistic workers?` -> **ASES**
> If the question asks `what machinery durably, deterministically, idempotently enforces that methodology across failures?` -> **Execution**

By that test, only **B, E, I, N** are pure EDASES. Only **C, O** are pure Execution. The rest are explicitly cross-level and should be decomposed, not assigned.

## 2. Clusters That Should Be Combined

Apparent diversity collapses to 4-5 underlying invariants.

**Cluster 1: Authority-Trust-Evidence Core**
**$$B + A_{verification,completion} + D + I + P$$ unified.**

These are one question: *What makes a claim about work trustworthy and who/what is authoritative to establish it?*
- B asks about execution assertions
- A decomposes authority types
- P typologizes review as evidence-generating transformations
- D asks who declares collective safety
- I asks who repairs the substrate that grants authority

Gas Town observations (`assignment, execution, completion are distinct facts; completion requires external evidence; supervision creates recursion`) are all corollaries of **Trust-Evidence-Authority**. Treating them separately duplicates research.

**Cluster 2: Durable State vs Ephemeral Execution**
**$$C + N + M + O + (part of L)$$ unified.**

- N asks the unit of durable state
- C asks what must survive restart
- M asks where Crosslink ends and Execution begins
- O asks what crosses a process boundary and how
- L contributes `process existence != state transition`

These are one question: *What state is truth about work vs transient about execution, and where/how is it durably represented and reconciled?* M and O are not independent research questions; they are allocation consequences of answering N and C. E.g., Crosslink vs Execution Engine is just two names for durable work substrate vs ephemeral execution substrate once N is decided.

**Cluster 3: Progress, Liveness, and Bounded Recovery**
**$$L + C_{doom-loop, quota, admission} + (part of F: pathological graph expansion)$$**

- L asks how to distinguish activity from progress
- C asks about doom-loop prevention, parking, bounded retry
- F notes pathological work-graph expansion

These are one question: *How is non-progress, stall, and pathology represented as state and bounded by policy without trusting agent self-report?*

**Cluster 4: Context as Authority Boundary**
**$$G + H + (part of A_{graph authority})$$**

G asks how to bound task expansion via context. H asks whether model diversity is a reliability mechanism. Both are instances of **information and capability as authority control**. G restricts what agent can *know*, H restricts what agent can *do* and diversifies who checks it. They belong together as **Capability and Context Governance**.

**Cluster 5: Distributed Systems Inheritance**
**$$E + K + F + J$$ unified.**

E hypothesizes `probabilistic participants` distinguishes the field. K asks what prior art already solves. F asks what minimal architecture remains after removing accidental Gas Town complexity. J asks how to distinguish necessity from model-generated accretion.

These are one meta-question: *What is genuinely novel vs ordinary distributed systems engineering + governance discipline to prevent re-introduction of accidental complexity?*

After combining, 16 letters compress to **5 research tracks**.

## 3. Questions That Must Be Decomposed Across Levels

The most valuable decomposition pattern explicitly called for in the prompt is correct and should be applied systematically:

**Canonical Decomposition:**

**B. Execution Trust:**
- **EDASES:** What is the ontology of trust? Is agent completion ever authoritative? What is execution evidence vs claim? Hypothesis: *No agent assertion about own completion is authoritative.*
- **ASES:** Methodology of external verification: independent review, evidence schemas, typed dispositions, verification quorum, transformation of untrusted result -> accepted result.
- **Execution:** Mechanisms that make completion authority unforgeable: state machine where `completed` is unreachable from agent-owned transition, evidence presence gates, capability enforcement.

**L. Liveness and Progress:**
- **EDASES:** Ontological distinction: process liveness $$ \neq $$ session health $$ \neq $$ tool activity $$ \neq $$ state transition $$ \neq $$ meaningful progress $$ \neq $$ terminal completion. What is `progress` as invariant?
- **ASES:** Policy for detecting stalls, infinite loops, non-progress: heartbeat semantics, progress metrics, parking policies, bounded retries.
- **Execution:** Instrumentation that enforces without LLM judgment: tokens/execution traces -> derived signals, timers, watchdogs, idempotent termination.

**A. Authority Boundaries:**
- **EDASES:** Principle: *Agents should not be trusted with authority mechanically enforceable by substrate.*
- **ASES:** Allocation of Graph/Execution/Verification/Completion authority to roles, policies, quorums.
- **Execution:** Enforcement via allowlists, state-machine guards, deterministic gates, Git/DB as source of truth vs prompt discouragement.

**D. Integration Authority:**
- **EDASES:** Collective correctness not monotonic: individually verified changes can be jointly incorrect. Who has authority to declare collective safety?
- **ASES:** Integration methodology: Refinery, Bors batching, merge queues, cross-cutting integration test scope, semantic vs integrated correctness.
- **Execution:** Integration machinery: deterministic batch construction, durable queue, isolation of verification of batch vs items.

**P. Verification:**
- **EDASES:** What confidence does each review type establish? Are failures correlated across models?
- **ASES:** Review protocol: builder self-check vs semantic review vs adversarial audit vs integration verification vs final acceptance; evidence representation.
- **Execution:** State transitions that reify review as evidence artifacts, reviewer diversity enforcement, quorum enforcement.

**G. Context:**
- **EDASES:** Is discoverability an authority? Principle of least context.
- **ASES:** Context contracts: scoping, Crosslink query boundaries, pre-grounding, allowlists.
- **Execution:** Enforcement: scoped file access, capability restrictions, context hydration policies as mechanical guards.

Attempting to assign any of these wholly to one level perpetuates the category error the three-level model is meant to correct.

## 4. Most Important Missing Research Questions

The current inventory is strong on state/authority/recovery but under-specifies:

**1. Human Authority and Escalation (Critical Gap)**
Where does human authority sit? When must system escalate to human vs auto-park vs auto-retry? What is the human's role: author, approver, repairer of substrate, override authority? I states agent should not repair substrate - but can human? Under what protocol? Without this, authority model is incomplete (machine and model but not human).

**2. Evidence Semantics and Attestation**
B and P assume `evidence` but never define formal semantics. What is admissible evidence? Artifact hash, test result, type check, proof, observation? How is evidence attested, tamper-evident, bound to work item identity and execution identity (Gas City's execution identity idea)? Cryptographic or content-addressable binding missing.

**3. Economics, Token Budget, and Resource Governance**
Mentioned as `excessive token expenditure on coordination` but no research question. How to model cost vs verification depth? Token budget as ASES policy with Execution enforcement (quotas, parking). Interacts with L and C but distinct as optimization under trust constraints.

**4. Security, Capability, and Confused Deputy**
G mentions scoped file access but no systematic security model: agent as principal with least privilege, capability attenuation, exfiltration, prompt injection as authority violation. Needed to ground `capability restrictions` formally.

**5. Identity, Lineage, and Provenance**
What is identity of work item, artifact, execution, agent session across restarts and scatter/gather? How to prevent state divergence via identity collision? Related to execution identity in Gas City but not formulated as EDASES invariant (e.g., work must outlive session -> requires stable identity).

**6. Time, Ordering, and Oracle**
No question about time: timers, deadlines, ordering of events, causality. Distributed systems prior art (K) solves this with logical clocks, but probabilistic agents introduce new temporal failure (stall detection depends on time oracle). Who is authoritative for time?

**7. Specification and Intent Drift**
Assumption drift and architectural amnesia are goals, but no research question formalizes *intent* representation. How is original intent durably represented and checked against implementation? Crosslink stores work items, but does it store invariant that work item must not violate? This is the `pre-coding grounding` deeper problem.

**8. Failure Taxonomy and Recovery Classes**
Implicit in C and L but missing explicit taxonomy: transient vs permanent failure, deterministic vs non-deterministic, agent fault vs substrate fault vs integration fault. Each class demands different recovery (retry idempotently vs park vs human escalate). Without taxonomy, C and L policies remain ad hoc.

## 5. Proposed Reduced Set of Fundamental Research Tracks

Compress 16 letters -> 5 tracks, ordered by dependency. Each track inherently spans EDASES->ASES->Execution but has distinct EDASES hypothesis.

### Track 1: Trust, Authority, and Evidence [EDASES Core]
**Unifies B + A + D + I + P**
Hypothesis: *Software produced by probabilistic participants is trustworthy iff every trust-relevant claim (assignment, completion, verification, integration, substrate repair) requires external, mechanically verifiable evidence and authority resides in deterministic substrate, not agents.*

Research program: Define authority types, evidence schemas, verification transformations, integration authority, substrate repair authority. Falsifiable: Show case where agent self-attestation without external evidence yields trustworthy completion at scale.

### Track 2: Durable Truth vs Ephemeral Execution [State Architecture]
**Unifies N + C + M + O**
Hypothesis: *There exists a minimal, correct unit of durable state representing truth about work that is distinct from ephemeral execution state, and all process/RPC boundaries can be derived from this distinction plus reconciliation.*

Research program: Define durable work substrate, execution evidence, events, policies; decide Crosslink vs Execution Engine allocation; define restart survivability, reconciliation, and identity.

### Track 3: Progress, Liveness, and Bounded Autonomy [Dynamics]
**Unifies L + C (doom loops, quotas) + F (graph expansion) + G (task bounding)**
Hypothesis: *Progress is a state transition in work substrate, not agent activity; without mechanical bounds on expansion, retry, and context, probabilistic workers inevitably diverge into pathological non-progress.*

Research program: Distinguish activity from progress, formulate stall/pathology detection as state, bound recovery idempotently, bound graph expansion and task scope via context/capability as authority (G).

### Track 4: Verification Diversity and Integration Safety [Collective Correctness]
**Unifies P + H + D + part of G**
Hypothesis: *Individual correctness does not compose; trustworthy integration requires heterogeneous, independent verification and collective safety authority distinct from individual completion authority; model diversity reduces correlated failure via verification quorum.*

Research program: Typologize review, test heterogeneous redundancy, define integration verification (Refinery/Bors) as transformation requiring its own evidence.

### Track 5: Minimality and Prior Art [Methodology Governance]
**Unifies E + K + F + J**
Hypothesis: *Most coordination, scheduling, recovery, durability problems are ordinary distributed systems problems; the Delta that is genuinely AI-agent-specific is authority/trust around probabilistic participants; model-driven accretion can be controlled by architectural compression discipline.*

Research program: Map Temporal/Kubernetes/MapReduce to EDASES, define `probabilistic non-authoritative participant` characterization, enforce `why not existing transition/determinism/capability?` gate, derive minimum viable architecture vocabulary.

These 5 tracks are falsifiable, have distinct empirical programs, and each demands EDASES invariant -> ASES methodology -> Execution mechanism articulation.

## 6. Strongest Argument Against the Current Three-Level Separation

The three-level model is valuable, but its strongest weakness is that it implies a **linear, waterfall dependency** ($$EDASES \rightarrow ASES \rightarrow Execution$$) and **clean separation** that does not survive real systems.

**Arguments:**

**1. Leakage and Co-definition.** Authority invariants cannot be formulated without reference to enforcement cost and mechanism. Example: Whether `verification quorum` is EDASES (principle of independent verification) or ASES (quorum size 2 vs 3) or Execution (how quorum is enforced) depends on model capability data and execution latency/cost. EDASES research that ignores Execution feasibility produces unimplementable invariants. Conversely, Execution machinery (state machine gates) silently decides EDASES questions if researchers are not forced to surface assumption. The levels are co-defining, not separable.

**2. Missing Fourth Level.** The model conflates two distinct things under EDASES: *fundamental truth about software engineering* and *research governance* (J). And it leaves *human authority and deployment/operations* without a home. Many failures (substrate repair, escalation, approval) are human-in-the-loop governance questions that are neither methodology for agents nor execution machinery. Forcing them into ASES overloads methodology. A more honest model might be 4 levels: **Foundations (EDASES) / Methodology (ASES) / Machinery (Execution) / Governance & Operations (Human Authority, Deployment, Economics, Security)**. Alternatively, a **two-axis** model: abstraction ($$principle \rightarrow methodology \rightarrow mechanism$$) vs concern ($$trust / state / progress / verification / context$$).

**3. Risk of Methodological Bureaucracy.** By creating ASES as methodology independent of runtime, the model invites specifying elaborate hand-offs, reviews, and evidence protocols that are never mechanically enforced, recreating the `prompt discouragement vs mechanical prevention` failure at a higher level. If ASES is not simultaneously prototyped in Execution, it becomes unfalsifiable process documentation.

**4. Overloading Execution.** With the current definition, Execution becomes `everything durable, deterministic, scalable` - i.e., a conventional distributed system. This tempts the team to reinvent Temporal/Kubernetes (K) rather than adopt them, under the banner of `not reinventing but identifying Delta`. Without a sharp `borrow vs build` criterion, Execution will accrete accidental complexity that J warns about.

In short: **The three levels correctly diagnose the problem (confusing what is true with how to enforce it) but incorrectly suggest the solution is strict layering. In reality, invariants are discovered by building enforcement and observing where agents violate intent. Treat levels as lenses or concerns, not as phases or teams.**

A healthier interpretation: EDASES, ASES, Execution are **perspectives for classifying a decision**, not **places to put code or documents**. Every significant decision should have an EDASES justification, an ASES specification, and an Execution enforcement - the `decomposition` pattern, not assignment.

## 7. Areas Where Independent Researchers Will Disagree Most Strongly

**Highest Expected Variance:**

**1. G (Context Hydration) and H (Model Capability Matrix): Research vs Engineering**
One camp will see these as EDASES research (fundamentally about bounding probabilistic cognition and correlated failure). Another will see them as prompt engineering / routing optimization with no architectural invariant - purely ASES/Execution tuning. Disagreement hinges on whether heterogeneous redundancy *provably* reduces correlated verification failure or merely improves cost/performance. This is empirically unsettled.

**2. M and N: Where Crosslink Ends**
Whether Crosslink is durable truth store (work items, dependencies, evidence, locks, worktrees) vs merely coordination substrate is contentious. Some will allocate locks/worktrees to Execution Engine as ephemeral; others to Crosslink as durable coordination. The durable vs ephemeral boundary (N) is philosophically sharp but practically blurry (e.g., `assignment` is durable fact but realized via ephemeral queue). Expect split between `database-centric` and `workflow-engine-centric` views.

**3. F (Skeleton Factory): Minimal Vocabulary**
Whether to include constructs like `Agent Session`, `Dependency`, `Policy` in minimal architecture. Minimalists will argue `Work Item + State Transition + Evidence + Event` suffices and `Agent Session` is ephemeral Execution detail. Others will argue agency requires first-class `Session` and `Dependency` as durable. This reflects deeper E vs K disagreement on how much is novel.

**4. B vs Execution: Can Agents Ever Be Authoritative?**
Hardliners: *Never;* agent completion claim is never authoritative, only substrate transition on evidence is. Pragmatists: For low-risk, reversible, or human-observed tasks, agent self-attestation with evidence attachment may be *sufficiently* authoritative per ASES policy. This is a trust-threshold debate, not purely technical.

**5. I (Substrate Self-Repair): Dogmatism vs Pragmatism**
Hypothesis `agent should not repair substrate that defines its authority` is elegant but will be contested in practice: Who else can repair if human unavailable and substrate inconsistent? Some will argue for narrow, auditable, deterministic self-repair capabilities (e.g., agent can propose reconciliation event, substrate approves). Others will insist on hard prohibition and human-only repair. This splits idealists vs operators.

**6. K (Prior Art): How Much to Borrow**
Division between `adopt Temporal/Kubernetes wholesale and build thin trust layer on top` vs `those systems assume trusted workers and thus fundamentally mismatch; we must build custom`. Expect disagreement correlating with researchers' backgrounds (distributed systems veterans vs LLM-agent builders).

**Moderate Variance:**
- D integration authority: is collective safety an ASES social process or a mechanically verifiable property (suite of integration tests as evidence)?
- J compression discipline: is it EDASES hypothesis, ASES rule, or team culture? All three plausible.
- L progress definition: is `meaningful progress` objectively definable or inherently model-judged?

### Convergence Prediction

Despite divergence, independent analyses will likely **converge** on:
- B/E/I as the EDASES nucleus (trust-authority-evidence)
- C/N/M/O as one durability question
- Recognition that A, D, L, P, G are cross-level decompositions, not single-level assignments
- Compression to $$5 \pm 1$$ tracks
- Identification of missing Human Authority and Evidence Semantics questions

Divergence will be most visible not in *what clusters exist* but in *where to draw mechanical enforcement line* and *how minimal is minimal* - which is exactly the productive tension the three-level model was designed to surface.