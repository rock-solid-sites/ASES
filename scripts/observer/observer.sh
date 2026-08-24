#!/usr/bin/env bash
#
# observer.sh — agentic per-agent supervision loop (EPIC #423; built per the
# consolidated dispatch spec on issue #460, 2026-08-24). Successor name to
# lifecycle-manager (#459/#442 rename decision: Observer = the mechanical
# pipeline). Extends the liveness-watchdog v2 monitoring posture into a
# supervisor that OWNS the post-transition response, per
# .design/lifecycle-manager-design.md.
#
# Relationship to the watchdog:
#   liveness-watchdog.sh detects verdict transitions and posts auditor flags.
#   observer.sh runs the SAME liveness scan (agent-liveness.py v2,
#   six-class verdict matrix, unchanged) and additionally EXECUTES scoped
#   responses per detected transition:
#
#     COMPLETED (DONE-CONFIRMED)
#       - crosslink kickoff cleanup --only <agent> --yes  (worktree + tmux)
#       - deliverable existence check on the agent branch vs main
#       - model-evidence row appended to the registry staging file
#     FINISHED-UNMARKABLE (read-only role finished without DONE marker)
#       - verify findings were posted on the working issue
#       - flag the worktree for operator force-sweep at wave end
#       - model-evidence row appended
#     FAILED (error exit, nonzero code)
#       - preserve worktree for forensics (never cleaned automatically)
#       - failure alert posted to the working issue with log-tail evidence
#       - recommend relaunch-with-backup-model to the orchestrator
#     KILLED (orchestrator stop signatures: SIGTERM/SIGKILL pane exit)
#       - immediate kickoff cleanup --only <agent> --yes
#       - verify no orphaned worktree remains (else force-sweep flag)
#       - termination record logged with evidence chain
#     PARKED (rate-limit signature in the agent log tail)
#       - do NOT kill (the agent is correctly waiting on quota)
#       - record resume_at parsed from retry-after evidence (or default window)
#       - reclassify as FROZEN if resume_at passes without activity
#       - alert only when multiple agents are parked simultaneously
#         (shared quota pool exhaustion signal, not individual failure)
#     FROZEN (LIKELY-FROZEN confirmed across >= 2 cycles, or STALE-SUSPECT
#             escalated after its one warning cycle, or PARKED expired)
#       - attach last-N-line opencode.log tail as diagnostic evidence bundle
#       - auto-kill per operator-granted spiral authority (#443 rev3,
#         granted 2026-08-24) via crosslink kickoff stop --force
#       - kickoff cleanup --only <agent> --yes
#       - termination record posted with sha256 evidence chain
#       - recommend relaunch-with-backup-model
#
#   Wave-level actions (beyond per-agent):
#     - main HEAD change (merge landed): report unpushed commit count and
#       suggest push when above threshold (#451 lint-the-command pattern).
#     - doctrine/knowledge file content change: reverse-edge dependent lookup
#       via frontmatter depends_on/related_documents/consumed_by, then run the
#       DIS existence-validator on each dependent document (#443/#459 spec).
#       An external validator supersedes the built-in checker via
#       OBSERVER_DIS_VALIDATOR when the DIS V1 script lands.
#
# Attribution mechanics:
#   Per-agent log evidence comes from the shared opencode.log, attributed by
#   the cwd=<...>.worktrees/<agent-slug> marker to recover session IDs, then
#   tailed per session. Model/provider identity comes from the last
#   llm.provider=/llm.model= pair in the attributed section.
#
# Evidence-at-transition (#460 F1):
#   EVERY terminal verdict (COMPLETED, FINISHED-UNMARKABLE, FAILED, KILLED,
#   FROZEN termination) composes a full evidence bundle AT DETECTION:
#   attributed opencode.log tail + pane tail + worktree git status/diffstat
#   + verdict timeline + last hub position ref (latest comment stamp/kind on
#   the working issue), all sha256-manifested, with a compact digest line
#   posted to the working issue. Failure documentation takes seconds, not
#   archaeology.
#
# Event-driven fast path (#456 revised scope; #460 F2):
#   A byte-offset cursor over opencode.log reads ONLY new bytes each cycle
#   (rotation/truncation safe, partial-line safe). New lines are classified:
#     AI_APICallError + retry-after        -> PARKED-RETRYING (tracked agents
#                                             enter PARKED same cycle)
#     AI_APICallError + consent/opt-in     -> CONSENT-GATE-FATAL (alert now;
#                                             accelerates STALE escalation)
#     AI_RetryError + exhausted            -> RETRY-EXHAUSTED-DEAD (alert now)
#     other AI_*Error                      -> UNKNOWN (flagged for review)
#   Alerts are deduped per (class, session) within
#   OBSERVER_FASTPATH_DEDUP_SECS. The expensive liveness walk keeps its own
#   slower cadence; detection of log-visible failures takes seconds.
#
# Commit-age signal (#460 F3):
#   Per-builder last-commit age (git log -1 %ct in the worktree) feeds the
#   STALE logic, making the incremental-commit discipline mechanical:
#     RUNNING-ALIVE + commit older than OBSERVER_COMMIT_STALE_MINS
#       -> deduped commit-overdue event (re-arms on fresh commit)
#     STALE-SUSPECT + stale commit  -> escalate on FIRST quiet cycle
#     STALE-SUSPECT + fresh commit  -> one extra grace cycle before
#                                      escalation
#
# Safety model:
#   - Never touches live agent processes or worktrees directly: every
#     mutation goes through crosslink CLI surfaces (kickoff stop/cleanup,
#     issue comment).
#   - All state lives under /tmp/opencode/observer-state/.
#   - Anti-loop protections: once-per-episode dedup per (agent, verdict),
#     a rolling-window circuit breaker capping mutating actions per hour,
#     and a consecutive-scan-failure cap that halts the loop rather than
#     looping destructively.
#   - OBSERVER_DRY_RUN=1 records every intended mutation (comments included)
#     in events.jsonl without executing it; OBSERVER_INPUT_JSON injects a
#     fixture liveness payload for deterministic testing.
#
# Deployment: intended to run inside a detached tmux session so it outlives
# the dispatching agent:
#   tmux new-session -d -s observer-mgr \
#     bash /home/claude-code/projects/ASES/scripts/observer/observer.sh
# Single-cycle invocation for testing:
#   OBSERVER_DRY_RUN=1 scripts/observer/observer.sh --once
#
# Shell: bash, stdlib tooling only (embedded python3 for JSON/state/actions).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Liveness scanner resolution: explicit override wins; then a sibling copy in
# this directory (self-contained deployment); then the repo scripts/ dir
# (canonical home of agent-liveness.py).
if [ -n "${OBSERVER_LIVENESS_PY:-}" ]; then
    LIVENESS_PY="$OBSERVER_LIVENESS_PY"
elif [ -f "$SCRIPT_DIR/agent-liveness.py" ]; then
    LIVENESS_PY="$SCRIPT_DIR/agent-liveness.py"
else
    LIVENESS_PY="$SCRIPT_DIR/../agent-liveness.py"
fi

# ---------------------------------------------------------------------------
# Configuration (environment-overridable; exported as OB_* for the embedded
# python program).
# ---------------------------------------------------------------------------
OBSERVER_INTERVAL="${OBSERVER_INTERVAL:-120}"
OBSERVER_STATE_DIR="${OBSERVER_STATE_DIR:-/tmp/opencode/observer-state}"
OBSERVER_FLAG_ISSUE="${OBSERVER_FLAG_ISSUE:-429}"
OBSERVER_EVIDENCE_LINES="${OBSERVER_EVIDENCE_LINES:-200}"
OBSERVER_PANE_LINES="${OBSERVER_PANE_LINES:-40}"
OBSERVER_PUSH_AHEAD_THRESHOLD="${OBSERVER_PUSH_AHEAD_THRESHOLD:-5}"
OBSERVER_PARKED_ALERT_COUNT="${OBSERVER_PARKED_ALERT_COUNT:-2}"
OBSERVER_PARKED_DEFAULT_RESUME_MINS="${OBSERVER_PARKED_DEFAULT_RESUME_MINS:-60}"
OBSERVER_MAX_ACTIONS_PER_HOUR="${OBSERVER_MAX_ACTIONS_PER_HOUR:-24}"
OBSERVER_MAX_CONSECUTIVE_ERRORS="${OBSERVER_MAX_CONSECUTIVE_ERRORS:-10}"
OBSERVER_STALE_ESCALATE_CYCLES="${OBSERVER_STALE_ESCALATE_CYCLES:-2}"
OBSERVER_OPENCODE_LOG="${OBSERVER_OPENCODE_LOG:-$HOME/.local/share/opencode/log/opencode.log}"
OBSERVER_DIS_VALIDATOR="${OBSERVER_DIS_VALIDATOR:-}"
OBSERVER_DRY_RUN="${OBSERVER_DRY_RUN:-}"
OBSERVER_INPUT_JSON="${OBSERVER_INPUT_JSON:-}"
OBSERVER_DOCTRINE_DIRS="${OBSERVER_DOCTRINE_DIRS:-.crosslink/knowledge:docs/methodology:docs/standards}"
OBSERVER_DOCTRINE_FILES="${OBSERVER_DOCTRINE_FILES:-AGENTS.md:ORIENTATION.md:SESSION-START.md:docs/SESSION-END.md}"
# F2 (#456 revised scope): event-driven fast path over opencode.log.
OBSERVER_FAST_PATH="${OBSERVER_FAST_PATH:-1}"
OBSERVER_FAST_READ_CAP="${OBSERVER_FAST_READ_CAP:-2097152}"
OBSERVER_FASTPATH_DEDUP_SECS="${OBSERVER_FASTPATH_DEDUP_SECS:-3600}"
# F3 (#460): per-builder commit-age signal feeding STALE logic.
OBSERVER_COMMIT_STALE_MINS="${OBSERVER_COMMIT_STALE_MINS:-10}"

export OB_REPO_ROOT OB_STATE_DIR OB_FLAG_ISSUE OB_EVIDENCE_LINES \
    OB_PANE_LINES OB_PUSH_AHEAD_THRESHOLD OB_PARKED_ALERT_COUNT \
    OB_PARKED_DEFAULT_RESUME_MINS OB_MAX_ACTIONS_PER_HOUR \
    OB_STALE_ESCALATE_CYCLES OB_OPENCODE_LOG OB_DIS_VALIDATOR \
    OB_DRY_RUN OB_DOCTRINE_DIRS OB_DOCTRINE_FILES \
    OB_FAST_PATH OB_FAST_READ_CAP OB_FASTPATH_DEDUP_SECS \
    OB_COMMIT_STALE_MINS

OB_STATE_DIR="$OBSERVER_STATE_DIR"
OB_FLAG_ISSUE="$OBSERVER_FLAG_ISSUE"
OB_EVIDENCE_LINES="$OBSERVER_EVIDENCE_LINES"
OB_PANE_LINES="$OBSERVER_PANE_LINES"
OB_PUSH_AHEAD_THRESHOLD="$OBSERVER_PUSH_AHEAD_THRESHOLD"
OB_PARKED_ALERT_COUNT="$OBSERVER_PARKED_ALERT_COUNT"
OB_PARKED_DEFAULT_RESUME_MINS="$OBSERVER_PARKED_DEFAULT_RESUME_MINS"
OB_MAX_ACTIONS_PER_HOUR="$OBSERVER_MAX_ACTIONS_PER_HOUR"
OB_STALE_ESCALATE_CYCLES="$OBSERVER_STALE_ESCALATE_CYCLES"
OB_OPENCODE_LOG="$OBSERVER_OPENCODE_LOG"
OB_DIS_VALIDATOR="$OBSERVER_DIS_VALIDATOR"
OB_DRY_RUN="${OBSERVER_DRY_RUN:+1}"
OB_DOCTRINE_DIRS="$OBSERVER_DOCTRINE_DIRS"
OB_DOCTRINE_FILES="$OBSERVER_DOCTRINE_FILES"
OB_FAST_PATH="$OBSERVER_FAST_PATH"
OB_FAST_READ_CAP="$OBSERVER_FAST_READ_CAP"
OB_FASTPATH_DEDUP_SECS="$OBSERVER_FASTPATH_DEDUP_SECS"
OB_COMMIT_STALE_MINS="$OBSERVER_COMMIT_STALE_MINS"

# Repo root discovery: this script may run from the main checkout
# (<root>/scripts/) or from an agent worktree (<root>/.worktrees/<slug>/scripts/).
# The root is the directory that contains .worktrees.
discover_repo_root() {
    local d="$SCRIPT_DIR"
    while [ "$d" != "/" ]; do
        if [ -d "$d/.worktrees" ]; then
            printf '%s\n' "$d"
            return 0
        fi
        d="$(dirname "$d")"
    done
    d="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" && {
        printf '%s\n' "$d"
        return 0
    }
    printf '%s\n' "$(dirname "$SCRIPT_DIR")"
}
OB_REPO_ROOT="${OBSERVER_REPO_ROOT:-$(discover_repo_root)}"
export OB_REPO_ROOT

EVENTS_FILE="$OBSERVER_STATE_DIR/events.jsonl"
ERRCOUNT_FILE="$OBSERVER_STATE_DIR/.consecutive-errors"

mkdir -p "$OBSERVER_STATE_DIR/evidence" 2>/dev/null
[ -f "$EVENTS_FILE" ] || : >> "$EVENTS_FILE" 2>/dev/null

ONCE=0
for arg in "$@"; do
    case "$arg" in
        --once) ONCE=1 ;;
        *)
            printf 'usage: observer.sh [--once]\n' >&2
            exit 2
            ;;
    esac
done

if [ -z "$OBSERVER_INPUT_JSON" ] && [ ! -r "$LIVENESS_PY" ]; then
    printf '{"ts":"%s","event":"fatal","kind":"missing-liveness-script","path":"%s"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$LIVENESS_PY" >> "$EVENTS_FILE"
    exit 1
fi

# ---------------------------------------------------------------------------
# CYCLE_PROG: the entire per-cycle brain, embedded (same pattern as the
# watchdog DIFF_PROG, scaled up). Reads the compacted liveness JSON on stdin,
# loads/saves manager-state.json atomically, refines verdicts into lifecycle
# transitions (deep probes only for candidate agents), executes the scoped
# actions through crosslink CLI surfaces, runs the wave-level checks
# (merge/push-ahead, doctrine-edit DIS validation), and prints one cycle
# summary JSON object on stdout. NOTE: this heredoc is single-quoted; the
# python code deliberately avoids single-quote characters.
# ---------------------------------------------------------------------------
CYCLE_PROG='
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

def env(name, default=""):
    return os.environ.get(name, default)

def env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except ValueError:
        return default

REPO_ROOT = env("OB_REPO_ROOT")
STATE_DIR = env("OB_STATE_DIR", "/tmp/opencode/observer-state")
WORKTREES_ROOT = os.path.join(REPO_ROOT, ".worktrees") if REPO_ROOT else ""
OPENCODE_LOG = env("OB_OPENCODE_LOG")
FLAG_ISSUE = env("OB_FLAG_ISSUE", "429")
DRY_RUN = env("OB_DRY_RUN", "") == "1"
EVIDENCE_LINES = env_int("OB_EVIDENCE_LINES", 200)
PANE_LINES = env_int("OB_PANE_LINES", 40)
PUSH_THRESHOLD = env_int("OB_PUSH_AHEAD_THRESHOLD", 5)
PARKED_ALERT_COUNT = env_int("OB_PARKED_ALERT_COUNT", 2)
PARKED_DEFAULT_MINS = env_int("OB_PARKED_DEFAULT_RESUME_MINS", 60)
MAX_ACTIONS_PER_HOUR = env_int("OB_MAX_ACTIONS_PER_HOUR", 24)
STALE_ESCALATE = env_int("OB_STALE_ESCALATE_CYCLES", 2)
DIS_VALIDATOR = env("OB_DIS_VALIDATOR")
DOCTRINE_DIRS = [d for d in env("OB_DOCTRINE_DIRS").split(":") if d]
DOCTRINE_FILES = [f for f in env("OB_DOCTRINE_FILES").split(":") if f]
FAST_PATH = env("OB_FAST_PATH", "1") == "1"
FAST_READ_CAP = env_int("OB_FAST_READ_CAP", 2097152)
FASTPATH_DEDUP_SECS = env_int("OB_FASTPATH_DEDUP_SECS", 3600)
COMMIT_STALE_MINS = env_int("OB_COMMIT_STALE_MINS", 10)

EVENTS_FILE = os.path.join(STATE_DIR, "events.jsonl")
STAGING_FILE = os.path.join(STATE_DIR, "model-evidence-staging.jsonl")
STATE_FILE = os.path.join(STATE_DIR, "manager-state.json")
SWEEP_FILE = os.path.join(STATE_DIR, "force-sweep-pending.txt")
EVIDENCE_ROOT = os.path.join(STATE_DIR, "evidence")

KILL_EXIT_STATUSES = {"137", "143"}  # SIGKILL / SIGTERM pane exit signatures

def now_iso(ts=None):
    return datetime.fromtimestamp(ts if ts is not None else time.time(),
                                 tz=timezone.utc).isoformat()

def parse_iso(value):
    """Tolerant ISO-8601 parser: truncates >6-digit fractions (metadata
    files carry nanosecond stamps that strict fromisoformat rejects)."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    m = re.match(r"^(.*?\.\d{1,6})\d*(.*)$", text)
    if m:
        text = m.group(1) + m.group(2)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()

def ts_slug(ts=None):
    return datetime.fromtimestamp(ts if ts is not None else time.time(),
                                  tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def log_event(fields):
    fields.setdefault("ts", now_iso())
    try:
        with open(EVENTS_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(fields, separators=(",", ":")) + "\n")
    except OSError:
        pass

def run(cmd, timeout=90, timeout_ok=True):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", "binary not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"

# ---------------------------------------------------------------------------
# Manager state (atomic write, single writer per state dir)
# ---------------------------------------------------------------------------

def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def save_state(state):
    tmp = STATE_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, sort_keys=True)
        os.replace(tmp, STATE_FILE)
        return None
    except OSError as exc:
        return str(exc)

# ---------------------------------------------------------------------------
# Circuit breaker: rolling 1h window over ALL mutating action invocations
# (real or dry-run). Prevents pathological loops from churning crosslink.
# ---------------------------------------------------------------------------

def breaker_allow(state, kind):
    now = time.time()
    window = [t for t in state.get("action_window", [])
              if isinstance(t, (int, float)) and now - t < 3600]
    if len(window) >= MAX_ACTIONS_PER_HOUR:
        if now - state.get("last_halt_event_ts", 0) > 3600:
            state["last_halt_event_ts"] = now
            log_event({"event": "breaker-halt", "kind": kind,
                       "window_actions": len(window),
                       "cap": MAX_ACTIONS_PER_HOUR,
                       "detail": "mutation cap reached; mutations suspended"})
        state["action_window"] = window
        return False
    window.append(now)
    state["action_window"] = window
    return True

def post_comment(state, issue, message):
    if not issue:
        log_event({"event": "comment-skipped", "reason": "no-issue",
                   "message": message[:200]})
        return False
    if not breaker_allow(state, "comment:" + str(issue)):
        return False
    if DRY_RUN:
        log_event({"event": "comment-dry-run", "issue": issue,
                   "message": message})
        return True
    rc, _, err = run(["crosslink", "issue", "comment", str(issue), message],
                     timeout=120)
    log_event({"event": "comment", "issue": issue, "posted": rc == 0,
               "rc": rc, "err": (err or "").strip()[:200]})
    return rc == 0

# ---------------------------------------------------------------------------
# Agent-context probes (bounded; only invoked for transition candidates)
# ---------------------------------------------------------------------------

def agent_log_section(agent):
    """Attribute the shared opencode.log to one agent.

    Primary marker: session-creation lines carry both the session ID and
    the instance directory (message=created id=ses_... directory=<wt>).
    Fallback marker: cwd=<...> tracking lines (older log formats).
    """
    result = {"available": False, "tail": [], "model": None,
              "provider": None, "rate_limited": False, "retry_after": None,
              "error_signature": False, "sessions": []}
    if not OPENCODE_LOG or not os.path.isfile(OPENCODE_LOG):
        return result
    esc = re.escape(agent)
    sessions = []
    provider = model = None

    def collect_sessions(pattern):
        rc, out, _ = run(["grep", "-a", "-E", pattern, OPENCODE_LOG],
                         timeout=90)
        if rc == 0 and out:
            for line in out.splitlines()[-200:]:
                m = re.search(r"id=(ses_[A-Za-z0-9]+)", line)
                if m and m.group(1) not in sessions:
                    sessions.append(m.group(1))

    # Primary: opencode fork session-creation lines bound to the worktree.
    # (slug/version/projectID fields sit between id= and directory=.)
    collect_sessions("message=created id=ses_[A-Za-z0-9]+ .*"
                     "directory=[^\t ]*" + esc)
    # Fallback: cwd tracking lines mentioning the worktree slug.
    if not sessions:
        collect_sessions("cwd=[^\t ]*" + esc)
    if not sessions:
        rc, out, _ = run(["grep", "-a", "-E", "directory=[^\t ]*" + esc +
                          "|cwd=[^\t ]*" + esc, OPENCODE_LOG], timeout=90)
        if rc == 0 and out:
            for line in out.splitlines()[-600:]:
                m = re.search(r"session\.id=(ses_[A-Za-z0-9]+)", line)
                if m and m.group(1) not in sessions:
                    sessions.append(m.group(1))
                pm = re.search(r"llm\.provider=(\S+)\s+llm\.model=(\S+)",
                               line)
                if pm:
                    provider, model = pm.group(1), pm.group(2)
    result["provider"], result["model"] = provider, model
    result["sessions"] = sessions
    if not sessions:
        return result
    result["available"] = True
    # Candidate sessions can be polluted by quoted command text inside the
    # shared log (shell commands that mention these markers get logged
    # too), so try each candidate most-recent-first and keep the first
    # one that actually yields log content.
    tail = []
    for sid in reversed(sessions[-3:]):
        rc2, out2, _ = run(["grep", "-a", "-F",
                            "session.id=" + sid, OPENCODE_LOG],
                           timeout=90)
        if rc2 == 0 and out2:
            tail = out2.splitlines()[-EVIDENCE_LINES:]
            break
    result["tail"] = tail
    for line in reversed(tail):
        pm = re.search(r"llm\.provider=(\S+)\s+llm\.model=(\S+)", line)
        if pm:
            result["provider"], result["model"] = pm.group(1), pm.group(2)
            break
    joined = "\n".join(tail[-120:])
    if re.search(r"AI_APICallError.*Rate limit|Rate limit exceeded",
                 joined):
        result["rate_limited"] = True
        result["retry_after"] = parse_retry_after(tail)
    if re.search(r"level=ERROR|Traceback|panic:", joined):
        result["error_signature"] = True
    return result

def parse_retry_after(tail_lines):
    """Best-effort resume_at epoch from retry-after evidence in the tail."""
    for line in reversed(tail_lines[-80:]):
        m = re.search(
            r"retry[-_ ]after[\"=: ]{0,6}(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})",
            line, re.IGNORECASE)
        if m:
            try:
                stamp = m.group(1).replace("T", " ")
                dt = datetime.strptime(stamp, "%Y-%m-%d %H:%M")
                return dt.replace(tzinfo=timezone.utc).timestamp()
            except ValueError:
                pass
    for line in reversed(tail_lines[-80:]):
        m = re.search(r"retry[-_ ]after[\"=: ]{0,6}(\d{1,6})\b", line,
                      re.IGNORECASE)
        if m:
            return time.time() + int(m.group(1))
    for line in reversed(tail_lines[-80:]):
        m = re.search(r"daily reset at (\d{2}):(\d{2})", line, re.IGNORECASE)
        if m:
            now = datetime.now(timezone.utc)
            target = now.replace(hour=int(m.group(1)),
                                 minute=int(m.group(2)), second=0,
                                 microsecond=0)
            if target <= now:
                target = target + timedelta(days=1)
            return target.timestamp()
    return None

def pane_status(agent):
    """(state, exit_status) from tmux; state in alive/dead/gone."""
    rc, out, _ = run(["tmux", "list-panes", "-t", agent, "-F",
                      "#{pane_dead}\t#{pane_dead_status}"], timeout=20)
    if rc != 0:
        return "gone", None
    dead_statuses = []
    alive = False
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        if parts[0].strip() == "1":
            dead_statuses.append(parts[1].strip())
        else:
            alive = True
    if alive:
        return "alive", None
    if dead_statuses:
        return "dead", dead_statuses[0]
    return "gone", None

def pane_tail_text(agent):
    rc, out, _ = run(["tmux", "capture-pane", "-p", "-S",
                      "-" + str(PANE_LINES), "-t", agent], timeout=20)
    if rc != 0:
        return None
    return out

def working_issue(agent):
    try:
        with open(os.path.join(WORKTREES_ROOT, agent, "KICKOFF.md"),
                  encoding="utf-8", errors="replace") as fh:
            head = fh.read(20000)
        m = re.search(r"\*\*Issue\*\*:\s*#(\d+)", head)
        if m:
            return m.group(1)
    except OSError:
        pass
    return None

def agent_started_epoch(agent):
    try:
        with open(os.path.join(WORKTREES_ROOT, agent,
                               ".kickoff-metadata.json"),
                  encoding="utf-8") as fh:
            started = json.load(fh).get("started_at")
        return parse_iso(started)
    except (OSError, ValueError, TypeError):
        return None

def agent_branch(agent):
    wt = os.path.join(WORKTREES_ROOT, agent)
    if not os.path.isdir(wt):
        return None
    rc, out, _ = run(["git", "-C", wt, "rev-parse", "--abbrev-ref", "HEAD"],
                     timeout=20)
    if rc == 0 and out.strip() and out.strip() != "HEAD":
        return out.strip()
    return None

def commit_age_min(agent):
    """F3 (#460): minutes since the last commit in the agent worktree.
    Makes the incremental-commit discipline mechanically observable."""
    wt = os.path.join(WORKTREES_ROOT, agent)
    if not os.path.isdir(wt):
        return None
    rc, out, _ = run(["git", "-C", wt, "log", "-1", "--format=%ct"],
                     timeout=20)
    if rc == 0 and out.strip().isdigit():
        return round(max(0.0, time.time() - int(out.strip())) / 60.0, 1)
    return None

# ---------------------------------------------------------------------------
# Evidence bundles
# ---------------------------------------------------------------------------

def write_evidence_bundle(agent, tag, sections):
    folder = os.path.join(EVIDENCE_ROOT, agent, ts_slug() + "-" + tag)
    hashes = {}
    try:
        os.makedirs(folder, exist_ok=True)
        for name, text in sections.items():
            path = os.path.join(folder, name)
            data = text if isinstance(text, bytes) else text.encode(
                "utf-8", "replace")
            with open(path, "wb") as fh:
                fh.write(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
        manifest = {"agent": agent, "tag": tag, "created_at": now_iso(),
                    "files": hashes}
        with open(os.path.join(folder, "bundle.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)
        log_event({"event": "evidence-bundle", "agent": agent, "tag": tag,
                   "path": folder, "sha256": hashes})
        return folder, hashes
    except OSError as exc:
        log_event({"event": "evidence-bundle-failed", "agent": agent,
                   "tag": tag, "err": str(exc)})
        return None, {}

# ---------------------------------------------------------------------------
# F1 (#460): evidence-at-transition composer. Every terminal verdict gets a
# full bundle composed AT DETECTION: attributed opencode.log tail (sha256),
# pane tail, worktree git status/diffstat, verdict timeline, and the last
# hub position ref from the working issue. Failure documentation must take
# seconds, not archaeology.
# ---------------------------------------------------------------------------

def worktree_git_evidence(agent):
    """Bounded git evidence from the agent worktree (status + diffstat +
    last-commit age). Read-only; absent worktree reported as such."""
    ev = {"worktree": None, "branch": None, "status": None,
          "status_count": 0, "diffstat": None, "last_commit_age_min": None}
    wt = os.path.join(WORKTREES_ROOT, agent)
    if not os.path.isdir(wt):
        return ev
    ev["worktree"] = wt
    rc, out, _ = run(["git", "-C", wt, "status", "--porcelain"], timeout=30)
    if rc == 0:
        lines = out.splitlines()
        ev["status_count"] = len(lines)
        ev["status"] = "\n".join(lines[:40]) or "(clean)"
    branch = agent_branch(agent)
    ev["branch"] = branch
    rc, out, _ = run(["git", "-C", wt, "diff", "--stat", "main"],
                     timeout=30)
    if rc == 0 and out.strip():
        ev["diffstat"] = "\n".join(out.splitlines()[:20])
    elif rc == 0:
        ev["diffstat"] = "(no delta vs main)"
    rc, out, _ = run(["git", "-C", wt, "log", "-1", "--format=%ct"],
                     timeout=20)
    if rc == 0 and out.strip().isdigit():
        ev["last_commit_age_min"] = round(
            max(0.0, time.time() - int(out.strip())) / 60.0, 1)
    return ev

def last_hub_position(issue):
    """Last synced position comment on the working issue (hub view).

    Returns {"stamp": ..., "kind": ...} for the most recent comment crosslink
    reports, or None. One bounded CLI read per terminal transition.
    """
    if not issue:
        return None
    rc, out, _ = run(["crosslink", "issue", "show", str(issue)], timeout=60)
    if rc != 0 or not out:
        return None
    best = None
    for m in re.finditer(
            r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?)\]\s+\[([a-z-]+)\]",
            out):
        best = {"stamp": m.group(1), "kind": m.group(2)}
    return best

def compose_transition_evidence(state, row, rec, tag):
    """Compose the full transition evidence bundle. Returns a dict with the
    bundle path, per-section sha256 map, log attribution info, git evidence
    and hub position ref."""
    agent = row["agent"]
    loginfo = agent_log_section(agent)
    tail_text = "\n".join(loginfo.get("tail", []))
    if not tail_text:
        tail_text = "(no attributed opencode.log section found)"
    pane_text = pane_tail_text(agent)
    if not pane_text:
        pane_text = "(tmux session unavailable for pane capture)"
    git_ev = worktree_git_evidence(agent)
    pos = last_hub_position(working_issue(agent) or FLAG_ISSUE)
    timeline = rec.get("history", [])[-12:]
    sections = {
        "opencode-tail.log": tail_text,
        "pane-tail.txt": pane_text,
        "git-status.txt": git_ev.get("status") or "(worktree absent)",
        "git-diffstat.txt": git_ev.get("diffstat") or "(none)",
        "verdict-timeline.json": json.dumps(timeline, indent=2),
        "hub-position.json": json.dumps(pos or {"position": None},
                                        separators=(",", ":")),
    }
    bundle, hashes = write_evidence_bundle(agent, tag, sections)
    return {"bundle": bundle, "sha256": hashes, "loginfo": loginfo,
            "git": git_ev, "hub_position": pos}

def evidence_summary_line(ev):
    """Compact one-line evidence digest for posted comments."""
    if not ev:
        return ""
    parts = []
    if ev.get("bundle"):
        parts.append("bundle={0}".format(ev["bundle"]))
    if ev.get("git", {}).get("branch"):
        parts.append("branch={0}".format(ev["git"]["branch"]))
    parts.append("dirty_files={0}".format(
        ev.get("git", {}).get("status_count", 0)))
    age = ev.get("git", {}).get("last_commit_age_min")
    if age is not None:
        parts.append("last_commit_age_min={0}".format(age))
    pos = ev.get("hub_position")
    if pos:
        parts.append("hub_position={0}[{1}]".format(pos.get("stamp"),
                                                    pos.get("kind")))
    nhash = len(ev.get("sha256", {}))
    if nhash:
        parts.append("sections_sha256={0}".format(nhash))
    return " ".join(parts)

# ---------------------------------------------------------------------------
# Crosslink mutation surfaces (the ONLY write paths into the fleet)
# ---------------------------------------------------------------------------

def kickoff_cleanup(state, agent):
    if not breaker_allow(state, "cleanup:" + agent):
        return False
    if DRY_RUN:
        log_event({"event": "cleanup-dry-run", "agent": agent,
                   "cmd": "crosslink kickoff cleanup --only " + agent +
                          " --yes"})
        return True
    rc, out, err = run(["crosslink", "kickoff", "cleanup", "--only", agent,
                        "--yes"], timeout=180)
    log_event({"event": "cleanup", "agent": agent, "rc": rc,
               "out": (out or "").strip()[:300],
               "err": (err or "").strip()[:300]})
    return rc == 0

def kickoff_stop(state, agent, branch):
    candidates = [c for c in (branch, agent) if c]
    for cand in candidates:
        if not breaker_allow(state, "stop:" + cand):
            return False
        if DRY_RUN:
            log_event({"event": "stop-dry-run", "agent": agent,
                       "target": cand,
                       "cmd": "crosslink kickoff stop " + cand + " --force"})
            return True
        rc, out, err = run(["crosslink", "kickoff", "stop", cand, "--force"],
                           timeout=90)
        log_event({"event": "stop", "agent": agent, "target": cand,
                   "rc": rc, "out": (out or "").strip()[:300],
                   "err": (err or "").strip()[:300]})
        if rc == 0:
            return True
    return False

def flag_for_sweep(agent, reason):
    line = "{0} {1} {2}\n".format(now_iso(), agent, reason)
    try:
        with open(SWEEP_FILE, "a", encoding="utf-8") as fh:
            fh.write(line)
        log_event({"event": "force-sweep-flagged", "agent": agent,
                   "reason": reason})
    except OSError as exc:
        log_event({"event": "force-sweep-flag-failed", "agent": agent,
                   "err": str(exc)})

def append_staging_row(row):
    row.setdefault("ts", now_iso())
    try:
        with open(STAGING_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")
        log_event({"event": "model-evidence-row", "agent": row.get("agent"),
                   "outcome": row.get("outcome")})
        return True
    except OSError as exc:
        log_event({"event": "model-evidence-row-failed",
                   "agent": row.get("agent"), "err": str(exc)})
        return False

def deliverable_check(branch):
    """Deliverable verification per #460 R2.

    Branch-state alone is NOT deliverable evidence: an empty branch (tip ==
    main, zero file delta) was reported merged_into_main=true (#460 false
    positive). The check now requires a real FILE delta between the
    merge-base and the branch tip, with each candidate file verified to
    EXIST in the branch tree via git cat-file -e. merged=true only when
    ancestry AND a present, non-empty file delta both hold.
    """
    info = {"branch": branch, "exists": False, "ahead_of_main": None,
            "merged": None, "files_changed": None,
            "deliverable_present": False, "sample_files": []}
    if not branch or not REPO_ROOT:
        return info
    rc, _, _ = run(["git", "-C", REPO_ROOT, "rev-parse", "--verify",
                    "--quiet", "refs/heads/" + branch], timeout=20)
    info["exists"] = rc == 0
    if not info["exists"]:
        return info
    rc2, out2, _ = run(["git", "-C", REPO_ROOT, "rev-list", "--count",
                        "main.." + branch], timeout=30)
    if rc2 == 0:
        try:
            info["ahead_of_main"] = int(out2.strip())
        except ValueError:
            pass
    rc_mb, out_mb, _ = run(["git", "-C", REPO_ROOT, "merge-base", "main",
                            branch], timeout=30)
    if rc_mb == 0:
        base = out_mb.strip()
        rc_d, out_d, _ = run(["git", "-C", REPO_ROOT, "diff", "--name-only",
                              base + ".." + branch], timeout=60)
        files = []
        if rc_d == 0:
            files = [ln.strip() for ln in out_d.splitlines() if ln.strip()]
        info["files_changed"] = len(files)
        info["sample_files"] = files[:5]
        present = 0
        for path in files[:20]:
            rcf, _, _ = run(["git", "-C", REPO_ROOT, "cat-file", "-e",
                             branch + ":" + path, "--"], timeout=20)
            if rcf == 0:
                present += 1
        info["deliverable_present"] = present > 0
    rc3, _, _ = run(["git", "-C", REPO_ROOT, "merge-base", "--is-ancestor",
                     branch, "main"], timeout=30)
    ancestor = rc3 == 0
    info["merged"] = bool(ancestor and info["deliverable_present"])
    return info

# ---------------------------------------------------------------------------
# Post-transition action sets (one per design verdict)
# ---------------------------------------------------------------------------

def act_completed(state, row, rec):
    agent = row["agent"]
    issue = working_issue(agent)
    started = agent_started_epoch(agent)
    branch = agent_branch(agent)
    ev = compose_transition_evidence(state, row, rec, "completed")
    loginfo = ev["loginfo"]
    cleanup_ok = kickoff_cleanup(state, agent)
    orphan = os.path.isdir(os.path.join(WORKTREES_ROOT, agent))
    if orphan:
        flag_for_sweep(agent, "completed-but-worktree-remains-after-cleanup")
    deliv = deliverable_check(branch)
    duration_min = None
    if started:
        duration_min = round((time.time() - started) / 60.0, 1)
    append_staging_row({
        "agent": agent, "outcome": "completed", "role": row.get("role"),
        "issue": issue, "model": loginfo.get("model"),
        "provider": loginfo.get("provider"), "branch": branch,
        "deliverable": deliv, "duration_min": duration_min,
        "cleanup": "dry-run" if DRY_RUN else ("executed" if cleanup_ok
                                              else "failed"),
        "orphan_worktree": orphan,
        "evidence_bundle": ev["bundle"], "evidence_sha256": ev["sha256"],
    })
    rec["phase"] = "completed"
    rec.setdefault("handled", {})["DONE-CONFIRMED"] = now_iso()
    message = ("[OBSERVER] COMPLETED agent={0} deliverable={1} "
               "files_changed={2} merged={3}. {4}".format(
                   agent,
                   deliv.get("deliverable_present"),
                   deliv.get("files_changed"), deliv.get("merged"),
                   evidence_summary_line(ev)))
    post_comment(state, issue or FLAG_ISSUE, message)
    log_event({"event": "transition-action", "action": "completed",
               "agent": agent, "issue": issue, "cleanup_ok": cleanup_ok,
               "orphan": orphan, "deliverable": deliv,
               "evidence": ev["bundle"], "sha256": ev["sha256"]})

def issue_comment_count_since(issue_text, since_epoch):
    count = 0
    for m in re.finditer(
            r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?)\]", issue_text):
        stamp = m.group(1)
        fmt = "%Y-%m-%d %H:%M:%S" if stamp.count(":") == 2 else \
              "%Y-%m-%d %H:%M"
        try:
            epoch = datetime.strptime(stamp, fmt).replace(
                tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
        if epoch >= since_epoch:
            count += 1
    return count

def act_finished_unmarkable(state, row, rec):
    agent = row["agent"]
    issue = working_issue(agent)
    findings_exist = None
    started = agent_started_epoch(agent)
    if issue and started:
        rc, out, _ = run(["crosslink", "issue", "show", issue], timeout=60)
        if rc == 0:
            findings_exist = issue_comment_count_since(out, started) > 0
    flag_for_sweep(agent, "finished-unmarkable: read-only role finished "
                          "without DONE marker; operator force-sweep at "
                          "wave end")
    ev = compose_transition_evidence(state, row, rec, "finished-unmarkable")
    loginfo = ev["loginfo"]
    append_staging_row({
        "agent": agent, "outcome": "finished-unmarkable",
        "role": row.get("role"), "issue": issue,
        "findings_on_working_issue": findings_exist,
        "model": loginfo.get("model"), "provider": loginfo.get("provider"),
        "evidence_bundle": ev["bundle"], "evidence_sha256": ev["sha256"],
    })
    rec["phase"] = "finished-unmarkable"
    rec.setdefault("handled", {})["FINISHED-UNMARKABLE"] = now_iso()
    message = ("[OBSERVER] FINISHED-UNMARKABLE agent={0} "
               "findings_on_working_issue={1}. Worktree flagged for "
               "operator force-sweep. {2}".format(
                   agent, findings_exist, evidence_summary_line(ev)))
    post_comment(state, issue or FLAG_ISSUE, message)
    log_event({"event": "transition-action", "action": "finished-unmarkable",
               "agent": agent, "issue": issue,
               "findings_on_working_issue": findings_exist,
               "evidence": ev["bundle"], "sha256": ev["sha256"]})

def classify_death(row, loginfo):
    """FAILED (preserve) vs KILLED (orchestrator stop) discrimination.

    Kill classification requires POSITIVE evidence (SIGTERM/SIGKILL pane
    exit status); everything else conservatively preserves the worktree.
    A pane that still shows processes is usually the zombie-prompt class
    (idle shell, no agent descendants): the FAILED path never destroys
    anything, so classify by log evidence rather than deferring forever.
    """
    status, exit_code = pane_status(row["agent"])
    if status == "alive":
        if loginfo.get("rate_limited"):
            return "parked", "rate-limit signature despite terminal verdict"
        return "failed", ("terminal verdict with only shell-level pane "
                          "activity (zombie-prompt class)")
    if status == "dead":
        if exit_code in KILL_EXIT_STATUSES:
            sig = "SIGKILL" if exit_code == "137" else "SIGTERM"
            return "killed", "pane exit status {0} ({1} signature)".format(
                exit_code, sig)
        return "failed", "pane exit status {0} (non-kill exit)".format(
            exit_code or "unknown")
    if loginfo.get("error_signature"):
        return "failed", "error signature in attributed log tail"
    return "failed", ("session gone with no kill evidence; preserved for "
                      "forensics (conservative default)")

def act_failed(state, row, rec, reason):
    agent = row["agent"]
    issue = working_issue(agent) or FLAG_ISSUE
    ev = compose_transition_evidence(state, row, rec, "failed")
    loginfo = ev["loginfo"]
    bundle, hashes = ev["bundle"], ev["sha256"]
    rec["phase"] = "failed"
    rec.setdefault("handled", {})["DEAD-UNMARKED"] = now_iso()
    rec["fail_reason"] = reason
    try:
        with open(os.path.join(STATE_DIR, "preserved-worktrees.txt"), "a",
                  encoding="utf-8") as fh:
            fh.write("{0} {1} {2}\n".format(now_iso(), agent, reason))
    except OSError:
        pass
    message = ("[OBSERVER] FAILED agent={0} verdict={1} reason={2}. "
               "Worktree PRESERVED for forensics (no automatic cleanup). "
               "{3}".format(agent, row.get("verdict"), reason,
                            evidence_summary_line(ev)))
    if loginfo.get("model"):
        message += (" Failed model={0}/{1}.".format(
            loginfo.get("provider"), loginfo.get("model")))
    message += (" Recommendation: relaunch-with-backup-model; operator "
                "selects the backup from the Model Routing Matrix.")
    post_comment(state, issue, message)
    log_event({"event": "transition-action", "action": "failed",
               "agent": agent, "issue": issue, "reason": reason,
               "evidence": bundle, "sha256": hashes})

def act_killed(state, row, rec, reason):
    agent = row["agent"]
    issue = working_issue(agent) or FLAG_ISSUE
    ev = compose_transition_evidence(state, row, rec, "killed")
    cleanup_ok = kickoff_cleanup(state, agent)
    orphan = os.path.isdir(os.path.join(WORKTREES_ROOT, agent))
    if orphan:
        flag_for_sweep(agent, "killed-but-orphaned-worktree-remains")
    rec["phase"] = "killed"
    rec.setdefault("handled", {})["DEAD-UNMARKED"] = now_iso()
    rec["kill_reason"] = reason
    chain = {
        "trigger": reason,
        "verdict_timeline": rec.get("history", [])[-8:],
        "cleanup_executed": cleanup_ok,
        "orphan_worktree": orphan,
        "evidence_bundle": ev["bundle"],
        "sha256": ev["sha256"],
    }
    message = ("[OBSERVER] KILLED agent={0} trigger={1}. Scoped cleanup "
               "executed={2}; orphaned worktree={3}. Evidence chain: "
               "{4}. {5}".format(
                   agent, reason,
                   "yes" if cleanup_ok else "NO",
                   "PRESENT (force-sweep flagged)" if orphan else "none",
                   json.dumps(chain, separators=(",", ":")),
                   evidence_summary_line(ev)))
    post_comment(state, issue, message)
    log_event({"event": "transition-action", "action": "killed",
               "agent": agent, "issue": issue, "chain": chain})

def act_frozen(state, row, rec, trigger_detail):
    agent = row["agent"]
    issue = working_issue(agent) or FLAG_ISSUE
    ev = compose_transition_evidence(state, row, rec, "terminated")
    loginfo = ev["loginfo"]
    bundle, hashes = ev["bundle"], ev["sha256"]
    branch = agent_branch(agent)
    stop_ok = kickoff_stop(state, agent, branch)
    cleanup_ok = kickoff_cleanup(state, agent)
    orphan = os.path.isdir(os.path.join(WORKTREES_ROOT, agent))
    if orphan:
        flag_for_sweep(agent, "frozen-but-orphaned-worktree-remains")
    rec["phase"] = "frozen-handled"
    rec.setdefault("handled", {})[row.get("verdict", "FROZEN")] = now_iso()
    rec["frozen_trigger"] = trigger_detail
    chain = {
        "trigger": trigger_detail,
        "verdict_timeline": rec.get("history", [])[-8:],
        "evidence_bundle": bundle,
        "sha256": hashes,
        "auto_kill": "executed" if stop_ok else ("dry-run" if DRY_RUN
                                                 else "FAILED"),
        "cleanup_executed": cleanup_ok,
        "orphan_worktree": orphan,
        "model": loginfo.get("model"), "provider": loginfo.get("provider"),
    }
    message = ("[OBSERVER] FROZEN TERMINATION agent={0} verdict={1} "
               "trigger={2}. Auto-killed per operator-granted spiral "
               "authority (#443 rev3, 2026-08-24): stop={3}, cleanup={4}, "
               "orphan_worktree={5}. Evidence bundle: {6} sha256={7}. "
               "{8} Recommendation: relaunch-with-backup-model.".format(
                   agent, row.get("verdict"), trigger_detail,
                   chain["auto_kill"],
                   "executed" if cleanup_ok else "FAILED",
                   "PRESENT (force-sweep flagged)" if orphan else "none",
                   bundle or "unavailable",
                   json.dumps(hashes, separators=(",", ":")),
                   evidence_summary_line(ev)))
    post_comment(state, issue, message)
    log_event({"event": "transition-action", "action": "frozen-termination",
               "agent": agent, "issue": issue, "chain": chain})

def act_parked(state, row, rec, loginfo):
    agent = row["agent"]
    resume = loginfo.get("retry_after")
    source = "retry-after-header"
    if resume is None:
        resume = time.time() + PARKED_DEFAULT_MINS * 60
        source = "default-window"
    first = rec.get("phase") != "parked"
    if first:
        rec["parked_since"] = now_iso()
    prev_resume = rec.get("resume_at")
    rec["phase"] = "parked"
    rec["resume_at"] = now_iso(resume)
    rec["resume_at_epoch"] = resume
    rec["resume_at_source"] = source
    if first or prev_resume != rec["resume_at"]:
        log_event({"event": "transition-action", "action": "parked",
                   "agent": agent, "first": first,
                   "resume_at": rec["resume_at"], "source": source,
                   "model": loginfo.get("model"),
                   "note": "kill suppressed; agent correctly waiting"})

# ---------------------------------------------------------------------------
# Per-agent transition refinement and dispatch
# ---------------------------------------------------------------------------

def fresh_rec(row):
    return {"verdict": row.get("verdict"),
            "aliveness": row.get("aliveness"),
            "age_min": row.get("age_min"),
            "seen_at": now_iso(), "phase": "active", "stale_streak": 0,
            "handled": {}, "parked_since": None, "resume_at": None,
            "history": [{"verdict": row.get("verdict"),
                         "seen_at": now_iso()}]}

def process_agent(state, row):
    agent = row.get("agent", "")
    verdict = row.get("verdict", "")
    rec = state["agents"].get(agent)
    if not isinstance(rec, dict):
        rec = fresh_rec(row)
    rec["verdict"] = verdict
    rec["aliveness"] = row.get("aliveness")
    rec["age_min"] = row.get("age_min")
    rec["seen_at"] = now_iso()
    hist = rec.get("history", [])
    hist.append({"verdict": verdict, "seen_at": now_iso()})
    rec["history"] = hist[-20:]

    phase = rec.get("phase", "active")
    handled = rec.setdefault("handled", {})
    deep_probed = {"loginfo": None}

    def loginfo():
        if deep_probed["loginfo"] is None:
            deep_probed["loginfo"] = agent_log_section(agent)
            sids = deep_probed["loginfo"].get("sessions") or []
            if sids:
                known = rec.setdefault("session_ids", [])
                for s in sids:
                    if s not in known:
                        known.append(s)
        return deep_probed["loginfo"]

    # PARKED resolution first: recovery on fresh activity, expiry to FROZEN.
    if phase == "parked":
        if verdict == "RUNNING-ALIVE":
            rec["phase"] = "active"
            rec["stale_streak"] = 0
            rec["resume_at"] = None
            log_event({"event": "parked-recovered", "agent": agent})
            state["agents"][agent] = rec
            return
        resume = rec.get("resume_at_epoch")
        if resume is None and rec.get("resume_at"):
            resume = parse_iso(rec["resume_at"])
            if resume is not None:
                rec["resume_at_epoch"] = resume
        if resume is not None and time.time() >= resume:
            log_event({"event": "parked-expired", "agent": agent,
                       "resume_at": rec.get("resume_at")})
            act_frozen(state, row, rec,
                       "parked resume_at expired without activity")
            state["agents"][agent] = rec
            return

    if verdict == "RUNNING-ALIVE":
        rec["stale_streak"] = 0
        if phase not in ("completed", "finished-unmarkable", "failed",
                         "killed", "frozen-handled"):
            rec["phase"] = "active"
            # F3: commit-overdue signal while nominally alive (deduped per
            # stale episode; re-arms automatically when a fresh commit lands).
            age = commit_age_min(agent)
            if age is not None:
                rec["commit_age_min"] = age
                if age > COMMIT_STALE_MINS:
                    if rec.get("commit_overdue_alerted") != "stale":
                        log_event({"event": "commit-overdue",
                                   "agent": agent,
                                   "commit_age_min": age,
                                   "threshold_min": COMMIT_STALE_MINS})
                        rec["commit_overdue_alerted"] = "stale"
                elif rec.get("commit_overdue_alerted"):
                    log_event({"event": "commit-caught-up", "agent": agent,
                               "commit_age_min": age})
                    rec["commit_overdue_alerted"] = None

    elif verdict == "DONE-CONFIRMED":
        if "DONE-CONFIRMED" not in handled and phase != "completed":
            act_completed(state, row, rec)

    elif verdict == "FINISHED-UNMARKABLE":
        if "FINISHED-UNMARKABLE" not in handled and \
                phase != "finished-unmarkable":
            act_finished_unmarkable(state, row, rec)

    elif verdict == "DEAD-UNMARKED":
        if "DEAD-UNMARKED" not in handled and phase not in (
                "failed", "killed", "frozen-handled"):
            kind, reason = classify_death(row, loginfo())
            if kind == "killed":
                act_killed(state, row, rec, reason)
            elif kind == "parked":
                act_parked(state, row, rec, loginfo())
            elif kind == "failed":
                act_failed(state, row, rec, reason)
            else:
                log_event({"event": "death-classification-deferred",
                           "agent": agent, "reason": reason})

    elif verdict == "LIKELY-FROZEN":
        if phase not in ("frozen-handled", "completed", "failed", "killed"):
            li = loginfo()
            if li.get("rate_limited"):
                act_parked(state, row, rec, li)
            else:
                act_frozen(state, row, rec,
                           "LIKELY-FROZEN confirmed (identical pane hashes "
                           "across two runs)")

    elif verdict == "STALE-SUSPECT":
        if phase not in ("frozen-handled", "completed", "failed", "killed"):
            li = loginfo()
            if li.get("rate_limited"):
                act_parked(state, row, rec, li)
            else:
                rec["stale_streak"] = rec.get("stale_streak", 0) + 1
                age = rec.get("commit_age_min")
                if age is None:
                    age = commit_age_min(agent)
                    if age is not None:
                        rec["commit_age_min"] = age
                fatal = rec.get("fast_path_fatal")
                old_commit = age is not None and age > COMMIT_STALE_MINS
                fresh_commit = age is not None and \
                    age <= COMMIT_STALE_MINS
                if fatal:
                    act_frozen(state, row, rec,
                               "STALE-SUSPECT escalated: fast-path fatal "
                               "evidence {0} at {1}".format(
                                   fatal.get("class"), fatal.get("ts")))
                elif old_commit:
                    # F3: a stale commit removes the benefit of the doubt.
                    act_frozen(state, row, rec,
                               "STALE-SUSPECT escalated on first quiet "
                               "cycle: last commit {0} min old exceeds "
                               "threshold {1} min".format(
                                   age, COMMIT_STALE_MINS))
                elif rec["stale_streak"] == 1:
                    if fresh_commit:
                        log_event({"event": "stale-warning", "agent": agent,
                                   "detail": "one warning cycle before "
                                             "escalation; fresh commit "
                                             "({0} min) grants an extra "
                                             "grace cycle".format(age)})
                    else:
                        log_event({"event": "stale-warning", "agent": agent,
                                   "detail": "one warning cycle before "
                                             "escalation"})
                elif rec["stale_streak"] >= max(2, STALE_ESCALATE) + \
                        (1 if fresh_commit else 0):
                    act_frozen(state, row, rec,
                               "STALE-SUSPECT escalated after {0} quiet "
                               "cycles".format(rec["stale_streak"]))

    state["agents"][agent] = rec

# ---------------------------------------------------------------------------
# Wave-level checks
# ---------------------------------------------------------------------------

def wave_merge(state):
    if not REPO_ROOT:
        return
    rc, out, _ = run(["git", "-C", REPO_ROOT, "rev-parse", "refs/heads/main"],
                     timeout=20)
    if rc != 0:
        return
    head = out.strip()
    prev = state.get("last_main_head")
    state["last_main_head"] = head
    if not prev or prev == head:
        return
    ahead = None
    ahead_ref = None
    for ref in ("origin/main", "@{u}"):
        rc2, out2, _ = run(["git", "-C", REPO_ROOT, "rev-list", "--count",
                            ref + "..main"], timeout=30)
        if rc2 == 0:
            try:
                ahead = int(out2.strip())
                ahead_ref = ref
                break
            except ValueError:
                continue
    log_event({"event": "merge-detected", "head": head[:12],
               "prev": prev[:12], "ahead_of_" + (ahead_ref or "remote"):
               ahead})
    if ahead is not None and ahead > PUSH_THRESHOLD and \
            state.get("push_suggested_head") != head:
        suggested = post_comment(
            state, FLAG_ISSUE,
            "[OBSERVER] main advanced to {0} and is {1} commits ahead of "
            "{2} (threshold {3}). Suggested next step - paste this to "
            "publish the wave:\n\n    cd {4} && git push\n".format(
                head[:12], ahead, ahead_ref, PUSH_THRESHOLD, REPO_ROOT))
        if suggested:
            state["push_suggested_head"] = head

def scan_doctrine_files():
    snapshot = {}
    budget = {"files": 0}
    cap = 800

    def add_file(path):
        if budget["files"] >= cap:
            return
        budget["files"] += 1
        try:
            with open(path, "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
            snapshot[os.path.relpath(path, REPO_ROOT)] = digest
        except OSError:
            pass

    def walk(base, depth):
        if depth > 4 or budget["files"] >= cap:
            return
        try:
            entries = sorted(os.listdir(base))
        except OSError:
            return
        for entry in entries:
            if entry.startswith(".git"):
                continue
            path = os.path.join(base, entry)
            if os.path.isdir(path):
                walk(path, depth + 1)
            elif entry.endswith(".md"):
                add_file(path)

    if not REPO_ROOT:
        return snapshot
    for rel in DOCTRINE_DIRS:
        walk(os.path.join(REPO_ROOT, rel), 1)
    for rel in DOCTRINE_FILES:
        add_file(os.path.join(REPO_ROOT, rel))
    return snapshot

DOC_UNIVERSE = {"paths": [], "basenames": {}}

def build_doc_universe():
    if DOC_UNIVERSE["paths"] or not REPO_ROOT:
        return
    roots = [os.path.join(REPO_ROOT, "docs"),
             os.path.join(REPO_ROOT, ".crosslink", "knowledge")]
    count = 0
    for base in roots:
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in sorted(dirnames)
                           if d != ".git"][:64]
            for fn in sorted(filenames):
                if fn.endswith(".md") and count < 800:
                    rel = os.path.relpath(os.path.join(dirpath, fn),
                                          REPO_ROOT)
                    DOC_UNIVERSE["paths"].append(rel)
                    DOC_UNIVERSE["basenames"].setdefault(fn, []).append(rel)
                    count += 1
    try:
        root_listing = sorted(os.listdir(REPO_ROOT))
    except OSError:
        root_listing = []
    for fn in root_listing:
        if fn.endswith(".md"):
            DOC_UNIVERSE["basenames"].setdefault(fn, []).append(fn)

def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()[1:]
    fm = {}
    key = None
    for line in lines:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            rest = m.group(2).strip()
            if rest in ("", "[]"):
                fm[key] = []
            elif rest.startswith("["):
                inner = rest.strip("[]")
                fm[key] = [item.strip().strip("\"") for item in
                           inner.split(",") if item.strip()]
            else:
                fm[key] = [rest.strip("\"")]
        elif key and re.match(r"^\s+-\s+(.+)$", line):
            fm[key].append(re.match(r"^\s+-\s+(.+)$", line).group(1)
                           .strip().strip("\""))
    return fm

PATHISH = re.compile(r"\.(md|py|sh|json|ya?ml|toml|txt|cfg|ini)$")

def builtin_existence_validate(doc_rel):
    """DIS V1 existence-validator stand-in: cited paths must resolve."""
    findings = []
    abs_path = os.path.join(REPO_ROOT, doc_rel)
    try:
        with open(abs_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        return ["document unreadable: {0}".format(exc)]
    fm = parse_frontmatter(text)
    citations = []
    for key in ("depends_on", "consumed_by", "related_documents",
                "supersedes"):
        for item in fm.get(key, []):
            if item and not item.startswith(("http://", "https://")):
                citations.append(item)
    for m in re.finditer(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        target = m.group(1)
        if not target.startswith(("http://", "https://", "mailto:")):
            citations.append(target)
    for m in re.finditer(r"`([^`\n]+)`", text):
        token = m.group(1).strip()
        if PATHISH.search(token) or "/" in token:
            if not token.startswith(("http://", "https://")):
                citations.append(token)

    def resolves(ref):
        for base in (REPO_ROOT, os.path.dirname(abs_path)):
            if os.path.exists(os.path.join(base, ref)):
                return True
        bare = os.path.basename(ref)
        return bare in DOC_UNIVERSE["basenames"]

    seen = set()
    for ref in citations:
        if ref in seen:
            continue
        seen.add(ref)
        if "{" in ref or "<" in ref or ref.endswith("/"):
            continue
        if not resolves(ref):
            findings.append("unresolved citation: {0}".format(ref))
    return findings

def external_existence_validate(doc_rel):
    rc, out, err = run([DIS_VALIDATOR, REPO_ROOT,
                        os.path.join(REPO_ROOT, doc_rel)], timeout=180)
    if rc == 0:
        return []
    lines = [ln.strip() for ln in (out or err or "").splitlines()
             if ln.strip()]
    return lines or ["external DIS validator exited {0}".format(rc)]

def dependents_of(changed_rel, index):
    deps = set()
    base = os.path.basename(changed_rel)
    for doc, fm in index.items():
        refs = []
        for key in ("depends_on", "related_documents"):
            refs.extend(fm.get(key, []))
        for ref in refs:
            if ref == changed_rel or os.path.basename(ref) == base:
                deps.add(doc)
    for doc, fm in index.items():
        for ref in fm.get("consumed_by", []):
            if ref == changed_rel or os.path.basename(ref) == base:
                deps.add(doc)
    deps.discard(changed_rel)
    return sorted(deps)

def wave_doctrine(state):
    if not REPO_ROOT:
        return
    current = scan_doctrine_files()
    previous = state.get("doctrine_snapshot") or {}
    state["doctrine_snapshot"] = current
    if not previous:
        return  # first cycle: baseline only, never alert on bootstrap
    changed = [k for k in current if k in previous and
               previous[k] != current[k]]
    if not changed:
        return
    build_doc_universe()
    index = {}
    for doc in DOC_UNIVERSE["paths"]:
        try:
            with open(os.path.join(REPO_ROOT, doc), encoding="utf-8",
                      errors="replace") as fh:
                index[doc] = parse_frontmatter(fh.read(40000))
        except OSError:
            continue
    for edited in changed:
        deps = dependents_of(edited, index)
        log_event({"event": "doctrine-edit", "file": edited,
                   "dependents": deps})
        for dep in deps:
            if DIS_VALIDATOR and os.path.isfile(DIS_VALIDATOR):
                findings = external_existence_validate(dep)
            else:
                findings = builtin_existence_validate(dep)
            fingerprint = hashlib.sha256(
                "\n".join(sorted(findings)).encode("utf-8")).hexdigest()
            known = state.get("doctrine_findings", {}).get(dep)
            if findings and known != fingerprint:
                preview = "\n".join("- " + f for f in findings[:10])
                post_comment(
                    state, FLAG_ISSUE,
                    "[DIS] existence-validator findings in {0} (upstream "
                    "edit: {1}):\n{2}\n({3} finding(s); re-alerts "
                    "suppressed until the findings change)".format(
                        dep, edited, preview, len(findings)))
                state.setdefault("doctrine_findings", {})[dep] = fingerprint
            elif not findings and known:
                state.get("doctrine_findings", {}).pop(dep, None)
                log_event({"event": "doctrine-findings-healed",
                           "dependent": dep, "upstream": edited})
            else:
                log_event({"event": "doctrine-validation-clean",
                           "dependent": dep, "upstream": edited,
                           "finding_count": 0})

# ---------------------------------------------------------------------------
# F2 (#456 revised scope): event-driven fast path over opencode.log.
# A byte-offset cursor reads ONLY new bytes each cycle; lines are classified
# (PARKED-RETRYING / CONSENT-GATE-FATAL / RETRY-EXHAUSTED-DEAD / UNKNOWN)
# and non-healthy classifications fire the SAME cycle. The expensive
# liveness walk stays on its own slower cadence.
# ---------------------------------------------------------------------------

def classify_log_line(line):
    """(class, session_id) for one log line; class None = uninteresting."""
    if "AI_" not in line:
        return None, None
    m = re.search(r"session\.id=(ses_[A-Za-z0-9]+)", line)
    sid = m.group(1) if m else None
    is_api_err = re.search(r"AI_APICallError", line) is not None
    if is_api_err and re.search(r"retry[-_ ]after", line, re.IGNORECASE):
        return "PARKED-RETRYING", sid
    if is_api_err and re.search(r"opt-?in|consent|approv", line,
                                re.IGNORECASE):
        return "CONSENT-GATE-FATAL", sid
    if re.search(r"AI_RetryError", line) and \
            re.search(r"exhaust", line, re.IGNORECASE):
        return "RETRY-EXHAUSTED-DEAD", sid
    if is_api_err or re.search(r"AI_[A-Za-z]+Error", line):
        return "UNKNOWN", sid
    return None, sid

def read_new_log_lines(state):
    """Byte-offset cursor read. Rotation/first-sight baselines at EOF so
    history is never re-classified; truncation resets to 0."""
    result = {"lines": [], "baseline": False}
    if not OPENCODE_LOG or not os.path.isfile(OPENCODE_LOG):
        return result
    try:
        st = os.stat(OPENCODE_LOG)
    except OSError:
        return result
    cur = state.get("log_cursor") or {}
    if cur.get("ino") != st.st_ino:
        state["log_cursor"] = {"ino": st.st_ino, "offset": st.st_size}
        result["baseline"] = True
        log_event({"event": "fastpath-baseline",
                   "rotated": bool(cur), "size": st.st_size})
        return result
    offset = cur.get("offset", 0)
    if offset > st.st_size:
        offset = 0  # truncated in place: start over
    if st.st_size == offset:
        return result
    try:
        with open(OPENCODE_LOG, "rb") as fh:
            fh.seek(offset)
            data = fh.read(FAST_READ_CAP)
            new_offset = offset + len(data)
        # avoid classifying a partial trailing line when capped mid-line
        if new_offset < st.st_size and data:
            idx = data.rfind(b"\n")
            if idx >= 0:
                data = data[:idx + 1]
                new_offset = offset + len(data)
    except OSError:
        return result
    state["log_cursor"] = {"ino": st.st_ino, "offset": new_offset}
    text = data.decode("utf-8", errors="replace")
    result["lines"] = [ln for ln in text.splitlines() if ln.strip()]
    return result

def fast_path_scan(state):
    if not FAST_PATH or not OPENCODE_LOG:
        return
    scan = read_new_log_lines(state)
    if scan["baseline"] or not scan["lines"]:
        return
    seen = state.get("fastpath_seen", {})
    now = time.time()
    for key, ts in list(seen.items()):
        if not isinstance(ts, (int, float)) or now - ts > FASTPATH_DEDUP_SECS:
            seen.pop(key, None)
    counts = {}
    for line in scan["lines"]:
        cls, sid = classify_log_line(line)
        if not cls:
            continue
        counts[cls] = counts.get(cls, 0) + 1
        dedup_key = cls + ":" + (sid or "unattributed")
        if now - seen.get(dedup_key, 0) < FASTPATH_DEDUP_SECS:
            continue
        seen[dedup_key] = now
        agent_name = None
        if sid:
            for a, r in state["agents"].items():
                if sid in (r.get("session_ids") or []):
                    agent_name = a
                    break
        log_event({"event": "fastpath-classification", "class": cls,
                   "session": sid, "agent": agent_name,
                   "line": line[:300]})
        if cls == "PARKED-RETRYING":
            li = {"retry_after": parse_retry_after([line]),
                  "rate_limited": True, "tail": [line],
                  "model": None, "provider": None}
            if agent_name and agent_name in state["agents"]:
                rec = state["agents"][agent_name]
                if rec.get("phase") in ("active", "parked"):
                    prow = {"agent": agent_name,
                            "verdict": rec.get("verdict",
                                               "RUNNING-ALIVE")}
                    act_parked(state, prow, rec, li)
            else:
                post_comment(state, FLAG_ISSUE,
                             "[OBSERVER][FAST] PARKED-RETRYING detected "
                             "(unattributed session {0}); retry-after "
                             "evidence recorded.".format(sid or "?"))
        elif cls in ("CONSENT-GATE-FATAL", "RETRY-EXHAUSTED-DEAD"):
            if agent_name and agent_name in state["agents"]:
                rec = state["agents"][agent_name]
                rec["fast_path_fatal"] = {"class": cls, "ts": now_iso()}
            post_comment(state, FLAG_ISSUE,
                         "[OBSERVER][FAST] {0} session={1} agent={2}: "
                         "fatal log signature; agent cannot proceed "
                         "without operator action.".format(
                             cls, sid or "?", agent_name or "unknown"))
        elif cls == "UNKNOWN":
            post_comment(state, FLAG_ISSUE,
                         "[OBSERVER][FAST] UNKNOWN AI-error signature "
                         "session={0} for review: {1}".format(
                             sid or "?", line[:200]))
    state["fastpath_seen"] = seen
    if counts:
        log_event({"event": "fastpath-summary", "counts": counts,
                   "lines_read": len(scan["lines"])})

# ---------------------------------------------------------------------------
# Main cycle
# ---------------------------------------------------------------------------

def main():
    try:
        data = json.load(sys.stdin)
    except ValueError as exc:
        log_event({"event": "cycle-input-invalid", "err": str(exc)})
        print(json.dumps({"error": "invalid-input"}))
        return 1
    state = load_state()
    state.setdefault("agents", {})
    rows = data.get("agents", [])
    scanned = set()

    for row in rows:
        agent = row.get("agent", "")
        if not agent:
            continue
        scanned.add(agent)
        process_agent(state, row)

    # Agents tracked but absent from this scan: verify physical cleanup.
    for agent in sorted(set(state["agents"]) - scanned):
        rec = state["agents"][agent]
        phase = rec.get("phase", "active")
        wt_present = os.path.isdir(os.path.join(WORKTREES_ROOT, agent))
        if phase == "frozen-handled":
            if wt_present:
                flag_for_sweep(agent, "post-termination-orphan-worktree")
                rec["phase"] = "orphan-flagged"
            else:
                rec["phase"] = "cleaned"
                log_event({"event": "cleanup-verified", "agent": agent,
                           "detail": "worktree removed after termination"})
        elif phase in ("active", "parked") and not wt_present:
            rec["phase"] = "cleaned-external"
            log_event({"event": "vanished-externally", "agent": agent,
                       "detail": "tracked agent left the scan; worktree "
                                 "already removed"})

    # F2: event-driven fast path fires BEFORE wave checks so classifications
    # land in the same cycle they appear in the log.
    fast_path_scan(state)

    # Simultaneous-parking alert (shared quota exhaustion signal).
    parked = [a for a, r in state["agents"].items()
              if r.get("phase") == "parked"]
    if len(parked) >= PARKED_ALERT_COUNT and \
            not state.get("parked_wave_alerted"):
        post_comment(state, FLAG_ISSUE,
                     "[OBSERVER] {0} agents parked simultaneously "
                     "({1}): shared quota pool exhaustion suspected, not "
                     "individual failure. No kills issued; resume_at "
                     "recorded per agent.".format(
                         len(parked), ", ".join(sorted(parked))))
        state["parked_wave_alerted"] = True
    elif len(parked) < PARKED_ALERT_COUNT:
        state["parked_wave_alerted"] = False

    wave_merge(state)
    wave_doctrine(state)

    err = save_state(state)
    if err:
        log_event({"event": "state-save-failed", "err": err})

    phases = {}
    for agent, rec in state["agents"].items():
        phases[rec.get("phase", "unknown")] = \
            phases.get(rec.get("phase", "unknown"), 0) + 1
    summary = {"scanned": len(rows), "tracked": len(state["agents"]),
               "phases": phases, "parked_now": len(parked),
               "actions_used_window": len(state.get("action_window", [])),
               "dry_run": DRY_RUN}
    print(json.dumps(summary, separators=(",", ":")))
    return 0

sys.exit(main())
'

cycle_start=$(date +%s)
consecutive_errors=0
while :; do
    cycle_ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    if [ -n "$OBSERVER_INPUT_JSON" ]; then
        out="$(cat "$OBSERVER_INPUT_JSON" 2>/dev/null)"
        liveness_rc=$?
    else
        out="$(python3 "$LIVENESS_PY" --json --all 2>/dev/null)"
        liveness_rc=$?
    fi

    if [ "$liveness_rc" -ne 0 ] || [ -z "$out" ]; then
        consecutive_errors=$((consecutive_errors + 1))
        printf '%s' "$consecutive_errors" > "$ERRCOUNT_FILE" 2>/dev/null
        printf '{"ts":"%s","event":"error","kind":"liveness-failed","rc":%s,"consecutive":%s}\n' \
            "$cycle_ts" "$liveness_rc" "$consecutive_errors" >> "$EVENTS_FILE"
        if [ "$consecutive_errors" -ge "$OBSERVER_MAX_CONSECUTIVE_ERRORS" ]; then
            printf '{"ts":"%s","event":"fatal","kind":"consecutive-error-cap","consecutive":%s}\n' \
                "$cycle_ts" "$consecutive_errors" >> "$EVENTS_FILE"
            exit 1
        fi
    else
        consecutive_errors=0
        printf '%s' 0 > "$ERRCOUNT_FILE" 2>/dev/null

        if ! compact="$(printf '%s' "$out" | python3 -c \
                'import json,sys; sys.stdout.write(json.dumps(json.load(sys.stdin), separators=(",", ":"))+"\n")' \
                2>/dev/null)" || [ -z "$compact" ]; then
            printf '{"ts":"%s","event":"error","kind":"json-parse-failed"}\n' \
                "$cycle_ts" >> "$EVENTS_FILE"
        else
            summary="$(printf '%s\n' "$compact" | python3 -c "$CYCLE_PROG" 2>>"$OBSERVER_STATE_DIR/python-stderr.log")"
            prog_rc=$?
            if [ -n "$summary" ]; then
                printf '{"ts":"%s","event":"cycle","rc":%s,"summary":%s}\n' \
                    "$cycle_ts" "$prog_rc" "$summary" >> "$EVENTS_FILE"
            else
                printf '{"ts":"%s","event":"error","kind":"cycle-program-failed","rc":%s}\n' \
                    "$cycle_ts" "$prog_rc" >> "$EVENTS_FILE"
            fi
        fi
    fi

    [ "$ONCE" -eq 1 ] && break
    sleep "$OBSERVER_INTERVAL"
done
