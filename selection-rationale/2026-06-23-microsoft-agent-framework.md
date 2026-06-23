# SR-2026-06-23-microsoft-agent-framework — Microsoft Agent Framework as second Track B evaluation

## Metadata

- **ID:** SR-2026-06-23-microsoft-agent-framework
- **Date of decision:** 2026-06-23
- **Decider:** OpenCode (Principal/Orchestrator Agent)
- **Selection:** Microsoft Agent Framework (MAF) as the second Track B harness evaluation (Crosslink issue #4)
- **Status:** Live
- **Crosslink issue:** #4
- **Author:** OpenCode (Principal/Orchestrator Agent)

## Rationale

Evaluating the Microsoft Agent Framework (MAF) is the logical and necessary successor to the Microsoft AutoGen evaluation (issue #3). Because AutoGen entered official maintenance mode in late 2025/early 2026, any potential EDASES integration or reliance on AutoGen represents an investment in a sunsetting, community-only framework. MAF is Microsoft's production-ready, actively developed successor, representing the evolution of AutoGen's multi-agent ideas. 

By conducting this evaluation, we can directly compare the old (AutoGen) and new (MAF) architectures across the same EDASES layers (Principal, Organizational, Knowledge, Capability, Verification, Execution). Specifically, MAF's documented features—such as graph-based workflows, checkpointing, human-in-the-loop, and time-travel—directly target several of the architectural gaps (e.g., Verification, Organizational persistence, and Principal oversight) that were identified in the AutoGen evaluation.

This two-part evaluation sequence establishes a clear empirical timeline of multi-agent framework evolution in the wild, testing our hypothesis of Progressive Externalization (AH-002).

## Alternatives considered

- **Remain on Microsoft AutoGen (Stop after #3)** — Rejected because AutoGen's maintenance mode introduces a severe longevity and support risk. We would be basing our architecture on a deprecated framework.
- **Evaluate OpenCode / OpenClaudia / CodeWhale (Coding harnesses)** — Postponed because these harnesses focus entirely on the Execution Layer. We must validate the Organizational and Verification layer coverage of multi-agent frameworks before evaluating purely code-execution harnesses. Evaluating MAF first maintains a logical progression from baseline to successor.

## Evidence expected to validate

- **Supports the choice if:** The MAF evaluation demonstrates that its new primitives (such as graph-based workflows, checkpointing, and time-travel) successfully address or mitigate at least two of the EDASES layer gaps identified in AutoGen (e.g., Verification or Organizational persistence).
- **Falsifies the choice if:** MAF is found to be a purely cosmetic rename of AutoGen with no significant changes to persistence, state management, or verification capabilities, making the evaluation redundant.

## Cross-references

- `harness-evaluations/Microsoft-AutoGen.md` — The baseline AutoGen evaluation
- `capability-mapping/Harness-Capability-Matrix.md` — The matrix we are updating with a MAF column
- `research-addenda/Research Addendum 01.md` — The EDASES layered architecture specifications

## Why this entry exists

Captured during the planning phase of the MAF evaluation under Track B, before commencing any Heuristic Scouting or verification subagent dispatches for issue #4.
