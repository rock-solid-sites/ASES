# Fresh-session thin client

Continuation of the same ASES-4 priority D vertical integration. The current
native gateway has no executable thin client; its integration tests construct
raw Unix requests. Add `resource-session`, a small Rust binary using the same
existing dependencies and OS peer authority, with no new durable state owner.

Interface: `resource-session SOCKET resume JOB LAUNCH`, or explicit
`launch JOB LAUNCH EXPECTED_CATALOG`, `poll JOB LAUNCH`,
`stop JOB LAUNCH STOP_ID`, `finalize JOB LAUNCH OUTCOME` after the socket argument.
Use literal argument parsing, no shell, executable/PID/environment controls,
identity claims, DB access or supplied observations. The client constructs
exact existing local_* requests; it cannot grant authority. Every invocation
is fresh. In particular, resume is read-only and never automatically dispatches,
stops or finalizes based on advisory state.

Transport: absolute Unix socket path, bounded connect/read/write where Linux
stdlib permits, <=8KiB response, finite read/write timeouts, request then write
shutdown (gateway reads to EOF). Successful structured replies go to stdout.
An interrupted transport or malformed/truncated reply must emit a bounded
machine-readable `outcome_unknown` diagnostic, return nonzero and never retry
an effect automatically. A server-declared refusal remains a distinct refusal.
Invalid CLI input is rejected before any connection. Do not imply a failed
request had no effect merely because the response was lost.

Test the actual binary against the actual optional gateway/fixed native worker:
fresh launch -> fresh resume (no second worker), explicit stop/observed exit ->
fresh finalize, and fresh cold resume preserving unknown without auto-dispatch.
Use a bounded local response-dropping test server only for client transport
semantics, clearly distinguished from native gateway histories. Its capture
must verify exactly one request, no automatic reconnect/retry, and an unknown
result on EOF. Role denial must remain an actual peer-policy decision.

Preserve the API and native evidence in #31. No provider support, new session
registry, scheduler, command delegation or production setup is introduced.
