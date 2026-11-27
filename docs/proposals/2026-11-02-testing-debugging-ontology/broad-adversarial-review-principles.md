---
title: Broad Adversarial Review — Proposed Principles
program: ASES / EDASES
layer: Methodology
document_type: Methodology Proposal
status: Draft
authority: Experimental; not adopted ASES policy
canonical_repository: ases
depends_on:
  - docs/research/EDASES Review Methodology.md
  - docs/research/prompting/Ontological Connection to Review Skill.md
  - skills/prompt/SKILL.md
related_documents:
  - docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md
  - adversarial-reviews/Adversarial-Review-Protocol.md
  - adversarial-reviews/adversarial-review-prompt-inventory.md
supersedes: []
superseded_by: []
last_updated: 2026-11-12
---

# Broad adversarial review — proposed principles

> **Proposal only.** This records a candidate default approach to adversarial review, not an adopted ASES-wide gate, a replacement for existing reviewers, or authorization to alter production systems. Evaluate and reconcile it with the current ASES review methodology before promotion.

## Purpose and default

An adversarial review should **discover what development failed to consider**, not simply verify the defects, requirements, examples, or test cases the builders already know about. Its primary operation is independent, sustained **attempted falsification** of an artifact and the assumptions that make the artifact appear correct.

**Broad, open-ended review is the proposed default** when the goal is to assess an implementation, test system, or design before its problems become costly to correct. A narrower, targeted review remains appropriate where there is a specific bounded claim, risk, regression, or question. The modes complement rather than replace one another.

Broad does not mean context-free: reviewers need the pinned artifact, its actual purpose and externally established constraints. It means **the reviewer, not the prompt author, chooses where and how to search for failure**.

## Depth must be earned in the investigation, not asserted in the report

A source skim, summary of the architecture, checklist recitation, or observation that the existing suite passes is **orientation**, not completion of an adversarial review. The reviewer should engage with implementation behavior sufficiently to challenge it:

- Reconstruct consequential behavior from the actual code, data flows and interfaces instead of relying on headings, test names, builder descriptions or claimed invariants.
- Pursue suspicious or poorly understood behavior through the necessary functions, dependencies and boundaries, including otherwise unremarkable surrounding code. Read and reason about individual implementations in full where a credible failure could hide there.
- Attempt to make the implementation violate its purpose, using independently derived counterexamples, controlled experiments, alternative oracles, or other available methods. Existing tests are potential evidence and potential objects of criticism, not the perimeter of the investigation.
- Revisit the initial explanation when a probe contradicts it, and pursue consequential leads rather than stopping at the first plausible bug or satisfied hypothesis.

These are **engagement principles, not a prescribed sequence or attack checklist**. Reviewers retain freedom to decide where deeper scrutiny is warranted. Neither every line receiving equal attention nor a fixed number of attacks is a useful measure of depth. Tracing a critical path thoroughly may be more valuable than mechanically scanning thousands of files.

For a substantial review, a report that contains only generic observations, source-level speculation, or reformulated test expectations **does not establish that deep engagement occurred**. Evidence should make clear what the reviewer actually examined or challenged, how that bears on the finding, and where investigation stopped. Extensive writing or elapsed time alone does not establish depth.

## Independent discovery and protection from anchoring

The initial broad review prompt should be deliberately sparse: identify the repository or artifact and immutable revision, state the broad objective, invite exhaustive inquiry where warranted, and set only indispensable execution/safety boundaries.

In particular, **do not feed independent first-pass reviewers** builder rationales, known defect lists, expected weak points, previous review conclusions, proposed mutations, or a long catalogue of likely edge cases. Such information can shrink the reviewer’s search space and make unrelated blind spots less likely to be found. Canonical requirements that define correctness are legitimate context; the developer’s story about why the system is correct is not authoritative.

Run formal independent reviews in fresh contexts, with cross-family model provenance established by the dispatch mechanism where applicable. Withhold peer outputs until each review is complete, then synthesize divergences and intersections. The synthesis phase may use previously known failures and detailed prompts to investigate contradictions. Independent review and synthesis are separate evidence-producing operations.

## Cost asymmetry and investigative persistence

A defect discovered while an implementation is still provisional is often cheaper to repair than one discovered after integration, data migration, real use or deployment. When that asymmetry is material, **thoroughness should take precedence over a fast superficial verdict**.

Reviewers should not stop because the conventional checklist is complete, the first hypothesis fails, tests are green, or the first defect is found. Continue where uncertainty and potential consequence justify further investigation. An initially minor anomaly may justify tracing an entire code path; an apparently central module may warrant little additional effort once strong evidence closes the question.

This is **not** an unlimited-runtime mandate. Depth should be proportional to consequences and marginal information gained. The caller may impose resource or execution boundaries; reviewers should report those boundaries and their effect on confidence rather than treating budget exhaustion as successful completion. The stopping basis should be evidential, not arbitrary token counts, file quotas, or the appearance of progress.

## Falsification without manufactured findings

Adversarial means trying to break assumptions, not adopting a requirement to produce a certain number of bugs. A reviewer must be willing to conclude that no material defect was found **within the investigated scope**. No material finding is preferable to speculative vulnerabilities, irrelevant style criticism, or invented requirements.

Distinguish:
- behavior actually reproduced or otherwise directly established;
- plausible risks or assumptions not yet falsified;
- untested surfaces and environment restrictions;
- disagreement with design choices rather than a demonstrated failure.

Findings should be traceable to the relevant source and observed evidence. A test failure, a planted mutant, a mock response and a live-system failure are different kinds of evidence; neither one should be silently promoted into another. The reviewer should challenge the evidence instruments themselves when their credibility matters.

The review outcome remains an input to human decision-making, not permission for the reviewer to change accepted requirements.

## Broad and targeted reviews

**Broad exploratory review** asks, in substance: *What is wrong, fragile, missing, or misunderstood here, including things we did not think to ask about?* It searches across implementation, tests, interfaces and assumptions, deepening according to emerging evidence.

**Targeted falsification** asks: *Does this specific property hold under these assumptions?* It can use a smaller context, a more precise claim and a narrowly chosen experiment. Targeted reviews are valuable for high-consequence properties, regressions, unresolved findings, and follow-up verification. They should not substitute for a broad first pass when the purpose is to uncover unknown failure modes.

A broad review may identify questions that deserve subsequent targeted reviews. Do not force broad and targeted work into a universal sequence, new mandatory phase, or review-agent count.

## Lightweight dispatch and evidence

The **method** may be detailed; the **reviewer-facing prompt** should not be. Stable review principles belong in project documentation or a selected reviewer skill, not as a checklist pasted into every review. Reviewer identity and model routing belong in trusted launch/provenance records, not the receiving model's self-description.

An example of the intended *shape*, not a mandatory template:

> Independently investigate the implementation and its tests at the specified revision. Actively try to break it, pursue unforeseen edge cases and unsupported assumptions, and follow important code paths as deeply as warranted. Choose your own methods. Report substantive findings with evidence and say what remains unverified. Do not alter the reviewed branch or production systems.

A credible result preserves enough information for another investigator to distinguish *what was examined*, *what was actually attempted or observed*, *what the finding means*, and *what was not established*. A mandated long report form can itself encourage performative completeness; prefer concise, reproducible evidence.

Read-only review should not mutate the target branch or production system. If controlled experiments require changes, use isolated disposable copies and restore a clean baseline. Existing safety and authorization boundaries continue to apply.

## Validation before adopting this default

The proposed approach must itself be evaluated. Compare independent broad reviews against more directed reviews on artifacts with genuinely unknown problems as well as known defective and clean controls. Examine whether open-ended prompts discover **additional substantiated failure classes**, improve depth and discrimination, or merely increase cost, repetition and false positives.

Useful counterevidence includes reviewers who spend substantially longer without reaching consequential code, invent findings to appear thorough, miss obvious defects that a focused review would find, or repeatedly reproduce the same known failure. Do not infer review quality from word count, a defect count, reviewer confidence or model prestige.

**Open question:** what minimal observable engagement evidence best discourages shallow completion without converting broad review into a prescribed checklist? Test competing lightweight approaches before establishing a global gate.

## Relationship to existing ASES work

This proposal is meant to sit beside the [Testing and Assurance Method](testing-and-assurance-method.md), the canonical EDASES review principles, and the existing Prompt Skill distinction between exploratory and post-build review. It does not supersede the earlier adversarial-review protocol, fixed-comparison prompt inventory, code reviewers, ontology reviewers or project-specific verification processes.

If adopted, future documentation should clearly distinguish this broad-discovery default from the tighter clean-room **single-claim conformance** operation, preserving reviewer independence in both. No operational routing or reviewer prompt changes are made here.
