#!/usr/bin/env python
"""Phase: Test 4 (respawn resilience; fresh session).

Sequence (fresh proxy process, fresh registry):
  1. Register against the lazy proxy (backend never started).
  2. First call spawns the backend and succeeds.
  3. Kill the real backend process directly (SIGKILL, not through the
     proxy).  Confirm the process is gone.
  4. Second call: observe whether the proxy detects the dead backend,
     respawns, and succeeds, and how long recovery takes.
  5. Third call: steady state on the respawned backend.

NOTE ON OPERATIONALIZATION: the brief says "start proxy AND backend,
register, then kill".  With ToolRegistry 0.15.0 the persistent MCP
connection is created lazily on the first tool call, so no backend
process exists between registration and the first call.  The literal
reading was therefore operationalized as register -> first call (backend
spawned and connected) -> kill -> second call.  This is distinct from
Test 1's cold-start path (backend never existed); here a live backend
session is established and then severed.
"""

from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import (  # noqa: E402
    LOGS_DIR,
    backend_pid_from_file,
    count_events,
    first_event,
    hlog,
    make_transport,
    now_ms,
    read_proxy_log,
    safe_invoke,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test4"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
BACKEND_PID_FILE = LOGS_DIR / f"{PHASE}-backend.pid"


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:  # pragma: no cover
        return True


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()
    if BACKEND_PID_FILE.exists():
        BACKEND_PID_FILE.unlink()

    registry = ToolRegistry(name="test4")
    transport = make_transport(str(PROXY_LOG), backend_pid_file=str(BACKEND_PID_FILE))

    # -- register (fresh session) --
    hlog("TEST4_BEGIN register")
    try:
        registry.register_from_mcp(transport)
        hlog("TEST4_REGISTER result=ok")
    except Exception as exc:
        hlog(f"TEST4_REGISTER result=FAILED error={exc!r}")
        sys.exit(2)

    # -- first call: spawn backend --
    value = safe_invoke(registry, "add", {"a": 2, "b": 3}, "5.0")
    pid1 = backend_pid_from_file(BACKEND_PID_FILE)
    hlog(f"TEST4_FIRST_CALL result={value!r} backend_pid={pid1}")
    if pid1 is None or value != "5.0":
        hlog("TEST4_ABORT first call did not establish a live backend")
        sys.exit(2)
    if not process_alive(pid1):
        hlog("TEST4_ABORT backend pid not alive right after first call")
        sys.exit(2)

    # -- kill the real backend directly --
    hlog(f"TEST4_KILL killing backend pid={pid1} directly (SIGKILL)")
    kill_start = now_ms()
    os.kill(pid1, signal.SIGKILL)
    # Wait for the kernel to reap it (SIGKILL is immediate; give the OS a beat).
    for _ in range(50):
        if not process_alive(pid1):
            break
        time.sleep(0.02)
    alive_after_kill = process_alive(pid1)
    kill_end = now_ms()
    hlog(
        f"TEST4_KILL_DONE pid={pid1} alive_after_kill={alive_after_kill} "
        f"kill_detection_ms={kill_end - kill_start}"
    )
    if alive_after_kill:
        hlog("TEST4_ABORT backend did not die after SIGKILL")
        sys.exit(2)

    # -- second call: observe respawn behaviour --
    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_before = count_events(proxy_lines, "backend_spawn_start")
    hlog(f"TEST4_PRE_SECOND_CALL backend_spawn_count={spawns_before}")
    t0 = now_ms()
    value2 = safe_invoke(registry, "add", {"a": 4, "b": 5}, "9.0")
    t1 = now_ms()

    proxy_lines = read_proxy_log(PROXY_LOG)
    failures = [l for l in proxy_lines if l[1].startswith("backend_call_failed")]
    respawn_lines = [l for l in proxy_lines if l[1].startswith("backend_spawn_start")]
    retry_ok = [l for l in proxy_lines if l[1].startswith("backend_call_retry_succeeded")]
    spawns_after = count_events(proxy_lines, "backend_spawn_start")
    pid2 = backend_pid_from_file(BACKEND_PID_FILE)

    hlog(
        f"TEST4_SECOND_CALL result={value2!r} end_to_end_ms={t1 - t0} "
        f"backend_spawn_count={spawns_after} new_backend_pid={pid2} "
        f"backend_respawned={pid2 is not None and pid2 != pid1}"
    )
    for epoch, msg in failures:
        hlog(f"TEST4_FAILURE_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in respawn_lines:
        hlog(f"TEST4_SPAWN_EVENT epoch={epoch} msg={msg}")
    for epoch, msg in retry_ok:
        hlog(f"TEST4_RETRY_OK_EVENT epoch={epoch} msg={msg}")

    respawn_detected = len(failures) >= 1 and spawns_after >= spawns_before + 1
    test4_pass = (
        value2 == "9.0"
        and respawn_detected
        and pid2 is not None
        and pid2 != pid1
        and process_alive(pid2)
    )
    hlog(f"TEST4_SECOND_CALL_PASS pass={test4_pass}")

    # -- third call: steady state on respawned backend --
    value3 = safe_invoke(registry, "add", {"a": 10, "b": 20}, "30.0")
    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_final = count_events(proxy_lines, "backend_spawn_start")
    pid3 = backend_pid_from_file(BACKEND_PID_FILE)
    steady_ok = value3 == "30.0" and spawns_final == spawns_after and pid3 == pid2
    hlog(
        f"TEST4_THIRD_CALL result={value3!r} backend_spawn_count={spawns_final} "
        f"backend_pid={pid3} reused={pid3 == pid2} pass={steady_ok}"
    )

    registry.close()
    hlog(f"phase_done phase={PHASE} test4_pass={test4_pass}")
    sys.exit(0 if test4_pass else 1)


if __name__ == "__main__":
    main()
