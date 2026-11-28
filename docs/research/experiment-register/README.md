# Experiment and decision register — draft pilot

ASES-28 / WNASES-37. Distinct from streaming engineering (ASES-21). Use Work Notes draft wiki templates `experiment-registration-template-pilot` and `investigation-decision-register-template-pilot`. Retrospective pilot complete; no global methodology promotion or runtime enforcement yet.

- [Frozen pilot plan](PILOT-PLAN.json)
- [Historical decision register](HISTORICAL-DECISION-REGISTER.md)
- [Results and proposed controls](PILOT-RESULTS.md)
- [Frozen historical packets](packets/) and [execution receipts](evidence/)

## Prospective operational pilot

- [OP-01 revision 1: frozen admission proposal](packets/op-01-r1.txt) — existing ASES-19 / WNASES-16 retrieval evaluation; scoped to pinned public ASES Markdown, not a cross-repository evaluation. Separate caller-only answer key in WNASES-37. Compact independent review delivered; operator manually admitted one benchmark, now executed and scored. No global enforcement or methodology promotion.

- [Decision-only review excerpt](packets/op-01-r1-review-excerpt.txt), [first attempt (incomplete)](evidence/op-01-r1-terminal.json), [complete excerpt review](evidence/op-01-r1-excerpt-terminal.json). Reviewer returned IMPLEMENT but explicitly recommended running the experiment as scoped. This is substantive support, not an automatic ACCEPT. Preserve the enum/action conflict; resolve by explicit manual disposition, not another reviewer invocation. Fixture details were excluded from the excerpt; owner qualification and execution authority remain separate. Both exact one-call permits are closed.

- [OP-01 r1 evaluation report](https://github.com/rock-solid-sites/ASES/blob/b55f64df3cb6990ada7f26e58e9f45e0e6739ac2/docs/research/knowledge-index/OP-01-R1-RESULTS.md) and [raw receipt](https://github.com/rock-solid-sites/ASES/blob/0aeee928d581990a5a51242fb560a1cac907ae4b/docs/research/knowledge-index/OP-01-R1-RETRIEVAL.json). 16 pairs, strict source-support 14/16 baseline vs 13/16 index, 42 candidate occurrences each, all selected native raw links wrong. Scoped DISCARD recommendation; owner review pending. No further benchmark or methodology promotion authorized. Independent review attempts consumed 11,752 completion tokens (one failed, one complete), benchmark zero inference; net cost-effectiveness of the admission gate remains unestablished.

## Consolidated admission mechanism

- [Integration candidate](ADMISSION-MECHANISM.md), [pure reference predicate](reference/admission-v1.mjs), [contract tests](reference/test-admission-v1.mjs), [verification receipt](reference/verification.json). 36/36 deterministic checks passed; permissive stub failed 33/36. This is an experimental eligibility predicate, not an authorization boundary. Existing Work Notes draft templates revised in place. No global policy or runtime deployment; existing reviewer dispatch and Resource Solver own actual execution. Owner review pending.

- [Independent admission mechanism review, 2026-11-28](ADMISSION-REVIEW-2026-11-28.md): Beam ACCEPT/no findings; Hy4/HungerG no visible verdict at cap; free Console DeepSeek omitted by authenticated catalogs, no inference. All permits closed. [Capability evidence](https://github.com/rock-solid-sites/ASES/blob/e8bedc2cef8809f6167e658a32a7219a5a9c6d2a/docs/research/registry/model-feedback-admission-review-2026-11-28.md). Standalone Node/clean-checkout verification recommended; no four-model clearance or adoption.
