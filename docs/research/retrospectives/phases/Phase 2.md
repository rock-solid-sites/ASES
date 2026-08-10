---
title: "EDASES Phase 2 Retrospective"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - knowledge-architecture-research/Knowledge Architecture Research Phase-1 draft 1.md

consumed_by:
  - EDASES Phase 3 Retrospective

supersedes:
  - EDASES Phase 1 Retrospective

superseded_by:
  - EDASES Phase 3 Retrospective

last_updated: 2026-08-10
---

# EDASES Phase 2

## Retrospective

### Purpose

This retrospective records the development of the EDASES project during this phase of work: what was discussed, what changed, what was decided, what was implemented, and which unresolved questions emerged.

The purpose is historical and organizational rather than prescriptive. It should preserve the reasoning that led to the current project state so that later work can distinguish decisions that were deliberately made from assumptions that have merely persisted.

---

# 1. Starting Point

The phase began from an existing body of EDASES research, project documents, handoffs, and methodology work.

The immediate problem was that the project had grown beyond what could reliably be held in a single person's memory or reconstructed by a fresh context-free conversation from a handful of Markdown files.

This was itself evidence of one of the project's central research concerns:

* knowledge loss,
* context loss,
* loss of reasoning chains,
* and difficulty maintaining continuity across long-running agent-assisted work.

The first practical objective was therefore to improve the project's own externalization and continuity mechanisms.

---

# 2. Reframing the Project

A major discussion during the phase concerned the scope of EDASES.

The project had originally been framed primarily as a software development system. Discussion of automation and other forms of human-agent interaction raised the possibility that the methodology might have broader applicability.

The analogy of **progressive externalization**, similar to an exoskeleton, emerged as a useful conceptual framing:

```text
Conversation
    ↓
Notes
    ↓
Documents
    ↓
Structured Artifacts
```

However, the project deliberately stopped short of treating this as a new theory of human-agent interaction.

The conclusion was that the evidence base was not yet sufficient to justify such a broad theoretical claim. Software development remained the actual domain of the project, while broader implications were retained as potential future research.

This established an important boundary:

> EDASES may eventually have broader implications, but it should not claim to have established them before generating sufficient evidence.

---

# 3. Expanding the Research Program

The project also recognized that its own research could not rely exclusively on internally generated ideas.

A parallel investigation of existing work became necessary.

The proposed research program therefore developed three broad branches:

1. **Historical research**
2. **Current state-of-the-art research**
3. **Assessment of specific software tooling**

The first two were considered capable of proceeding independently and being synthesized later. Tool assessment was deliberately placed after the first two because tooling should be evaluated against requirements and patterns discovered through research rather than allowed to define the methodology prematurely.

Historical research was intended to include previous projects and the adversarial reviews they had undergone. The hospitality project was specifically identified as an example where multiple rounds of adversarial review had already generated useful evidence.

Current state-of-the-art research was deliberately defined broadly. Relevant work might exist in:

* small GitHub repositories,
* Discord communities,
* research-paper PDFs,
* relatively obscure practitioner projects,
* agent skills,
* and other sources that may not have significant public visibility.

Popularity was explicitly rejected as a proxy for relevance. Projects such as Gastown and OpenClaw could be highly visible while having little relevance to EDASES, whereas small projects such as those associated with Dollspace and Claude Code modes might contain highly developed techniques worth examining.

This established another methodological principle:

> Evidence should be sought from wherever useful practice is actually occurring, rather than inferred from popularity or prominence.

---

# 4. Knowledge Architecture Became a First-Class Problem

As the research program expanded, it became clear that effective research could not be conducted if the research itself could not be organized.

The project had initially considered a research notebook implemented as an Astro site. The static-site approach remained attractive because Markdown could be version-controlled while Astro could provide a more useful presentation layer.

However, the conceptual structure was recognized as fundamentally different from a normal blog.

The desired system needed to behave more like a database while retaining the simplicity and inspectability of Markdown and Git.

The research archive therefore needed to support:

* relationships between concepts,
* provenance,
* navigation,
* reasoning chains,
* accumulated findings,
* and continuity across sessions and agents.

A separate research identity and `.pages.dev` notebook were considered appropriate, with the public-facing Rock Solid Sites website acting as a separate publication surface.

This was ultimately recognized as an implementation detail. The more important requirement was the underlying knowledge structure.

---

# 5. Why Knowledge Architecture Was Moved Forward

The project explicitly decided that knowledge architecture needed to move to the front of the research queue.

The reasoning was straightforward:

> An effective research program cannot operate indefinitely without a system for organizing the knowledge it generates.

The architecture did not need to be final.

It needed to be sufficient to begin capturing relationships and evidence without immediately losing them.

The project therefore adopted an evidence-driven approach to the architecture itself:

* start with a useful structure,
* use it operationally,
* observe where it succeeds or fails,
* and modify it based on evidence.

A fully custom system was not ruled out. Existing components, including Rust crates and other reusable pieces, could make a custom assembly practical if that allowed the project to shape its tools rather than forcing the methodology to conform to an existing product.

---

# 6. Phase 1 Was Explicitly Numbered From One

An explicit project convention was established during charter development:

> Phase numbering begins at Phase 1 rather than Phase 0.

The reasoning was that zero-based numbering is primarily a programmer convention, whereas this project is intended for non-programmers as well. Standard human-facing notation was therefore preferred.

This is a small decision, but it illustrates the project's general preference for making the methodology understandable outside programming culture.

---

# 7. Phase 1 Charter Development

A Phase 1 project charter was drafted around knowledge architecture research.

The charter deliberately remained flexible. It specified:

* goals,
* research topics,
* methods,
* and intended deliverables,

without attempting to prescribe the exact architecture that the research would discover.

The charter was sent through external review, and two reviewers' responses were considered together.

A correction was made when it became apparent that both reviews needed to be explicitly accounted for rather than referring generically to "the reviewer."

The resulting synthesis made several points more explicit:

* the choices were driven by actual project experience,
* the failure modes were not hypothetical,
* the research infrastructure was intended to support future projects using the methodology,
* and the deliverables existed to solve concrete organizational problems rather than merely document the research.

The project was therefore positioned as research grounded in observed failures rather than speculative architecture design.

---

# 8. The Repository Became the First Practical Knowledge Architecture

The project then moved from discussing a knowledge architecture to examining the repository already being used for ASES.

The repository structure was:

```text
ASES/
├── README.md
├── charters/
├── assumption-registers/
├── assumption-to-decision-registers/
├── core-system-prompts/
├── knowledge-architecture-research/
├── research-programs/
├── architecture-validation-plans/
├── specifications/
├── research-addenda/
├── research-handoffs/
├── session-handoffs/
└── handoff-bundle/
```

This revealed an important fact:

> The project had already begun developing a knowledge architecture operationally, before formally researching knowledge architecture.

The existing repository contained distinct representations for:

* charters,
* research programs,
* assumptions,
* decisions,
* validation plans,
* specifications,
* and handoffs.

These were treated not merely as folders but as emerging knowledge-object categories.

---

# 9. Extending the Repository's Knowledge Model

The existing repository was missing obvious upstream stages in the evidence chain.

The project therefore proposed and implemented:

```text
sources/
observations/
findings/
syntheses/
evaluation-corpus/
```

The intended conceptual flow became:

```text
Source
    ↓
Observation
    ↓
Finding
    ↓
Assumption
    ↓
Decision
    ↓
Validation
    ↓
Outcome
```

The new directories were:

```text
sources/
├── papers/
├── repositories/
├── methodologies/
├── communities/
└── historical-projects/

observations/

findings/

syntheses/

evaluation-corpus/
```

Each directory received a README explaining its purpose and conventions, and the main README was updated to document the knowledge-flow chain.

Existing repository structure was intentionally left unchanged.

This was an important practical decision: the project did not attempt to redesign the entire repository or impose a final ontology. It added obvious missing knowledge objects while retaining the ability to remove or revise them later.

---

# 10. The Evidence Chain

The expanded repository made an increasingly important distinction possible.

Previously, reasoning could appear to begin with:

```text
Assumption
    ↓
Decision
```

The new structure allowed the preceding evidence to be represented:

```text
Source
    ↓
Observation
    ↓
Finding
    ↓
Assumption
    ↓
Decision
```

This was significant because many of the project's known failure modes occur when the upstream reasoning disappears while the downstream decision survives.

The repository therefore began to function as an organizational-memory system rather than simply a documentation repository.

The project did not claim that this was the final ontology. It was a working representation derived from actual operational needs.

---

# 11. Archival Problems Became Evidence for the Methodology

A separate thread concerned preservation of the work itself.

The conversation reached a point where the assistant could still reconstruct the broad project history but could no longer guarantee verbatim access to all earlier documents because of conversation length and context limitations.

The following distinction became explicit:

```text
Original Documents
    ↓
Conversation Context
    ↓
Model Reconstruction
```

The first layer has the highest fidelity.

The second has partial fidelity.

The third can preserve intent and conclusions but cannot guarantee exact wording, structure, or provenance.

This exposed the very failure mode EDASES was designed to address.

The project initially considered ZIP-based session archives. A condensed archive was generated, followed by an expanded archive, but this was recognized as inferior to preserving the actual source artifacts.

The conclusion was:

> Do not treat the conversation as the canonical archive.

Instead:

> Extract durable artifacts from the conversation and preserve them in Git.

---

# 12. GitHub As Organizational Memory

The existing ASES GitHub repository therefore became more important than a ZIP-based conversation archive.

Git provides:

* exact historical artifacts,
* version history,
* provenance,
* recoverability,
* structural navigation,
* and continuity between sessions.

The repository can become the source of truth while conversations become working environments.

This creates a cleaner separation:

```text
Conversation
    ↓
Analysis / Drafting / Reasoning
    ↓
Repository
    ↓
Canonical Organizational Memory
```

This was recognized as a concrete example of the project's broader principle of progressive externalization.

---

# 13. What EDASES Is At This Point

By the end of the knowledge-architecture discussion, the project was understood as more than a conventional agentic coding methodology.

The working description became approximately:

> A research program using AI-assisted software development as a proving ground for developing evidence-driven methods of organizational memory, reasoning traceability, adversarial validation, and long-duration human-agent collaboration.

The project still deliberately avoided claiming a general theory of human-agent interaction.

Software development remained the actual experimental domain.

The broader implication remained a future research possibility.

---

# 14. Transition From Knowledge Architecture To Operational Development

Later in the conversation, an actual software-development phase was reported as complete.

The reported Phase 2 success criteria were:

* 5+ museums integrated
* 3+ geographic regions
* 15+ normalized styles
* corpus seeding
* audit tooling
* source-health validation
* capability for a 5,000+ eligible corpus

The reported implementation included eight agent contributions and multiple integration commits.

Verification reported:

```text
gofmt -l .        — clean
go vet ./...      — clean
go build ./...    — clean
go test -count=1 ./... — all 20 packages green
migration check  — successful and idempotent
```

The work was initially declared ready for Phase 3.

This triggered a new methodological question:

> Should a phase be considered complete merely because implementation and verification succeed?

The answer developed during this conversation was no.

---

# 15. Verification Is Not Adversarial Review

The distinction between ordinary verification and adversarial review became explicit.

Verification asks:

> Did we build what we intended to build, and does it behave according to the tests?

Adversarial review asks:

> Are we wrong about anything important?

The latter can identify:

* hidden assumptions,
* incomplete validation,
* weak success criteria,
* architectural blind spots,
* requirement mismatches,
* untested edge cases,
* security concerns,
* scope drift,
* and overstated conclusions.

A project can therefore pass every test and still have an invalid conclusion.

This distinction became one of the most important methodological developments of the phase.

---

# 16. The Phase Gate Was Reframed

An initial proposal was:

```text
Phase Work
    ↓
Verification
    ↓
Phase Report
    ↓
Adversarial Review
    ↓
Phase Complete
```

This was challenged as backwards.

The review should not primarily review the report.

It should review the work itself.

The revised process became:

```text
Phase Work
    ↓
Integration
    ↓
Adversarial Review
    ↓
Required Fixes
    ↓
Commit
    ↓
Phase Record
```

The crucial principle is:

> Review the integrated changeset before it becomes accepted project history.

This avoids the psychological and procedural pressure that comes with reviewing something already committed and declared complete.

The review is therefore a gate, not an after-the-fact audit.

---

# 17. Adversarial Review Should Be Automatic

The next question was how to operationalize this.

The conclusion was that adversarial review should not depend on the human remembering to request it.

It should be built into the development system itself.

The proposed flow became:

```text
Agent Work
    ↓
Integration
    ↓
Tests / Verification
    ↓
Adversarial Reviewer
    ↓
Orchestrator
    ↓
Human Operator
    ↓
Approve / Revise / Reject
    ↓
Commit
```

The reviewer can be a cheap model because the task is intentionally bounded and one-shot.

The reviewer does not need to be the strongest reasoning model available. Its job is to act as a systematic skeptic.

---

# 18. The Cheap Reviewer

The proposed adversarial reviewer would receive a package containing:

* phase objective,
* success criteria,
* relevant design or requirements documents,
* Git diff,
* changed files,
* tests and their results,
* and potentially the phase's assumptions.

Its prompt should explicitly tell it to assume that the implementation team may be mistaken.

It should look for:

* unsupported claims,
* incorrect assumptions,
* missing validation,
* unmet success criteria,
* weak tests,
* architectural risks,
* and conclusions that go beyond the evidence.

The reviewer should not be responsible for taking over implementation.

Its role is bounded criticism.

---

# 19. The Orchestrator's Role

The reviewer should not directly decide whether the project proceeds.

Instead:

```text
Review Model
    ↓
Review Findings
    ↓
Orchestrator
    ↓
Human Operator
```

The orchestrator interprets the review and determines whether findings require:

* immediate remediation,
* escalation,
* human clarification,
* or simply recording.

The human operator remains the decision authority.

This preserves the separation between:

```text
Reviewer = finds weaknesses
Orchestrator = synthesizes and routes
Human = decides
```

rather than allowing a cheap reviewer to become an autonomous gatekeeper.

---

# 20. Crosslink Connection

The proposed process was then connected to the existing Crosslink development.

Crosslink already had concepts related to:

* kickoff,
* analysis-only agents,
* design-document support,
* specification validation,
* verification levels,
* and adversarial self-review.

This suggested that the new EDASES requirement could fit naturally into Crosslink rather than being implemented as an unrelated external mechanism.

The key distinction identified was:

### Existing verification

> Is the implementation sound and does it satisfy the specified requirements?

### EDASES-style adversarial review

> Are the requirements, assumptions, validation, and conclusions themselves justified?

The latter is broader than code review.

It is better understood as a **decision gate** or **evidence gate**.

---

# 21. Review Findings Become Knowledge

An especially important connection was made between adversarial review and the newly expanded knowledge architecture.

A review finding is not necessarily just disposable feedback.

It can become a knowledge object.

For example:

```text
Observation:
A criterion demonstrates capability but not actual execution.
```

Repeated observations can produce:

```text
Finding:
Projects frequently conflate capability validation
with execution validation.
```

Repeated findings can contribute to:

```text
Synthesis:
Validation criteria should distinguish capability,
execution, and operational readiness.
```

This creates a direct connection between development execution and methodology research.

The development system becomes a producer of evidence.

---

# 22. A More Complete EDASES Operational Model

By the end of the conversation, the emerging process looked approximately like:

```text
Research / Requirements
        ↓
Assumptions
        ↓
Planning
        ↓
Agent Execution
        ↓
Integration
        ↓
Verification
        ↓
Adversarial Review
        ↓
Remediation
        ↓
Human Decision
        ↓
Commit / Accepted State
        ↓
Evidence + Findings
        ↓
Organizational Memory
```

The repository then preserves the resulting knowledge:

```text
Sources
    ↓
Observations
    ↓
Findings
    ↓
Syntheses
    ↓
Assumptions
    ↓
Decisions
    ↓
Specifications / Plans
    ↓
Implementation
    ↓
Validation
    ↓
Outcomes
```

These are not yet claimed to be a finalized formal model. They are the current operational understanding emerging from the project.

---

# 23. What This Phase Changed

Several assumptions changed materially during this phase.

### From Documentation To Organizational Memory

The repository is not primarily a place to store documents.

It is intended to preserve relationships, provenance, reasoning, and project continuity.

### From Tool Selection To Evidence-Driven Tool Selection

Tooling should follow research rather than define the research.

### From Project-Specific Infrastructure To Methodology Infrastructure

The knowledge system should support future projects using the methodology, not only the current EDASES research.

### From Verification To Adversarial Validation

Passing tests is necessary but insufficient.

### From Optional Review To Automatic Review

Adversarial review should occur automatically before a changeset becomes accepted project history.

### From Review As Commentary To Review As Evidence

Review findings can become observations and findings in the project's organizational memory.

### From Conversation As Archive To Git As Source Of Truth

Conversation is a workspace.

The repository is the durable organizational memory.

---

# 24. Remaining Uncertainties

Several questions remain intentionally unresolved.

## Exact Knowledge Model

The repository now contains:

```text
sources/
observations/
findings/
syntheses/
evaluation-corpus/
```

but the project has not established a final ontology or schema.

Those should emerge from evidence.

## Exact Review Trigger

The principle of automatic pre-commit adversarial review is established, but the exact Crosslink implementation remains to be designed.

## Review Scope

The project still needs to determine how much context a cheap reviewer requires to identify meaningful weaknesses without becoming expensive or redundant.

## Review Severity

A practical classification is still needed for deciding when findings:

* block commitment,
* require human review,
* require remediation,
* or can simply be recorded.

## Evidence Accumulation

The expanded repository needs to be used in practice before conclusions about its effectiveness can be drawn.

---

# 25. Retrospective Assessment

The most important outcome of this phase was not a particular directory structure or automation mechanism.

It was the discovery that the project was already generating the organizational-memory problems it was trying to solve.

The inability to reliably reconstruct earlier documents from a long conversation was itself a demonstration of context and reasoning loss.

The existing ASES repository then demonstrated that useful knowledge structures had already emerged organically:

```text
Charters
Assumptions
Decisions
Validation
Specifications
Handoffs
```

Adding:

```text
Sources
Observations
Findings
Syntheses
Evaluation Corpus
```

made the upstream evidence path explicit.

The later discussion of automatic adversarial review extended the same principle into execution:

```text
Work
    ↓
Challenge
    ↓
Decision
    ↓
Accepted Knowledge
```

The resulting direction is therefore increasingly coherent:

> EDASES is not simply attempting to make AI agents better at producing software. It is attempting to create a development methodology in which the reasoning, evidence, assumptions, decisions, challenges, and outcomes surrounding agent-produced work remain recoverable, reviewable, and useful over time.

That remains a working research direction rather than a proven final theory.

The next stages should therefore continue to treat the architecture and processes themselves as experimental objects, preserving both their successes and their failures as evidence for the methodology.

---

# 26. Current State At The End Of This Phase

At the end of this retrospective period, the project has:

* established knowledge architecture as a first-class concern;
* expanded the ASES repository with source, observation, finding, synthesis, and evaluation-corpus structures;
* adopted GitHub as the preferred durable source of truth for project knowledge;
* distinguished historical research, state-of-the-art research, and tooling evaluation;
* retained broader human-agent interaction research as future work rather than overclaiming current evidence;
* identified adversarial review as distinct from ordinary verification;
* moved adversarial review to the pre-commit phase gate;
* identified automatic cheap-model review as a practical implementation strategy;
* connected that mechanism to Crosslink's existing execution and verification architecture;
* and identified adversarial review as a potential source of reusable methodological evidence.

The project therefore enters its next stage with a more explicit relationship between **research, organizational memory, execution, review, and evidence** than it had at the beginning of this phase.
