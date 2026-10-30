# F3 Landlock probe checkpoint (incomplete)

Resume verified: existing Crosslink session #2 is active and bound to issue #10. Branch `research/phase-i-protected-work-unit-f3-20261029` is at remote-verified SHA `562f595000d8ad90751087e8382b48ee2e61dff8`. `REPORT.md`, `CHECKPOINT.md`, and the plain observation were inspected; the plain chmod result is conclusive only for that fixture and will not be rerun. Existing untracked `exp1/run/` and `.crosslink/.last-hydrated-ref` state are preserved.

## Single bounded next operation

Probe Linux Landlock from one unprivileged child in a new disposable directory under `exp2/` in this worktree. First check ABI availability and whether the child can create a ruleset, set `no_new_privs` if required, and enter restriction. Do not use privileged operations, alter host policy, or install anything. If unavailable or setup requires privilege/host changes, record the exact errno/result and stop. If available, only the same probe milestone may test a tiny fixture: direct path open and alias path should be denied under the child ruleset; access through a trusted per-operation mediator should be exercised; an already-open descriptor must be tested separately to see whether ruleset restriction affects retained access. Stop test processes, preserve the fixture/logs, and do not generalize into proxy/bodyguard/runtime implementation.

F1 remains partial; no lifecycle acceptance. F5 independent review remains outstanding.