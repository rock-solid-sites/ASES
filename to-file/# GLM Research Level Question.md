# GLM-5.3 Research Level Question

## 0. The Main Structural Finding (Read First)

Before per-question classification, one finding dominates everything else:

**The three levels do not partition the questions. They partition the *answers*.**

Of the sixteen questions, almost none is naturally "an EDASES question" or "an Execution question." Nearly every one is a single underlying question that legitimately has three level-appropriate formulations. The three-level model does emerge — but as an *answer structure*, not as a sorting criterion. This matters for how the comparative exercise should be read: researchers who sort questions into boxes will produce apparent divergence that is actually an artifact of method. Researchers who decompose questions will converge strongly.

A second structural finding: the inventory contains **no ASES-native research questions and no Execution-native research questions** as currently written. Everything is framed from the fundamental-trust side. This is not necessarily wrong, but it means the three-level model is being tested only at the layer where it is most confident (EDASES). The underweighted levels are where the missing questions live (§4).

---

## 1. Per-Question Classification

| Q | Primary level | Genuinely spans | Cluster | Key judgment |
|---|---|---|---|---|
| **A** | EDASES (comparative empirical) | ASES (policy output), Execution (enforcement column) | Authority | A research *method*, not a question. Its proposed decomposition is action-centric and omits the knowledge/visibility axis (G). |
| **B** | EDASES (epistemology of agent claims) | All three | Evidence | The generic form of P, D, H, L. Its authority half is partially pre-settled by the program's own enforcement principle. |
| **C** | EDASES core (durability semantics); Execution surface | All three | Substrate | Same underlying question as N and M, viewed from the failure angle. Its sub-items (quota parking, admission control) are Execution mechanisms serving an ASES policy question. |
| **D** | EDASES (collective-vs-individual correctness; integration authority) | ASES (integration methodology), Execution (machinery) | Evidence | Batching machinery is prior art. The open content is authority + compositionality semantics. |
| **E** | EDASES | — | Novelty | The framing hypothesis. Upstream of the taxonomy itself: its resolution reclassifies C, L, M, N, O. |
| **F** | EDASES (as method: necessity ablation) | Outputs land in ASES/Execution | Discipline | The empirical arm of J. Its proposed vocabulary is suspiciously isomorphic to generic workflow ontologies. |
| **G** | Decomposes: EDASES (knowledge as authority; minimum-context empirics) | ASES (context contracts), Execution (enforcement) | Authority | The strongest candidate for a genuinely agent-specific problem. See note below. |
| **H** | EDASES (decorrelation hypothesis) | ASES (quorum/reviewer selection), Execution (routing) | Evidence | Mis-framed as stated: needs an *error-correlation* matrix, not a capability matrix. |
| **I** | EDASES (root of trust / TCB) | ASES (repair and escalation protocols), Execution (safe mode, reconciliation) | Authority | A trusted-computing-base argument. Its authority chain terminates in humans — whom the inventory never studies. |
| **J** | EDASES (fundamental vs. accidental complexity) | Rule-form belongs to ASES governance | Discipline | A meta-question about the research program. It applies to the three-level taxonomy itself. |
| **K** | EDASES | — | Novelty | Should be dissolved: it is the literature arm of E plus per-question prior-art checks. |
| **L** | EDASES (liveness ontology) | ASES (enforce vs. infer), Execution (detection) | Evidence / Substrate | The novel nugget is the activity≠progress gap for token-emitting workers; the rest is classic failure-detector prior art. |
| **M** | EDASES core (work ontology) / Execution surface (partitioning) | ASES (what methodology requires the substrate to express) | Substrate | Merge with N and C. |
| **N** | EDASES (unit of durable state) | Execution (representation) | Substrate | The sharpest formulation of the substrate cluster. The novel edge: durable *evidence and reasoning context*, not workflow state. |
| **O** | Execution | EDASES core duplicates A/I | (dissolves) | Mostly mechanics with prior art; its research content reduces to trust boundaries already present elsewhere. |
| **P** | EDASES (review→confidence taxonomy) | ASES (review methodology), Execution (evidence representation) | Evidence | "Evidence, not conversation" is nearly settled by the program's own principles. Open: evidence ontology and sufficiency conditions. |

### Notes on the non-obvious calls

**A** is an empirical program (comparative study of authority regimes), which the EDASES charter explicitly includes. Its proposed five-way decomposition conflates normative categories (authority types) with a descriptive one (enforcement mechanism). It also needs a sixth dimension: *knowledge/visibility authority* (what an agent may discover), which is G's territory. Expect disagreement about whether comparative system study is "research" or a survey feeding ASES.

**B** — "Can an agent's completion claim ever be authoritative?" is partially pre-settled by the project's own central principle (mechanical enforcement over agent trust). The genuinely open content is the escape clause: *when is external verification impossible or costlier than the risk, and what is the fallback?* Also, B's verification half ("how do untrusted results become accepted?") is the parent of P, D, H, and half of L. B is the generic form; those are specializations.

**F** — the clean-room vocabulary (Work Item, State Transition, Agent Session, Execution Evidence, Dependency, Artifact, Event, Policy) is nearly isomorphic to standard workflow/orchestration ontologies. This is either confirmation of E (the substrate is ordinary) or evidence of contamination. Notably, the vocabulary **omits the concepts the program's own principles emphasize most**: reviewer, model identity/diversity, context contract, verification depth. A minimum vocabulary missing those would structurally under-express ASES. The vocabulary itself needs to be treated as a hypothesis, not a starting point.

**G** contains what I believe is the single most underrated idea in the inventory: restricting context is not classical access control. In classical security, restricting knowledge prevents *disclosure*. In agent systems, restricting context also *shapes competence* — ignorance is a capability limiter and a behavior shaper, not merely a confidentiality control. A context-starved agent is not a leaked-to agent; it is a *different, more bounded* agent. This inversion is a strong candidate for a genuinely agent-specific phenomenon and feeds directly into E.

**H** as framed ("model capability matrix") asks the wrong question. Reviewer diversity for reliability requires knowing how *errors correlate*, not what models are good at. Capability benchmarks and failure correlation are different objects: two strong models can share a blind spot. The prior-art warning is severe — Knight and Leveson's N-version programming experiments showed independently designed implementations failing correlated on the same inputs. LLMs trained on overlapping corpora are a worst case for that failure mode. The research question should be reframed: *do heterogeneous models exhibit sufficiently decorrelated verification failures to support quorum-based trust, and can we measure the correlation structure?*

**I** is a TCB argument: an agent cannot be the ultimate authority for repairing the substrate that defines its authority, because that's circular. Fine — but then the authority chain must terminate somewhere, and the only candidates are humans plus deterministic machinery. This pushes the *human* into the center of the trust architecture, and no question in the inventory studies humans. I is where the missing human question becomes unavoidable.

**L** — the six-level hierarchy (process existence → … → terminal completion) is a genuine conceptual contribution. The prior art (failure detectors, watchdogs, heartbeats) covers the bottom levels; the novel level is the gap between *tool activity* and *meaningful progress*, because a token-emitting worker can simulate activity indefinitely while making no state transitions. That gap is only closable via the evidence ontology of B/P — which is why L belongs half in Evidence, half in Substrate.

**N** — "What is the correct unit of durable state?" is the sharpest formulation of the entire substrate cluster. The prior art (Temporal, event sourcing, workflow engines) answers "workflow state." What prior art does *not* answer is what is arguably the actually-novel durable content in agentic SE: evidence, verification history, and reasoning context. The Molecules/Wisps distinction is the generic durable/ephemeral distinction wearing local names.

**O** — decompose and mostly dissolve. Its EDASES core ("where must trust boundaries exist across processes?") is a duplicate of A/I content. Its ASES content ("what must cross boundaries as methodology") is real but thin. Its mechanics (RPC vs. event vs. plugin) are prior art and engineering choice. O should not survive as a standalone question.

---

## 2. Clusters That Should Be Combined

**Cluster 1 — Authority.** A + G + I + O's core + the authority aspects of B, D, and J.
One underlying question: *where may the right to establish facts and perform actions reside — over actions (A), over knowledge (G), over the substrate itself (I), over process boundaries (O), over completion (B), over integration (D)?*

**Cluster 2 — Substrate / Durable Truth.** C + M + N (+ L's state aspects).
One underlying question viewed three ways: from the state-modeling side (N), the design side (M), and the failure side (C). These are not three questions. "What must survive restart" (C) is operationally identical to "what is the correct unit of durable state" (N); M is just the question asked about a particular component.

**Cluster 3 — Evidence / Verification.** B + P + H + D (+ L's progress aspects).
One underlying question at three scopes: unit-level (P, B), set-level (D), and temporal (L: progress as evidence over time). H is the empirical hypothesis about one mechanism (diversity) inside this cluster.

**Cluster 4 — Novelty / Prior Art.** E + K (+ F as partial test).
K should not exist independently; it is E's literature arm. The individual prior-art items dissolve into other clusters as mandatory "prior-art check" sub-steps: Temporal → C/N, Kubernetes reconciliation → I/C, Bors/merge queues → D, failure detectors → L, N-version programming → H, feature-interaction literature → D.

**Cluster 5 — Complexity Discipline.** F + J.
J is the analytical discipline ("prove the requirement can't be expressed more simply"); F is its empirical test (rebuild from scratch and see what re-emerges). F is what makes J falsifiable rather than aesthetic.

---

## 3. Questions That Decompose Across Levels

The triadic pattern recurs. Worked examples:

**B — Execution Trust**
- *EDASES:* What is the epistemic status of a probabilistic worker's assertions? Can any claim class (completion, state, intent, progress) be self-authoritative, and under what verification-cost conditions is the answer yes?
- *ASES:* What protocol — evidence requirements, independent verification, reviewer diversity, verification depth by risk class — transforms an untrusted result into an accepted one?
- *Execution:* What machinery captures evidence, gates transitions on evidence, and makes self-attestation structurally impossible?

**C — Restart Survivability**
- *EDASES:* What is the semantics of durability — which facts about work are invariants across substrate failure? Is the substrate's single-point-of-failure status necessary or contingent?
- *ASES:* What recovery methodology is acceptable — bounded, idempotent, evidence-preserving? What may be reconstructed versus must be restored?
- *Execution:* Persistence, restart, reconciliation, admission control, quota parking, doom-loop guards.

**G — Context**
- *EDASES:* Is knowledge-access an authority boundary distinct from action authority? (Empirical arm: what minimum context enables reliable execution?)
- *ASES:* Context contracts, hydration policies, scoping rules per work-item type.
- *Execution:* Path allowlists, capability restrictions, query boundaries.

The same decomposition applies cleanly to I, L, N, and P. This recurrence is itself a result: **the three-level model is independently confirmed as an answer structure**, but it predicts that every mature research question will eventually have all three forms, so classifying a question wholesale to one level is a sign the question is either immature or mis-framed.

---

## 4. Missing Research Questions

Ranked by importance:

**1. Threat model: incompetence vs. adversarial behavior.** The entire inventory assumes workers are *unreliable* (probabilistic failure). Nothing addresses workers that are *compromised or adversarial* — prompt injection, exfiltration through context, confused-deputy scenarios where an agent's legitimate authority is hijacked. Authority design differs radically under crash-fault versus Byzantine assumptions; the E hypothesis says "non-authoritative, probabilistic," which quietly chooses the fault model without defending it. EDASES-level question: *what is the correct fault model for agentic SE participants, and which ASES mechanisms change if it is adversarial?* Currently homeless, and it potentially reorders the Authority cluster.

**2. The human.** Authority chains (I), final acceptance (P), substrate repair (I), and methodology governance (J) all terminate in humans — yet no question studies human authority, human attention as a scarce resource, when human judgment is the correct verification mechanism, or human failure modes (rubber-stamping, escalation fatigue). EDASES-level question: *what is the human's role in the trust architecture, and what are its scaling limits?*

**3. Decomposition and granularity.** "Pathological work-graph expansion" is listed as a named failure mode and *no question in A–P owns it*. Who decides decomposition, what granularity suits probabilistic workers, what bounds graph growth, what is the lifecycle of abandoned subgraphs? This is the most ASES-native question in the entire space and its absence is the clearest evidence that the inventory is substrate-heavy and methodology-light.

**4. Evaluation and failure-mode empirics.** How would anyone know EDASES/ASES works? No question establishes a failure-mode taxonomy with observed frequencies, or the metrics for "verifiably trustworthy." Note that EDASES's charter currently bundles two different activities — normative truth-seeking and empirical falsification programs — and the evaluation *of the methodology itself* fits neither cleanly. This suggests either a missing fourth activity or an overloaded EDASES.

**5. The ASES/Execution formal interface.** For "Execution must not silently decide methodology" to be more than aspiration, ASES must be expressible in a formalism from which Execution can be derived and against which it can be checked. What formalism? This sits exactly on the layer boundary and is absent. (This is also the crux of §6.)

**6. Economics of verification.** Every trust mechanism costs tokens, money, and latency. H's verification quorum is the most expensive proposal in the inventory and has no cost model. *What is the optimal verification intensity per unit of work, and how should a bounded trust budget be allocated across review layers?*

Honorable mentions: **knowledge vs. work state** (architectural amnesia and assumption drift are named failure modes; the substrate cluster covers work state, but durable *understanding* — design intent, architectural rationale — has no owning question beyond per-session context); and **model-generation invariance** (which EDASES claims survive the next model generation — the three levels have no time axis, and a methodology pinned to current capabilities is stale on arrival).

---

## 5. Reduced Set of Fundamental Research Tracks

Sixteen questions compress to **five tracks**:

**Track 1 — Authority.** *Where may the right to establish facts and perform actions reside in a system whose participants are probabilistic and non-authoritative — across actions, knowledge, state, completion, integration, and the substrate itself?*
(A, G, I, O-core, authority aspects of B/D, governance aspect of J.)

**Track 2 — Durable Truth.** *What is the enduring reality of work — its correct unit, its relation to ephemeral execution, and its behavior under failure, disagreement, and repair?*
(C, M, N, state aspects of L.)

**Track 3 — Evidence.** *By what transformations do untrusted claims become accepted results — at unit level, at set level, and over time?*
(B, P, H, D, progress aspects of L.)

**Track 4 — Novelty.** *Which of these are prior distributed-systems problems, and what exactly changes when the worker is an LLM?*
(E, K, F-as-test.)

**Track 5 — Complexity Discipline.** *How does the program distinguish fundamental from accidental complexity and prevent mechanism accretion?*
(J, F.)

Two observations on this compression. First, tracks 1–3 have a clean philosophical structure — Authority is *deontic* (who may), Truth is *ontological* (what is), Evidence is *epistemic* (what convinces) — which suggests the compression is real rather than convenient. Second, this partially validates but also corrects the example hypothesis in the brief: "authority, trust, and evidence" as one deeper question over-compresses. Authority and Evidence are distinct (one can change evidence standards without changing who holds authority, and vice versa), and the example omits Track 2, which I judge equally fundamental. Compression below five tracks loses structure; compression to five from sixteen loses little.

---

## 6. The Strongest Argument Against the Three-Level Separation

**The ASES/Execution boundary is unstable, because enforcement machinery is semantics-bearing.**

The charter requires that Execution "not become the place where unresolved methodological or research questions are silently decided." But a state machine's transition relation *is* methodology. Deciding that a work item moves from Verified to Integrated only through a merge-queue gate is a methodological commitment, materialized as machinery. There is no such thing as neutral enforcement: every mechanical decision either (a) follows from an ASES rule formal enough to derive it, or (b) silently decides methodology. The separation is therefore only real if ASES is a formal specification from which Execution is semi-derivable and against which it is checkable — and the existence and sufficiency of such a formalism is itself an open research question that the inventory does not contain. Absent it, the three levels are a statement of intent about where decisions *should* be made, not a structural guarantee about where they *are* made. Methodology will leak into machinery, invisibly, precisely because the machinery cannot help embodying it.

Secondary weaknesses, in descending strength:

- **Epistemic direction is inverted.** The layering implies truth → methodology → machinery as a knowledge flow. The project's own history contradicts this: Gas Town's lessons came from building and failing, not from theory. The levels work as a *responsibility* partition (who owns which decisions) but not as a *knowledge-flow* model. Taking the derivation direction literally would starve EDASES of its main source of evidence.
- **Missing homes.** Evaluation of the methodology itself and governance of methodology change fit no level cleanly (§4, items 4–5), and EDASES is already double-loaded with normative and empirical programs.
- **No time axis.** The model is static while its subject (model capabilities) turns over monthly.

---

## 7. Where Independent Researchers Will Disagree Most

1. **The durability cluster (C/M/N): EDASES or Execution?** This is the largest predicted split. It turns on whether "the correct unit of durable state" is a novel ontology or applied event-sourcing. The prompt's own warning ("a Rust state machine may belong at EDASES") cuts both ways — researchers with distributed-systems backgrounds will push C/M/N down to Execution; researchers from the trust/verification side will pull them up.

2. **E's status: root framing or dangerous analogy?** Some will treat the probabilistic-participants hypothesis as the foundation that organizes everything (as I mostly do). Others will argue it imports assumptions that don't hold — distributed systems have no "methodology" layer, their workers aren't shaped by their input context, and analogy-driven design is exactly the mechanism-complexity generator J warns against. Notably, E is *meta* to this exercise: its resolution reclassifies half the inventory.

3. **Where J lives.** The question explicitly offers three homes, so disagreement is guaranteed. It will track a deeper split: whether researchers regard methodology design as research (EDASES) or engineering practice (discipline).

4. **Whether G is novel.** Security-background researchers will call discoverability-as-authority "need-to-know access control, rediscovered." Agent researchers will argue the competence-shaping effect of context (ignorance as a capability limiter, not a confidentiality control) makes it a genuinely new boundary type. I hold the latter view, but expect a fight.

5. **H: decorrelation optimism vs. pessimism.** The Knight–Leveson prior (independent designs, correlated failures) vs. the intuition that heterogeneous training produces heterogeneous blind spots. Also whether the question is mis-framed (capability matrix vs. error-correlation matrix), as I argue.

6. **Whether Execution has any research content.** One camp will say Execution is engineering, full stop — and note the inventory contains zero Execution-native questions as evidence. The other will identify substrate trustworthiness (low-TCB enforcement, auditable enforcement, self-verifying substrate) as legitimate systems research — which is where I lands.

7. **Whether the comparative study (A) is research.** Empirical comparison of existing systems as EDASES-level inquiry vs. mere survey work that feeds ASES policy.

8. **Whether the human deserves question-status** or is merely ambient context. I believe the absence of the human question is the inventory's largest single gap (§4.2); others will consider it out of scope for a system-design program.

---

## Summary of Independent Findings

- The three-level model **does** emerge — but as a triadic answer-structure applying to nearly every question, not as a sorting of questions. Wholesale single-level assignments are mostly artifacts of immature framing.
- Sixteen questions compress to **five tracks**: Authority (deontic), Durable Truth (ontological), Evidence (epistemic), Novelty, Complexity Discipline.
- C, M, and N are one question; K should be dissolved into E; O should be dissolved into the Authority cluster plus prior art.
- The inventory is EDASES-heavy and contains no ASES-native or Execution-native research questions; the most important gaps (threat model, human authority, decomposition/granularity, evaluation, the ASES/Execution formal interface, verification economics) lie precisely in and around the underweighted levels.
- The strongest objection to the three-level separation is that the ASES/Execution boundary cannot be kept clean without a formal specification relationship that is itself an unstated research problem. The model is best defended as a responsibility partition, not a knowledge-flow pipeline.