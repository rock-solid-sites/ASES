# Selected T18 managed revocation observations

Executed at source c917ba87a3a0fb73963b18f3ef6c75379f927e46 in authorized
Cloud disposable loopback processes. Reproduce:

```
python3 research/phase-i-t18-sink-order-20261103/managed-revocation/probe.py > /tmp/managed-t18.json
python3 research/phase-i-t18-sink-order-20261103/managed-revocation/check.py /tmp/managed-t18.json
```

WHY: replacement-only tests lacked the frozen use-current fixture's distinct grant,
activation and revocation. WHAT: actual HTTP management/use, after-reply caller
invocation timestamps, sink-lock event sequence, raw persisted JSONL, effects and
ACKs, source/executable/fixture hashes. Certainty: bounded executed evidence, with
coordinator-authored read-only checker; no independent review yet.

Reference: create/no-grant409, grant/no-activate409, activate/current201; revoke200
fully received before post-revoke send; old token1 still equals lastissued1 but
gets409 and no payload-x acceptance in either journal or effects. Regrant allocates2,
inactive2 denies, explicit activate2/current2 succeeds, old1 denies. Equality-only
mutation bootstraps/accepts current normally, then returns201 and retains x after
revoke despite grant=false/active=false. Thus equality alone is falsified in this
selected profile. This is a new mutation, not a recharacterization of the original
detached-check mutant; its post-replacement nondiscrimination remains recorded.

Separate exact-obligation: explicitly committed m/x under p/C/old/gen1 before the
frozen event sequence. Replaced p holder old->new/gen2 and then actually sent delivery;
x is accepted under the retained exact obligation. Ordinary current-use2 before fresh
activation is denied. No inference about obligation cancellation by revocation.

All three serving children killed/reaped; all three actual restart attempts refuse
existing journal before ready, unchanged bytes. Restart PID was not captured; its
synchronous subprocess completion, return code, stderr and interval are retained.
This is explicit missing identity metadata, not absence of a restart. Managed replay
is not implemented. Persistence hook preserves original three default event names;
original post-replacement reference/mutation regression remains201/200/409/201 vs
201/200/201/201. No original fixture bytes/status modified. The original f2lib fixture
is still prepared-only; this is a selected standalone concrete local realization,
not execution by f2lib or aggregate F2/F4 acceptance.

WHAT NOT TESTED: native host enforcement, genuine credential revocation, authenticated
manager source, independent nonrollback witness, hierarchy/ancestor state, managed
cold recovery, concurrent managers, exactly-once delivery, fsync failure in this new
profile or actual power loss. Flat C/p and trusted manager/root/journal are premises;
exp=true is a frozen fixture precondition, not a separately tested expansion law.
Raw status is diagnostic evidence under that trusted premise. Finite tests are not
universal proof. Checker missing-reply/journal controls return INCOMPLETE, distinct
from the mutation's VIOLATION. No product defect claimed in pre-existing source from
this intentionally weakened managed-eligibility mutation.

Next cheapest discriminator: managed eligibility replay before readiness, particularly
ACKed revoke followed by process death; then old token must remain denied and new
grant/activation must be explicit. Also freeze whether exact obligations survive
revoke before testing that distinct contract; do not infer it from replacement.
