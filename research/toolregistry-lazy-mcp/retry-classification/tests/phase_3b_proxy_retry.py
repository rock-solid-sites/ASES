#!/usr/bin/env python
"""Phase: Test 3B (supplementary) -- backend killed mid-call: the MODIFIED
proxy's OWN respawn-retry must still fire for a genuine connection failure.

Test 3 kills the PROXY process (ToolRegistry's reconnect layer).  This
supplementary check kills the BACKEND process mid-call instead, which
exercises the modified proxy's internal ``BackendClient.call`` respawn
path (Delta 1 leaves it unchanged for non-schema failures): the proxy's
client should see a real connection failure (MCPError(-32000, 'Connection
closed'), NOT the schema-validation RuntimeError), close the dead session,
respawn the backend, retry once, and succeed.

Expected:
  * backend_spawn_count = 2 (be-1 killed, be-2 respawned by the proxy),
    proxy_processes = 2 (registration temp + one persistent),
    reconnect_fired = False (ToolRegistry never saw a failure -- the proxy
    recovered internally).
  * one backend_call_failed (attempt=1 respawning) + one
    backend_call_retry_succeeded in the proxy log.
  * final caller-visible outcome: success '5.0' (backend conforming).
  * no backend_schema_validation_failed (classifier did not swallow it).
"""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_retry as common  # noqa: E402
from common_retry import (  # noqa: E402
    CLASSIFIED_PROXY,
    HERE,
    LOGS_DIR,
    events,
    first_event,
    hlog,
    make_transport,
    now_ms,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-3b-proxy-retry"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
BACKEND_PID_FILE = LOGS_DIR / f"{PHASE}-backend.pid"
MANIFEST = HERE / "manifest.json"


def wait_and_kill_backend() -> int | None:
    """Wait for the backend to spawn (pid file) then SIGKILL it mid-call."""
    deadline = time.time() + 60.0
    while time.time() < deadline:
        p = Path(BACKEND_PID_FILE)
        if p.exists():
            try:
                pid = int(p.read_text(encoding="utf-8").strip())
            except (ValueError, OSError):
                pid = None
            if pid is not None:
                try:
                    os.kill(pid, 0)
                    hlog(f"KILL_BACKEND killing_backend pid={pid}")
                    os.kill(pid, signal.SIGKILL)
                    return pid
                except ProcessLookupError:
                    pass
        time.sleep(0.05)
    hlog("KILL_BACKEND backend_pid=NOT_FOUND (timeout waiting for pid file)")
    return None


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=MODIFIED({CLASSIFIED_PROXY.name}) "
        f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=conforming "
        f"action=kill_backend_mid_call"
    )
    for p in (PROXY_LOG, BACKEND_PID_FILE):
        if p.exists():
            p.unlink()

    registry = ToolRegistry(name="test3b")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=CLASSIFIED_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="conforming",
        backend_pid_file=str(BACKEND_PID_FILE),
    )

    hlog("TEST3B_BEGIN register")
    t0 = now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = now_ms()
    hlog(f"TEST3B_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    holder: dict[str, object] = {}

    def do_invoke() -> None:
        inv_start = now_ms()
        outcome = registry.invoke("add", {"a": 2, "b": 3})
        holder["outcome"] = outcome
        holder["delta_ms"] = now_ms() - inv_start

    hlog("TEST3B_BEGIN call (thread)")
    t = threading.Thread(target=do_invoke, name="test3b-invoke")
    t.start()
    killed_pid = wait_and_kill_backend()
    t.join(timeout=120)
    if t.is_alive():
        hlog("TEST3B_INVOKE_THREAD_STILL_RUNNING_AFTER_120S")
        registry.close()
        sys.exit(2)
    hlog(f"TEST3B_INVOKE_THREAD_DONE delta_ms={holder.get('delta_ms')}")

    outcome = holder.get("outcome")
    if outcome is not None:
        if hasattr(outcome, "message"):
            hlog(f"TEST3B_OUTCOME message_verbatim={outcome.message!r}")
        elif hasattr(outcome, "result"):
            hlog(f"TEST3B_OUTCOME result={outcome.result!r}")
    else:
        hlog("TEST3B_OUTCOME none (invoke returned None)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    failures = events(proxy_lines, "backend_call_failed")
    retry_ok = events(proxy_lines, "backend_call_retry_succeeded")
    schema_failures = events(proxy_lines, "backend_schema_validation_failed")
    pids = proxy_pids(proxy_lines)
    persistent_proxies = max(0, len(pids) - 1)
    reconnect_fired = len(pids) > 2

    hlog(
        f"TEST3B_SPAWN_COUNTS backend_spawn_count={len(spawns)} "
        f"backend_call_failed_count={len(failures)} retry_succeeded_count={len(retry_ok)} "
        f"backend_schema_validation_failed_count={len(schema_failures)} "
        f"proxy_processes={len(pids)} persistent_proxies={persistent_proxies} "
        f"reconnect_fired={reconnect_fired} killed_backend_pid={killed_pid} proxy_pids={pids}"
    )
    for epoch, msg in failures:
        hlog(f"TEST3B_FAILURE_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in retry_ok:
        hlog(f"TEST3B_RETRY_OK_EVENT epoch={epoch} msg={msg}")

    success = outcome is not None and hasattr(outcome, "result") and str(outcome.result) == "5.0"
    proxy_retried = len(failures) >= 1 and len(retry_ok) >= 1
    test3b_ok = (
        success
        and proxy_retried
        and not reconnect_fired
        and len(schema_failures) == 0
        and killed_pid is not None
    )
    hlog(
        f"TEST3B_RESULT pass={test3b_ok} "
        f"(expected: proxy-internal retry fired + success 5.0, no reconnect, no misclassification; "
        f"observed: proxy_retried={proxy_retried} success={success} reconnect={reconnect_fired} "
        f"schema_misclassified={len(schema_failures) > 0})"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} test3b_proxy_retry_pass={test3b_ok}")
    sys.exit(0 if test3b_ok else 1)


if __name__ == "__main__":
    main()
