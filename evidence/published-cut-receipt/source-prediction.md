# Source prediction — published-cut receipt loss

Recorded before execution evidence was opened. Reviewed source: `published-cut/cut_sink.py`, its paired probe/check and implementation packet, plus the receipt-loss probe/check/packet.

## Competing outcomes

1. **Receipt lost after successful compare-and-swap:** the witness first advances revision and current cut, then closes the connection without delivering the response. The sink records a transport exception, has already durably committed `receipt-z`, and returns 503 with `local_control_committed=true`. A later operation performs a new `/check` against the actual current local cut, can proceed, and same-file recovery followed by a second cold recovery retains the earlier acknowledged effect, z, and later accepted effects.
2. **Publication rejected before update:** the witness replies 503 with `published=false`, keeping its prior revision/current cut. The sink returns 503 with z locally committed. Later request does not append, and cold startup refuses the divergent local journal without discarding z or changing witness state.
3. **Ordinary positive control:** publication reply is delivered and validated, z returns 201, and later check/recovery succeed.

## Evidence needed to distinguish these

Correlate the exact sink `/publish` request/nonce with the witness log entry, actual status/current/revision, and whether the reply was suppressed. Separately verify sink transport result and caller response; local journal bytes/hash and event sequence; prior ACK persistence; a later fresh nonce `/check`; actual restart and second cold recovery; witness process identity/liveness; and child process start/exit ordering.

## Possible harness traps

- A missing sink response alone cannot distinguish a successful remote update with a lost reply from rejection or no update.
- Witness logs/status must be from the same live process and tied to the exact request; a configured fault is not proof the intended branch occurred.
- A caller 503 may conceal a durable local effect, so event bytes and `local_control_committed` must be checked directly.
- Same-process retry can fail to test recovery; require real process closure/restart, ready evidence, and a second cold instance.
- A later success is meaningful only if a fresh check occurs after z and uses the actual journal digest.
- Missing or uncorrelated evidence is incomplete; contradictory identity, revision, bytes, or ordering is a violation.

This prediction is scoped to the selected trusted live witness/current-root experiment. It does not predict witness durability across its own failure, hostile rollback resistance, generic distributed atomicity, or universal C7/F4 behavior.
