#!/usr/bin/env python
"""Phase: Test 3 -- real connection failure still retries (MODIFIED proxy).

Using proxy_classified.py with a HEALTHY backend (schema_mode=conforming,
response_mode=conforming -- no drift), kill the persistent proxy process
mid-call (SIGKILL).  This is a genuine connection-level failure, NOT a
schema-validation failure.  ToolRegistry 0.15.0's reconnect-retry
(connection.py:106) must STILL fire: it closes the dead client, spawns a
fresh proxy, and the retried call succeeds.

Expected observations:
  * proxy_started count = 3 (registration temp + killed persistent + fresh
    post-reconnect persistent) -> reconnect_fired = YES.
  * backend spawn count = 2 (one for the killed proxy, one for the fresh
    proxy after reconnect).
  * final caller-visible outcome: SUCCESS (ToolCallResult with result 5.0).
  * the proxy's classifier must NOT have swallowed this failure (no
    backend_schema_validation_failed / no classified isError response).
"""

from __future__ import annotations

import os
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
    kill_proxy_mid_call,
    make_transport,
    now_ms,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-3-connection"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
PID_FILE = LOGS_DIR / f"{PHASE}-proxy.pid"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(
        f"proxy=MODIFIED({CLASSIFIED_PROXY.name}) "
        f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=conforming "
        f"action=kill_persistent_proxy_mid_call"
    )
    for p in (PROXY_LOG, PID_FILE):
        if p.exists():
            p.unlink()

    registry = ToolRegistry(name="test3")
    transport = make_transport(
        str(PROXY_LOG),
        proxy_path=CLASSIFIED_PROXY,
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="conforming",
        proxy_pid_file=str(PID_FILE),
    )

    hlog("TEST3_BEGIN register")
    t0 = now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = now_ms()
    hlog(f"TEST3_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    # ---- invoke in a background thread so we can kill the proxy mid-call ----
    holder: dict[str, object] = {}

    def do_invoke() -> None:
        inv_start = now_ms()
        outcome = registry.invoke("add", {"a": 2, "b": 3})
        holder["outcome"] = outcome
        holder["delta_ms"] = now_ms() - inv_start

    hlog("TEST3_BEGIN call (thread)")
    t = threading.Thread(target=do_invoke, name="test3-invoke")
    t.start()
    killed_pid = kill_proxy_mid_call(PID_FILE, PROXY_LOG)
    t.join(timeout=120)
    if t.is_alive():
        hlog("TEST3_INVOKE_THREAD_STILL_RUNNING_AFTER_120S")
        registry.close()
        sys.exit(2)
    hlog(f"TEST3_INVOKE_THREAD_DONE delta_ms={holder.get('delta_ms')}")

    outcome = holder.get("outcome")
    if outcome is not None:
        if hasattr(outcome, "message"):
            hlog(f"TEST3_OUTCOME message_verbatim={outcome.message!r}")
        elif hasattr(outcome, "result"):
            hlog(f"TEST3_OUTCOME result={outcome.result!r}")
    else:
        hlog("TEST3_OUTCOME none (invoke returned None)")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = events(proxy_lines, "backend_spawn_start")
    ups = events(proxy_lines, "backend_up")
    schema_failures = events(proxy_lines, "backend_schema_validation_failed")
    classified_responses = events(proxy_lines, "call_tool_classified_schema_failure")
    pids = proxy_pids(proxy_lines)

    persistent_proxies = max(0, len(pids) - 1)
    reconnect_fired = len(pids) > 2

    hlog(
        f"TEST3_SPAWN_COUNTS backend_spawn_count={len(spawns)} backend_up_count={len(ups)} "
        f"backend_schema_validation_failed_count={len(schema_failures)} "
        f"classified_response_count={len(classified_responses)} "
        f"proxy_processes={len(pids)} persistent_proxies={persistent_proxies} "
        f"reconnect_fired={reconnect_fired} killed_pid={killed_pid} proxy_pids={pids}"
    )
    for epoch, msg in spawns:
        hlog(f"TEST3_SPAWN_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in events(proxy_lines, "proxy_started"):
        hlog(f"TEST3_PROXY_STARTED epoch={epoch} msg={msg}")

    # ToolRegistry stringifies single text results ("5.0"), so compare the
    # string form, not a float.
    success = outcome is not None and hasattr(outcome, "result") and str(outcome.result) == "5.0"
    test3_ok = reconnect_fired and success and killed_pid is not None
    hlog(
        f"TEST3_RESULT pass={test3_ok} "
        f"(expected: reconnect_fired=YES, final outcome success 5.0, proxy killed; observed: "
        f"reconnect={reconnect_fired} success={success} killed={killed_pid is not None})"
    )
    registry.close()
    hlog(f"phase_done phase={PHASE} test3_connection_pass={test3_ok}")
    sys.exit(0 if test3_ok else 1)


if __name__ == "__main__":
    main()
