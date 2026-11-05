# Reading retained evidence is not evidence for a new acceptance

Baseline d66b281, repair e27180b (full source pins/raw hashes retained). Reproduce
`python3 docs/research/phase-i-f1/c11-history/unavailable_input.py fixed > /tmp/unavailable.json`, then
`python3 docs/research/phase-i-f1/c11-history/check_unavailable_input.py /tmp/unavailable.json`.
Historical baseline uses the baseline source in an isolated checkout.

WHY: None is a legitimate recovery configuration because old tuples must not come from
an oracle; startup type checking cannot decide future new-acceptance input availability.
WHAT: actual valid pre-read/retained archive, original accept-one RPC, SQL trace/raw
rows, caller response and later startup, explicit-input positive, exact source/executable
hashes and process intervals. Certainty: bounded executed evidence/coordinator checker,
no independent review of this new guard.

Baseline: recovered holder has no observations config, actual read returns valid old
pair, then content-one COMMIT occurs without new tuple. Caller receives no usable
response; raw diagnostic sees new one with old zero metadata/archive. Next startup
correctly refuses the incompatible binding. Explicit tuple positive ACKs/recovery pass.
This is runtime missing input after valid recovery, beyond malformed-field examples.

Repair: proposal under original holder lock/SQLite transaction returns no candidate
when accepted content changes and new observations unavailable. Actual deny/ROLLBACK
before UPDATE/COMMIT preserves current state and old consumer tuple; valid read and
new explicit-input acceptance continue. Eight actual children/max1 per phase, all
reaped; missing pre-read observation INCOMPLETE, source hashes verified against actual
execution git objects. No automatic oracle tuple or metadata reconstruction supplied.

WHAT NOT TESTED: source authentication/truth, generic maximal availability, new wire
protocol for supplying observations, physical power loss, independent nonrollback,
concurrent writer, generic C9/C11/F1/PhaseI proof. Conservative guard also refuses
content changes to already archived bytes without input; no promise of maximal
availability or retry semantics. Data/management operations leaving accepted content
unchanged remain original policy operations. New accepted observations still require
trusted explicit input, not provenance inferred from retained contents or process PID.
Earlier archive/type-check results stay qualified; parent/canonical/main unchanged.

Next: a materially different physical resource-claim discriminator, such as native
resource occupancy surviving bookkeeping release or descriptor transfer; keep SQL
conservation, active use and actual resource availability distinct. No extra routine
field examples or blind full-model budget doubling.
