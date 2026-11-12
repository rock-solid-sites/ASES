# Native pending-publication reconciler interface

This experimental command is scoped to the existing native owner/F4 private
Unix attachment. It derives the journal, witness endpoint, and witness root
from the selected protected `sink_binding`:

```text
python -B reconcile.py OWNER_ROOT REQUEST_ID
```

The only optional argument is a test gate used for a kill/restart history:

```text
python -B reconcile.py OWNER_ROOT REQUEST_ID --test-gate after-confirmed-publication-before-settlement
```

There is no caller-supplied journal, witness endpoint/root, cut, payload,
certificate, publication claim, or override. The command requires an existing
regular journal, existing regular `sink-writer.lock`, unchanged bound parent
identities, and the existing bound Unix witness socket. It takes the existing
writer lock exclusively and nonblocking before replay or witness traffic.

## Output and exit status

Normal execution emits one JSON line with `event` equal to
`native-publication-reconcile`. A successful settlement has `status` equal to
`published`, `settlement.status` equal to `published`, `event_seq`, and
`cas_count` (`0` or `1`). `publication_reply_lost` records a CAS whose response
was lost but whose target was established by a later fresh check. The `protocol`
array contains nonce-bearing witness request/response frames for this command.
Exit status is `0` only when the protected owner effect is published.

Bounded refusal emits `status: refused` and a concrete `reason`; an occupied
writer lock emits `status: refused-writer-guard-busy`. A witness observation or
target confirmation that cannot establish the exact target emits
`status: unresolved-publication`. These cases exit `1` and never retry a CAS
after an uncertain reply. Invalid CLI syntax prints usage and exits `2`.

With the explicit test gate, the command prints this frame after a fresh check
has confirmed the target and immediately before owner settlement:

```json
{"event":"GATE","phase":"after-confirmed-publication-before-settlement","pid":123,"request_id":"..."}
```

It then waits for `continue\n` on stdin. Continuing produces the normal final
result frame. Killing the process at the gate produces no final result frame;
the next invocation observes the exact target, performs no second CAS or
journal append, and invokes the existing settlement helper. The gate is
accepted only through the explicit test-only CLI form above.

## Supported transition

The command replays the bounded complete journal with the existing
`RetryState` parser and request index. It requires the requested native effect
to be the exact final journal event, unique in the index, and to match exactly
one protected owner effect with `status: local`, the same sequence and payload
hash. It verifies the retained registration/world evidence, historical owner
record, retained F1 observation, and owned material. It does not require the
current D write grant, selected registration, selected F1 row, or current owner
epoch to match the historical event.

The fresh witness `/check` must report either the exact full local cut or the
cut whose journal hash covers the prefix immediately before the final effect,
with the same replayed authority. Only the exact preceding cut permits one
`/publish` CAS. A fresh `/check` must confirm the full cut before settlement.
Publication reply loss remains distinct from a confirmed no-effect response;
it is never grounds for blind CAS retry. Already-published matching cuts skip
CAS. The command then calls `native_sink.settle_from_native_sink` under the
actual parsed state's mutex and the exclusive F4 writer guard, without holding
`Owner.locked` across that helper.

Malformed/torn/oversized journals, unsupported profiles, unsupported or
missing attachments, changed identities, reserved-only effects, other pending
effects, and non-exact witness cuts are refused without cleanup or journal
mutation. The command does not append, initialize F4, modify F1/L6, or create a
new authority store.
