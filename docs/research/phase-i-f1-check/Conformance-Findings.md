# F1 source conformance check

**Subject:** capacity competition and SQLite snapshot/witness/crash-cut probes in `docs/research/phase-i-f1`, pinned at `651a740bea2d1e25ed221ba541d8f7a9d0166913`.

## Finding

The fixed claims receive bounded, conditional support from the selected probes. The capacity check preserves its declared parent budget across serialized commits in its two-request fixture. The exact crash-cut comparator admits only the candidate whose epoch and digest match both declared authority and witness, and it denies all candidate images in the two mixed-store cuts. Missing witness and digest disagreement also fail closed.

The source set contains an older counterexample to the crash-recovery claim: `two_store_crash_cuts.py` admits an old candidate after only the authority store advances. Its admission rule accepts any candidate epoch less than or equal to authority so long as it matches the witness (`two_store_crash_cuts.py:66-68`). The newer `exact_authority_cuts.py` closes that tested gap by requiring exact epoch-and-digest agreement with each store (`exact_authority_cuts.py:25-27`).

That repair does not establish that the authority and witness are current. A bounded correlated-rollback test gave both stores the same valid epoch-0 record while the independent fixture current was epoch 1. The exact comparator then admitted the epoch-0 image because it matched both stores. Consequently, currentness and witness availability must be trusted outside the rollback domain, or recovery must fail closed when that premise is unavailable. SQLite integrity and pairwise equality do not supply this premise.

The result is a conditional conformance finding for these finite probes, not an all-C1–C13 conformance claim or a production SQLite durability result. In the canonical Work Unit target this primarily bears on C3's resource constraint and C7's current compatible recovery cut. Other obligations and realizations were not evaluated.

## Independent observations

- `capacity_competition.py` completed with exit 0, no truncation, and its 10,000-state limit untouched. The reference conflict case explored 136 states with no violation edge; the fitting case explored 121 states and reached both allocations and consumptions. Disabling commit-time recheck produced 18 over-reservation edges in 145 states. This supports commit-time serialization/revalidation for two participants and capacity 2; it says nothing about a concurrent allocator or persistent implementation.
- `snapshot_witness.py` completed with exit 0. The current snapshot with its matching digest was accepted; the old snapshot against the current digest and the current snapshot without a witness were denied. An intentional comparison bypass accepted the old snapshot, confirming the digest comparison is the discriminating guard.
- `two_store_crash_cuts.py` completed with exit 0 but its own record-first cut admitted the old epoch-0 image while authority was epoch 1. Its oracle marked that admitted image non-current.
- `exact_authority_cuts.py` completed with exit 0. Initial old state was admitted; both one-store-advanced crash cuts admitted no image; both completed updates admitted only the new image.
- The added paired-stale discriminator completed with exit 0: with both authority and witness coherent at old epoch 0 and the fixture's known current at epoch 1, the exact reader admitted old and denied new. This is the smallest unresolved discriminator for any unconditional “current authority” claim.
- The full `phase_i_f1_model.py` comparator did not finish within the declared independent cap of 40 seconds and 1 GiB virtual memory (exit 124; no result file). No full-model conclusion is drawn. A smaller diagnostic over the model's `capacity-one`, `currentness-image`, and `two-loss-currentness` contexts reached 8, 42, and 51 states respectively with no invariant violation returned; its global semantic-check helper reports checks for events absent from an individual context, so those helper results are retained as diagnostic raw output and not treated as pass/fail evidence.

## Trusted premises and limits

The capacity result assumes a single serialized decision point, commit-time budget recheck, the declared parent capacity and allocation/consumption accounting, and no state corruption. The SQLite experiments use same-host local files, SQLite transactions, SHA-256 digests, controlled process kills, and temporary directories. They do not test power loss, filesystem ordering, hardware corruption, concurrent writers, a multi-host protocol, or rollback resistance for authority/witness stores. The reader's “external fixture current” in the paired-stale test is an adversarial oracle to expose the missing guarantee, not a mechanism the implementation supplies.

The scripts were run as-is; no implementation source was changed. The paired-stale test used only disposable temporary SQLite files. `First-Verdict.md` preserves the source-only assessment recorded before results were read.

## Reproduction and raw evidence

Exact bounded commands, exit codes, limits, and preserved stdout/stderr are in [Run-Record.md](./Run-Record.md). Raw independent observations are in [`raw/`](./raw/). Source SHA-256 values are recorded in [First-Verdict.md](./First-Verdict.md).
