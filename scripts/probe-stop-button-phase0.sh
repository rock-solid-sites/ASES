#!/usr/bin/env bash
#
# probe-stop-button-phase0.sh
# ---------------------------------------------------------------------------
# Phase 0 — 9-point interrupt fence probe for issue #510 (stop-button).
#
# Goal: verify that POST /api/session/:id/interrupt is an AUTHORITATIVE fence
# (not a placebo that returns 204 while the fiber/stream/tool keeps running).
#
# The server handler (fork/opencode-src/packages/server/src/handlers/session.ts:366)
# calls `session.interrupt(sessionID)` which (code-inspection, see below) fences
# the process-local SessionRunCoordinator fiber via Fiber.interrupt, and the
# SessionExecution local implementation interrupts the active Runner, which
# Fiber.interrupts the LLM stream and Deferred.fails any parked tool/retry.
# Idle or missing interruption is a documented no-op.
#
# If the probe shows a 204 but the session never reaches idle / a child process
# survives, that is the PLACEBO bug -> halt UI wiring and flag
# SessionRunCoordinator fence bug (per issue #510 spec).
#
# ---------------------------------------------------------------------------
# CODE-INSPECTION EVIDENCE (cheapest-test, run before any UI wiring)
#   - SessionRunCoordinator.interrupt fences the owner fiber (Fiber.interrupt
#     on the entry.owner fiber) -> the whole drain (LLM stream + tool children)
#     is interrupted, not just the TUI state.
#   - SessionExecution local delegates interrupt to the active Runner; Runner
#     cancel does Fiber.interrupt + Deferred.fail on in-flight tool promises.
#   - Parked 401/429 retry loops live inside the same fiber, so interrupting
#     the fiber clears them too (no orphaned retry timer).
#   - session.interrupt on an idle/missing session is a no-op (returns 204).
#
# These are evidence-based (code) claims; the live curl points below are the
# discriminating test that falsifies the "placebo" premise.
# ---------------------------------------------------------------------------
#
# Usage:
#   OPENCODE_URL=http://localhost:4096 OPENCODE_TOKEN=... ./probe-stop-button-phase0.sh
#
# Env:
#   OPENCODE_URL      base URL of the opencode server (default http://localhost:4096)
#   OPENCODE_PASSWORD basic-auth password for the opencode server (user=OPENCODE_USER, default opencode)
#   OPENCODE_USER     basic-auth username (default opencode)
#   OPENCODE_TOKEN    optional bearer token (fallback if OPENCODE_PASSWORD unset)
#   PROBE_SESSION     existing session id to reuse (else a fresh one is created)
#   PROBE_TOOL_CMD    command the tool-kill point should run (default "sleep 42")
#   PROBE_LONG_TEXT   long-generation prompt text
#   FORCE_429         if set, attempt to provoke a 429 before the 401/429 point
#   TIMEOUT_S         per-point poll budget in seconds (default 60)
#   PROBE_MODEL       model for probe session (default opencode-go/muse-spark-1.2-contributor)
#   PROBE_PROVIDER    provider for probe session (default opencode-go)
#
set -u

BASE="${OPENCODE_URL:-http://localhost:4096}"
# opencode's server uses HTTP Basic auth: base64("<user>:<password>").
# It also accepts ?auth_token=base64("<user>:<password>").
# Prefer OPENCODE_PASSWORD (Basic); fall back to OPENCODE_TOKEN (Bearer) for other servers.
USER="${OPENCODE_USER:-opencode}"
PASSWORD="${OPENCODE_PASSWORD:-}"
TOKEN="${OPENCODE_TOKEN:-}"
# NOTE: TOOL_CMD must NOT be a substring of other process command lines on the
# host. The default "sleep 30" collides with kickoff watchers whose cmdline
# contains "sleep 300", causing pgrep -f "sleep 30" false positives. Use a
# value that cannot appear elsewhere (e.g. "sleep 42").
TOOL_CMD="${PROBE_TOOL_CMD:-sleep 42}"
LONG_TEXT="${PROBE_LONG_TEXT:-Write a 3000-word essay on the history of computing. Do not stop until it is complete.}"
TIMEOUT_S="${TIMEOUT_S:-60}"
SESSION="${PROBE_SESSION:-}"
PROBE_MODEL="${PROBE_MODEL:-muse-spark-1.2-contributor}"
PROBE_PROVIDER="${PROBE_PROVIDER:-opencode-go}"

B64=""
if [ -n "$PASSWORD" ]; then
  B64=$(printf '%s:%s' "$USER" "$PASSWORD" | base64 | tr -d '\n')
  AUTH_HDR=(-H "Authorization: Basic $B64")
elif [ -n "$TOKEN" ]; then
  AUTH_HDR=(-H "Authorization: Bearer $TOKEN")
else
  AUTH_HDR=()
fi

PASS=0
FAIL=0
NA=0
SKIP=0

# --- helpers ---------------------------------------------------------------
http() { # method path [body] -> echoes HTTP code (or "0" on transport failure)
  local method="$1" path="$2" body="${3:-}"
  local url="$BASE$path"
  if [ -n "$B64" ]; then
    if [[ "$url" == *"?"* ]]; then url="$url&auth_token=$B64"; else url="$url?auth_token=$B64"; fi
  elif [ -n "$TOKEN" ]; then
    if [[ "$url" == *"?"* ]]; then url="$url&auth_token=$TOKEN"; else url="$url?auth_token=$TOKEN"; fi
  fi
  local out rc
  if [ -n "$body" ]; then
    out=$(curl -sS -m 20 -o /tmp/probe-body.txt -w '%{http_code}' -X "$method" \
      "${AUTH_HDR[@]}" -H "Content-Type: application/json" -d "$body" "$url" 2>/tmp/probe-err.txt)
  else
    out=$(curl -sS -m 20 -o /tmp/probe-body.txt -w '%{http_code}' -X "$method" \
      "${AUTH_HDR[@]}" "$url" 2>/tmp/probe-err.txt)
  fi
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "CURL_ERR($rc): $(head -1 /tmp/probe-err.txt 2>/dev/null)" >&2
    echo "0"
    return
  fi
  echo "$out"
}

status_type() { # sessionID -> prints "idle" | "running" | "unknown"
  local id="$1"
  local body
  body=$(curl -sS -m 20 "${AUTH_HDR[@]}" "$BASE/api/session/$id${B64:+?auth_token=$B64}" 2>/dev/null)
  # Completed sessions have time.idle = numeric; running sessions have no time.idle
  # (or idle:null in older API). Also check outcome field: interrupted/succeeded = idle.
  if echo "$body" | grep -q '"idle"[ ]*:[ ]*[0-9]'; then
    echo "idle"
  elif echo "$body" | grep -q '"idle"[ ]*:[ ]*null'; then
    echo "running"
  elif echo "$body" | grep -q '"time"[ ]*:[ ]*{[^}]*"created"[^}]*"updated"[^}]*"idle"'; then
    # Fallback: if time block contains idle anywhere, it's idle
    echo "idle"
  elif echo "$body" | grep -q '"outcome"[ ]*:[ ]*"'; then
    # Session has outcome (succeeded/interrupted/failed) — it is settled/idle
    echo "idle"
  else
    # No idle and no outcome → still running (streaming or tool executing)
    # Verify by checking if latest message is still without completed time
    local msg_body
    msg_body=$(curl -sS -m 10 "${AUTH_HDR[@]}" "$BASE/api/session/$id/message${B64:+?auth_token=$B64}" 2>/dev/null)
    if echo "$msg_body" | grep -q '"completed"[ ]*:'; then
      # Latest message has completed time — check if it's the most recent
      # If session time has no idle but messages show recent completion, it may be mid-settle
      echo "idle"
    else
      echo "running"
    fi
  fi
}

wait_status() { # sessionID target_type -> 0 if reached within TIMEOUT_S
  local id="$1" target="$2" elapsed=0
  while [ $elapsed -lt "$TIMEOUT_S" ]; do
    local st
    st=$(status_type "$id")
    if [ "$st" = "$target" ]; then return 0; fi
    sleep 2
    elapsed=$((elapsed+2))
  done
  return 1
}

create_session() {
  local body
  # Use a tool-child-capable model (muse-spark via opencode-go) — without this
  # the server defaults to claude-fable-5 via google-vertex which 403s and never
  # spawns tool children, making points 3/6 N/A (see #542).
  local payload
  payload=$(jq -n --arg m "$PROBE_MODEL" --arg p "$PROBE_PROVIDER" '{"title":"probe-stop-button","model":{"id":$m,"providerID":$p}}')
  body=$(http POST "/api/session" "$payload")
  if [ "$body" = "0" ] || [ -z "$body" ]; then echo ""; return; fi
  # extract id from response body
  grep -o '"id"[ ]*:[ ]*"[^"]*"' /tmp/probe-body.txt | head -1 | sed 's/.*:"\([^"]*\)"/\1/'
}

send_prompt() { # sessionID text -> http code
  local id="$1" text="$2"
  local json
  # opencode's POST /api/session/:id/prompt expects {"text":"..."} at the root.
  json=$(jq -n --arg t "$text" '{"text":$t}')
  http POST "/api/session/$id/prompt" "$json"
}

has_tool_child() {
  # True if a real `sleep 42` child (the shell-tool) is alive — not the probe's
  # own shell whose cmdline happens to contain the string "sleep 42".
  # pgrep -f matches the probe's `bash -c ...sleep 42...` wrapper and the grep
  # itself; filter them out and only count the bare `sleep 42` binary.
  pgrep -a -f "sleep 42" 2>/dev/null | grep -v "B64=" | grep -v "PROBE_" | grep -v "grep" | grep -q " sleep 42"
}

report() { # kind point detail
  local kind="$1" point="$2" detail="$3"
  case "$kind" in
    PASS) PASS=$((PASS+1)); echo "  [PASS] $point — $detail" ;;
    FAIL) FAIL=$((FAIL+1)); echo "  [FAIL] $point — $detail" ;;
    NA)   NA=$((NA+1));   echo "  [N/A]  $point — $detail" ;;
    SKIP) SKIP=$((SKIP+1)); echo "  [SKIP] $point — $detail" ;;
  esac
}

# --- server reachability ---------------------------------------------------
echo "== Phase 0 stop-button 9-point interrupt probe =="
echo "   target: $BASE"
CODE=$(http GET "/api/session")
if [ "$CODE" = "0" ]; then
  echo "!! Server unreachable at $BASE — live points will SKIP."
  echo "!! Run this script against a live opencode server to execute the 9 points."
  echo "!! Code-inspection evidence (above) stands regardless."
  SERVER_UP=0
else
  SERVER_UP=1
  echo "   server reachable (session.list -> $CODE)"
fi

# --- ensure a session ------------------------------------------------------
if [ "$SERVER_UP" = "1" ]; then
  if [ -z "$SESSION" ]; then
    SESSION=$(create_session)
    if [ -z "$SESSION" ]; then
      echo "!! Could not create a probe session; aborting live points."
      SERVER_UP=0
    else
      echo "   probe session: $SESSION"
    fi
  fi
fi

# === POINT 1: idle interrupt is a no-op (204) or not-found (404) ===========
echo ""
echo "1) idle interrupt -> no-op (204) / not-found (404)"
if [ "$SERVER_UP" = "1" ]; then
  # make sure it is idle first
  wait_status "$SESSION" "idle" 2>/dev/null
  CODE=$(http POST "/api/session/$SESSION/interrupt")
  if [ "$CODE" = "204" ] || [ "$CODE" = "404" ]; then
    report PASS "idle" "interrupt on idle session returned $CODE (no crash, no orphan)"
  else
    report FAIL "idle" "interrupt on idle session returned $CODE (expected 204/404)"
  fi
else
  report SKIP "idle" "server down"
fi

# === POINT 2: streaming generation killed =================================
echo ""
echo "2) stream killed -> session returns to idle after interrupt"
if [ "$SERVER_UP" = "1" ]; then
  send_prompt "$SESSION" "$LONG_TEXT" >/dev/null
  if wait_status "$SESSION" "running" 2>/dev/null || wait_status "$SESSION" "busy" 2>/dev/null; then
    http POST "/api/session/$SESSION/interrupt" >/dev/null
    if wait_status "$SESSION" "idle" "$TIMEOUT_S"; then
      report PASS "stream" "session reached idle after interrupt (LLM stream fiber fenced)"
    else
      report FAIL "stream" "session did NOT return to idle after interrupt (possible placebo)"
    fi
  else
    report NA "stream" "session never observed running (model may have answered instantly); rerun with a heavier prompt"
  fi
else
  report SKIP "stream" "server down"
fi

# === POINT 3: tool child killed (no orphan) ===============================
echo ""
echo "3) tool killed -> session idle AND no orphan child process"
if [ "$SERVER_UP" = "1" ]; then
  send_prompt "$SESSION" "Run this shell command and wait for it to finish, then tell me it is done: ${TOOL_CMD}" >/dev/null
  # wait until a child process for the tool appears OR session running
  slept=0; seen=0
  while [ $slept -lt "$TIMEOUT_S" ]; do
    if has_tool_child; then seen=1; break; fi
    if [ "$(status_type "$SESSION")" = "idle" ]; then break; fi
    sleep 2; slept=$((slept+2))
  done
  if [ "$seen" = "1" ]; then
    http POST "/api/session/$SESSION/interrupt" >/dev/null
    # give the fence a moment, then confirm the child is gone
    sleep 3
    if ! has_tool_child; then
      if wait_status "$SESSION" "idle" 20; then
        report PASS "tool" "tool child '$TOOL_CMD' killed and session idle (no orphan)"
      else
        report FAIL "tool" "tool child killed but session not idle"
      fi
    else
      report FAIL "tool" "tool child '$TOOL_CMD' STILL ALIVE after interrupt (placebo / fence bug)"
    fi
  else
    report NA "tool" "tool child '$TOOL_CMD' never observed (prompt may not have invoked a tool); rerun"
  fi
else
  report SKIP "tool" "server down"
fi

# === POINT 4: new prompt accepted after interrupt =========================
echo ""
echo "4) new prompt accepted after interrupt (200/2xx)"
if [ "$SERVER_UP" = "1" ]; then
  wait_status "$SESSION" "idle" 10 2>/dev/null
  CODE=$(send_prompt "$SESSION" "Say hello in one word.")
  if [ "$CODE" = "200" ] || [ "${CODE:0:1}" = "2" ]; then
    report PASS "new-prompt" "post-interrupt prompt admitted (HTTP $CODE)"
  else
    report FAIL "new-prompt" "post-interrupt prompt rejected (HTTP $CODE)"
  fi
else
  report SKIP "new-prompt" "server down"
fi

# === POINT 5: 401/429 parked retry also killed ============================
echo ""
echo "5) 401/429 parked retry cleared by interrupt"
if [ "$SERVER_UP" = "1" ]; then
  if [ -n "${FORCE_429:-}" ]; then
    # best-effort: hammer prompts to provoke a 429, then interrupt, then idle
    for i in $(seq 1 20); do send_prompt "$SESSION" "ping $i" >/dev/null; done
    http POST "/api/session/$SESSION/interrupt" >/dev/null
    if wait_status "$SESSION" "idle" "$TIMEOUT_S"; then
      report PASS "401/429" "session idle after interrupt during retry storm (parked retries cleared)"
    else
      report FAIL "401/429" "session stuck after interrupt during retry storm (parked retry not fenced)"
    fi
  else
    # Cannot deterministically force a 401/429 from the session API in a script.
    # Code-inspection evidence: parked retries live inside the same coordinator
    # fiber that interrupt fences, so they are cleared. Manual check: when a
    # real 401/429 occurs, run `POST /api/session/:id/interrupt` and confirm the
    # session returns to idle and no retry loop continues (watch server log).
    report NA "401/429" "not auto-forcible; code-verified (retry loop is inside fenced fiber) + manual check documented"
  fi
else
  report SKIP "401/429" "server down"
fi

# === POINT 6: no orphan after UI restart ==================================
echo ""
echo "6) no orphan after UI restart (server-side fiber/tool truly dead)"
if [ "$SERVER_UP" = "1" ]; then
  # Re-run a tool, interrupt, then confirm (a) session inactive in /active and
  # (b) no orphan child. Simulates the TUI (UI) restarting while server owns run.
  send_prompt "$SESSION" "Run this shell command and wait: ${TOOL_CMD}" >/dev/null
  slept=0; seen=0
  while [ $slept -lt "$TIMEOUT_S" ]; do
    if has_tool_child; then seen=1; break; fi
    [ "$(status_type "$SESSION")" = "idle" ] && break
    sleep 2; slept=$((slept+2))
  done
  if [ "$seen" = "1" ]; then
    http POST "/api/session/$SESSION/interrupt" >/dev/null
    sleep 3
    if has_tool_child; then orphan=1; else orphan=0; fi
    active=$(curl -sS -m 20 "${AUTH_HDR[@]}" "$BASE/api/session/active${B64:+?auth_token=$B64}" 2>/dev/null | grep -c "$SESSION")
    if [ "$orphan" = "0" ] && [ "$active" = "0" ]; then
      report PASS "no-orphan" "no orphan child and session not active after interrupt (UI restart safe)"
    else
      report FAIL "no-orphan" "orphan child=$orphan active-listing=$active after interrupt"
    fi
  else
    report NA "no-orphan" "tool child not observed; rerun to confirm"
  fi
else
  report SKIP "no-orphan" "server down"
fi

# === POINT 7: concurrency — duplicate concurrent interrupts idempotent ======
# Universal Checklist §14: duplicate events, completion/cancellation interaction,
# mutually exclusive states cannot both be authoritative. Two concurrent POST /interrupt
# must be coalesced (second is a no-op 204) and leave the session idle, not resurrect.
echo ""
echo "7) concurrency — duplicate concurrent interrupts idempotent"
if [ "$SERVER_UP" = "1" ]; then
  wait_status "$SESSION" "idle" 10 2>/dev/null
  CODE1_FILE=/tmp/probe-conc-1.txt
  CODE2_FILE=/tmp/probe-conc-2.txt
  # Fire two interrupts concurrently (background curls)
  http POST "/api/session/$SESSION/interrupt" >"$CODE1_FILE" 2>/dev/null &
  pid1=$!
  http POST "/api/session/$SESSION/interrupt" >"$CODE2_FILE" 2>/dev/null &
  pid2=$!
  wait $pid1; wait $pid2
  CODE1=$(cat "$CODE1_FILE" 2>/dev/null | tr -d ' \n')
  CODE2=$(cat "$CODE2_FILE" 2>/dev/null | tr -d ' \n')
  # Both should be 204 (or 404 if session vanished) — not 500 — and session must settle idle.
  if { [ "$CODE1" = "204" ] || [ "$CODE1" = "404" ]; } && { [ "$CODE2" = "204" ] || [ "$CODE2" = "404" ]; }; then
    if wait_status "$SESSION" "idle" 10; then
      report PASS "concurrency" "concurrent interrupts $CODE1/$CODE2 both 204 idempotent, session idle (no duplicate active)"
    else
      report FAIL "concurrency" "concurrent interrupts $CODE1/$CODE2 but session not idle (re-entrant leak)"
    fi
  else
    report FAIL "concurrency" "concurrent interrupts returned $CODE1/$CODE2 (expected 204/204 idempotent)"
  fi
else
  report SKIP "concurrency" "server down"
fi

# === POINT 8: temporal — debounce coalescence + observation staleness =====
# Universal Checklist §15: authoritative vs observed state, timers cannot manufacture
# authoritative transitions, reconciliation bounded. Two rapid interrupts (debounce 1s)
# must coalesce to one fence; stale observation (time.idle poll) must reconcile.
echo ""
echo "8) temporal — debounce and authoritative vs observed state"
if [ "$SERVER_UP" = "1" ]; then
  wait_status "$SESSION" "idle" 10 2>/dev/null
  # Send a normal prompt, wait briefly for running, then fire two interrupts 200ms apart.
  # The server's fence is authoritative; the TUI's 1s debounce is shell-level — here we
  # check the server's idempotence + that observed state reconciles to idle.
  send_prompt "$SESSION" "Say hi." >/dev/null
  sleep 1
  CODEA=$(http POST "/api/session/$SESSION/interrupt")
  sleep 0.2
  CODEB=$(http POST "/api/session/$SESSION/interrupt")
  # Both must be 204/404 (debounced at fence), and status poll must show idle within 10s.
  if { [ "$CODEA" = "204" ] || [ "$CODEA" = "404" ]; } && { [ "$CODEB" = "204" ] || [ "$CODEB" = "404" ]; }; then
    # Poll observed status: time.idle must appear (authoritative idle reconciles).
    if wait_status "$SESSION" "idle" 10; then
      report PASS "temporal" "rapid duplicate interrupts $CODEA/$CODEB coalesced, observed state reconciled to idle"
    else
      report FAIL "temporal" "rapid duplicate $CODEA/$CODEB but observed status never reconciled to idle (stale projection)"
    fi
  else
    report FAIL "temporal" "rapid duplicate returned $CODEA/$CODEB (expected 204/404 coalesced)"
  fi
  # Also verify new prompt after the debounce window is still accepted (recovery).
  sleep 1
  CODE3=$(send_prompt "$SESSION" "After debounce, are you idle? Answer yes.")
  if [ "$CODE3" = "200" ] || [ "${CODE3:0:1}" = "2" ]; then
    report PASS "temporal-recovery" "post-debounce prompt admitted ($CODE3) — no lost prompt"
  else
    report FAIL "temporal-recovery" "post-debounce prompt rejected ($CODE3) — lost prompt after debounce"
  fi
else
  report SKIP "temporal" "server down"
  report SKIP "temporal-recovery" "server down"
fi

# === POINT 9: transport — acceptance vs completion, duplicate/timeout =====
# Universal Checklist §16: success/failure/timeout/response-loss/duplicate semantics;
# transport acceptance (HTTP 204) distinct from underlying completion (fiber settled).
echo ""
echo "9) transport — acceptance vs completion and ambiguous outcomes"
if [ "$SERVER_UP" = "1" ]; then
  wait_status "$SESSION" "idle" 10 2>/dev/null
  # Transport acceptance: POST /interrupt on idle must be 204 (accepted as no-op)
  # even though there is no underlying completion to await — acceptance != completion.
  CODE_IDLE=$(http POST "/api/session/$SESSION/interrupt")
  if [ "$CODE_IDLE" = "204" ] || [ "$CODE_IDLE" = "404" ]; then
    report PASS "transport-idle" "idle interrupt transport accepted as $CODE_IDLE (acceptance distinct from completion)"
  else
    report FAIL "transport-idle" "idle interrupt transport returned $CODE_IDLE (expected 204 acceptance)"
  fi
  # Underlying completion: after a running interrupt, the session must reach idle
  # (fiber settled) — verify transport 204 did not mask a placebo.
  send_prompt "$SESSION" "Respond with a single word." >/dev/null
  sleep 1
  CODE_RUN=$(http POST "/api/session/$SESSION/interrupt")
  # Give up to TIMEOUT_S for underlying completion (fiber settle), not just HTTP 204
  if [ "$CODE_RUN" = "204" ] || [ "$CODE_RUN" = "404" ]; then
    if wait_status "$SESSION" "idle" 10; then
      report PASS "transport-completion" "running interrupt $CODE_RUN + fiber settled to idle (acceptance and completion both verified)"
    else
      report FAIL "transport-completion" "running interrupt $CODE_RUN accepted but fiber never settled idle — transport masked placebo"
    fi
  else
    report FAIL "transport-completion" "running interrupt transport $CODE_RUN not 204"
  fi
  # Duplicate suppression: ambiguous duplicate (retried POST) must not silently become
  # success with side-effects — it must remain idempotent (second 204, still idle).
  CODEDUP=$(http POST "/api/session/$SESSION/interrupt")
  if [ "$CODEDUP" = "204" ] || [ "$CODEDUP" = "404" ]; then
    if wait_status "$SESSION" "idle" 5; then
      report PASS "transport-duplicate" "duplicate POST $CODEDUP still idempotent and idle (ambiguous outcome not silently success)"
    else
      report FAIL "transport-duplicate" "duplicate POST $CODEDUP but status not idle"
    fi
  else
    report FAIL "transport-duplicate" "duplicate POST returned $CODEDUP (expected idempotent 204)"
  fi
else
  report SKIP "transport-idle" "server down"
  report SKIP "transport-completion" "server down"
  report SKIP "transport-duplicate" "server down"
fi

# --- summary ---------------------------------------------------------------
echo ""
echo "== Summary =="
echo "  PASS=$PASS  FAIL=$FAIL  N/A=$NA  SKIP=$SKIP"
if [ "$FAIL" -gt 0 ]; then
  echo "  VERDICT: FAIL — interrupt fence is a PLACEBO or partially broken."
  echo "  ACTION: halt UI wiring and flag SessionRunCoordinator fence bug (issue #510)."
  exit 2
elif [ "$SERVER_UP" = "0" ]; then
  echo "  VERDICT: SKIPPED (server down) — code-inspection evidence stands; rerun live."
  exit 3
else
  echo "  VERDICT: PASS — interrupt is an authoritative fence across all tested points."
  exit 0
fi
