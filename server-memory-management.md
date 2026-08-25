---
title: "Server Memory Management"
tags: ["ops", "memory", "oom", "systemd"]
sources: []
contributors: ["OL2r"]
created: 2026-07-20
updated: 2026-08-25
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



---

## earlyoom kill behavior (documented 2026-08-25 after #473 misfire chain)

Stock Debian earlyoom, DEFAULT thresholds on this host: SIGTERMs the **biggest memory consumer** whenever available RAM AND swap BOTH drop below 10 percent. The only flag in use is -r 3600 (hourly self-report) — no -m/-s threshold overrides and NO prefer/avoid lists.

**Observed kills:** opencode sessions (operator-reported, multiple times) and agent processes (pp3g-qlIC collector killed ~05:58 UTC 2026-08-25 during swap exhaustion at 3.4G/3.9G — see issue #473).

**Forensics trap:** earlyoom kills are USERSPACE SIGTERMs. They are logged under the earlyoom unit journal / syslog, NOT the kernel ring buffer — journalctl -k plus grep oom returns EMPTY even right after an earlyoom kill. Check: journalctl -u earlyoom --since <window> (may require sudo).

**PRE-LAUNCH CHECK (orchestrator procedure before dispatching memory-heavy agents):**
1. free -m — read the available column.
2. Rule of thumb from the July-13 crash postmortem: keep >=1GB headroom over base stack (~1.9GB) plus expected fleet footprint; defer or stagger launches when available RAM+swap headroom approaches the 10-percent earlyoom trigger.
3. Heavy collectors/scrapers: schedule during low-fleet windows or add their own memory ceiling.

**Mitigation knobs if tuned later:** earlyoom -m/-s PERCENT to move thresholds, --prefer/--avoid regex lists (e.g., protect the opencode TUI itself), -r for report cadence.

Related: #473 (first live Observer misfire chain — earlyoom SIGTERM of a self-throttling collector misread hours earlier by the freeze detector).
