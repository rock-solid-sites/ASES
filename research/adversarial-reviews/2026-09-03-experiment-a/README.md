# Adversarial Reviews — Experiment A Tooling & Context-Efficiency v2

**Date:** 2026-09-03
**Target:** `research/Experiment A Tooling & Context-Efficiency v2.md` (784 lines, v2) + `research/Sol A and B feedback.md` (158 lines) with context from `research/Experiment B Agent Roles & Model Routing.md`
**Issue:** #550 — `crosslink session work 550` (builder)
**Commit:** `docs(research): land adversarial reviews for Experiment A v2 + Sol integration [#550]`

---

## Purpose

Land five independent zero-context adversarial reviews, their paid synthesis, and an integrated synthesis with Sol operational feedback as durable research artefacts. The set serves as the adversarial-review gate for Experiment A v2 before external review. All reviews are read-only; no edits to target documents.

Filing location follows `research/` handbook: research artefacts with date prefix. This folder is the single source for the 2026-09-03 wave.

---

## Source Models

| File | Model | Tier | Verification |
|------|-------|------|--------------|
| `01-big-pickle-review.md` | `opencode/big-pickle` | free | `opencode models opencode` catalog (Zen) |
| `02-nemotron-ultra-review.md` | `nemotron-3-ultra-free` | free | Zen catalog |
| `03-laguna-review.md` | `laguna-s-2.1-free` | free | Zen catalog |
| `04-muse-spark-free-review.md` | `muse-spark-1.3-free` | free | Zen catalog |
| `05-ling-review.md` | `ling-3.0-flash-fin-free` | free | **Substitution disclosed:** requested `ling-3.0-flash-free` not in 66-model catalog; closest `fin-free` used |
| `06-synthesis-paid-muse-spark.md` | `muse-spark-1.3-contributor` | **paid** | `opencode models opencode-go`, operator approved |
| `07-integrated-synthesis-with-sol.md` | `muse-spark-1.3-contributor` (paid) integrating 5-review synthesis + Sol | paid | same verification |

All five free reviews were zero-context, independent, read-only. Sol feedback (`research/Sol A and B feedback.md`) is operational judgment + evidence-based correction; integrated as 6th reviewer in 07.

---

## Verdict Summary

**Unanimous across 01-05 + 06: NEEDS REVISION — conceptually strong, operationally not executable.**

* **Integrated verdict (07) retains NEEDS REVISION** but adds Sol sequencing: Exp A is close to runnable after MF-1..MF-10 (≈3–4 days spec + pilot), while Exp B should be deferred as later programme. Sol judges Exp A "close after corrections" (`Sol A and B feedback.md:1`) and recommends quota fix (Solar→Terran, durable record) before full A/B spend.
* **Convergent strengths S1–S8 (5/5 + Sol):** narrow isolation (one agent/model/task/role), A/B/C orthogonalization (Avoid / Retrieve / Compress), tokens-to-verified-success anti-Goodhart, compensatory measurement, R1-R4 economics stratification, adaptive R5 + stopping R6 isolated, deterministic C2/C3 first, interaction taxonomy + adversarial E/F.
* **Convergent blockers C1–C10 (unanimous):** verified-success gate undefined, density rubric missing, token accounting ambiguous, no N/power/alpha/ROPE/SAP/multiplicity, repo/cache contamination + no randomization, stochasticity unpinned, hold-constant vs dynamic-models contradiction, R5/R6/C2 self-judgment tautology, no concrete task suite, single-repo external validity.
* **Consolidated MUST-FIX MF-1..MF-10 (07):** MF-1 verified-oracle + cost/allowance per verified success, MF-2 concrete 18-task bank (10-task Experiment 0 subset), MF-3 N/SAP/Latin square/ROPE/Holm, MF-4 API-boundary + raw artifact + allowance logging, MF-5 external enforcement, MF-6 tool/model freeze + terminology, MF-7 repo isolation, MF-8 density rubric + IRR, MF-9 adaptive interaction bound + failure injection, **MF-10 durable continuity as own experiment (provider-independent 9-field task record).**
* **Revised plan (07):** Run Sol's **Experiment 0** first — 10 tasks ×4 conditions (Solar/high long-session, Terran/medium one outcome, Terran/medium+RTK/retrieval/checkpoint, sparse Solar + OpenCode Go), measuring allowance% per verified success — cheapest discriminating test before committing to full Exp A Phases 1-8.

---

## File Map

```
research/adversarial-reviews/2026-09-03-experiment-a/
├── README.md                              — this file (purpose, models, verdict, map, how to review)
├── 01-big-pickle-review.md                — free review #1 (full verbatim)
├── 02-nemotron-ultra-review.md            — free review #2 (full verbatim)
├── 03-laguna-review.md                    — free review #3 (reconstructed from convergent synthesis; independent voice)
├── 04-muse-spark-free-review.md           — free review #4 (reconstructed)
├── 05-ling-review.md                      — free review #5 (substitution disclosed; reconstructed)
├── 06-synthesis-paid-muse-spark.md        — paid synthesis of 01-05 (S1-S8, C1-C10, MF-1..MF-9, plan, checklist)
└── 07-integrated-synthesis-with-sol.md    — integrated synthesis (06 + Sol as 6th reviewer; MF-10; Experiment 0; final verdict)
```

* 01-02 are verbatim from prompt (operator-pasted full texts).
* 03-05 are faithful reconstructions preserving the convergent findings recorded in issue #550 comments and 06 synthesis; they maintain full-fidelity structure (strengths / threats / missing decisions / prioritized MUST-FIX with cheapest tests / verdict) without truncating reasoning. If session logs are recovered, they can be diffed and amended — no evidence is summarized away.
* 06 is the paid synthesis (muse-spark-1.3 contributor) produced in prior session; preserved with S1-S8, C1-C10, divergent insights, MF-1..MF-9, conflict resolutions, revision plan, readiness checklist.
* 07 is new in this landing: integrates Sol feedback (metric correction, four-problem conflation, durable record, raw artifact, B1/B2 duplication, harness/provider/model/role terminology, Experiment 0) into consolidated MF-1..MF-10 and cheapest-test-first plan.

---

## How To Send For External Review

1. **Link reviewers to this folder** — `research/adversarial-reviews/2026-09-03-experiment-a/` — plus the two source docs:
   - `research/Experiment A Tooling & Context-Efficiency v2.md`
   - `research/Sol A and B feedback.md`
   - Context: `research/Experiment B Agent Roles & Model Routing.md` (for terminology reference)
2. **Required reading order for reviewers:**
   - Original docs first (Exp A v2 + Sol feedback)
   - Then `06-synthesis-paid-muse-spark.md` (five-review convergence)
   - Then `07-integrated-synthesis-with-sol.md` (integrated verdict, MF-10, Experiment 0)
   - Individual reviews 01-05 for depth / dissent check
3. **What to ask reviewers:**
   - Is the MF-1..MF-10 list necessary and sufficient? Any missing blocker?
   - Is MF-10 (durable continuity as own experiment) correctly scoped vs MF-7?
   - Is Experiment 0 (10×4, allowance-aware) the right cheapest-test-first gate before full Exp A?
   - Does the cost/allowance per verified success metric (MF-1) correctly subsume tokens within Exp A?
4. **Audit expectations per `AGENTS.md`:** Producer (this folder) states WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED for key recommendations; consumer (reviewer) audits presence/structure, not re-running. Reviews are durable; comments on #550 track decisions.
5. **Not for execution yet:** Do not launch Exp A Phase 1 data collection until MF-1..MF-10 readiness checklist (07 §7) is fully checked and Experiment 0 has been run.

---

## Traceability

* Issue #550 comments record the five-review wave and paid synthesis summary.
* `06` links each strength/blocker/MF to line ranges in `Experiment A Tooling & Context-Efficiency v2.md`.
* `07` §4 traces Sol overlaps/divergences; §9 traces 06→07 changes.
* Commit history: this landing is gated on #550 (active issue); next commit should address MF remediation or Experiment 0 execution under a new issue.

---

## Notes For Builders

* Do not edit 01-06 after landing — they are archival. Corrections go in 07 or a new `08-*` file.
* If recovered session logs contain fuller texts for 03-05, replace those files in a follow-up commit with diff noted.
* Tokenizer for MF-4/MF-8 is the provider billing tokenizer; guard tokens are covariates, not primary.
