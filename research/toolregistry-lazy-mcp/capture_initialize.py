#!/usr/bin/env python
"""Supplementary capture: one stdio initialize handshake against the lazy proxy.

Evidence-only. Does NOT modify proxy.py/backend.py/tests. Spawns the proxy
exactly as ToolRegistry does (venv python + proxy.py), performs one MCP
initialize handshake over stdio, and records the RAW request and response
payloads with timestamps so the report's capability claims are on file rather
than inferred.

Frame format: mcp 2.0.0 stdio transport uses newline-delimited JSON-RPC
(one message per line, UTF-8). The request protocolVersion is 2025-11-25,
which is LATEST_HANDSHAKE_VERSION in mcp 2.0.0 — the value ClientSession
(used by ToolRegistry) sends by default.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = HERE / "proxy.py"
VENV_PY = "/tmp/toolregistry-venv/bin/python"
OUT = HERE / "logs" / "initialize-capture.json"


def now_ms() -> int:
    return int(time.time() * 1000)


def now_iso() -> str:
    t = time.time()
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + f".{int(t * 1000) % 1000:03d}Z"


def main() -> None:
    events: list[dict] = []

    def event(kind: str, payload: object) -> None:
        events.append({
            "kind": kind,
            "timestamp_iso": now_iso(),
            "epoch_ms": now_ms(),
            "payload": payload,
        })

    event("capture_start", {
        "purpose": "supplementary initialize handshake capture for report MUST FIX 4",
        "proxy": str(PROXY),
        "venv_python": VENV_PY,
        "spawn_command": [VENV_PY, str(PROXY)],
        "transport": "stdio (newline-delimited JSON-RPC)",
    })

    proc = subprocess.Popen(
        [VENV_PY, str(PROXY)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(HERE),
        env={**os.environ, "PROXY_LOG_FILE": str(HERE / "logs" / "initialize-capture-proxy.log")},
        bufsize=1,
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None

    def send(method: str, params: object, req_id: int | None = None) -> None:
        msg: dict = {"jsonrpc": "2.0", "method": method}
        if req_id is not None:
            msg["id"] = req_id
        if params is not None:
            msg["params"] = params
        event("send", msg)
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()

    def recv(timeout: float = 30.0) -> dict | None:
        """Read one line from the proxy's stdout with a deadline."""
        import select
        import io
        deadline = time.time() + timeout
        buf = io.StringIO()
        while time.time() < deadline:
            r, _, _ = select.select([proc.stdout], [], [], 0.25)
            if r:
                line = proc.stdout.readline()
                if line == "":
                    return None
                if line.strip():
                    event("recv_raw", line.strip())
                    try:
                        parsed = json.loads(line)
                        event("recv_parsed", parsed)
                        return parsed
                    except json.JSONDecodeError as exc:
                        event("recv_parse_error", {"line": line.strip(), "error": str(exc)})
                        return None
                continue
        event("recv_timeout", {"timeout_s": timeout})
        return None

    # --- 1. initialize handshake (what ToolRegistry's ClientSession sends) ---
    send(
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "initialize-capture", "version": "1.0"},
        },
        req_id=1,
    )
    init_result = recv()
    if init_result is None:
        event("capture_error", "no initialize response received")
    else:
        # Surface the listChanged serialization explicitly for the report.
        tools_cap = ((init_result.get("result") or {}).get("capabilities") or {}).get("tools")
        event("listChanged_serialization_note", {
            "tools_capability_object": tools_cap,
            "listChanged_present": "listChanged" in (tools_cap or {}),
            "listChanged_value": (tools_cap or {}).get("listChanged"),
        })

    # --- 2. notifications/initialized (client completes handshake) ---
    send("notifications/initialized", None)
    time.sleep(0.2)

    # --- 3. tools/list (the request ToolRegistry makes for discovery) ---
    send("tools/list", {}, req_id=2)
    recv()

    # --- close stdin so the proxy exits cleanly ---
    event("closing_stdin", None)
    proc.stdin.close()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
        event("proxy_killed_after_timeout", None)
    event("proxy_exit", {"returncode": proc.returncode})

    stderr = proc.stderr.read()
    proxy_log_lines = [l for l in stderr.splitlines() if l.startswith("PROXY|")]
    event("proxy_stderr_lines", proxy_log_lines)

    event("capture_end", {"artifact": str(OUT)})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"capture": events}, fh, indent=2)
        fh.write("\n")

    print(f"wrote {OUT}")
    print(f"events: {len(events)}")
    for e in events:
        if e["kind"] in ("send", "recv_raw", "recv_parsed", "listChanged_serialization_note"):
            print(f"  {e['kind']} @ {e['epoch_ms']}: {json.dumps(e['payload'])[:400]}")


if __name__ == "__main__":
    main()
