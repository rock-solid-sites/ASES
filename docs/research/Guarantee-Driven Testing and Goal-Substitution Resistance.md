---
title: Guarantee-Driven Testing and Goal-Substitution Resistance
program: EDASES
layer: Research
document_type: Research Framework
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - Documentation Standard
  - "Concept: Levels of Abstraction"
  - EDASES Review Methodology
  - Evaluation Framework
consumed_by:
  - Atmosphere Free Stack Spaces Testing Methodology Plan (proposed)
related_documents:
  - AI Evaluation Protocol
  - AI Orchestration Guide
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-10-19
---

# Guarantee-Driven Testing and Goal-Substitution Resistance

## Purpose and boundaries

EDASES is investigating how to construct, evaluate, and govern reliable testing methods, including agent-assisted model-based and property-based testing. A real implementation is an experimental substrate, not the subject whose success or failure determines the research result.

The initial candidate is ATProto Spaces, because it implements private-data behavior beyond the underlying protocol's native capabilities and makes consequential claims about real software behavior. This selection is provisional until its actual documented claims and available test interfaces are verified. Defect reports for maintainers are possible secondary outputs, not a research objective.

**Zero detected defects is a fully valid experimental result.** It means no discrepancy was observed within the executed scope; it does not establish that the implementation is flawless. Conversely, finding a defect does not by itself validate the methodology.

## Specification is the boundary

Only actual, attributable claims of the target implementation may define expected behavior. Preserve the exact claim, source/version, qualifications, assumptions, and observable interface. Do not silently strengthen, weaken, or repair a claim. If it is ambiguous, contradictory, unobservable, tautological, or otherwise nondiscriminating, record the limitation and stop that claim's test construction. An untestable claim is neither a passed test nor an implementation defect.

An executable property must trace to an approved claim. A meaningful test's failure must correspond to a violation of that property, not merely to an incidental response, outage, or implementation detail.

## Research questions

1. Can documented natural-language guarantees be translated faithfully into executable properties and small independent state models?
2. Can tests demonstrate discrimination between relevant compliant and violating behavior, rather than merely passing?
3. Can generated operation histories, shrinking, and independent or metamorphic observations provide reproducible evidence under a bounded budget?
4. Do agents improve the validity, breadth, or efficiency of this process relative to deterministic and hand-written baselines?
5. Can the workflow detect and resist goal substitution: optimizing for test counts, passing rates, reported defects, superficial coverage, or task completion rather than evidence?
6. Can the workflow identify its own model, fixture, oracle, generator, reviewer, and environment failures without misclassifying them as target defects?

These are research questions, not established findings.

## Valid outcomes and evidence

Valid claim-analysis outcomes include TESTABLE, UNTESTABLE, and INCONCLUSIVE. Valid execution outcomes include NO_DISCREPANCY, CONFIRMED_DISCREPANCY, INCONCLUSIVE, and BLOCKED. Keep analysis status separate from execution status. No outcome is rewarded merely for producing tests or defects.

For each accepted executable test, require a controlled violating case that fails for the relevant reason and a compliant case that passes, **where both can be constructed without inventing requirements**. This is red/green discrimination, not proof of comprehensive sensitivity. Record when a suitable control cannot be constructed; do not fabricate one. Supplement with fault injection or mutation testing where useful. Distinguish false positives, false negatives on known controls, and inconclusive execution.

Evidence must be machine-recorded where feasible: claim identifier, approved property, source and implementation revisions, fixture versions, seeds, operation history, observations, expected behavior, execution status, minimization, and artifact hashes. Agent narratives cannot substitute for execution evidence.

## Preventing goal substitution

The research objective and each agent's bounded task must be written separately. A task contract defines authorized inputs, changes, outputs, budgets, and legitimate terminal states including NO_CHANGE, UNTESTABLE, and BLOCKED. Agents must not alter acceptance criteria to make tests easier or declare their own work accepted.

Prefer mechanical constraints over instructions where possible: frozen claim register; restricted write permissions; pinned target revision; separate reference oracle; immutable execution records; independent verification; explicit operator authority for changing scope or approved criteria. Independence should include model-family diversity and, when useful, blind review before exposure to the builder's rationale. Different models alone do not guarantee independent reasoning.

Controlled qualification cases should include tautological specifications, weakened assertions, unrelated failures, fabricated execution claims, and cases where no further work is correct. A system that cannot reject these should not be trusted merely because its production tests pass.

## Gates as reviewed design objects

Adversarial review belongs throughout the workflow, but each gate must protect a stated invariant rather than exist by default. Before execution, the gate plan itself undergoes independent adversarial design review. Each gate specifies:

- **Purpose and risk:** the precise failure mode it prevents and what happens on false acceptance or false rejection.
- **Entry and inputs:** prerequisite artifacts, frozen versions, and evidence.
- **Procedure and acceptance:** exact checks, PASS/REVISE/BLOCKED/ESCALATE decisions, and conditions for each.
- **Authority and independence:** who may review, who may advance, and who may change criteria.
- **Validation:** deliberately defective artifacts that the gate must reject, and legitimate artifacts it must not reject.
- **Cost and necessity:** expected latency/resources, overlap with other gates, and cheaper deterministic alternatives.
- **Failure transitions:** disagreement, stale inputs, exhausted budget, environmental failure, revisions, and invalidation of downstream approvals.

Mechanical gates check hashes, execution, provenance, and permissions. Semantic gates examine fidelity and relevance. Authority gates reserve scope changes and final acceptance to the operator. Reviewers recommend gate decisions; a separate controller enforces transitions. A gate's own acceptance must not become a new proxy objective.

A minimal candidate sequence is: (1) research and gate-design review; (2) specification approval; (3) harness fidelity review; (4) test validity and controlled-failure validation; (5) execution integrity; (6) evidence and research-conclusion review. These are candidates to be justified, combined, or removed in design review, not a fixed required gate count.

## Evaluation and limits

Compare bounded hand-written, deterministic model-based, and agent-assisted approaches on valid-property yield, known-violation detection, false acceptance/rejection, reproducibility, minimization, cost, and time. Evaluate gate utility with controlled defective artifacts and, when safe, ablation experiments. Record negative and null findings without forcing progress.

Testing supports scoped empirical conclusions, not universal proof of absence of flaws. The program should produce transferable reasoning, procedures, evidence standards, failure modes, and design tradeoffs. Implementation-specific choices belong in the Atmosphere free stack experiment plan, not in this research note.

## Research status

This is a discussion-derived research framework proposal, not a validated EDASES finding or canonical ASES methodology. Its hypotheses, proposed gates, and evaluation procedures require independent adversarial review and empirical validation. The concrete Spaces experiment is planned separately in rock-solid-sites/atmosphere-free-stack.
