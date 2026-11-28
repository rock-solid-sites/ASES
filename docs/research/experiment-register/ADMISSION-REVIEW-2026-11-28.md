# Independent review of admission v1 — 2026-11-28

**Outcome: one complete ACCEPT, two incomplete reviews, one model blocked before inference.** This is not four-reviewer clearance. ASES-28 / WNASES-37 remain in review. No runtime adoption or code changes made on the strength of a model verdict.

## Frozen scope

[Review packet](packets/admission-v1-review.txt), pinned reviewed revision 8314413c7b6d989ce72e26019e1583d400edf21b, packet commit 8c0ea0446019018b59204281a216562ff1a0eea7, SHA-256 5d689083b5a1054d92650d872233b2d3eead50a28edeb304ba67536eb83766c2, 9817 bytes. Same decision/contract excerpt and exact validator with test names, not complete specification/test bodies. No previous verdicts, no tools, read-only public packet, 8192 completion token cap, 90 seconds per inference, one request per eligible model, zero additional monetary spend, no fallback/retry. Model identity from selected route and wire check, not independent vendor attestation. OpenCode CLI 2.4.2; exact same-job source/permit/dummy-wire checks. Different reasoning settings are a confound, not a ranking experiment.

| Requested model/route | Reasoning | Inference s | Input | Completion | Provider reasoning tokens | Outcome |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| [Go Hy4 Flash Free](evidence/admission-v1-review-hy4.json) | default | 41.034 | 2775 | 8192 | 8192 | Length, no answer |
| [Go HungerG Free](evidence/admission-v1-review-hungerg.json) | default | 79.120 | 3049 | 8192 | 0 | Length, no answer |
| [Go Beam Free](evidence/admission-v1-review-beam.json) | low | 9.641 | 2763 | 1289 | 1205 | ACCEPT, no findings |
| [Console DeepSeek V4.1 Flash Free](evidence/admission-v1-review-deepseek-preflight.json) | none (dry only) | — | — | — | — | Blocked before inference |

Three admitted requests, 8587 input and 17673 completion tokens, provider-reported cash/list/allowance all zero; independent invoice verification absent, replay NOT_FREE_CLASSIFIED retained. All three request/completion/cash reservations settled; no overrun or orphan. Hy4 and HungerG continuation blocked. HungerG's provider-reported zero reasoning tokens conflicts with 39873 decoded reasoning characters; do not infer zero reasoning work. Hy4 had 35311 decoded reasoning characters. Beam provider retention non-ZDR; no private input.

## Findings and disposition

Beam's hash-verified strict JSON verdict ACCEPT contains no material findings, recommends standalone Node import and clean-checkout testing, and explicitly limits its assessment to supplied source/test names and assumed controller guarantees. This corroborates the already documented verification gap; it does not prove the pure predicate complete, the controller trustworthy, or scientific necessity automatically checkable. No source defect reproduced in this review. No verdict attributed to failed/blocked models.

DeepSeek Go model has nonzero listed prices. Official [Console models](https://opencode.ai/docs/console/models/) list the distinct free variant. [GET-only catalog diagnostic](evidence/admission-v1-review-deepseek-catalog.json) verified that public listing has exact zero input/output/cache and expected endpoint; both authenticated inference and workspace lists returned HTTP 200 but omit the free model. The reason for omission is unknown. The exact Console wire dry run passed; account qualification did not, so no inference or substitute. No retry to seek a different verdict.

The proportionate next action is the already identified deterministic standalone module verification, not global enforcement and not automatic repeated model reviews. If broader independent scrutiny is required, scope a short focused packet or explicitly authorize a suitable route and envelope; do not claim four-model approval. ASES-13 retains reusable dispatch work; no new reviewer service. Review permits closed and operations removed from protected executor at 90f1bc4b74e1a1a77811c150a735a346c9934d59 (Go closure 804a9370c2b8124191a5a57e53537e45eb78051e, DeepSeek closure 224ad1b08b0945635c85e5e5ed345e160fbf36f3).
