# Required-observation validation before content commitment

Frozen after9b1be41 before negative-input execution. Completed archive runs assume
trusted well-typed opaque observations. This is a new failure-boundary discriminator,
not a retroactive falsification of that premise or a provenance-authentication test.

Hypotheses: checking records only when querying after COMMIT is sufficient; or required
field shape/type and existing record compatibility must be established before accepting
new content/advertising a recovered consumer boundary. Cheapest tests use actual archive
holder: current valid zero/old evidence, then attempt new one with missing consumer_evidence
or non-string evidence. Predict baseline content/archive/latest writes COMMIT, then query
throws/no ACK and fresh holder may advertise ready but cannot answer; integrity remains ok.
Well-formed new one positive and same-content different evidence conflict control distinguish
unsupported route from malformed-data window. Conflict must leave prior accepted data intact
(no success ACK), with explicit ROLLBACK rather than a fabricated denial.

Only after documented failure: validate supplied field presence/types before startup and
validate existing current/archive record shape/content-key binding before ready. Do not
claim type checks establish provenance truth or source authority. Keep original well-typed
positive/history controls, source-root/currentness premise and selected stable opaque field
premise. No canonical schema change. Preserve original malformed committed database image
as bounded disposable fixture/digest; fixed recovery must refuse it before ready unchanged,
not repair/erase it. Separate baseline and fixed raw logs/source pins, no rewriting artifacts.

Four admission histories (valid,missing,type,conflict) plus retained-invalid-image recovery
control; one owned child at a time,256MiB, bounded Unix sockets/process waits. Fresh recovery
gets no original required tuple. Capture startup readiness/failure, actual RPC/no response,
SQL trace/local commit versus rollback, raw diagnostic SQL rows (without pretending malformed
rows are consumer evidence), exact executable/source/fixture hashes, process exit/stderr.
Missing metadata INCOMPLETE. These are deliberately invalid protocol/configuration controls,
not spontaneous failure or external targeting. SIGKILL/live-host SQLite APIs are not power
loss. Generic C9/C11/F1 acceptance, hostile credentials, independent truth/nonrollback,
concurrent writer, arbitrary schemas and liveness remain unproved. Next discriminator is
selected from genuine remaining obligations after these guards, not expanding field tests.
