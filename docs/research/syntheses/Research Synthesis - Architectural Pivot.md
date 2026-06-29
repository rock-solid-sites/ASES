---
title: Research Synthesis: Provenance Deadlock and the Epistemic Architectural Pivot
program: EDASES
layer: Research
document_type: Synthesis
status: Active
authority: Canonical
canonical_repository: edases

depends_on:
  - Synthesis of Adversarial Reviews: Decisional Provenance Architecture
  - reframe-chatgpt.md
  - reframe-claude.md
  - reframe-deepseekpro.md
  - reframe-glm52.md
  - Concept: Levels of Abstraction

consumed_by:
  - ARCHITECTURE.md
  - Methodology to Requirements Mapping
  - AGENTS.md
  - Execution Engine Vision

supersedes: []
last_updated: 2026-06-29
---

# Research Synthesis: Provenance Deadlock and the Epistemic Architectural Pivot

## 1. Context and Problem Statement

The initial focus of the Knowledge Architecture Research was to establish a mechanism for **Decisional Provenance**—a system to record AI-assisted decisions locally and sync them via Git. This was addressed by synthesizing four architectural proposals (Paths A, B, C, D) which centered on managing event logs, Git hooks, and eventual consistency using the Git repository as the system of record.

This synthesis document confirms the conclusion that the subsequent architectural deadlock and failure of consensus was not due to technical irreconcilability, but because the **problem itself was fundamentally misframed**. The system was attempting to solve a high-level cognitive problem using low-level implementation mechanics.

## 2. Observation: The Deadlock and Consensus Breakdown

Four independent adversarial reviews were conducted in parallel against the original architectural synthesis. While there was universal agreement on the fatal flaws of the initial Option 1 and Option 2 proposals, the four subsequent paths (A-D) failed to achieve consensus.

| Reviewer | Primary Finding | Architectural Critique |
|---|---|---|
| **Claude** | The system needs mechanical enforcement via a GUI/CLI to survive. | The storage problem is secondary to the epistemic data model and enforcement logic. |
| **ChatGPT** | The primary adversary is **Entropy** (Assumption Drift, Context Loss). | The focus must shift from *artifact preservation* to *reasoning continuity*. |
| **Deepseek** | Fragile Git hooks and daemons are **Adoption Killers**. | The system must be zero-configuration, robust, and driven by a simple executable CLI. |
| **GLM5.2** | The core flaw was an **Abstraction Mismatch**. | The debate was about implementation details (YAML vs. JSON vs. Git hooks) rather than the foundational Methodology. |

The collective observation was that that the reviewers were arguing over the implementation of a **commit-level audit trail**, while the project's true objective had evolved into a **long-duration, multi-agent organizational memory system** where software development is the testbed, not the end goal.

## 3. Finding: The Object of Interest is Reasoning, Not Commits

The overwhelming evidence from the failed architectural debate and subsequent operational failures (e.g., the Handoff Failure Analysis, where an agent reconstructed a plausible but incorrect project model) proved that:

1.  **The problem is Epistemic:** Failures are caused by a lack of an **Epistemic Validation Layer** capable of checking the quality of an agent's reconstructed knowledge, not merely a lack of event logs.
2.  **The primary asset is Reasoning:** The project must preserve the chain of evidence (Source → Observation → Finding → Decision) rather than a simple log of AI actions.
3.  **The solution requires Abstraction:** Resolving the deadlock required elevating the problem from the **Implementation** layer (Git, SQLite, JSONL) to the **Methodology** layer, as defined in `Concept: Levels of Abstraction`.

## 4. Conclusion: The Epistemic Architectural Pivot

Based on this synthesis, the project pivots from an architectural model derived from Git operations to one derived from the **Methodological Requirements** of the ASES research program.

The key architectural decision is the formal separation of concerns into explicit layers:

*   **EDASES (Research):** Investigates and validates principles.
*   **ASES (Methodology):** Defines the rules and workflows derived from research.
*   **Requirements:** Translates methodology into verifiable capabilities.
*   **Execution Engine (Implementation):** Executes and mechanically enforces the methodology.

This pivot provides the research program with an architecture that is:

*   **Traceable:** Every implementation choice can be traced back to a methodological principle.
*   **Portable:** Methodology is independent of specific implementation technologies.
*   **Enforceable:** The Execution Engine's primary purpose is mechanical compliance, reducing predictable human and AI error.

This synthesis serves as the canonical research justification for the entire new project structure, the canonical documents, and the development of the Execution Engine.

## 5. Next Steps

The focus shifts immediately to translating the ASES methodology into concrete, machine-enforceable requirements (as detailed in `Methodology → Requirements Mapping Specification`) and defining the Execution Engine's architecture to satisfy those requirements. This architectural pivot enables the project to move from debating how to hack Git to formalizing and automating the research methodology itself.