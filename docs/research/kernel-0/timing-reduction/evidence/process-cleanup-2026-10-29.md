# Process cleanup record (2026-10-29)

Operator observed duplicate unbounded runs of `timing_event_model.py`
(PID 90722 at ~6 min, PID 94571 at ~1 min) and asked for the stale duplicate to
be stopped, and later specifically for PID 94571.

Observed state when checked (in this sandbox's PID namespace):

- `ps -p 94571` -> no such process; `/proc/94571` absent; `kill -0 94571` -> ESRCH.
- No `timing_event_model.py` process was present; `ps | grep python3` empty.

The earlier exec sessions that would have hosted those runs were aborted by the
harness (`<turn_aborted>`), which terminates the sandboxed command tree; the
processes were therefore already gone. No `kill` was issued against any PID other
than the `kill -0` liveness probe on 94571, and no later run was aborted for this
reason.

Subsequent runs use a single bounded invocation:
`timeout 2400 python3 -u timing_event_model.py --deadline 1500 --output
evidence/correspondence.json`, i.e. a deterministic traversal order with a
wall-clock bound per profile, logging progress every 2^18 state words to
`evidence/correspondence-run.log`.
