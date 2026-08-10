---
title: "EDASES Phase 3 Retrospective"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - docs/research/Workflow Topology Design and Reasoning Record.md

consumed_by:
  - EDASES Phase 4 Retrospective

supersedes:
  - EDASES Phase 2 Retrospective

superseded_by:
  - EDASES Phase 4 Retrospective

last_updated: 2026-08-10
---

# EDASES Phase 3

## Retrospective

### 1. Purpose

This phase began with an anomalous fresh-session interaction with Gemini 3.1 Pro Preview and developed into a broader examination of how agentic development systems reconstruct project state, validate their own understanding, enforce authority, and determine where those controls should live.

The discussion connected this incident to the existing ASES/EDASES architecture, Crosslink, OpenClaudia, Thermite, and OpenCode.

The central result was a distinction between **project knowledge**, **project-state reconstruction**, **epistemic validation**, and **agent execution**. The discussion ultimately questioned whether the latter should be the architectural home for the former concerns.

---

# 2. Initial Incident

A fresh Gemini 3.1 Pro Preview session was given access to project material concerning multi-agent orchestration and decision architecture.

The session had no prior conversational context.

The document had originally been authored by Gemini, and a previous Gemini interaction had confidently suggested that the document together with the Crosslink knowledge base would be sufficient for a new conversation to understand the project.

The experiment challenged that assumption.

The model recovered a number of the project's concepts, but did not preserve their exact intended meanings. It subsequently behaved as though its reconstructed understanding was sufficiently reliable to proceed.

The failure became substantially stranger later in the session.

Gemini began discussing:

* physical manufacturing,
* different manufacturing methods,
* additive manufacturing,
* injection molding,
* manufacturing cost structures,
* and repeatedly Woodrow Wilson.

None of these subjects belonged to the referenced Crosslink material. The Crosslink document concerned multi-agent orchestration and decision architecture, not physical manufacturing.

The session eventually entered a severe repetition failure involving hundreds of lines of repeated `producing` output. Those repetitions were excluded from the preserved transcript.

---

# 3. Initial Interpretation: Reconstruction Failure

The first interpretation of the incident focused on a problem that appeared directly relevant to EDASES.

The fresh model had not simply failed to understand the project.

It had recovered enough information to construct a plausible model of it.

The problem was that the model's reconstruction was imperfect while its confidence appeared to exceed what the available evidence justified.

This produced an important distinction:

> **Retrieving knowledge is not the same thing as knowing that the reconstructed model is sufficiently accurate.**

A retrieval failure might look like:

```text
I don't know what this project is.
```

The observed behavior was closer to:

```text
I understand what this project is.
```

followed by interpretations that were only partially grounded in the source material.

This was considered considerably more important to EDASES than ordinary hallucination because autonomous orchestration depends not merely on possessing information but on determining whether one's understanding is sufficient for the action being contemplated.

---

# 4. Crosslink and the Intended Solution

This immediately connected the incident to Crosslink.

Crosslink was already intended to solve many of the problems surrounding:

* persistent project memory,
* knowledge sharing,
* session continuity,
* project state,
* multi-agent coordination,
* issue tracking,
* design-document-driven work,
* and recovery after interruption.

The discussion therefore initially treated the Gemini failure as evidence that Crosslink's knowledge architecture might be incomplete as an autonomous-agent substrate.

The more precise conclusion became:

> Crosslink may be capable of transmitting substantial project knowledge without necessarily guaranteeing faithful reconstruction of that knowledge by a fresh agent.

This distinction matters because a sophisticated knowledge base can actually make a failure more dangerous.

An agent can retrieve enough coherent information to construct a highly plausible interpretation while silently filling gaps with inference.

The danger is not ignorance.

It is **confidently coherent error**.

---

# 5. The Proposed Verification Mechanism

The first proposed mitigation was a pre-execution reconstruction and verification process.

The agent would first be required to produce an explicit model of the project, including:

* current phase,
* project goals,
* implementation state,
* assumptions,
* open questions,
* confidence,
* and evidence.

A second agent would then perform an adversarial review of that reconstruction.

The review would specifically search for:

* unsupported claims,
* inferred facts presented as facts,
* missing uncertainty,
* mismatches between claimed readiness and available evidence.

The idea was not to have the second agent independently solve the project.

It would instead attack the first agent's reconstruction.

This produced a proposed workflow:

```text
Bootstrap
    ↓
Reconstruction
    ↓
Adversarial Validation
    ↓
Execution
```

The key shift was from validating the work product to validating the agent's understanding of the environment in which the work product would be produced.

---

# 6. The Infinite Verification Problem

A major objection was immediately identified.

If every understanding must itself be verified, then the verifier's understanding could require verification, followed by verification of the verifier, and so on:

```text
Verify understanding
    ↓
Verify verification
    ↓
Verify verifier
    ↓
...
```

This introduces an effectively recursive verification problem.

The discussion concluded that the solution cannot be absolute certainty.

Instead, verification must be **bounded by the action being considered**.

The relevant question becomes:

> Is the agent's understanding sufficiently reliable for the next decision?

rather than:

> Is the agent's understanding completely correct?

This produced the idea of **decision-weighted confidence**.

Low-risk actions could require relatively little confidence.

Higher-risk actions would require progressively stronger evidence.

For example:

| Action                  | Relative confidence requirement |
| ----------------------- | ------------------------------- |
| Summarize documentation | Low                             |
| Create an issue         | Low                             |
| Propose architecture    | Medium                          |
| Modify architecture     | High                            |
| Direct builders         | Very high                       |
| Merge changes           | Extremely high                  |

This prevents verification from becoming an infinite process because the verification requirement is tied to a concrete action.

---

# 7. Externalizing Uncertainty Instead of Eliminating It

The discussion then moved toward a second refinement.

Rather than trying to make the agent prove that its worldview was correct, the system could require the agent to externalize:

* what it believes,
* what it assumes,
* why it believes it,
* what evidence supports it,
* and where uncertainty remains.

This aligns naturally with the existing ASES structures:

```text
assumption registers
        ↓
decisions
        ↓
outcomes
        ↓
validation
```

These artifacts already treat uncertainty as something to be managed rather than something that must be eliminated before action.

The proposed direction therefore became:

> Make uncertainty explicit and govern action according to it.

This was considered more scalable than attempting recursive certainty.

---

# 8. The Possibility of Cheap Verification

The next question was whether this verification mechanism would require expensive frontier models.

The conclusion was that much of the proposed work is substantially narrower than general-purpose orchestration.

A verifier does not necessarily need to solve the project.

It can instead perform tasks such as:

```text
For each claim:
    Is it supported?
    Is it partially supported?
    Is it unsupported?
    What evidence supports it?
    What assumptions are being made?
```

This is closer to evidence tracing and classification than open-ended architecture generation.

That suggests the possibility of using relatively inexpensive models for verification while reserving more capable models for orchestration and difficult reasoning.

A conceptual pipeline emerged:

```text
Frontier Orchestrator
        ↓
Cheap Evidence Verifier
        ↓
Cheap Assumption Checker
        ↓
Cheap Consistency Checker
        ↓
Tests / Execution
```

The central economic insight was:

> Verification may be substantially cheaper than generation.

This also makes the mechanism attractive for automatic integration into development pipelines.

---

# 9. The Existing Tooling

The discussion then examined whether this functionality was already gestured toward by existing agent systems.

Three projects became particularly relevant:

* Crosslink
* OpenClaudia
* Thermite

## Crosslink

Crosslink appeared to provide much of the persistent project-state and knowledge infrastructure:

* project knowledge,
* issue tracking,
* continuity,
* coordination,
* session recovery,
* and structured project information.

The conclusion was not that Crosslink had solved epistemic validation, but that it supplied much of the substrate on which such validation could operate.

## OpenClaudia

OpenClaudia appeared to provide a different set of relevant mechanisms:

* memory,
* persistence,
* task tracking,
* subagents,
* adversarial review,
* hooks,
* guardrails,
* coordination,
* and workflow enforcement.

Its enforcement philosophy appeared directionally correct.

However, the discussion identified a potential abstraction-boundary problem.

OpenClaudia's enforcement operates primarily within the agent execution environment.

The Gemini incident suggested that some important failures happen **before execution**.

The agent can construct an incorrect model of project reality before any tool call, code modification, or builder action occurs.

Thus:

> The enforcement mechanism may be correct while being located at the wrong architectural layer.

---

# 10. The Harness Question

This led to a broader question:

> Does this tooling actually belong in the agent harness?

The initial temptation was to implement the mechanism as:

* hooks,
* middleware,
* guards,
* pre-task checks,
* or execution gates.

That would be practical.

But the discussion identified a conceptual problem.

Questions such as:

```text
What phase is the project in?
Which assumptions remain unresolved?
Is this architectural decision validated?
What authority does the agent have?
Is the reconstructed state sufficient for this action?
```

are not fundamentally harness questions.

They are project-level questions.

Putting them inside a particular harness risks coupling the project's governance methodology to:

* OpenCode,
* Claude Code,
* OpenClaudia,
* Gemini CLI,
* or whichever execution system happens to be in use.

That suggested a different abstraction boundary.

---

# 11. A Possible Layered Architecture

The discussion converged toward a conceptual architecture resembling:

```text
                    EDASES / Project Governance
                              │
             ┌────────────────┼────────────────┐
             │                │                │
        Knowledge           State          Validation
          Layer             Layer             Layer
             │                │                │
             └────────────────┼────────────────┘
                              │
                       Execution API
                              │
                     Agent Harnesses
                              │
                           Models
```

Under this model:

### Knowledge Layer

Provides:

* research,
* assumptions,
* decisions,
* rationale,
* specifications,
* handoffs,
* persistent project knowledge.

Crosslink appears relevant here.

### State Layer

Tracks:

* current phase,
* active questions,
* unresolved assumptions,
* blocked work,
* current operational state,
* and last-known validated state.

This is distinct from historical knowledge.

### Validation Layer

Evaluates:

* what the agent believes,
* evidence for those beliefs,
* confidence,
* unsupported assumptions,
* contradictions,
* and whether confidence is sufficient for the proposed action.

### Execution Layer

Actually performs work through:

* OpenCode,
* OpenClaudia,
* Claude Code,
* Gemini CLI,
* or future agent harnesses.

Under this model, the harness becomes an execution backend rather than the ultimate authority.

---

# 12. The "Project OS" / "Agent OS" Concept

This discussion connected strongly with Doll's description of Thermite as an **Agent Operating System**.

The distinction became useful:

### Agent Harness

Primarily answers:

> How does an agent execute?

### Agent Operating System

Potentially answers:

> How do agents, knowledge, state, policies, capabilities, workflows, and authority coexist and interact over time?

This makes the OS analogy more useful than treating Thermite merely as another coding harness.

The discussion deliberately avoided taking the analogy too literally.

The important question is:

> What resources does the system actually govern?

For the emerging ASES architecture, those resources appear less like CPU and memory and more like:

* knowledge,
* project state,
* assumptions,
* confidence,
* authority,
* capabilities,
* and decision rights.

This led to the tentative characterization of the desired system as closer to a **governance kernel** than a conventional computational kernel.

---

# 13. Capability Gating

A particularly useful architectural idea emerged from this distinction.

Instead of the harness itself deciding whether an action is acceptable, the higher-level system could issue or deny an explicit capability.

Conceptually:

```json
{
  "capability": "architecture_modification",
  "confidence": 0.89,
  "validated_against": [
    "decision-register/...",
    "validation-plan/..."
  ],
  "expires": "..."
}
```

The execution harness would then be responsible for enforcing the capability rather than independently determining whether the agent had earned it.

This produces a separation between:

```text
Authority
```

and:

```text
Execution
```

The agent can request an action.

The governance layer determines whether the action is authorized.

The harness executes only within the authority granted to it.

This was considered a potentially important direction for EDASES.

---

# 14. The More General Architectural Insight

The conversation repeatedly returned to the idea that the EDASES research questions had been moving upward in abstraction.

The progression was roughly:

```text
How should agents coordinate?
        ↓
How should project state persist?
        ↓
How should assumptions be managed?
        ↓
How should project state be reconstructed?
        ↓
How do we know reconstruction is sufficient?
        ↓
Who has authority to decide that it is sufficient?
```

This suggested that EDASES may ultimately be less about designing an agent harness and more about designing a **methodology and governance layer for agentic software engineering**.

The execution harness remains important, but it may not be the correct location for the project's fundamental controls.

---

# 15. The Gemini Failure Revisited

Later inspection of the complete captured Gemini transcript changed the interpretation of the incident.

The manufacturing and Woodrow Wilson material did not appear to be merely an extended analogy from the Crosslink "factory floor" metaphor.

The unrelated material was highly specific and included:

* additive manufacturing,
* injection molding,
* SLS/FDM/SLA-related discussion,
* manufacturing cost analysis,
* and a historical discussion involving Woodrow Wilson.

These topics were absent from the Crosslink project material being analyzed.

The sequence therefore appears to contain at least two distinct failure modes:

```text
1. Imperfect project reconstruction
2. Severe unrelated-content / runtime corruption
```

The later failure also included the extended `producingproducingproducing...` repetition.

The exact cause of the second failure was not established.

Possible explanations considered included:

* retrieval contamination,
* context-stream corruption,
* planner/state corruption,
* model-specific failure,
* runtime failure,
* or other infrastructure-level defects.

No specific mechanism was established.

---

# 16. Why the Distinction Matters

The two failure modes should not be collapsed.

### Epistemic reconstruction failure

The model:

* recovered substantial project information,
* interpreted it imperfectly,
* and appeared more confident in its reconstruction than the evidence warranted.

This is directly relevant to EDASES.

### Runtime/context corruption

The model:

* entered a repetition failure,
* then produced apparently unrelated material from other domains.

This may be relevant to agent-system reliability, but its relationship to EDASES's epistemic architecture is not yet established.

The second failure should therefore be treated as an observed anomaly requiring investigation rather than as evidence that the first hypothesis is correct.

---

# 17. Documentation Implications

The discussion produced three candidate artifacts for preserving the findings.

### Session Handoff

The historical record should capture:

* the original experiment,
* the chronology,
* the reconstruction failure,
* the later runtime corruption,
* the distinction between the two,
* and the unresolved causal questions.

### Research Addendum

The durable architectural insight should capture:

> Project-state reconstruction and project-state validation are distinct capabilities.

It should also note that the later runtime corruption may represent a separate failure mode.

### Assumption Register

The existing assumption:

> Fresh-agent reconstruction is sufficient for autonomous project operation.

should remain challenged.

The observed runtime corruption does not invalidate or replace that finding.

---

# 18. Candidate Research Questions Emerging from Phase 3

The discussion produced several questions suitable for subsequent EDASES research.

### Reconstruction

Can a fresh agent reliably reconstruct project state from persistent project knowledge?

### Validation

Can an agent determine whether its reconstruction is sufficiently complete for a specific action?

### Evidence

Can important agent beliefs and decisions be systematically linked to evidence?

### Confidence

Can action thresholds be tied to explicit levels of confidence and risk?

### Governance

Should authority to act be granted by a project-level control plane rather than inferred by the execution agent?

### Portability

Can governance remain independent of the underlying agent harness?

### Runtime Resilience

How should an agent system detect and recover from catastrophic context corruption or unrelated-content intrusion?

### Economics

How capable can low-cost verification models be when restricted to evidence tracing, assumption checking, and consistency validation?

---

# 19. Architectural Direction at the End of Phase 3

The strongest architectural hypothesis at the end of the discussion was:

```text
                 ASES / EDASES
                       │
              Project Governance
                       │
       ┌───────────────┼───────────────┐
       │               │               │
   Knowledge         State         Validation
       │               │               │
       └───────────────┼───────────────┘
                       │
                Authority / API
                       │
                Agent Harness
                       │
                    Models
```

Crosslink, OpenClaudia, Thermite, and OpenCode each appear relevant to different portions of this conceptual stack.

The purpose of this model is not to prescribe a final implementation.

It is to identify a potentially important separation of concerns:

> **The system that executes an agent does not necessarily need to be the system that determines whether the agent is justified in acting.**

---

# 20. Final Position

Phase 3 began with an apparently bizarre Gemini failure and ended with a broader architectural hypothesis.

The important finding was not simply that a fresh agent can misunderstand documentation.

That is already expected.

The more consequential finding is that an agent can potentially construct a coherent, plausible reconstruction of a project without having a reliable mechanism for recognizing that the reconstruction is incomplete.

This makes **epistemic validation** distinct from memory, retrieval, and execution.

The subsequent manufacturing/Woodrow Wilson failure added a second, substantially stranger observation: severe runtime or context corruption can produce content apparently unrelated to the project entirely. That phenomenon remains unexplained and should be investigated independently.

The architectural discussion then suggested that enforcement of these concerns may belong above the agent harness.

OpenClaudia's enforcement philosophy may be directionally correct while operating at too low a layer. Crosslink appears to address persistent project knowledge. Thermite's Agent Operating System framing may point toward a broader control-plane abstraction. OpenCode and similar systems can remain execution environments.

The resulting hypothesis is that EDASES may need to treat **project knowledge, project state, epistemic validation, authority, and execution as distinct layers**, with the execution harness operating beneath a higher-level governance system.

The next phase should therefore avoid prematurely turning this hypothesis into an implementation.

The immediate research objective should be to determine whether this separation is actually necessary, what minimum mechanism would validate the hypothesis, and which existing systems already provide enough infrastructure to test it without building a new agent platform from scratch.
