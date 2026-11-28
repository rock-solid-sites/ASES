---
title: "G4 pilot (GLM-5.3) run log and research programme"
version: 0.1.1
program: ASES
layer: Research
document_type: Experimental Run Log
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-28
---

# G4 pilot (GLM-5.3) run log and research programme

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
| 0 | e65dc6d69 | Run log, starting context, frontier assessment, programme. |
| 1 | 98262c6b4 | Q1 results: [Selector rollback recovery](Selector-rollback-recovery.md) with executable model [selector_rollback_recovery.py](selector_rollback_recovery.py). |
| 2 | b02f92960 | Q2 results: [Custody after a forgotten commit](Custody-after-a-forgotten-commit.md); model extended with forgotten-commit window counts. |
| 3 | (this commit) | Run-end wrap: precision fix to study evidence text; 3-gate breadth attempt recorded as failed (host memory); resume point and uncertainties below. |

## Run-end record (2026-11-28)

**Bounded coverage.** Verified configurations: one gate with attempts ≤ 3
(700 phase-one states, 7,586 image records, 6,769 restored runs per rule) and
two gates with attempts ≤ 2 (526 states, 4,796 records, 4,219 runs). A third
breadth configuration (three gates, attempts ≤ 2) was attempted and **failed
mechanically**: the process died silently at 2m30s with no output, consistent
with an out-of-memory kill during the phase-one image fixpoint on this 2-core/8
GB Codespace (the script's first print follows the fixpoint, so buffered output
was lost). This is a coverage limitation of the executed evidence, not of the
claims; the two smaller configurations carry all published results. A machine
with more memory should re-run `selector_rollback_recovery.py 3 2 4` before
trusting the invariant counts at three gates.

**Artifacts produced (all under `docs/research/kernel-0/glm-g4/` on main).**

- [RUN-LOG.md](RUN-LOG.md) — this record.
- [Selector-rollback-recovery.md](Selector-rollback-recovery.md) — Q1 study.
- [Custody-after-a-forgotten-commit.md](Custody-after-a-forgotten-commit.md) — Q2 study.
- [selector_rollback_recovery.py](selector_rollback_recovery.py) — self-verifying executable model for both studies.

**Exact resume point.** The next investigator should start from commit (this
commit) on main and, in order of expected value: (1) port the resumption-rule
induction obligations to SMT-LIB in the style of `abortable_induction.smt2` —
the trace lemma, the two sufficient-rule invariants and the abort-binding
necessity — noting that this Codespace hosts no `z3`/`cvc5` binaries, so the
obligations were checked only by bounded enumeration; (2) compose the
resumption floor with changing membership (`Changing-the-set-of-resource-owners.md`
semantics under rollback); (3) make the custody reconciliation rule executable
in the surviving-content study's certificate terms (store-cut verification at
the first fresh commit); (4) re-run the three-gate breadth configuration on a
host with more memory. Q1 and Q2 boundary sections list the remaining proof
obligations in detail.

**Uncertainties that remain.** All results are bounded-model demonstrations or
explicitly marked conditional arguments; neither study has independent replay,
SMT obligations, or runtime conformance evidence. Study 2's core claims
(control-plane obliviousness, truncation/reclamation witnesses, the
reconciliation rule's safety) are [C]-marked arguments grounded in the [D]
window counts, not enumerated content histories. The convergence counter is a
lower bound by construction. Harm counts depend on the conservative
"every issued message stays deliverable" premise. Selector failover (two live
selectors), store rollback sharing the selector's domain, hostile corruption
beyond genuine images, and changing membership under rollback are unmodeled.
No result selects an implementation; everything is experimental/provisional.

## Q2 outcome (recorded at checkpoint 2)

Composed the rollback result with the custody/receipt family: the
forgotten-commit window is the majority case (3,572/6,769 one-gate; 1,358/4,219
two-gate restored images [D]); the control plane is structurally oblivious to
accepted contents, so no procedure keyed to the resumed selector's regressed
record can reconstruct the accepted prefix [C]; truncating transfer and
record-driven reclamation each have witness histories of lost accepted work [C];
under any append-safe resumption the maximal store cut is the authoritative
accepted prefix, giving the asymmetric placement principle: resumption
authority is rebuildable from control evidence, resumption custody only from
the content plane [C]. The two studies share one failure clause (no gate may
open under a never-authorized tenure), which is exactly the clause Q1's
sufficient rules guarantee.

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
