# F1 bounded conformance check — first verdict

**Recorded before execution and synthesis.** Source commit: `651a740bea2d1e25ed221ba541d8f7a9d0166913`.

## Verdict

The capacity probe appears to support only the narrow serialized two-request fixture: commit-time rechecking enforces the total capacity, allocation is a view of reservation, and consumption cannot exceed that allocation. It does not establish that a concurrent or persistent allocator preserves parent budget beyond this model.

The SQLite probes give conditional evidence that missing or disagreeing witness/current-authority data fail closed. `exact_authority_cuts.py` requires the candidate image's epoch and digest to equal both the authority record and witness, so the mixed one-record-advanced cuts appear to deny admission. The older `two_store_crash_cuts.py` does not meet that exact predicate: it accepts an image when its epoch is no newer than authority and it matches the witness. A record-first cut can therefore admit the old image even though its epoch/digest disagree with current authority. The exact-agreement probe appears to repair this specific discriminator.

The largest unresolved premise is freshness of the authority and witness themselves. If both can be rolled back or coherently replaced with a stale matching pair, equality and SQLite integrity alone cannot establish that either is current. The scripts appear to assume a trusted supervisor-held or otherwise current authority source; they do not demonstrate such a source against rollback.

## Scope of this verdict

The source appears consistent with the bounded Work Unit/C1–C13 target only under serialized transitions, fixed fixture identities and capacities, SQLite's local transaction/integrity behavior, and a trusted currentness witness. It does not establish general allocator behavior, authority-store rollback resistance, multi-host crash semantics, atomic cross-store commits, filesystem durability, or production conformance. This is a source-level initial verdict pending independent execution and falsification.

## Source digests

SHA-256:

- `phase_i_f1_model.py`: `b0240c9aa1326f9a41d76e0ffe457bc3828b513b921f3c83ca41965958e07518`
- `capacity_competition.py`: `68cc4f7f7d39d4caf559c34f5dccb2b6834714c2ff5cfd5a1e3c49dd6bad5092`
- `snapshot_witness.py`: `6c406dbaa1c585a4c47a46fe0c138fc02b33bafd740cf005ebb3c19a7034d72c`
- `exact_authority_cuts.py`: `eac2811c2268f696b1dd57d18e300b0ae17ccd9fd044c19e77e10142d0a545e3`
- `two_store_crash_cuts.py`: `b5861948fe185fb4c99230122817968a019d14020e769310c498d79e61a6ca14`
