#!/usr/bin/env python
"""Addendum B thread-profile check: does the calling mode hold different
resident resources?

In ONE fresh process:
  Phase 1 — ASYNC-only: register 1 connector via register_from_mcp_async,
            refresh, measure thread profile. Expect ZERO 'async-runtime'
            threads (ToolRegistry's AsyncRuntime is never touched by the
            async path — source: _async_runtime.py is only imported/used by
            the sync entry points).
  Phase 2 — SYNC call: one invoke via the sync path. Expect the single
            shared 'async-runtime' daemon thread to appear and stay.

Also records proxy/backend process counts alongside (per addendum B:
daemon-thread count tracked ALONGSIDE process count and RSS).

Run as a standalone fresh subprocess so no prior sync call contaminated the
profile. Stdio only.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    GRACE_SECONDS,
    build_transport,
    pct_line,
    snapshot,
    versions,
    write_json,
)

from toolregistry import ToolRegistry  # noqa: E402

RUN_LABEL = "threadcheck"


def _conn_for(reg: ToolRegistry, cid: str):
    idx = int(cid.lstrip("c"))
    return reg._mcp_integrations[idx]._connections[0]


def main() -> None:
    base = HERE / "logs" / RUN_LABEL
    base.mkdir(parents=True, exist_ok=True)
    log_dir = base / "run"
    log_dir.mkdir(parents=True, exist_ok=True)
    for stale in list(log_dir.glob("*.log")) + list(log_dir.glob("*.pid")):
        stale.unlink()

    pct_line(f"THREADCHECK begin versions={versions()}")

    # Phase 1: async-only
    reg = ToolRegistry()
    transport = build_transport("ta", log_dir)

    async def _async_register_and_refresh():
        await reg.register_from_mcp_async(transport, namespace="ta")
        await reg._mcp_integrations[0]._connections[0].list_tools()

    asyncio.run(_async_register_and_refresh())
    time.sleep(GRACE_SECONDS)
    profile_async = snapshot()
    pct_line(
        f"THREADCHECK async_only threads={profile_async['threads']} "
        f"proxies={profile_async['proxy_count']} backends={profile_async['backend_count']}"
    )

    # Phase 2: sync call in the same process (spawns persistent proxy + backend)
    r = reg.invoke("ta-add", {"a": 1, "b": 2})
    pct_line(f"THREADCHECK sync_call result={getattr(r, 'result', r)}")
    time.sleep(1.0)
    profile_sync = snapshot()
    pct_line(
        f"THREADCHECK after_sync_call threads={profile_sync['threads']} "
        f"proxies={profile_sync['proxy_count']} backends={profile_sync['backend_count']}"
    )

    result = {
        "test": "threadcheck",
        "calling_mode": "async-then-sync",
        "async_only_profile": profile_async,
        "after_sync_call_profile": profile_sync,
        "versions": versions(),
        "grace_seconds": GRACE_SECONDS,
    }
    write_json(base / "threadcheck.json", result)
    pct_line("THREADCHECK done")
    sys.exit(0)


if __name__ == "__main__":
    main()
