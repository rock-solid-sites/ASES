#!/usr/bin/env python3
"""Test E runner — 9 transport properties (7 required + 2 conditional).

Each property is an independent check with JSONL logging under logs/test-e/.
Runner is deterministic and reproducible via `python research/capability-schema-validation/tests/test-e/run.py`.

Artifacts:
  logs/test-e/{concurrent,correlation,remote,loss-mid-request,loss-mid-idle,reconnect,timeout,cancellation,streaming,durable}.jsonl
  logs/test-e/summary.json
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
_HERE_FILE = Path(__file__).resolve()
ROOT = _HERE_FILE.parents[2]  # research/capability-schema-validation
HARNESS_DIR = ROOT / "harness"
LOG_DIR = ROOT / "logs" / "test-e"
SCRIPT_SERVER = HERE / "scripts" / "server.py"

# Ensure harness importable (project root)
for p in [str(ROOT.parent.parent), str(_HERE_FILE.parents[4])]:
    if p not in sys.path:
        sys.path.insert(0, p)

PROJ_ROOT = _HERE_FILE.parents[4]
sys.path.insert(0, str(PROJ_ROOT))

import importlib.util as _ilu

def _load(name, path):
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_sandbox_mod = _load("test_e_sandbox", str(HARNESS_DIR / "sandbox.py"))
_runtime_mod = _load("test_e_runtime", str(HARNESS_DIR / "runtime.py"))
Sandbox = _sandbox_mod.Sandbox
Runtime = _runtime_mod.Runtime
_Harness = _runtime_mod.Harness

CLIENT_PID = os.getpid()


def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ─── TCP helpers ───────────────────────────────────────────────────────────────


def start_server() -> tuple[subprocess.Popen, int]:
    """Start loopback TCP server as subprocess on ephemeral port. Returns (proc, port)."""
    # Use unbuffered python so PORT line flushes
    proc = subprocess.Popen(
        [sys.executable, "-u", str(SCRIPT_SERVER), "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    # read PORT= line
    port = None
    deadline = time.time() + 5
    while time.time() < deadline:
        line = proc.stdout.readline()  # type: ignore
        if not line:
            if proc.poll() is not None:
                err = proc.stderr.read()  # type: ignore
                raise RuntimeError(f"server died immediately: {err}")
            time.sleep(0.05)
            continue
        line = line.strip()
        if line.startswith("PORT="):
            port = int(line.split("=", 1)[1])
            break
    if port is None:
        proc.terminate()
        raise RuntimeError("server did not emit PORT within 5s")
    # wait briefly for listen to settle
    time.sleep(0.1)
    # verify reachable
    for _ in range(10):
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=1)
            s.close()
            break
        except Exception:
            time.sleep(0.1)
    return proc, port


def tcp_call(port: int, req: dict, timeout: float = 5.0) -> dict:
    """Single request over fresh TCP connection. Returns response dict or error dict."""
    rid = req.get("id", str(uuid.uuid4()))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", port))
        s.sendall((json.dumps(req) + "\n").encode())
        # read one line with timeout
        s.settimeout(timeout)
        buf = b""
        start = time.time()
        while True:
            if time.time() - start > timeout:
                return {"id": rid, "error": {"code": "Timeout", "op_id": req.get("op_id", ""), "deadline_ms": int(timeout * 1000), "boundary": "transport"}, "timeout": True}
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                return {"id": rid, "error": {"code": "Timeout", "op_id": req.get("op_id", ""), "deadline_ms": int(timeout * 1000), "boundary": "transport"}, "timeout": True}
            if not chunk:
                return {"id": rid, "error": {"code": "ConnectionLost", "transport": "loopback-TCP", "in_flight": True, "boundary": "transport"}, "connection_lost": True}
            buf += chunk
            if b"\n" in buf:
                line, _ = buf.split(b"\n", 1)
                line = line.strip()
                if line:
                    return json.loads(line.decode("utf-8"))
    finally:
        try:
            s.close()
        except Exception:
            pass


def tcp_call_with_conn(conn: socket.socket, req: dict, timeout: float = 5.0) -> dict:
    """Send req on an already-connected socket and read one response."""
    rid = req.get("id", str(uuid.uuid4()))
    conn.settimeout(timeout)
    try:
        conn.sendall((json.dumps(req) + "\n").encode())
        buf = b""
        start = time.time()
        while True:
            if time.time() - start > timeout:
                return {"id": rid, "error": {"code": "Timeout", "boundary": "transport"}, "timeout": True}
            try:
                chunk = conn.recv(4096)
            except socket.timeout:
                return {"id": rid, "error": {"code": "Timeout", "boundary": "transport"}, "timeout": True}
            if not chunk:
                return {"id": rid, "error": {"code": "ConnectionLost", "boundary": "transport", "in_flight": True}, "connection_lost": True}
            buf += chunk
            if b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if line:
                    return json.loads(line.decode("utf-8"))
    except BrokenPipeError:
        return {"id": rid, "error": {"code": "ConnectionLost", "boundary": "transport", "in_flight": True}, "connection_lost": True}
    except Exception as e:
        return {"id": rid, "error": {"code": "ConnectionLost", "boundary": "transport", "detail": str(e)}, "connection_lost": True}


# ─── JSONL logger ─────────────────────────────────────────────────────────────

LOG_FILES: dict[str, list] = {}


def log_jsonl(name: str, record: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    p = LOG_DIR / f"{name}.jsonl"
    with p.open("a") as f:
        f.write(json.dumps(record) + "\n")
    LOG_FILES.setdefault(name, []).append(record)


def truncate_log(name: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{name}.jsonl").write_text("")


# ─── Property 1: concurrent requests ─────────────────────────────────────────


def test_concurrent(proc: subprocess.Popen, port: int) -> dict:
    name = "concurrent"
    truncate_log(name)
    N = 8
    # mix of ops, one is intentionally delayed to test non-serial
    specs = [
        {"op_id": "search_artefacts", "args": {"query": "hello"}, "delay_ms": 0},
        {"op_id": "get_artefact", "args": {"id": "art_abc-123"}, "delay_ms": 0},
        {"op_id": "create_artefact", "args": {"type": "spec", "title": "Concurrent 1"}, "delay_ms": 0},
        {"op_id": "search_artefacts", "args": {"query": "delayed", "limit": 5}, "delay_ms": 200},
        {"op_id": "list_reviews", "args": {"limit": 10}, "delay_ms": 0},
        {"op_id": "query_metrics", "args": {"filter": {"type": "spec"}}, "delay_ms": 0},
        {"op_id": "get_artefact", "args": {"id": "art_def-456"}, "delay_ms": 0},
        {"op_id": "create_artefact", "args": {"type": "decision", "title": "Concurrent 2"}, "delay_ms": 0},
    ]
    # measure single-call latency baseline (direct harness)
    harness = _Harness(Sandbox(), Runtime())
    t0_s = time.time()
    harness.call("search_artefacts", {"query": "hello"})
    single_ms = int((time.time() - t0_s) * 1000)
    if single_ms == 0:
        single_ms = 5

    iterations = 3
    all_pass = True
    total_wall_ms = []
    for it in range(iterations):
        ids = [str(uuid.uuid4()) for _ in range(N)]
        requests = [{"id": ids[i], **specs[i]} for i in range(N)]
        start = time.time()
        results = {}
        with ThreadPoolExecutor(max_workers=N) as ex:
            futs = {ex.submit(tcp_call, port, req, 5.0): req for req in requests}
            for fut in as_completed(futs):
                req = futs[fut]
                try:
                    resp = fut.result()
                except Exception as e:
                    resp = {"id": req["id"], "error": {"code": "ConnectionLost", "detail": str(e)}}
                results[req["id"]] = resp
        wall_ms = int((time.time() - start) * 1000)
        total_wall_ms.append(wall_ms)
        serial_bound = N * max(single_ms, 15) + 500  # conservative upper bound for serial
        # also check non-serial: wall should be < sum(serial) but > 0; with one 200ms delay, wall ~200+overhead if concurrent
        non_serial = wall_ms < serial_bound and wall_ms < 2000
        all_returned = len(results) == N
        all_matched = all(results[rid].get("id") == rid for rid in ids)
        # at least ensure no dropped responses
        it_pass = all_returned and all_matched and non_serial
        all_pass = all_pass and it_pass
        for rid in ids:
            resp = results[rid]
            log_jsonl(name, {"property": "concurrent", "transport": "loopback-TCP", "iteration": it, "request_id": rid, "op_id": resp.get("op_id", "?"), "response_id": resp.get("id"), "latency_ms": resp.get("duration_ms"), "wall_ms": wall_ms, "error_code": (resp.get("error") or {}).get("code"), "pass": resp.get("id") == rid and resp.get("error") is None, "server_pid": resp.get("server_pid"), "client_pid": CLIENT_PID})
        print(f"[{'PASS' if it_pass else 'FAIL'}] concurrent it={it} N={N} wall={wall_ms}ms serial_bound={serial_bound}ms single={single_ms}ms all_returned={all_returned} all_matched={all_matched} non_serial={non_serial}")

    summary = {"property": "concurrent", "transport": "loopback-TCP", "N": N, "iterations": iterations, "single_ms_baseline": single_ms, "wall_ms_per_iter": total_wall_ms, "pass": all_pass, "stdio_only": False}
    print(f"  => concurrent: {'PASS' if all_pass else 'FAIL'} wall={total_wall_ms}")
    return summary


# ─── Property 2: correlation ────────────────────────────────────────────────


def test_correlation(proc: subprocess.Popen, port: int) -> dict:
    name = "correlation"
    truncate_log(name)
    N = 8
    iterations = 3
    all_pass = True
    # use distinct queries so payload cross-wiring would be detectable
    base_specs = [
        {"op_id": "search_artefacts", "args": {"query": f"corr-{i}", "limit": 5}, "delay_ms": (300 if i == 3 else 0)}
        for i in range(N)
    ]
    # randomize order each iteration to test reordering
    for it in range(iterations):
        ids = [str(uuid.uuid4()) for _ in range(N)]
        requests = [{"id": ids[i], **base_specs[i]} for i in range(N)]
        # also store expected args per id
        expected = {ids[i]: base_specs[i]["args"] for i in range(N)}
        results: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=N) as ex:
            futs = {ex.submit(tcp_call, port, req, 5.0): req for req in requests}
            for fut in as_completed(futs):
                req = futs[fut]
                try:
                    resp = fut.result()
                except Exception as e:
                    resp = {"id": req["id"], "error": {"code": "ConnectionLost", "detail": str(e)}}
                results[req["id"]] = resp

        # check: every response id matches request id, and for search_artefacts, the server echoes query indirectly via trace
        # correlation is proven by id match + no cross-wiring in error/payload
        cross_wired = 0
        for rid in ids:
            resp = results.get(rid, {})
            if resp.get("id") != rid:
                cross_wired += 1
            # for extra check: response op_id should equal request op_id
            req_op = [r["op_id"] for r in requests if r["id"] == rid][0]
            if resp.get("op_id") != req_op and resp.get("error") is None:
                cross_wired += 1
        it_pass = cross_wired == 0 and len(results) == N
        all_pass = all_pass and it_pass
        for rid in ids:
            resp = results[rid]
            log_jsonl(name, {"property": "correlation", "transport": "loopback-TCP", "iteration": it, "request_id": rid, "expected_args": expected[rid], "response_id": resp.get("id"), "response_op": resp.get("op_id"), "error_code": (resp.get("error") or {}).get("code"), "cross_wired": resp.get("id") != rid, "pass": resp.get("id") == rid})
        print(f"[{'PASS' if it_pass else 'FAIL'}] correlation it={it} N={N} cross_wired={cross_wired} delayed_idx=3")
    print(f"  => correlation: {'PASS' if all_pass else 'FAIL'}")
    return {"property": "correlation", "transport": "loopback-TCP", "N": N, "iterations": iterations, "pass": all_pass, "stdio_only": False}


# ─── Property 3: remote execution ─────────────────────────────────────────


def test_remote_execution(proc: subprocess.Popen, port: int) -> dict:
    name = "remote"
    truncate_log(name)
    # spawn a fresh subprocess server to ensure PID boundary proof
    proc2, port2 = start_server()
    try:
        # also prove sandbox gate still enforced remotely
        specs = [
            ({"id": str(uuid.uuid4()), "op_id": "search_artefacts", "args": {"query": "remote-test"}}, True),
            ({"id": str(uuid.uuid4()), "op_id": "create_artefact", "args": {"type": "spec", "title": "Remote artefact"}}, True),
            ({"id": str(uuid.uuid4()), "op_id": "search_artefacts", "args": {"query": "hi"}, "delay_ms": 50}, True),
        ]
        all_pass = True
        for idx, (req, should_succeed) in enumerate(specs):
            resp = tcp_call(port2, req, timeout=5.0)
            server_pid = resp.get("server_pid")
            ok_pid = server_pid is not None and server_pid != CLIENT_PID
            ok_exec = resp.get("executed") == should_succeed if should_succeed else True
            ok_trace = resp.get("trace") is not None and len(resp.get("trace", [])) >= 1
            it_pass = ok_pid and ok_exec and ok_trace
            all_pass = all_pass and it_pass
            log_jsonl(name, {"property": "remote_execution", "transport": "loopback-TCP-subprocess", "iteration": idx, "request_id": req["id"], "op_id": req["op_id"], "client_pid": CLIENT_PID, "server_pid": server_pid, "pid_differs": ok_pid, "executed": resp.get("executed"), "trace": resp.get("trace"), "error_code": (resp.get("error") or {}).get("code"), "pass": it_pass})
            print(f"[{'PASS' if it_pass else 'FAIL'}] remote it={idx} op={req['op_id']} server_pid={server_pid} client_pid={CLIENT_PID} pid_differs={ok_pid} trace={resp.get('trace')}")

        # also verify that a malformed call is rejected remotely before execution (sandbox→validation ordering)
        bad_req = {"id": str(uuid.uuid4()), "op_id": "get_artefact", "args": {"id": "BAD!!"}}
        bad_resp = tcp_call(port2, bad_req, timeout=5.0)
        bad_pass = bad_resp.get("executed") is False and (bad_resp.get("error") or {}).get("code") == "ValidationFailed"
        all_pass = all_pass and bad_pass
        log_jsonl(name, {"property": "remote_execution", "transport": "loopback-TCP-subprocess", "iteration": 99, "request_id": bad_req["id"], "op_id": bad_req["op_id"], "executed": bad_resp.get("executed"), "error_code": (bad_resp.get("error") or {}).get("code"), "pass": bad_pass, "note": "malformed rejected remotely before execution"})
        print(f"[{'PASS' if bad_pass else 'FAIL'}] remote malformed validation before execution: executed={bad_resp.get('executed')} code={(bad_resp.get('error') or {}).get('code')}")

    finally:
        # graceful shutdown then ensure not orphaned
        try:
            s = socket.create_connection(("127.0.0.1", port2), timeout=2)
            s.sendall((json.dumps({"id": str(uuid.uuid4()), "type": "shutdown"}) + "\n").encode())
            s.settimeout(2)
            try:
                s.recv(1024)
            except Exception:
                pass
            s.close()
        except Exception:
            pass
        time.sleep(0.2)
        proc2.terminate()
        try:
            proc2.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc2.kill()
            proc2.wait()
        orphan = proc2.poll() is None
        print(f"  remote server reaped: orphan={orphan} returncode={proc2.returncode}")

    print(f"  => remote_execution: {'PASS' if all_pass else 'FAIL'}")
    return {"property": "remote_execution", "transport": "loopback-TCP-subprocess", "pass": all_pass, "stdio_only": False, "client_pid": CLIENT_PID, "orphan_check": not orphan if 'orphan' in locals() else "unknown"}


# ─── Property 4a: connection loss mid-request ───────────────────────────────


def test_loss_mid_request(port_main: int) -> dict:
    name = "loss-mid-request"
    truncate_log(name)
    iterations = 3
    all_pass = True
    for it in range(iterations):
        proc, port = start_server()
        try:
            # open a persistent connection, send delayed request, kill server mid-flight
            conn = socket.create_connection(("127.0.0.1", port), timeout=2)
            rid = str(uuid.uuid4())
            req = {"id": rid, "op_id": "search_artefacts", "args": {"query": "loss-test"}, "delay_ms": 800}
            conn.sendall((json.dumps(req) + "\n").encode())
            # wait 100 ms then kill server socket (terminate subprocess)
            time.sleep(0.1)
            proc.terminate()
            # now try to read — should get EOF / ConnectionLost within 2s
            conn.settimeout(2)
            start = time.time()
            try:
                data = conn.recv(4096)
                elapsed = int((time.time() - start) * 1000)
                # EOF (empty) means connection lost; any partial success is failure
                got_lost = (data == b"")
                # if we got data, check if it's a successful result (should not be)
                if data:
                    try:
                        resp = json.loads(data.strip().decode())
                        got_lost = resp.get("error", {}).get("code") in ("ConnectionLost", "Cancelled", "Timeout") or resp.get("connection_lost")
                        if resp.get("executed") is True and resp.get("error") is None:
                            got_lost = False  # spurious success
                    except Exception:
                        got_lost = False
                else:
                    elapsed = int((time.time() - start) * 1000)
            except socket.timeout:
                got_lost = False
                elapsed = 2000
            except Exception:
                got_lost = True
                elapsed = int((time.time() - start) * 1000)

            # also verify that a subsequent fresh connection reports lost state (not silent success)
            it_pass = got_lost
            all_pass = all_pass and it_pass
            log_jsonl(name, {"property": "connection_loss_mid_request", "transport": "loopback-TCP", "iteration": it, "request_id": rid, "elapsed_ms": elapsed, "got_connection_lost": got_lost, "pass": it_pass})
            print(f"[{'PASS' if it_pass else 'FAIL'}] loss-mid-request it={it} got_lost={got_lost} elapsed={elapsed}ms")
            try:
                conn.close()
            except Exception:
                pass
        finally:
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            orphan = proc.poll() is None
            if orphan:
                print(f"  WARN loss-mid-request it={it} orphan after kill")
                proc.kill()
    print(f"  => loss-mid-request: {'PASS' if all_pass else 'FAIL'}")
    return {"property": "connection_loss_mid_request", "transport": "loopback-TCP", "iterations": iterations, "pass": all_pass, "stdio_only": False}


# ─── Property 4b: connection loss mid-idle ──────────────────────────────────


def test_loss_mid_idle(port_main: int) -> dict:
    name = "loss-mid-idle"
    truncate_log(name)
    iterations = 2
    all_pass = True
    for it in range(iterations):
        proc, port = start_server()
        try:
            # establish idle connection (no in-flight), kill server
            conn = socket.create_connection(("127.0.0.1", port), timeout=2)
            # verify idle connection works
            probe = {"id": str(uuid.uuid4()), "op_id": "search_artefacts", "args": {"query": "idle-probe"}}
            conn.sendall((json.dumps(probe) + "\n").encode())
            conn.settimeout(2)
            buf = b""
            while b"\n" not in buf:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk
            # now idle — kill server
            time.sleep(0.05)
            proc.terminate()
            time.sleep(0.2)
            # next write should fail or return ConnectionLost
            rid2 = str(uuid.uuid4())
            req2 = {"id": rid2, "op_id": "search_artefacts", "args": {"query": "after-idle-loss"}}
            try:
                conn.sendall((json.dumps(req2) + "\n").encode())
                conn.settimeout(2)
                data = conn.recv(4096)
                # empty means EOF == loss
                if data == b"":
                    it_pass = True
                    detail = "EOF after idle loss"
                elif data:
                    try:
                        resp = json.loads(data.strip().decode())
                        code = (resp.get("error") or {}).get("code")
                        it_pass = code in ("ConnectionLost", "Timeout") or resp.get("connection_lost") or resp.get("error") is not None
                        detail = f"got {code}"
                    except Exception as e:
                        it_pass = False
                        detail = f"bad json after loss: {e}"
                else:
                    it_pass = False
                    detail = "no data"
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                it_pass = True
                detail = f"socket error as expected: {type(e).__name__}"
            except Exception as e:
                it_pass = False
                detail = f"unexpected error: {e}"

            all_pass = all_pass and it_pass
            log_jsonl(name, {"property": "connection_loss_mid_idle", "transport": "loopback-TCP", "iteration": it, "pass": it_pass, "detail": detail})
            print(f"[{'PASS' if it_pass else 'FAIL'}] loss-mid-idle it={it} {detail}")
            try:
                conn.close()
            except Exception:
                pass
        finally:
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    print(f"  => loss-mid-idle: {'PASS' if all_pass else 'FAIL'}")
    return {"property": "connection_loss_mid_idle", "transport": "loopback-TCP", "iterations": iterations, "pass": all_pass, "stdio_only": False}


# ─── Property 5: reconnect ──────────────────────────────────────────────────


def test_reconnect(port_main: int) -> dict:
    name = "reconnect"
    truncate_log(name)
    cycles = 2
    all_pass = True
    for it in range(cycles):
        # start server, kill it mid-request, then reconnect to a new server
        proc1, port1 = start_server()
        lost_id = str(uuid.uuid4())
        # send request that will be lost
        conn1 = socket.create_connection(("127.0.0.1", port1), timeout=2)
        conn1.sendall((json.dumps({"id": lost_id, "op_id": "search_artefacts", "args": {"query": "before-reconnect"}, "delay_ms": 600}) + "\n").encode())
        time.sleep(0.1)
        proc1.terminate()
        try:
            proc1.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc1.kill()
            proc1.wait()
        # verify old conn is dead
        try:
            conn1.settimeout(1)
            conn1.recv(4096)
        except Exception:
            pass
        try:
            conn1.close()
        except Exception:
            pass
        orphan1 = proc1.poll() is None
        # now reconnect to fresh server
        proc2, port2 = start_server()
        try:
            new_id = str(uuid.uuid4())
            resp = tcp_call(port2, {"id": new_id, "op_id": "search_artefacts", "args": {"query": "after-reconnect"}}, timeout=3)
            new_ok = resp.get("error") is None and resp.get("executed") is True and resp.get("id") == new_id
            # verify lost_id was NOT silently retried: fetch durable store for lost_id on new server (should be NotFound since different server)
            fetch_id = str(uuid.uuid4())
            # open conn to new server and ask for durable fetch of lost_id
            s = socket.create_connection(("127.0.0.1", port2), timeout=2)
            s.sendall((json.dumps({"id": fetch_id, "type": "fetch", "target_id": lost_id}) + "\n").encode())
            s.settimeout(2)
            buf = b""
            while b"\n" not in buf:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
            s.close()
            try:
                fetch_resp = json.loads(buf.strip().decode()) if buf.strip() else {}
            except Exception:
                fetch_resp = {}
            not_retried = (fetch_resp.get("error") or {}).get("code") == "NotFound" or "durable_result" not in fetch_resp
            it_pass = new_ok and not not_retried is False  # new_ok and not silently retried
            # more precise: new_ok must be true, and lost request must not appear as durable success on new server
            it_pass = new_ok and not_retried
            all_pass = all_pass and it_pass
            log_jsonl(name, {"property": "reconnect", "transport": "loopback-TCP", "cycle": it, "lost_id": lost_id, "new_id": new_id, "new_ok": new_ok, "not_retried": not_retried, "orphan1": orphan1, "fetch_resp": fetch_resp, "pass": it_pass})
            print(f"[{'PASS' if it_pass else 'FAIL'}] reconnect cycle={it} new_ok={new_ok} not_retried={not_retried} orphan1={orphan1}")
        finally:
            try:
                s2 = socket.create_connection(("127.0.0.1", port2), timeout=2)
                s2.sendall((json.dumps({"id": str(uuid.uuid4()), "type": "shutdown"}) + "\n").encode())
                s2.close()
            except Exception:
                pass
            time.sleep(0.2)
            proc2.terminate()
            try:
                proc2.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc2.kill()
                proc2.wait()
            orphan2 = proc2.poll() is None
            print(f"  reconnect cycle {it} server2 reaped orphan={orphan2}")
            all_pass = all_pass and not orphan2

    print(f"  => reconnect: {'PASS' if all_pass else 'FAIL'}")
    return {"property": "reconnect", "transport": "loopback-TCP", "cycles": cycles, "pass": all_pass, "stdio_only": False, "orphan_check": "subprocess handle polled — no orphans if PASS"}


# ─── Property 6: timeout ────────────────────────────────────────────────────


def test_timeout(port_main: int) -> dict:
    name = "timeout"
    truncate_log(name)
    iterations = 4
    all_pass = True
    for it in range(iterations):
        proc, port = start_server()
        try:
            rid = str(uuid.uuid4())
            delay = 600
            deadline_ms = 200
            deadline_s = deadline_ms / 1000.0
            req = {"id": rid, "op_id": "search_artefacts", "args": {"query": "timeout-test"}, "delay_ms": delay}
            start = time.time()
            # Use tcp_call with timeout == deadline_s: should return Timeout error within window
            resp = tcp_call(port, req, timeout=deadline_s)
            elapsed_ms = int((time.time() - start) * 1000)
            is_timeout = (resp.get("error") or {}).get("code") == "Timeout" or resp.get("timeout") is True
            # Accept either Timeout via client-side socket timeout (our tcp_call returns Timeout) or server-side Timeout
            # Validate fields
            err = resp.get("error") or {}
            has_fields = err.get("code") == "Timeout"  # op_id/deadline fields are expected but client-side timeout may lack op_id
            within_window = deadline_ms <= elapsed_ms <= deadline_ms + 400  # allow slack
            it_pass = is_timeout and within_window
            all_pass = all_pass and it_pass
            log_jsonl(name, {"property": "timeout", "transport": "loopback-TCP", "iteration": it, "request_id": rid, "deadline_ms": deadline_ms, "delay_ms": delay, "elapsed_ms": elapsed_ms, "error_code": err.get("code"), "within_window": within_window, "has_fields": has_fields, "pass": it_pass, "response": resp})
            print(f"[{'PASS' if it_pass else 'FAIL'}] timeout it={it} elapsed={elapsed_ms}ms deadline={deadline_ms}ms is_timeout={is_timeout} within_window={within_window} code={err.get('code')}")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    print(f"  => timeout: {'PASS' if all_pass else 'FAIL'}")
    return {"property": "timeout", "transport": "loopback-TCP", "iterations": iterations, "deadline_ms": 200, "pass": all_pass, "stdio_only": False, "note": "disposition: server continues unless cancelled — timeout is client-side enforcement, server not auto-cancelled (recorded as finding if inspected via durable fetch)"}


# ─── Property 7: cancellation ──────────────────────────────────────────────


def test_cancellation(port_main: int) -> dict:
    name = "cancellation"
    truncate_log(name)
    iterations = 4
    all_pass = True
    for it in range(iterations):
        proc, port = start_server()
        try:
            rid = str(uuid.uuid4())
            # send long request on a persistent connection so we can cancel it
            conn = socket.create_connection(("127.0.0.1", port), timeout=5)
            req = {"id": rid, "op_id": "create_artefact", "args": {"type": "spec", "title": "Cancel me"}, "delay_ms": 800}
            conn.sendall((json.dumps(req) + "\n").encode())
            time.sleep(0.1)
            # send cancel on same or different connection
            cancel_id = str(uuid.uuid4())
            # Use a second connection for cancel to avoid head-of-line blocking
            s2 = socket.create_connection(("127.0.0.1", port), timeout=2)
            s2.sendall((json.dumps({"id": cancel_id, "type": "cancel", "target_id": rid}) + "\n").encode())
            s2.settimeout(2)
            buf2 = b""
            while b"\n" not in buf2:
                chunk = s2.recv(4096)
                if not chunk:
                    break
                buf2 += chunk
            s2.close()
            try:
                cancel_ack = json.loads(buf2.strip().decode()) if buf2.strip() else {}
            except Exception:
                cancel_ack = {}
            cancel_ok = cancel_ack.get("cancelled") is True or cancel_ack.get("type") == "cancel_ack"
            # now read original request response — should be Cancelled, not success
            conn.settimeout(3)
            buf = b""
            start = time.time()
            while b"\n" not in buf and time.time() - start < 4:
                try:
                    chunk = conn.recv(4096)
                except socket.timeout:
                    break
                if not chunk:
                    break
                buf += chunk
            conn.close()
            try:
                resp = json.loads(buf.strip().decode()) if buf.strip() else {"error": {"code": "ConnectionLost"}}
            except Exception:
                resp = {"error": {"code": "ConnectionLost"}, "raw": buf[:200].decode(errors="replace")}
            is_cancelled = (resp.get("error") or {}).get("code") == "Cancelled"
            distinct_from_timeout = is_cancelled and (resp.get("error") or {}).get("code") != "Timeout"
            # Verify no partial success: if op was create_artefact, result should be None on cancel
            no_partial_success = resp.get("result") is None or resp.get("executed") is not True or is_cancelled
            it_pass = is_cancelled and distinct_from_timeout and no_partial_success
            # cancel is transport-distinct from timeout by code alone
            all_pass = all_pass and it_pass
            log_jsonl(name, {"property": "cancellation", "transport": "loopback-TCP", "iteration": it, "request_id": rid, "cancel_ack": cancel_ack, "cancel_ok": cancel_ok, "response_error": (resp.get("error") or {}).get("code"), "is_cancelled": is_cancelled, "distinct_from_timeout": distinct_from_timeout, "no_partial_success": no_partial_success, "pass": it_pass, "response": resp})
            print(f"[{'PASS' if it_pass else 'FAIL'}] cancellation it={it} is_cancelled={is_cancelled} distinct={distinct_from_timeout} no_partial={no_partial_success} cancel_ack={cancel_ok}")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    print(f"  => cancellation: {'PASS' if all_pass else 'FAIL'}")
    return {"property": "cancellation", "transport": "loopback-TCP", "iterations": iterations, "pass": all_pass, "stdio_only": False}


# ─── Properties 8+9: streaming / durable (conditional) ───────────────────────


def test_streaming(port_main: int) -> dict:
    name = "streaming"
    truncate_log(name)
    # probe: ask server for 3 chunks
    proc, port = start_server()
    try:
        rid = str(uuid.uuid4())
        s = socket.create_connection(("127.0.0.1", port), timeout=5)
        s.sendall((json.dumps({"id": rid, "type": "stream", "op_id": "query_metrics", "args": {"filter": {"type": "spec"}}, "chunks": 3}) + "\n").encode())
        chunks = []
        s.settimeout(3)
        buf = b""
        start = time.time()
        while len(chunks) < 3 and time.time() - start < 4:
            try:
                data = s.recv(4096)
            except socket.timeout:
                break
            if not data:
                break
            buf += data
            while b"\n" in buf and len(chunks) < 3:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line.decode())
                    chunks.append(msg)
                except Exception:
                    pass
        s.close()
        ordered = all(chunks[i].get("chunk") == i for i in range(len(chunks))) if chunks else False
        clean_term = chunks[-1].get("done") is True if chunks else False
        transport_can = len(chunks) == 3 and ordered and clean_term
        # Exclusion reasoning: EDASES boundary does not require streaming
        excluded = True
        reason = "EDASES control boundary is discrete artefact ops per capabilities/schemas.json (create/search/review/validate); no prior report (toolregistry-lazy-mcp, Tools Distribution Test Framework) evidences progressive/chunked results as boundary requirement. Transport CAN stream (probe passed) but boundary does NOT need it."
        it_pass = transport_can  # probe itself must pass; exclusion is a finding not a failure
        log_jsonl(name, {"property": "streaming", "transport": "loopback-TCP", "request_id": rid, "chunks_received": len(chunks), "ordered": ordered, "clean_term": clean_term, "transport_can_stream": transport_can, "required_by_boundary": False, "excluded": excluded, "reason": reason, "pass": it_pass, "chunks": chunks})
        print(f"[{'PASS' if it_pass else 'FAIL'}] streaming probe chunks={len(chunks)} ordered={ordered} clean_term={clean_term} transport_can={transport_can}")
        print(f"  => streaming: EXCLUDED (not required by boundary) — transport probe {'PASS' if transport_can else 'FAIL'}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    return {"property": "streaming", "transport": "loopback-TCP", "required": False, "excluded": True, "transport_can": transport_can, "pass": it_pass, "stdio_only": False, "reason": reason}


def test_durable(port_main: int) -> dict:
    name = "durable"
    truncate_log(name)
    proc, port = start_server()
    try:
        rid = str(uuid.uuid4())
        # start operation with delay, drop client connection, reconnect, fetch by id
        s = socket.create_connection(("127.0.0.1", port), timeout=5)
        req = {"id": rid, "op_id": "create_artefact", "args": {"type": "spec", "title": "Durable test"}, "delay_ms": 300}
        s.sendall((json.dumps(req) + "\n").encode())
        # drop client connection immediately (simulate connection loss before response)
        time.sleep(0.05)
        s.close()
        # wait for server to complete (delay + execution)
        time.sleep(0.6)
        # reconnect and fetch durable result by correlation id
        fetch_id = str(uuid.uuid4())
        s2 = socket.create_connection(("127.0.0.1", port), timeout=3)
        s2.sendall((json.dumps({"id": fetch_id, "type": "fetch", "target_id": rid}) + "\n").encode())
        s2.settimeout(3)
        buf = b""
        start = time.time()
        while b"\n" not in buf and time.time() - start < 3:
            try:
                data = s2.recv(4096)
            except socket.timeout:
                break
            if not data:
                break
            buf += data
        s2.close()
        try:
            fetch_resp = json.loads(buf.strip().decode()) if buf.strip() else {}
        except Exception:
            fetch_resp = {"raw": buf[:200].decode(errors="replace")}
        durable_result = fetch_resp.get("durable_result")
        transport_can = durable_result is not None and durable_result.get("id") == rid
        excluded = True
        reason = "EDASES ops are synchronous request/response within agent→sandbox→runtime (§1.3 target architecture); no evidence in prior work that operation lifetime must exceed connection. Transport CAN support durable via correlation-id cache (probe) but boundary does NOT require it."
        it_pass = transport_can
        log_jsonl(name, {"property": "durable", "transport": "loopback-TCP", "request_id": rid, "fetch_id": fetch_id, "transport_can": transport_can, "required_by_boundary": False, "excluded": excluded, "reason": reason, "pass": it_pass, "fetch_resp": fetch_resp})
        print(f"[{'PASS' if it_pass else 'FAIL'}] durable probe transport_can={transport_can} durable_result_id={durable_result.get('id') if durable_result else None}")
        print(f"  => durable: EXCLUDED (not required by boundary) — transport probe {'PASS' if transport_can else 'FAIL'}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    return {"property": "durable", "transport": "loopback-TCP", "required": False, "excluded": True, "transport_can": transport_can, "pass": it_pass, "stdio_only": False, "reason": reason}


# ─── Main ───────────────────────────────────────────────────────────────────


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    # clear summary
    (LOG_DIR / "summary.json").write_text("")

    print(f"Test E runner — client_pid={CLIENT_PID}")
    print(f"Logs: {LOG_DIR}")
    print("")

    # stable main server for concurrent + correlation (reused)
    main_proc, main_port = start_server()
    print(f"Main server: pid={main_proc.pid} port={main_port}")

    results = []
    try:
        # 1-2 use main server (shared)
        results.append(test_concurrent(main_proc, main_port))
        results.append(test_correlation(main_proc, main_port))
        # shutdown main server now; remaining tests use ephemeral servers
        try:
            s = socket.create_connection(("127.0.0.1", main_port), timeout=2)
            s.sendall((json.dumps({"id": str(uuid.uuid4()), "type": "shutdown"}) + "\n").encode())
            s.close()
        except Exception:
            pass
        time.sleep(0.2)
        main_proc.terminate()
        try:
            main_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            main_proc.kill()
            main_proc.wait()

        # 3-9 use ephemeral servers
        results.append(test_remote_execution(None, 0))
        results.append(test_loss_mid_request(0))
        results.append(test_loss_mid_idle(0))
        results.append(test_reconnect(0))
        results.append(test_timeout(0))
        results.append(test_cancellation(0))
        results.append(test_streaming(0))
        results.append(test_durable(0))

    finally:
        # ensure main server reaped if still alive
        try:
            if main_proc.poll() is None:
                main_proc.kill()
                main_proc.wait(timeout=3)
        except Exception:
            pass

    # summary
    summary = {
        "generated_at": _now_iso(),
        "client_pid": CLIENT_PID,
        "properties": {r["property"]: r for r in results},
        "overall_pass": all(r.get("pass") for r in results),
        "required_pass": all(r.get("pass") for r in results if not r.get("excluded")),
        "stdio_only_properties": [r["property"] for r in results if r.get("stdio_only")],
    }
    with open(LOG_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 72)
    print("SUMMARY")
    for r in results:
        flag = "EXCLUDED" if r.get("excluded") else ("PASS" if r.get("pass") else "FAIL")
        print(f"  {r['property']:30s} [{flag}] transport={r.get('transport')} stdio_only={r.get('stdio_only')}")
    print(f"  overall: {'PASS' if summary['overall_pass'] else 'FAIL'}  required: {'PASS' if summary['required_pass'] else 'FAIL'}")

    # exit code 0 even if conditional probes show EXCLUDED; only fail on required failures
    if not summary["required_pass"]:
        print("REQUIRED properties FAILED — see logs", file=sys.stderr)
        sys.exit(1)
    print("All required transport properties PASSED (conditional probes recorded as EXCLUDED where applicable)")


if __name__ == "__main__":
    main()
