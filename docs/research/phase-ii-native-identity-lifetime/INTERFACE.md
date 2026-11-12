---
title: Native local identity lifetime interface
program: EDASES
layer: Research
document_type: Interface Note
status: Active
authority: Derived
depends_on:
  - PACKET.md
  - REPORT.md
---
# Native local identity lifetime interface

## Surface

The correction is contained in `resource-control/src/local.rs`. It does not
change the public `LocalSupervisor` constructor, its production inputs, Store
event types, resume schema, or process identity representation. Production
identity reads still use the existing `/proc/<pid>/stat` reader.

The existing adapter operations remain the boundary:

| Operation | Identity and exit behavior |
| --- | --- |
| `launch` | A newly granted dispatch reads identity once after spawning its owned `Child`. A replay delegates to `poll` and cannot dispatch another child. |
| `poll` | A missing identity may be retried only while the owned `Child` has not yet returned a status from `try_wait`. The exit is durable only when the retained child status and captured identity are both available. |
| `stop` | A missing identity may be retried only before the retained child is reaped. A reaped child with no identity remains unknown and does not gain start or exit evidence. |
| `stop_graceful` | The same lifetime boundary applies. Without identity and a recorded start, it returns unknown without attempting a signal. |
| `resume` | `exit_observed` requires a reaped child, a captured identity, and a recorded start. A reaped child without those facts reports the existing `unknown` state. |
| `finalize` | No adapter behavior is added; the existing Store finalizer still requires exact process exit evidence. |

An identity already captured during the child's lifetime remains available for
recording that child's later exit. Once `try_wait` has returned an exit status,
an absent identity is not refreshed from the numeric PID. The local result,
launch state, and reservation therefore remain unknown/held when exact identity
evidence is unavailable.

## Test-only seam

Under `cfg(test)`, each `LocalSupervisor` has a private `identity_reader` closure
initialized to the same `/proc` reader. A test can replace the closure on that
supervisor instance to inject an initial read error and later offer a synthetic
stale identity. The seam is neither a production constructor parameter nor
global state. The test module is a private child module of `local.rs`, allowing
it to inspect owned-child state without adding a public diagnostic API.

The bounded histories use the real SQLite-backed Store and an actual `/bin/true`
child. They observe the child's own wait status before changing the injected
reader result. The synthetic token is not an OS observation, a second process,
or proof of PID reuse. Five pre-fix failures and the post-fix focused and
affected-target results are recorded in [`REPORT.md`](REPORT.md) and
[`evidence/`](evidence/).

## Source and evidence pins

The seam-only baseline is commit `36acdf8f6f280e40c86d3dad94a99c372e8b7558`.
The implementation correction is commit
`e1148e883102b880125380e55f08dd22ad63ea58`. The raw command output and source
hash metadata under `evidence/` identify the source actually exercised.

WHY: an identity lookup after reap is no longer tied to the owned Child's
unreaped lifetime.

WHAT: actual Child wait/reap and Store effects, combined with bounded private
test fault injection.

HOW CERTAIN: the old behavior was reproduced and the corrected focused histories
and two affected targets passed; see the run records for command and source
provenance.

WHAT NOT TESTED: actual PID reuse, `/proc` tampering or staleness, hostile
same-UID/root behavior, host loss, remote providers, process adoption, or
automatic repair of an unknown identity.
