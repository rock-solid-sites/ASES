# Incomplete checkpoint — Agent A (Kernel-0 timing reduction)

- Branch: `research/phase-i-kernel0-timing-20261029`
- Parent/base commit: `d0c6e564d36f38ed09a37bc21e85c8df48da77b7`
- Pre-checkpoint branch HEAD: `d0c6e564d36f38ed09a37bc21e85c8df48da77b7`
- Crosslink: issue #7
- Provider session: `74352b31-39e3-4471-9838-23cbcc04f92f` (ended with Phoenix Grove HTTP 402)

## Preserved findings

The October 5 handoff/review was read and the existing RTL/oracle inputs were inspected. `timing_event_model.py` and partial run evidence exist. The last preserved correspondence progress is `independent: state-word 0/4194304, offers 0, 0.0s`. Several unbounded duplicate runs were stopped; see `evidence/process-cleanup-2026-10-29.md` and the orchestrator amendment beside it.

No timing weakening has been established. No correspondence run completed, and no counterexample or synthesis/regression result is claimed.

## Incomplete work / next operation

Review the event/cut harness for state-space and implementation defects; run one bounded profile at a time; capture raw output in this directory; only state a weaker timing contract if whole-proposal capture, coherent observation, whole-successor publication and interacting-commitment order are demonstrated with ingress unchanged.

## Artifacts

- `timing_event_model.py`
- `evidence/correspondence-run.log`
- `evidence/process-cleanup-2026-10-29.md`
- `evidence/orchestrator-cleanup-amendment.md`