# Executed missing-receipt discriminator

One primary execution at `38d529d` completed all three preregistered histories.
Reproduce with `python3 research/phase-i-t18-sink-order-20261103/published-cut/receipt-loss/probe.py > /tmp/receipt.json`
then `python3 research/phase-i-t18-sink-order-20261103/published-cut/receipt-loss/check.py /tmp/receipt.json`.

The witness performed a real successful CAS update, recorded the publication, then
closed the actual HTTP connection without sending the reply. Sink-side transport
evidence is `RemoteDisconnected`, no received/validated publication response. The
caller received503/`local_control_committed=true`, while the actual local bytes already
matched the live witness's newer cut. A later request used a fresh nonce/current-cut
check and succeeded. Actual same-file process recovery retained the previously ACKed,
unACKed z and later ACKed events; a new acceptance and second cold restart also passed.

The uninterrupted positive returned201 after validated publication. Actual rejection
before update returned503/local committed but left the witness on its older cut;
later append and startup were refused while preserving z. Thus the same caller status
and local commitment indication do not identify the actual remote outcome. Missing
success receipt is evidence of an unknown response outcome, not absent publication or
absent local effect. The wrapper's existing fresh comparison distinguishes these
selected states without a permanent failure latch or observer-supplied expected data.

All11 owned children were reaped, maximum overlap2. Full local/witness/caller/process
transcripts, source and executable hashes are retained. Both stderr files are empty.
Source hashes verified against the recorded execution commit. Removing the witness
observation yields INCOMPLETE; contradictory remote revision yields VIOLATION.

Executed bounded evidence, without separate independent reproduction at publication.
Conditional trusted genesis/source/root/cooperative writer/live nonrolled witness
premises remain. The witness was not restarted; memory persistence, actual power loss,
reconciliation of a genuinely older witness cut, maximal availability, C7/F4/F1 closure
and a general distributed acceptance proof remain open. A 503 with definite local
commit remains a partial outcome requiring explicit caller interpretation.
