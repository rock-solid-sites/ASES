# Expiry remains terminal under generic finalization

Frozen 2026-11-10. Parent source: compact resume-view PR #25,
`9fb8a525c32b56b9191d3f33df9925939636dc9a`. Grounding: Engine Vision's
explicit recoverable state and invalid-transition enforcement; campaign P5
continuation from durable state. This narrow defect was found while selecting
the termination observation integration boundary.

`finalize` explicitly handles CLOSED, LAUNCHING, RESERVED and AUTHORIZED but
does not whitelist the remaining source states. An already EXPIRED job can
therefore become CLOSED/completed (or another terminal label), retaining both
EXPIRED and FINALIZED events. The compact resume interpreter correctly refuses
that contradiction. This is a local state-machine bug, independent of actual
worker termination or provider behavior.

First capture the unchanged implementation's behavior for all four allowed
finalization outcomes from independently expired reservations. Then refuse
generic finalization from EXPIRED or unsupported states without writing an
event or changing state/capacity. Keep CLOSED same-outcome replay and existing
unlaunched/mock profiles. Do not alter expiry timing, launch-intent semantics,
canonical policy or the separate active termination-evidence implementation.

Use the existing Rust control fixture and one focused regression, checking
job/event/view/balance stability, repeated expiry and the valid neighboring
unlaunched cancellation path. Preserve before/after JSON and exact commands;
run existing control and resume suites once after repair. No dependency, native
process, external service, CI or independent review is needed for this purely
local database transition.
