---
title: "Server Memory Management"
tags: ["ops", "memory", "oom", "systemd"]
sources: []
contributors: ["OL2r"]
created: 2026-07-20
updated: 2026-07-20
---

# Server Memory Management

**Crosslink knowledge page — ops/memory**

---

## Problem

The VPS has 8GB RAM with a ~1.9GB base stack (code-server, MariaDB, MCP servers). OpenCode sessions with fan-out subagents can spike to 3GB+ per session (parent 870MB + subagents cloning context). Multiple concurrent sessions → OOM → hard reset.

The July 13 crash killed the server during a session with 2 concurrent subagents (~3.2GB opencode alone + 1.9GB base = 5.1GB, leaving <1GB headroom on 8GB).

## Three-Layer Defense

| Layer | Mechanism | What it does | Config |
|-------|-----------|--------------|--------|
| **1** | systemd scope (MemoryMax) | Hard-caps a single session to 3GB | `/home/claude-code/.local/bin/claude` wrapper |
| **2** | earlyoom | Kills the hungriest process before kernel OOM | `sudo apt install earlyoom && sudo systemctl enable earlyoom` |
| **3** | zram swap | 3.9GB compressed RAM swap as buffer | Already configured (`/dev/zram0`) |

## systemd Scope Wrapper

The `claude` wrapper at `/home/claude-code/.local/bin/claude` automatically wraps opencode in a systemd user scope when running inside tmux:

```bash
# Inside tmux → scoped
systemd-run --scope --user -p MemoryMax=3G -p MemoryHigh=2560M opencode run ...

# Outside tmux (interactive) → uncapped
opencode run ...
```

**Key details:**
- Only applies inside tmux sessions (interactive sessions are uncapped)
- Requires lingering: `sudo loginctl enable-linger $(whoami)` (already enabled)
- Override per-session: `OPENCODE_MEMORY_SCOPE=4G claude --model ...`
- MemoryHigh (2.5GB) triggers reclaim before hard cap (3GB) is hit
- Subagents inherit the cgroup via fork/exec — no extra config needed

**Verify it's working:**
```bash
# Check scoped sessions
systemctl --user list-units --type=scope

# Check memory limit on a specific scope
cat /sys/fs/cgroup/user.slice/user-1003.slice/user@1003.service/run-*/memory.max
```

## VACUUM Policy

opencode.db grows due to session/event/message storage. After bulk deletions, run VACUUM to reclaim freelist space:

```bash
# Must be done with ALL opencode sessions closed (file lock)
sqlite3 ~/.local/share/opencode/opencode.db "VACUUM;"
```

The DB was 922MB (with ~730MB freelist) before VACUUM → 207MB after.

## Session Cleanup Rules

When an agent needs to delete sessions from the DB:

1. **Never delete the active session** — opencode allows it (bug [#37975](https://github.com/anomalyco/opencode/issues/37975)), but it kills the session with FOREIGN KEY constraint failed
2. **Use filtered lists, not raw indices** — cross-reference classification files against live DB
3. **Exclude the active session ID explicitly** — hardcode it in the delete script
4. **VACUUM requires full shutdown** — all opencode processes must exit first

## See Also

- `docs/research/session-recovery-after-crash.md` — crash recovery procedures
- `docs/research/session-audit-plan.md` — 7-stage cleanup plan and results
- `docs/research/opencode-bug-session-delete-active.md` — upstream bug report
- `to-file/crosslink-gates/server-crash-postmortem.md` — July 13 crash postmortem
