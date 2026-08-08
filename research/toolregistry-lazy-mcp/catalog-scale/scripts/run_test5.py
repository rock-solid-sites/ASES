#!/usr/bin/env python
"""TEST 5 — Catalog Invalidation Behavior (characterize, do NOT fix).

Session-boundary model assumption: a confirmed catalog stays valid until the
next confirmation point. Two distinct experiments (addendum A):

5a INVALIDATION TEST — establish small catalog, modify backend's tool set,
   emit notifications/tools/list_changed via the proxy's control tool,
   observe whether the registry/proxy receives it, refreshes the catalog,
   starts any backend unnecessarily, or leaves processes resident.
5b STALE-CATALOG BASELINE — with NO invalidation signal, does the stack
   retain the previous catalog as-is, and what happens on next first-use of
   a tool whose backend changed underneath it? (Baseline measurement, no
   drift-detection expectation.)

ToolRegistry not consuming/propagating list_changed is a WIDELY DOCUMENTED
current gap across major MCP clients — recorded as an implementation gap,
NOT a bug to fix here.

Calling mode: SYNC. Stdio only.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    GRACE_SECONDS,
    clean_orphans,
    count_events,
    pct_line,
    snapshot,
    versions,
    write_json,
)

from toolregistry import ToolRegistry  # noqa: E402
from toolregistry._async_runtime import AsyncRuntime  # noqa: E402

RUN_LABEL = "test5"
VENV_PY = sys.executable


def _conn_for(reg: ToolRegistry, idx: int):
    return reg._mcp_integrations[idx]._connections[0]


def _write_control(path: Path, tool_names: list[str]) -> None:
    """Control file: tools dicts for backend_5a.py. add/sub schema inline."""
    defs = []
    for name in tool_names:
        if name == "add":
            defs.append({
                "name": "add",
                "description": "Add two numbers and return the sum.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First addend"},
                        "b": {"type": "number", "description": "Second addend"},
                    },
                    "required": ["a", "b"],
                },
            })
        elif name == "sub":
            defs.append({
                "name": "sub",
                "description": "Subtract two numbers and return the difference.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First operand"},
                        "b": {"type": "number", "description": "Second operand"},
                    },
                    "required": ["a", "b"],
                },
            })
    path.write_text(json.dumps({"tools": defs}, indent=2))


def _transport(cid: str, log_dir: Path, control_file: Path) -> dict:
    return {
        "command": VENV_PY,
        "args": [str(HERE / "proxy_5a.py")],
        "env": {
            "PROXY_LOG_FILE": str(log_dir / f"{cid}-proxy.log"),
            "BACKEND_PID_FILE": str(log_dir / f"{cid}-backend.pid"),
            "BACKEND_5A_CONTROL_FILE": str(control_file),
            "PROXY_5A_MANIFEST": str(HERE / "manifest_5a.json"),
        },
    }


def test_5a(log_dir: Path) -> dict:
    pct_line("TEST5a begin")
    control = log_dir / "control-5a.json"
    _write_control(control, ["add"])

    reg = ToolRegistry()
    reg.register_from_mcp(_transport("a", log_dir, control), namespace="a")
    catalog_initial = sorted(reg.list_tools())
    pct_line(f"TEST5a catalog_initial={catalog_initial}")

    # refresh (temp client) before any invocation
    AsyncRuntime.run_sync(_conn_for(reg, 0).list_tools())

    # first call: backend spawns, persistent proxy + backend resident
    r1 = reg.invoke("a-add", {"a": 1, "b": 2})
    pct_line(f"TEST5a call_add result={getattr(r1, 'result', r1)}")

    time.sleep(1.0)
    resident_before_change = snapshot()
    pct_line(
        f"TEST5a resident_before_change proxies={resident_before_change['proxy_count']} "
        f"backends={resident_before_change['backend_count']}"
    )

    # modify backend tool set: remove add, add sub
    _write_control(control, ["sub"])

    # emit notifications/tools/list_changed via control tool
    r2 = reg.invoke("a-_emit_list_changed", {})
    pct_line(f"TEST5a emit_result={getattr(r2, 'result', r2)}")

    time.sleep(GRACE_SECONDS)
    resident_after_notify = snapshot()

    # Does the registry's catalog change? (it should not — no listener)
    catalog_after = sorted(reg.list_tools())

    # Does a fresh refresh see the change? (temp proxy serves the static
    # manifest — backend not connected in the temp process)
    refresh_tools = []
    try:
        tools = AsyncRuntime.run_sync(_conn_for(reg, 0).list_tools())
        refresh_tools = sorted(t.name for t in tools)
    except Exception as exc:
        pct_line(f"TEST5a refresh_after error {type(exc).__name__}:{exc}")

    events = count_events(
        [log_dir / "a-proxy.log"],
        ["proxy_5a_started", "backend_spawn_start", "backend_up", "sent notifications/tools/list_changed",
         "send_list_changed_error", "live_list_error", "request tools/list"],
    )

    result = {
        "test": "5a",
        "catalog_initial": catalog_initial,
        "catalog_after_notify": catalog_after,
        "catalog_changed": catalog_initial != catalog_after,
        "refresh_tools_after_notify": refresh_tools,
        "resident_before_change": resident_before_change,
        "resident_after_notify": resident_after_notify,
        "proxy_log_events": events,
        "call_result": getattr(r1, "result", r1),
        "emit_result": getattr(r2, "result", r2),
        "calling_mode": "sync",
        "versions": versions(),
        "grace_seconds": GRACE_SECONDS,
    }
    write_json(log_dir / "test5a.json", result)
    pct_line(
        f"TEST5a done catalog_changed={result['catalog_changed']} "
        f"resident_proxies_after={resident_after_notify['proxy_count']} "
        f"resident_backends_after={resident_after_notify['backend_count']} "
        f"backend_spawns_total={events['backend_spawn_start']}"
    )

    # Cleanup (NOT measurement): close every manager so this phase's
    # persistent connector cannot orphan into the 5b phase's snapshots.
    for cid in ("a",):
        try:
            _conn_for(reg, 0).close_sync()
        except Exception as exc:
            pct_line(f"CLEANUP_ERROR cid={cid} exc={type(exc).__name__}:{exc}")
    time.sleep(GRACE_SECONDS)
    return result


def test_5b(log_dir: Path) -> dict:
    pct_line("TEST5b begin")
    control = log_dir / "control-5b.json"
    _write_control(control, ["add"])

    reg = ToolRegistry()
    reg.register_from_mcp(_transport("b", log_dir, control), namespace="b")
    catalog_initial = sorted(reg.list_tools())
    pct_line(f"TEST5b catalog_initial={catalog_initial}")

    # refresh before change (temp client, static manifest)
    AsyncRuntime.run_sync(_conn_for(reg, 0).list_tools())

    # backend changes underneath WITHOUT any signal
    _write_control(control, ["sub"])

    time.sleep(GRACE_SECONDS)
    resident_before_first_use = snapshot()

    # next first-use of a tool whose backend changed underneath it
    r1 = reg.invoke("b-add", {"a": 1, "b": 2})
    pct_line(f"TEST5b first_use_changed result={getattr(r1, 'result', r1)} is_error={getattr(r1, 'is_error', getattr(r1, 'isError', None))}")

    time.sleep(GRACE_SECONDS)
    resident_after_first_use = snapshot()

    # a tool added on the backend but absent from the catalog
    r2 = reg.invoke("b-sub", {"a": 5, "b": 2})
    pct_line(f"TEST5b invoke_new_tool_absent_from_catalog result={getattr(r2, 'result', r2)}")

    # fresh refresh: does it see the change? (static manifest, stale)
    refresh_tools = []
    try:
        tools = AsyncRuntime.run_sync(_conn_for(reg, 0).list_tools())
        refresh_tools = sorted(t.name for t in tools)
    except Exception as exc:
        pct_line(f"TEST5b refresh_after error {type(exc).__name__}:{exc}")

    events = count_events(
        [log_dir / "b-proxy.log"],
        ["proxy_5a_started", "backend_spawn_start", "backend_up", "sent notifications/tools/list_changed"],
    )

    result = {
        "test": "5b",
        "catalog_initial": catalog_initial,
        "first_use_result": getattr(r1, "result", r1),
        "first_use_is_error": getattr(r1, "is_error", getattr(r1, "isError", None)),
        "invoke_new_tool_absent_from_catalog_result": getattr(r2, "result", r2),
        "refresh_tools_after_change": refresh_tools,
        "resident_before_first_use": resident_before_first_use,
        "resident_after_first_use": resident_after_first_use,
        "proxy_log_events": events,
        "calling_mode": "sync",
        "versions": versions(),
        "grace_seconds": GRACE_SECONDS,
    }
    write_json(log_dir / "test5b.json", result)
    pct_line(
        f"TEST5b done first_use_is_error={result['first_use_is_error']} "
        f"refresh_stale={refresh_tools == catalog_initial} "
        f"resident_proxies_after={resident_after_first_use['proxy_count']} "
        f"resident_backends_after={resident_after_first_use['backend_count']} "
        f"backend_spawns_total={events['backend_spawn_start']}"
    )

    # Cleanup (NOT measurement): close this phase's persistent connector so
    # it cannot orphan into a later phase (proxy exit can hang — see
    # clean_orphans). Last phase, but hygiene keeps the corpus reproducible.
    try:
        _conn_for(reg, 0).close_sync()
    except Exception as exc:
        pct_line(f"CLEANUP_ERROR exc={type(exc).__name__}:{exc}")
    time.sleep(GRACE_SECONDS)
    return result


def main() -> None:
    base = HERE / "logs" / RUN_LABEL
    base.mkdir(parents=True, exist_ok=True)
    orphan_count = clean_orphans()
    pct_line(f"TEST5 begin versions={versions()} pre_cleaned_orphans={orphan_count}")
    log_5a = base / "5a"
    log_5a.mkdir(parents=True, exist_ok=True)
    for stale in list(log_5a.glob("*.log")) + list(log_5a.glob("*.pid")):
        stale.unlink()
    test_5a(log_5a)

    log_5b = base / "5b"
    log_5b.mkdir(parents=True, exist_ok=True)
    for stale in list(log_5b.glob("*.log")) + list(log_5b.glob("*.pid")):
        stale.unlink()
    test_5b(log_5b)

    pct_line("TEST5 done")
    sys.exit(0)


if __name__ == "__main__":
    main()
