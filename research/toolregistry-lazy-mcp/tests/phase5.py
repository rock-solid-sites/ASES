#!/usr/bin/env python
"""Phase: Test 5 (notification dependency; fresh session).

Part A (runtime): register exactly as Test 1 (backend never started),
then invoke a tool.  The proxy never sends ANY notification at any point
(no ``notifications/tools/list_changed``, no ``notifications/*`` at all).
Confirm the registry keeps functioning for discovery and invocation.

Part B (source read): done in the report — inspect the installed
ToolRegistry source for any use of ``notifications/tools/list_changed``.
This phase only records the runtime half of the evidence.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import (  # noqa: E402
    LOGS_DIR,
    backend_pid_from_file,
    count_events,
    hlog,
    make_transport,
    now_ms,
    read_proxy_log,
    safe_invoke,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test5"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
BACKEND_PID_FILE = LOGS_DIR / f"{PHASE}-backend.pid"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()
    if BACKEND_PID_FILE.exists():
        BACKEND_PID_FILE.unlink()

    registry = ToolRegistry(name="test5")
    transport = make_transport(str(PROXY_LOG), backend_pid_file=str(BACKEND_PID_FILE))

    # -- register as Test 1 --
    hlog("TEST5_REGISTER_BEGIN")
    try:
        registry.register_from_mcp(transport)
        hlog("TEST5_REGISTER result=ok")
    except Exception as exc:
        hlog(f"TEST5_REGISTER result=FAILED error={exc!r}")
        sys.exit(2)
    time.sleep(0.5)

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_after_register = count_events(proxy_lines, "backend_spawn_start")
    backend_pid_after_register = backend_pid_from_file(BACKEND_PID_FILE)
    registered = registry.list_tools()
    hlog(
        f"TEST5_AFTER_REGISTER list_tools={registered} "
        f"backend_spawn_count={spawns_after_register} "
        f"backend_pid_file_exists={backend_pid_after_register is not None}"
    )

    # -- invocation --
    value = safe_invoke(registry, "add", {"a": 2, "b": 3}, "5.0")

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_after_call = count_events(proxy_lines, "backend_spawn_start")
    # The proxy has zero notification-send code paths; assert the log
    # contains no notification-related outgoing marker either.
    notify_lines = [l for l in proxy_lines if "notification" in l[1].lower()]
    hlog(f"TEST5_PROXY_LOG notification_related_lines={notify_lines}")

    # Discovery still works after the call (registry is a live object).
    discovered = registry.list_tools()
    hlog(f"TEST5_AFTER_CALL list_tools={discovered}")

    pass5 = (
        value == "5.0"
        and spawns_after_register == 0
        and "add" in registered
        and "add" in discovered
        and spawns_after_call == 1
        and all("notifications/tools/list_changed" not in msg for _, msg in proxy_lines)
    )
    hlog(f"TEST5_RESULT pass={pass5}")

    registry.close()
    hlog(f"phase_done phase={PHASE} test5_pass={pass5}")
    sys.exit(0 if pass5 else 1)


if __name__ == "__main__":
    main()
