---
title: Independent F1 SQLite Bridge and Stale-Observation Review
program: EDASES
layer: Research
document_type: Adversarial Review
status: Evidence-based, bounded
---

# Independent F1 SQLite Bridge and Stale-Observation Review

**Review target:** `89db5e03380b9420d0e54c0e11e459fd079b3329`  
**Compared with:** `651a740be` (new F1 Python scripts only)  
**Review branch:** `review/autonomy-20261103-f1-bridge`  
**Scope:** selected capacity/emptiness/activity observation at a SQLite commit boundary; stale disposition and active reassignment. This review makes no F5, cross-family, universal C11-schema, crash-recovery, or all-ingress claim.

## Finding

The SQLite experiment is real subprocess evidence for one narrow admission pattern. With the reference path, each of two independent Python processes uses SQLite `BEGIN IMMEDIATE`, reads the shared capacity row count while holding the writer reservation, and couples the capacity reservation and an effect row in one commit. Exactly one effect commits; the other sees the current count and is denied. With the detached mutant, both processes read zero before acquiring the write lock, retain that stale observation, and then each commits. Two reservations and two effect rows result. The unsafe control therefore discriminates the reference behavior at the database commit boundary, with a positive committed row effect.

The result is conditional on the SQLite file and its commit function being the selected trusted acceptance boundary: every protected effect must pass through this transaction path, and other processes must not be able to write protected state around it. The schema has no constraint or permission mechanism that enforces capacity one. A process with direct write access can insert reservation/effect rows without calling the admission path. Thus the run supports “a protected effect routed through this guarded transaction does not commit from a superseded count observation” for this fixture; it does not show that the SQLite file itself closes every route or protects against arbitrary direct writers. The `effects` row is a synthetic owner marker, not a representative accepted content payload.

The stale-disposition and active-reassignment runs are model-only evidence. Both call the inherited `phase_i_f1_model.resolve` for abstract F1 events, while the newly added wrapper keeps relevant object or activity state in local Python values. In the disposition run, `owner` for the extra dependent `z` is not part of the F1 state; the independent violation observer detects `z-unbounded:S` after the stale mutant removes S. In the reassignment run, `active` is a Python set, and the wrapper directly replaces `capacity_reserved` to model reassignment. These cases successfully separate stale eligibility from current recheck and include positive accepted paths, but they do not exercise a SQLite or OS-level commit race. They cannot independently establish that a realized Work Unit removal/reassignment implementation binds those observations to its acceptance boundary.

## Execution evidence

The three target scripts were copied to `/tmp/f1-bridge-review/phase-i-f1` with their existing model dependency and run from that copy. Runtime was Python 3.12.14 and SQLite 3.53.1. All commands completed within their bounded timeouts and stderr was empty.

- `sqlite_capacity_competition.py`: reference had two distinct child PIDs, decisions `C=committed`, `S=denied(count=1)`, pre-ACK integrity `ok`, reservation/effect rows `[C]`, one ACK and child exit codes `[0,0]`. Detached mutant had two distinct child PIDs, both prechecks `0`, both committed, pre-ACK integrity `ok`, reservation/effect rows `[C,S]`, two ACKs and child exit codes `[0,0]`.
- `active_capacity_reassignment.py`: `hazard_reference` denied C consumption and ended without modeled violations; `hazard_stale_mutant` committed C consumption and ended with `active-use-exceeds-one-unit` and `active-use-without-current-reservation`. Completed and quiet references accepted C consumption without modeled violations.
- `stale_disposition_recovery.py`: `hazard_reference` denied removal while the wrapper linked z to S; `hazard_stale_mutant` committed removal and ended with `z-unbounded:S`. Empty removal and the transfer-to-Q-then-remove controls committed without modeled violations.

A separate bounded harness in `/tmp/f1-bridge-review/independent_bridge.py` repeated the two SQLite cases. Its orchestrator opened a separate read-only connection after child commits and before releasing ACK. It independently observed integrity `ok` and `[C]` rows in the reference, `[C,S]` rows in the detached mutant, then observed the expected ACK messages and zero child exit codes in both cases. This confirms the effect is visible in the store before ACK; it does not test power loss or crash durability.

## Source and artifact provenance

The first source-only verdict was written at `2026-11-03T20:08:50Z`, before reading target output, checkpoint, history, or review artifacts. It is preserved at `/tmp/f1-bridge-review/first-verdict.md` (SHA-256 `d20ec3a3e3229623e02fd0ab5767712d99de279b292a0ca838e0f418ef931eba`).

Target source SHA-256 values:

- `sqlite_capacity_competition.py`: `34e60b2c6a291fb1f2ec3cfdf2d9512fca931970cb7e78cab3d518fef42402df`
- `active_capacity_reassignment.py`: `cd2a4b57ea5454d85fce553990854c6c8a76f9d6858491b3d5c6ed1e489278ba`
- `stale_disposition_recovery.py`: `871b2f03f7ff2b470070523abac9d60250adaa3c7eb5cd5385bf3bf59dee4560`

Exact copies of the first verdict, bounded reproduction inputs, and raw run outputs are preserved in [the review evidence directory](review-evidence-2026-11-03/manifest.md). The original temporary copies remain under `/tmp/f1-bridge-review/` in this execution environment. The evidence manifest records hashes and notes that the top-level numeric shell exit code was not separately captured; child exits are in the raw stdout JSON.

- `sqlite-capacity-run.json` — SHA-256 `957c50e3db63288c18502ea41e95d8732f7f0c286ccebd00499bf3dcf1fe0cd7`; matching stderr file is empty.
- `active-reassignment-run.json` — SHA-256 `1b9cccf75952688b19d34705901c5df389a69b1681692c09604f981c93641679`; matching stderr file is empty.
- `stale-disposition-run.json` — SHA-256 `9fa5cf3858885247cefaf93b79bdea3dbd6b1379defb22ca143915d010fbbe78`; matching stderr file is empty.
- `independent-bridge.py` — SHA-256 `bf192c3733afac1b2d32f7ccc745a0c3ef99d29955b68f40b58b2d4b19e40bfa`.
- `independent-bridge.json` — SHA-256 `0ee67c1040b73e196c7c9a62989a93673525ae389d82c43b7120f766880e5c8a`; matching stderr file is empty.

The other new scripts, `consumer_observation_continuity.py` and `independent_observation_fields.py`, concern retained observation-field distinguishability. They were not run because those erasure controls do not discriminate the selected stale-bridge claim. No conclusion about a universal observation schema is made.

## Next smallest discriminator

Exercise the same competing-writer schedule through the intended trusted admission API with a representative accepted content value, while independently confirming that all write routes for that protected value pass through the API. If arbitrary local processes are in scope, the immediate next test is a direct SQLite writer attempting the same protected effect without admission; the current schema offers no barrier to that route, so the trust-boundary premise would fail. If only the single trusted holder is in scope, keep the route closed by design and test the protected effect at that holder's actual commit function.
