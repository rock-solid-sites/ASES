---
title: "Server Crash Post-Mortem — Evidence Log"
program: EDASES
layer: Research
document_type: Incident Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - session-recovery-after-crash.md
  - evidence-based-gates.md

consumed_by:
  - session-recovery-after-crash.md

supersedes: []

superseded_by: []

last_updated: 2026-08-10
---

# Server Crash Post-Mortem — Evidence Log

**Date of incident:** 2026-07-13, ~17:46 UTC
**Reported by:** user (claude-code)
**Investigated by:** opencode session (opencode v1.17.19)
**Status:** OPEN — root cause strongly inferred but not yet confirmed at the hypervisor layer

---

## 1. Incident summary

The Hostkey VPS (Ubuntu, kernel `5.15.0-184-generic`) became **fully unresponsive**: the
Hostkey web panel, SSH, and Tailscale SSH were all unreachable. The user performed a
**hard reset via the Hostkey control panel**. This is the **second** such crash while an
opencode session with **multiple concurrent `task` agents** was running.

The investigation goal: determine what consumed memory before the reset.

**Working hypothesis (high confidence):** Memory exhaustion caused by opencode session
context bloat (≈870 MB/session) multiplied across concurrently-launched subagents, on a
≈8 GB VPS already carrying a ≈1.9 GB base stack (code-server, embedded mongo, MariaDB,
MCP servers). The box went unresponsive from memory pressure / thrashing, and the hard
reset destroyed the in-guest kernel log buffer.

---

## 2. Environment facts (verified)

| Fact | Value | Source |
|---|---|---|
| Host | Hostkey VPS, Ubuntu | user statement |
| Kernel | `5.15.0-184-generic` | `last reboot` |
| RAM (guest view) | 7919 MB total | `free -m` |
| opencode version | 1.17.19 | `opencode --version` |
| opencode data dir (live) | `/tmp/opencode/` (only `mcp-sqlite.db`, 0 bytes) | `ps` of MCP servers |
| opencode session store | embedded MongoDB (`mongodb-memory-server`, PID 2273) | `ps` |
| User | `claude-code` (uid 1003), groups: `sudo`, `docker`, `www` | `id` |
| `npx` | present at `/home/claude-code/.nvm/.../bin/npx` in interactive shell | `which npx` |

---

## 3. Timeline (reconstructed)

| Time (UTC) | Event |
|---|---|
| Jun 23 13:56 | Host previous boot began (per `journalctl --list-boots -1`) |
| Jul 13 03:45 | vscode-server session `20260712T124327` started |
| Jul 13 04:14 | Host boot known to journald ends (journal gap begins) |
| ~17:4x | opencode session active; reads **entire cargo-registry crosslink source tree** + large `rtk rg` outputs into context (→ ≈870 MB `opencode.db`) |
| ~17:4x | User requests two `task` subagents (deepseek-flash + nemotron-verifier) launched **in a single message** (each clones parent context) |
| **17:46** | **VPS becomes unresponsive; user hard-resets via Hostkey panel** (`last reboot` shows boot at 17:46) |
| 17:48 | vscode-server session `20260713T174808` starts (current) |
| 17:53 | opencode session PID 5026 starts (pts/1) |
| 17:55 | opencode session PID 6082 starts (pts/2 — current recovery session) |

Note: `journalctl --list-boots` shows boot `0` as `17:48:06 → 17:48:09` (3 s), which is
inconsistent with a normal boot and reflects container/boot-tracking quirks. The
authoritative reboot marker is `last reboot` → `Jul 13 17:46`.

---

## 4. Evidence gathered (and its limits)

### 4.1 Checked — NO crash-cause trace found in-guest
- **`dmesg`**: no OOM-killer, no kernel panic, no `kill` entries.
- **`journalctl -k -p err` and `journalctl` full-text**: **zero** `out of memory` /
  `invoked oom-killer` / `killed process` entries across **all** boots.
  - Implication: either the OOM killer never fired (pressure/thrashing instead), or its
    messages were lost in the hard reset (journald does not fsync every line).
- **`/var/log/kern.log`**: **Permission denied** (root/adm only). `sudo -n` fails
  ("a password is required") — NOPASSWD is not configured.
- **`/var/log/syslog`**: same permission restriction; not directly readable.
- **`apport.log`**: empty (no userspace crash reported).
- **`/var/log/apport.log`**: no crash dumps.
- **Process accounting** (`lastcomm`/`sa`/`accton`): **not installed** → no per-process
  historical resource records.
- **vscode-server logs** (`~/.vscode-server/data/logs/`): the pre-crash session
  (`20260712T124327`) simply **stops at 04:11** with only benign "Could not find pty"
  warnings — no crash record at 17:46. The death was not logged (process killed outright).
- **cgroup memory limit**: `/sys/fs/cgroup/memory.max` and `memory.events` are **not
  readable** from inside the container → the enforced memory ceiling is set by a parent
  cgroup/hypervisor we cannot see. This is consistent with a parent-level OOM/reclaim
  that is invisible to the guest.

### 4.2 Checked — context-bloat signal (the standout anomaly)
- Pre-crash session produced an **`opencode.db` of 871 MB** (plus a 640 MB `.bak`) in
  `~/.opencode/`. That directory is **gone** after the reboot (session state discarded),
  but its size was captured before deletion. A normal session is far smaller; this size
  is attributable to ingesting the full crosslink cargo-registry source + large ripgrep
  outputs into context during this session.
- `opencode --log-level DEBUG --print-logs` exists but was **not enabled** at crash time,
  so no server-side trace was captured.

### 4.3 Current footprint (measured 2026-07-13 ~19:10, post-reboot, 2 sessions live)

| Consumer | RSS |
|---|---|
| opencode PID 6082 (current session) | 924 MB |
| opencode PID 5026 (other session) | 734 MB |
| mariadbd | 276 MB |
| code-server + extension hosts | ~490 MB |
| embedded mongo (opencode sessions) | 152 MB |
| node (chat-ui + MCP servers) | ~315 MB |
| **Total used** | **3.5 GB** (1.0 GB free of 7.9 GB) |

At crash time the estimate is: parent (~870 MB) + 2 subagents (~870 MB each, cloned
context) + other session (~730 MB) ≈ **3.2 GB opencode alone**, on top of ≈1.9 GB base
stack → near/over the ≈8 GB ceiling.

---

## 5. Constraints on the investigation
1. `sudo` requires a password the agent cannot supply → system logs (`kern.log`,
   `syslog`) are unreadable from inside.
2. Hard reset destroys the kernel ring buffer → in-guest OOM evidence is unrecoverable
   post-hoc.
3. No process accounting installed → no historical per-process memory series.
4. The **definitive** evidence (kernel OOM message + RAM graph) exists only at the
   **Hostkey control-panel layer** (Serial Console / Metrics), which the agent cannot reach.

---

## 6. Open questions for the user (needed to confirm)
1. **Hostkey Serial Console**: kernel output around 17:46 — is there
   `Out of memory: Killed process …` or `rcu_sched detected stalls`? Paste it.
2. **RAM graph**: peak RAM % just before 17:46?
3. **Plan size**: is the VPS 8 GB? (Confirm no smaller host cap.)
4. **Sessions open**: how many opencode terminal/chat windows were live before crash?
5. **Other load**: docker containers (none running now), `cargo` build, DB import, or a
   second AI session?
6. **Sudo password**: available to read `/var/log/kern.log`/`syslog` directly?

---

## 7. Recommendations (preventive, pending confirmation)
1. **Launch agents serially** — one `task` per message, never several at once. This is the
   change most directly correlated with both crashes.
2. **Shrink context** — delegate large source reads (e.g. the cargo-registry tree) to
   subagents instead of pulling them into the main session. The ≈870 MB context is the
   dominant, avoidable risk.
3. **Capture the next crash**: before any future multi-agent run, either (a) enable
   `opencode --log-level DEBUG --print-logs`, or (b) run a lightweight background poller
   writing `free -m` / `ps` RSS snapshots to disk every few seconds, so the last
   pre-death snapshot survives a reboot. Best source remains the Hostkey Serial Console.
4. **Consider a RAM bump** on the VPS if multiple concurrent agent sessions are needed.
5. **Fix MCP `npx` flakiness** (separate issue): `opencode.json` MCP commands use bare
   `npx -y`; npm logs showed transient `could not determine executable to run` for
   `@modelcontextprotocol/server-github` at 17:53. Use absolute `npx` paths to harden.

---

## 8. Files examined during investigation
- `/home/claude-code/projects/ASES/to-file/evidence-based-gates.md` (design doc)
- `/home/claude-code/projects/ASES/to-file/gates-issues.md`
- `/home/claude-code/projects/ASES/to-file/gates-verified-facts.md`
- `/home/claude-code/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/crosslink-0.9.0-beta.1/` (verified facts for the gates work)
- `/home/claude-code/.config/opencode/opencode.json`, `models-cache.log`
- `/home/claude-code/.vscode-server/data/logs/20260712T124327/remoteagent.log` (pre-crash session)
- `/home/claude-code/.vscode-server/cli/agent-host-stable.log`
- `/tmp/crosslink-guard.log`, `/tmp/rtk-guard.log`, `/tmp/orchestrator-guard.log`
- `/home/claude-code/.npm/_logs/2026-07-13T17_5*.log` (MCP spawn noise)
- `/var/log/syslog`, `/var/log/kern.log`, `/var/log/apport.log` (root-only, unread)
- `journalctl --list-boots`, `journalctl -k -p err`, `journalctl` full-text
- `dmesg`, `last reboot`, `uptime`, `free -m`, `ps`, `id`, `ulimit -a`,
  `/sys/fs/cgroup/memory.*` (limit/events unreadable)
