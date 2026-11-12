# Native local observation interface

The opt-in observer is a separate manager command:

```text
python -B observe_local.py OWNER_ROOT REQUEST_ID
```

It derives the existing native attachment from the protected owner state. It
accepts no journal path, sequence, payload, certificate, cut, witness endpoint,
publication claim, or force flag. It takes the existing F4 writer guard once,
parses the bounded journal with the actual `RetryState`, holds that state's
mutex, and reuses the existing owner session and publication settlement helper.

The observer accepts a reserved owner effect only when the request has one
existing protected reservation with no sequence, and the requested effect is
the exact complete final journal record at its actual parsed sequence. It
rechecks the journal, owner reservation, retained historical registration/F1
world, owned material, immutable owner generations, attachment, and witness
under the existing locks before calling `Session.record_local_effect`. It then
continues through the existing single-CAS/fresh-check/settlement flow in the
same process and under the same F4 writer lock.

The strict `reconcile.py OWNER_ROOT REQUEST_ID` command remains unchanged at its
CLI boundary and continues to refuse reserved-only owner status. If no actual
matching final event exists, observation refuses without cancelling the
reservation or declaring no effect. An already-local or already-published
effect uses the existing reconciler behavior. Published state still requires
the current witness to match the full actual cut; a prior cut is never repaired
from an old receipt.

## Results and test gates

The command emits one JSON result frame with `event` equal to
`native-local-observation`. `status` uses the existing reconciler outcomes:
`published`, `refused`, `refused-writer-guard-busy`, `unresolved-publication`,
or `unresolved-settlement`. Successful promotion reports
`observation_attempted: true`, `observation_status: local`, and the parsed
`event_seq`. A prepublication interruption reports the same committed local
observation with `status: unresolved-publication`,
`publication_attempted: false`, and `settlement_status: not-attempted`. This
means the owner selection may have committed even though publication has not
started; rerun strict `reconcile.py` to finish without another observation,
journal append, or CAS when the witness is still at the preceding cut.

Only tests may request an explicit gate:

```text
python -B observe_local.py OWNER_ROOT REQUEST_ID --test-gate after-local-observation-before-publication
python -B observe_local.py OWNER_ROOT REQUEST_ID --test-gate after-confirmed-publication-before-settlement
```

The first gate exists only after a reserved record has been durably selected as
local, when the witness was at the exact preceding cut and before a publication
CAS. The frame is `GATE` with phase
`after-local-observation-before-publication`; stdin must receive `continue\n`.
Killing at that gate leaves the local owner selection and the original complete
journal event in place. The strict reconciler can then issue the one necessary
CAS and settle the same sequence.

The second gate is the existing postpublication gate, after the settlement
helper's fresh witness check and before it selects owner status `published`.
Closing stdin there returns `unresolved-settlement` with confirmed publication
and unknown settlement; a process kill produces no final frame. No gate adds an
owner status or changes the journal.

WHY: recover the narrow crash gap between the original F4 fsync and its native
owner `record_local_effect` callback without treating local admission as remote
publication or current use.

WHAT: the original native owner reservation, parsed final event and sequence,
retained historical evidence, existing witness and callback/settlement paths.

HOW CERTAIN: experimental until the real sink fsync-gap histories and controls
pass.

WHAT NOT TESTED: hostile same-UID/root, arbitrary rollback or power loss,
absence-based cancellation, missing-witness repair, remote exactly-once
delivery, generalized F3 semantics, or automatic grant revival.
