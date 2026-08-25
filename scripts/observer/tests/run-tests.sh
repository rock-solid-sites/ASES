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
# C2 (#460 v1.1): canonical test-side orchestrator identity. Fixture
# worktrees carry a matching .owner-orchestrator stamp so owner-match is
# the default; individual tests override to exercise downgrades.
TEST_ORCH_ID="obs-test-orchestrator"

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
        # C1 (#460 v1.1): hermetic flag issue - gate/hub decisions must not
        # depend on live hub state; an unresolvable number fails fast and
        # deterministically (last_hub_position -> None).
        export OBSERVER_FLAG_ISSUE="${OBSERVER_FLAG_ISSUE:-999999}"
        # C2 (#460 v1.1): default test identity (owner-match default).
        export OBSERVER_ORCHESTRATOR_ID="${OBSERVER_ORCHESTRATOR_ID:-$TEST_ORCH_ID}"
        # F4 backup pass OFF by default: every test uses a fresh state dir,
        # so an enabled pass would hot-copy the REAL multi-GB stores each
        # cycle. T15 opts back in explicitly with fixture stores.
        export OBSERVER_BACKUP_ENABLED="${OBSERVER_BACKUP_ENABLED:-0}"
        for kv in "$@"; do export "$kv"; done
        # FIX 1 (#465 F1) hermeticity proof: cycles run from a NEUTRAL cwd
        # (not the repo, not the project). Before the fix, crosslink-based
        # checks silently no-op'd here (T16 issue-exists/claimed failed);
        # after the fix the script anchors itself and this is green from
        # anywhere.
        cd /
        bash "$MANAGER" --once >/dev/null 2>&1
    )
}

mkdir -p "$TESTS"
: > "$TESTS/empty.log"

# FIX 3 (#466 F3) fixture: a real git repo whose agent worktree carries a
# COMMITTED file delta vs main, so deliverable_check() can actually pass
# (cleanup is now gated on that check).
make_deliverable_wt() { # make_deliverable_wt <root> <agent>
    local root="$1" agent="$2"
    mkdir -p "$root/.worktrees"
    git -C "$root" init -q -b main
    git -C "$root" config user.email t@t
    git -C "$root" config user.name t
    printf 'base\n' > "$root/base.txt"
    git -C "$root" add base.txt
    git -C "$root" commit -qm base
    git -C "$root" worktree add -q -b "feature/$agent" \
        "$root/.worktrees/$agent"
    printf 'deliverable\n' > "$root/.worktrees/$agent/deliverable.txt"
    git -C "$root/.worktrees/$agent" add deliverable.txt
    git -C "$root/.worktrees/$agent" commit -qm "deliverable for $agent"
    # C2 (#460 v1.1): launcher-written owner stamp (immutable per
    # execution); default fixtures belong to the canonical test identity.
    printf '%s\n' "$TEST_ORCH_ID" > "$root/.worktrees/$agent/.owner-orchestrator"
}

# C3 fixture: worktree whose last commit is deliberately OLD (the P1
# commit-stale authoritative signal) + owner stamp.
make_stale_wt() { # make_stale_wt <root> <agent> [orch_id]
    local root="$1" agent="$2" orch="${3:-$TEST_ORCH_ID}"
    mkdir -p "$root/.worktrees"
    git -C "$root" init -q -b main
    git -C "$root" config user.email t@t
    git -C "$root" config user.name t
    printf 'base\n' > "$root/base.txt"
    git -C "$root" add base.txt
    git -C "$root" commit -qm base
    git -C "$root" worktree add -q -b "feature/$agent" \
        "$root/.worktrees/$agent"
    printf 'stale work\n' > "$root/.worktrees/$agent/stale.txt"
    git -C "$root/.worktrees/$agent" add stale.txt
    GIT_AUTHOR_DATE="2026-08-20T10:00:00" \
        GIT_COMMITTER_DATE="2026-08-20T10:00:00" \
        git -C "$root/.worktrees/$agent" commit -qm "stale commit for $agent"
    printf '%s\n' "$orch" > "$root/.worktrees/$agent/.owner-orchestrator"
}

# C3 helper: rewrite the last commit's dates so commit_age crosses the
# staleness threshold (tree unchanged).
backdate_last_commit() { # backdate_last_commit <worktree-path>
    GIT_AUTHOR_DATE="2026-08-20T10:00:00" \
        GIT_COMMITTER_DATE="2026-08-20T10:00:00" \
        git -C "$1" commit -q --amend --no-edit
}

# ---------------------------------------------------------------------------
note "T1 COMPLETED transition (deliverable gate PASSES -> cleanup fires)"
sd="$TESTS/t1"; root="$TESTS/t1-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-done
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-done DONE-CONFIRMED builder EXITED DONE
run_cycle "$sd" "$fx"
check "T1 cleanup dry-run recorded"   "cleanup-dry-run" "$sd/events.jsonl"
check "T1 deliverable verified note"  "Deliverable verified" "$sd/events.jsonl"
check "T1 staging row appended"       "model-evidence-row" "$sd/events.jsonl"
check "T1 outcome completed"          '"outcome":"completed"' "$sd/model-evidence-staging.jsonl"
check "T1 phase completed"            '"phase": *"completed"\|"phase":"completed"' "$sd/manager-state.json"
unset TEST_REPO_ROOT

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
# FIX 4 (#466 F1): expiry with a FRESH rate-limit signature still in the
# attributed tail -> park EXTENDED (resume_at = max(parsed, now+grace)),
# never killed.
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
check "T5 fresh signature extends park" '"event":"parked-extended"' "$sd/events.jsonl"
check "T5 extension source recorded"    '"resume_at_source": *"park-extension-fresh-signature"' "$sd/manager-state.json"
check_absent "T5 no kill while signature live" "frozen-termination" "$sd/events.jsonl"
# floor: parsed retry-after (2026-08-24 09:30) is in the PAST; the extended
# resume_at must be at least now + default grace (60 min), not the stale parse
python3 - "$sd/manager-state.json" <<'PYEOF'
import json, sys, time
path = sys.argv[1]
with open(path) as fh: state = json.load(fh)
epoch = state["agents"]["zzz-lc-parked"]["resume_at_epoch"]
floor = time.time() + 3000  # 60-min grace minus 10-min slack
if epoch >= floor:
    print("PASS T5 extension floor = max(parsed, now+grace)")
    sys.exit(0)
print("FAIL T5 extension floor violated: %s < %s" % (epoch, floor))
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
# expiry with a CLEAN tail (no parking evidence) -> kill fires
cat > "$sd/agent-clean.log" <<'LOGEOF'
timestamp=2026-08-24T07:00:00.000Z level=INFO run=abc message=tracking cwd=/tmp/opencode/observer-tests/fake-wt/zzz-lc-parked session.id=ses_testparked001
timestamp=2026-08-24T07:00:01.000Z level=INFO run=abc message="llm runtime selected" llm.runtime=ai-sdk llm.provider=opencode-go llm.model=test-model-free session.id=ses_testparked001
LOGEOF
export TEST_OPENCODE_LOG="$sd/agent-clean.log"
python3 - "$sd/manager-state.json" <<'PYEOF'
import json, sys
path = sys.argv[1]
with open(path) as fh: state = json.load(fh)
rec = state["agents"]["zzz-lc-parked"]
rec["resume_at"] = "2026-08-24T00:00:00+00:00"
rec["resume_at_epoch"] = 1
with open(path, "w") as fh: json.dump(state, fh)
PYEOF
fx3="$sd/fix3.json"; fixture "$fx3" zzz-lc-parked LIKELY-FROZEN builder ALIVE RUNNING
# C3: the clean tail was first sighted at this expiry attempt -> log-quiet
# undecidable -> gate holds; the SECOND expiry evaluation converges.
run_cycle "$sd" "$fx3"
check "T5 expiry reclassified frozen" "parked-expired" "$sd/events.jsonl"
check_absent "T5 first expiry held by gate" "frozen-termination" "$sd/events.jsonl"
run_cycle "$sd" "$fx3"
check "T5 termination after clean-tail expiry" "frozen-termination" "$sd/events.jsonl"
unset TEST_OPENCODE_LOG

# ---------------------------------------------------------------------------
note "T6 FROZEN direct (evidence bundle + auto-kill + termination record)"
# C2/C3 refit: the agent owns a stamped worktree whose last commit is
# deliberately OLD - owner-match lets the dry-run stop/cleanup fire now,
# and the stale commit provides the P1 authoritative signal the convergent
# gate will require once C3 lands.
sd="$TESTS/t6"; root="$TESTS/t6-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_stale_wt "$root" zzz-lc-frozen
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-frozen LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx"
# C2: observe mode records intents authorization-free but carries the
# ownership fact on the record; act-mode owner-match enforcement is proven
# end-to-end by T20b (real cleanup executes).
check "T6 stop record carries owner fact" '"owner_orchestrator":"obs-test-orchestrator"' "$sd/events.jsonl"
check "T6 stop dry-run recorded"      "stop-dry-run" "$sd/events.jsonl"
check "T6 cleanup dry-run recorded"   "cleanup-dry-run" "$sd/events.jsonl"
check "T6 termination record"         "frozen-termination" "$sd/events.jsonl"
check "T6 spiral authority cited"     "#443 rev3" "$sd/events.jsonl"
check "T6 relaunch recommendation"    "relaunch-with-backup-model" "$sd/events.jsonl"
ls "$sd/evidence/zzz-lc-frozen"/*/bundle.json >/dev/null 2>&1 && { printf 'PASS T6 bundle manifest\n'; PASS=$((PASS+1)); } || { printf 'FAIL T6 bundle manifest missing\n'; FAIL=$((FAIL+1)); }
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T7 STALE-SUSPECT warning cycle then escalation"
# C3-aware sequence: fresh commit -> warning cycle; escalation fires but
# the convergent gate HOLDS it (no P1 yet); once the commit goes stale the
# same escalation converges and terminates.
sd="$TESTS/t7"; root="$TESTS/t7-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-stale
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-stale STALE-SUSPECT builder ALIVE RUNNING
run_cycle "$sd" "$fx"
check "T7 first cycle warning only"   "stale-warning" "$sd/events.jsonl"
check_absent "T7 no escalation yet"   "frozen-termination" "$sd/events.jsonl"
run_cycle "$sd" "$fx"
# fresh commit grants one extra grace cycle (F3)
check_absent "T7 grace cycle holds"   "STALE-SUSPECT escalated" "$sd/events.jsonl"
run_cycle "$sd" "$fx"
check "T7 escalation fires"           "STALE-SUSPECT escalated" "$sd/events.jsonl"
check_absent "T7 gate holds unconfirmed escalation" "frozen-termination" "$sd/events.jsonl"
check "T7 gate-held recorded"         '"event":"termination-gate-held"' "$sd/events.jsonl"
backdate_last_commit "$root/.worktrees/zzz-lc-stale"
run_cycle "$sd" "$fx"
check "T7 termination after convergence" "frozen-termination" "$sd/events.jsonl"
unset TEST_REPO_ROOT

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
# C3 refit: stale-commit worktree lets the convergent gate ADMIT the
# termination so the breaker window is actually exercised by stop/cleanup.
sd="$TESTS/t9"; root="$TESTS/t9-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_stale_wt "$root" zzz-lc-brk
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-brk LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx" "OBSERVER_MAX_ACTIONS_PER_HOUR=1"
check "T9 breaker halt event"         "breaker-halt" "$sd/events.jsonl"
unset TEST_REPO_ROOT

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
sd="$TESTS/t12"; root="$TESTS/t12-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-ev
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-ev DONE-CONFIRMED builder EXITED DONE
run_cycle "$sd" "$fx"
ls "$sd/evidence/zzz-lc-ev/"*-completed/verdict-timeline.json >/dev/null 2>&1 && { printf 'PASS T12 verdict timeline section\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 verdict timeline section missing\n'; FAIL=$((FAIL+1)); }
ls "$sd/evidence/zzz-lc-ev/"*-completed/git-status.txt >/dev/null 2>&1 && { printf 'PASS T12 git status section\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 git status section missing\n'; FAIL=$((FAIL+1)); }
ls "$sd/evidence/zzz-lc-ev/"*-completed/hub-position.json >/dev/null 2>&1 && { printf 'PASS T12 hub position section\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 hub position section missing\n'; FAIL=$((FAIL+1)); }
ls "$sd/evidence/zzz-lc-ev/"*-completed/bundle.json >/dev/null 2>&1 && { printf 'PASS T12 bundle manifest\n'; PASS=$((PASS+1)); } || { printf 'FAIL T12 bundle manifest missing\n'; FAIL=$((FAIL+1)); }
check "T12 completed digest comment recorded" "\[OBSERVER\] COMPLETED agent=zzz-lc-ev" "$sd/events.jsonl"
check "T12 staging row carries evidence" '"evidence_bundle"' "$sd/model-evidence-staging.jsonl"
unset TEST_REPO_ROOT

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

# ---------------------------------------------------------------------------
note "T15 dual-store backup subsystem (F4: hot copy, incremental export, GREEN verification, pending flag, prune gate)"
f4root="$TESTS/f4-root"; f4arch="$TESTS/f4-archive"; sd="$TESTS/t15"
rm -rf "$f4root" "$f4arch" "$sd"; mkdir -p "$f4root" "$f4arch" "$sd"
python3 - "$f4root" <<'PYEOF'
import sqlite3, sys, os
root = sys.argv[1]
for name in ("opencode.db", "opencode-fork-pp3g.db"):
    conn = sqlite3.connect(os.path.join(root, name))
    conn.execute("CREATE TABLE session (id TEXT PRIMARY KEY, "
                 "directory TEXT, title TEXT, time_created INTEGER, "
                 "time_updated INTEGER)")
    conn.execute("INSERT INTO session VALUES "
                 "('ses_a1','/wt/a','alpha',1000,2000)")
    conn.execute("INSERT INTO session VALUES "
                 "('ses_a2','/wt/b','beta',1500,2500)")
    conn.commit()
    conn.close()
PYEOF
fx="$sd/fix.json"; fixture "$fx" zzz-none RUNNING-ALIVE builder ALIVE RUNNING
BKENV=(OBSERVER_BACKUP_ENABLED=1 OBSERVER_BACKUP_INTERVAL_MINS=0
       OBSERVER_ARCHIVE_DIR="$f4arch" OBSERVER_STORES_ROOT="$f4root"
       OBSERVER_STORES=main:opencode.db,fork:opencode-fork-pp3g.db
       OBSERVER_RCLONE_REMOTE=totally-absent-remote
       OBSERVER_PRUNE_AGE_DAYS=30)
# pass 1: baseline export of both fixture stores
run_cycle "$sd" "$fx" "${BKENV[@]}"
ls "$f4arch/hot-backups/main/"*.db >/dev/null 2>&1 && { printf 'PASS T15 main hot copy\n'; PASS=$((PASS+1)); } || { printf 'FAIL T15 main hot copy missing\n'; FAIL=$((FAIL+1)); }
ls "$f4arch/hot-backups/fork/"*.db >/dev/null 2>&1 && { printf 'PASS T15 fork hot copy\n'; PASS=$((PASS+1)); } || { printf 'FAIL T15 fork hot copy missing\n'; FAIL=$((FAIL+1)); }
check "T15 GREEN verify main"   "GREEN | store=main" "$f4arch/verification.log"
check "T15 GREEN verify fork"   "GREEN | store=fork" "$f4arch/verification.log"
check "T15 index keyed row"     '"session_id":"ses_a1"' "$f4arch/index/main.ndx"
check "T15 index carries artifact ref" '"export_file":"exports/' "$f4arch/index/main.ndx"
check "T15 sync pending explicit" "PENDING | remote=" "$f4arch/sync-pending.log"
check "T15 absent remote named in pending" "totally-absent-remote" "$f4arch/sync-pending.log"
check "T15 local-mode ack in events (FIX 6 gate)" '"event":"backup-sync-pending"' "$sd/events.jsonl"
check "T15 prune report gated GREEN" "gate=GREEN" "$f4arch/prune-report.txt"
N1=$(ls "$f4arch/exports/"*/*.jsonl.gz 2>/dev/null | wc -l)
test "$N1" -eq 2 && { printf 'PASS T15 one artifact per store\n'; PASS=$((PASS+1)); } || { printf 'FAIL T15 expected 2 artifacts got %s\n' "$N1"; FAIL=$((FAIL+1)); }
# pass 2: no new rows -> export-empty, watermark holds, artifact count stable
run_cycle "$sd" "$fx" "${BKENV[@]}"
E2=$(grep -c "backup-export-empty" "$sd/events.jsonl")
test "$E2" -ge 2 && { printf 'PASS T15 empty exports reported\n'; PASS=$((PASS+1)); } || { printf 'FAIL T15 expected >=2 export-empty got %s\n' "$E2"; FAIL=$((FAIL+1)); }
N2=$(ls "$f4arch/exports/"*/*.jsonl.gz 2>/dev/null | wc -l)
test "$N2" -eq 2 && { printf 'PASS T15 no duplicate artifacts\n'; PASS=$((PASS+1)); } || { printf 'FAIL T15 artifact count drifted: %s\n' "$N2"; FAIL=$((FAIL+1)); }
# pass 3: one new row -> exactly one new single-row artifact (incremental)
python3 - "$f4root" <<'PYEOF'
import sqlite3, sys, os
conn = sqlite3.connect(os.path.join(sys.argv[1], "opencode.db"))
conn.execute("INSERT INTO session VALUES "
             "('ses_a3','/wt/c','gamma',2800,3000)")
conn.commit()
conn.close()
PYEOF
run_cycle "$sd" "$fx" "${BKENV[@]}"
N3=$(ls "$f4arch/exports/"*/*.jsonl.gz 2>/dev/null | wc -l)
test "$N3" -eq 3 && { printf 'PASS T15 incremental artifact added\n'; PASS=$((PASS+1)); } || { printf 'FAIL T15 expected 3 artifacts got %s\n' "$N3"; FAIL=$((FAIL+1)); }
check "T15 new row exported alone" "rows=1 sha256=" "$f4arch/verification.log"
check "T15 new row indexed"       '"session_id":"ses_a3"' "$f4arch/index/main.ndx"
# generation cap: KEEP=1 -> exactly one .db per label after three passes
G=$(ls "$f4arch/hot-backups/main/"*.db 2>/dev/null | wc -l)
test "$G" -eq 1 && { printf 'PASS T15 generation cap enforced\n'; PASS=$((PASS+1)); } || { printf 'FAIL T15 expected 1 generation got %s\n' "$G"; FAIL=$((FAIL+1)); }

# ---------------------------------------------------------------------------
note "T16 admission-policy absorption (F5: model/issue/claim/estimate checks + audit trail)"
root="$TESTS/t16-root"; sd="$TESTS/t16"
rm -rf "$root" "$sd"; mkdir -p "$root/.worktrees/zzz-adm-good" \
    "$root/.worktrees/zzz-adm-badmodel" "$root/.worktrees/zzz-adm-noest" "$sd"
cat > "$root/.worktrees/zzz-adm-good/KICKOFF.md" <<'EOF'
# KICKOFF: good contract
**Issue**: #460
--model opencode-go/real-model
Estimated duration: 45 minutes
EOF
cat > "$root/.worktrees/zzz-adm-badmodel/KICKOFF.md" <<'EOF'
# KICKOFF: bad model
**Issue**: #460
--model opencode-go/fake-model-xyz
Estimated duration: 30 minutes
EOF
cat > "$root/.worktrees/zzz-adm-noest/KICKOFF.md" <<'EOF'
# KICKOFF: contract without duration note
**Issue**: #460
--model opencode-go/real-model
EOF
cat > "$sd/fake-models.sh" <<'EOF'
#!/usr/bin/env bash
# deterministic stand-in for the OBSERVER_MODELS_CMD template; the
# substituted {provider} arrives as $1
if [ "$1" = "opencode-go" ]; then
    printf 'opencode-go/real-model\nopencode-go/other-model\n'
else
    printf 'opencode/free-one\n'
fi
EOF
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"
python3 - "$fx" <<'PYEOF'
import json, sys
def row(agent):
    return {"agent": agent, "status": "RUNNING", "aliveness": "ALIVE",
            "age_min": 1.0, "source": "walk", "role": "builder",
            "verdict": "RUNNING-ALIVE",
            "last_activity": "2026-08-24T06:00:00+00:00",
            "budget_min": 45.0, "probe": {"state": "ALIVE"}}
payload = {"generated_at": "2026-08-24T07:10:00+00:00", "root": "/x",
           "budget_min": 45.0, "state_dir": "/x",
           "agents": [row("zzz-adm-good"), row("zzz-adm-badmodel"),
                      row("zzz-adm-noest")],
           "skipped_no_signal": []}
with open(sys.argv[1], "w") as fh:
    json.dump(payload, fh)
PYEOF
run_cycle "$sd" "$fx" "OBSERVER_MODELS_CMD=bash $sd/fake-models.sh {provider}"
# FIX 1 (#465 F1): cycles now run from a neutral cwd (see run_cycle); the
# issue-exists/issue-claimed checks reach the live crosslink repo through
# the script's own anchored CROSSLINK_ROOT, so they are CWD-independent.
# NOTE: issue-exists ok:true is the hermeticity discriminator (#460 exists
# permanently). issue-claimed depends on SESSION lock state, not script
# correctness: ok:true whenever #460 is locked (kickoff/shakedown sessions),
# ok:false otherwise - the suite asserts the check executed and returned a
# definitive boolean either way.
check "T16 valid model accepted"   '"check":"model-valid","ok":true,"model":"opencode-go/real-model"' "$sd/events.jsonl"
check "T16 invalid model flagged"  '"check":"model-valid","ok":false,"model":"opencode-go/fake-model-xyz"' "$sd/events.jsonl"
check "T16 issue-exists true"      '"check":"issue-exists","ok":true,"issue":"460"' "$sd/events.jsonl"
CLAIMED_OK=$(grep -c '"check":"issue-claimed","ok":true,"issue":"460"' "$sd/events.jsonl")
CLAIMED_ANY=$(grep -c '"check":"issue-claimed","ok":\(true\|false\),"issue":"460"' "$sd/events.jsonl")
if [ "$CLAIMED_ANY" -ge 1 ]; then printf 'PASS T16 issue-claimed executed (%s definitive, %s claimed)\n' "$CLAIMED_ANY" "$CLAIMED_OK"; PASS=$((PASS+1));
else printf 'FAIL T16 issue-claimed check never produced a verdict\n'; FAIL=$((FAIL+1)); fi
check "T16 estimate detected"      '"check":"estimate-declared","ok":true' "$sd/events.jsonl"
check "T16 missing estimate fails" '"check":"estimate-declared","ok":false' "$sd/events.jsonl"
check "T16 violation alert posted" "\[OBSERVER\]\[ADMISSION\]" "$sd/events.jsonl"
A1=$(grep -c "\[OBSERVER\]\[ADMISSION\]" "$sd/events.jsonl")
run_cycle "$sd" "$fx" "OBSERVER_MODELS_CMD=bash $sd/fake-models.sh {provider}"
A2=$(grep -c "\[OBSERVER\]\[ADMISSION\]" "$sd/events.jsonl")
test "$A1" = "$A2" && { printf 'PASS T16 alert deduped until fingerprint changes\n'; PASS=$((PASS+1)); } || { printf 'FAIL T16 alert not deduped: %s -> %s\n' "$A1" "$A2"; FAIL=$((FAIL+1)); }
N=$(grep -c '"event":"admission-check"' "$sd/events.jsonl")
test "$N" -ge 12 && { printf 'PASS T16 audit trail populated (%s checks)\n' "$N"; PASS=$((PASS+1)); } || { printf 'FAIL T16 audit trail thin: %s\n' "$N"; FAIL=$((FAIL+1)); }
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T17 wave-anomaly all-agents-vanish (F6: platform-restart signature, dedup, re-arm)"
sd="$TESTS/t17"; rm -rf "$sd"; mkdir -p "$sd"
fx1="$sd/fix1.json"; fixture "$fx1" zzz-wv RUNNING-ALIVE builder ALIVE RUNNING
python3 - "$sd/fix0.json" <<'PYEOF'
import json, sys
payload = {"generated_at": "2026-08-24T07:10:00+00:00", "root": "/x",
           "budget_min": 45.0, "state_dir": "/x", "agents": [],
           "skipped_no_signal": []}
with open(sys.argv[1], "w") as fh:
    json.dump(payload, fh)
PYEOF
run_cycle "$sd" "$fx1"                                  # baseline: tracked active
run_cycle "$sd" "$sd/fix0.json"                         # mass vanish
check "T17 wave-anomaly event"          '"event":"wave-anomaly"' "$sd/events.jsonl"
check "T17 platform-restart signature"  '"signature":"platform-restart-suspected"' "$sd/events.jsonl"
check "T17 alert names vanished agent"  "all-agents-vanish: 1 tracked active/parked agent(s) (zzz-wv)" "$sd/events.jsonl"
C1=$(grep -c "WAVE-ANOMALY" "$sd/events.jsonl")
run_cycle "$sd" "$sd/fix0.json"                         # still gone: deduped
C2=$(grep -c "WAVE-ANOMALY" "$sd/events.jsonl")
test "$C1" = "$C2" && { printf 'PASS T17 anomaly deduped per episode\n'; PASS=$((PASS+1)); } || { printf 'FAIL T17 anomaly not deduped: %s -> %s\n' "$C1" "$C2"; FAIL=$((FAIL+1)); }
run_cycle "$sd" "$fx1"                                  # reappearance
check "T17 rearm on reappearance"       '"event":"wave-anomaly-rearmed"' "$sd/events.jsonl"
run_cycle "$sd" "$sd/fix0.json"                         # vanishes again
C3=$(grep -c "WAVE-ANOMALY" "$sd/events.jsonl")
test "$C3" -eq $((C2 + 1)) && { printf 'PASS T17 second episode alerts again\n'; PASS=$((PASS+1)); } || { printf 'FAIL T17 expected %s alerts got %s\n' "$((C2 + 1))" "$C3"; FAIL=$((FAIL+1)); }

# ---------------------------------------------------------------------------
note "T18 COMPLETED with UNVERIFIED deliverable -> NO cleanup, worktree preserved (FIX 3 / #466 F3)"
# (a) branch missing entirely: no worktree, no ref -> gate indeterminate
sd="$TESTS/t18a"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-nodel DONE-CONFIRMED builder EXITED DONE
run_cycle "$sd" "$fx"
check_absent "T18a no cleanup on unverified deliverable" "cleanup-dry-run" "$sd/events.jsonl"
check "T18a skip event recorded"       '"event":"cleanup-skipped"' "$sd/events.jsonl"
check "T18a sweep flag preserves worktree" "completed-deliverable-unverified-worktree-preserved" "$sd/events.jsonl"
check "T18a staging skip reason"       "skipped-unverified-deliverable" "$sd/model-evidence-staging.jsonl"
check "T18a orchestrator flag comment" "Cleanup SKIPPED" "$sd/events.jsonl"
check "T18a phase still completed"     '"phase": *"completed"\|"phase":"completed"' "$sd/manager-state.json"
# (b) EMPTY branch: ref exists but zero file delta vs main - the exact
# #460 false-positive class; deliverable_present must be False.
root="$TESTS/t18-root"; sd="$TESTS/t18b"; rm -rf "$root" "$sd"; mkdir -p "$sd" "$root/.worktrees"
git -C "$root" init -q -b main
git -C "$root" config user.email t@t; git -C "$root" config user.name t
printf 'base\n' > "$root/base.txt"
git -C "$root" add base.txt
git -C "$root" commit -qm base
git -C "$root" worktree add -q -b feature/zzz-lc-empty "$root/.worktrees/zzz-lc-empty"
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-empty DONE-CONFIRMED builder EXITED DONE
run_cycle "$sd" "$fx"
check_absent "T18b no cleanup on empty branch" "cleanup-dry-run" "$sd/events.jsonl"
check "T18b skip event recorded"       '"event":"cleanup-skipped"' "$sd/events.jsonl"
check "T18b files_changed zero reported" '"files_changed": *0\|"files_changed":0' "$sd/events.jsonl"
check "T18b sweep flag preserves worktree" "completed-deliverable-unverified-worktree-preserved" "$sd/events.jsonl"
test -d "$root/.worktrees/zzz-lc-empty" && { printf 'PASS T18b worktree physically preserved\n'; PASS=$((PASS+1)); } || { printf 'FAIL T18b worktree gone\n'; FAIL=$((FAIL+1)); }
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T19 instance lockfile (FIX 5 / #466 F6: refuse double-run, recover stale lock)"
sd="$TESTS/t19"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-lock RUNNING-ALIVE builder ALIVE RUNNING
# (a) LIVE holder -> loud refusal, nonzero exit, foreign lock untouched
sleep 30 &
HOLDER=$!
printf '%s\n' "$HOLDER" > "$sd/observer.lock"
rc=0
(
    export OBSERVER_DRY_RUN=1 OBSERVER_STATE_DIR="$sd" \
        OBSERVER_INPUT_JSON="$fx" \
        OBSERVER_OPENCODE_LOG="$TESTS/empty.log" \
        OBSERVER_REPO_ROOT="$TESTS/fake-repo" \
        OBSERVER_BACKUP_ENABLED=0
    cd /
    bash "$MANAGER" --once
) >/dev/null 2>"$sd/stderr.txt" || rc=$?
if [ "$rc" -ne 0 ]; then printf 'PASS T19 second instance refused (rc=%s)\n' "$rc"; PASS=$((PASS+1));
else printf 'FAIL T19 second instance ran despite live lock\n'; FAIL=$((FAIL+1)); fi
check "T19 refusal event recorded"     '"kind":"instance-lock-held"' "$sd/events.jsonl"
if grep -q "REFUSING to start" "$sd/stderr.txt" 2>/dev/null; then printf 'PASS T19 loud stderr refusal\n'; PASS=$((PASS+1));
else printf 'FAIL T19 no loud stderr refusal\n'; FAIL=$((FAIL+1)); fi
LOCKPID_NOW="$(cat "$sd/observer.lock" 2>/dev/null || true)"
if [ "$LOCKPID_NOW" = "$HOLDER" ]; then printf 'PASS T19 foreign lock not removed\n'; PASS=$((PASS+1));
else printf 'FAIL T19 foreign lock disturbed: %s\n' "$LOCKPID_NOW"; FAIL=$((FAIL+1)); fi
kill "$HOLDER" 2>/dev/null; wait "$HOLDER" 2>/dev/null
# (b) STALE holder (dead pid) -> recovered exactly once, cycle proceeds,
# and our own lock is removed on exit by the trap.
printf '%s\n' "$HOLDER" > "$sd/observer.lock"
run_cycle "$sd" "$fx"
check "T19 stale recovery event"       '"event":"instance-lock-stale-recovered"' "$sd/events.jsonl"
check "T19 cycle executed after recovery" '"event":"cycle"' "$sd/events.jsonl"
if [ ! -f "$sd/observer.lock" ]; then printf 'PASS T19 own lock released on exit\n'; PASS=$((PASS+1));
else printf 'FAIL T19 own lock leaked\n'; FAIL=$((FAIL+1)); fi

# ---------------------------------------------------------------------------
note "T20a saturated mutation window denies cleanup LOUDLY (shakedown #460)"
# Production failure reproduction: 2026-08-25 05:26-05:31 the leftover-fleet
# triage consumed all 24 window slots; the healthy builder YBKJ legitimate
# cleanup at 05:54:54 was then denied by the breaker SILENTLY (no subprocess,
# no out/err event, halt event already fired) - surfacing only as
# cleanup_ok:false. Pre-seed the exact production state (full window) and
# require the deny to emit its own cleanup event.
sd="$TESTS/t20a"; root="$TESTS/t20a-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-denied
export TEST_REPO_ROOT="$root"
python3 - "$sd/manager-state.json" <<'PYEOF'
import json, sys, time
now = time.time()
with open(sys.argv[1], "w") as fh:
    json.dump({"agents": {}, "action_window": [now - i for i in range(24)]}, fh)
PYEOF
fx="$sd/fix.json"; fixture "$fx" zzz-lc-denied DONE-CONFIRMED builder EXITED DONE
run_cycle "$sd" "$fx"
check "T20a deny emits cleanup event"  '"denied": *"breaker-cap"\|"denied":"breaker-cap"' "$sd/events.jsonl"
check_absent "T20a command never attempted" "cleanup-dry-run" "$sd/events.jsonl"
check "T20a transition-action failed" '"cleanup_ok": *false\|"cleanup_ok":false' "$sd/events.jsonl"

# ---------------------------------------------------------------------------
note "T20b successful cleanup resolves prior force-sweep flag (shakedown #460)"
# The pending-sweep file was append-only: a successful cleanup left stale
# flags for operator hand-reconciliation. Faithful test needs a REAL cleanup
# execution (dry-run never removes the worktree, so orphan would stay true
# and resolution must NOT fire). Hermetic real-mode cycle: PATH-shimmed
# crosslink stub simulates the cleanup side effect (worktree removal) and
# no-ops comments; admission checks off; backup off.
sd="$TESTS/t20b"; root="$TESTS/t20b-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-resv
printf '2026-08-25T05:54:54+00:00 zzz-lc-resv completed-but-worktree-remains-after-cleanup\n' \
    > "$sd/force-sweep-pending.txt"
mkdir -p "$sd/bin"
cat > "$sd/bin/crosslink" <<STUBEOF
#!/usr/bin/env bash
# test stub: real-mode stand-in for crosslink (hermetic; no hub contact)
if [ "\$1" = "kickoff" ] && [ "\$2" = "cleanup" ]; then
    agent=""
    prev=""
    for a in "\$@"; do
        if [ "\$prev" = "--only" ]; then agent="\$a"; fi
        prev="\$a"
    done
    for slug in \${agent//,/ }; do
        rm -rf "$root/.worktrees/\$slug"
    done
    printf '{"cleaned": ["%s"], "dry_run": false}\n' "\$agent"
    exit 0
fi
exit 0
STUBEOF
chmod +x "$sd/bin/crosslink"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-resv DONE-CONFIRMED builder EXITED DONE
(
    export OBSERVER_STATE_DIR="$sd" OBSERVER_INPUT_JSON="$fx"
    export OBSERVER_OPENCODE_LOG="$TESTS/empty.log"
    export OBSERVER_REPO_ROOT="$root"
    # C1 (#460 v1.1): real mutations now require EXPLICIT act-mode arming
    # (unset DRY_RUN alone resolves to observe, fail-closed).
    export OBSERVER_MODE=act
    export OBSERVER_ORCHESTRATOR_ID="$TEST_ORCH_ID"
    unset OBSERVER_DRY_RUN
    export OBSERVER_BACKUP_ENABLED=0 OBSERVER_ADMISSION_ENABLED=0
    export PATH="$sd/bin:$PATH"
    cd /
    bash "$MANAGER" --once >/dev/null 2>&1
)
check "T20b cleanup really executed"    '"event": *"cleanup"\|"event":"cleanup"' "$sd/events.jsonl"
check "T20b cleanup rc zero"            '"rc": *0\|"rc":0' "$sd/events.jsonl"
test ! -d "$root/.worktrees/zzz-lc-resv" && { printf 'PASS T20b worktree removed by cleanup\n'; PASS=$((PASS+1)); } || { printf 'FAIL T20b worktree still present\n'; FAIL=$((FAIL+1)); }
check "T20b resolution event emitted"   '"event":"force-sweep-resolved"' "$sd/events.jsonl"
check "T20b resolution line appended"   "resolved-by-cleanup-ok" "$sd/force-sweep-pending.txt"

# ---------------------------------------------------------------------------
note "T21 fail-closed execution mode (C1 #460 v1.1: default/garbage -> observe)"
# Mutation tripwire harness: a PATH-shimmed crosslink that RECORDS any
# kickoff stop/cleanup reaching it. Observe mode must never touch it;
# act mode must (proving the tripwire and the arming both work).
make_tripwire() { # make_tripwire <statedir>
    mkdir -p "$1/bin"
    cat > "$1/bin/crosslink" <<STUBEOF
#!/usr/bin/env bash
if [ "\$1" = "kickoff" ]; then
    printf 'MUTATION-ATTEMPTED %s\n' "\$*" >> "$1/mutations.txt"
fi
if [ "\$1" = "issue" ] && [ "\$2" = "comment" ]; then
    printf 'COMMENT %s\n' "\$*" >> "$1/comments.txt"
fi
exit 0
STUBEOF
    chmod +x "$1/bin/crosslink"
}
run_tripwire_cycle() { # <statedir> <fixture> [extra env KEY=VAL...]
    local sd="$1" fx="$2"; shift 2
    (
        export OBSERVER_STATE_DIR="$sd" OBSERVER_INPUT_JSON="$fx"
        export OBSERVER_OPENCODE_LOG="$TESTS/empty.log"
        export OBSERVER_REPO_ROOT="${TEST_REPO_ROOT:-$TESTS/fake-repo}"
        export OBSERVER_BACKUP_ENABLED=0 OBSERVER_ADMISSION_ENABLED=0
        export PATH="$sd/bin:$PATH"
        for kv in "$@"; do export "$kv"; done
        cd /
        bash "$MANAGER" --once >/dev/null 2>&1
    )
}
tripwire_clean() { # tripwire_clean <name> <statedir> <worktree-root> <agent>
    if [ ! -e "$2/mutations.txt" ]; then printf 'PASS %s zero mutation capability\n' "$1"; PASS=$((PASS+1));
    else printf 'FAIL %s destructive command reached crosslink: %s\n' "$1" "$(cat "$2/mutations.txt")"; FAIL=$((FAIL+1)); fi
    if [ -d "$3/.worktrees/$4" ]; then printf 'PASS %s worktree untouched\n' "$1"; PASS=$((PASS+1));
    else printf 'FAIL %s worktree mutated\n' "$1"; FAIL=$((FAIL+1)); fi
}
# (a) NO mode configuration at all -> observe-only (the historical safe
# default is now enforced, not incidental)
sd="$TESTS/t21a"; root="$TESTS/t21a-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-obsdef
export TEST_REPO_ROOT="$root"
make_tripwire "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-obsdef DONE-CONFIRMED builder EXITED DONE
run_tripwire_cycle "$sd" "$fx"
check "T21a summary carries resolved mode" '"mode":"observe"' "$sd/events.jsonl"
check "T21a intent recorded not executed" "cleanup-dry-run" "$sd/events.jsonl"
check "T21a startup record present" '"event":"startup","mode":"observe"' "$sd/events.jsonl"
check "T21a state record carries mode" '"mode": *"observe"\|"mode":"observe"' "$sd/manager-state.json"
tripwire_clean "T21a" "$sd" "$root" "zzz-lc-obsdef"
# (b) garbage mode value -> observe (never lethal via unrecognized input)
sd="$TESTS/t21b"; root="$TESTS/t21b-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-obsgarbage
export TEST_REPO_ROOT="$root"
make_tripwire "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-obsgarbage DONE-CONFIRMED builder EXITED DONE
run_tripwire_cycle "$sd" "$fx" "OBSERVER_MODE=i-am-absolutely-act-trust-me"
check "T21b garbage mode resolved observe" '"mode":"observe"' "$sd/events.jsonl"
tripwire_clean "T21b" "$sd" "$root" "zzz-lc-obsgarbage"
# (c) legacy alias wins: OBSERVER_DRY_RUN forces observe over MODE=act
sd="$TESTS/t21c"; root="$TESTS/t21c-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-obsalias
export TEST_REPO_ROOT="$root"
make_tripwire "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-obsalias DONE-CONFIRMED builder EXITED DONE
run_tripwire_cycle "$sd" "$fx" "OBSERVER_MODE=act" "OBSERVER_ORCHESTRATOR_ID=obs-test" \
    "OBSERVER_DRY_RUN=1"
check "T21c alias forces observe over act" '"mode":"observe"' "$sd/events.jsonl"
tripwire_clean "T21c" "$sd" "$root" "zzz-lc-obsalias"
# (d) act mode arms real behavior (tripwire fires; non-vacuous proof)
sd="$TESTS/t21d"; root="$TESTS/t21d-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-actreal
export TEST_REPO_ROOT="$root"
make_tripwire "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-actreal DONE-CONFIRMED builder EXITED DONE
run_tripwire_cycle "$sd" "$fx" "OBSERVER_MODE=act" \
    "OBSERVER_ORCHESTRATOR_ID=$TEST_ORCH_ID"
check "T21d summary carries act" '"mode":"act"' "$sd/events.jsonl"
if [ -e "$sd/mutations.txt" ] && grep -q "cleanup" "$sd/mutations.txt"; then
    printf 'PASS T21d act mode executes real mutations\n'; PASS=$((PASS+1))
else
    printf 'FAIL T21d act mode did not reach crosslink\n'; FAIL=$((FAIL+1))
fi
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T22 cross-owner destructive action DOWNGRADED to notification (C2)"
# The worktree belongs to a DIFFERENT orchestrator domain: even in act mode
# with full identity, stop/cleanup must never fire - only a notification
# naming the actual owner.
sd="$TESTS/t22"; root="$TESTS/t22-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-crossown
printf '%s\n' "sibling-orchestrator-domain" \
    > "$root/.worktrees/zzz-lc-crossown/.owner-orchestrator"
export TEST_REPO_ROOT="$root"
make_tripwire "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-crossown DONE-CONFIRMED builder EXITED DONE
run_tripwire_cycle "$sd" "$fx" "OBSERVER_MODE=act" \
    "OBSERVER_ORCHESTRATOR_ID=$TEST_ORCH_ID"
check "T22 authority check recorded mismatch" '"reason":"owner-mismatch"' "$sd/events.jsonl"
check "T22 downgrade names would-be action" '"event":"authority-downgraded","agent":"zzz-lc-crossown","would_be_action":"kickoff_cleanup"' "$sd/events.jsonl"
check "T22 actual owner named in event" '"owner_orchestrator":"sibling-orchestrator-domain"' "$sd/events.jsonl"
if grep -q "AUTHORITY.*sibling-orchestrator-domain" "$sd/comments.txt" 2>/dev/null; then
    printf 'PASS T22 notification names actual owner\n'; PASS=$((PASS+1))
else
    printf 'FAIL T22 downgrade notification missing owner name\n'; FAIL=$((FAIL+1))
fi
tripwire_clean "T22" "$sd" "$root" "zzz-lc-crossown"
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T23 unknown-owner destructive action DOWNGRADED (C2 fail-closed)"
# Missing stamp -> owner unknown -> downgraded REGARDLESS of mode. This is
# the default state of every pre-stamp fleet agent.
sd="$TESTS/t23"; root="$TESTS/t23-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-nostamp
rm -f "$root/.worktrees/zzz-lc-nostamp/.owner-orchestrator"
export TEST_REPO_ROOT="$root"
make_tripwire "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-nostamp DONE-CONFIRMED builder EXITED DONE
run_tripwire_cycle "$sd" "$fx" "OBSERVER_MODE=act" \
    "OBSERVER_ORCHESTRATOR_ID=$TEST_ORCH_ID"
check "T23 authority check owner-unknown" '"reason":"owner-unknown"' "$sd/events.jsonl"
check "T23 downgrade event recorded" '"event":"authority-downgraded","agent":"zzz-lc-nostamp"' "$sd/events.jsonl"
check "T23 owner reported as unknown" '"owner_orchestrator":"unknown"' "$sd/events.jsonl"
tripwire_clean "T23" "$sd" "$root" "zzz-lc-nostamp"
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T24 MODE=act without OBSERVER_ORCHESTRATOR_ID fatals loudly (C2)"
sd="$TESTS/t24"; rm -rf "$sd"; mkdir -p "$sd"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-noid RUNNING-ALIVE builder ALIVE RUNNING
rc=0
(
    export OBSERVER_MODE=act OBSERVER_STATE_DIR="$sd" \
        OBSERVER_INPUT_JSON="$fx" \
        OBSERVER_OPENCODE_LOG="$TESTS/empty.log" \
        OBSERVER_REPO_ROOT="$TESTS/fake-repo" \
        OBSERVER_BACKUP_ENABLED=0
    unset OBSERVER_ORCHESTRATOR_ID OBSERVER_DRY_RUN
    cd /
    bash "$MANAGER" --once
) >/dev/null 2>"$sd/stderr.txt" || rc=$?
if [ "$rc" -ne 0 ]; then printf 'PASS T24 act-without-id refused (rc=%s)\n' "$rc"; PASS=$((PASS+1));
else printf 'FAIL T24 act mode started without an orchestrator identity\n'; FAIL=$((FAIL+1)); fi
check "T24 fatal event recorded"       '"kind":"act-mode-requires-orchestrator-id"' "$sd/events.jsonl"
if grep -q "FATAL" "$sd/stderr.txt" 2>/dev/null; then printf 'PASS T24 loud stderr fatal\n'; PASS=$((PASS+1));
else printf 'FAIL T24 no loud stderr fatal\n'; FAIL=$((FAIL+1)); fi

# ---------------------------------------------------------------------------
note "T25 pane-hash silence alone NEVER terminates (C3: #473 misfire class)"
# Fresh-commit worktree: NO authoritative non-progress signal exists, so
# repeated LIKELY-FROZEN confirmation must hold the gate forever.
sd="$TESTS/t25"; root="$TESTS/t25-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_deliverable_wt "$root" zzz-lc-panealone
export TEST_REPO_ROOT="$root"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-panealone LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx"
run_cycle "$sd" "$fx"
run_cycle "$sd" "$fx"
check "T25 gate held events recorded" '"event":"termination-gate-held"' "$sd/events.jsonl"
N=$(grep -c "frozen-termination" "$sd/events.jsonl")
test "$N" -eq 0 && { printf 'PASS T25 repeated pane-silence never terminates\n'; PASS=$((PASS+1));
} || { printf 'FAIL T25 terminated on pane silence alone (%s records)\n' "$N"; FAIL=$((FAIL+1)); }
tripwire_clean "T25" "$sd" "$root" "zzz-lc-panealone"
# (b) advancing log VETOES even when a P1 signal exists: stale commit +
# live attributed tail whose last line changes between evaluations.
sd="$TESTS/t25b"; root="$TESTS/t25b-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_stale_wt "$root" zzz-lc-logveto
export TEST_REPO_ROOT="$root"
cat > "$sd/agent.log" <<'LOGEOF'
timestamp=2026-08-24T07:00:00.000Z level=INFO run=abc message=tracking cwd=/tmp/opencode/observer-tests/t25b-root/.worktrees/zzz-lc-logveto session.id=ses_logveto001
timestamp=2026-08-24T07:00:01.000Z level=INFO run=abc message="llm runtime selected" llm.runtime=ai-sdk llm.provider=opencode-go llm.model=test-model-free session.id=ses_logveto001
LOGEOF
export TEST_OPENCODE_LOG="$sd/agent.log"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-logveto LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx"          # first sighting of the tail: undecidable -> held
printf 'timestamp=2026-08-24T07:03:00.000Z level=INFO run=abc message="agent-loop step 42 still working" session.id=ses_logveto001\n' >> "$sd/agent.log"
run_cycle "$sd" "$fx"          # tail changed: fresh activity VETOES despite P1
check "T25b gate held on live tail" '"event":"termination-gate-held"' "$sd/events.jsonl"
N=$(grep -c "frozen-termination" "$sd/events.jsonl")
test "$N" -eq 0 && { printf 'PASS T25b advancing log vetoes termination\n'; PASS=$((PASS+1));
} || { printf 'FAIL T25b killed a working agent (%s records)\n' "$N"; FAIL=$((FAIL+1)); }
unset TEST_OPENCODE_LOG
unset TEST_REPO_ROOT

# ---------------------------------------------------------------------------
note "T26 convergence-kills: pane-frozen + P1 + quiet log terminates (C3)"
sd="$TESTS/t26"; root="$TESTS/t26-root"; rm -rf "$sd" "$root"; mkdir -p "$sd"
make_stale_wt "$root" zzz-lc-converge
export TEST_REPO_ROOT="$root"
cat > "$sd/agent.log" <<'LOGEOF'
timestamp=2026-08-24T07:00:00.000Z level=INFO run=abc message=tracking cwd=/tmp/opencode/observer-tests/t26-root/.worktrees/zzz-lc-converge session.id=ses_converge001
timestamp=2026-08-24T07:00:01.000Z level=INFO run=abc message="llm runtime selected" llm.runtime=ai-sdk llm.provider=opencode-go llm.model=test-model-free session.id=ses_converge001
LOGEOF
export TEST_OPENCODE_LOG="$sd/agent.log"
fx="$sd/fix.json"; fixture "$fx" zzz-lc-converge LIKELY-FROZEN builder ALIVE RUNNING
run_cycle "$sd" "$fx"          # baseline: tail sighted, held
check "T26 first evaluation held" '"event":"termination-gate-held"' "$sd/events.jsonl"
check_absent "T26 not yet terminated" "frozen-termination" "$sd/events.jsonl"
run_cycle "$sd" "$fx"          # same tail + stale commit -> converges
check "T26 converged termination fired" "frozen-termination" "$sd/events.jsonl"
check "T26 commit-stale signal cited" "commit-stale" "$sd/events.jsonl"
unset TEST_OPENCODE_LOG
unset TEST_REPO_ROOT

printf '\nRESULT: %d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
