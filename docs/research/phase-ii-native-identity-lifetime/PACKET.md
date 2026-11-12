# Keep identity observation inside the actual Child lifetime

ASES-4 C/D follow-through, parent draft #33 at94616a21. This is a narrow
resource-control adapter correction; no canonical identity model or process
adoption API is added.

## Reasoned defect and required behavior

LocalSupervisor poll/stop/stop_graceful currently refresh process_identity from
/proc/child.id whenever the cached process is None, including after owned.exited
has been set by an actual wait. If the initial identity observation failed,
a later lookup after reap is no longer tied to the Child's unreaped lifetime.
A reused numeric PID or stale observation could then create a false Started
identity followed by the old Child's cached exit. Resume also labels any cached
exit as exit_observed even when no exact identity/start was established.

The source path is concrete; real Linux PID reuse has NOT been reproduced.
Use bounded observation-fault injection with an actual Child and actual Store
to falsify the old adapter behavior, clearly labeled as such. Do not stress PID
allocation, change procfs/host configuration, or claim an injected token was an
actual OS observation.

Refresh missing process identity only while that actual owned Child has not
been reaped. Preserve a previously captured identity for its historical exit.
After reap without identity, poll/launch replay/force stop/graceful stop/resume
must preserve unknown exact outcome: no new Started or exit-evidence event,
no signal, no automatic finalize or capacity release. A raw wait result without
its required identity does not become typed durable evidence. Resume must not
claim exact exit_observed for that unidentified child. Known-identity normal
exits and existing wire schemas remain unchanged.

## Implementation boundary

Make the smallest changes in resource-control/src/local.rs. A private test-only
identity reader per LocalSupervisor is allowed to inject observation failures
and a later stale result; no production constructor/input or global test state.
The actual runtime default remains the existing /proc reader. Tests live in
resource-control/src/local/identity_lifetime_tests.rs, included as a cfg(test)
child module so they can examine private state without a public diagnostic API.
No new dependency, database, event type or credential.

## Discriminating test

Use the actual Store catalog/reserve/acknowledge and actual supervisor launch
of one fixed harmless local program, with an injected initial identity-read
failure. Poll with that failure until the actual Child has exited and is reaped.
Then offer a stale identity result through the test-only reader. Exercise poll,
exact launch replay, force stop, graceful stop (separate fresh fixtures if stop
plans conflict), and resume. The old algorithm should be demonstrably capable
of accepting that post-reap observation; capture a failing pre-fix test against
otherwise unchanged production logic plus the explicit test seam.

After the fix, require unknown result, no LAUNCH_STARTED_OBSERVED or
LAUNCH_EXIT_OBSERVED, LAUNCHING state/reservation held, finalize refused, and
no second dispatch. Assertions target durable behavior, not merely a reader
call count. Preserve exact source versions/commands and the injected nature of
the counterexample. Real wait status comes from the actual Child; the offered
stale token is explicitly NOT an actual second process or proven PID reuse.

Run the focused fault histories after the fix and the affected existing native
local gateway and cooperative-stop targets once. Store-only broad suites and
independent CI/review are out of scope. Use existing toolchain/cache, reduced
debug/incremental-off flags, and one shared build at a time; disk about300MiB.

WHY: prevent a numeric lookup after lifetime end from becoming exact evidence.
WHAT: actual owned Child/wait and Store plus a labeled observation-fault seam.
HOW CERTAIN: reasoned source defect until pre-fix failure and fixed behavior pass.
WHAT NOT TESTED: actual PID reuse, hostile procfs/root/same-UID, host loss, remote
providers, generic process adoption or automatic repair of unknown identity.
