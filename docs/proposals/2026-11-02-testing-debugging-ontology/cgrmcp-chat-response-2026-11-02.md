---
title: cgrmcp Chat — Response on Testing, Debugging, and Ontology Proposals
program: ASES / EDASES
document_type: In-Context Discussion Draft
status: Draft commentary; not adopted policy
authority: Research / Discussion
date: 2026-11-02
target_conversation: cgrmcp research and optimization
related_proposal_branch: proposal/testing-and-assurance-method-2026-11-01
---

# Response from the cgrmcp Development Discussion

The [ASES testing, debugging, and ontology proposals](https://github.com/rock-solid-sites/ASES/tree/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology) are well aligned with cgrmcp's direction. **I recommend adopting the shared reasoning and evidence discipline provisionally, but not promoting the proposals to mandatory ASES-wide policies or adding permanent review roles yet.** This response records an opinion from the ongoing cgrmcp project discussion, **not a handoff, instruction to another agent, or acceptance decision**.

## What the cgrmcp work demonstrates

cgrmcp is a read-only, commit-pinned CodeGraph research connector. Its ongoing multi-forge work has tested GitHub regression, Tangled, GitLab, Codeberg and SourceHut, SHA-1/SHA-256 handling, and bounded source delivery. Those tests give a useful real-world illustration of why **test execution, evidence sufficiency, causal diagnosis, and release acceptance must remain separate**.

- A successful Git clone or four-tool MCP sequence demonstrates transport and operational compatibility at a particular pinned revision; **it does not prove the returned call graph or source answer is correct**. Likewise, 774/774 eligible source files indexed is not evidence that all tracked files, symbols and relationships were understood. Negative controls and known-correct source locations are still needed.
- GitLab's implicit `.git` redirect, SourceHut's non-`main` default branch, and a live test's incorrect file-line range each required different diagnoses. These failures should remain visible, including the test-harness fault, instead of being retrospectively labeled implementation defects or erased by a later green run.
- The current `focused` response mode largely caps an already-generated exploration; reduced response bytes have **not yet demonstrated reduced total tokens per correct completed task**. The proposal's instrument-qualification principle argues for checking follow-up calls, answer correctness, CPU/RAM/disk and end-to-end agent cost.
- Repository tests do not constitute acceptance of the installed ChatGPT app. The source branch, running backend, client tool schema, and actual user-facing invocation are separate acceptance surfaces. GitHub Actions links also do not, by themselves, constitute an independent durable evidence archive.

The appropriate small record is: original claim and surface; source revision; competing explanations and pretest predictions; cheapest discriminating test and positive/negative controls; actual observed result and execution classification; supported conclusion and unverified boundaries; archive integrity; authorized decision or next check. It can live in an existing PR or experiment note rather than requiring a large new event schema.

## Debugging is causal isolation, not indiscriminate testing

The [Debugging and Fault Isolation Method](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md) usefully formalizes what worked in the cgrmcp host experiments: start with the specific observed deviation, predict how rival causes would behave under a cheap test, make the smallest correction the evidence supports, and re-run the **original** user-visible operation. A failure in a test instrument should trigger an instrument investigation; a green unrelated regression suite is not a substitute for that original-operation check.

The [Testing and Assurance Method](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md) answers the complementary question: which kinds of evidence would establish a particular claim and how sensitive is the selected instrument to the relevant wrong behavior? This is a useful *method-selection discipline*, not a requirement for mutation testing, full state modeling, or adversarial reviewers on every cgrmcp change.

## Ontology roles: justified distinction, conditional invocation

The proposed [Ontology Design Reviewer](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/ontology-design-reviewer.md) asks whether the concepts and boundaries are appropriate. For cgrmcp, this could challenge the separation between **canonical Git URL, actual transport/knot location, immutable commit/object format, snapshot identity, index coverage, structural correctness, and per-agent context**.

The proposed [Ontology Conformance Reviewer](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/ontology-conformance-reviewer.md) instead tests whether a finished artifact respects already-approved meanings, preferably in a clean room and with falsifiable examples. For instance: do different Git object formats remain isolated, and can one agent's prior exploration ever suppress evidence another agent still needs?

Both operations are useful; **they need not become automatically launched agents or mandatory sequential stages**. First compare them against the existing umbrella ontology role, ordinary code review, and deterministic checks. The initial proposed six-case comparison is a seed for measurement, not proof that two new roles improve outcomes. Any formal independence claim must reflect the actual reviewer model and context isolation. The earlier [integration patch](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/integration-changes.patch) still targets the combined ontology role and should not be applied unchanged.

## Current disposition and evaluation

We have already begun a [project-local evidence-discipline trial in the cgrmcp branch](https://github.com/rock-solid-sites/ases-plugins/blob/feat/cgrmcp-phase1-multiforge-2026-11-02/docs/CGRMCP-EVIDENCE-DISCIPLINE-TRIAL-2026-11-02.md). It records new consequential tests' hypotheses **before execution**, separates observations from interpretations, preserves errors and unverified archives, and explicitly avoids imposing a new ASES-wide gate. The planned checkpoints are after **three** and **ten** new meaningful diagnostic/test episodes (or Phase 1 qualification), with actual accuracy, false classifications detected, repeatability, tokens/time/tool calls and process overhead assessed rather than assumed. Earlier runs are retrospective examples, not manufactured pre-registrations.

The same approach should inform proposed cgrmcp optimizations: compare CodeGraph 1.6.0 against 1.6.2 and targeted source retrieval using pinned repositories and correct-answer oracles, rather than presume that importing another graph engine or stripping CodeGraph improves efficiency. GitNexus provides useful architectural comparisons, but its PolyForm Noncommercial license means its implementation should not simply be incorporated into commercial cgrmcp work.

**Recommendation:** preserve the proposals as drafts, selectively incorporate their evidence/diagnostic distinctions into live project experiments, and promote only the elements that demonstrably prevent wrong conclusions or materially improve work relative to their cost. The shared principle is to preserve the difference between **what we predicted, what ran, what was observed, what that establishes, and who authorized the resulting decision**.
