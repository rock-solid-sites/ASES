# Prefix recovery bounded verification

**Verdict:** The bounded source and execution evidence supports the claim within the stated premise: a trusted, correct and current journal has an append-only, new, unterminated unacknowledged tail; earlier complete records remain intact; no later durable success exists. Recovery validates the complete newline-terminated prefix, durably writes the original bytes to a hash-named quarantine, writes and syncs a prepared prefix, atomically replaces the journal, and only then emits server readiness. Strict `recover-ordered` rejects the partial journal. This evidence does not show that file shape establishes the premise.

The checked implementation was `research/phase-i-t18-sink-order-20261103/run.py` at source SHA-256 `a1185881e18b2611b373753ee0fabb8ecc68175f6948a950759a123c8fd027cb`. Its implementation order is visible in `SinkState.recover_prefix` and `recover_ordered`. The frozen Phase-I verification document separately says process-kill evidence does not establish power-loss durability and labels rollback-resistant successful recovery a stronger profile.

I ran the scoped prefix-recovery probe once from the pinned review worktree, with a 45-second timeout. It exited 0 in about 1.5 seconds, emitted 58,897 bytes of JSON, and wrote no stderr. It recorded successful normal, quarantined-gate-death, and published-gate-death histories. Both injected deaths exited -9 before readiness; retries restored the acknowledged `ack-before` record, preserved the quarantined original bytes by hash, accepted `post-prefix` with HTTP 201, and cold recovery retained both effects. The probe also refused each of seven controls without changing fixture files: a boolean version, duplicate sequence, later ACK behind malformed tail, no complete prefix, malformed complete record before tail, strict-mode partial journal, and mismatched quarantine.

The probe's outside-relation control is a useful boundary witness: the source fixture had three acknowledged effects, then its final record was truncated. Prefix recovery returned two effects. This is not a within-premise failure; it demonstrates why the recovery decision must be restricted to the stated fault premise and why shape alone cannot justify truncating acknowledged data.

An additional disposable retry check independently killed the server at each of the `quarantined` and `published` gates on a known one-record complete prefix plus an unterminated tail. In both cases the retry reached readiness and the journal equaled the valid prefix; the quarantined bytes matched the original. Its raw observations are in `gate-restart-check.json`.

**Evidence limits:** These are same-family operational checks of the pinned source, not formal cross-family review or F4 closure. They establish process-death recovery at the two instrumented gates. They do not establish machine/power-loss behavior, filesystem or device-cache durability, resistance to rollback or corrupted premises, or that any external caller can infer ACK history from bytes. Quarantine and prefix hashes aid verification but do not prove the fault premise. No execution failure occurred within the stated premise; the acknowledged-tail truncation result is explicitly outside it.

Artifacts:

- `primary-rerun.stdout.json` — full probe observations, including raw hex and exit statuses.
- `primary-rerun.stderr.txt` and `primary-rerun.meta.json` — stderr and run metadata/hashes.
- `gate-restart-check.json` — independent two-gate restart observations.
