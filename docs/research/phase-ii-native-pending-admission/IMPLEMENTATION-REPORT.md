---
title: Native pending-effect admission implementation report
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Implementation Report
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - PACKET.md
  - ../../astra-prelaunch-20261123/NATIVE-PENDING-ADMISSION-IMPLEMENTATION-PACKET.md
last_updated: 2026-11-24
---

# Native pending-effect admission implementation

## Scope and source

Implemented the compiled A1–A7 packet from PR #77 against PR #43's exact pinned source, `e91fb4b14875487dee9c19cc764e72655ba534c0`. The original baseline was not rerun. The existing `run-02` baseline report/raw capture was reused as specified. No seal-policy change was made.

The admission bound lives under the existing native owner lock and preserves the current F1 transaction, L5 lock and L6 transaction. `Session.reserve_effect` checks duplicate request identity first, then refuses a reservation if any effect is not `published`. `NativeAdmission.guard` makes the same check only for a new request ID, after the existing authority and retained-material checks and before marking the outcome uncertain. This keeps known denials out of the reconciliation-required path. Existing same-ID journal lookup/replay and supported reconciliation remain intact.

## A1–A7 results

| ID | Result | Evidence |
| --- | --- | --- |
| A1 | PASS — real `guarded` EOF retained exactly one eventless `reserved` A; journal and witness cut/revision stayed unchanged; response remained reconciliation-required. | `evidence/implementation/run-01/admission.json` |
| A2 | PASS — after A remained pending, fresh B was denied before reservation with an ordinary admission denial; owner effects/selection, F1, L6 tree, journal bytes and witness cut/revision were unchanged. | Same raw capture |
| A3 | PASS — repeated B and fresh C were also refused without growing effects or claiming uncertainty. | Same raw capture |
| A4 | PASS — clean sequential A then B each published under distinct IDs and journal events. | Same raw capture |
| A5 | PASS — actual fsync-before-owner-callback A was reconciled to `published` from journal/witness evidence; with current authority still eligible, fresh B published; exact A retry returned `already-accepted` without a duplicate append. The parent case separately moved the source, denied fresh B with `native-current-path-denied`, and retained historical A lookup. | `admission.json`; `parent-regression.json` (`fsync-gap`) |
| A6 | PASS — pending eventless reservation did not block existing `seal`; child disposal was denied with `pending-in-domain-effect`; strict reconcile and local observation refused the eventless A without changing its retained record or journal. | `admission.json` (`A1-A3` includes A6 assertions) |
| A7 | PASS — affected #35/#36 parent histories were rerun once. The publication-reconciliation parent returned `PASS`; local-observation histories passed, including a changed-payload control refused as `native-owner-local-effect-mismatch`. | `evidence/implementation/run-01/parent-regression.json` |

## Verification commands

- **Pinned-base red check:** detached test-only commit `6f1ca505d630f319695ca2d337e222a51e2f68ae`, whose parent/source was the pinned #43 head and had no implementation edits: `python docs/research/phase-ii-native-pending-admission/verify_probe.py /tmp/native-pending-baseline-red` → exit 1 at A2, because fresh B/C were not truthfully refused. Raw failure: `evidence/implementation/pinned-base-red/raw.json`.
- **Implemented green check:** `python docs/research/phase-ii-native-pending-admission/verify_probe.py /tmp/native-pending-verify-run-09` → exit 0 (`PASS`).
- **Parent recovery histories:** `python docs/research/phase-ii-native-local-observation/probe.py --out /tmp/native-pending-parent-regression` → exit 0 (`PASS`), including its #35 parent reconciliation regression and changed-evidence control.

The histories were committed before the implementation commit, but the test script was first authored after the source edit was already present in the working tree; the pinned-base red check was then run in a detached checkout containing only the test commit and base implementation. The red capture records base owner/sink hashes `f772e9054966646257faa3460cfda7833ede0e452043dbc7001158ffe54fa59d` and `f4262271ea008208b99f5339d3b1e42c8239753d0a823e65e725bf2097bea70d`. This is a verified base/final red-green result, not a claim of test-first authorship.

The implementation source hashes in both passing captures are:

- `native_owner.py`: `341a4f6239aa43ed57f6d9d3067d2e6e8b509b452a267ae716fe4edf47e25544`
- `native_sink.py`: `d96e125bf40c3ecf3750c05bf46742de60463cd28195511c58e49bb03d610717`

## Limits

An eventless reservation remains retained and can block fresh IDs indefinitely. This change adds no cancellation, timeout, automatic recovery, rollback, or release rule. Host/power failure, arbitrary publishers, hostile same-UID actors and universal confinement were not tested. The result applies to this experimental native profile and does not promote project-wide Kernel semantics.
