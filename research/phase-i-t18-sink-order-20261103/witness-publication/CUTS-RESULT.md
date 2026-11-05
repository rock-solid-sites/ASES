# No reply does not identify the committed control outcome

Executed source0963679 (full SHA in cuts.raw.json). Reproduce
`python3 research/phase-i-t18-sink-order-20261103/witness-publication/cuts_probe.py > /tmp/publication-cuts.json`, then
`python3 research/phase-i-t18-sink-order-20261103/witness-publication/check_cuts.py /tmp/publication-cuts.json`.

WHY: governing C12 says lost reply preserves uncertainty about a definite outcome;
previous publication controls returned503, rather than actually losing the reply.
WHAT: actual held HTTP request, retained stage/PID/source-hash/monotonic gate, actual
SIGKILL/reap, live witness outside sink process, original surviving journal, fresh
recovery and next use/second restart. Certainty: executed finite cases and read-only
coordinator checker; no independent cut review.

All3 actual callers got no response (raw transport error retained), but outcomes differ:

| Actual cut | Local revoke | Witness revoke | Current-journal recovery/use |
|---|---|---|---|
| before local mutation | absent | absent | old/current1 succeeds201 |
| after local commit before publish | durable/observed | absent | revoked, old1 denies409 |
| after validated witness publish before reply | durable/observed | published | revoked, old1 denies409 |

Gate source/hash and raw witness/journal observations distinguish these outcomes.
No gate/oracle information is supplied to recovery; path/mode only. No fixture bytes
are restored into these histories. Prior ACKed content survives all3, and actual
post-cut positive before-local request survives second restart. Uninterrupted control
returns200 after validated witness publication.14 actual distinct owned children,
maximum2, all reaped; missing gate/reply controls INCOMPLETE. No-response is the common
success-ACK observation category, not proof all transport failures are interchangeable.

Interpretation: caller's missing success reply cannot establish neither side changed,
nor authorize an automatic retry as if no control operation committed. Local and
external outcomes remain definite for this instrumented observer, while caller starts
uncertain. Current-journal replay reconstructs eligibility, without claiming operation
identity/provenance not present in this bounded protocol. C11 requires different
identity/provenance/project/consumer observations; do not relabel C12 state recovery as
C11 closure. Locally committed/unpublished state remains a distinct reconciliation
problem if continuity of external exclusion is required; startup deliberately does not
publish possibly rolled local state.

WHAT NOT TESTED: power failure/storage durability beyond returned APIs, independent
root/currentness/source trust, witness process/host recovery, hostile manager, concurrent
management/global atomicity, distributed retry identifiers or completion/liveness for
unfinished operation. No F1-F5/PhaseI acceptance. Process termination differs from actual
power loss. Earlier publication/parent manifests remain tied to historical source pins;
CUTS-SHA256SUMS binds this instrumented revision and new evidence.

Next high-value choice: actual consumer-required provenance/evidence retention in an
existing physical SQLite holder, distinguishing atomic accepted-content retention from
separate-commit metadata loss; preserve trusted-acceptance premise and no schema mandate.
A remote-only cold index restoration is justified after these new branches/evidence.
