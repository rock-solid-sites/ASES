#!/usr/bin/env bash
#
# liveness-watchdog.sh — v2 watchdog loop (EPIC #423; upgrades the log-only
# loop dispatched 2026-08-23 23:56 under the two-part part-1 task).
#
# Behavior (v2):
#   Every INTERVAL_SECS seconds:
#     1. Run scripts/agent-liveness.py --json --all (resolved relative to this
#        script, so the loop keeps working from any checkout of the repo).
#     2. Append the run as ONE compacted JSON line to
#        /tmp/opencode/liveness-log.jsonl (true JSONL; the v1 loop appended
#        raw multi-line pretty-printed blobs).
#     3. Diff each agent's verdict/aliveness against the previous snapshot in
#        /tmp/opencode/liveness-state/watchdog-state.json and flag:
#          - NEW LIKELY-FROZEN or STALE-SUSPECT entries,
#          - worsening of an already-flagged agent (severity order mirrors
#            agent-liveness.py VERDICT_SEVERITY: lower = worse),
#          - any previously-ALIVE agent whose tmux session vanished
#            (ALIVE -> SESSION-GONE transition).
#        Each flag posts exactly:
#          crosslink issue comment 429 '[WATCHDOG] <agent-id> verdict=<v>
#          age_min=<n> source=<s> - auditor investigation requested'
#        Dedup: the state file remembers last_flagged_verdict per agent; the
#        same agent is NOT re-flagged on later cycles unless its verdict
#        worsens, or it recovers (flag memory cleared) and degrades again.
#     4. Append every event (flag, error, cycle summary) to the same JSONL.
#
# Write policy (constraint from EPIC #423): this script writes ONLY
#   - the JSONL log and state files under /tmp/opencode/, and
#   - crosslink issue comments (via the crosslink CLI).
# It never modifies agent worktrees; agent-liveness.py itself is read-only
# outside its own pane-hash state file in the same state dir.
#
# Deployment: intended to run inside a detached tmux session so it outlives
# the dispatching agent:
#   tmux new-session -d -s liveness-watch \
#     bash /home/claude-code/projects/ASES/scripts/liveness-watchdog.sh
#
# Shell: bash, stdlib tooling only (python3 used for JSON parsing).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIVENESS_PY="$SCRIPT_DIR/agent-liveness.py"
LOG_FILE="${LIVENESS_WATCHDOG_LOG:-/tmp/opencode/liveness-log.jsonl}"
STATE_DIR="/tmp/opencode/liveness-state"
STATE_FILE="$STATE_DIR/watchdog-state.json"
INTERVAL_SECS="${LIVENESS_WATCHDOG_INTERVAL:-120}"
FLAG_ISSUE="${LIVENESS_WATCHDOG_ISSUE:-429}"

mkdir -p "$STATE_DIR" 2>/dev/null
[ -f "$LOG_FILE" ] || : >> "$LOG_FILE" 2>/dev/null

if [ ! -r "$LIVENESS_PY" ]; then
    printf '{"ts":"%s","event":"fatal","kind":"missing-liveness-script","path":"%s"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$LIVENESS_PY" >> "$LOG_FILE"
    exit 1
fi

# ---------------------------------------------------------------------------
# diff_against_state: read compacted liveness JSON on stdin, load the previous
# snapshot from $WATCHDOG_STATE_FILE, decide flags, atomically save the new
# snapshot, and print one action per flag as TAB-separated:
#   trigger<TAB>agent<TAB>verdict<TAB>age_min<TAB>source
# trigger ∈ {new, worsened, vanished}
# ---------------------------------------------------------------------------
DIFF_PROG='
import json, os, sys

SEVERITY = {  # mirrors agent-liveness.py VERDICT_SEVERITY (lower = worse)
    "DEAD-UNMARKED": 0,
    "LIKELY-FROZEN": 1,
    "FINISHED-UNMARKABLE": 2,
    "STALE-SUSPECT": 3,
    "RUNNING-ALIVE": 4,
    "DONE-CONFIRMED": 5,
}
FLAG_VERDICTS = {"LIKELY-FROZEN", "STALE-SUSPECT"}
STATE_FILE = os.environ["WATCHDOG_STATE_FILE"]

data = json.load(sys.stdin)
now_iso = data.get("generated_at")

try:
    with open(STATE_FILE, encoding="utf-8") as fh:
        state = json.load(fh)
except (OSError, ValueError):
    state = {}
prev_agents = state.get("agents", {}) if isinstance(state, dict) else {}
if not isinstance(prev_agents, dict):
    prev_agents = {}

actions = []
new_agents = {}
for row in data.get("agents", []):
    agent = row.get("agent", "")
    verdict = row.get("verdict", "")
    aliveness = row.get("aliveness", "")
    age_min = row.get("age_min", 0)
    source = row.get("source", "")
    prev = prev_agents.get(agent, {})
    prev_alive = prev.get("aliveness") == "ALIVE"
    flagged_verdict = prev.get("last_flagged_verdict")

    trigger = None
    if prev_alive and aliveness == "SESSION-GONE":
        trigger = "vanished"
    elif verdict in FLAG_VERDICTS:
        if flagged_verdict is None:
            trigger = "new"
        elif SEVERITY.get(verdict, 99) < SEVERITY.get(flagged_verdict, 99):
            trigger = "worsened"
    elif flagged_verdict is not None and aliveness != "ALIVE":
        # Escalation past the flag classes while an investigation is open,
        # e.g. LIKELY-FROZEN -> DEAD-UNMARKED after the pane died.
        if SEVERITY.get(verdict, 99) < SEVERITY.get(flagged_verdict, 99):
            trigger = "worsened"

    rec = {
        "verdict": verdict,
        "severity": SEVERITY.get(verdict),
        "aliveness": aliveness,
        "age_min": age_min,
        "source": source,
        "seen_at": now_iso,
    }
    if trigger:
        rec["last_flagged_verdict"] = verdict
        rec["last_flagged_at"] = now_iso
        rec["last_flagged_trigger"] = trigger
        actions.append((trigger, agent, verdict, age_min, source))
    elif verdict not in FLAG_VERDICTS and flagged_verdict is not None:
        # Recovered: clear flag memory so a future degradation is a new episode.
        rec["recovered_at"] = now_iso
    new_agents[agent] = rec

tmp_path = STATE_FILE + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as fh:
    json.dump({"version": 1, "updated_at": now_iso, "agents": new_agents},
              fh, indent=2, sort_keys=True)
os.replace(tmp_path, STATE_FILE)

for trigger, agent, verdict, age_min, source in actions:
    sys.stdout.write(f"{trigger}\t{agent}\t{verdict}\t{age_min}\t{source}\n")
'

cycle_start=$(date +%s)
while :; do
    cycle_ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    out="$(python3 "$LIVENESS_PY" --json --all 2>/dev/null)"
    liveness_rc=$?

    flags_fired=0

    if [ "$liveness_rc" -ne 0 ] || [ -z "$out" ]; then
        printf '{"ts":"%s","event":"error","kind":"liveness-failed","rc":%s}\n' \
            "$cycle_ts" "$liveness_rc" >> "$LOG_FILE"
    else
        # One compacted JSON line per cycle (true JSONL).
        if ! compact="$(printf '%s' "$out" | python3 -c \
                'import json,sys; sys.stdout.write(json.dumps(json.load(sys.stdin), separators=(",", ":"))+"\n")' \
                2>>"$LOG_FILE")" || [ -z "$compact" ]; then
            printf '{"ts":"%s","event":"error","kind":"json-parse-failed"}\n' \
                "$cycle_ts" >> "$LOG_FILE"
        else
            printf '%s\n' "$compact" >> "$LOG_FILE"

            actions="$(printf '%s\n' "$compact" \
                | WATCHDOG_STATE_FILE="$STATE_FILE" python3 -c "$DIFF_PROG")"

            if [ -n "$actions" ]; then
                while IFS=$'\t' read -r trigger agent verdict age source; do
                    [ -z "${agent:-}" ] && continue
                    msg="[WATCHDOG] ${agent} verdict=${verdict} age_min=${age} source=${source} - auditor investigation requested"
                    posted=true
                    crosslink issue comment "$FLAG_ISSUE" "$msg" >/dev/null 2>&1 || posted=false
                    printf '{"ts":"%s","event":"flag","trigger":"%s","agent":"%s","verdict":"%s","age_min":%s,"source":"%s","issue":%s,"posted":%s}\n' \
                        "$cycle_ts" "$trigger" "$agent" "$verdict" "$age" "$source" \
                        "$FLAG_ISSUE" "$posted" >> "$LOG_FILE"
                    flags_fired=$((flags_fired + 1))
                done <<< "$actions"
            fi
        fi
    fi

    duration=$(( $(date +%s) - cycle_start ))
    printf '{"ts":"%s","event":"cycle","flags":%s,"liveness_rc":%s,"uptime_s":%s}\n' \
        "$cycle_ts" "$flags_fired" "$liveness_rc" "$duration" >> "$LOG_FILE"

    sleep "$INTERVAL_SECS"
done
