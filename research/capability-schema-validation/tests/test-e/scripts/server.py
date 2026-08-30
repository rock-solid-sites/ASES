#!/usr/bin/env python3
"""Minimal loopback TCP runtime server for Test E.

Speaks newline-delimited JSON. Each line is a JSON object; responses are also one JSON line.

Request shapes:
  { "id": "<uuid>", "op_id": "search_artefacts", "args": {...}, "delay_ms": 0, "payload_version": "0.1.0"? }
  { "id": "<uuid>", "type": "cancel", "target_id": "<request id to cancel>" }  — cancellation probe
  { "id": "<uuid>", "type": "stream", "op_id": "...", "args": {...}, "chunks": 3 } — streaming probe
  { "id": "<uuid>", "type": "shutdown" } — graceful shutdown

Response shapes:
  { "id": "<same id>", "op_id": "...", "result": {...}|null, "error": {...}|null, "trace": [...], "server_pid": int, "duration_ms": int, "executed": bool, "version": "0.1.0" }
  For stream: sequence of { "id":..., "chunk": n, "total": 3, "data": {...}, "done": bool }

Usage:
  python -m research.capability-schema-validation.tests.test-e.scripts.server --port 0  (ephemeral, prints PORT=<port>)
  python research/capability-schema-validation/tests/test-e/scripts/server.py --port 8765
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
# harness import via importlib (handles hyphens in path)
import importlib.util as _ilu2

def _load2(name, path):
    spec = _ilu2.spec_from_file_location(name, path)
    mod = _ilu2.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

Harness = None
Sandbox = None
Runtime = None
try:
    harness_dir = HERE.parents[2] / "harness"
    _sb = _load2("svr_sandbox", str(harness_dir / "sandbox.py"))
    _rt = _load2("svr_runtime", str(harness_dir / "runtime.py"))
    Sandbox, Runtime, Harness = _sb.Sandbox, _rt.Runtime, _rt.Harness
except Exception as e:
    print(f"server import failed: {e}", file=sys.stderr)
    raise

# in-flight registry for cancellation support
_IN_FLIGHT: dict[str, dict] = {}
_CANCELLED_IDS: set[str] = set()
_LOCK = threading.Lock()
_DURABLE_STORE: dict[str, dict] = {}  # id -> last response (for durable probe)


def get_harness():
    if Harness is None:
        raise RuntimeError("Harness not imported")
    return Harness(Sandbox(), Runtime())


_harness_singleton = None
_harness_lock = threading.Lock()


def harness():
    global _harness_singleton
    with _harness_lock:
        if _harness_singleton is None:
            _harness_singleton = get_harness()
        return _harness_singleton


def handle_request(req: dict) -> dict:
    pid = os.getpid()
    rid = req.get("id", "unknown")
    delay = int(req.get("delay_ms", 0) or 0)
    rtype = req.get("type", "call")

    if rtype == "shutdown":
        return {"id": rid, "type": "shutdown_ack", "server_pid": pid}

    if rtype == "cancel":
        target = req.get("target_id")
        with _LOCK:
            _CANCELLED_IDS.add(target)
        return {"id": rid, "type": "cancel_ack", "target_id": target, "server_pid": pid, "cancelled": True}

    if rtype == "stream":
        # streaming is handled inline by the caller (chunk loop); return error if called via handle_request
        op_id = req.get("op_id", "query_metrics")
        args = req.get("args", {})
        chunks = int(req.get("chunks", 3))
        # simulate: return first chunk only; streaming loop will handle multi-send
        return {"id": rid, "op_id": op_id, "chunk": 0, "total": chunks, "data": {"stream": True, "chunk": 0}, "done": False, "server_pid": pid}

    # normal call
    op_id = req.get("op_id")
    args = req.get("args", {})
    payload_version = req.get("payload_version")
    policy = req.get("policy")

    # register in-flight
    with _LOCK:
        _IN_FLIGHT[rid] = {"op_id": op_id, "start": time.time()}

    # honor delay cooperatively: sleep in small slices and check cancellation
    if delay > 0:
        # slice into 50 ms chunks to allow cancellation to interrupt
        remaining = delay
        while remaining > 0:
            with _LOCK:
                if rid in _CANCELLED_IDS:
                    del _IN_FLIGHT[rid]
                    return {
                        "id": rid,
                        "op_id": op_id,
                        "result": None,
                        "error": {"code": "Cancelled", "op_id": op_id, "boundary": "transport", "reason": "caller-initiated cancel"},
                        "trace": ["server:cancelled"],
                        "server_pid": pid,
                        "duration_ms": int((time.time() - _IN_FLIGHT.get(rid, {}).get("start", time.time())) * 1000),
                        "executed": False,
                        "version": harness().runtime.version,
                        "disposition": "cancelled_before_execution",
                    }
            step = min(50, remaining)
            time.sleep(step / 1000.0)
            remaining -= step
            # check again after sleep
            with _LOCK:
                if rid in _CANCELLED_IDS:
                    del _IN_FLIGHT[rid]
                    return {
                        "id": rid,
                        "op_id": op_id,
                        "result": None,
                        "error": {"code": "Cancelled", "op_id": op_id, "boundary": "transport", "reason": "caller-initiated cancel"},
                        "trace": ["server:cancelled"],
                        "server_pid": pid,
                        "duration_ms": int((time.time() - _IN_FLIGHT[rid].get("start", time.time())) * 1000) if rid in _IN_FLIGHT else 0,
                        "executed": False,
                        "version": harness().runtime.version,
                        "disposition": "cancelled_before_execution",
                    }

    start = time.time()
    try:
        res = harness().call(op_id, args, payload_version=payload_version, policy=policy)
    except Exception as e:
        res = {"op_id": op_id, "error": {"code": "ValidationFailed", "message": str(e)}, "executed": False, "trace": ["server:exception"], "version": "0.1.0"}
        duration_ms = int((time.time() - start) * 1000)
        out = {
            "id": rid,
            "op_id": op_id,
            "result": None,
            "error": res["error"],
            "trace": res.get("trace", []),
            "server_pid": pid,
            "duration_ms": duration_ms,
            "executed": False,
            "version": res.get("version", "0.1.0"),
        }
        with _LOCK:
            _IN_FLIGHT.pop(rid, None)
            _DURABLE_STORE[rid] = out
        return out

    duration_ms = res.get("latency_ms", int((time.time() - start) * 1000))
    out = {
        "id": rid,
        "op_id": op_id,
        "result": res.get("result"),
        "error": res.get("error"),
        "trace": res.get("trace", []),
        "server_pid": pid,
        "duration_ms": duration_ms,
        "executed": res.get("executed", False),
        "version": res.get("version", "0.1.0"),
        "validation_result": res.get("validation_result"),
    }
    # if this request was marked cancelled concurrently, override
    with _LOCK:
        if rid in _CANCELLED_IDS:
            _IN_FLIGHT.pop(rid, None)
            # cancelled wins even if execution already happened — record disposition
            if out["executed"]:
                out["disposition"] = "completed_before_cancel_ack"
            else:
                out["disposition"] = "cancelled_before_execution"
                out["error"] = {"code": "Cancelled", "op_id": op_id, "boundary": "transport"}
            _DURABLE_STORE[rid] = out
            return out
        _IN_FLIGHT.pop(rid, None)
        _DURABLE_STORE[rid] = out

    # also support durable query: if client later asks for same id via special type fetch
    return out


def client_handler(conn: socket.socket, addr, executor: ThreadPoolExecutor):
    conn.settimeout(None)
    buf = b""
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    req = json.loads(line.decode("utf-8"))
                except Exception as e:
                    err = json.dumps({"error": {"code": "ValidationFailed", "message": f"bad json: {e}"}}).encode() + b"\n"
                    try:
                        conn.sendall(err)
                    except Exception:
                        pass
                    continue

                # durable fetch probe: { "type": "fetch", "target_id": "<prior id>" }
                if req.get("type") == "fetch":
                    tid = req.get("target_id")
                    with _LOCK:
                        stored = _DURABLE_STORE.get(tid)
                    if stored is None:
                        resp = json.dumps({"id": req.get("id"), "error": {"code": "NotFound", "target_id": tid}}).encode() + b"\n"
                    else:
                        resp = json.dumps({"id": req.get("id"), "durable_result": stored}).encode() + b"\n"
                    try:
                        conn.sendall(resp)
                    except Exception:
                        pass
                    continue

                # streaming probe: send chunks as separate lines
                if req.get("type") == "stream":
                    rid = req.get("id")
                    chunks = int(req.get("chunks", 3))
                    for n in range(chunks):
                        chunk_msg = json.dumps({"id": rid, "chunk": n, "total": chunks, "data": {"chunk": n, "value": f"chunk-{n}"}, "done": n == chunks - 1, "server_pid": os.getpid()}).encode() + b"\n"
                        try:
                            conn.sendall(chunk_msg)
                        except Exception:
                            break
                        time.sleep(0.02)
                    continue

                # normal request via thread pool (allows server-side concurrency)
                def do_send(r):
                    resp = handle_request(r)
                    line_out = json.dumps(resp).encode() + b"\n"
                    try:
                        conn.sendall(line_out)
                    except Exception:
                        pass
                    # shutdown signal
                    if r.get("type") == "shutdown":
                        try:
                            conn.shutdown(socket.SHUT_RDWR)
                        except Exception:
                            pass

                # for concurrent correctness: dispatch via executor but wait for ordering? No — submit and continue reading
                # For simplicity, handle inline for small concurrency; use executor for delayed cases
                if req.get("delay_ms", 0):
                    executor.submit(do_send, req)
                else:
                    # also via executor so reordering is possible
                    executor.submit(do_send, req)

                if req.get("type") == "shutdown":
                    return
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def serve(port: int):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    actual = srv.getsockname()[1]
    print(f"PORT={actual}", flush=True)
    print(f"PID={os.getpid()}", flush=True)
    srv.listen(32)
    executor = ThreadPoolExecutor(max_workers=16)
    try:
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=client_handler, args=(conn, addr, executor), daemon=True)
            t.start()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown(wait=False)
        try:
            srv.close()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0, help="Port 0=ephemeral (prints PORT=...)")
    args = ap.parse_args()
    serve(args.port)


if __name__ == "__main__":
    main()
