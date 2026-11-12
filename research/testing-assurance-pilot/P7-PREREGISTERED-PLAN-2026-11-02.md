---
title: EDASES P7 — Blind Ontology Review Benchmark and Source-First P5 Reconstruction
status: Frozen experimental plan (no role promotion)
date: 2026-11-02
authority: Experimental
---
# P7: Qualify the ontology review benchmark before interpreting agent performance

**Objectives:** (1) mechanically reconstruct P5's crash-recovery method comparison from *original archived per-check observations*, not the author's narrative; (2) construct a six-case ontology review benchmark with four defective and two clean controls, independently frozen scoring labels; (3) measure a cheap deterministic baseline and ensure each case is actually falsifiable. Formal separate-model reviewer runs remain **NOT_RUN** unless a separately identified model route executes them and returns auditable evidence.

## Separate claims and prospective controls

**R1 — Archive-only reconstruction:** Reopen the two original P5 CI ZIPs from independent GitHub storage; compute ZIP SHA-256 and CRC; extract original `p5.json` and independently recompute (not trust their `A.status` and `B.status` labels) the assertion failures by implementation and mode, checkpoint and repetition. Verify the claimed corrected fixture 90 > cap 80 by direct source diff; original 50 <= cap 80 was an oracle mistake. The original red result must not be overwritten.

**R2 — No independent-model claim:** This independent *calculation* is authored by the same assistant and is **not** independent model review. Never mark a role benchmark run independent solely because a second Python process executed it.

**R3 — Six-case control corpus:** Prepare distinct cases for Ontology Design and Ontology Conformance:
- Design: two conceptual flaws and one clean design, with scope/authority requirements supplied and optional concise design rationale.
- Conformance: two fixed-invariant artifact violations and one clean artifact, without design-process history.
All six require bounded detection claims, precise evidence, and a no-violation output option. The answer key must be committed to a separately access-controlled project before scoring, not exposed in reviewer packets or prompts.

**R4 — Cheapest benchmark before LLM use:** Run a deliberately simple deterministic rule baseline to measure detectable obvious issues and false alarms. Record that it cannot detect unanticipated semantic errors. Do not misrepresent its performance as an ordinary language-model reviewer or an independent ontology reviewer.

**R5 — Scoring evidence:** Score a future independent reviewer only against a sealed key, the exact prompt/packet hashes, model-family/route proof, contamination boundaries, observed counterexamples, false positive clean controls, missing information, elapsed time and token/cost where available. A non-run reviewer is a missing experiment, not a zero score.

**R6 — Positive and negative qualification:** Benchmark packet contains all six cases; secret key has exactly four defect labels and two clean; both role names appear only where appropriate. An invalid packet, a leaked label, a missing key, a mismatched case ID, or a false claim of an independent reviewer must be recorded as blocked/error, not as a valid benchmark outcome.

## Methods

Use existing GitLab CI to run standard-library-only Python; do not compile native implementations again. Preserve complete CI artifact ZIPs independently when recoverable, with original source jobs retained. Do not run production monitoring, booking, payment, provider APIs or stress shared resources.

Create a structured six-case evaluation packet and private sealed key. The reviewer **does not** receive the sealed key, design review findings or the author's case labels. A Design Reviewer receives domain requirements and rationale for conceptual adequacy; a Conformance Reviewer receives explicit fixed claims and artifact excerpts. Do not compare review effectiveness until each review is actually invoked under the relevant contract.

**Falsifiers:** corrupted ZIP not detected, incorrect mutant classification, incorrect fixed-funding arithmetic, leaked key in reviewer packet, clean case classified by deterministic checker as proven defective without grounded counterexample, seeded defective case missing a falsifiable invariant, or normal/baseline reasoning automatically treated as a human-authorized decision.

## Acceptance and limits

This experiment qualifies the **benchmark construction and source-first arithmetic**, not the proposed roles' performance or the global methodology. A six-case selected corpus is insufficient for general-purpose reviewer performance claims. Cost of downstream agent reviews can be measured only when those reviews actually occur. Canonical role docs and proposed PR #4 stay unchanged; accept/promote decision remains **DEFER**.
