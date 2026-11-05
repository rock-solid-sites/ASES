# Live generation equality is insufficient at actual sink acceptance

Executed source05de151 (full SHA in raw.json). Reproduce:

```
python3 research/phase-i-t18-sink-order-20261103/sink-witness/probe.py > /tmp/sink-witness.json
python3 research/phase-i-t18-sink-order-20261103/sink-witness/check.py /tmp/sink-witness.json
```

WHY: prior F1 external witness was admission-only; actual managed sink now queries it
under its local sink lock before journal append/fsync and ACK. WHAT: real independent
process remains alive outside journal rollback, published revoked state/update reply,
nonce-bound check request/reply inside actual submit, journal/effects/ACK and cold
replay; source/executable/transitive input hashes and process intervals. Certainty:
executed finite evidence with coordinator read-only checker, no independent review yet.

Generation-only profile: activated/current positive ACKs. Actual revoke ACK then actual
witness publication ACK precede sink death, retained-current replay denial, authentic
older-prefix rollback and post-restart request. Witness same PID still knows grant=false,
active=false/gen1, but presented stale eligible state also has gen1. Fresh nonce reply
allows it; actual sink appends x, returns201, and x survives cold replay. Thus genuine
liveness, nonce freshness and generation equality do not encode eligibility freshness.
This is a selected weak projection counterexample, not a defect in canonical policy.

Eligibility tuple profile under the same ordering: actual witness sees stale local
created/grant/active/gen/holder tuple differ, returns allowed=false; sink409/no x.
Existing current journal retains revoked eligibility and denies without needing a
witness query. Healthy initial/current positives pass. Separate otherwise-eligible
nonce-fault control returns allowed=true with wrong nonce but actual sink rejects409;
reset response restores201. Killing/reaping witness before another actual submit
causes409/no new effect, explicit request failure in sink log.12 actual owned distinct
children, maximum2 concurrent (witness+sink); all killed/reaped, intervals retained.
Two missing-publication/exchange controls INCOMPLETE, distinct from projection failure.

WHAT NOT TESTED: external source authentication, hostile local callers, physical power
loss, independent trust establishment/nonrollback of witness, generic F1/F4/PhaseI
closure, concurrent management, atomic distributed publication or minimality of tuple.
Witness and manager are trusted loopback roles. Parent intentionally publishes state
after local ACK and waits for witness update ACK before tested rollback/sends; that
synchronization is a premise, not supplied by the management mechanism. Missing-witness
control is deliberate process death, not spontaneous network failure. Full tuple
comparison is only sufficient for these frozen finite histories, not a proposed schema
or proof under other control laws. Exact-obligation path is intentionally distinct and
not covered by this ordinary-use guard experiment. Accepted-history rollback is not
solved by permission-state matching.

Next discriminator: withhold the witness update after actual revoke ACK, then restart
on older authentic journal. A live full-state witness may confidently accept stale use.
Test an explicit publish-before-management-ACK barrier and its failure response, while
preserving the gap between local durability, external publication and physical loss.
