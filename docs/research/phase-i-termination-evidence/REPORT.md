# Exact process exit before intent-backed finalization

The surviving implementation at `7d0fba07` adds a trusted local-adapter exit
observation tied to the exact Started process identity and launch. The typed
status distinguishes exit code from signal. Observation is durable and
idempotent, leaves RUNNING/capacity held, and does not grant redispatch.
Intent-backed finalization requires that evidence. Mock behavior stays separate.
The compact resume view points to exit evidence and advises finalization only
after it is recorded; present process liveness remains unknown.

The real pre-change comparator, compiled against immutable `9fb8a525`, shows a
fixed child still live after finalize(cancelled): active reservation drops
50 to 0, available capacity rises 50 to 100 and another reservation succeeds.
The source, runner and captured JSON are retained here. The generated detached
comparison worktree also survives locally; it is ignored, not copied as an
embedded repository or claimed as committed evidence.

The repaired native target passes eight tests: four actual process histories,
two profile/projection controls and two fixed helper entrypoints. Actual owned
children demonstrate all four finalization labels refused while live; wait/reap
then explicit observation then separate finalization; controller SIGKILL after
Child::wait but before recording, followed by cold refusal until explicit trusted
evidence; and a signal-9 exit observed through its exact Child handle. No PID is
adopted or signaled by guessing a number. Synthetic identity/status controls are
separately labeled by their tests. Source semantic tests pass 3/3, control 47/47
and resume view 5/5 in the retained pre-integration capture.

Observation truth and current store custody are trusted adapter premises. The
local typed record does not prove arbitrary caller input true. This slice does
not implement a generic stop API, external provider, process takeover, automatic
cancellation, power-loss proof or physical liveness service. No independent CI
or review, merge or deployment occurred.

ASES-4 resumption found packet `cc4c795b`, implementation `7d0fba07`, native
sources and evidence intact in `/workspace/ases-termination`. They were preserved
before reconstructing anything. The source owner reported a stale shared-target
artifact and two fixture mistakes during initial runs; only the final raw
capture and its suite log survive here, so no missing failed log is fabricated.
Integration retained #28's exact three-line terminal EXPIRED guard and its
four-outcome regression from `3d24915b`, without copying unrelated evidence.
The integrated offline/locked run passes 48 control, five resume-view, three
exit-observation, four launch-target and eight termination-target tests. Its
fresh source-bound observations and exact command are retained separately in
`evidence/integrated-01`; the earlier native capture remains intact. All captured
source hashes were checked against the corresponding implementation before
publication. Initial shared-cache collisions were avoided with an explicit
test debug profile; no dependency or host/toolchain configuration was changed.
