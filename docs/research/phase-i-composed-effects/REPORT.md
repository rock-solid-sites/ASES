---
title: Current effect admission composed with durable retry observations
program: EDASES
layer: Research
document_type: Investigation
status: Experimental
authority: Derived
last_updated: 2026-11-10
---

# Result

The two isolated candidates compose within their declared test-only,
participating-writer profile after one concrete integration correction. New
effects still pass the F1/L5/L6 append guard. An identical request already
accepted locally can be observed without appending again, even after source
disposition or flat F4 revoke, when a fresh exact witness-cut check supports that
historical observation. This confers no permission for a new request ID.

Six native histories pass the independent raw checker, and three altered
controls reject. The original negative control is retained: the retry-only sink
accepts the exact source-denied payload under its flat contract, while the
composed port refuses it without appending. Deduplication is not source authority.

## Minimal composition

`composed_sink.py` installs retry's replay-derived `RetryState` inside admission's
managed-state wrapper. A historical observation returns without invoking append.
New use reaches the original managed authorization and the guarded
`emit_locked(effect_accepted)` hook. Original journal fsync, native witness CAS,
reply suppression, native source transitions and cold replay are executed.
The adapter adds no new durable identity table or authorization store.

## Integration failure and correction

Initial `run-03` exposed a real composition gap. After one local append followed
by witness rejection, the outer cut check intercepted an exact retry before
retry state saw its retained ID. The reply was generic 503
`published-cut-unavailable`, `local_control_committed=false`, without the original
sequence. A known conflicting payload was intercepted in the same way.

The added outer outcome wrapper uses the already validated local identity
index. A known payload conflict returns 409 with the original sequence and
`new_local_effect=false` before a witness exchange. An exact retry whose cut
cannot currently be verified returns 503 `retry-observation-unresolved`, original
`local_event_seq`, `local_control_committed=true`, and `new_local_effect=false`.
It neither appends nor claims remote success. Native cold recovery still refuses
the divergent cut. The initial trace remains unchanged; `run-05` demonstrates
the corrected return boundary with exact journal and witness-log comparisons.

## Observed histories

| History | Observation |
| --- | --- |
| Healthy current new effect | 201, one admitted/certified effect, exact journal published |
| Native moved/attenuated source | Composed 409/no append; retry-only comparator 201 for the identical payload |
| Real witness reply loss, then native L6 disposal/removal | First 503 with one actually published effect; same-ID observation 200/no bytes; conflicting payload 409; new ID 409 at current lifecycle guard |
| Cold sink restart after that loss/removal | Same journal inode and retained effect; identical retry 200/no duplicate |
| Native flat revoke after acceptance | Historical result observation 200, original sequence; new ID denies, no bytes |
| Explicit remote rejection | One local effect retained; exact retry unresolved with original sequence; conflict 409 without new witness calls; cold mismatch refuses |
| Actual kill after append before publication | One local effect/no reply, witness old; cold mismatch refuses |

The latter two interruption cases are recorded as separate branches of the
six-history fixture set. Outcome knowledge, new acceptance and original accepted
history remain distinct throughout.

## Reproduction and claims

Run `bash docs/research/phase-i-composed-effects/reproduce.sh <new-dir>`. Final
raw process/HTTP/source/journal evidence and evaluation: `evidence/run-05`.
The deciding source-denied, source-removed, revoked and receipt-loss transitions
are native operations, not values constructed by the checker. `check.py` imports
no adapter predicate. Three alterations—original receipt identity, duplicate
observation identity and source eligibility—are required to reject.

WHY: an accepted-effect lookup and a request for a new effect need different
guards; layering must preserve the original outcome through outer refusal.
WHAT: six finite native histories, 28 component processes, 66 recorded events,
fresh before/after native runs and altered controls. HOW CERTAIN: evidence-based
within this bounded cooperative composition. WHAT-NOT-TESTED:

- Native protected F1→F3 import or complete shared lifecycle identity; mappings
  remain test-only and are never promoted by equal hashes/certificates.
- Exclusion of unguarded writers, root custody, source truth, witness durability,
  authentication/nonrollback, arbitrary schedules or physical power loss.
- Exactly-once external delivery, automatic divergent-cut reconciliation or
  cancellation at remote visibility.
- Production policy for reading historical effects after revoke. The selected
  trusted local management boundary may observe retained results; this is not
  a new grant to perform the original effect again.

Original component sources, frozen policy and parent research PRs are unchanged.
This is implementation integration/verification, not independent review or CI.
