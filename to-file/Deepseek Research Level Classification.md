# Deepseek Research Level Classification

## 1. Proposed EDASES / ASES / Execution Taxonomy

I treat the three levels as:

- **EDASES**: invariants, trust/authority semantics, research hypotheses, what is fundamentally true.
- **ASES**: methodology, roles, evidence requirements, work models, review/integration policy.
- **Execution**: mechanical enforcement, durable state machinery, process boundaries, restart/reconciliation.

Most of the open questions are currently **EDASES-primary**, because they are still unresolved research questions rather than settled methodology or implementation concerns. That itself is a finding: the inventory is research-heavy.

| ID | Primary | Secondary / Tertiary | Notes |
|---|---|---|---|
| **A. Authority Boundary Comparison** | **EDASES** | ASES, Execution | Fundamental authority taxonomy. ASES expresses it as an authority matrix; Execution enforces it. Overlaps B, D, G, I, O. |
| **B. Execution Trust** | **EDASES** | ASES, Execution | What can a probabilistic agent assert? Completion/evidence/trust transformation is an EDASES question. ASES defines evidence protocol; Execution captures evidence. Overlaps A, L, P. |
| **C. Restart Survivability** | **Execution** | ASES, EDASES | Execution-primary if the question is about restart/recovery machinery. But the deeper durable-vs-reconstructed distinction belongs with N and EDASES. Overlaps M, N, O, L, E, K. |
| **D. Merge / Integration Authority** | **ASES** | EDASES, Execution | Integration methodology is ASES. The deeper question of collective correctness and authority to declare it is EDASES. Execution provides merge queues/gates. Overlaps A, B, P. |
| **E. Distributed Systems + Probabilistic Participants** | **EDASES** | ASES, Execution | This is a core research hypothesis. It should not be treated as settled. Overlaps K, L, C. |
| **F. Skeleton Factory / Minimum Viable Architecture** | **ASES** | EDASES, Execution | Clean-room minimum vocabulary and work model are ASES. The question of which complexity is fundamental is EDASES. Overlaps J, M, N. |
| **G. Context Hydration vs Injection** | **EDASES** | ASES, Execution | The real question is whether discoverability is an authority boundary. ASES defines context contracts; Execution enforces allowlists/capabilities. Overlaps A, O. |
| **H. Model Capability Matrix as Architectural Control** | **EDASES** | ASES, Execution | Whether heterogeneous redundancy reduces correlated failure is an empirical research question. ASES defines reviewer diversity; Execution routes models. Overlaps B, P. |
| **I. Substrate Failure and Self-Repair Limits** | **EDASES** | ASES, Execution | Self-referential authority is fundamentally EDASES. ASES defines repair policy; Execution performs reconciliation. Overlaps A, C, N, O. |
| **J. Human Design vs Model-Driven Architectural Emergence** | **EDASES** | ASES | Architectural compression is a research methodology question first, then an ASES design rule. Overlaps F. |
| **K. Distributed-System Prior Art** | **EDASES** | Execution, ASES | Identifying the genuinely novel layer is EDASES. Execution should reuse mature machinery where valid. Overlaps E, L, C. |
| **L. Liveness and Progress** | **EDASES** | ASES, Execution | The distinction between activity, progress, and completion is fundamental. ASES defines progress evidence; Execution detects stalls. Overlaps B, C, P. |
| **M. Crosslink / Work Substrate** | **ASES** | EDASES, Execution | Durable work substrate is methodology. Its identity/completion semantics are EDASES; physical storage is Execution. Overlaps C, N, O, F. |
| **N. State / Durable Execution Boundary** | **EDASES** | ASES, Execution | “What is the correct unit of durable state?” is an EDASES question. ASES chooses the work model; Execution persists it. Overlaps C, M, O. |
| **O. RPC / Process Boundary** | **Execution** | ASES, EDASES | Process/state boundary mechanics are Execution. But which boundaries are authority boundaries is EDASES/ASES. Overlaps A, C, M, N. |
| **P. Verification and Review Architecture** | **ASES** | EDASES, Execution | Review methodology is ASES. What confidence each review establishes is EDASES; evidence/gates are Execution. Overlaps B, D, H, L. |

A few classifications are deliberately close. The largest ambiguities are:

- **C vs N/O**: Is this about restart machinery, or about durable truth?
- **A vs B vs D vs I**: Are these separate questions, or four views of one authority/evidence problem?
- **L vs B**: Is completion a special case of evidence, or a separate progress property?
- **F vs J**: Is minimum architecture a design exercise or a research methodology?

I would not treat A–P as sixteen independent questions. They are better understood as overlapping clusters.

---

## 2. Clusters That Should Be Combined

### Cluster 1: Authority, Trust, and Evidence

**Contains:** A, B, D, G, I, L, P, and the authority aspect of O.

These are all manifestations of a single deeper problem:

> Which facts may a probabilistic agent assert, and which facts must be established outside the agent?

Completion claims, verification claims, integration authority, discoverability boundaries, self-repair authority, and progress claims are all special cases.

---

### Cluster 2: Durable State and Work Substrate

**Contains:** C, M, N, O, and the substrate aspect of F.

The common question is:

> What is durable because it is truth about work, versus ephemeral because it is current execution?

Crosslink, durable work items, restart recovery, process boundaries, and the execution state/work state split belong together.

---

### Cluster 3: Probabilistic Participants in Distributed Systems

**Contains:** E, K, L, and the recovery/liveness part of C.

The common question is:

> Which coordination, recovery, scheduling, and liveness problems are inherited from distributed systems, and which change because the worker is an LLM?

This cluster should explicitly test the stated hypothesis in E rather than assume it.

---

### Cluster 4: Verification and Model Diversity

**Contains:** H, P, B, D.

The common question is:

> Can verification be made reliable by using heterogeneous, independent reviewers, and can verification itself be represented as evidence rather than conversation?

This includes the verification quorum question and the integration-verification overlap.

---

### Cluster 5: Context, Capability, and Discoverability

**Contains:** G, A, and parts of O.

The common question is:

> Is the ability to discover or access information an authority boundary?

Context hydration is not only an efficiency problem; it determines what an agent can believe, claim, or act upon.

---

### Cluster 6: Architectural Minimality and Compression

**Contains:** F, J, and parts of M.

The common question is:

> How do we distinguish fundamental architecture from accumulated, model-generated, or historically accidental complexity?

The clean-room minimum architecture exercise and the architectural compression rule are the same discipline applied differently.

---

## 3. Questions That Should Be Decomposed Across Levels

Several questions should not be forced into one level. The most important decompositions:

### A. Authority Boundary Comparison

- **EDASES:** Which authority roles must be non-agent? What are the invariants?
- **ASES:** What authority matrix should the methodology require?
- **Execution:** What mechanisms mechanically prevent unauthorized transitions?

### B. Execution Trust

- **EDASES:** Under what conditions is a probabilistic agent assertion trustworthy?
- **ASES:** What evidence transforms an untrusted agent result into an accepted result?
- **Execution:** How is that evidence captured, stored, and made non-repudiable?

### D. Merge / Integration Authority

- **EDASES:** Is correctness of an integrated set non-compositional? Who may assert collective safety?
- **ASES:** What integration methodology is required: batching, review, ordering?
- **Execution:** What merge queue, gate, and atomic integration machinery enforces it?

### G. Context Hydration vs Injection

- **EDASES:** Is discoverability itself an authority boundary?
- **ASES:** What is the context contract for a bounded task?
- **Execution:** What path allowlists, capability restrictions, and query boundaries enforce that contract?

### I. Substrate Failure and Self-Repair

- **EDASES:** Can an agent authoritatively repair the substrate that defines its own authority?
- **ASES:** Who is permitted to repair authority state, and under what procedure?
- **Execution:** How is inconsistency detected and reconciled?

### L. Liveness and Progress

- **EDASES:** What distinguishes activity from meaningful progress and terminal completion?
- **ASES:** What evidence must demonstrate progress?
- **Execution:** What monitors detect stall, loops, and non-progress?

### P. Verification and Review Architecture

- **EDASES:** What kind of confidence does each review type establish?
- **ASES:** What review workflow and evidence requirements should exist?
- **Execution:** How are review states and evidence represented as gates?

### C / N / O combined

- **EDASES:** What is durable truth versus ephemeral execution state?
- **ASES:** Which work facts must survive failure?
- **Execution:** How are restart, reconciliation, and process boundaries implemented?

---

## 4. Missing Research Questions

The most important missing questions are:

### 1. Human Authority, Override, and Exception Handling

Most of the current questions concern agent/system boundaries, but not the human boundary.

- Which decisions are non-delegable?
- What happens when a human is unavailable?
- What is the semantics of a human override?
- How are human judgments recorded as evidence?

This is not merely an ASES role question; it is an EDASES authority question.

### 2. Auditability, Provenance, and Non-Repudiation

The current inventory asks what evidence is, but not how that evidence remains trustworthy after the fact.

- Who can prove what happened?
- What is the chain of custody for a decision?
- Can an agent or system later repudiate a prior acceptance?
- What does a trustworthy audit log require?

### 3. Failure Containment, Cancellation, Rollback, and Revocation

There is substantial work on recovery, but not enough on containment.

- What is the blast radius of an agent action?
- How is authority revoked mid-task?
- What are cancellation and rollback semantics?
- How are partially completed side effects handled?

### 4. Security and Adversarial Participants

The current model treats agents as probabilistic but not adversarial.

- What happens under prompt injection?
- What if a reviewer model is compromised?
- What if an agent deliberately attempts to expand authority?
- What if a dependency or tool is malicious?

This is a major gap because many authority boundaries become security boundaries.

### 5. Empirical Evaluation and Falsification Methodology

The inventory contains research hypotheses, especially E and H, but no explicit empirical program for testing them.

- How do we know that heterogeneous review reduces correlated failure?
- How do we know that mechanical enforcement improves trustworthiness?
- What failure-injection experiments are needed?
- What would falsify the central hypothesis that agents should not be trusted with mechanically enforceable authority?

### 6. Work Decomposition Topology and Graph Expansion Control

The Gas Town observations mention pathological work-graph expansion, but the current questions do not make decomposition itself a first-class authority problem.

- Who may decompose work?
- Who may renegotiate scope?
- When is decomposition final?
- How is expansion prevented without introducing excessive coordination tokens?

### 7. Identity and Lineage

Execution identity is mentioned in passing, but there is no explicit question about the identity of:

- agents;
- sessions;
- work items;
- artifacts;
- reviews;
- evidence.

This matters for audit, recovery, and non-repudiation.

### 8. Resource Budget as an Authority Boundary

Token expenditure and quota are mentioned as concerns, but not treated as authority.

- Is budget a mechanical limit?
- Can budget exhaustion invalidate a completion claim?
- How should resource limits interact with liveness and recovery?

---

## 5. Reduced Set of Fundamental Research Tracks

The sixteen questions compress into six fundamental tracks.

### Track 1: Authority and Evidence

> Which facts require non-agent authority, and how do untrusted agent assertions become accepted evidence?

**Covers:** A, B, D, G, I, L, P, and parts of O.

This is the largest and most central track. Completion, verification, integration, progress, discoverability, and self-repair are all authority/evidence transformations.

---

### Track 2: Durable State and Work Substrate

> What is the correct unit of durable truth, and how is it separated from ephemeral execution state?

**Covers:** C, M, N, O, and parts of F.

This track includes work identity, dependencies, lifecycle, restart, reconciliation, and the Crosslink/Execution boundary.

---

### Track 3: Probabilistic Participants in Distributed Systems

> Which problems are ordinary distributed-systems problems, and which are qualitatively different because workers are probabilistic and non-authoritative?

**Covers:** E, K, L, and parts of C.

This track should test the working hypothesis in E rather than accept it.

---

### Track 4: Independent Verification and Model Diversity

> Can heterogeneous, independent review reduce correlated verification failure, and what verification quorum is required?

**Covers:** H, P, B, and parts of D.

This track is empirically testable and should not be collapsed into ordinary review methodology.

---

### Track 5: Context, Capability, and Discoverability

> Is information discoverability an authority boundary, and what is the minimum context contract for bounded execution?

**Covers:** G, A, and parts of O.

This track connects context hydration to authority rather than treating it as an efficiency concern.

---

### Track 6: Architectural Minimality and Compression

> How do we distinguish fundamental architecture from accidental or model-generated complexity?

**Covers:** F, J, and parts of M.

This track is methodological, but it is also a research discipline. It asks how EDASES itself should avoid accumulating mechanisms.

These six tracks are not entirely independent. If forced to compress further, Tracks 1 and 4 could merge into one larger “authority, evidence, and verification” track, but I would keep them separate because heterogeneous model verification is an empirical question of its own.

---

## 6. Strongest Argument Against the Three-Level Separation

The strongest argument is that the three-level model may create a false impression that research, methodology, and execution can be cleanly sequenced.

In practice, many of the most important questions are **one invariant expressed at three grain sizes**, not three separate problems. For example:

> “What constitutes trustworthy completion?”

cannot be fully answered at EDASES alone, because completion only becomes trustworthy if the Execution engine makes it impossible to record completion without external evidence. The methodology is not a later application of the principle; the mechanism is part of what makes the principle true.

Similarly, many ASES rules are themselves empirical hypotheses. The idea that heterogeneous reviewers reduce correlated failure is an EDASES research question, but it is also an ASES model-selection policy. If the levels are treated too rigidly, such questions may be classified as settled methodology when they are still open empirical claims.

The EDASES/ASES boundary is especially unstable. “What should agents be allowed to do?” can be stated as a research question about authority or as a methodology rule. The correct level depends on whether the claim is still in doubt.

Finally, Execution cannot be completely neutral. Any mechanical enforcement necessarily chooses defaults for unresolved methodological questions. Saying that Execution “should not silently decide” unresolved questions is useful discipline, but in practice it will always do so unless every such decision is explicitly surfaced.

The three-level model is useful for preventing premature implementation, but it is a project-management and abstraction discipline, not a natural ontology of the problem.

---

## 7. Areas Where Independent Researchers Will Likely Disagree Most

I expect the strongest disagreements in these areas:

### 1. Whether authority questions are EDASES or ASES

Many researchers will classify A, B, D, and I as ASES because they concern roles and policies. Others will classify them as EDASES because they concern fundamental authority invariants.

### 2. Whether durable state/restart questions are Execution or EDASES/ASES

Distributed-systems researchers may see C, N, and O as Execution. Methodology researchers may see them as durable work model questions. The correct answer is often cross-level, but independent reviewers will differ on the primary level.

### 3. Whether model capability matrix is fundamental research or operational routing

H can look like a cost/routing question to some, and like a reliability research question to others. The verification quorum idea makes it research, but not everyone will agree.

### 4. Whether context/discoverability is an authority boundary

Some will treat G as an ASES context-management problem. Others will see it as an EDASES authority boundary. The phrase “discoverability itself is an authority boundary” is likely to be controversial.

### 5. Whether integration authority is distinct from verification authority

D may be seen as a special case of P, or as a separate problem about non-compositional correctness. Researchers with merge-queue experience may classify it differently from those with verification background.

### 6. Whether architectural compression is research or design discipline

J sits awkwardly between EDASES and ASES. Some will say it is only a design rule; others will say it is a necessary research methodology for EDASES.

### 7. Whether the inventory compresses to one track or many

Some will argue that nearly everything reduces to “authority, trust, and evidence.” Others will resist that compression as too abstract and will prefer separate tracks for verification, state, context, and liveness.

### 8. Whether human governance belongs inside ASES or above the whole model

The missing human-authority questions may be seen as ASES roles, as EDASES invariants, or as a governance layer outside the three-level model entirely.

The main source of divergence is not confusion about the three levels. It is that many of these questions are genuinely cross-level, and the primary classification depends on what the researcher considers still open.