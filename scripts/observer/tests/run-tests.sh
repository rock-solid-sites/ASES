#!/usr/bin/env bash
# Test harness for scripts/observer/observer.sh (issue #460; adapted from the
# recovered #459 matched-pair harness).
# All tests run with OBSERVER_DRY_RUN=1: no real mutations, no real comments.
# Isolated state dirs per test under /tmp/opencode/observer-tests/.
#
# Harness triage fixes carried from the #460 recovery triage:
#   T3: placeholder grep-on-/dev/null replaced with a real preservation-note
#       check against events.jsonl.
#   T4: kill-signature case now drives an interactive default-shell pane with
#       "exit <code>" (typing into a foreground `sleep` can never exit the
#       pane), plus a bounded dead-poll instead of a blind sleep 1.
#   T5: resume_at pattern made space-tolerant (state file pretty-prints;
#       compact-JSON-only grep was the stale pattern).
#   T8: removed the internally inconsistent second last_main_head overwrite
#       (setting prev == current head made merge-detected unreachable); the
#       merge is now simulated by a real commit landing on main between
#       cycles.
set -u

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGER="$TEST_DIR/../observer.sh"
TESTS=/tmp/opencode/observer-tests
PASS=0
FAIL=0

note() { printf '%s\n' "== $*"; }
check() { # check <name> <pattern> <file>
    if grep -q "$2" "$3" 2>/dev/null; then
        printf 'PASS %s\n' "$1"; PASS=$((PASS+1))
    else
        printf 'FAIL %s (missing pattern: %s in %s)\n' "$1" "$2" "$3"; FAIL=$((FAIL+1))
    fi
}
check_absent() {
    if grep -q "$2" "$3" 2>/dev/null; then
        printf 'FAIL %s (unexpected pattern: %s in %s)\n' "$1" "$2" "$3"; FAIL=$((FAIL+1))
    else
        printf 'PASS %s\n' "$1"; PASS=$((PASS+1))
    fi
}

fixture() { # fixture <file> <agent> <verdict> [role] [aliveness] [status]
    python3 - "$@" <<'PYEOF'
import json, sys
path, agent, verdict = sys.argv[1], sys.argv[2], sys.argv[3]
role = sys.argv[4] if len(sys.argv) > 4 else "builder"
alive = sys.argv[5] if len(sys.argv) > 5 else "ALIVE"
status = sys.argv[6] if len(sys.argv) > 6 else "RUNNING"
row = {"agent": agent, "status": status, "aliveness": alive, "age_min": 1.0,
       "source": "walk", "role": role, "verdict": verdict,
       "last_activity": "2026-08-24T06:00:00+00:00", "budget_min": 45.0,
       "probe": {"state": alive}}
payload = {"generated_at": "2026-08-24T07:10:00+00:00",
           "root": "/tmp/opencode/observer-tests/fake-root",
           "budget_min": 45.0, "state_dir": "/tmp/x",
           "agents": [row], "skipped_no_signal": []}
with open(path, "w") as fh:
    json.dump(payload, fh)
PYEOF
}

run_cycle() { # run_cycle <statedir> <fixture.json> [extra env as KEY=VAL...]
    local sd="$1" fx="$2"; shift 2
    (
        export OBSERVER_DRY_RUN=1
        export OBSERVER_STATE_DIR="$sd"
        export OBSERVER_INPUT_JSON="$fx"
        export OBSERVER_OPENCODE_LOG="${TEST_OPENCODE_LOG:-$TESTS/empty.log}"
        export OBSERVER_REPO_ROOT="${TEST_REPO_ROOT:-$TESTS/fake-repo}"
        for kv in "$@"; do export "$kv"; done
        bash "$MANAGER" --once >/dev/null 2>&1
    )
}

mkdir -p "$TESTS"
: > "$TESTS/empty.log"

# ---------------------------------------------------------------------------
note "T1 COMPLETED transition"
sd="$TESTS/t1"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-done DONE-CONFIRMED builder EXITED DONE
run_cycle "$sd" "$fx"
check "T1 cleanup dry-run recorded"   "cleanup-dry-run" "$sd/events.jsonl"
check "T1 staging row appended"       "model-evidence-row" "$sd/events.jsonl"
check "T1 outcome completed"          '"outcome":"completed"' "$sd/model-evidence-staging.jsonl"
check "T1 phase completed"            '"phase": *"completed"\|"phase":"completed"' "$sd/manager-state.json"

# ---------------------------------------------------------------------------
note "T2 FINISHED-UNMARKABLE transition"
sd="$TESTS/t2"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-fin FINISHED-UNMARKABLE reviewer EXITED RUNNING
run_cycle "$sd" "$fx"
check "T2 sweep flag written"         "force-sweep-flagged" "$sd/events.jsonl"
check "T2 sweep file has reason"      "finished-unmarkable" "$sd/force-sweep-pending.txt"
check "T2 staging row unmarkable"     '"outcome":"finished-unmarkable"' "$sd/model-evidence-staging.jsonl"

# ---------------------------------------------------------------------------
note "T3 FAILED transition (conservative preservation)"
sd="$TESTS/t3"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-fail DEAD-UNMARKED builder SESSION-GONE RUNNING
run_cycle "$sd" "$fx"
check "T3 classified failed"          '"action": *"failed"\|"action":"failed"' "$sd/events.jsonl"
check "T3 evidence bundle written"    "evidence-bundle" "$sd/events.jsonl"
check "T3 worktree preserved note"    "PRESERVED for forensics" "$sd/events.jsonl"
test -f "$sd/preserved-worktrees.txt" && printf 'PASS T3 preserved-worktrees.txt exists\n' && PASS=$((PASS+1)) || { printf 'FAIL T3 preserved-worktrees.txt missing\n'; FAIL=$((FAIL+1)); }
ls "$sd/evidence/zzz-lc-fail" >/dev/null 2>&1 && { printf 'PASS T3 evidence dir\n'; PASS=$((PASS+1)); } || { printf 'FAIL T3 evidence dir missing\n'; FAIL=$((FAIL+1)); }
check "T3 comment dry-run recorded"   "comment-dry-run" "$sd/events.jsonl"
check "T3 relaunch recommendation"    "relaunch-with-backup-model" "$sd/events.jsonl"

# ---------------------------------------------------------------------------
note "T4 KILLED vs FAILED via real tmux pane exit statuses"
if command -v tmux >/dev/null 2>&1; then
    for sigcase in killed:143 failed:1; do
        name="${sigcase%%:*}"; code="${sigcase##*:}"
        sess="zzz-lc-$name"
        tmux kill-session -t "$sess" 2>/dev/null
        # Interactive default shell: "exit <code>" typed at the prompt makes
        # the pane process exit with exactly <code>; remain-on-exit preserves
        # the dead-pane status for the manager's kill-signature probe.
        tmux new-session -d -s "$sess"
        tmux set-option -t "$sess" remain-on-exit on
        tmux send-keys -t "$sess" "exit $code" Enter
        dead=""
        for _ in 1 2 3 4 5 6 7 8 9 10; do
            dead="$(tmux list-panes -t "$sess" -F '#{pane_dead}' 2>/dev/null | head -1)"
            [ "$dead" = "1" ] && break
            sleep 0.5
        done
        sd="$TESTS/t4-$name"; rm -rf "$sd"; mkdir -p "$sd"
        fx="$sd/fix.json"; fixture "$fx" "$sess" DEAD-UNMARKED builder EXITED RUNNING
        run_cycle "$sd" "$fx"
        if [ "$name" = killed ]; then
            check "T4-$name kill signature recognized" '"action": *"killed"\|"action":"killed"' "$sd/events.jsonl"
            check "T4-$name SIGTERM evidence" "SIGTERM signature" "$sd/events.jsonl"
        else
            check "T4-$name non-kill exit classified failed" '"action": *"failed"\|"action":"failed"' "$sd/events.jsonl"
        fi
        tmux kill-session -t "$sess" 2>/dev/null
    done
else
    printf 'SKIP T4 (no tmux)\n'
fi

# ---------------------------------------------------------------------------
note "T5 PARKED via rate-limit log signature + retry-after parse + expiry"
sd="$TESTS/t5"; rm -rf "$sd"; mkdir -p "$sd"
cat > "$sd/agent.log" <<'LOGEOF'
timestamp=2026-08-24T07:00:00.000Z level=INFO run=abc message=tracking cwd=/tmp/opencode/observer-tests/fake-wt/zzz-lc-parked session.id=ses_testparked001
timestamp=2026-08-24T07:00:01.000Z level=INFO run=abc message="llm runtime selected" llm.runtime=ai-sdk llm.provider=opencode-go llm.model=test-model-free session.id=ses_testparked001
timestamp=2026-08-24T07:00:02.000Z level=ERROR run=abc message="stream error" providerID=opencode-go modelID=test-model-free session.id=ses_testparked001 error.error="AI_APICallError: Rate limit exceeded. Please try again later." retry-after: 2026-08-24 09:30
LOGEOF
export TEST_OPENCODE_LOG="$sd/agent.log"
fx="$sd/fix1.json"; fixture "$fx" zzz-lc-parked LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx"
check "T5 parked action fired"        '"action": *"parked"\|"action":"parked"' "$sd/events.jsonl"
check "T5 resume_at parsed from header" '"resume_at_source": *"retry-after-header"' "$sd/manager-state.json"
check_absent "T5 no kill while parked" '"event":"stop-dry-run"' "$sd/events.jsonl"
# expiry: rewrite resume_at into the past, rerun
python3 - "$sd/manager-state.json" <<'PYEOF'
import json, sys
path = sys.argv[1]
with open(path) as fh: state = json.load(fh)
rec = state["agents"]["zzz-lc-parked"]
rec["resume_at"] = "2026-08-24T00:00:00+00:00"
rec["resume_at_epoch"] = 1
with open(path, "w") as fh: json.dump(state, fh)
PYEOF
fx2="$sd/fix2.json"; fixture "$fx2" zzz-lc-parked LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx2"
check "T5 expiry reclassified frozen" "parked-expired" "$sd/events.jsonl"
check "T5 termination after expiry"   "frozen-termination" "$sd/events.jsonl"
unset TEST_OPENCODE_LOG

# ---------------------------------------------------------------------------
note "T6 FROZEN direct (evidence bundle + auto-kill + termination record)"
sd="$TESTS/t6"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-frozen LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx"
check "T6 stop dry-run recorded"      "stop-dry-run" "$sd/events.jsonl"
check "T6 cleanup dry-run recorded"   "cleanup-dry-run" "$sd/events.jsonl"
check "T6 termination record"         "frozen-termination" "$sd/events.jsonl"
check "T6 spiral authority cited"     "#443 rev3" "$sd/events.jsonl"
check "T6 relaunch recommendation"    "relaunch-with-backup-model" "$sd/events.jsonl"
ls "$sd/evidence/zzz-lc-frozen"/*/bundle.json >/dev/null 2>&1 && { printf 'PASS T6 bundle manifest\n'; PASS=$((PASS+1)); } || { printf 'FAIL T6 bundle manifest missing\n'; FAIL=$((FAIL+1)); }

# ---------------------------------------------------------------------------
note "T7 STALE-SUSPECT warning cycle then escalation"
sd="$TESTS/t7"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-stale STALE-SUSPECT builder ALIVE RUNNING
run_cycle "$sd" "$fx"
check "T7 first cycle warning only"   "stale-warning" "$sd/events.jsonl"
check_absent "T7 no escalation yet"   "frozen-termination" "$sd/events.jsonl"
run_cycle "$sd" "$fx"
check "T7 second cycle escalates"     "STALE-SUSPECT escalated" "$sd/events.jsonl"
check "T7 termination record posted"  "frozen-termination" "$sd/events.jsonl"

# ---------------------------------------------------------------------------
note "T8 merge detection + push suggestion + doctrine DIS trigger (fixture git repo)"
repo="$TESTS/fake-repo"; sd="$TESTS/t8"; rm -rf "$repo" "$sd"; mkdir -p "$sd" "$repo"
git -C "$repo" init -q -b main
git -C "$repo" config user.email t@t; git -C "$repo" config user.name t
git -C "$repo" remote add origin "$repo/.origin-base"
git -C "$repo" clone -q --bare "$repo" "$repo/.origin-base" 2>/dev/null
mkdir -p "$repo/docs/methodology"
printf 'base\n' > "$repo/docs/methodology/source.md"
printf -- '---\ndepends_on:\n  - source.md\n---\nSee `docs/methodology/source.md` and `docs/missing-file.md`\n' > "$repo/docs/methodology/consumer.md"
git -C "$repo" add -A && git -C "$repo" commit -qm base
git -C "$repo" push -q origin main 2>/dev/null || git -C "$repo" push -q "$repo/.origin-base" main
# six extra local commits ahead of origin/main
for i in 1 2 3 4 5 6; do echo "$i" >> "$repo/docs/methodology/source.md"; git -C "$repo" commit -qam "c$i"; done
export TEST_REPO_ROOT="$repo"
# empty-agent fixture (created BEFORE the baseline cycle so the input exists)
python3 - "$sd/fix.json" <<'PYEOF'
import json, sys
row = {"agent": "zzz-none", "status": "RUNNING", "aliveness": "ALIVE",
       "age_min": 1.0, "source": "walk", "role": "builder",
       "verdict": "RUNNING-ALIVE", "last_activity": None,
       "budget_min": 45.0, "probe": {"state": "ALIVE"}}
payload = {"generated_at": "2026-08-24T07:10:00+00:00", "root": "/x",
           "budget_min": 45.0, "state_dir": "/x", "agents": [],
           "skipped_no_signal": []}
with open(sys.argv[1], "w") as fh: json.dump(payload, fh)
PYEOF
# cycle 1: baseline (doctrine snapshot + main head recorded)
run_cycle "$sd" "$sd/fix.json"
# simulate a merge landing on main BETWEEN cycles: a real commit moves main
# past the stored baseline head; prev != head this cycle -> merge-detected.
printf 'edited\n' >> "$repo/docs/methodology/source.md"
git -C "$repo" commit -qam "doctrine-edit"
run_cycle "$sd" "$sd/fix.json"
check "T8 merge detected"             "merge-detected" "$sd/events.jsonl"
check "T8 push suggestion above threshold" "commits ahead of" "$sd/events.jsonl"
check "T8 copy-paste push command"    "cd $repo && git push" "$sd/events.jsonl"
check "T8 doctrine edit detected"     "doctrine-edit" "$sd/events.jsonl"
check "T8 dependent found"            "docs/methodology/consumer.md" "$sd/events.jsonl"
check "T8 unresolved citation finding" "unresolved citation: docs/missing-file.md" "$sd/events.jsonl"
check "T8 DIS comment dry-run"        "\[DIS\]" "$sd/events.jsonl"
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T9 circuit breaker caps mutating actions"
sd="$TESTS/t9"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-brk LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx" "OBSERVER_MAX_ACTIONS_PER_HOUR=1"
check "T9 breaker halt event"         "breaker-halt" "$sd/events.jsonl"

# ---------------------------------------------------------------------------
note "T10 consecutive-error cap halts loop"
sd="$TESTS/t10"; rm -rf "$sd"; mkdir -p "$sd"
rc=0
(
    export OBSERVER_DRY_RUN=1 OBSERVER_STATE_DIR="$sd"
    export OBSERVER_INPUT_JSON="$sd/does-not-exist.json"
    export OBSERVER_MAX_CONSECUTIVE_ERRORS=1
    bash "$MANAGER" --once >/dev/null 2>&1
) || rc=$?
if [ "$rc" -eq 1 ]; then printf 'PASS T10 fatal exit on error cap\n'; PASS=$((PASS+1));
else printf 'FAIL T10 expected exit 1 got %s\n' "$rc"; FAIL=$((FAIL+1)); fi
check "T10 fatal event logged"        "consecutive-error-cap" "$sd/events.jsonl"

# ---------------------------------------------------------------------------
note "T11 vanished-agent reconciliation (tracked then absent)"
sd="$TESTS/t11"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-vanish RUNNING-ALIVE builder ALIVE RUNNING
run_cycle "$sd" "$fx"
python3 - "$sd/fix.json" <<'PYEOF'
import json, sys
path = sys.argv[1]
with open(path) as fh: payload = json.load(fh)
payload["agents"] = []
with open(path, "w") as fh: json.dump(payload, fh)
PYEOF
run_cycle "$sd" "$sd/fix.json"
check "T11 external vanish recorded"  "vanished-externally" "$sd/events.jsonl"

# ---------------------------------------------------------------------------
note "T12 evidence-at-transition on COMPLETED (F1: full bundle + digest comment)"
sd="$TESTS/t12"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-ev DONE-CONFIRMED builder EXITED DONE
run_cycle "$sd" "$fx"
ls "$sd/evidence/zzz-lc-ev/"*-completed/verdict-timeline.json >/dev/null 2>&1 && { printf 'PASS T12 verdict timeline section\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 verdict timeline section missing\n'; FAIL=$((FAIL+1)); }
ls "$sd/evidence/zzz-lc-ev/"*-completed/git-status.txt >/dev/null 2>&1 && { printf 'PASS T12 git status section\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 git status section missing\n'; FAIL=$((FAIL+1)); }
ls "$sd/evidence/zzz-lc-ev/"*-completed/hub-position.json >/dev/null 2>&1 && { printf 'PASS T12 hub position section\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 hub position section missing\n'; FAIL=$((FAIL+1)); }
ls "$sd/evidence/zzz-lc-ev/"*-completed/bundle.json >/dev/null 2>&1 && { printf 'PASS T12 bundle manifest\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 bundle manifest missing\n'; FAIL=$((FAIL+1)); }
check "T12 completed digest comment recorded" "\[OBSERVER\] COMPLETED agent=zzz-lc-ev" "$sd/events.jsonl"
check "T12 staging row carries evidence" '"evidence_bundle"' "$sd/model-evidence-staging.jsonl"

# ---------------------------------------------------------------------------
note "T13 event-driven fast path (F2: cursor, classification, same-cycle fire)"
sd="$TESTS/t13"; rm -rf "$sd"; mkdir -p "$sd"
cat > "$sd/agent.log" <<'LOGEOF'
timestamp=2026-08-24T07:00:00.000Z level=INFO run=abc message=tracking cwd=/tmp/opencode/observer-tests/fake-wt/zzz-lc-fast session.id=ses_fastknown001
LOGEOF
export TEST_OPENCODE_LOG="$sd/agent.log"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-fast RUNNING-ALIVE builder ALIVE RUNNING
# cycle 1: baseline cursor at EOF; nothing classified
run_cycle "$sd" "$fx"
check_absent "T13 baseline classifies nothing" "fastpath-classification" "$sd/events.jsonl"
# deep-probe the tracked agent so its known session id is recorded
fx2="$sd/fix2.json"; fixture "$fx2" zzz-lc-fast STALE-SUSPECT builder ALIVE RUNNING
run_cycle "$sd" "$fx2"
# append fatal + parked signatures; next cycle must classify them SAME cycle
cat >> "$sd/agent.log" <<'LOGEOF'
timestamp=2026-08-24T07:05:00.000Z level=ERROR run=abc message="stream error" providerID=opencode-go modelID=m1 session.id=ses_fastknown001 error.error="AI_APICallError: This model requires opt-in consent before use."
timestamp=2026-08-24T07:05:01.000Z level=ERROR run=abc message="stream error" providerID=opencode-go modelID=m1 session.id=ses_other002 error.error="AI_APICallError: Rate limit exceeded." retry-after: 2026-08-24 09:30
timestamp=2026-08-24T07:05:02.000Z level=ERROR run=abc message="stream error" providerID=opencode-go modelID=m1 session.id=ses_other002 error.error="AI_RetryError: retries exhausted after 5 attempts"
LOGEOF
fx3="$sd/fix3.json"; fixture "$fx3" zzz-lc-fast STALE-SUSPECT builder ALIVE RUNNING
run_cycle "$sd" "$fx3"
check "T13 consent-gate classified"   '"class":"CONSENT-GATE-FATAL"' "$sd/events.jsonl"
check "T13 parked-retrying classified" '"class":"PARKED-RETRYING"' "$sd/events.jsonl"
check "T13 retry-exhausted classified" '"class":"RETRY-EXHAUSTED-DEAD"' "$sd/events.jsonl"
check "T13 fatal alert posted same cycle" "\[OBSERVER\]\[FAST\] CONSENT-GATE-FATAL" "$sd/events.jsonl"
check "T13 attribution to tracked agent" '"agent":"zzz-lc-fast"' "$sd/events.jsonl"
BEFORE_N=$(grep -c "fastpath-classification" "$sd/events.jsonl")
run_cycle "$sd" "$fx3"
AFTER_N=$(grep -c "fastpath-classification" "$sd/events.jsonl")
if [ "$BEFORE_N" = "$AFTER_N" ]; then printf 'PASS T13 dedup suppresses repeats\n'; PASS=$((PASS+1));
else printf 'FAIL T13 dedup: %s -> %s classifications\n' "$BEFORE_N" "$AFTER_N"; FAIL=$((FAIL+1)); fi
unset TEST_OPENCODE_LOG

# ---------------------------------------------------------------------------
note "T14 commit-age signal (F3: overdue event, accelerated + graced escalation)"
root="$TESTS/fake-repo3"; rm -rf "$root"; mkdir -p "$root/.worktrees/zzz-lc-slow" "$root/.worktrees/zzz-lc-fresh"
git -C "$root/.worktrees/zzz-lc-slow" init -q -b main
git -C "$root/.worktrees/zzz-lc-slow" config user.email t@t; git -C "$root/.worktrees/zzz-lc-slow" config user.name t
echo old > "$root/.worktrees/zzz-lc-slow/f.txt"
git -C "$root/.worktrees/zzz-lc-slow" add f.txt
GIT_AUTHOR_DATE="2026-08-20T10:00:00" GIT_COMMITTER_DATE="2026-08-20T10:00:00" \
    git -C "$root/.worktrees/zzz-lc-slow" commit -qm old-commit
git -C "$root/.worktrees/zzz-lc-fresh" init -q -b main
git -C "$root/.worktrees/zzz-lc-fresh" config user.email t@t; git -C "$root/.worktrees/zzz-lc-fresh" config user.name t
echo new > "$root/.worktrees/zzz-lc-fresh/f.txt"
git -C "$root/.worktrees/zzz-lc-fresh" add f.txt
git -C "$root/.worktrees/zzz-lc-fresh" commit -qm fresh-commit
export TEST_REPO_ROOT="$root"
# (a) RUNNING-ALIVE with stale commit -> deduped commit-overdue event
sd="$TESTS/t14a"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-slow RUNNING-ALIVE builder ALIVE RUNNING
run_cycle "$sd" "$fx"
check "T14a commit-overdue fired"      "commit-overdue" "$sd/events.jsonl"
run_cycle "$sd" "$fx"
check "T14a overdue deduped on rerun"  '"event":"commit-overdue"' "$sd/events.jsonl"
test "$(grep -c '"event":"commit-overdue"' "$sd/events.jsonl")" -eq 1 && { printf 'PASS T14a exactly one overdue event\n'; PASS=$((PASS+1)); } || { printf 'FAIL T14a overdue event count != 1\n'; FAIL=$((FAIL+1)); }
# (b) STALE-SUSPECT with stale commit -> escalate on FIRST quiet cycle
sd="$TESTS/t14b"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-slow STALE-SUSPECT builder ALIVE RUNNING
run_cycle "$sd" "$fx"
check "T14b immediate escalation"      "last commit .* min old exceeds" "$sd/events.jsonl"
check "T14b termination recorded"      "frozen-termination" "$sd/events.jsonl"
check_absent "T14b no plain warning first" "stale-warning" "$sd/events.jsonl"
# (c) STALE-SUSPECT with FRESH commit -> warning, extra grace, then escalate
sd="$TESTS/t14c"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-fresh STALE-SUSPECT builder ALIVE RUNNING
run_cycle "$sd" "$fx"
check "T14c first cycle warning only"  "stale-warning" "$sd/events.jsonl"
check "T14c grace noted"               "grace cycle" "$sd/events.jsonl"
check_absent "T14c no escalation yet"  "frozen-termination" "$sd/events.jsonl"
run_cycle "$sd" "$fx"
check_absent "T14c grace cycle holds"  "frozen-termination" "$sd/events.jsonl"
run_cycle "$sd" "$fx"
check "T14c escalates after grace"     "STALE-SUSPECT escalated after" "$sd/events.jsonl"
unset TEST_REPO_ROOT

printf '\nRESULT: %d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
