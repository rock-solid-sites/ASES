# T05 host adapter ? selected subprofile

This F2-side evaluator independently checks the raw trace fields in `raw-run.json`; it does not execute or import F3 implementation code, and does not use F3 `safe_candidate_pass` or `violation_detected` labels as assertions.

## Pinned input and discrepancy

- Frozen packet: `origin/planning/ases-phase-i-f2-t05-host-bridge-20261030` commit `da72ed0d97f0e3adb1225cab2cd0dfa6b8eb415f`, `T05-HOST-ADAPTER-PACKET.md`.
- Packet's F3 pin: `04600b1b45e6510665bdc3108db9d51e6b2f8c56` (**unavailable/incorrect pin**).
- Corrected immutable source commit verified by the orchestrator: `04600b1b45e6510665bdc3108db9d51f6b2f8c56` (the packet pin's penultimate `e` is `f`). Only the `research/phase-i-protected-work-unit-f3/authority-loss/run.json` Git blob from that commit was copied here.
- Source blob/input SHA-256: `afafe338f9470cb35fadee28969fe10f4b51c15a6bf490a6041b070055d6245c`.
- Raw sentinel SHA-256 is independently recomputed from `authority-loss-sentinel-v1` and compared with the trace field.

## Checks and captured facts

The validator checks exact baseline sentinel replies; worker/holder/mediator PID relationships; H=-9 plus kill-request/reap/trigger order; positive integer CPU loop and post-reap interval; successful worker exit; safe same-socket `IOERROR:32` with no sentinel bytes; direct, symlink, and no-op `O_WRONLY` denial fields with errno 13; and the separate-H stale-grant control's post-reap sentinel delivery. It saves a mutated copy with protected sentinel bytes delivered post-loss and requires that the safe-profile evaluator reject it.

The observed safe profile has H=M=184953 and W=184954. The control has H=184955, M=184956, W=184957. Recorded safe CPU count is 392488 (a measurement, not a threshold); control count is 337193. Result details and raw field observations are in `result.json`. `mutated-safe-trace.json` is the fault-sensitivity input; `raw-run.json` remains unmodified.

Recorded environment from captured evidence: kernel `5.15.0-184-generic`, Landlock ABI 1, Python `3.10.12 (main, Jul 15 2026, 23:40:17) [GCC 11.4.0]`.

## Scope boundary

This is **host-observed for the selected T05 authority-holder-loss / surviving-worker / retained-socket / current-protected-read subprofile only**. Same-socket EPIPE is evidence about that peer/socket, not universal confinement. Untested inherited FDs, hostile peers, descriptors/SCM_RIGHTS, descendants, additional aliases, network, credentials, partial policy application, and D2/general external effects remain explicitly untested. Full T05 acceptance and aggregate T01?T24 acceptance remain partial; the F2 fixture catalogue and expected values are unchanged, and its abstract runner still reports T05 as prepared-only.

## Reproduction

From the F2 worktree:

```sh
python3 docs/architecture/core-substrate/fixtures-f2/t05-host-adapter/validate_host_trace.py docs/architecture/core-substrate/fixtures-f2/t05-host-adapter/raw-run.json --mutation-output docs/architecture/core-substrate/fixtures-f2/t05-host-adapter/mutated-safe-trace.json
```

The exact invocation used to persist `result.json` is the same command with stdout redirected to that file. See `manifest.json` for source, hashes, and command record.

## Bounded abstract regression

Command: `timeout 110s python3 docs/architecture/core-substrate/fixtures-f2/run_fixtures.py` (stdout/stderr captured in `abstract-runner.stdout.txt`; exit code in `abstract-runner.exit-code.txt`). Observed exit code: **0**; 46 abstract replays executed, 2 prepared-only (T05 and T18 use-current), 0 blocked, and all 16 listed mutations discriminated. This run did not change the catalogue or expected values. The actual runner returned zero; prepared-only remains reflected in the summary rather than a runner failure.
