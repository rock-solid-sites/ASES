# Live witness in actual managed sink path

Research extension frozen before implementation/execution, from aefdd5ece043190a76e8f14434aca9e9ec156038.
Prior F1 witness96e3e62 was admission-only; managed replay retained revoke but accepted
an older authentic prefix under the trusted-current-journal limit. New discriminator:
does a genuinely live witness suffice if its projection remembers only last-issued
generation? Competing hypotheses: live generation equality distinguishes rollback;
or revocation/eligibility changes without generation advance require more information.

Cheapest actual test: separate live loopback witness process survives sink process
death and journal rollback. Trusted supervisor bootstraps C/p, publishes eligible
state to witness, actual sink guard queries witness with fresh nonce under sink lock
before durable ordinary use, positive request ACKs. Revoke ACK then publish revoked
state (same issued generation1) to witness; observe witness update ACK BEFORE sink
kill/old-prefix restoration and post-restart request initiation. Run separate guarded
profiles generation-only and eligibility tuple(created/granted/active/gen/holder).
Both have actual witness query/reply in sink acceptance path. Predict generation-only
allows token1/x with real journal/effect/201 despite live witness knowing revoke;
eligibility tuple denies/no x. This is a projection discriminator, not a canonical
minimal schema or general full-currentness proof.

Controls: activated/current positive before revoke; fresh current recovery matching
witness denies token1 because local grant/active false; stale local recovery is actual
authentic older bytes, not a fabricated authority state. Wrong reply nonce and missing
witness deny actual otherwise-eligible sink use/no new accepted effect; record as
protocol controls, not spontaneous network faults. Keep root tag binding explicit.
No claims about hostile manager calls. Trusted supervisor synchronizes publication
AFTER local control ACK and BEFORE tested sends; no atomic distributed management
commit is implemented. No concurrency/global linearization guarantee from this path.

Bounds: disposable journals and loopback sockets, <=2 owned children at a time
(witness+sink), 256MiB address space per inherited process, finite HTTP/startup timeouts.
Witness resides outside the rolled file set, its actual PID stays alive, nonce and
update/check transcript/current-state are retained. Capture serving/restart process
boundaries, exact source/executable/base hashes, journal snapshots, requests/replies,
monotonic ordering. Reuse managed persistence/replay unchanged; wrapper guards ordinary
submit/commit only, exact-obligation delivery remains a distinct contract not tested.

Evidence categories: executed observations versus deliberate weak projection controls,
source-reviewed assumptions and missing metadata. No native host/source authentication,
real credential revocation, independent nonrollback trust establishment, physical power
loss, generic F1/F4 closure or infinite proof. Keeping witness state live/nonrolled and
publishing correct state are external premises. The witness may be untrusted by a
hostile local caller; this experiment explicitly assumes trusted management/endpoint.
Next discriminator: manager-to-witness publication failure/ordering, then the frozen
contract for authority changes overlapping a witness-approved in-flight request.
