# SR-2026-06-22-AUTOGEN — Microsoft AutoGen as first Track B evaluation

## Metadata

- **ID:** SR-2026-06-22-AUTOGEN
- **Date of decision:** N/A — Reconstructed
- **Date Reconstructed:** 2026-06-23
- **Decider:** Unknown (reconstructed from indirect evidence)
- **Selection:** Microsoft AutoGen as the first Track B harness evaluation (Crosslink issue #3)
- **Status:** Reconstructed (no live record)
- **Crosslink issue:** #3 (created 2026-06-22 01:59:09 UTC, parent #1)
- **Backfilled by:** OpenCode (Principal/Orchestrator Agent) on 2026-06-23

## The gap

This entry exists to fill a missing live record. As of reconstruction, EDASES has no structured mechanism for capturing the reasoning behind a selection at the moment the decision is made. Crosslink issue #3 was created without a description field recording *why* AutoGen was chosen. The reasoning below is reconstructed from indirect evidence and is not a substitute for a live rationale.

Reconstruction quality: medium-high overall. Each factor below carries its own confidence rating. Direct evidence exists for some factors; others are inferred from circumstantial context. This is the best the available evidence supports.

## Rationale (reconstructed)

1. **Heuristic Scouting was written with AutoGen as the intended first target.** *Confidence: medium-high.* Direct evidence: the Heuristic Scouting methodology doc (`methodology-reviews/Heuristic-Scouting.md`, closed in Crosslink #6) uses AutoGen as its worked example — Step 1: *"Query a headless browser for an AI Overview of the target (e.g., 'Microsoft AutoGen architecture')."* The example is AutoGen specifically. A random-example hypothesis is statistically weak against the corpus of well-known multi-agent frameworks; the more parsimonious explanation is that the author planned to apply the methodology to AutoGen first.

2. **AutoGen tests a different EDASES layer profile than the Addendum 01 candidates.** *Confidence: high.* Direct evidence: Addendum 01 §3 names OpenCode, OpenClaudia, and CodeWhale as primary candidates — all are *coding harnesses* that stress the Execution Layer. AutoGen is a *multi-agent orchestration framework* that stresses the Organizational, Knowledge, and Capability Layers. Evaluating AutoGen first tests whether the EDASES architecture covers the multi-agent-framework case, not just the coding-harness case. This surfaces gaps the OpenCode/OpenClaudia evals would miss.

3. **AutoGen has high-profile provenance suitable for falsifiable claims.** *Confidence: high.* Direct evidence: 59.2k GitHub stars, 8.9k forks, foundational paper (Wu et al. 2023, arXiv 2308.08155), Microsoft Research origin, explicit "pioneered several concepts in multi-agent orchestration" framing in its own README. If the project's working hypothesis is that Progressive Externalization is happening in the wild (AH-002 in Addendum 01), AutoGen is a high-signal target.

4. **The Addendum 01 §6 deliverable (Harness Capability Matrix) needed a first column.** *Confidence: medium.* Direct evidence: `capability-mapping/Harness-Capability-Matrix.md` did not exist before #3 was worked; the AutoGen evaluation produced the first column. A well-documented framework gives the matrix a recognizable anchor.

5. **The AutoGen → MAF sequencing was foreseeable from the start.** *Confidence: medium-high.* Direct evidence: MAF's existence as AutoGen's successor was public at the time of selection; the AutoGen README explicitly directs new users to MAF. The natural two-issue sequence (evaluate lineage, then evaluate successor) was available as a planning choice. The fact that #7 (Evaluate MAF) was filed immediately after #3's work finished suggests this sequencing was planned, not improvised.

## Alternatives considered

The Addendum 01 §3 candidate list names three alternatives. Each was not chosen as the *first* evaluation, for reasons that the rationale above does not capture — backfill reconstruction, again, but with higher confidence on these rejections:

- **OpenCode (coding harness)** — not chosen first because it stresses the Execution Layer only; would not test the EDASES architecture's coverage of the multi-agent-framework case. Selected as a candidate for a later evaluation once the architecture has been validated against at least one multi-agent framework.
- **OpenClaudia (coding harness)** — same reasoning as OpenCode. Not chosen first for the same layer-coverage reason.
- **CodeWhale (coding harness)** — same reasoning. The three Addendum 01 candidates are functionally similar (coding harnesses) and would have produced three evaluations with the same layer profile. The first evaluation was diversified by category instead.
- **Microsoft Agent Framework (MAF)** — not chosen first because the AutoGen → MAF lineage relationship makes the MAF evaluation more meaningful *after* the AutoGen evaluation establishes a baseline. Reversing the order would conflate "MAF's properties" with "MAF's relationship to AutoGen."

## Evidence expected to validate

What observations would prove the choice was right:

- **Layer-alignment result:** the AutoGen evaluation should produce non-trivial findings about layers other than Execution (i.e., the multi-agent-framework category should reveal something the coding-harness category would have missed). *Observed:* the eval found a Capability Layer tension (no registry despite model-client abstraction) that an OpenCode/OpenClaudia eval would not have surfaced, and a Principal Layer nuance (Studio provides trace viewing only) that wouldn't arise for a coding harness.

- **Methodology validation:** the Heuristic Scouting methodology should be applicable to AutoGen without major modification. *Observed:* applied cleanly to 4 sub-questions; the methodology doc's structure mapped directly to the evaluation flow. No methodology changes were forced by the AutoGen target.

- **MAF follow-up value:** the MAF evaluation should be meaningful as a follow-up (not redundant with AutoGen). *Observed:* the AutoGen evaluation explicitly identified 4 EDASES gaps (Organizational persistence, Knowledge store, Verification pathway, Principal surface) that MAF features (per OBS-30: time-travel, human-in-the-loop, checkpointing, graph-based workflows) are positioned to address. The two evaluations form a coherent research program, not two redundant artifacts.

- **Adversarial review catches real issues:** a multi-model adversarial review of the AutoGen evaluation should surface real defects (not just nitpicks), validating that the choice of a complex, well-documented target produces a substantive document worth reviewing. *Observed:* 3-model review caught 10 real issues across methodology, completeness, and factual-sanity dimensions. The complexity was load-bearing, not incidental.

What observations would have falsified the choice:

- If AutoGen had been in active development with frequent breaking changes, the maintenance-mode risk identified in FIN-04 would have invalidated the choice of evaluating a sunsetting framework.
- If Heuristic Scouting had required major modification to fit AutoGen (e.g., the Scout phase couldn't compress AutoGen's docs into a usable Map), the methodology would have been revealed as AutoGen-specific rather than general.
- If the EDASES layer-alignment had produced the same Finding for a coding harness (OpenCode) as for AutoGen, the category diversification would have added no value.

## What cannot be verified

- The exact moment the choice was made. No description on #3 in Crosslink; no entry in `session-handoffs/`, `research-handoffs/`, or `handoff-bundle/` records the decision.
- Whether there was a deliberation, conversation, or written rationale at decision time.
- The relative weight of each of the 5 rationale factors in the actual decision.
- The Decider's identity. The Crosslink agent ID for the session that created #3 may or may not match the agent that made the selection; this entry does not assert a specific Decider.

## Cross-references

- `research-addenda/Research Addendum 01.md` — the EDASES layered architecture that AutoGen was evaluated against
- `methodology-reviews/Heuristic-Scouting.md` — the methodology applied; uses AutoGen as worked example
- `harness-evaluations/Microsoft-AutoGen.md` — the evaluation produced by this selection
- `harness-evaluations/Microsoft-AutoGen.md.trace.md` — auto-generated evidence trace
- `capability-mapping/Harness-Capability-Matrix.md` — the Addendum 01 §6 deliverable that this selection anchored
- `scripts/validate_evaluation.py` — the Tier 1 linter, post-commit artifact of the discipline gap exposed by this evaluation

## Why this entry exists (precedent statement)

This is the first explicit acknowledgement that EDASES has a decision-provenance gap and the first explicit attempt to backfill it. Going forward, similar selections should be captured **at decision time, in a structured form, by the agent or user making the decision** — not reconstructed. Reconstruction is a poor substitute for a live record; the confidence ratings above are the cost of working from indirect evidence.

The convention this entry establishes (filename = `YYYY-MM-DD-target-name.md`, 8-field template, `Status: Live | Reconstructed` with nullable fields for backfills) is the contract for future entries. If a future selection is found without a live rationale, the gap should be flagged and a backfill entry created, but the *expected* path is live capture.
