# Selected local T18 revocation discriminator

Research implementation; provisional November2 experimental method, no canonical change.
Frozen before implementation/execution, from bacf8f7d85fd10674554f5b7ef6415fc770e7f4a.

Claim: a selected flat-unit local sink can reproduce the frozen prepared-only
T18 use-current ordering, with explicit create/grant/activate/revoke and a request
initiated only after the revoke acknowledgment was received. Competing hypotheses:
last-issued generation equality suffices; or equality must be conjoined with current
write eligibility/activation. Keep generation unchanged on revoke, increment on grant,
so the hypotheses actually differ. Cheapest test: actual loopback sink with one lock
covering management, authorization, journal append/fsync, and publication; deny a
post-revoke token still equal to last-issued generation. A single-comparison mutant
that ignores grant/activation must accept that same post-revoke request. Earlier
replacement-only and detached-check observations remain narrower and unchanged.

Implementation packet: standalone managed_sink.py imports the existing persistence
primitive. Replace its fixed durable-event tuple with a module constant retaining the
same three default names; only the managed module extends that set/mode. New durable
create/grant/activate/revoke/replace events publish memory only after persistence.
Fresh managed startup refuses any existing journal; managed replay is unimplemented.
Revoke clears grant/active; explicit grant allocates a new generation and activation
is separately required. Position replacement advances generation and holder, clears
active, and preserves already-committed exact obligations. No revocation cancellation
semantics for exact obligations are tested. No generic deduplication promise.

Controls: actual create without grant denies; grant without activate denies; activated
current request succeeds; revoke-ACK then send denies with no x effect; regrant without
activate denies; activate fresh token succeeds and old token denies. Equality-only
mutant runs legitimate bootstrap/positive/revoke/send, avoiding unrelated earlier
negative controls. Separate exact-obligation fixture: explicitly commit x under
old/p/gen1 before replacement, advance to new/gen2, then deliver x successfully;
ordinary current-use before fresh activation denies. Existing-journal startup refuses.
Read-only checker compares calls, ordering, raw journal and effect observations;
missing metadata is INCOMPLETE; unsafe acceptance violates the frozen expectation.
Keep fixture bytes/status unchanged (f2lib still lacks this managed sink profile).

Bounds/capabilities: Python3 loopback, disposable temporary journals, one owned child
at a time, <=256MiB address space, bounded HTTP/startup timeouts. Retain exact source,
fixture, executable hashes, base revision, raw request/reply and monotonic timestamps,
status/effects, journal bytes/digest, PID/reap result; reproduction command and manifest.
Positive result supports only selected concrete correspondence under trusted management,
correct current journal/root, flat C/p, serialized sink lock. Management is a test
supervisor capability, not demonstrated credential authentication/revocation or native
F3 confinement. Append/fsync-return is not actual power-loss proof. No durable managed
recovery, general F2/F4 completion, nonrollback witness, hierarchy or universal proof.

Next discriminator: reconstruct managed eligibility/revocation before readiness from
retained journal, refusing incomplete/invalid transitions; or a real independent
manager-to-sink authority channel, depending on observed failures/cost.
