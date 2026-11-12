# UID-custodied native recovery interface

## Bounded runner

The host entry point is:

```text
python -B run_uid_recovery.py --out OUTPUT_DIRECTORY
```

It verifies the pinned local image ID, creates one labeled container from that
image, copies a normalized explicit source set into `/opt/owned-src`, then
starts and attaches to the container. It preserves the image's
`/opt/probe/driver.py` and runs this fixture's root driver using the image's
Python. The driver imports the pinned base driver's actual `Child`, `preexec`,
`role_worker`, and `mediate` helpers. The runner records each Docker argv,
return code, stdout/stderr, copied-source SHA-256, container identity and
cleanup result in the outer report. It creates no image and attaches no host
mounts, socket mounts, or ports.

## Manager controller

`owner_controller.py` runs as UID 2000 with fixed argv:

```text
owner_controller.py {local|reserved} REQUEST_ID
```

The trusted root driver chooses the case and bounded request ID. The worker
cannot select a recovery command or supply owner metadata, payload, token,
pair, certificate, or native operation.

The controller's first frame is:

```json
{
  "event": "READY",
  "case_kind": "local",
  "request_id": "uid-recovery-local",
  "uid": 2000,
  "owner_root": "/run/.../owner",
  "f1_db": "/run/.../store.sqlite",
  "sink_socket": "/tmp/.../sink.sock",
  "witness_socket": "/tmp/.../witness.sock",
  "owner_server_pid": 123,
  "snapshot": {
    "owner": {}, "f1": {}, "f4": {}
  }
}
```

`snapshot` contains the actual owner CLI snapshot, read-only F1 view and
retained observations, F4 journal bytes/status, witness status, and sink/witness
process/socket metadata. Each pipe command produces one `RESPONSE` frame that
retains its input and exact underlying command/API result.

Supported fixed controller operations are:

| Operation | Behavior |
|---|---|
| `snapshot` | Capture current actual owner, F1, journal, witness, process and socket state. |
| `write` | Treat the worker's bounded payload string only as its request ID, derive the native envelope and current F4 version from actual manager state, and submit through NativeF4. The initial fixture ID is gated and killed; after transition a fresh worker-chosen ID reaches the actual current-path check. |
| `recover` | Accept no mode or path arguments. Run strict reconcile for `local`, explicit observe-local for `reserved`, capture argv/stdout/stderr/exit/parsed JSON, then cold-restart the actual sink against the same witness. |
| `transition` | Replace and activate current F4 authority using manager-owned commands, then call actual native owner `seal`, `move`, and `activate` operations. |
| `exact_old` | Read the original payload from the actual recovered `RetryState` request index and submit that exact ID/payload under its original F4 version. |
| `stop` | Stop manager-owned F4 and owner services and report process tails and final records. |

The worker direct audit is a separate one-shot process, not a controller pipe
route. The root driver still uses the pinned `role_worker()` and `mediate()`
for ordinary D writes and management-route denial. The manager proxy accepts
only the same fixed D-write operation; a management request denied by root
mediation is not forwarded to UID 2000.

## One-shot worker audit

The UID 2001 worker is invoked as:

```text
worker.py OWNER_ROOT SINK_SOCKET WITNESS_SOCKET OWNER_PID REQUEST_ID
```

It emits one `UID_RECOVERY_WORKER_AUDIT` JSON frame and exits. It attempts both
recovery CLIs with the known fixture owner/request ID, a protected-store write,
direct sink/witness socket access, a read-only inspection of the manager's
`/proc/<pid>/fd`, and a fork/exec descendant check. It reports its own open
descriptors, raw CLI argv/stdout/stderr, parsed CLI frames, errno values, and
actual `/proc` UID/GID/group/capability/NoNewPrivs status. A Python import or
syntax failure does not count as a protected-store denial. The root driver
snapshots the actual owner/material/journal/witness state before and after
these denied requests.

## Case flow and results

Each sequential case begins with actual `setup_native_f3` and `NativeF4`
services under the UID 2000 controller. The worker supplies only the bounded
request ID through the existing root-mediated D-write route. The local case
gates after the original owner callback; the reserved case gates in the
test-only wrapper after the real parent append/fsync and before
`NativeAdmission.after_append`. The controller records the actual final event,
owner status/sequence and prefix witness, then kills its own sink child.

Before manager recovery, UID 2001 direct CLI/socket/store attempts and a
mediated management request must be denied without changing the actual selected
owner records, owned material, journal bytes, or witness cut. UID 2000 then
runs the one appropriate CLI and captures its structured output. Recovery must
settle the same event without appending. A normal cold startup must accept the
matching cut and remain sealed. The manager then replaces/activates current F4
authority and performs actual native seal/move/activation. A fresh current
request must reach native current-path denial without append; the old accepted
ID must be looked up using the exact original payload recovered from the
actual journal index.

The outer raw report has `status` equal to `PASS` or `FAIL`, a `cases` object
with `local` and `reserved` histories, actual controller/worker status frames,
and an `outer` object containing Docker identity/invocations and staged source
hashes. Worker/checker-specific frame assertions are defined by the focused
probe and checker maintained with the evidence.

The root fixture driver's case keys are stable: `request_id`, `case_kind`,
`manager_ready`, `initial_write_route`, `initial_effect`, `worker_audit`,
`worker_process`, `manager_before_denials`, `worker_management_attempt`, and
`manager_after_denials`. The before snapshot is taken after the gated effect
and immediately before the direct audit; the after snapshot follows the direct
audit and mediated management denial. `worker_management_attempt` includes
`controller_op_count_before` and `controller_op_count_after`, counting only
requests forwarded to the UID-2000 pipe.

`recovery` is the controller's raw response, with `before`, `command`,
`cold_restart_ready`, and `after`. The `command` retains exact argv, monotonic
start/end times, exit status, stdout/stderr, and parsed CLI frame. Separate
`cold_restart`, `transition`, `fresh_denial`, and `exact_old` keys retain the
actual cold sink readiness, F4/native transition replies, fresh request result,
and old request-index event/request/journal records respectively. The runner
does not synthesize these results from status labels.
