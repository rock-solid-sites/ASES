---
title: Graph-Assisted Analysis and Review — evaluation rubric
program: EDASES
layer: Research
document_type: Research Proposal
status: Draft
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-26
---

# Graph-assisted analysis and review

Operator asks to compare chat and review agents reasoning from code graphs versus direct source. CodeGraph is already an adopted structural analysis capability; this evaluates suitability and marginal benefit, not tool selection. Related: [research charter](README.md), [source map](SOURCE-MAP.md), [comparative implementation research](../Comparative%20Implementation%20Research%20and%20Upstream%20Contribution%20Proposal%202026-11-25.md), [testing and assurance source map](../Testing%20and%20Assurance%20Source%20Map.md). No test execution authorized by this draft.

## Distinguish representation from workflow

A: source-only, normal scoped search/navigation and source reads, not deliberately inefficient full-repo dumping. B: graph-only, structural nodes, typed relationships, identifiers and locations, no verbatim source payload or generated source-based explanation. C: graph-assisted, query graph then verify relevant source, with same source access as A. Current CodeGraph Actions issue response may include source excerpts or a composed answer; inspect actual payload before classifying. If it cannot supply a pure graph representation, measure B as unavailable in that interface or label separately as graph-derived answer packet (D); never count source-bearing context as graph-only. For fixed-context secondary comparison, give reviewers equivalent-sized packets, varying only representation and access; do not conflate retrieval quality with reasoning from the retrieved evidence. Distinguish direct graph queries from receiving another agent's graph summary; the latter can introduce anchoring and evidence loss. For independent adversarial review, no builder conclusions or defect hints.

## Task-stratified evaluation

| Task | Scorable output | Expected limits to test (hypotheses) |
| --- | --- | --- |
| Architecture and mechanism discovery (chat) | Required components, interfaces, paths and qualified relationships | Structural navigation may help; graph may omit config and dynamic binding |
| Call/dependency and change-impact analysis (chat/review) | Required and extraneous nodes/edges; affected behavior/test locations | Static callers are not necessarily executed; absence of edge not proof of no caller |
| Comparative donor evaluation (chat) | Evidence-backed mechanism fit and incompatible assumptions | Need source/contract details and cross-donor semantics |
| Targeted claim falsification (review) | Correct verdict, relevant path, counterexample or explicit unresolved obligation | Conditional guards, effects, authority, ordering and failure semantics may not be represented |
| Broad defect discovery (review) | Independently confirmed distinct findings by severity and relevant missed seeded/known faults | No defect count target; valid clean controls, new findings adjudicated |
| Graph/evidence integrity (both) | Identify missing/spurious/stale/truncated relationships, correct escalation | Historical Go edge-loss and query truncation are useful controls, not current product defect claims |

Use materially different repos/languages and sizes, pinned revisions, fixed task and output contract, read-only scope. Start with a bounded pilot: six cases (two structural, two semantic/authority, one comparative composition, one clean/no-defect or graph integrity control; add controls as needed), matched fresh runs across A/B/C in each modality that can support the arm. A reasonable initial option is a chat-model block and an approved reviewer-model block; repeat on different permitted models/cases after identifying a discriminator. Do not compare different models in different arms and attribute differences to graph representation. Within a block fix model/revision, effort, instructions, harness, tool privileges except tested access, wall/token budgets, and pinned source. Randomize arm order, separate sessions, pre-register case selection and acceptable evidence; no shared answer cache across arms. Equal budget comparison first; then quality-matched cost comparison if feasible. Include failed/timeout attempts and invalid responses; record unavailable metrics instead of estimating hidden model tokens. Current public Actions route only for eligible public data; never submit private code or credentials. Use already approved reviewer routes and preserve current review independence/authorization requirements. No additional provider or paid API assumption.

## Rubric (report separate metrics, not one blended score)

| Dimension | Operational measure |
| --- | --- |
| Claim correctness | Confirmed / evaluated distinct claims; verdict accuracy by task; unresolved separate |
| Structural coverage | Recall of independently established required entities and edges; precision of reported edges; location accuracy |
| Defect coverage | Confirmed known faults found / applicable known faults; severity-stratified; novel independently validated findings separate; clean-control false alarms |
| Evidence quality | 0 unsupported; 1 plausible pointer but unverified; 2 exact source/revision supports claim with limits; 3 independent check/counterexample where required. Grade per claim against task-required level, not require runtime tests for structural questions |
| Calibration | Unsupported certainty, appropriate abstention/escalation, recognition of incomplete/truncated graph and scope |
| Retrieval effort | Queries, files/lines/bytes read, graph nodes/edges returned, duplicate reads, model-visible input tokens where observable |
| Reasoning effort | Model output/reasoning/total tokens where measured; context peak, rounds/retries, qualified claims per observed token; do not substitute output length for hidden reasoning |
| End-to-end cost | Wall time including queue/index/restore/query/source/model/retries, CPU/RAM/I/O/transfer if measured, actual provider meter if available; report cold, warm and amortized separately |
| Reusability | Same-revision repeat cost and cross-revision retained evidence validity, invalidation failures and needed rechecks |

Known-answer structural cases use independent source inspection and, when needed, separately qualified execution/oracles; the graph is not its own ground truth. Freeze oracle before test; blinded adjudicator sees shuffled outputs without arm labels where possible. Separate independently found new defects from seeded historical defects and baseline known facts. For safety-sensitive claims, missed critical fault, false assurance, wrong revision or unsupported proof is a gate failure regardless of speed. Do not equate valid uncertainty with an incorrect claim, but score incomplete answer coverage and task success separately. Report per-task paired differences and variability, not universal rankings from tiny samples. Investigate each material disagreement: graph extraction error, retrieval/query/truncation error, representation loss, model reasoning error, source ambiguity, or oracle defect.

Cost model: for n equivalent analyses at a retained revision, report total cost = index build + storage/transfer/restore + graph query + source reads + inference + retries + validation, summing per-run terms and stating units; compare to source-only at equivalent assurance. Compute break-even only if measured marginal savings positive; include index freshness/retention and false-confidence cost. Distinguish local resource use, runner costs and subscription/API usage rather than treating tokens as cash. No artificial full-source baseline.

## Initial external literature leads

- [RepoGraph, ICLR 2025](https://arxiv.org/abs/2410.14684): repository structural navigation improves reported SWE-bench outcomes in tested systems; code repair/generation is not adversarial review and results do not validate CodeGraph specifically.
- [CodexGraph, NAACL 2025](https://arxiv.org/abs/2408.03910): graph queries for repository-aware retrieval, evaluated on CrossCodeEval, SWE-bench, EvoCodeBench; useful comparison of retrieval mechanisms, not a proof of graph-only behavioral review.
- [How Should Agents See Code?](https://arxiv.org/abs/2611.07286): recent representation-comparison preprint lead; primary abstract endpoint unavailable during initial check, [reproduction repository](https://github.com/MelikaSepidband/How-Should-Agents-See-Code) describes shared retrieval and representation experiments. Inspect actual design before using results; no numerical claims yet.

## Decision rule

For each task/representation establish whether graph-only is sufficient for a bounded structural claim, graph-assisted improves or preserves qualified correctness with less effort, source-only remains preferable, or evidence is inconclusive. If necessary graph access is unavailable for a reviewer, do not count an unsupported arm as a failure of representation. Keep ordinary CodeGraph route unchanged; possible rubric promotion to comparative assurance guidance follows independent transfer evidence. First next action: choose matched cases from already pinned CodeGraph and comparative research evidence, independently define expected answers/controls, and verify exact available representation payloads and reviewer routes. No live experiments, workflow changes, universal gate or new toolkit component yet.
