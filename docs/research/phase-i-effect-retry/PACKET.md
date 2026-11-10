# F4 durable request identity — bounded repair candidate

Frozen 2026-11-10 after fresh #10 Cloud replay. Original receipt extension pin
`9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9`, parent PR #11 `1970abe2`.
Comparator: Phase-I-Closure §4/H10, C1/C7/C10/C12 and Verification T17/T19/F4
at `29ec3960`. Original weak profile allows duplicates; this opt-in experiment
adds a stronger **at-most-once local F4 acceptance per request ID** contract.
It is not a production migration or an exactly-once external delivery claim.

## Behavior and reduced mechanism

Reuse the real receipt-extended cut sink, managed replay, writer lock, journal
append+fsync, witness CAS, receipt suppression, HTTP and cold recovery. Add an
isolated subclass; do not modify original sources. Disposable Python integration
reuses the existing tested implementation instead of rewriting its storage and
protocol. New boundary decoding and discriminating crash/fault tests compensate
for this bounded reuse; no maintained authority service is delivered.

Key scope: fixed witness root + flat C/p + exact nonempty string request_id.
Payload identity is exact UTF-8 bytes, not a caller-supplied hash or semantic JSON
equivalence. Persist identity in the existing `effect_accepted` journal event,
not an in-memory-only cache or second store. Replay derives the index from the
validated journal. Reject a preexisting duplicate-ID journal rather than silently
choosing one event. New intentional effects need a new ID even with equal bytes.

On `/submit`, while the inherited sink lock holds:

1. Existing ID, different exact payload: conflict, zero new append/publication.
2. Existing ID, identical payload: this is an outcome observation, not new use.
   If the live witness freshly verifies the entire current local cut, return
   HTTP 200 `already-accepted` with original sequence/accepted authority version
   and current verified journal hash/revision. No effect append and no republish.
   Current authority may have changed since original acceptance; do not relabel
   the old effect as a newly authorized one. The local trusted management boundary
   may observe retained results; a production information-access policy is absent.
3. New ID: use original current flat authority and real append/publication path.
4. Publication committed but receipt lost: return original uncertainty; after
   same-process retry or cold recovery, a fresh exact cut check may resolve the
   receipt without another append. Do not infer no effect from a 503.
5. Local append committed but remote cut remains old/rejects: no new acceptance,
   no blind retry, no successful cold readiness. Preserve local event as committed
   and remote status as unresolved/rejected. This candidate does not reconcile
   divergent stores by guessing or roll back local effects.

No automatic retry queue, epoch database, witness durability, witness rollback
detection, or publisher authentication is added. Root/current journal custody,
single writer, honest live witness and current storage remain trusted premises.
An in-memory witness restart must cause sealed/refused recovery, not reset genesis.

State distinction is PRIMARY: absent → locally committed → remotely published →
reply known; pending publication is not denied, and a duplicate observation is not
a second acceptance. Crashes before append leave absent; after fsync retain local
identity. Partial/torn append remains a native recovery failure, not success.

## Required discriminators

Fresh baseline: lost real witness reply causes 503 then same-ID retry duplicates.
Candidate: same-process and cold same-ID retry after receipt loss has one effect;
conflicting-payload retry has zero new bytes; new ID succeeds; current invalid
token for a new ID denies; previously accepted result remains observable after
native revoke. Remote rejection differs from lost receipt and blocks further
append/recovery. Kill before append and after append before publication, actual
kill after publication before caller reply if instrumentable. Restart witness
with no retained state: cold sink refuses. Existing duplicate-ID original journal
is rejected. Include valid neighboring fresh work after safe recovery, and retain
raw local bytes, witness exchanges, frames and source hashes.

Completion: establish bounded behavior or exact blocker, document the remaining
custody/freshness assumptions and preservation of committed local effects; move
on to Priority 4. No independent review/CI/backup or production adoption.
