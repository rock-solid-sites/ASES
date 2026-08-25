# Hy3 Research Level Question

# Muse Spark 1.2 Research Level Classification

## 1. Proposed EDASES / ASES / Execution Taxonomy

Judging the *actual* research question behind each item, not its current implementation:

| Item | Primary Level | Secondary Level | Rationale (actual question) |
|------|---------------|-----------------|-----------------------------|
| **A** Authority Boundary Comparison | **EDASES** | ASES, Execution | Core question is *what authority must be mechanical vs prompt-enforced* — a fundamental principle. Survey of systems is empirical EDASES work. |
| **B** Execution Trust | **EDASES** | ASES, Execution | Asks what trust/evidence/completion *mean* fundamentally. Methodology and mechanics follow. |
| **C** Restart Survivability | **EDASES** | ASES, Execution | The question “what state is enduring truth vs reconstructable” is a state-semantics research question, not merely a durability-engine issue. |
| **D** Merge/Integration Authority | **EDASES** | ASES, Execution | “Who may declare collective safety” is an authority-principle question. Batching/Refinery are derived. |
| **E** DS + Probabilistic Participants | **EDASES** | — | Pure classification of novel vs inherited problems. |
| **F** Skeleton Factory / MVA | **EDASES** | ASES | Determines fundamental vs accidental complexity; methodology expresses the result. |
| **G** Context Hydration vs Injection | **EDASES** | ASES, Execution | “Is discoverability an authority boundary?” is a fundamental authority question. |
| **H** Model Capability Matrix | **EDASES** | ASES | Whether heterogeneous redundancy reduces correlated failure is a reliability-research hypothesis. |
| **I** Substrate Failure / Self-Repair | **EDASES** | ASES | “Agent must not repair its own authority substrate” is a foundational separation principle. |
| **J** Human Design vs Emergence | **EDASES** | ASES | Examines whether compression is hypothesis, rule, or discipline — meta-research on methodology. |
| **K** DS Prior Art | **EDASES** | — | Maps solved vs unsolved; identifies novel layer. |
| **L** Liveness and Progress | **EDASES** | ASES, Execution | Distinguishing process existence from meaningful progress is a fundamental semantic distinction. |
| **M** Crosslink / Work Substrate | **EDASES** | ASES, Execution | “What should durable work truth represent?” is foundational; where it lives is secondary. |
| **N** State / Durable Boundary | **EDASES** | Execution | “Correct unit of durable state” is a fundamental modeling question. |
| **O** RPC / Process Boundary | **ASES** | EDASES, Execution | The *methodological need* for a boundary is ASES; the principle of authority crossing is EDASES; protocol is Execution. |
| **P** Verification Architecture | **EDASES** | ASES, Execution | “What confidence does each review type establish?” is foundational; representation as evidence is methodology. |

---

## 2. Clusters That Should Be Combined

- **Authority–Trust–Evidence Cluster:** A, B, D, G (discoverability as authority), I (substrate authority), L (progress/completion), P (verification).  
  These are all manifestations of one deeper problem: *How is authority extracted from probabilistic workers and converted into mechanically-held, externally-verifiable evidence?*

- **Durable-State Cluster:** C, M, N, and parts of O.  
  Manifestation of: *What is the minimal enduring truth about work, and what is legitimately ephemeral?*

- **Novelty-vs-Inherited Cluster:** E, K.  
  Manifestation of: *What is genuinely specific to AI-agent software engineering versus ordinary distributed systems?*

- **Methodological Minimalism Cluster:** F, J.  
  Manifestation of: *How do we prove a mechanism is necessary rather than historical accident?*

---

## 3. Questions That Should Be Decomposed Across Levels

**B (Execution Trust)**
- **EDASES:** What constitutes execution evidence, and can a completion claim ever be authoritative?
- **ASES:** What verification protocol transforms untrusted agent output into accepted result?
- **Execution:** How does the substrate record evidence and block self-certified completion?

**D (Merge/Integration Authority)**
- **EDASES:** Who holds authority to declare individually-verified changes collectively safe?
- **ASES:** What integration methodology (batch, stack, queue, refinery) expresses that authority?
- **Execution:** What state machine enforces batching, locks, and integration testing?

**G (Context Hydration)**
- **EDASES:** Is unbounded discoverability itself an authority violation?
- **ASES:** What context-contract methodology bounds a task?
- **Execution:** What scoped access / path allowlist mechanically enforces it?

---

## 4. Most Important Missing Research Questions

1. **Human Authority & Accountability** — The inventory discusses agent/model authority heavily but never asks: *What must a human explicitly authorize, and who is accountable when verified-but-wrong software ships?* This is neither settled nor merely Execution.
2. **Adversarial Robustness of the Substrate** — Prompt injection, agent hijacking, or malicious model output attempting to exploit Execution Engine capabilities. Currently implied but not called out as a research track.
3. **Cost/Token Accountability as Methodological Constraint** — The project lists “excessive token expenditure” as a failure mode, but no open question asks how ASES should *bound* economic cost as a first-class policy rather than an optimization afterthought.
4. **Evaluation Metrics for “Trustworthy”** — Without a research-level definition of how trustworthiness is measured empirically, EDASES claims are unfalsifiable.
5. **Observability as Research Feedback** — How do we instrument the Execution Engine so that EDASES hypotheses (e.g., about doom loops) are empirically testable rather than speculative?

---

## 5. Proposed Reduced Set of Fundamental Research Tracks

The inventory compresses to **four** tracks, not sixteen:

1. **Authority & Evidence (A, B, D, G, I, L, P)**  
   The single question: *How is irreversible authority removed from probabilistic actors and replaced by external, durable evidence?*

2. **Durable Truth & Recovery (C, M, N, O)**  
   The single question: *What is the minimal state that must survive any failure, and where does ephemeral execution legitimately begin?*

3. **Probabilistic Distributed Systems Theory (E, K)**  
   The single question: *Which failure modes are inherited, which are transformed, and which are novel because workers are LLMs?*

4. **Methodological Discipline & Minimalism (F, J, H)**  
   The single question: *How do we prove a control (including heterogeneous models) is a necessary reliability primitive rather than accretion?*  
   (H fits here because it asks if model heterogeneity is a structural control, not a routing tactic.)

---

## 6. Strongest Argument Against the Three-Level Separation

The EDASES → ASES → Execution model implies a **one-directional pipeline**: research settles principles, methodology encodes them, execution enforces them.  

In reality, **execution failures recursively reshape research**. For example, C (restart survivability) is tagged EDASES-primary above, but in practice the inability of a runtime to reconstruct state *reveals* what the fundamental unit of durable truth must be. If you forbid Execution from informing EDASES, you risk specifying principles that are physically unrealizable, then silently resolving the contradiction in the Execution layer — exactly the “unresolved methodological questions decided silently by tooling” failure mode the project itself warns against.  

Additionally, **ASES risks becoming an overloaded middle layer** where anything not “fundamental enough” for EDASES and not “mechanical enough” for Execution gets parked, blurring the very distinction you want independent researchers to test.

---

## 7. Areas Where Independent Researchers Will Disagree Most

- **H (Model Capability Matrix):** Is heterogeneous verification a *fundamental* EDASES reliability primitive, or merely a tactical ASES cost/quality lever? Reasonable researchers will split.
- **G (Discoverability as Authority):** Whether letting an agent freely read the repo is an authority boundary violation (EDASES) or just a scoping config (Execution) is genuinely ambiguous.
- **I (Substrate Self-Repair):** The hypothesis “agent must never repair its own authority substrate” is clean, but emergency recovery scenarios may force a qualified exception — researchers will disagree on absolutism vs contingency.
- **L (Liveness/Progress):** How much of “meaningful progress” can be *mechanically* enforced vs inferred from model behavior. The line is unclear and level-assignment flips depending on answer.
- **O (RPC/Process Boundary):** Whether the boundary is a methodological necessity (ASES) or a fundamental authority-separating invariant (EDASES) will provoke disagreement because the question is phrased at the wrong abstraction level today.