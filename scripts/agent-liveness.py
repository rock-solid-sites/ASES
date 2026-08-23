#!/usr/bin/env python3
"""
agent-liveness.py v2 — read-only one-glance liveness dashboard for kickoff
agents (EPIC #423 liveness workstream; issue #435).

v1 believed two liars and this is v2's reason to exist:

  Bug-A (fixed): LAST_ACTIVITY sourced from .git reflog mtimes reported
      identical fresh ages across ALL worktrees, because crosslink hydration
      and git housekeeping touch refs globally. Reflog mtime measures
      INFRASTRUCTURE activity, not agent activity. v2 drops the reflog as a
      signal entirely.
  Bug-B (fixed): STATUS was trusted from .kickoff-status files, which are
      write-once builder artifacts: killed processes show RUNNING forever,
      and read-only roles (blocked from sentinel writes per #434) show
      RUNNING after finishing. v2 never trusts the sentinel alone; it
      cross-checks against process aliveness.

Activity signal (last_activity), per agent:
    walk      — newest mtime among worktree files via a bounded recursive
                scandir walk that EXCLUDES the .git directory (depth cap +
                entry-count cap keep it bounded). This intentionally still
                includes the worktree's .crosslink/ tree: comments, syncs and
                issue writes there are authored by the agent itself, whereas
                the global-churn culprits of Bug-A live under .git/ and in
                the main checkout — both outside this walk.
    baseline  — checkout-time fallback used only when the walk finds no
                files: max(.kickoff-metadata.json started_at, worktree root
                mtime). The row always reports which source won.

Process aliveness probe (tmux, per agent whose session name == agent name):
    SESSION-GONE — tmux reports no such session.
    EXITED       — session exists but every pane is dead (#{pane_dead}) or
                   the pane's process tree contains nothing but shells: the
                   agent process exited back to an idle prompt while tmux
                   kept the session (remain-on-exit). Verified live: zombie
                   panes show pane_dead=0 + cmd=bash, so pane_dead alone is
                   NOT sufficient — the descendant scan is the discriminator.
    ALIVE        — at least one pane has a live non-shell descendant
                   (claude/opencode/node/timeout/...).

Agent role (for the #434 class): recovered from the session's FULL scrollback
(`tmux capture-pane -S -`), which retains the launch command containing
`--agent '<role>'` even after the agent process has exited. Roles
reviewer/auditor/orchestrator are read-only (sentinel-write blocked per #434).
When the session is gone the role is unknowable and reported as "unknown".

Cross-signal verdict matrix (sentinel x aliveness x recency x role):
    DONE-CONFIRMED        sentinel DONE (any aliveness) — explicit
                          completion beats every other signal
    RUNNING-ALIVE         ALIVE + fresh walk activity (< 2x budget)
    STALE-SUSPECT         ALIVE but quiet (>= 2x budget) — process lives,
                          evidence of progress does not
    FINISHED-UNMARKABLE   gone/exited + sentinel RUNNING/ABSENT + read-only
                          role (#434 class; mitigated by guard exception but
                          still detected)
    DEAD-UNMARKED         gone/exited + sentinel RUNNING/ABSENT + builder or
                          unknown role (the zombie class; conservative when
                          role is undetectable)
    LIKELY-FROZEN         overlay: identical pane hashes across two runs
                          (--pane/--all) freezes the verdict regardless of
                          the matrix outcome above

Pane-hash freeze detection:
    --pane NAME (repeatable) hashes the named agents' panes;
    --all hashes EVERY alive session in one pass. Two consecutive runs with
    identical hashes => nothing on that pane changed between runs =>
    LIKELY-FROZEN overlay. The first observation never concludes frozenness.
    State is written ONLY inside --state-dir.

Usage:
    python3 scripts/agent-liveness.py                     # dashboard table
    python3 scripts/agent-liveness.py --budget-min 30     # override silence budget
    python3 scripts/agent-liveness.py --pane pp3g-rChm-relaunch-of-429-research-after-frozen-predecessor-see
    python3 scripts/agent-liveness.py --all               # hash every alive session
    python3 scripts/agent-liveness.py --json              # machine-readable

Constraints: reads only outside --state-dir; writes ONLY the pane-hash state
file inside --state-dir (default /tmp/opencode/liveness-state/). Never
modifies agent state; tmux is invoked only for list-panes/capture-pane/
display-message reads; `ps` is invoked read-only for the process-tree scan.

Dependencies: Python 3 stdlib only (argparse, hashlib, json, os, re,
subprocess, sys, time, datetime); external read-only tools: tmux, ps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

DEFAULT_ROOT = "/home/claude-code/projects/ASES/.worktrees"
DEFAULT_STATE_DIR = "/tmp/opencode/liveness-state"
STATE_FILENAME = "pane-hashes.json"

WALK_MAX_DEPTH = 6          # depth cap for the worktree mtime walk
WALK_MAX_ENTRIES = 20000    # hard ceiling on visited entries (bounded walk)
AGENT_COL_CAP = 46          # display cap for long worktree names in text mode
PANE_CAPTURE_LINES = 40     # tail length for -S capture in hash/evidence mode
TMUX_TIMEOUT_SECS = 10
PS_TIMEOUT_SECS = 10

EXCLUDED_WALK_DIRS = {".git"}          # Bug-A: global git churn is not activity
SHELL_COMM_NAMES = {"bash", "sh", "zsh", "dash", "fish", "ksh"}
READ_ONLY_ROLES = {"reviewer", "auditor", "orchestrator"}  # #434 sentinel-blocked
ROLE_RE = re.compile(r"--agent\s+'?([A-Za-z][A-Za-z0-9_-]*)'")
IDLE_SHELL_TAIL_RE = re.compile(r"[@\w:~/-]+[$#]\s*$")

# Verdict severity for one-glance sorting (lower = needs attention sooner).
VERDICT_SEVERITY = {
    "DEAD-UNMARKED": 0,
    "LIKELY-FROZEN": 1,
    "FINISHED-UNMARKABLE": 2,
    "STALE-SUSPECT": 3,
    "RUNNING-ALIVE": 4,
    "DONE-CONFIRMED": 5,
}


def iso(ts: float | None) -> str | None:
    """Epoch seconds -> ISO-8601 UTC string (or None)."""
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


# --------------------------------------------------------------------------
# Discovery and activity signals (all read-only)
# --------------------------------------------------------------------------

def discover_agents(root: str) -> list[tuple[str, str]]:
    """Return sorted (name, path) for <root>/*/ containing .kickoff-metadata.json."""
    agents = []
    try:
        entries = sorted(os.listdir(root))
    except OSError as exc:
        sys.stderr.write(f"agent-liveness: cannot list root {root}: {exc}\n")
        return agents
    for name in entries:
        wt = os.path.join(root, name)
        if os.path.isfile(os.path.join(wt, ".kickoff-metadata.json")):
            agents.append((name, wt))
    return agents


def read_status(wt: str) -> str:
    """Sentinel content, uppercased; 'ABSENT' when missing or empty."""
    try:
        with open(os.path.join(wt, ".kickoff-status"), encoding="utf-8") as fh:
            content = fh.read().strip().upper()
    except OSError:
        return "ABSENT"
    return content or "ABSENT"


def walk_max_mtime(top: str, max_depth: int = WALK_MAX_DEPTH,
                   max_entries: int = WALK_MAX_ENTRIES) -> float | None:
    """Newest mtime of regular files under top, excluding .git directories.

    Bounded twice: recursion depth <= max_depth AND total visited entries <=
    max_entries (whichever hits first ends the walk). Symlinks are never
    followed (no escapes, no loops). Errors ignored on individual entries:
    best-effort heuristic by design. Returns None when no file was seen.
    """
    best: float | None = None
    visited = 0

    def rec(directory: str, depth: int) -> None:
        nonlocal best, visited
        if visited >= max_entries:
            return
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if visited >= max_entries:
                        return
                    visited += 1
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_file(follow_symlinks=False):
                            mtime = entry.stat().st_mtime
                            if best is None or mtime > best:
                                best = mtime
                        elif (entry.is_dir(follow_symlinks=False)
                              and depth < max_depth
                              and entry.name not in EXCLUDED_WALK_DIRS):
                            rec(entry.path, depth + 1)
                    except OSError:
                        continue
        except OSError:
            pass

    rec(top, 1)
    return best


def baseline_mtime(wt: str) -> float | None:
    """Checkout-time fallback: newest of metadata started_at / root dir mtime."""
    candidates: list[float] = []
    try:
        candidates.append(os.stat(wt).st_mtime)
    except OSError:
        pass
    meta_path = os.path.join(wt, ".kickoff-metadata.json")
    try:
        with open(meta_path, encoding="utf-8") as fh:
            started_at = json.load(fh).get("started_at")
        if isinstance(started_at, str):
            candidates.append(
                datetime.fromisoformat(started_at).timestamp())
    except (OSError, ValueError, TypeError):
        pass
    return max(candidates) if candidates else None


def collect_activity(wt: str) -> tuple[float | None, str]:
    """(last_activity_epoch, source) with source in {'walk', 'baseline'}."""
    walked = walk_max_mtime(wt)
    if walked is not None:
        return walked, "walk"
    base = baseline_mtime(wt)
    if base is not None:
        return base, "baseline"
    return None, "none"


# --------------------------------------------------------------------------
# Process aliveness probe (read-only tmux + ps)
# --------------------------------------------------------------------------

def _run(cmd: list[str], timeout: int) -> tuple[int, str, str | None]:
    """Run a read-only external command; stderr collapsed to first line."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout)
    except FileNotFoundError:
        return 127, "", "binary not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
    err = (proc.stderr or "").strip().splitlines()
    return proc.returncode, proc.stdout, (err[0] if err else None)


def probe_session(session: str) -> dict:
    """Classify session aliveness: ALIVE / EXITED / SESSION-GONE (+evidence).

    EXITED means the agent process is gone although tmux may still hold the
    session: either every pane reports #{pane_dead}=1, or the process tree
    under each pane pid contains nothing but shell processes (idle prompt).
    """
    rc, out, err = _run(
        ["tmux", "list-panes", "-t", session,
         "-F", "#{pane_dead}\t#{pane_pid}\t#{pane_current_command}"],
        TMUX_TIMEOUT_SECS)
    if rc != 0:
        return {"state": "SESSION-GONE",
                "detail": err or "tmux reported no such session"}

    panes = [line.split("\t") for line in out.splitlines() if line.strip()]
    if not panes:
        return {"state": "SESSION-GONE", "detail": "session has no panes"}

    procs = _process_table()
    alive_panes, dead_panes = [], []
    for dead_flag, pid_str, command in panes:
        pid = int(pid_str) if pid_str.isdigit() else None
        if dead_flag == "1":
            dead_panes.append({"pid": pid, "command": command})
            continue
        non_shell = _non_shell_descendants(pid, procs) if pid else []
        if non_shell:
            alive_panes.append({
                "pid": pid, "command": command,
                "live_descendants": sorted(non_shell)[:8],
            })
        else:
            dead_panes.append({"pid": pid, "command": command,
                               "reason": "only shell processes remain"})

    if alive_panes:
        return {"state": "ALIVE", "panes_alive": alive_panes,
                "panes_dead": dead_panes}
    return {"state": "EXITED", "panes_alive": [], "panes_dead": dead_panes}


def _process_table() -> dict[int, tuple[int, str]]:
    """Snapshot of {pid: (ppid, comm)} from ps; empty map if ps unavailable."""
    rc, out, _ = _run(["ps", "-eo", "pid=,ppid=,comm="], PS_TIMEOUT_SECS)
    table: dict[int, tuple[int, str]] = {}
    if rc != 0:
        return table
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) != 3:
            continue
        pid_s, ppid_s, comm = parts
        if pid_s.isdigit() and ppid_s.isdigit():
            table[int(pid_s)] = (int(ppid_s), comm.strip())
    return table


def _non_shell_descendants(root_pid: int | None,
                           procs: dict[int, tuple[int, str]]) -> set[str]:
    """comm names of descendants of root_pid that are not plain shells."""
    found: set[str] = set()
    if root_pid is None:
        return found
    children: dict[int, list[int]] = {}
    for pid, (ppid, _comm) in procs.items():
        children.setdefault(ppid, []).append(pid)
    stack = list(children.get(root_pid, []))
    while stack:
        pid = stack.pop()
        comm = procs.get(pid, (0, ""))[1]
        base = os.path.basename(comm)
        if base and base not in SHELL_COMM_NAMES:
            found.add(base)
        stack.extend(children.get(pid, []))
    return found


def role_from_scrollback(session: str) -> tuple[str | None, bool]:
    """(role, idle_shell_hint) from full scrollback, or (None, hint).

    The launch command (`... claude --agent 'builder' ...`) stays in tmux
    history after the agent exits, so the role remains recoverable while the
    session exists. idle_shell_hint=True when the last non-blank captured
    line looks like an idle shell prompt (corroborating EXITED evidence).
    """
    rc, out, _ = _run(["tmux", "capture-pane", "-p", "-S", "-", "-t", session],
                      TMUX_TIMEOUT_SECS)
    role = None
    idle_hint = False
    if rc == 0:
        match = ROLE_RE.search(out)
        if match:
            role = match.group(1).lower()
        tail_lines = [ln.rstrip() for ln in out.splitlines() if ln.strip()]
        if tail_lines and IDLE_SHELL_TAIL_RE.search(tail_lines[-1]):
            idle_hint = True
    return role, idle_hint


def capture_pane_hash(session: str) -> tuple[str | None, str | None]:
    """sha256 of the pane tail (`capture-pane -p -S -40`), or (None, reason)."""
    cmd = ["tmux", "capture-pane", "-p",
           "-S", f"-{PANE_CAPTURE_LINES}", "-t", session]
    rc, out, err = _run(cmd, TMUX_TIMEOUT_SECS)
    if rc != 0:
        return None, err or "capture failed"
    return hashlib.sha256(out.encode("utf-8", "replace")).hexdigest(), None


# --------------------------------------------------------------------------
# Pane-hash state (the ONLY thing this tool writes, always under --state-dir)
# --------------------------------------------------------------------------

def load_state(state_dir: str) -> dict:
    path = os.path.join(state_dir, STATE_FILENAME)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(state_dir: str, panes: dict) -> str | None:
    """Persist pane hashes; returns error string on failure (never raises)."""
    path = os.path.join(state_dir, STATE_FILENAME)
    try:
        os.makedirs(state_dir, exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump({"version": 2, "panes": panes}, fh, indent=2,
                      sort_keys=True)
        os.replace(tmp_path, path)
        return None
    except OSError as exc:
        return f"cannot write {path}: {exc}"


# --------------------------------------------------------------------------
# Verdict matrix
# --------------------------------------------------------------------------

def classify(status: str, aliveness: str, age_min: float,
             role: str | None, pane_frozen: bool | None,
             budget_min: float) -> str:
    """Cross-signal verdict matrix — see module docstring for the full table."""
    if status == "DONE":
        return "DONE-CONFIRMED"
    if aliveness in ("SESSION-GONE", "EXITED"):
        if role in READ_ONLY_ROLES:
            return "FINISHED-UNMARKABLE"
        return "DEAD-UNMARKED"
    # ALIVE below here.
    if pane_frozen:
        return "LIKELY-FROZEN"
    if age_min < 2.0 * budget_min:
        return "RUNNING-ALIVE"
    return "STALE-SUSPECT"


def truncate(name: str, cap: int = AGENT_COL_CAP) -> str:
    return name if len(name) <= cap else name[: cap - 1] + "\u2026"


def render_table(rows: list[dict]) -> str:
    headers = ("AGENT", "STATUS", "ALIVENESS", "AGE_MIN", "SRC", "ROLE",
               "VERDICT")
    agent_w = max([len(truncate(r["agent"])) for r in rows]
                  + [len(headers[0])])
    widths = [
        max([len(r["status"]) for r in rows] + [len(headers[1])]),
        max([len(r["aliveness"]) for r in rows] + [len(headers[2])]),
        max([len(headers[3])]),
        max([len(r["source"]) for r in rows] + [len(headers[4])]),
        max([len(r["role"]) for r in rows] + [len(headers[5])]),
        max([len(r["verdict"]) for r in rows] + [len(headers[6])]),
    ]
    lines = [
        f"{headers[0]:<{agent_w}}  {headers[1]:<{widths[0]}}  "
        f"{headers[2]:<{widths[1]}}  {headers[3]:>{widths[2]}}  "
        f"{headers[4]:<{widths[3]}}  {headers[5]:<{widths[4]}}  {headers[6]}",
        (f"{'-' * agent_w}  {'-' * widths[0]}  {'-' * widths[1]}  "
         f"{'-' * widths[2]}  {'-' * widths[3]}  {'-' * widths[4]}  "
         f"{'-' * widths[5]}"),
    ]
    for r in rows:
        lines.append(
            f"{truncate(r['agent']):<{agent_w}}  {r['status']:<{widths[0]}}  "
            f"{r['aliveness']:<{widths[1]}}  {r['age_min']:>{widths[2]},.1f}  "
            f"{r['source']:<{widths[3]}}  {r['role']:<{widths[4]}}  "
            f"{r['verdict']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-liveness.py",
        description="Read-only liveness dashboard for kickoff agents (EPIC "
                    "#423, v2 per #435). Cross-checks sentinels against tmux "
                    "process aliveness and .git-free filesystem activity. "
                    "Writes only its pane-hash state file.",
        epilog="Verdict matrix: DONE-CONFIRMED (explicit DONE); RUNNING-ALIVE "
               "(alive+fresh); STALE-SUSPECT (alive+quiet >=2x budget); "
               "FINISHED-UNMARKABLE (gone/exited + read-only role, #434); "
               "DEAD-UNMARKED (gone/exited + RUNNING sentinel, zombie class); "
               "LIKELY-FROZEN (identical pane hashes across runs).")
    p.add_argument("--root", default=DEFAULT_ROOT,
                   help=f"worktrees root to scan (default: {DEFAULT_ROOT})")
    p.add_argument("--budget-min", type=float, default=45.0, metavar="MIN",
                   help="expected silence budget in minutes (default: 45)")
    p.add_argument("--pane", action="append", default=[], metavar="AGENT",
                   help="enable tmux pane-hash freeze detection for this "
                        "agent name (repeatable)")
    p.add_argument("--all", action="store_true",
                   help="run pane-hash comparison across every ALIVE session "
                        "in one pass (supersedes --pane selection)")
    p.add_argument("--state-dir", default=DEFAULT_STATE_DIR, metavar="DIR",
                   help=f"directory for the pane-hash state file "
                        f"(default: {DEFAULT_STATE_DIR}; the only write "
                        f"target)")
    p.add_argument("--json", action="store_true",
                   help="emit machine-readable JSON instead of a table")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    now = time.time()

    prior_state = load_state(args.state_dir)
    prior_panes = prior_state.get("panes", {})
    new_panes: dict = {}
    rows: list[dict] = []
    skipped: list[str] = []

    for name, wt in discover_agents(args.root):
        status = read_status(wt)
        last_activity, source = collect_activity(wt)
        if last_activity is None:
            skipped.append(name)  # no walkable files AND no baseline at all
            continue
        age_min = max(0.0, (now - last_activity) / 60.0)

        probe = probe_session(name)
        aliveness = probe["state"]

        role: str | None = None
        idle_hint: bool | None = None
        if aliveness != "SESSION-GONE":
            role, idle_hint = role_from_scrollback(name)

        # Pane hashing: --all covers every alive session; --pane names are
        # honoured additionally (so an exited-but-present session can still
        # be hashed on explicit request).
        want_hash = args.all and aliveness == "ALIVE" or name in args.pane
        pane_frozen: bool | None = None
        pane_note: str | None = None
        pane_hash: str | None = None
        if want_hash:
            digest, err = capture_pane_hash(name)
            pane_hash = digest
            if digest is None:
                pane_note = err
            else:
                prev = prior_panes.get(name)
                new_panes[name] = {"hash": digest, "captured_at": iso(now)}
                if prev is None:
                    pane_note = "first observation (frozen check needs 2 runs)"
                elif prev.get("hash") == digest:
                    pane_frozen = True
                else:
                    pane_frozen = False
                    pane_note = "pane changed since previous run"

        verdict = classify(status, aliveness, age_min, role, pane_frozen,
                           args.budget_min)

        row = {
            "agent": name,
            "status": status,
            "aliveness": aliveness,
            "age_min": round(age_min, 1),
            "source": source,
            "role": role or "unknown",
            "verdict": verdict,
            "last_activity": iso(last_activity),
            "budget_min": args.budget_min,
            "probe": probe,
        }
        if idle_hint is not None:
            row["idle_shell_tail_hint"] = idle_hint
        if want_hash:
            row["pane_frozen"] = pane_frozen
            row["pane_hash"] = pane_hash
        if pane_note is not None:
            row["pane"] = pane_note
        rows.append(row)

    state_error = None
    if new_panes:
        state_error = save_state(args.state_dir, new_panes)

    # One-glance question is "what needs attention": severity rank first,
    # newest-activity-first within each severity class.
    rows.sort(key=lambda r: (VERDICT_SEVERITY.get(r["verdict"], 99),
                             r["age_min"]))

    if args.json:
        payload = {
            "generated_at": iso(now),
            "root": args.root,
            "budget_min": args.budget_min,
            "state_dir": args.state_dir,
            "agents": rows,
            "skipped_no_signal": skipped,
        }
        if state_error:
            payload["state_error"] = state_error
        print(json.dumps(payload, indent=2))
    else:
        if rows:
            print(render_table(rows))
        else:
            print("no kickoff agents discovered")
        if skipped:
            print(f"(skipped, no activity signal: {', '.join(skipped)})",
                  file=sys.stderr)
        if state_error:
            print(f"agent-liveness: {state_error}", file=sys.stderr)
        if args.all or args.pane:
            print(f"pane-hash state: {os.path.join(args.state_dir, STATE_FILENAME)} "
                  f"(identical hashes across 2 runs => LIKELY-FROZEN)",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
