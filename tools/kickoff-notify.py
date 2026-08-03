#!/usr/bin/env python3
"""ASES kickoff agent lifecycle watcher — Phase 1 (monitor + notify only).

Watches the ASES worktrees directory for kickoff agents and reports lifecycle
state transitions to the operator. Phase 1 is strictly OBSERVATION +
NOTIFICATION: it never kills, relaunches, or otherwise mutates agents.

Signals read per agent (worktree directory):

  .kickoff-status                 LAUNCHING / RUNNING / DONE / FAILED /
                                  CI_FAILED (terminal states: DONE, FAILED,
                                  CI_FAILED).
  .kickoff-metadata.json          {started_at: ISO-8601, timeout_secs: int}.
  .crosslink/.cache/last-heartbeat
                                  PRIMARY liveness signal (mtime = last
                                  heartbeat). Written by the PostToolUse
                                  heartbeat.py hook, throttled to 120s.

State machine per agent:
  LAUNCHING -> RUNNING -> DONE | FAILED | CI_FAILED
  RUNNING/LAUNCHING -> STALLED   (heartbeat stale past threshold, detected on
                                  2 consecutive scans, outside grace period)

Notifications (desktop notify-send + optional webhook POST):
  DONE      -> COMPLETED
  STALLED   -> STALLED alert (NO kill/relaunch in Phase 1)
  FAILED    -> FAILED
  CI_FAILED -> CI_FAILED

Missing heartbeat is handled conservatively: if the heartbeat file does not
exist (the hook is not currently installed in worktrees — a Phase 2 item), the
watcher does NOT declare STALLED from absence alone. It falls back to a
timeout-overrun signal (elapsed > timeout_secs + buffer with a non-terminal
status), which is the "timeout exceeded = likely stalled" primary signal from
playbook §5.3.

State is persisted to a JSON state file (default
~/.local/state/ases-kickoff-notify/state.json) so transitions are idempotent
across watcher restarts: a terminal state that was already notified is not
re-notified, and the consecutive-stale debounce counter survives restarts.

Usage:
  python3 tools/kickoff-notify.py --once --dry-run   # single scan, no side effects
  python3 tools/kickoff-notify.py --once             # single scan, notify on transitions
  python3 tools/kickoff-notify.py                    # loop forever (systemd timer uses --once)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------

DEFAULT_WORKTREES_DIR = "/home/claude-code/projects/ASES/.worktrees"
DEFAULT_STATE_FILE = os.path.expanduser(
    "~/.local/state/ases-kickoff-notify/state.json"
)
DEFAULT_INTERVAL_SECS = 20
DEFAULT_GRACE_SECS = 300          # mirror crosslink watchdog's 300s grace
DEFAULT_STALL_AFTER_SECS = 900    # floor; scaled by timeout_secs, see below
DEFAULT_METADATA_TIMEOUT_SECS = 1800
OVERRUN_BUFFER_SECS = 120         # tolerance past timeout_secs before overrun stall
DEBOUNCE_DETECTIONS = 2           # consecutive scans with stale signal required

TERMINAL_STATES = ("DONE", "FAILED", "CI_FAILED")
NON_TERMINAL_STATES = ("LAUNCHING", "RUNNING")


# ---------------------------------------------------------------------------
# Signal readers
# ---------------------------------------------------------------------------

def read_status(worktree: Path) -> str | None:
    """Return the .kickoff-status content (stripped) or None if absent."""
    status_file = worktree / ".kickoff-status"
    try:
        content = status_file.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except OSError:
        return None
    return content or None


def read_metadata(worktree: Path) -> dict:
    """Return parsed .kickoff-metadata.json or an empty dict."""
    meta_file = worktree / ".kickoff-metadata.json"
    try:
        return json.loads(meta_file.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}


def parse_started_at(meta: dict) -> float | None:
    """Parse started_at (ISO-8601, may end in Z or +00:00) to epoch seconds.

    Python 3.10's datetime.fromisoformat rejects >6-digit fractional seconds
    (crosslink writes 9-digit precision), so normalize the fraction first.
    """
    raw = meta.get("started_at")
    if not raw:
        return None
    text = str(raw).replace("Z", "+00:00")
    # Truncate the fractional part to 6 digits (microseconds).
    if "." in text:
        head, _, tail = text.partition(".")
        frac = tail[:6]
        text = f"{head}.{frac}"
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except (ValueError, TypeError):
        return None


def heartbeat_age(worktree: Path) -> float | None:
    """Return age in seconds of .crosslink/.cache/last-heartbeat, or None if
    the file does not exist (signal unavailable)."""
    hb = worktree / ".crosslink" / ".cache" / "last-heartbeat"
    try:
        return time.time() - hb.stat().st_mtime
    except (FileNotFoundError, OSError):
        return None


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def load_state(state_file: str) -> dict:
    """Load persisted per-agent state. Returns {} on first run or corruption."""
    try:
        with open(state_file, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        pass
    return {}


def save_state(state_file: str, state: dict) -> None:
    """Atomically persist state (write temp, rename) to avoid corruption."""
    path = Path(state_file)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, path)
    except OSError as exc:
        print(f"[{ts()}] WARN: failed to persist state to {state_file}: {exc}",
              file=sys.stderr)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def notify_desktop(message: str, urgent: bool = False) -> bool:
    """Send a desktop notification via notify-send. Returns False if
    notify-send is unavailable (libnotify-bin not installed — see #133)."""
    exe = shutil.which("notify-send")
    if exe is None:
        print(f"[{ts()}] WARN: notify-send not found; skipping desktop "
              f"notification: {message}", file=sys.stderr)
        return False
    urgency = "critical" if urgent else "normal"
    cmd = [exe, "-u", urgency, "ASES kickoff watcher", message]
    try:
        subprocess.run(cmd, check=True, timeout=10,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.SubprocessError, OSError) as exc:
        print(f"[{ts()}] WARN: notify-send failed: {exc}", file=sys.stderr)
        return False


def notify_webhook(webhook: str | None, event: str, payload: dict) -> None:
    """POST the notification payload to the configured webhook (if any)."""
    if not webhook:
        return
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        webhook, data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
        print(f"[{ts()}] webhook {event} -> {webhook} (HTTP {resp.status})")
    except (urllib.error.URLError, OSError) as exc:
        print(f"[{ts()}] WARN: webhook POST failed for {event}: {exc}",
              file=sys.stderr)


# ---------------------------------------------------------------------------
# Per-agent observation
# ---------------------------------------------------------------------------

def observe_agent(worktree: Path, stall_after_secs: int,
                  grace_secs: int) -> dict:
    """Collect the raw signals for one worktree.

    Returns a dict with keys: worktree, slug, status, started_at, timeout_secs,
    heartbeat_age, elapsed, heartbeat_missing, stall_candidate (bool)."""
    status = read_status(worktree)
    if status is None:
        return {}
    meta = read_metadata(worktree)
    started_at = parse_started_at(meta)
    timeout_secs = int(meta.get("timeout_secs") or DEFAULT_METADATA_TIMEOUT_SECS)
    now = time.time()
    elapsed = now - started_at if started_at is not None else None

    hb_age = heartbeat_age(worktree)
    heartbeat_missing = hb_age is None

    # Stall threshold scales with task size but never below the floor.
    threshold = max(stall_after_secs, timeout_secs // 2)

    # A stall is a stale heartbeat (primary) or a timeout overrun (fallback
    # when heartbeat signal is unavailable).
    stall_candidate = False
    if status in NON_TERMINAL_STATES:
        past_grace = (elapsed is not None and elapsed >= grace_secs)
        if past_grace:
            if hb_age is not None and hb_age > threshold:
                stall_candidate = True
            elif heartbeat_missing and elapsed is not None \
                    and elapsed > timeout_secs + OVERRUN_BUFFER_SECS:
                # No heartbeat signal at all (hook not installed) and the
                # agent has blown past its full task budget with a
                # non-terminal status -> likely stalled/overrun.
                stall_candidate = True

    return {
        "worktree": str(worktree),
        "slug": worktree.name,
        "status": status,
        "started_at": started_at,
        "timeout_secs": timeout_secs,
        "heartbeat_age": hb_age,
        "heartbeat_missing": heartbeat_missing,
        "elapsed": elapsed,
        "stall_candidate": stall_candidate,
    }


def build_message(event: str, obs: dict, elapsed_fmt: str) -> str:
    slug = obs["slug"]
    if event == "COMPLETED":
        return f"Agent completed: {slug} ({elapsed_fmt})"
    if event == "STALLED":
        if obs["heartbeat_age"] is not None:
            detail = f"no heartbeat for {int(obs['heartbeat_age'])}s"
        else:
            detail = "past task timeout with no terminal status"
        return f"Agent STALLED: {slug} — {detail} (investigate; no auto-recovery in Phase 1)"
    if event == "FAILED":
        return f"Agent failed: {slug} ({elapsed_fmt})"
    if event == "CI_FAILED":
        return f"Agent CI_FAILED: {slug} ({elapsed_fmt})"
    return f"Agent {slug}: {event}"


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------

def scan_once(worktrees_dir: str, state_file: str, webhook: str | None,
              stall_after_secs: int, grace_secs: int, dry_run: bool,
              verbose: bool) -> int:
    """Run one scan pass over the worktrees directory.

    Returns 0 on success. In dry-run mode, reports what WOULD happen without
    writing state or sending notifications.
    """
    root = Path(worktrees_dir)
    if not root.is_dir():
        print(f"[{ts()}] ERROR: worktrees dir not found: {root}", file=sys.stderr)
        return 1

    state = {} if dry_run else load_state(state_file)
    now = time.time()

    # Discover agent worktrees (dirs containing .kickoff-status).
    agents = {}
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        obs = observe_agent(entry, stall_after_secs, grace_secs)
        if obs:
            agents[obs["slug"]] = obs

    print(f"[{ts()}] scan: {len(agents)} agent(s) in {root}")

    for slug, obs in sorted(agents.items()):
        rec = state.get(slug, {})
        prev_state = rec.get("state")
        consecutive_stale = int(rec.get("consecutive_stale", 0))
        notified = set(rec.get("notified", []))
        status = obs["status"]

        # Resolve the new state for this agent.
        new_state = status
        if status in NON_TERMINAL_STATES and obs["stall_candidate"]:
            consecutive_stale += 1
            if consecutive_stale >= DEBOUNCE_DETECTIONS:
                new_state = "STALLED"
        else:
            consecutive_stale = 0

        elapsed_fmt = "?"
        if obs["elapsed"] is not None:
            elapsed_fmt = f"{int(obs['elapsed'] // 60)}m{int(obs['elapsed'] % 60)}s"

        hb_desc = "missing" if obs["heartbeat_missing"] else \
            f"{int(obs['heartbeat_age'])}s old"
        print(f"  {slug}: status={status} state={new_state} "
              f"(prev={prev_state}) heartbeat={hb_desc} elapsed={elapsed_fmt}")

        # Determine transition events.
        events = []
        if new_state == "DONE" and "COMPLETED" not in notified:
            events.append("COMPLETED")
        elif new_state == "FAILED" and "FAILED" not in notified:
            events.append("FAILED")
        elif new_state == "CI_FAILED" and "CI_FAILED" not in notified:
            events.append("CI_FAILED")
        elif new_state == "STALLED" and "STALLED" not in notified \
                and prev_state != "STALLED":
            events.append("STALLED")

        if verbose:
            for ev in events:
                print(f"    -> would notify {ev}: {build_message(ev, obs, elapsed_fmt)}")

        if not dry_run and events:
            payload_base = {
                "event": events[0],
                "agent": slug,
                "worktree": obs["worktree"],
                "status": status,
                "message": build_message(events[0], obs, elapsed_fmt),
                "started_at": obs["started_at"],
                "timeout_secs": obs["timeout_secs"],
                "elapsed_secs": int(obs["elapsed"]) if obs["elapsed"] is not None else None,
                "timestamp": now,
            }
            for ev in events:
                urgent = ev in ("STALLED", "FAILED", "CI_FAILED")
                notify_desktop(build_message(ev, obs, elapsed_fmt), urgent=urgent)
                notify_webhook(webhook, ev, {**payload_base, "event": ev})
            notified.update(events)

        # Persist the record. If the agent recovered from STALLED (heartbeat
        # fresh again / terminal status), drop the STALLED notification flag
        # so a FUTURE stall re-alerts the operator instead of being silently
        # deduped for the rest of the watcher's lifetime.
        if prev_state == "STALLED" and new_state != "STALLED":
            notified.discard("STALLED")
        state[slug] = {
            "state": new_state,
            "consecutive_stale": consecutive_stale,
            "notified": sorted(notified),
            "first_seen": rec.get("first_seen", now),
            "last_seen": now,
            "timeout_secs": obs["timeout_secs"],
        }

    # Drop agents whose worktrees disappeared (cleanup) — report, don't notify.
    for slug in list(state.keys()):
        if slug not in agents:
            if verbose:
                print(f"  {slug}: worktree gone — dropping from state")
            del state[slug]

    if not dry_run:
        save_state(state_file, state)
    else:
        print(f"[{ts()}] dry-run: state/notifications NOT persisted "
              f"(no side effects)")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ASES kickoff agent lifecycle watcher — Phase 1 "
                    "(monitor + notify only; no kill/relaunch)."
    )
    parser.add_argument("--once", action="store_true",
                        help="run a single scan pass and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what WOULD happen; no state writes, no "
                             "notifications, no webhook POSTs")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECS,
                        help=f"seconds between scans (default {DEFAULT_INTERVAL_SECS})")
    parser.add_argument("--worktrees-dir", default=DEFAULT_WORKTREES_DIR,
                        help=f"worktrees root to scan (default {DEFAULT_WORKTREES_DIR})")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE,
                        help=f"state file path (default {DEFAULT_STATE_FILE})")
    parser.add_argument("--webhook",
                        default=os.environ.get("KICKOFF_NOTIFY_WEBHOOK"),
                        help="webhook URL for notification POSTs "
                             "(default: $KICKOFF_NOTIFY_WEBHOOK)")
    parser.add_argument("--stall-after", type=int, default=DEFAULT_STALL_AFTER_SECS,
                        help=f"minimum heartbeat staleness (secs) before a "
                             f"stall candidate; scaled by task timeout_secs "
                             f"(default floor {DEFAULT_STALL_AFTER_SECS})")
    parser.add_argument("--grace", type=int, default=DEFAULT_GRACE_SECS,
                        help=f"grace period after launch before stall "
                             f"evaluation (default {DEFAULT_GRACE_SECS})")
    parser.add_argument("--verbose", action="store_true",
                        help="print per-agent detail and would-notify lines")
    args = parser.parse_args()

    if args.interval < 1:
        print("ERROR: --interval must be >= 1", file=sys.stderr)
        return 2

    while True:
        rc = scan_once(
            worktrees_dir=args.worktrees_dir,
            state_file=args.state_file,
            webhook=args.webhook,
            stall_after_secs=args.stall_after,
            grace_secs=args.grace,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
        if rc != 0 or args.once:
            return rc
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
