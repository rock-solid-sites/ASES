# Executed published-cut profile

Executed source `25c3721df2b258dc2d0b6ea22ffcd6e870339255` once. Reproduce:

```sh
python3 research/phase-i-t18-sink-order-20261103/published-cut/probe.py > /tmp/published-cut.json
python3 research/phase-i-t18-sink-order-20261103/published-cut/check.py /tmp/published-cut.json
```

The four preregistered histories completed; checker output is `check.json`. All 13
owned children were reaped, at most two overlapped. `raw.json` retains full caller,
startup, local bytes, witness protocol and process evidence, source hashes, execution
revision, Python executable identity and environment. Both stderr files are empty.
The checker verifies recorded source hashes against that execution revision. Missing
success-response and startup-refusal controls are INCOMPLETE, not passes or defects.

* Positive: actual create/grant/activate, x acceptance and q commitment succeeded only
  after local persistence and validated exact-byte cut publication. Proper current-file
  recovery retained x/q; new y succeeded and a second restart retained x/y/q. A stale
  compare-and-swap publisher received 409 without changing the witness.
* Authentic earlier management-only prefix: the unchanged strict parser accepted the
  local file and its authority matched the live witness, but the published-cut wrapper
  refused before READY because the journal digest differed. It changed neither file
  nor witness. This discriminates the prior authority-only acceptance counterexample.
* Coherent mutation: changing x payload plus its self-hash while preserving authority,
  record count, sequence values and byte length passed the original strict parser but
  failed the published-cut startup check. This is a synthetic mutation control.
* Publication rejection: z was locally committed, then the witness rejected publication.
  The caller received 503 with `local_control_committed=true`; the next request received
  503 without another append. Cold startup refused the divergent file and retained z.
  No record was dropped or automatically published to manufacture agreement.

This is executed bounded evidence, without a separate independent reproduction. The
witness denotes its last published cut, not complete knowledge of an unreported local
event. Successful API/byte/publication-response ordering is observed; per-syscall fsync
timestamps are inherited source assumptions. Process termination is not power loss.
Trusted genesis, publisher/source/root custody, a witness that survives the selected
file fault, and cooperative serialized writers with a stable lock inode are premises.
No hostile-publisher confinement, witness nonrollback establishment, minimal schema,
generic C7/F4/F1 completion or two-store atomicity is established. Exact byte binding
may reject semantically equivalent encodings.

Next discriminator: distinguish publication rejected before witness update from an
actual successful witness update whose response is lost. A missing receipt must not
be mistaken for evidence that publication did not occur; inspect real current-file
recovery and later access before designing reconciliation for divergent cuts.
