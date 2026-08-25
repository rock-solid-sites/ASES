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
# Dual-store backup subsystem (#460 F4; .crosslink/knowledge/data-retention.md):
#   A wave-level pass (interval-gated, default daily — the live stores are
#   multi-GB, so this is NEVER per-cycle) that:
#     (a) hot-copies BOTH session stores (sqlite3 .backup; discovery mirrors
#         scripts/session-union.py: main:opencode.db + fork:opencode-fork-pp3g.db),
#         verifying each copy with PRAGMA integrity_check + sha256;
#     (b) incrementally exports NEW session rows from THE SNAPSHOT COPY
#         (zero load on the live DB) as compressed JSONL plus an
#         uncompressed index under ~/opencode-archive/, keyed
#         (store, session_id); a per-(store,table) time_updated watermark
#         advances ONLY when local read-back is GREEN AND (rclone sync is
#         GREEN OR remote-unconfigured local mode is explicitly
#         acknowledged); sync RED holds every watermark and queues the
#         artifacts into a retry backlog for later passes (#466 F2);
#     (c) syncs the archive off-server via rclone ONLY when
#         OBSERVER_RCLONE_REMOTE names a remote that exists in
#         `rclone listremotes`; otherwise an explicit sync-pending entry is
#         recorded (graceful local mode — never blocks);
#     (d) performs destination-side read-back verification (decompress,
#         row count, sha256 vs manifest; `rclone cat` when remote) and
#         appends GREEN/RED entries to <archive>/verification.log.
#   Deletion gating: NOTHING is ever deleted from the live stores. The pass
#   emits a prune-gate REPORT (operator-manual deletion per policy v1):
#   sessions older than OBSERVER_PRUNE_AGE_DAYS are listed prune-eligible
#   ONLY when covered by GREEN-verified exports; RED/unverified windows are
#   explicitly excluded. Hot-backup generations beyond OBSERVER_BACKUP_KEEP
#   (Observer's OWN artefacts, not live data) are pruned after a verified
#   newer copy exists.
#
# Admission-policy absorption (#460 F5):
#   Launch-contract validation as config-driven pre-dispatch checks over
#   each tracked agent's KICKOFF.md, absorbing the would-be plugin family
#   (#448/#445/#446/#451/#452) into one Observer policy surface — NO new
#   plugin files:
#     model-declared-and-valid  — every model ID in the contract resolves
#                                 against the LIVE opencode models catalog
#                                 (`opencode models <provider>`, TTL-cached;
#                                 command template OBSERVER_MODELS_CMD
#                                 overridable for deterministic tests)
#     issue-exists              — crosslink issue show <n> succeeds
#     issue-claimed             — crosslink locks check <n> reports a lock
#     estimate-declared         — contract matches OBSERVER_ADMISSION_ESTIMATE_RE
#   Every check appends an admission-check event to events.jsonl (audit
#   trail); failing fingerprints alert the flag issue, deduped until the
#   failure set changes.
#
# Wave-anomaly detection (#460 F6):
#   When EVERY agent that was active/parked last cycle is absent from the
#   current scan simultaneously (no terminal verdicts, no Observer-executed
#   cleanup), the transition emits a platform-restart signature alert to
#   the flag issue plus a wave-anomaly event. Deduped per episode; re-arms
#   when any agent reappears. Normal terminal wind-down never triggers it.
#
# Safety model:
#   - Never touches live agent processes or worktrees directly: every
#     mutation goes through crosslink CLI surfaces (kickoff stop/cleanup,
#     issue comment).
#   - The backup pass never opens the live databases for writing: hot copies
#     go through sqlite3 .backup; exports read the static snapshot copy.
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
#
# Strict failure mode (FIX 2, #469 CRITICAL):
#   set -euo pipefail. Every command whose NONZERO exit is EXPECTED is an
#   explicit, documented exception (rc captured via '|| rc=$?' and handled);
#   nothing else may fail silently. Critical failures halt or escalate
#   loudly per the action table: unwritable state dir -> fatal exit;
#   cycle-program failure -> counted toward the consecutive-error cap
#   (halt-not-loop); state write failure -> nonzero cycle rc so the cap can
#   halt before duplicate mutations; backup hot-copy/verification/sync
#   failure -> deduped loud alert + shortened retry backoff instead of a
#   silent full-interval skip.

set -eu
set -o pipefail

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
# F4 (#460): dual-store backup subsystem (data-retention.md policy).
OBSERVER_BACKUP_ENABLED="${OBSERVER_BACKUP_ENABLED:-1}"
OBSERVER_BACKUP_INTERVAL_MINS="${OBSERVER_BACKUP_INTERVAL_MINS:-1440}"
OBSERVER_ARCHIVE_DIR="${OBSERVER_ARCHIVE_DIR:-$HOME/opencode-archive}"
OBSERVER_STORES_ROOT="${OBSERVER_STORES_ROOT:-$HOME/.local/share/opencode}"
OBSERVER_STORES="${OBSERVER_STORES:-main:opencode.db,fork:opencode-fork-pp3g.db}"
OBSERVER_BACKUP_KEEP="${OBSERVER_BACKUP_KEEP:-1}"
# FIX 2 (#469): retry backoff after a FAILED backup pass (a failed pass must
# not silently skip for a full interval).
OBSERVER_BACKUP_RETRY_MINS="${OBSERVER_BACKUP_RETRY_MINS:-15}"
OBSERVER_RCLONE_REMOTE="${OBSERVER_RCLONE_REMOTE:-}"
OBSERVER_PRUNE_AGE_DAYS="${OBSERVER_PRUNE_AGE_DAYS:-30}"
# F5 (#460): admission-policy absorption (config-driven checks).
OBSERVER_ADMISSION_ENABLED="${OBSERVER_ADMISSION_ENABLED:-1}"
OBSERVER_ADMISSION_PROVIDERS="${OBSERVER_ADMISSION_PROVIDERS:-opencode:opencode-go}"
# NOTE: default assigned via single quotes, NOT ${VAR:-...}: a closing
# brace inside the :-default word leaks an extra } into the SET-var value
# (bash does not nest-match the terminator), corrupting the {provider}
# placeholder to {provider}}.
OBSERVER_MODELS_CMD="${OBSERVER_MODELS_CMD:-}"
if [ -z "$OBSERVER_MODELS_CMD" ]; then
    OBSERVER_MODELS_CMD='opencode models {provider}'
fi
OBSERVER_ADMISSION_CATALOG_TTL_SECS="${OBSERVER_ADMISSION_CATALOG_TTL_SECS:-1800}"
OBSERVER_ADMISSION_ESTIMATE_RE="${OBSERVER_ADMISSION_ESTIMATE_RE:-(?i)\\bestimat}"

export OB_REPO_ROOT OB_STATE_DIR OB_FLAG_ISSUE OB_EVIDENCE_LINES \
    OB_PANE_LINES OB_PUSH_AHEAD_THRESHOLD OB_PARKED_ALERT_COUNT \
    OB_PARKED_DEFAULT_RESUME_MINS OB_MAX_ACTIONS_PER_HOUR \
    OB_STALE_ESCALATE_CYCLES OB_OPENCODE_LOG OB_DIS_VALIDATOR \
    OB_DRY_RUN OB_DOCTRINE_DIRS OB_DOCTRINE_FILES \
    OB_FAST_PATH OB_FAST_READ_CAP OB_FASTPATH_DEDUP_SECS \
    OB_COMMIT_STALE_MINS \
    OB_BACKUP_ENABLED OB_BACKUP_INTERVAL_MINS OB_ARCHIVE_DIR \
    OB_STORES_ROOT OB_STORES OB_BACKUP_KEEP OB_BACKUP_RETRY_MINS \
    OB_RCLONE_REMOTE \
    OB_PRUNE_AGE_DAYS \
    OB_ADMISSION_ENABLED OB_ADMISSION_PROVIDERS OB_MODELS_CMD \
    OB_ADMISSION_CATALOG_TTL_SECS OB_ADMISSION_ESTIMATE_RE

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
OB_BACKUP_ENABLED="$OBSERVER_BACKUP_ENABLED"
OB_BACKUP_INTERVAL_MINS="$OBSERVER_BACKUP_INTERVAL_MINS"
OB_ARCHIVE_DIR="$OBSERVER_ARCHIVE_DIR"
OB_STORES_ROOT="$OBSERVER_STORES_ROOT"
OB_STORES="$OBSERVER_STORES"
OB_BACKUP_KEEP="$OBSERVER_BACKUP_KEEP"
OB_BACKUP_RETRY_MINS="${OBSERVER_BACKUP_RETRY_MINS:-15}"
OB_RCLONE_REMOTE="$OBSERVER_RCLONE_REMOTE"
OB_PRUNE_AGE_DAYS="$OBSERVER_PRUNE_AGE_DAYS"
OB_ADMISSION_ENABLED="$OBSERVER_ADMISSION_ENABLED"
OB_ADMISSION_PROVIDERS="$OBSERVER_ADMISSION_PROVIDERS"
OB_MODELS_CMD="$OBSERVER_MODELS_CMD"
OB_ADMISSION_CATALOG_TTL_SECS="$OBSERVER_ADMISSION_CATALOG_TTL_SECS"
OB_ADMISSION_ESTIMATE_RE="$OBSERVER_ADMISSION_ESTIMATE_RE"

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

# FIX 1 (#465 F1, #460): CWD hermeticity. Every external invocation (git,
# crosslink, opencode, sqlite3, rclone, tmux) and every state-path resolution
# must derive from absolute paths, never from the process CWD: a detached
# tmux launch inherits the launcher CWD, and crosslink silently no-ops
# outside a crosslink repository (demonstrated in #465: rc=0 in-project,
# rc=1 from /tmp). Two layers:
#   (a) normalize every path-like env var to an ABSOLUTE path BEFORE any cd;
#   (b) anchor the process CWD to the Observer's own crosslink repository
#       root so inherited-CWD subprocesses land in valid repo context too.
# Relative OBSERVER_* inputs are resolved against the LAUNCH directory (the
# only moment the original CWD is meaningful).
normalize_abs() { # normalize_abs <path>  -> absolute (against launch CWD)
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *)  printf '%s\n' "$(pwd)/$1" ;;
    esac
}
OBSERVER_STATE_DIR="$(normalize_abs "$OBSERVER_STATE_DIR")"
[ -n "${OBSERVER_OPENCODE_LOG:-}" ] && \
    OBSERVER_OPENCODE_LOG="$(normalize_abs "$OBSERVER_OPENCODE_LOG")"
[ -n "${OBSERVER_INPUT_JSON:-}" ] && \
    OBSERVER_INPUT_JSON="$(normalize_abs "$OBSERVER_INPUT_JSON")"
[ -n "${OBSERVER_LIVENESS_PY:-}" ] && \
    LIVENESS_PY="$(normalize_abs "$LIVENESS_PY")"
[ -n "${OBSERVER_ARCHIVE_DIR:-}" ] && \
    OBSERVER_ARCHIVE_DIR="$(normalize_abs "$OBSERVER_ARCHIVE_DIR")"
[ -n "${OBSERVER_STORES_ROOT:-}" ] && \
    OBSERVER_STORES_ROOT="$(normalize_abs "$OBSERVER_STORES_ROOT")"
[ -n "${OBSERVER_DIS_VALIDATOR:-}" ] && \
    OBSERVER_DIS_VALIDATOR="$(normalize_abs "$OBSERVER_DIS_VALIDATOR")"

# Crosslink repo context: the Observer's OWN repository (where .crosslink
# lives), discovered by walking up from this script. NOT necessarily the
# monitored OB_REPO_ROOT (tests point that at fixture trees). Env override
# wins; fallback is the monitored repo root.
discover_crosslink_root() {
    local d="$SCRIPT_DIR"
    while [ "$d" != "/" ]; do
        if [ -d "$d/.crosslink" ]; then
            printf '%s\n' "$d"
            return 0
        fi
        d="$(dirname "$d")"
    done
    printf '%s\n' "$OB_REPO_ROOT"
}
OB_CROSSLINK_ROOT="${OBSERVER_CROSSLINK_ROOT:-$(discover_crosslink_root)}"
export OB_CROSSLINK_ROOT

# Anchor the process CWD (layer b). Loud failure per FIX 2: without a valid
# anchor, every crosslink surface would silently no-op for the whole run.
if ! cd "$OB_CROSSLINK_ROOT" 2>/dev/null; then
    printf '{"ts":"%s","event":"fatal","kind":"crosslink-root-unresolvable","root":"%s"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$OB_CROSSLINK_ROOT" >&2
    exit 1
fi

EVENTS_FILE="$OBSERVER_STATE_DIR/events.jsonl"
ERRCOUNT_FILE="$OBSERVER_STATE_DIR/.consecutive-errors"

# FIX 2 (#469): state-dir creation failures were suppressed with
# 2>/dev/null, leaving subsequent writes to fail mysteriously. Loud fatal:
# without a writable state dir the observer is blind and must not run.
if ! mkdir -p "$OBSERVER_STATE_DIR/evidence" 2>/dev/null; then
    printf '{"ts":"%s","event":"fatal","kind":"state-dir-unwritable","dir":"%s"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$OBSERVER_STATE_DIR" >&2
    exit 1
fi
[ -f "$EVENTS_FILE" ] || : >> "$EVENTS_FILE" 2>/dev/null

# FIX 2 (#469): events are the audit trail; a failed append must not pass
# silently. Documented exception to strict mode: fall back LOUDLY to stderr
# instead of killing supervision over a transient write error.
emit_event() { # emit_event <complete-json-line>
    printf '%s\n' "$1" >> "$EVENTS_FILE" 2>/dev/null \
        || printf '%s\n' "$1" >&2
}

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
    emit_event "$(printf '{"ts":"%s","event":"fatal","kind":"missing-liveness-script","path":"%s"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$LIVENESS_PY")"
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
import gzip
import hashlib
import json
import os
import re
import shutil
import sqlite3
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
# FIX 1 (#465 F1): crosslink CLI context root. The monitored repo (fixtures
# in tests) is NOT necessarily a crosslink repository, so crosslink
# invocations are pinned to the repo the Observer itself runs from,
# discovered by the bash wrapper (env OBSERVER_CROSSLINK_ROOT override;
# falls back to REPO_ROOT).
CROSSLINK_ROOT = env("OB_CROSSLINK_ROOT") or env("OB_REPO_ROOT")
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
BACKUP_ENABLED = env("OB_BACKUP_ENABLED", "1") == "1"
BACKUP_INTERVAL_MINS = env_int("OB_BACKUP_INTERVAL_MINS", 1440)
ARCHIVE_DIR = env("OB_ARCHIVE_DIR") or os.path.join(
    os.path.expanduser("~"), "opencode-archive")
STORES_ROOT = env("OB_STORES_ROOT") or os.path.join(
    os.path.expanduser("~"), ".local/share/opencode")
BACKUP_KEEP = env_int("OB_BACKUP_KEEP", 1)
# FIX 2 (#469 / #465 F7): a FAILED backup pass must not silently wait a full
# interval (default 1440 min) before retrying; it retries after this much.
BACKUP_RETRY_MINS = env_int("OB_BACKUP_RETRY_MINS", 15)
RCLONE_REMOTE = env("OB_RCLONE_REMOTE").strip()
PRUNE_AGE_DAYS = env_int("OB_PRUNE_AGE_DAYS", 30)
STORES = []
for _chunk in env("OB_STORES").split(","):
    _chunk = _chunk.strip()
    if _chunk and ":" in _chunk:
        _label, _fname = _chunk.split(":", 1)
        STORES.append((_label.strip(), _fname.strip()))
ADMISSION_ENABLED = env("OB_ADMISSION_ENABLED", "1") == "1"
ADMISSION_PROVIDERS = [p for p in
                       env("OB_ADMISSION_PROVIDERS").split(":") if p]
MODELS_CMD_TMPL = env("OB_MODELS_CMD", "opencode models {provider}")
ADMISSION_CATALOG_TTL = env_int("OB_ADMISSION_CATALOG_TTL_SECS", 1800)
ADMISSION_ESTIMATE_RE = env("OB_ADMISSION_ESTIMATE_RE",
                            r"(?i)\bestimat")

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
    except OSError as exc:
        # FIX 2 (#469): audit-trail write failures are never silent (stderr
        # mirror); they also must not kill supervision over a transient
        # write error, so this is a documented swallow-with-witness.
        sys.stderr.write(
            "observer: event-log-write-failed: {0}\n".format(exc))

def run(cmd, timeout=90, cwd=None):
    """Run a subprocess and return (rc, stdout, stderr).

    FIX 2 (#469): rc is ALWAYS returned; callers decide. The unused
    timeout_ok parameter (dead code, #467 M4) is removed. FIX 1: callers
    pass cwd= explicitly for CWD-sensitive binaries (crosslink); nothing
    here depends on the inherited process CWD.
    """
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd)
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
                     timeout=120, cwd=CROSSLINK_ROOT)
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
    rc, out, _ = run(["crosslink", "issue", "show", str(issue)], timeout=60,
                     cwd=CROSSLINK_ROOT)
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
        # Shakedown fix (#460, 2026-08-25): this early-return was SILENT.
        # During the 05:26-05:31 leftover-fleet triage the 24/hour mutation
        # budget was fully consumed by comments; when the healthy builders
        # legitimate cleanup fired at 05:54:54 the breaker denied it with
        # ZERO trace - no subprocess ran (so no out/err existed to log) and
        # the once-per-hour breaker-halt event had already fired at
        # 05:31:38. The failure surfaced only as cleanup_ok:false in the
        # transition-action event, i.e. archaeology. Every early-return now
        # emits the cleanup event with an explicit denial reason so a
        # denied cleanup is bounded and evidenced, never silent.
        log_event({"event": "cleanup", "agent": agent, "rc": None,
                   "denied": "breaker-cap",
                   "out": "",
                   "err": "mutation cap reached; cleanup not attempted"})
        return False
    if DRY_RUN:
        log_event({"event": "cleanup-dry-run", "agent": agent,
                   "cmd": "crosslink kickoff cleanup --only " + agent +
                          " --yes"})
        return True
    rc, out, err = run(["crosslink", "kickoff", "cleanup", "--only", agent,
                        "--yes"], timeout=180, cwd=CROSSLINK_ROOT)
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
                           timeout=90, cwd=CROSSLINK_ROOT)
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

def resolve_sweep(agent):
    """Shakedown #460 (2026-08-25): the pending-sweep file was append-only
    with no code path ever resolving an entry - a successful cleanup left
    the stale flag behind for the operator to reconcile by hand. When a
    cleanup succeeds and no orphan remains, close the loop: append an
    explicit resolution line (only if the agent has an unresolved flag)
    plus a force-sweep-resolved event."""
    try:
        if not os.path.isfile(SWEEP_FILE):
            return False
        last = None
        with open(SWEEP_FILE, encoding="utf-8") as fh:
            for ln in fh:
                parts = ln.split()
                if len(parts) >= 3 and parts[1] == agent:
                    last = parts[-1]
        if last is None or last.startswith("resolved-"):
            return False
        line = "{0} {1} resolved-by-cleanup-ok\n".format(now_iso(), agent)
        with open(SWEEP_FILE, "a", encoding="utf-8") as fh:
            fh.write(line)
        log_event({"event": "force-sweep-resolved", "agent": agent})
        return True
    except OSError as exc:
        log_event({"event": "force-sweep-resolve-failed", "agent": agent,
                   "err": str(exc)})
        return False

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
    # FIX 3 (#466 F3): deliverable verification gates cleanup. Observer
    # automates the exact lost-worktree class that produced the #460 data
    # loss (DONE-marked builder, uncommitted/unverified work, worktree
    # wiped). So: kickoff_cleanup fires ONLY after deliverable_check
    # PASSES (real committed file delta present on the branch). Failure or
    # indeterminacy -> NO cleanup, worktree preserved, force-sweep flag +
    # loud flag comment for the orchestrator.
    deliv = deliverable_check(branch)
    cleanup_ok = None  # None = gate not passed (skipped)
    orphan = None
    if deliv.get("deliverable_present"):
        cleanup_ok = kickoff_cleanup(state, agent)
        orphan = os.path.isdir(os.path.join(WORKTREES_ROOT, agent))
        if orphan:
            flag_for_sweep(agent,
                           "completed-but-worktree-remains-after-cleanup")
        elif cleanup_ok:
            # Shakedown #460: successful cleanup closes any prior
            # force-sweep flag for this agent (resolution flows through
            # code, not operator hand-reconciliation).
            resolve_sweep(agent)
    else:
        flag_for_sweep(agent,
                       "completed-deliverable-unverified-worktree-preserved")
        log_event({"event": "cleanup-skipped", "agent": agent,
                   "reason": "deliverable-unverified",
                   "branch": branch, "deliverable": deliv})
    duration_min = None
    if started:
        duration_min = round((time.time() - started) / 60.0, 1)
    if cleanup_ok is None:
        cleanup_field = "skipped-unverified-deliverable"
    elif DRY_RUN:
        cleanup_field = "dry-run"
    elif cleanup_ok:
        cleanup_field = "executed"
    else:
        cleanup_field = "failed"
    append_staging_row({
        "agent": agent, "outcome": "completed", "role": row.get("role"),
        "issue": issue, "model": loginfo.get("model"),
        "provider": loginfo.get("provider"), "branch": branch,
        "deliverable": deliv, "duration_min": duration_min,
        "cleanup": cleanup_field,
        "orphan_worktree": orphan,
        "evidence_bundle": ev["bundle"], "evidence_sha256": ev["sha256"],
    })
    rec["phase"] = "completed"
    rec.setdefault("handled", {})["DONE-CONFIRMED"] = now_iso()
    if cleanup_ok is None:
        message = ("[OBSERVER] COMPLETED agent={0} deliverable={1} "
                   "files_changed={2} merged={3}. Cleanup SKIPPED - "
                   "deliverable unverified (branch missing or no "
                   "committed file delta); worktree PRESERVED and "
                   "flagged for operator review before any sweep. "
                   "{4}".format(
                       agent,
                       deliv.get("deliverable_present"),
                       deliv.get("files_changed"), deliv.get("merged"),
                       evidence_summary_line(ev)))
    else:
        message = ("[OBSERVER] COMPLETED agent={0} deliverable={1} "
                   "files_changed={2} merged={3}. Deliverable verified; "
                   "scoped cleanup executed={4}. {5}".format(
                       agent,
                       deliv.get("deliverable_present"),
                       deliv.get("files_changed"), deliv.get("merged"),
                       "yes" if cleanup_ok else "NO",
                       evidence_summary_line(ev)))
    post_comment(state, issue or FLAG_ISSUE, message)
    log_event({"event": "transition-action", "action": "completed",
               "agent": agent, "issue": issue, "cleanup_ok": cleanup_ok,
               "cleanup_skipped": cleanup_ok is None,
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
        rc, out, _ = run(["crosslink", "issue", "show", issue], timeout=60,
                         cwd=CROSSLINK_ROOT)
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
            # FIX 4 (#466 F1): expiry alone is the weakest-evidence kill
            # trigger in the whole action table (a stale or misparsed
            # resume_at would auto-kill a correctly-waiting agent). Before
            # ANY expiry kill, re-scan the attributed log tail for a FRESH
            # rate-limit/retry-after signature; if one is live, extend the
            # park with resume_at = max(parsed, now + grace) instead.
            # Kill requires expiry AND no live parking evidence.
            li = loginfo()
            if li.get("rate_limited"):
                parsed = li.get("retry_after")
                grace = time.time() + PARKED_DEFAULT_MINS * 60
                new_resume = max(parsed, grace) if parsed else grace
                prev_resume = rec.get("resume_at")
                rec["resume_at"] = now_iso(new_resume)
                rec["resume_at_epoch"] = new_resume
                rec["resume_at_source"] = \
                    "park-extension-fresh-signature"
                log_event({"event": "parked-extended", "agent": agent,
                           "prev_resume_at": prev_resume,
                           "resume_at": rec["resume_at"],
                           "grace_floor_min": PARKED_DEFAULT_MINS,
                           "detail": "fresh rate-limit signature at "
                                     "expiry; park extended, kill "
                                     "suppressed"})
                state["agents"][agent] = rec
                return
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
# F4 (#460): dual-store backup subsystem per data-retention.md.
# Hot sqlite3 .backup of BOTH stores -> incremental session-row export
# (compressed JSONL + uncompressed index keyed (store,session_id)) read from
# THE SNAPSHOT COPY -> destination-side read-back verification appending
# GREEN/RED entries to verification.log -> rclone off-server sync when
# OBSERVER_RCLONE_REMOTE names an existing remote else explicit sync-pending
# flag -> prune-gate REPORT ONLY (deletion stays operator-manual v1; nothing
# is ever deleted from the live stores).
# ---------------------------------------------------------------------------

def verify_log_line(result, store, table, artifact, rows, digest,
                    destination, detail=""):
    line = "{0} | {1} | store={2} table={3} artifact={4} rows={5} " \
           "sha256={6} destination={7}".format(
               now_iso(), result, store, table, artifact, rows, digest,
               destination)
    if detail:
        line += " detail=" + detail
    try:
        with open(os.path.join(ARCHIVE_DIR, "verification.log"), "a",
                  encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        log_event({"event": "backup-verify-log-failed", "err": str(exc)})


def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1048576), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def backup_alert(state, key, subject, detail):
    """FIX 2 (#469): backup-critical failures (hot-copy failure, RED
    read-back, snapshot/export failure) escalate LOUDLY - a deduped alert
    comment to the flag issue per changed failure fingerprint - instead of
    continuing silently. Dedup key resets when the failure detail changes."""
    fp = hashlib.sha256("{0}:{1}".format(key, detail).encode(
        "utf-8", "replace")).hexdigest()[:12]
    alerted = state.setdefault("backup_alerted", {})
    if alerted.get(key) == fp:
        return
    alerted[key] = fp
    post_comment(state, FLAG_ISSUE,
                 "[OBSERVER][BACKUP] {0}: {1}. Data-retention extraction "
                 "degraded; watermark held for affected windows and the "
                 "pass will retry after {2} min (not a full interval)."
                 .format(subject, detail[:300], BACKUP_RETRY_MINS))


def hot_copy_store(label, fname, stamp):
    """sqlite3 .backup hot copy + integrity check + sha256. Returns
    (info, error) where info has path/sha256/bytes or None."""
    src = os.path.join(STORES_ROOT, fname)
    if not os.path.isfile(src):
        return None, "store-missing:" + src
    dest_dir = os.path.join(ARCHIVE_DIR, "hot-backups", label)
    dest = os.path.join(dest_dir, stamp + ".db")
    try:
        os.makedirs(dest_dir, exist_ok=True)
        free = shutil.disk_usage(ARCHIVE_DIR).free
        need = os.path.getsize(src) * 1.2 + 1048576
        if free < need:
            return None, "insufficient-disk:free={0} need={1}".format(
                free, need)
    except OSError as exc:
        return None, "fs-error:" + str(exc)[:120]
    rc, out, err = run(["sqlite3", src, ".backup " + dest], timeout=600)
    if rc != 0 or not os.path.isfile(dest):
        return None, "backup-failed:" + ((err or out or "").strip()[:150])
    try:
        conn = sqlite3.connect(dest)
        row = conn.execute("PRAGMA integrity_check").fetchone()
        conn.close()
    except sqlite3.Error as exc:
        return None, "integrity-error:" + str(exc)[:100]
    if not row or row[0] != "ok":
        return None, "integrity-report:" + str(row)[:100]
    digest = sha256_file(dest)
    if not digest:
        return None, "digest-failed"
    return {"path": dest, "sha256": digest,
            "bytes": os.path.getsize(dest)}, None


def prune_hot_generations(label, keep):
    """Prune Observer-owned hot-backup generations beyond keep (its OWN
    artefacts — never live data)."""
    d = os.path.join(ARCHIVE_DIR, "hot-backups", label)
    try:
        gens = sorted(f for f in os.listdir(d) if f.endswith(".db"))
    except OSError:
        return
    for old in gens[:-keep] if keep > 0 else gens:
        try:
            os.remove(os.path.join(d, old))
            log_event({"event": "backup-generation-pruned",
                       "store": label, "file": old})
        except OSError:
            pass


def snapshot_session_tables(conn):
    """Discover session tables at runtime (session-union.py pattern)."""
    tables = []
    try:
        for (name,) in conn.execute(
                "SELECT name FROM sqlite_master WHERE type=?", ("table",)):
            if name == "session" or name == "session_v2":
                cols = {r[1] for r in conn.execute(
                    "PRAGMA table_info({0})".format(name))}
                if {"id", "directory", "title", "time_created",
                    "time_updated"} <= cols:
                    tables.append(name)
    except sqlite3.Error:
        pass
    return sorted(tables)


def export_new_rows(conn, store, table, watermark):
    """Rows with time_updated > watermark from the SNAPSHOT copy."""
    q = ("SELECT id, directory, title, time_created, time_updated "
         "FROM {0} WHERE time_updated > ? ORDER BY time_updated ASC"
         ).format(table)
    try:
        return conn.execute(q, (watermark,)).fetchall()
    except sqlite3.Error as exc:
        log_event({"event": "backup-export-query-failed",
                   "store": store, "table": table, "err": str(exc)[:150]})
        return None


def write_export(store, table, rows):
    """Write gzip JSONL + append uncompressed index lines. Returns
    (rel_artifact, count, decompressed_sha256) or (None, 0, reason)."""
    day = now_iso()[:10]
    # Microsecond stamp: second-resolution names collided when two passes
    # ran within one second, silently overwriting the earlier artefact.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    exp_dir = os.path.join(ARCHIVE_DIR, "exports", day)
    idx_dir = os.path.join(ARCHIVE_DIR, "index")
    try:
        os.makedirs(exp_dir, exist_ok=True)
        os.makedirs(idx_dir, exist_ok=True)
        fname = "{0}-{1}-{2}.jsonl.gz".format(store, table, stamp)
        fpath = os.path.join(exp_dir, fname)
        h = hashlib.sha256()
        n = 0
        with gzip.open(fpath, "wb") as gz:
            for sid, directory, title, tc, tu in rows:
                rec = {"store": store, "session_id": sid,
                       "table": table,
                       "directory": directory, "title": title,
                       "time_created": tc, "time_updated": tu,
                       "source": "{0}:{1}".format(store, table)}
                line = (json.dumps(rec, separators=(",", ":")) +
                        "\n").encode("utf-8")
                gz.write(line)
                h.update(line)
                n += 1
        rel = os.path.join("exports", day, fname)
        with open(os.path.join(idx_dir, store + ".ndx"), "a",
                  encoding="utf-8") as idx:
            for sid, directory, title, tc, tu in rows:
                idx.write(json.dumps({
                    "store": store, "session_id": sid, "table": table,
                    "time_created": tc, "time_updated": tu,
                    "export_file": rel, "exported_at": now_iso()},
                    separators=(",", ":")) + "\n")
        return rel, n, h.hexdigest(), None
    except OSError as exc:
        return None, 0, None, "write-failed:" + str(exc)[:150]


def verify_export_readback(rel, expected_digest, expected_count):
    """Destination-side read-back: decompress the written artefact and
    compare row count + sha256 against the write-time manifest."""
    path = os.path.join(ARCHIVE_DIR, rel)
    try:
        h = hashlib.sha256()
        n = 0
        with gzip.open(path, "rb") as gz:
            for chunk in iter(lambda: gz.read(1048576), b""):
                h.update(chunk)
                n += chunk.count(b"\n")
        if n != expected_count:
            return False, "row-count-mismatch:{0}!={1}".format(
                n, expected_count)
        if h.hexdigest() != expected_digest:
            return False, "sha256-mismatch"
        return True, ""
    except (OSError, EOFError) as exc:
        return False, "readback-failed:" + str(exc)[:120]


def rclone_remote_ready():
    """True when OBSERVER_RCLONE_REMOTE names a configured remote."""
    if not RCLONE_REMOTE:
        return False
    rc, out, _ = run(["rclone", "listremotes"], timeout=30)
    if rc != 0:
        return False
    want = RCLONE_REMOTE.rstrip(":").lower()
    for ln in out.splitlines():
        if ln.strip().rstrip(":").lower() == want:
            return True
    return False


def rclone_sync_and_verify(new_rels):
    """Copy new artefacts + index to remote and read back via rclone cat.
    Returns (ok, detail)."""
    dest = RCLONE_REMOTE.rstrip(":") + ":opencode-archive"
    rc, _, err = run(["rclone", "copy",
                      os.path.join(ARCHIVE_DIR, "index"),
                      dest + "/index"], timeout=600)
    if rc != 0:
        return False, "index-sync-failed:" + (err or "")[:150]
    day_dirs = sorted(set(os.path.dirname(r) for r in new_rels))
    for d in day_dirs:
        rc, _, err = run(["rclone", "copy",
                          os.path.join(ARCHIVE_DIR, d), dest + "/" + d],
                         timeout=1800)
        if rc != 0:
            return False, "export-sync-failed:" + (err or "")[:150]
    # Destination-side read-back: hash every index file remotely.
    for label in sorted({s for s, _ in STORES}):
        local = os.path.join(ARCHIVE_DIR, "index", label + ".ndx")
        if not os.path.isfile(local):
            continue
        want = sha256_file(local)
        rc, out, err = run(["rclone", "cat",
                            dest + "/index/" + label + ".ndx"],
                           timeout=300)
        got = hashlib.sha256(out.encode("utf-8", "replace")).hexdigest() \
            if rc == 0 else None
        if got != want:
            return False, "remote-readback-mismatch:index=" + label
    return True, "verified index files for {0} store(s)".format(
        len(STORES))


def wave_backup(state):
    if not BACKUP_ENABLED or not STORES:
        return
    bk = state.setdefault("backup", {})
    last = bk.get("last_run_ts", 0)
    if not isinstance(last, (int, float)):
        last = 0
    if time.time() - last < BACKUP_INTERVAL_MINS * 60:
        return
    # FIX 2 (#469/#465 F7): last_run_ts is provisional until the pass
    # finishes; a FAILED pass re-stamps it to a SHORT retry backoff below,
    # so a daily backup that fails retries in minutes, not tomorrow.
    run_started = time.time()
    bk["last_run_ts"] = run_started
    stamp = ts_slug()
    log_event({"event": "backup-pass-start", "stores": [s for s, _ in STORES],
               "interval_mins": BACKUP_INTERVAL_MINS})
    try:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
    except OSError as exc:
        log_event({"event": "backup-pass-aborted",
                   "reason": "archive-dir-unavailable:" + str(exc)[:120]})
        return

    watermarks = bk.get("watermarks", {})
    pass_ok = True

    # (a) hot copies
    snapshots = {}
    for label, fname in STORES:
        info, err = hot_copy_store(label, fname, stamp)
        if err:
            pass_ok = False
            log_event({"event": "backup-hot-copy-failed", "store": label,
                       "err": err})
            backup_alert(state, "hotcopy:" + label,
                         "hot copy FAILED store=" + label, err)
            continue
        snapshots[label] = info["path"]
        log_event({"event": "backup-hot-copy", "store": label,
                   "path": info["path"], "bytes": info["bytes"],
                   "sha256": info["sha256"]})

    # (b)+(d) incremental export from the snapshot copies + read-back
    new_rels = []
    green_wms = {}
    store_green_map = {}
    for label, _ in STORES:
        snap = snapshots.get(label)
        if not snap:
            continue
        try:
            conn = sqlite3.connect("file:{0}?immutable=1".format(snap),
                                   uri=True)
        except sqlite3.Error as exc:
            pass_ok = False
            log_event({"event": "backup-snapshot-open-failed",
                       "store": label, "err": str(exc)[:150]})
            backup_alert(state, "snapshot:" + label,
                         "snapshot open FAILED store=" + label,
                         str(exc)[:200])
            continue
        store_green = True
        try:
            for table in snapshot_session_tables(conn):
                wm_key = "{0}:{1}".format(label, table)
                wm = watermarks.get(wm_key, 0)
                if not isinstance(wm, (int, float)):
                    wm = 0
                rows = export_new_rows(conn, label, table, wm)
                if rows is None:
                    store_green = False
                    continue
                if not rows:
                    log_event({"event": "backup-export-empty",
                               "store": label, "table": table,
                               "watermark": int(wm)})
                    green_wms[wm_key] = wm
                    continue
                rel, n, digest, werr = write_export(label, table, rows)
                if werr:
                    pass_ok = False
                    store_green = False
                    log_event({"event": "backup-export-failed",
                               "store": label, "table": table,
                               "err": werr})
                    backup_alert(state,
                                 "export:" + label + ":" + table,
                                 "export FAILED store=" + label +
                                 " table=" + table, werr)
                    continue
                new_rels.append(rel)
                ok, detail = verify_export_readback(rel, digest, n)
                if ok:
                    green_wms[wm_key] = max(tu for *_x, tu in rows)
                    verify_log_line("GREEN", label, table, rel, n,
                                    digest, "local")
                    log_event({"event": "backup-verify-green",
                               "store": label, "table": table,
                               "artifact": rel, "rows": n,
                               "sha256": digest})
                else:
                    pass_ok = False
                    store_green = False
                    verify_log_line("RED", label, table, rel, n,
                                    digest or "-", "local", detail)
                    log_event({"event": "backup-verify-red",
                               "store": label, "table": table,
                               "artifact": rel, "detail": detail})
                    backup_alert(state, "verify:" + rel,
                                 "read-back RED artifact=" + rel, detail)
        finally:
            conn.close()
        store_green_map[label] = store_green

    # hot-backup generation cap (Observer-owned artefacts only)
    for label, _ in STORES:
        prune_hot_generations(label, BACKUP_KEEP)

    # (c) off-server sync gate -> decides whether the candidate watermarks
    # may be COMMITTED. FIX 6 (#466 F2): a watermark advances ONLY when
    # local read-back is GREEN AND (rclone sync is GREEN OR remote-
    # unconfigured local mode is explicitly acknowledged in events). Sync
    # RED holds ALL watermarks and queues every artifact into a retry
    # backlog that later passes re-attempt; nothing is silently lost.
    def commit_watermarks():
        for k, v in green_wms.items():
            if store_green_map.get(k.split(":", 1)[0]):
                watermarks[k] = v

    remote_ok = None
    backlog = [r for r in bk.get("sync_backlog", [])
               if isinstance(r, str)]
    if rclone_remote_ready():
        pending_rels = sorted(set(new_rels) | set(backlog))
        ok, detail = rclone_sync_and_verify(pending_rels)
        remote_ok = ok
        if ok:
            commit_watermarks()
            cleared = len(backlog)
            bk["sync_backlog"] = []
            log_event({"event": "backup-sync-complete",
                       "remote": RCLONE_REMOTE, "artifacts": len(new_rels),
                       "backlog_cleared": cleared, "detail": detail})
        else:
            pass_ok = False
            bk["sync_backlog"] = pending_rels
            try:
                with open(os.path.join(ARCHIVE_DIR, "sync-pending.log"),
                          "a", encoding="utf-8") as fh:
                    fh.write("{0} | SYNC-FAILED | remote={1} | detail={2} "
                             "| held_artifacts={3} backlog={4}\n".format(
                                 now_iso(), RCLONE_REMOTE,
                                 (detail or "")[:200], len(new_rels),
                                 len(pending_rels)))
            except OSError:
                pass
            log_event({"event": "backup-watermark-held",
                       "reason": "sync-red",
                       "remote": RCLONE_REMOTE, "detail": detail,
                       "held_candidates": sorted(green_wms.keys()),
                       "backlog": len(pending_rels)})
            backup_alert(state, "sync:" + RCLONE_REMOTE,
                         "off-server sync FAILED remote=" + RCLONE_REMOTE,
                         "{0}; watermarks HELD and {1} artifact(s) queued "
                         "for retry next pass".format(detail,
                                                      len(pending_rels)))
    else:
        # Local mode: no remote configured. Explicitly acknowledged here;
        # GREEN local read-back is sufficient to advance the watermark.
        commit_watermarks()
        try:
            with open(os.path.join(ARCHIVE_DIR, "sync-pending.log"), "a",
                      encoding="utf-8") as fh:
                fh.write("{0} | PENDING | remote={1} not configured "
                         "(unset or absent from rclone listremotes) | "
                         "artifacts={2}\n".format(
                             now_iso(),
                             RCLONE_REMOTE or "<unset>", len(new_rels)))
        except OSError:
            pass
        log_event({"event": "backup-sync-pending",
                   "detail": "local mode; off-server sync deferred until "
                             "OBSERVER_RCLONE_REMOTE is wired",
                   "artifacts": len(new_rels)})

    uncommitted = {k: v for k, v in green_wms.items()
                   if watermarks.get(k) != v}
    if uncommitted:
        log_event({"event": "backup-watermark-held",
                   "keys": sorted(uncommitted),
                   "detail": "candidates not committed: local read-back "
                             "red/unverified for their store, or off-server "
                             "sync failed (pruning stays gated)"})

    # prune-gate report (REPORT ONLY — operator-manual deletion v1)
    cutoff_ms = int((time.time() - PRUNE_AGE_DAYS * 86400) * 1000)
    report_lines = []
    for label, _ in STORES:
        snap = snapshots.get(label)
        if not snap:
            continue
        try:
            conn = sqlite3.connect("file:{0}?immutable=1".format(snap),
                                   uri=True)
        except sqlite3.Error:
            continue
        try:
            for table in snapshot_session_tables(conn):
                wm_key = "{0}:{1}".format(label, table)
                gwm = watermarks.get(wm_key, 0)
                gate = "GREEN" if store_green_map.get(label) and gwm \
                    else "PENDING"
                q = ("SELECT COUNT(*) FROM {0} WHERE time_updated < ?"
                     ).format(table)
                try:
                    old_total = conn.execute(q, (cutoff_ms,)).fetchone()[0]
                    elig = conn.execute(
                        q + " AND time_updated <= ?",
                        (cutoff_ms, gwm)).fetchone()[0]
                except sqlite3.Error:
                    continue
                report_lines.append(
                    "{0} | store={1} table={2} older_than_{3}d={4} "
                    "prune_eligible={5} gate={6}".format(
                        now_iso(), label, table, PRUNE_AGE_DAYS,
                        old_total, elig, gate))
        finally:
            conn.close()
    if report_lines:
        try:
            with open(os.path.join(ARCHIVE_DIR, "prune-report.txt"), "a",
                      encoding="utf-8") as fh:
                for ln in report_lines:
                    fh.write(ln + "\n")
            log_event({"event": "backup-prune-report",
                       "lines": len(report_lines),
                       "detail": "report only; no live deletion"})
        except OSError:
            pass

    bk["watermarks"] = watermarks
    bk["last_pass"] = {
        "ts": now_iso(), "ok": pass_ok, "snapshots": snapshots,
        "new_artifacts": new_rels, "remote_sync": remote_ok,
        "watermarks_committed": not uncommitted,
        "sync_backlog": bk.get("sync_backlog", []),
        "watermarks": {k: int(v) for k, v in watermarks.items()}}
    if not pass_ok:
        # FIX 2 (#469/#465 F7): failed pass retries after the SHORT backoff,
        # not a full silent interval.
        bk["last_run_ts"] = time.time() - BACKUP_INTERVAL_MINS * 60 + \
            BACKUP_RETRY_MINS * 60
        log_event({"event": "backup-retry-scheduled",
                   "retry_mins": BACKUP_RETRY_MINS})
    log_event({"event": "backup-pass-done", "ok": pass_ok,
               "new_artifacts": len(new_rels),
               "remote_sync": remote_ok})


# ---------------------------------------------------------------------------
# F5 (#460): admission-policy absorption. Config-driven launch-contract
# validation over each tracked agent KICKOFF.md; audit trail in events.jsonl;
# absorbs would-be plugins #448/#445/#446/#451/#452 into this policy surface
# (no new plugin files).
# ---------------------------------------------------------------------------

MODEL_PATTERNS = [
    re.compile(r"--model[ =]([A-Za-z0-9._/-]+)"),
    re.compile(r"(?im)^model:\s*([A-Za-z0-9._/-]+)"),
    re.compile(r"\b((?:opencode(?:-go)?)\/([A-Za-z0-9._-]+))"),
]

def load_catalog(state, force=False):
    """Live opencode models catalog with TTL cache. Returns
    {provider: [model ids]} or None when unavailable."""
    cat = state.get("admission_catalog") or {}
    if not force and isinstance(cat.get("ts"), (int, float)) and \
            time.time() - cat["ts"] < ADMISSION_CATALOG_TTL and \
            isinstance(cat.get("models"), dict):
        return cat["models"]
    models = {}
    for provider in ADMISSION_PROVIDERS:
        cmd = MODELS_CMD_TMPL.replace("{provider}", provider).split()
        rc, out, _ = run(cmd, timeout=60)
        if rc == 0 and out.strip():
            models[provider] = [ln.strip() for ln in
                                out.splitlines() if ln.strip()]
        else:
            models[provider] = []
    if not any(models.values()):
        state["admission_catalog"] = {"ts": time.time(), "models": models}
        return None
    state["admission_catalog"] = {"ts": time.time(), "models": models}
    return models


def model_valid(model_id, catalog):
    if not catalog:
        return None  # catalog unavailable: not decidable
    if model_id in {m for ids in catalog.values() for m in ids}:
        return True
    if "/" in model_id:
        prov, mid = model_id.split("/", 1)
        if mid in catalog.get(prov, []):
            return True
    return False


def admission_checks(state, agent):
    """Run the config-driven contract checks for one tracked agent.
    Appends admission-check events; returns list of failure strings."""
    wt = os.path.join(WORKTREES_ROOT, agent)
    kfile = os.path.join(wt, "KICKOFF.md")
    failures = []
    try:
        with open(kfile, encoding="utf-8", errors="replace") as fh:
            text = fh.read(40000)
    except OSError:
        log_event({"event": "admission-check", "agent": agent,
                   "check": "kickoff-present", "ok": False,
                   "detail": "KICKOFF.md unreadable"})
        return ["kickoff-present: KICKOFF.md unreadable"]
    # model-declared-and-valid
    declared = []
    for pat in MODEL_PATTERNS:
        for m in pat.finditer(text):
            tok = m.group(1)
            if tok not in declared:
                declared.append(tok)
    catalog = load_catalog(state)
    for tok in declared:
        valid = model_valid(tok, catalog)
        if valid is None:
            log_event({"event": "admission-check", "agent": agent,
                       "check": "model-valid", "ok": None,
                       "detail": "catalog-unavailable model=" + tok})
            continue
        if valid:
            log_event({"event": "admission-check", "agent": agent,
                       "check": "model-valid", "ok": True, "model": tok})
        else:
            log_event({"event": "admission-check", "agent": agent,
                       "check": "model-valid", "ok": False, "model": tok,
                       "detail": "not in live catalog"})
            failures.append("model-valid: {0} not in live catalog".format(
                tok))
    # issue-exists + issue-claimed
    m = re.search(r"\*\*Issue\*\*:\s*#(\d+)", text)
    issue = m.group(1) if m else None
    if not issue:
        log_event({"event": "admission-check", "agent": agent,
                   "check": "issue-declared", "ok": False,
                   "detail": "no Issue field in KICKOFF.md"})
        failures.append("issue-declared: no Issue field")
    else:
        rc, _, _ = run(["crosslink", "issue", "show", issue], timeout=60,
                       cwd=CROSSLINK_ROOT)
        exists = rc == 0
        log_event({"event": "admission-check", "agent": agent,
                   "check": "issue-exists", "ok": exists,
                   "issue": issue})
        if not exists:
            failures.append("issue-exists: #{0} not found".format(issue))
        else:
            rc2, out2, _ = run(["crosslink", "locks", "check", issue],
                               timeout=30, cwd=CROSSLINK_ROOT)
            claimed = rc2 == 0 and "is locked by" in (out2 or "")
            log_event({"event": "admission-check", "agent": agent,
                       "check": "issue-claimed", "ok": claimed,
                       "issue": issue})
            if not claimed:
                failures.append(
                    "issue-claimed: #{0} has no active lock".format(issue))
    # estimate-declared
    try:
        est = re.search(ADMISSION_ESTIMATE_RE, text) is not None
    except re.error:
        est = re.search(r"(?i)\bestimat", text) is not None
    log_event({"event": "admission-check", "agent": agent,
               "check": "estimate-declared", "ok": est})
    if not est:
        failures.append("estimate-declared: no estimate in KICKOFF.md")
    return failures


def wave_admission(state):
    if not ADMISSION_ENABLED:
        return
    for agent in sorted(state["agents"]):
        wt = os.path.join(WORKTREES_ROOT, agent)
        if not os.path.isdir(wt):
            continue
        failures = admission_checks(state, agent)
        fp = hashlib.sha256(
            "\n".join(sorted(failures)).encode("utf-8")).hexdigest()[:12]
        alerted = state.setdefault("admission_alerted", {})
        if failures:
            if alerted.get(agent) != fp:
                post_comment(state, FLAG_ISSUE,
                             "[OBSERVER][ADMISSION] launch-contract "
                             "violations agent={0}: {1}. Checks are "
                             "config-driven Observer policy (events.jsonl "
                             "audit trail); fix the contract before "
                             "re-dispatch.".format(agent, "; ".join(
                                 failures[:6])))
                alerted[agent] = fp
        else:
            if alerted.pop(agent, None) is not None:
                log_event({"event": "admission-healed", "agent": agent})

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

    # F5: admission-policy absorption (config-driven contract checks).
    wave_admission(state)

    # F6: all-agents-vanish transition -> platform-restart signature alert.
    # Tracking is SCAN-based (who physically appeared), not phase-based:
    # a vanished agent degrades to the cleaned-external phase, which would
    # otherwise make the re-arm undetectable.
    cur_active = {a for a, r in state["agents"].items()
                  if r.get("phase") in ("active", "parked")}
    prev_active = set(state.get("wave_prev_active") or [])
    vanished = prev_active - scanned
    if prev_active and vanished == prev_active and \
            not state.get("wave_anomaly_alerted"):
        wt_present = [a for a in sorted(vanished)
                      if os.path.isdir(os.path.join(WORKTREES_ROOT, a))]
        state["wave_anomaly_alerted"] = True
        state["wave_vanished"] = sorted(vanished)
        log_event({"event": "wave-anomaly",
                   "vanished": sorted(vanished),
                   "worktrees_present": len(wt_present),
                   "signature": "platform-restart-suspected"})
        post_comment(
            state, FLAG_ISSUE,
            "[OBSERVER][WAVE-ANOMALY] all-agents-vanish: {0} tracked "
            "active/parked agent(s) ({1}) absent from the scan "
            "simultaneously with no terminal verdicts and no "
            "Observer-executed cleanup; worktrees still present: "
            "{2}/{3}. Platform-restart signature suspected - "
            "recommend host/platform health-check before any "
            "relaunch.".format(
                len(vanished), ", ".join(sorted(vanished)),
                len(wt_present), len(vanished)))
    reappeared = [a for a in (state.get("wave_vanished") or [])
                  if a in scanned]
    if reappeared:
        if state.get("wave_anomaly_alerted"):
            log_event({"event": "wave-anomaly-rearmed",
                       "reappeared": reappeared})
        state["wave_anomaly_alerted"] = False
        state["wave_vanished"] = []
    state["wave_prev_active"] = sorted(cur_active)

    # F4: dual-store backup pass (interval-gated inside).
    wave_backup(state)

    phases = {}
    for agent, rec in state["agents"].items():
        phases[rec.get("phase", "unknown")] = \
            phases.get(rec.get("phase", "unknown"), 0) + 1
    summary = {"scanned": len(rows), "tracked": len(state["agents"]),
               "phases": phases, "parked_now": len(parked),
               "actions_used_window": len(state.get("action_window", [])),
               "dry_run": DRY_RUN}
    print(json.dumps(summary, separators=(",", ":")))
    err = save_state(state)
    if err:
        # FIX 2 (#469 F5): state loss AFTER executed actions means the next
        # cycle would re-fire those actions (duplicate kills/cleanups/
        # comments). Escalate loudly: stderr witness + nonzero rc feeds the
        # consecutive-error cap so the loop halts instead of repeating
        # mutations with volatile state.
        log_event({"event": "state-save-failed", "err": err})
        sys.stderr.write(
            "observer: FATAL state-save-failed: {0}\n".format(err))
        return 2
    return 0

sys.exit(main())
'

cycle_start=$(date +%s)
consecutive_errors=0
cycle_ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# FIX 2 (#469): one error-accounting path for every failure class. A cycle
# that fails (liveness, json parse, or the python program itself) bumps the
# consecutive counter; hitting the cap HALTS the loop rather than looping
# destructively.
bump_error() { # bump_error <source>
    consecutive_errors=$((consecutive_errors + 1))
    printf '%s' "$consecutive_errors" > "$ERRCOUNT_FILE" 2>/dev/null || :
    emit_event "$(printf '{"ts":"%s","event":"error","kind":"%s","consecutive":%s}\n' \
        "$cycle_ts" "$1" "$consecutive_errors")"
    if [ "$consecutive_errors" -ge "$OBSERVER_MAX_CONSECUTIVE_ERRORS" ]; then
        emit_event "$(printf '{"ts":"%s","event":"fatal","kind":"consecutive-error-cap","source":"%s","consecutive":%s}\n' \
            "$cycle_ts" "$1" "$consecutive_errors")"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# FIX 5 (#466 F6): single-instance guard. The observer holds kill/cleanup
# authority over the fleet; two interleaved instances would double-fire
# mutations against last-writer-wins state. Lock = atomic exclusive create
# (noclobber) carrying our PID. A second instance REFUSES loudly while the
# recorded PID is alive; a crashed instance leaves a STALE lock that is
# detected (recorded PID no longer alive, checked via ps so cross-owner
# zombies count as alive) and recovered exactly once.
# Known limitation (documented, fail-safe direction): PID reuse could make
# a stale lock look live -> the second instance refuses (never double-runs).
# ---------------------------------------------------------------------------
LOCK_FILE="$OBSERVER_STATE_DIR/observer.lock"
LOCK_OWNED=0
release_lock() {
    # Only ever remove a lock WE own - never a live competitor's.
    if [ "$LOCK_OWNED" -eq 1 ]; then
        rm -f "$LOCK_FILE" 2>/dev/null || :
    fi
}
trap release_lock EXIT
trap 'release_lock; exit 130' INT
trap 'release_lock; exit 143' TERM

acquire_lock() {
    tries=0
    while [ "$tries" -lt 2 ]; do
        if ( set -o noclobber; printf '%s\n' "$$" > "$LOCK_FILE" ) 2>/dev/null; then
            LOCK_OWNED=1
            return 0
        fi
        lock_pid="$(cat "$LOCK_FILE" 2>/dev/null || true)"
        case "$lock_pid" in
            ''|*[!0-9]*)
                # unreadable or garbage lock content: treat as stale,
                # remove and retry once
                rm -f "$LOCK_FILE" 2>/dev/null || :
                tries=$((tries + 1))
                continue
                ;;
        esac
        if ps -p "$lock_pid" >/dev/null 2>&1; then
            emit_event "$(printf '{"ts":"%s","event":"fatal","kind":"instance-lock-held","holder_pid":%s,"my_pid":%s}\n' \
                "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$lock_pid" "$$")"
            printf 'observer: REFUSING to start - another instance already holds %s (pid %s); this invocation (pid %s) will not run.\n' \
                "$LOCK_FILE" "$lock_pid" "$$" >&2
            return 1
        fi
        emit_event "$(printf '{"ts":"%s","event":"instance-lock-stale-recovered","stale_pid":%s,"my_pid":%s}\n' \
            "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$lock_pid" "$$")"
        rm -f "$LOCK_FILE" 2>/dev/null || :
        tries=$((tries + 1))
    done
    emit_event "$(printf '{"ts":"%s","event":"fatal","kind":"instance-lock-unavailable","my_pid":%s}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$$")"
    printf 'observer: REFUSING to start - lock %s could not be acquired.\n' \
        "$LOCK_FILE" >&2
    return 1
}
if ! acquire_lock; then
    exit 1
fi

while :; do
    cycle_ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # FIX 2 (#469): strict mode + pipefail. Nonzero rc from these command
    # substitutions is EXPECTED and captured explicitly ('|| rc=$?'); it is
    # handled immediately below, never swallowed.
    liveness_rc=0
    out=""
    if [ -n "$OBSERVER_INPUT_JSON" ]; then
        out="$(cat "$OBSERVER_INPUT_JSON" 2>/dev/null)" || liveness_rc=$?
    else
        out="$(python3 "$LIVENESS_PY" --json --all 2>/dev/null)" || liveness_rc=$?
    fi

    if [ "$liveness_rc" -ne 0 ] || [ -z "$out" ]; then
        emit_event "$(printf '{"ts":"%s","event":"error","kind":"liveness-failed","rc":%s,"consecutive":%s}\n' \
            "$cycle_ts" "$liveness_rc" "$((consecutive_errors + 1))")"
        bump_error "liveness-failed"
    else
        consecutive_errors=0
        printf '%s' 0 > "$ERRCOUNT_FILE" 2>/dev/null || :

        compact=""
        json_rc=0
        compact="$(printf '%s' "$out" | python3 -c \
                'import json,sys; sys.stdout.write(json.dumps(json.load(sys.stdin), separators=(",", ":"))+"\n")' \
                2>/dev/null)" || json_rc=$?
        if [ "$json_rc" -ne 0 ] || [ -z "$compact" ]; then
            emit_event "$(printf '{"ts":"%s","event":"error","kind":"json-parse-failed","rc":%s}\n' \
                "$cycle_ts" "$json_rc")"
            bump_error "json-parse-failed"
        else
            summary=""
            prog_rc=0
            summary="$(printf '%s\n' "$compact" | python3 -c "$CYCLE_PROG" 2>>"$OBSERVER_STATE_DIR/python-stderr.log")" || prog_rc=$?
            if [ -n "$summary" ]; then
                emit_event "$(printf '{"ts":"%s","event":"cycle","rc":%s,"summary":%s}\n' \
                    "$cycle_ts" "$prog_rc" "$summary")"
            else
                emit_event "$(printf '{"ts":"%s","event":"error","kind":"cycle-program-failed","rc":%s}\n' \
                    "$cycle_ts" "$prog_rc")"
            fi
            # FIX 2 (#469 finding 10): python program failures previously
            # logged but never counted toward the consecutive-error cap,
            # so a persistently crashing program looped forever. Counted
            # now: halt-not-loop applies to program failures too.
            if [ "$prog_rc" -ne 0 ]; then
                bump_error "cycle-program-failed"
            fi
        fi
    fi

    if [ "$ONCE" -eq 1 ]; then
        break
    fi
    sleep "$OBSERVER_INTERVAL"
done
