---
title: Ontology Review Integration - Comparison and Adoption Plan
program: ASES
layer: Methodology
document_type: Methodology Proposal
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/roles/Ontology-Reviewer.md
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/research/EDASES Review Methodology.md
related_documents:
  - docs/proposals/2026-11-02-testing-debugging-ontology/ontology-design-reviewer.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/ontology-conformance-reviewer.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md
  - skills/prompt/SKILL.md
consumed_by:
  - ASES review architecture reconciliation (proposed)
supersedes: []
superseded_by: []
last_updated: 2026-11-02
---

# Ontology Review Integration — Comparison and Adoption Plan

## 1. Problem and scope

The earlier proposed umbrella Ontology Reviewer in docs/roles/Ontology-Reviewer.md covers *exploratory conceptual design* and *independent fixed-claim conceptual conformance*. A September 2026 design note and Prompt Skill already describe these as separate **review domain versus review mode** axes. The November 2026 testing and debugging proposals independently converge on the same need to avoid category errors before constructing tests or diagnosing faults.

The operator's latest direction is to define two **distinct named roles**, then review them alongside other concurrent ASES work **before** making active changes to role dispatch, the Prompt Skill, the Build Method or canonical policy.

## 2. Proposed roles, not extra phases

| Selection question | Proposed role | Distinct operation | Context rule |
| --- | --- | --- | --- |
| Is the proposed conceptual representation justified or missing distinctions? | **Ontology Design Reviewer** | Challenge or improve concept identity, necessity, ownership and relationships | Exploratory context and rationale may be useful |
| Does a completed artifact preserve approved concept meaning? | **Ontology Conformance Reviewer** | Try to falsify a fixed conceptual claim | Clean-room: pinned artifact + canonical definitions + invariant + assumptions |
| Are tests actually sensitive to wrong behavior? | Existing testing/assurance techniques | Qualify instruments and evaluate behavioral evidence | Evidence relevant to the selected claim |
| Why does runtime behavior differ from requirements? | Existing debugging and fault-isolation method | Separate causal hypotheses with cheapest discriminating tests | Observations and controlled comparisons |

Either ontology role may be invoked during a larger project investigation as its reasoning operation demands. This is not a mandatory order of four phases; a Design Reviewer does not automatically imply a later Conformance Reviewer, or vice versa.

## 3. Existing roles remain distinct

- **Code Reviewer** (per docs/ORCHESTRATOR.md): assesses implementation readiness, testability, evidence presence and calibrated claims; does not become a domain ontology authority.
- **Auditor:** detects in-flight divergence and evidence/position mismatch; no duplicate verifier role.
- **Ontology Design Reviewer:** examines appropriateness of the conceptual model, before it hardens into a fixed contract. It cannot create canonical meaning on its own.
- **Ontology Conformance Reviewer:** independently checks fixed conceptual invariants after an artifact exists. It cannot redesign the model or declare whole-system safety.
- **Orchestrator:** selects bounded domain-specific work and routes results; it does not do the specialized review itself.
- **Human/operator or authorized governance:** decides whether canonical definitions, scope, releases or material design commitments change.

All named reviewers are read-only, independently routed when formal review is claimed, and their findings remain evidence rather than decisions.

## 4. Candidate operational entry points — NOT APPLIED

The file integration-changes.patch preserves the **exact earlier draft edits** to these active paths, but those edits were written when the ontology role was still named generically. They should be **revised for the newly separated role contracts**, not automatically applied.

1. **docs/ORCHESTRATOR.md:** add selective triage for material ontology changes; route Design versus Conformance according to problem, not a universal gate. Maintain current Reviewer/Auditor responsibilities and read-only separation.
2. **docs/methodology/ASES Bounded Project Build Method.md:** before freezing the Implementation Packet, consider Design Review for unresolved ontological questions; under existing independent verification, choose Conformance Review for material fixed conceptual invariants.
3. **skills/prompt/SKILL.md:** replace generic ontology-review mode pairing with two independent role selections while retaining domain/mode semantics, task-specific context compression, actual model route provenance and minimal prompts.
4. **docs/roles/Ontology-Reviewer.md:** retain as historical umbrella with a proposed supersession path only after separate role contracts pass review/benchmark. Avoid two competing active role authorities.
5. **Testing and Assurance Method proposal:** choose Design Review to catch an incorrect test/spec concept before tests are frozen; choose Conformance Review to challenge finished test-plan conceptual mappings. Neither substitutes for instrument sensitivity tests.
6. **Debugging and Fault Isolation Method proposal:** choose Design Review when a fault taxonomy or causal boundary is conceptually wrong; choose Conformance Review for a finished diagnostic artifact's mapping to canonical concepts. Neither proves causal attribution by itself.

## 5. Comparison work against other conversations

Prior to deciding on adoption, compare each candidate change to the most recent work elsewhere on:
- role count and whether role boundaries already changed;
- Orchestrator/Auditor/Reviewer semantics, pre-consumption gates, in-flight verification;
- existing prompt operations and fresh-context isolation;
- VSDD/assurance architecture and test-first workflow;
- ASES Work Units, project state, Observer and resource-solver records;
- concept/ontology registry authority and how canonical changes are approved;
- planned model routing, free/paid budgets, and agent launch caps.

Record conflicting statements and their **source, date, authority, evidence, and scope**, rather than using recency or document location alone to resolve them. Prefer existing canonical definitions over new invented structures. Do not merge independent review results before independent passes complete.

## 6. Promotion and validation criteria

**Design Reviewer** should be tested on defective and clean conceptual designs: high-signal issue detection, appropriate alternatives, unjustified abstraction creation, false positives and cost.

**Conformance Reviewer** should be tested on fixed concepts and finished artifacts: planted violations, clean controls, reproducible counterexamples, absence of process-history leakage, independent model provenance, false positives and cost.

The proposed historical initial benchmark is six cases (four defective, two clean). Verify the actual material and controls before treating the case count as measured data. Compare both roles to baseline ordinary review and direct deterministic ontology checks. Retain prompts, inputs, route provenance, results, disagreements and decisions. If additional role launches fail to improve outcomes enough to justify their cost, narrow or reject automatic invocation.

Only after review and evidence should canonical docs be updated, and then **adapt the integrations to the two role names**, rather than blindly applying the earlier generic-role patch.
