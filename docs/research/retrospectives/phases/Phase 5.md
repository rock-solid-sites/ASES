---
title: "EDASES Phase 5 Retrospective"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - docs/research/registry/Model-Routing-Matrix.md

consumed_by:
  - docs/research/registry/Model-Routing-Matrix.md

supersedes:
  - EDASES Phase 4 Retrospective

superseded_by: []

last_updated: 2026-08-10
---

# EDASES Phase 5

## Retrospective

**Date:** 2026-08-09

---

## 1. Overview

Phase 5 began by revisiting an earlier observation: the goals of ASES/EDASES—particularly reducing unnecessary token consumption, preserving useful reasoning, and making AI-assisted software development more efficient—appeared to converge with practical work already being done around tools such as Crosslink and RTK.

The immediate trigger was an independent exploration of MCP tools for general software-development workflows. That exploration concluded that:

* RTK already addresses a major source of wasted context by compressing terminal output.
* Crosslink addresses another major source by preserving project knowledge and preventing agents from repeatedly rediscovering prior work.
* Further gains were likely to come from semantic retrieval rather than simply adding more MCP servers.

Two possible extensions emerged:

1. a **Crosslink Index**, capable of providing structured semantic information about repository objects; and
2. a **Semantic Repository Cache**, allowing agents to retrieve structural information without repeatedly reading raw source files.

The central question became how to turn these hypotheses into usable tooling while preserving the ability to study their effects later.

---

# 2. Initial Convergence

The independent MCP discussion identified a general progression in token efficiency:

```text
Raw output
    ↓
Compressed output
    ↓
Persistent knowledge
    ↓
Semantic retrieval
```

RTK already operates at the first important layer by reducing terminal output before it reaches the model.

Crosslink operates at the persistent-knowledge layer by allowing issues, design documents, research, and session handoffs to survive across agents and conversations.

The proposed repository-indexing work would operate at the next layer: allowing an agent to ask for the exact structural information required rather than reconstructing that information by opening files and searching the repository.

This led to the idea that the three systems were complementary rather than redundant.

---

# 3. Moving From Research Hypothesis to Working Tooling

An early research-oriented proposal focused heavily on collecting evidence about whether semantic retrieval actually reduced redundant reasoning.

That proposal was subsequently challenged by a practical question:

> Does this research get us any closer to using current tools to reduce token use now?

The answer was no, at least not directly.

The research proposal could establish a framework for studying the hypothesis, but it did not itself provide the tooling required to test the hypothesis in ordinary development.

The direction therefore changed.

Rather than waiting for the research program to establish the perfect design, the tooling should be built for immediate practical use while preserving enough observability that the tools could later become research subjects.

This resulted in a two-track principle:

```text
Immediate engineering utility
+
Future research observability
```

The tools should solve a real problem today without being burdened by a premature research framework.

---

# 4. The Initial RST Concept

The practical implementation was narrowed to a repository-structure tool, initially called **RST (Repository Structure Tool)**.

The MVP constraints were deliberately tightened:

* Rust as the implementation language.
* Opencode CLI as the only target environment.
* Rust repositories as the initial repository type.
* No premature multi-language abstraction.
* No attempt to build a comprehensive semantic repository platform.

Rust was selected because:

* the broader EDASES project has a preference for memory-safe software;
* Rust's compiler prevents entire classes of bugs;
* Crosslink and RTK are already Rust projects;
* keeping the tooling ecosystem in one language reduces fragmentation;
* the tooling itself is intended to participate in a project concerned with provably secure software.

The initial role of RST was to answer structural questions such as:

* Where is a symbol defined?
* Where is it referenced?
* What structural relationships surround it?
* Which tests are relevant?

The agent should only need to read the source itself after structural retrieval is insufficient.

---

# 5. Relationship Between RST, Crosslink and RTK

A major question throughout the discussion was what happened to the benefits of Crosslink/RTK integration if RST were developed as a separate engineering project.

The answer evolved during the review process.

The initial mental model was roughly:

```text
Crosslink
    ↓
RST
    ↓
RTK
```

This implied that the tools would need to interact directly.

The later model was substantially cleaner:

```text
             Opencode
          /      |      \
         ↓       ↓       ↓
   Crosslink    RST      RTK
```

The tools remain independent.

Their responsibilities are different:

* **Crosslink:** Why does this exist? What decisions, requirements, research and prior work matter?
* **RST:** Where is this? What structural relationships exist?
* **RTK:** What happened when it was executed?

The integration occurs at the orchestration and information-model level rather than through direct implementation dependencies.

This also permits the tools to be queried concurrently. The information hierarchy is conceptual rather than a mandatory sequential pipeline.

---

# 6. Adversarial Review of the First RST Proposal

Four models independently reviewed the tooling proposal:

* GLM
* Claude
* DeepSeek
* Gemini

The reviews were notable because they approached essentially identical material from markedly different perspectives.

The differences were not merely stylistic. Each reviewer surfaced a different category of engineering problem.

---

# 7. GLM Review

GLM focused primarily on architectural realism.

Its central observation was that sophisticated repository analysis is difficult to implement efficiently as a purely stateless CLI.

If RST relies on `rust-analyzer`, analysis state naturally wants to persist.

GLM therefore proposed a client/daemon architecture:

```text
Opencode
   ↓
RST client
   ↓
RST daemon
   ↓
rust-analyzer
```

It also recommended:

* making MCP the primary agent interface;
* providing a thin CLI for humans and scripting;
* reusing an in-memory analysis state;
* avoiding a provider abstraction until a second language exists;
* explicitly reporting incomplete or uncertain structural results.

The proposal adopted the important architectural conclusions while rejecting premature commitments to particular internal implementations.

In particular, the decision was made not to require a provider abstraction before there was a second provider.

---

# 8. Claude Review

Claude approached the proposal as an architecture and assumptions review rather than primarily as an implementation exercise.

The central question it identified was:

> What latency is actually acceptable, and what analysis approach achieves it?

Claude identified several possible architectures:

* a persistent daemon;
* Tree-sitter-based analysis;
* existing CLI tooling;
* a thin interface with the implementation deferred.

The important contribution was not choosing among these options but pointing out that the choice should follow measurement.

Claude also identified three additional concerns:

### Determinism and configuration

Structural results may depend on build configuration, feature flags, macros, and other conditions.

The proposal therefore should not claim exhaustive deterministic knowledge where it cannot guarantee it.

### Observability

Instrumentation should exist from the beginning rather than being retrofitted later.

### Agent behaviour

Whether an agent actually uses RST effectively is partly an orchestration/model-behaviour problem rather than solely a tool-design problem.

This review introduced the principle that the implementation architecture should remain contingent upon evidence from an initial engineering spike.

---

# 9. DeepSeek Review

DeepSeek focused on the proposal from the perspective of an engineer who would implement it immediately.

Its principal contribution was removing ambiguity.

It proposed explicit semantics for commands such as:

* symbol search;
* definition;
* references;
* test discovery.

It also proposed:

* local structured JSON logging;
* explicit cache behaviour;
* privacy guarantees;
* explicit LSP integration;
* a managed analysis process;
* concurrent rather than sequential invocation of Crosslink, RST and RTK.

DeepSeek also proposed measuring whether structural exploration was actually a significant source of token consumption before investing heavily in the tooling.

The proposal adopted the general principle of precise query semantics and lightweight observability, but rejected premature commitments such as a fixed crate layout or SQLite cache.

---

# 10. Gemini Review

Gemini took the broadest systems view.

Like GLM and DeepSeek, it proposed a client/daemon architecture.

However, its most important contribution was different: it proposed a shared canonical identifier for repository objects.

The basic idea was that the same repository object could be referenced consistently by:

* RST;
* Crosslink;
* RTK.

For example, a structural object could have a canonical identifier that appears in:

```text
RST:
definition of <identifier>

Crosslink:
design decision concerning <identifier>

RTK:
test failure involving <identifier>
```

This avoids requiring the tools to call one another or share databases.

The proposal adopted this underlying idea but rejected prematurely treating the identifiers as an RST-owned concept or necessarily calling them "URNs."

The preferred direction became a broader **canonical repository identifier** or similar shared identifier specification owned by the ecosystem rather than by RST alone.

Gemini also proposed higher-level queries such as `context` and `test-targets`. These were recognised as potentially valuable, but higher-level structural interpretation was treated cautiously because Phase 1 should preserve the property that outputs are mechanically derivable rather than architectural interpretations.

---

# 11. Synthesis of the Four Reviews

The four reviewers effectively filled different gaps.

| Reviewer | Primary gap filled                                    |
| -------- | ----------------------------------------------------- |
| GLM      | Architectural realism                                 |
| Claude   | Assumption validation and unresolved design decisions |
| DeepSeek | Implementation precision                              |
| Gemini   | Ecosystem integration                                 |

Their characteristic questions could be summarised as:

**GLM:** Can this actually be built efficiently?

**Claude:** Have we justified the decision to build it this way?

**DeepSeek:** Could an engineer implement this without guessing?

**Gemini:** How does this fit into the larger system?

This difference was itself considered valuable evidence for future EDASES work.

---

# 12. Model Performance as a Research Observation

The reviewer process revealed that models given the same input can exhibit substantially different reasoning patterns and useful specialisations.

The observed characteristics included:

* architectural reasoning;
* assumption detection;
* implementation realism;
* specification precision;
* ecosystem reasoning;
* abstraction discipline;
* novelty generation;
* resistance to premature optimisation.

The important conclusion was not that one model was simply "better."

Instead, the models appeared to occupy different useful roles.

The preliminary interpretation was:

* **Claude:** research/architecture reviewer;
* **GLM:** implementation architecture reviewer;
* **DeepSeek:** specification/implementation reviewer;
* **Gemini:** ecosystem/systems reviewer.

These should not yet be treated as fixed capabilities or permanent model rankings. They are observations from one review exercise.

---

# 13. The Model Capability Matrix

The discussion then considered how this information should be preserved.

An earlier idea was to create explicit capability metadata immediately, including fields such as architectural reasoning, implementation realism, and specification precision.

That was rejected as premature.

The exact structure of a future **Model Capability Matrix** is not yet known.

Instead, the current evaluations should be treated as evidence contributing to the eventual discovery of the matrix's dimensions and rubric.

The intended progression is:

```text
Individual model evaluation
        ↓
Repeated evaluations
        ↓
Observed recurring characteristics
        ↓
Findings
        ↓
Capability rubric
        ↓
Model Capability Matrix
        ↓
Evidence-based reviewer/model selection
```

The important methodological distinction is that current work is partly **rubric discovery**, not merely rubric application.

The evaluation corpus should therefore preserve detailed observations without forcing them into a prematurely fixed scoring system.

---

# 14. Filing the Reviewer Evaluation

The reviewer-performance report was considered inappropriate for direct placement into the normal epistemic chain of:

```text
Source
→ Observation
→ Finding
→ Synthesis
```

It is not itself a finding about software engineering.

It is an evaluation of research instruments—specifically, the behaviour of models used for adversarial review.

The appropriate location was therefore identified as the evaluation corpus, with a folder-level explanation describing the future capability-matrix work.

A proposed structure was:

```text
evaluation-corpus/
├── README.md
├── reviewer-model-evaluations/
│   ├── Reviewer Model Capability Evaluation v1.md
│   └── ...
└── ...
```

The folder README should explain that these evaluations:

* preserve empirical observations about models and research tools;
* are not themselves final capability rankings;
* contribute to a future Model Capability Matrix;
* should preserve qualitative observations while the rubric is still being discovered.

---

# 15. Why the Capability Rubric Should Remain Open

A key methodological conclusion was that the categories themselves should emerge from evidence.

The reviewer evaluations did not begin with a predefined requirement to assess "ecosystem reasoning" or "architectural realism."

Those dimensions became visible because they explained meaningful differences between the four reviews.

If a fixed rubric were introduced immediately, future observations could be forced into categories that were chosen before sufficient evidence existed.

The more appropriate principle is:

> The evaluation corpus should help discover what dimensions of model capability are worth measuring before those dimensions become a formal scoring rubric.

This preserves flexibility while still accumulating structured evidence.

---

# 16. Final RST Direction

By the end of the phase, the proposed RST direction was:

### Purpose

Provide efficient, mechanically derived structural repository information to LLM agents so that they do not need to reconstruct repository structure from raw files.

### Scope

* Rust implementation.
* Rust repositories.
* Opencode CLI.
* Focused structural queries.
* No premature multi-language provider architecture.

### Likely architecture

A client/managed-analysis-service split is increasingly likely because serious semantic analysis requires persistent state, but this should be validated by Phase 0 measurements rather than treated as an unconditional requirement.

### Core queries

The exact command names remain implementation-level details, but the conceptual operations are:

* locate a structural object;
* find references;
* retrieve narrowly defined structural context;
* identify relevant tests or test targets.

### Output requirements

Results should be:

* structured;
* concise;
* mechanically derived;
* explicit about uncertainty and scope;
* suitable for consumption by an LLM.

### Observability

Local, opt-in structured logging should capture enough information to evaluate:

* query frequency;
* latency;
* cache behaviour;
* success/failure;
* confidence or result scope.

### Privacy

The tool should operate offline and should not transmit repository contents or telemetry.

---

# 17. Crosslink and RTK Integration

The phase ultimately moved away from direct integration.

Crosslink should remain responsible for persistent project knowledge.

RTK should remain responsible for execution-result compression.

RST should remain responsible for repository structure.

The primary integration mechanisms are:

1. Opencode orchestration.
2. Shared canonical repository identifiers.
3. Concise structured outputs.
4. Future observations about how agents use the three information sources.

This preserves independence while allowing the systems to participate in a common information architecture.

---

# 18. Research Value

The engineering work also creates a useful future research opportunity.

If RST is deployed in ordinary projects, it can generate evidence about:

* how often agents reconstruct repository structure;
* which structural questions occur repeatedly;
* whether agents actually substitute semantic queries for raw file reads;
* whether the resulting context reduction is meaningful;
* when agents ignore or distrust structural results;
* which forms of structural retrieval are most useful.

Crosslink and RTK similarly provide opportunities to observe other forms of reconstruction.

This means the tools can be useful independently of whether the original research hypothesis is ultimately confirmed.

---

# 19. What Remained Unresolved

Several issues were intentionally left open.

### Exact RST implementation architecture

A daemon is increasingly likely, but Phase 0 measurements should establish whether its complexity is justified.

### Exact structural identifier format

A canonical identifier mechanism is promising, but its final syntax and ownership should be designed after more ecosystem experience.

### Exact RST query surface

The conceptual operations are clear, but the smallest useful set of queries should be determined through implementation and use.

### Model Capability Matrix

The matrix is a future artefact.

Its dimensions, scoring method, evidence requirements, and update process remain deliberately undefined.

### Definition of redundant reasoning

This remained a particularly difficult research problem identified in earlier review rounds.

The difficulty is that redundancy requires some reference model of what reasoning was necessary. That reference model may itself require empirical investigation.

---

# 20. Lessons From Phase 5

Several broader lessons emerged.

### Build useful tools before the research framework is complete

A research programme should not require every hypothesis to be resolved before practical experimentation can begin.

Useful tooling can be deployed first while preserving enough observability for later study.

### Separate tool responsibilities

Crosslink, RTK and RST become more powerful when each has a narrow responsibility rather than attempting to become a unified system.

### Integrate through shared concepts

A common identifier vocabulary can provide interoperability without requiring direct software dependencies.

### Delay abstractions until evidence exists

The provider abstraction, multi-language architecture, fixed persistence layer, and detailed capability rubric were all examples where premature generalisation would have increased complexity without corresponding evidence.

### Preserve observations before formalising categories

The reviewer-model evaluation demonstrated that useful capability dimensions can emerge from actual comparative use.

---

# 21. Final State at the End of Phase 5

Phase 5 began as an investigation into whether MCP and token-saving tooling could connect with the goals of ASES/EDASES.

It ended with two related but distinct outcomes.

The first was a practical engineering direction:

```text
Crosslink → project knowledge
RST       → repository structure
RTK       → execution results
```

with Opencode orchestrating them and a possible shared canonical repository-identifier system providing a common vocabulary.

The second was a methodological observation:

> Different reviewer models can provide materially different kinds of useful engineering reasoning even when given identical review tasks.

That observation should not yet become a capability ranking.

Instead, it becomes evidence in the evaluation corpus from which a future Model Capability Matrix and its rubric can eventually be developed.

The most important outcome of the phase is therefore not a final RST architecture or a finished model taxonomy. It is the establishment of a pattern for future work:

```text
Hypothesis
    ↓
Practical tool
    ↓
Real-world use
    ↓
Structured observation
    ↓
Comparative evidence
    ↓
Emergent methodology
```

This preserves the project's ability to make immediate engineering progress without sacrificing the longer-term objective of developing an empirically grounded methodology for directing AI agents.
