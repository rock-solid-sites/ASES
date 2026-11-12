# Native UID recovery evidence schema

The host runner writes one bounded JSON object to `evidence/uid-recovery.json`.
The object is the raw root-driver report with the actual host `outer` records
attached. It has `status`, `cases.local`, `cases.reserved`, UID process status
frames, and `outer`; raw command stdout, stderr, argv, return codes, and native
byte records are retained in those objects.

Each case has a fixed `case_kind` and `request_id`, the manager's READY frame,
the separate one-shot worker audit frame (`worker_audit`), the actual worker
process record (`worker_process`), a manager snapshot before and after denied
worker attempts, and the existing role-worker mediated management attempt.
`worker_audit` records the worker and manager `/proc` status, worker descriptor
access modes, direct protected `CURRENT` open and read-only manager FD listing,
private sink and witness socket connection attempts, both direct real CLI
invocations (argv, exit, stdout, stderr, parsed JSON), and a bounded fork/exec
descendant's corresponding credential/FD/socket/CLI observations.

The recovery record retains the actual command argv/stdio/exit/parsed result and
manager snapshots. `cold_restart` retains fresh sink startup/readiness and
owner disposition. `transition` retains manager-owned F4 replace/activate and
actual native owner seal/move/activate replies. `fresh_denial` retains the
fresh current-ID request, native response, and before/after journal records.
`exact_old` retains the actual request-index payload lookup, submitted bytes,
historical result, and journal records. Every byte record carries raw hex,
length, and SHA-256 where provided by the native helpers.

The checker derives the result from these raw records. It checks both cases,
actual UID/GID/groups/capabilities/NNP, absence of writable regular worker FDs,
structured protected-store CLI permission failures, unchanged state across
denied worker operations, one actual journal effect with witness confirmation,
and correct post-move new-ID denial plus exact-old-ID behavior. Its negative
controls mutate a worker management result to allowed and a recovery success
while leaving the owner pending; both must be rejected.

`CapBnd` is retained and syntax-checked as an observation; its value is not
assumed to be zero. The capture is a bounded native fixture experiment, not a
general same-UID/root confinement claim.
