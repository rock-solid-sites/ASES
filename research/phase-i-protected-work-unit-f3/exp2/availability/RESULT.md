# Landlock availability milestone (2026-10-30)

Executed once in `exp2/availability/landlock_availability.py`, from its disposable directory in the assigned worktree, under unprivileged UID 1003. Five-second timeout; child exited normally.

Observed JSON: `{"abi": 1, "machine": "x86_64", "pid": 155992, "result": "restriction-entry-succeeded", "ruleset_fd": 3, "status": "empty-read-deny-ruleset-entered", "uid": 1003}`.

The child queried Landlock ABI 1, created a ruleset handling read_file/read_dir, successfully set PR_SET_NO_NEW_PRIVS and entered restriction. This establishes syscall/API availability for this child only. It does not yet establish the policy denies any path, restricts aliases, mediates access, or revokes a retained descriptor. No package, privilege escalation, host policy/sysctl, or external service was used.

Next bounded step: one disposable fixture and one confined child; test direct target path, symlink alias, an FD opened before restriction, and a per-operation parent mediator. Record exact allow/deny results; stop only these children. No runtime or lifecycle implementation.