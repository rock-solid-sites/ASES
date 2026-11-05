# Current authority can coexist with stale accepted history

Execution99c2551 (full SHA raw.json). Reproduce
`python3 research/phase-i-t18-sink-order-20261103/authority-cut/probe.py > /tmp/authority-cut.json`, then
`python3 research/phase-i-t18-sink-order-20261103/authority-cut/check.py /tmp/authority-cut.json`.

WHY: current-authority truth and whole accepted-cut currentness are different C7/C10/C12
propositions. WHAT: real management ACK prefix, actual x201/q-commit201, two authority-only
publications (second after those ACKs), live witness process, proper current-journal
recovery, authentic older-prefix restoration, new nonce-bound use/y201, actual q409 and
final strict recovery. Certainty: executed bounded counterexample/coordinator checker,
no independent review of this history. Five actual owned children/max2, all reaped.

Positive current journal reconstructs x and pending q before ready. Authority stayed
created/granted/active/gen1/old throughout; witness PID survives every sink restart and
controlled rollback. Publisher sends only five authority fields, not x/q, expected
journal digest or observer oracle. After restoring actual earlier management-only prefix,
new recovery has that genuinely current authority but no x/q. Actual new y gets201 under
fresh matching nonce/publication2/allowed witness reply; durable seq4 is reused for y
where original x had seq4. q delivery409; final valid strict journal contains y/no x/no q.
Raw ACKed x/q bytes and expected values stay in observer artifacts, never supplied to
runtime as a recovery repair. Missing prior-ACK/live-exchange controlsINCOMPLETE.

Interpretation: live correct eligibility witness can justify authority while failing to
certify accepted contents/outstanding obligations. Additional whole-cut binding or a
trusted-current-journal/nonrollback premise is required for that different proposition.
This does not show the authority-only witness false under its original scope. Deliberate
file rollback is outside earlier process-loss/current-journal profile, not spontaneous
storage failure or physical power loss. No minimal schema, source-authentication proof,
independent witness nonrollback establishment, hostile confinement or generic C7/F4/F1
closure. The fixed source never claimed accepted-history matching from authority fields.

Next high-value discriminator: selected published-cut witness binds actual journal
commitments, and every success ACK follows both local persistence and validated external
publication. Recovery must refuse mismatching cut before ready without auto-publishing
possibly stale state. Publication failure must preserve local unknown/unACKed commitment
rather than silently restoring old bytes. This would be a new explicitly conditional
profile, not universal atomicity or a mandatory schema.
