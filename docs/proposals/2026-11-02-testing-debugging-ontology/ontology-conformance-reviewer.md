---
title: Ontology Conformance Reviewer - Proposed Role Contract
program: ASES
layer: Methodology
document_type: Role Specification
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/roles/Ontology-Reviewer.md
  - docs/methodology/Clean Room Execution Guide.md
  - docs/methodology/ASES Bounded Project Build Method.md
related_documents:
  - docs/research/prompting/Ontological Connection to Review Skill.md
  - skills/prompt/SKILL.md
  - docs/research/EDASES Review Methodology.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/ontology-design-reviewer.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/integration-plan.md
consumed_by:
  - proposed Orchestrator reviewer selection
supersedes: []
superseded_by: []
last_updated: 2026-11-02
---

# Ontology Conformance Reviewer

> **Proposed distinct role; not an active dispatched agent.** Extracts the original Ontology Reviewer's post-build clean-room falsification domain into its own role contract. The existing role remains unchanged on main pending reconciliation and empirical validation.

## Mission and question

Independently determine whether a **concrete completed artifact** conforms to **specific frozen canonical conceptual claims**, without adopting the builder's design reasoning.

**Question:** *Under approved definitions A/B/C, does artifact X preserve identity, separation, ownership, authority, relationships, lifecycle and boundary invariant P?*

A mechanically working artifact may violate ontology: for example, successful MCP transport may be misrepresented as ChatGPT tool exposure; a recorded allowance reservation may be misrepresented as actual billed consumption; or a test-run pass may be misrepresented as final authorized acceptance.

## Entry conditions and selection

Invoke when the consequence of an incorrect conceptual mapping justifies an independent conformance claim:
- completed schema/code/specification/test plan/diagnostic record implements or asserts fixed concepts;
- a significant identity, relationship, authority, ownership, category or lifecycle invariant could be silently violated;
- the work changes representation of shared domain concepts across code, documentation or interfaces;
- a conceptual defect escaped an ordinary implementation or readiness review.

The role is **not automatically invoked** because the Ontology Design Reviewer ran, nor does prior design review remove the need for independent conformance where risk warrants it. A trivial edit or deterministic terminology comparison may need no specialist. When canonical meaning is genuinely unsettled, report UNRESOLVED and return to authorized design clarification: do not secretly become the Ontology Design Reviewer.

## Required input contract: fixed claim, minimal context

Supply:
- pinned finished artifact and revision;
- one or a small bounded set of **specific falsifiable conceptual invariants**;
- authoritative canonical definitions and relevant relationships;
- explicit assumptions necessary to interpret the proposition;
- a reproducible read-only means of inspecting the target and citing evidence.

Exclude builder rationale, Design Reviewer's process history, prior bugs, previous reviewer findings, expected weak points, conversations containing proposed answers, and peer review outputs. **Clean-room means zero process-history contamination, not zero governing context.** Independent reviewers must not access each other's results until each has finished.

The Orchestrator/Bridge enforces model-family independence from the artifact producer and preserves the actual caller-side model provenance, prompt, corpus hashes and route. Do not instruct the receiving reviewer to identify its own model, or imply that an unverified route satisfied isolation.

## Review operations

1. Restate the exact proposition being tested in its frozen canonical terms; identify any ambiguous or untestable claim without "repairing" it.
2. Inspect the pinned artifact independently using permitted read-only tools.
3. Re-derive relevant mappings and invariants from the artifact and canonical definitions, rather than trusting declarations, implementation comments, builder intent, prior review or test names.
4. Attempt to construct a concrete counterexample, violating trace, misleading state collapse, ownership inversion, category error or relationship mismatch.
5. Validate a suspected finding against the exact source and scope; avoid extrapolating from one implementation or test to the whole system.
6. Emit factual findings and limitations. Report that no violation was found **within the examined scope**, never "ontology correct in all cases" from finite inspection.
7. Allow synthesis only after independently completed results are preserved.

Do not turn the post-build task into exploratory redesign. A contradiction in canonical meaning is a separate authority/definition defect to escalate; the reviewer cannot rewrite the comparison baseline.

## Output contract

Provide:
- pinned artifact and canonical comparator identifiers;
- the tested conceptual claim/invariant and inspection scope;
- a minimal falsifying counterexample with direct supporting evidence **or** a bounded no-counterexample finding;
- known blind spots, unresolved ambiguity and certainty;
- source references and material needed for independent reproduction.

Outcomes: VIOLATION_SUPPORTED, NO_VIOLATION_OBSERVED_WITHIN_SCOPE, CANONICAL_CONTRADICTION, INCONCLUSIVE, NOT_RUN/BLOCKED. These are **evidentiary** conclusions, not operator acceptance or proof of universal conformance. Avoid an invented "PASS" if the review never ran.

## Authority, independence and prohibited substitutions

Strictly read-only, non-authoritative, cannot change code/specification/canonical meaning or approve deployment. An agent that contributed to the implementation or has seen undisclosed process context is ineligible for the corresponding formal independent pass. Same-family internal acceptance may be logged but not substituted for independent conformance evidence.

The role is not an Ontology Design Reviewer, Code Reviewer, Auditor, general code security tester, or implementation builder. If behavioral verification is required, route it through the relevant testing/assurance method; conceptual mapping alone does not show operational correctness. It may flag missing testable conceptual claims, but must not invent requirements to justify a gate.

## Relationship to other roles and lifecycle

- **Orchestrator:** selects eligible reviewer and isolated run only for justified conceptual claims; synthesizes evidence but does not self-review.
- **Ontology Design Reviewer:** may challenge proposed ontology in a separate exploratory process; outputs must be withheld from this clean-room reviewer before independent completion.
- **Code Reviewer/Auditor:** continue pre-consumption readiness and in-flight verification without being recast as ontology experts.
- **Testing:** may use this review to check that test-plan semantics match source claims; behavioral and test-sensitivity checks remain separate.
- **Debugging:** may use this review to check completed diagnostic records preserve fault-category distinctions, without making causal verification automatic.

## Validation and economical rollout

Test against known planted conceptual violations and **clean controls** without showing the answer to the reviewer. Measure true detection, false positives, bounded counterexample quality, canonical fidelity, contamination resistance, reviewer family effects, and cost. Evaluate separately from exploratory design review and from code review; compare targeted extra findings against the cheapest baseline. Different model-family and prompt isolation are claims to verify at dispatch, not inferred from report style. Until benchmarked, this remains a proposed role.
