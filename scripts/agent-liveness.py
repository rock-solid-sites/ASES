#!/usr/bin/env python3
"""
agent-liveness.py — read-only one-glance staleness dashboard for running
kickoff agents (EPIC #423 liveness workstream).

Discovers kickoff agents from ``<root>/*/.kickoff-metadata.json`` (default root:
``/home/claude-code/projects/ASES/.worktrees``), reads each agent's lifecycle
sentinel (``.kickoff-status``: DONE / RUNNING / absent), estimates how long
since the agent last did *anything observable*, and renders a verdict table.

DESIGN NOTE — why "old + no DONE" is not "confirmed done" (#434):
    DONE-marker writes are blocked for read-only agent roles (issue #434), so a
    finished-but-never-marked agent is indistinguishable from an agent that was
    killed mid-flight: in both cases the sentinel is absent and activity stops.
    This tool therefore treats *absent sentinel + old activity* as
    STALE-SUSPECT / LIKELY-FROZEN — never as confirmed-done. Only an explicit
    DONE sentinel counts as completed. The verdict vocabulary is deliberately
    suspicion-shaped ("SUSPECT", "LIKELY") because every signal here is
    heuristic; the human orchestrator decides.

Activity signals per agent (last_activity = NEWEST of):
    status  — mtime of the worktree's .kickoff-status file;
    reflog  — newest file mtime under the worktree gitdir's logs/ (reflog),
              located via the worktree's ".git: gitdir:" pointer file;
    walk    — approximate tracked-file activity: max mtime over an os.walk of
              the worktree capped at depth 3 (cheap proxy for "files changed
              since checkout"; blessed approximation, not exact git tracking).
If none of these exist the agent is skipped (reported on stderr).

Pane-hash freeze detection (--pane NAME, repeatable):
    For each named agent, if a tmux session of the same name exists, capture
    its pane (`tmux capture-pane -p -S -40`), sha256 it, and store the hash in
    a state file under --state-dir. If two consecutive runs record identical
    hashes, nothing on that pane has changed between runs → LIKELY-FROZEN
    regardless of age. The FIRST observation can never conclude frozenness
    (one sample, no delta). State is written ONLY inside --state-dir.

Verdicts (age measured against --budget-min, default 45 min):
    ok            age <  2x budget silence
    STALE-SUSPECT 2x <= age <= 4x budget silence
    LIKELY-FROZEN age > 4x budget silence, OR identical pane hashes across runs

Usage:
    python3 scripts/agent-liveness.py                     # dashboard table
    python3 scripts/agent-liveness.py --budget-min 30     # override silence budget
    python3 scripts/agent-liveness.py --pane pp3g-rChm-relaunch-of-429-research-after-frozen-predecessor-see
    python3 scripts/agent-liveness.py --json              # machine-readable
    python3 scripts/agent-liveness.py --help

Constraints: reads only; writes ONLY the pane-hash state file inside
--state-dir (default /tmp/opencode/liveness-state/). Never modifies any agent
state, never invokes git, never touches tmux except capture-pane.

Dependencies: Python 3 stdlib only (argparse, hashlib, json, os, subprocess,
sys, time, datetime).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

DEFAULT_ROOT = "/home/claude-code/projects/ASES/.worktrees"
DEFAULT_STATE_DIR = "/tmp/opencode/liveness-state"
STATE_FILENAME = "pane-hashes.json"
WALK_MAX_DEPTH = 3          # depth cap for the worktree mtime walk (see docstring)
AGENT_COL_CAP = 52          # display cap for long worktree names in text mode
PANE_CAPTURE_LINES = 40     # matches `-S -40`
TMUX_TIMEOUT_SECS = 10


def iso(ts: float | None) -> str | None:
    """Epoch seconds -> ISO-8601 UTC string (or None)."""
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


# --------------------------------------------------------------------------
# Discovery and signal collection (all read-only)
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


def walk_max_mtime(top: str, max_depth: int = WALK_MAX_DEPTH) -> float | None:
    """Max mtime of regular files under top, recursing at most max_depth levels.

    Symlinks are never followed (no escapes, no loops). Errors ignored: this is
    a best-effort heuristic signal by design.
    """
    best: float | None = None

    def rec(directory: str, depth: int) -> None:
        nonlocal best
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_file(follow_symlinks=False):
                            mtime = entry.stat().st_mtime
                            if best is None or mtime > best:
                                best = mtime
                        elif entry.is_dir(follow_symlinks=False) and depth < max_depth:
                            rec(entry.path, depth + 1)
                    except OSError:
                        continue
        except OSError:
            pass

    rec(top, 1)
    return best


def reflog_newest_mtime(wt: str) -> float | None:
    """Newest mtime under the worktree gitdir's logs/ via the .git pointer."""
    try:
        with open(os.path.join(wt, ".git"), encoding="utf-8") as fh:
            line = fh.read().strip()
    except OSError:
        return None
    if not line.startswith("gitdir:"):
        return None
    gitdir = line.split(":", 1)[1].strip()
    if not os.path.isabs(gitdir):
        gitdir = os.path.join(wt, gitdir)
    return walk_max_mtime(os.path.join(gitdir, "logs"), max_depth=WALK_MAX_DEPTH)


def collect_signals(wt: str) -> dict[str, float]:
    """All available activity signals: {'status'|'reflog'|'walk': mtime}."""
    signals: dict[str, float] = {}
    try:
        signals["status"] = os.stat(
            os.path.join(wt, ".kickoff-status")).st_mtime
    except OSError:
        pass
    reflog = reflog_newest_mtime(wt)
    if reflog is not None:
        signals["reflog"] = reflog
    walked = walk_max_mtime(wt)
    if walked is not None:
        signals["walk"] = walked
    return signals


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
            json.dump({"version": 1, "panes": panes}, fh, indent=2, sort_keys=True)
        os.replace(tmp_path, path)
        return None
    except OSError as exc:
        return f"cannot write {path}: {exc}"


def capture_pane_hash(session: str) -> tuple[str | None, str | None]:
    """sha256 of `tmux capture-pane -p -S -40 -t session`, or (None, reason)."""
    cmd = ["tmux", "capture-pane", "-p",
           "-S", f"-{PANE_CAPTURE_LINES}", "-t", session]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=TMUX_TIMEOUT_SECS)
    except FileNotFoundError:
        return None, "tmux binary not found"
    except subprocess.TimeoutExpired:
        return None, "tmux capture timed out"
    if proc.returncode != 0:
        first_err = (proc.stderr or "").strip().splitlines()
        return None, (first_err[0] if first_err else "capture failed")
    return hashlib.sha256(proc.stdout.encode("utf-8", "replace")).hexdigest(), None


# --------------------------------------------------------------------------
# Verdicts
# --------------------------------------------------------------------------

def classify(status: str, age_min: float, pane_frozen: bool | None,
             budget_min: float) -> str:
    """ok (<2x) / STALE-SUSPECT (2x-4x inclusive) / LIKELY-FROZEN (>4x or pane).

    DONE sentinels short-circuit to ok (explicit completion beats age math);
    ABSENT sentinels go through the same thresholds as RUNNING — see the #434
    design note in the module docstring.
    """
    if pane_frozen:
        return "LIKELY-FROZEN"
    if status == "DONE":
        return "ok"
    if age_min < 2.0 * budget_min:
        return "ok"
    if age_min <= 4.0 * budget_min:
        return "STALE-SUSPECT"
    return "LIKELY-FROZEN"


def truncate(name: str, cap: int = AGENT_COL_CAP) -> str:
    return name if len(name) <= cap else name[: cap - 1] + "\u2026"


def render_table(rows: list[dict]) -> str:
    headers = ("AGENT", "STATUS", "LAST_ACTIVITY_AGE_MIN", "SOURCE", "VERDICT")
    agent_w = max([len(truncate(r["agent"])) for r in rows] + [len(headers[0])])
    status_w = max([len(r["status"]) for r in rows] + [len(headers[1])])
    src_w = max([len(r["source"]) for r in rows] + [len(headers[3])])
    verd_w = max([len(r["verdict"]) for r in rows] + [len(headers[4])])
    lines = [
        f"{headers[0]:<{agent_w}}  {headers[1]:<{status_w}}  "
        f"{headers[2]:>21}  {headers[3]:<{src_w}}  {headers[4]}",
        f"{'-' * agent_w}  {'-' * status_w}  {'-' * 21}  {'-' * src_w}  {'-' * verd_w}",
    ]
    for r in rows:
        lines.append(
            f"{truncate(r['agent']):<{agent_w}}  {r['status']:<{status_w}}  "
            f"{r['age_min']:>21,.1f}  {r['source']:<{src_w}}  {r['verdict']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-liveness.py",
        description="Read-only staleness dashboard for running kickoff agents "
                    "(EPIC #423). Writes only its pane-hash state file.",
        epilog="Verdict thresholds: ok < 2x budget; STALE-SUSPECT 2x-4x; "
               "LIKELY-FROZEN >4x or identical pane hashes across runs.")
    p.add_argument("--root", default=DEFAULT_ROOT,
                   help=f"worktrees root to scan (default: {DEFAULT_ROOT})")
    p.add_argument("--budget-min", type=float, default=45.0, metavar="MIN",
                   help="expected silence budget in minutes (default: 45)")
    p.add_argument("--pane", action="append", default=[], metavar="AGENT",
                   help="enable tmux pane-hash freeze detection for this agent "
                        "name (repeatable); tmux session must share the name")
    p.add_argument("--state-dir", default=DEFAULT_STATE_DIR, metavar="DIR",
                   help=f"directory for the pane-hash state file "
                        f"(default: {DEFAULT_STATE_DIR}; the only write target)")
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
        signals = collect_signals(wt)
        if not signals:
            skipped.append(name)  # spec: skip when no signal exists at all
            continue
        source, last_activity = max(signals.items(), key=lambda kv: kv[1])
        age_min = max(0.0, (now - last_activity) / 60.0)

        pane_frozen: bool | None = None
        pane_note: str | None = None
        pane_hash: str | None = None
        if name in args.pane:
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

        row = {
            "agent": name,
            "status": status,
            "age_min": round(age_min, 1),
            "source": source,
            "verdict": classify(status, age_min, pane_frozen, args.budget_min),
            "last_activity": iso(last_activity),
            "signals": {k: iso(v) for k, v in sorted(signals.items())},
            "budget_min": args.budget_min,
        }
        if name in args.pane:
            # Always expose pane evidence in JSON, even when it changed nothing.
            row["pane_frozen"] = pane_frozen
            row["pane_hash"] = pane_hash
        if pane_note is not None:
            row["pane"] = pane_note
        rows.append(row)

    state_error = None
    if new_panes:
        state_error = save_state(args.state_dir, new_panes)

    # Most-stale first: the one-glance question is "what needs attention".
    rows.sort(key=lambda r: r["age_min"], reverse=True)

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
        if args.pane:
            print(f"pane-hash state: {os.path.join(args.state_dir, STATE_FILENAME)} "
                  f"(identical hashes across 2 runs => LIKELY-FROZEN)",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
