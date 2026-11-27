---
title: GLM-4 pilot run log and research programme
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Run Log
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-28
---

# GLM-4 pilot run log and research programme

Experimental research record from the authorized G4 pilot. Not an architectural
decision. Each study below carries its own evidence and limits; this log records
starting context, programme selection and checkpoint history for the run.

## Starting context (recorded as supplied)

- Frozen assignment: `docs/research/astra-followup-20261125/frontier-comparison/G4-RESEARCH-PILOT.md`
  as read at commit `fc4770a468a1de89c58b6e81337be67b7b94e869` (re-read verbatim at run start; matches the
  assignment supplied to this run).
- Operator-supplied start revision (recorded verbatim): `dcc8c5e34614459ce1944780e72dceb3d2d9ad89`.
- At run start, `origin/main` had advanced two commits beyond that local checkout
  (`9c303a825`, `538fe90b5`, both `docs/research/historical-idea-recovery/` only). The checkout was
  fast-forwarded to `538fe90b5` before any research edit; no history was rewritten. All kernel-0
  content is identical between `ed0266c4` (the pinned research index) and the fast-forwarded start.
- Pinned research index read: `docs/research/kernel-0/README.md` at `ed0266c4a9e606a2b5112cc0aeaa19221561dea2`.
- Boundary conditions honored: publication only under `docs/research/kernel-0/glm-g4/`; no edits to prior
  research; no subagents; no model substitution; no credential inspection; experimental status only.

## Frontier assessment at start

The existing corpus (24 studies, 25 scripts, 6 SMT files at the pinned index) resolves, within stated
boundaries: local handover witnesses; gate selection, abort and catch-up with fixed and changing
membership; gate snapshot recovery; receipt/retry/custody continuity; nested-authority relocation and
seal state; decision-cost lower bounds; recovery-stamp encodings and their online maintenance cost.

Explicitly open boundaries named by the corpus:

1. **Selector (owner) storage rollback.** `Abortable-handover-and-catch-up.md` tested no selector
   storage rollback; `Recovering-a-gate-with-votes-in-flight.md` repairs a rolled-back *gate* and
   states that none of its procedures "repairs rollback of the selector itself". The gate-rollback
   proof also leans on the premise that "attempts never repeat" when discarding decided votes.
2. **Acknowledged publications vs the trusted updater** agreeing across process or storage failure
   (kernel-0 README open boundary).
3. **Native-owner correspondence** (general distributed conformance; explicitly outside local scope).

## Chosen programme

**Q1 (selected).** *When is an earlier selector image safe to resume?* This is the mirror of the
solved gate-rollback question, on the side the corpus explicitly leaves open, and it composes three
prior results: the abortable handover protocol (whose "nonreused increasing attempt numbers" premise
rollback breaks), the gate-rollback threshold (whose selector is assumed at its true latest state),
and the tenure-reuse lower bound (whose drain premise an undrainable vote channel violates).
Working hypotheses at start:

- H1: a restored selector can complete a commit of a *reused* attempt number using escaped votes
  emitted before its image was taken, installing a never-authorized tenure.
- H2: an exact resumption threshold exists in the same style as the gate study's `t ≥ max(u+1, a)`,
  expressed against the never-rolled-back gate floors, and the necessity of each clause is an
  indistinguishability argument.
- H3: the gate-local rules cannot be strengthened to prevent this without external evidence
  (a two-store indistinguishability argument), so the repair must live in the resumption procedure.

Status markers used below: **D** = demonstrated (executable or deductive within stated premises),
**C** = conditional argument, **H** = hypothesis, **O** = open proof obligation.

## Checkpoint history

| # | Commit | Content |
| --- | --- | --- |
| 0 | (this commit) | Run log, starting context, frontier assessment, programme. |
| 1 | (next commit) | Q1 results: [Selector rollback recovery](Selector-rollback-recovery.md) with executable model [selector_rollback_recovery.py](selector_rollback_recovery.py). |

## Q1 outcome (recorded at checkpoint 1)

All three working hypotheses held and are now demonstrated, with one sharpening
discovered during falsification: the absorption bound that a resumed selector
must respect is set by gate floors *plus issued summaries*, not floors alone —
an aborted attempt whose summary is still in flight is invisible to gates and
is exactly the shortest forgery. Consequences:

- **[D]** Unrepaired resumption fails two ways: a three-step forged tenure
  (re-commit of a forgotten abort from a retained receipt) and a four-step stale
  reopen (abort summary binding the forgotten tenure). 6,241 of 6,769 restored
  images admit harm in the one-gate bounded model; 3,649 of 4,219 with two gates.
- **[D]** No gate-local rule can repair this (two-worlds indistinguishability,
  asserted in the script): the acceptance that ordinary catch-up liveness
  requires is the one rollback exploits.
- **[D]** Two sufficient resumption rules — withhold summaries until one
  commit above the trace bound, or renumber past the bound plus one of the two
  withholdings — each clause necessary against the other's absence; the exact
  condition subsumes both.
- **[D]** The append contract and the grant-authorization contract diverge
  under rollback: summary withholding alone still minted 415 contained forged
  grants; renumbering alone still admitted 3,572 stale reopens.

Challenge to prior conclusions: the abortable study's "attempts never repeat"
premise (also load-bearing for discarding decided votes in the gate-rollback
proof) is unsound across selector rollback and must be replaced by the resumption
floor over traces; the gate-rollback study's recovery procedure remains valid
because it holds the selector at true-latest state, but its mirror needed the
spool, an evidence source outside both the gate and the rolled-back selector
domain — a new placement obligation for any realization.

Remaining Q1 proof obligations are recorded in the study's boundary. Next
frontier reassessment: the README's trusted-updater agreement obligation and
the custodial consequence of a forgotten commit (the resumed selector that
forgets a commit forgets its accepted-prefix custody transfer) are the live
candidates for a second investigation.
