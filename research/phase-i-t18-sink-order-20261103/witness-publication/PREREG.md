# Revocation ACK and witness publication boundary

Frozen from7ee4837 before implementation/execution; isolated experimental extension.
The full eligibility witness result requires supervisor publication before tested sends.
Competing hypotheses: a live full-state witness is enough despite delayed updates;
or management ACK must be qualified by witness publication. Cheapest test: actual
revoke ACK, deliberately withhold external publication, kill/reap sink, restore genuine
earlier ACKed active journal, restart and send after revoke ACK. Predict full-state
witness returns a fresh but stale eligible reply and actual sink201/x. A later actual
publication of retained revoked state should deny further use.

Candidate repair only for selected revoke path: after local durable revoke/state
publication, synchronously publish its exact eligibility tuple to the trusted witness
while sink lock remains held. Return revoke success only after nonce/root/exact-state
publication reply is validated. No automatic startup publication from possibly rolled
local state. Other management transitions remain under explicit supervisor setup, not
a claim of a general distributed control protocol. Source endpoint authentication and
nonrollback/truth of witness publication are trusted premises.

Controls: initial active/current201, witness publication succeeds before revoke200,
actual older-prefix restart then token1 denied. For rejected publication before state
update, wrong-nonce reply after actual witness update, and actual witness process death,
return503 with explicit local_control_committed=true and no success revoke ACK, while
local durable state remains revoked. These are different observations: local commit,
external state publication and usable ACK. No rollback of a committed local revoke to
hide failure. Missing publication metadata and missing local durable evidence must be
INCOMPLETE. Preserve partial-commit/availability limitations; no general liveness fix.

Retain raw requests/replies/process intervals/source hashes/journal/effects and exact
witness transcripts. <=2 owned children at once,256MiB inherited per process, bounded
HTTP/startup. Actual caller after-ACK send precedence is required for success claim.
No physical power loss, native enforcement, independent source-authentication proof,
canonical schema/policy change, arbitrary-corruption repair, concurrent manager/global
linearization guarantee, complete F1/F4 or exactly-once claim. A failed publication
means caller sees failure/unknown even if local state or witness committed; do not
classify it as neither side changed. Next discriminator: process death between local
commit and witness publication, and explicit recovery requirements for unfinished
management operations (do not auto-publish rolled local state).
