#!/usr/bin/env bash
# Arm an automatic retry of the Phase 2 verification.
#
# WHY THIS EXISTS. Both designated verifiers are blocked by an account-level
# free-tier quota (rate limit, nextDelay ~8.5-8.7M ms from 21:34-21:39Z on
# 2026-07-27, clearing ~23:58Z). Step 2 and Step 3 of the verification are
# outstanding. This script polls the DESIGNATED verifier until it answers, then
# dispatches the already-committed VERIFY-BRIEF-2.md, which appends to
# verification.md and skips the completed Step 1.
#
# It introduces NO new model and makes NO substitution: it only retries
# opencode/muse-spark-1.3-contributor-free, which the operator designated and
# which already produced Step 1. Preserving the original verifier family matters:
# it keeps Step 1 and Steps 2-3 on the same independent lineage.
#
# Safety: bounded attempts, a single dispatch, no repo mutation outside
# results/ and verification.md, and every decision logged.
set -u
W=/home/claude-code/projects/ASES/.worktrees/jev-phase1/research/jev-bounded-judgment/phase2
LOG=$W/results/autoretry.log
MODEL=opencode/muse-spark-1.3-contributor-free
MAX_POLLS=${MAX_POLLS:-24}
INTERVAL=${INTERVAL:-600}
BASE_SIZE=$(wc -c < "$W/verification.md" 2>/dev/null || echo 0)

log(){ echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"; }

log "=== autoretry armed. model=$MODEL base_verification_bytes=$BASE_SIZE max_polls=$MAX_POLLS interval=${INTERVAL}s ==="

dispatched=0
for i in $(seq 1 "$MAX_POLLS"); do
  probe=$(cd "$W" && timeout 200 opencode run --model "$MODEL" --format json \
          "Reply with exactly: READY" 2>/dev/null | python3 -c "
import sys,json
t=[]
for l in sys.stdin:
    l=l.strip()
    if not l: continue
    try: x=json.loads(l)
    except Exception: continue
    if x.get('type')=='text':
        p=x.get('part') or {}
        if p.get('text'): t.append(p['text'])
print('ALIVE' if t else 'BLOCKED')" 2>/dev/null)
  log "poll $i/$MAX_POLLS probe=$probe"

  if [ "$probe" = "ALIVE" ]; then
    log "verifier is live; dispatching VERIFY-BRIEF-2.md"
    (cd "$W" && timeout 3000 opencode run --agent build --model "$MODEL" \
        --format json "$(cat VERIFY-BRIEF-2.md)" \
        > results/verify-muse-autoretry.jsonl 2> results/verify-muse-autoretry.err \
        < /dev/null)
    log "dispatch returned rc=$?"
    dispatched=1
    NEW=$(wc -c < "$W/verification.md" 2>/dev/null || echo 0)
    log "verification.md bytes: $BASE_SIZE -> $NEW"
    if [ "$NEW" -gt "$BASE_SIZE" ]; then
      log "RESULT: verification artifact GREW by $((NEW-BASE_SIZE)) bytes; Step 2 checkpoint(s) landed"
    else
      log "RESULT: artifact did NOT grow. The turn ended before a checkpoint, as in prior runs."
    fi
    break
  fi
  sleep "$INTERVAL"
done

[ "$dispatched" -eq 0 ] && log "=== exhausted $MAX_POLLS polls without the verifier coming back ==="
log "=== autoretry finished ==="
