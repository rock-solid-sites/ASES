# Bounded local execution vertical integration

ASES-4 priority D. Frozen parent: termination/expiry integration
8de86a3c2e330c5d0d1b600f150334f56c928f85 (draft #29), reusing launch
intents (#20), compact resume (#25), expiry (#28), exact exit evidence (#29).
Native F3 ownership convergence is separately retained in draft #30 at
f7b16ddbf34034ce1a0967c37cd92d5869f7e399; this slice does not replace it.

## Interface decision

Extend the existing resource-gateway with an optional trusted local profile.
Default gateway operation is unchanged. The actual SO_PEERCRED/Policy admin
grant is required for local_launch, local_poll, local_stop, local_resume and
local_finalize. No nonadmin operation list is broadened. Requests carry exact
job/launch IDs and operation-specific selectors, never executable, PID,
identity, observation, clock or environment. Reject unknown request fields.
The startup profile selects one absolute program, arguments, cwd and explicit
environment and exact account/project/environment scope. No shell parsing.
Jobs remain resource-controller jobs, not canonical Work Units.

An in-process LocalSupervisor owns nonserializable Child handles. It consumes
Store.begin_launch's nonclone DispatchGranted once. Replays return observation
and never dispatch. Native Started and exit evidence come from that known
Child; observe_launch_exit remains the existing exact-identity durable path.
A failure after intent/spawn stays unknown and retains capacity. Observe /proc
start token only for a known Child, never adopt a persisted PID. Use null stdin,
stdout and stderr, clear environment, and bounded local resources where feasible.

local_stop durably records one exact launch-bound stop request in the existing
SQLite event owner before acting on an owned Child handle. Identical replay
must be idempotent; conflicting stop ID or launch must have no effect. A stop
request is neither observed exit nor semantic completion. Kill/wait only the
owned Child, record actual wait status through #29, and leave capacity held
until explicit local_finalize. Polling may observe an exit but never finalize.

On gateway loss no Child handle survives in durable state. Cold resume reports
unknown present liveness; no PID reconstruction, blind redispatch or fabricated
exit. A cold stop can retain a bounded request but cannot signal an unowned
process. Existing finalize must remain blocked without exact exit evidence.
A retained stop pointer may accompany the existing <=2KiB resume view, within a
bounded outer result. Existing lifecycle event storage is reused; no parallel
scheduler, registry, provider adapter or universal state database is introduced.

## Required discriminating histories

Use the actual Unix gateway and fixed harmless worker to demonstrate: native
launch/replay with one child; rejected caller-controlled command/PID/identity;
actual peer role denial; wrong launch/stop selector without effect; durable
stop -> actual wait -> compact resume -> explicit finalize -> released capacity;
controller death -> cold unknown with no redispatch/finalization; and exact exit
and expiry regressions from the parent. Clean test workers using retained test
Child handles or their own bounded release/timeout, never PID adoption.

WHY: close the gap between independently tested lifecycle APIs and a native
engine consumer. WHAT: actual parent Store, peer policy and process handles.
HOW CERTAIN: experimental until native histories pass. WHAT NOT TESTED: remote
providers, arbitrary command delegation, containment of hostile same-UID code,
whole-machine power loss, mandatory wall-clock quiescence, generalized F3,
or automatic cancellation on later authority/catalog changes. Profile and
host remain trusted; launch retains #20 decision-authorized semantics.
