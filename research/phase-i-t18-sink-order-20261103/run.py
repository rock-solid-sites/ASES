#!/usr/bin/env python3
"""Bounded loopback probe for T18 sink-side currentness ordering."""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import platform
import select
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class SinkState:
    def __init__(self, mode: str, journal: Path):
        self.mode = mode
        self.journal = journal
        self.lock = threading.Lock()
        self.gate = threading.Event()
        self.version = 1
        self.waiting = 0
        self.events: list[dict[str, Any]] = []
        self.effects: list[dict[str, Any]] = []
        self.obligations: dict[str, str] = {}
        if mode == "f4" and journal.exists():
            for line in journal.read_bytes().splitlines():
                event = json.loads(line)
                self.events.append(event)
                if event.get("event") == "effect_accepted":
                    self.effects.append(event)

    def emit_locked(self, name: str, **fields: Any) -> dict[str, Any]:
        event = {"seq": len(self.events) + 1, "event": name, **fields}
        self.events.append(event)
        if name in ("effect_accepted", "obligation_committed", "authority_replaced"):
            self.journal.parent.mkdir(parents=True, exist_ok=True)
            payload = (json.dumps(event, sort_keys=True) + "\n").encode()
            fd = os.open(self.journal, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                os.write(fd, payload)
                os.fsync(fd)
            finally:
                os.close(fd)
        if name == "effect_accepted":
            self.effects.append(event)
        return event


def make_handler(state: SinkState):
    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, _format: str, *_args: Any) -> None:
            return

        def send_json(self, status: int, data: dict[str, Any]) -> None:
            body = json.dumps(data, sort_keys=True).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()

        def read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length))

        def do_GET(self) -> None:  # noqa: N802
            if self.path != "/status":
                self.send_json(404, {"error": "unknown route"})
                return
            with state.lock:
                data = {
                    "authority_version": state.version,
                    "waiting": state.waiting,
                    "events": list(state.events),
                    "effects": list(state.effects),
                }
            self.send_json(200, data)

        def do_POST(self) -> None:  # noqa: N802
            try:
                data = self.read_json()
            except Exception as exc:
                self.send_json(400, {"error": f"invalid json: {type(exc).__name__}"})
                return

            if self.path == "/submit":
                token = int(data["authority_version"])
                request_id = str(data["request_id"])
                payload = str(data["payload"])
                hold = bool(data.get("hold", False))
                if state.mode == "detached-check":
                    with state.lock:
                        authorized = token == state.version
                        state.emit_locked(
                            "detached_permission_read",
                            request_id=request_id,
                            presented_version=token,
                            observed_version=state.version,
                            allowed=authorized,
                        )
                        if not authorized:
                            state.emit_locked("sink_rejected", request_id=request_id, reason="stale detached check")
                            self.send_json(409, {"outcome": "rejected"})
                            return
                        if hold:
                            state.waiting += 1
                            state.emit_locked("request_held", request_id=request_id, mode=state.mode)
                    if hold and not state.gate.wait(4.0):
                        with state.lock:
                            state.waiting -= 1
                            state.emit_locked("request_timeout", request_id=request_id)
                        self.send_json(504, {"outcome": "timeout"})
                        return
                    with state.lock:
                        if hold:
                            state.waiting -= 1
                        event = state.emit_locked(
                            "effect_accepted",
                            request_id=request_id,
                            payload=payload,
                            presented_version=token,
                            accepted_under_version=state.version,
                            check_mode=state.mode,
                        )
                    self.send_json(201, {"outcome": "accepted", "event_seq": event["seq"]})
                    return

                if hold:
                    with state.lock:
                        state.waiting += 1
                        state.emit_locked("request_held", request_id=request_id, mode=state.mode)
                    if not state.gate.wait(4.0):
                        with state.lock:
                            state.waiting -= 1
                            state.emit_locked("request_timeout", request_id=request_id)
                        self.send_json(504, {"outcome": "timeout"})
                        return

                with state.lock:
                    if hold:
                        state.waiting -= 1
                    if token != state.version:
                        state.emit_locked(
                            "sink_rejected",
                            request_id=request_id,
                            reason="authority changed before sink acceptance",
                            presented_version=token,
                            current_version=state.version,
                        )
                        self.send_json(409, {"outcome": "rejected"})
                        return
                    event = state.emit_locked(
                        "effect_accepted",
                        request_id=request_id,
                        payload=payload,
                        presented_version=token,
                        accepted_under_version=state.version,
                        check_mode=state.mode,
                    )
                self.send_json(201, {"outcome": "accepted", "event_seq": event["seq"]})
                return

            if self.path == "/replace":
                with state.lock:
                    previous = state.version
                    state.version += 1
                    state.emit_locked(
                        "authority_replaced",
                        previous_version=previous,
                        current_version=state.version,
                    )
                    new_version = state.version
                state.gate.set()
                self.send_json(200, {"outcome": "replaced", "authority_version": new_version})
                return

            if self.path == "/commit-obligation":
                token = int(data["authority_version"])
                obligation_id = str(data["obligation_id"])
                payload = str(data["payload"])
                with state.lock:
                    if token != state.version:
                        state.emit_locked(
                            "obligation_rejected",
                            obligation_id=obligation_id,
                            presented_version=token,
                            current_version=state.version,
                        )
                        self.send_json(409, {"outcome": "rejected"})
                        return
                    state.obligations[obligation_id] = payload
                    event = state.emit_locked(
                        "obligation_committed",
                        obligation_id=obligation_id,
                        payload=payload,
                        payload_sha256=hashlib.sha256(payload.encode()).hexdigest(),
                        committed_under_version=state.version,
                    )
                self.send_json(201, {"outcome": "committed", "event_seq": event["seq"]})
                return

            if self.path == "/deliver-obligation":
                obligation_id = str(data["obligation_id"])
                with state.lock:
                    if obligation_id not in state.obligations:
                        state.emit_locked("obligation_delivery_rejected", obligation_id=obligation_id)
                        self.send_json(409, {"outcome": "rejected"})
                        return
                    payload = state.obligations[obligation_id]
                    event = state.emit_locked(
                        "effect_accepted",
                        request_id=f"obligation:{obligation_id}",
                        obligation_id=obligation_id,
                        payload=payload,
                        payload_sha256=hashlib.sha256(payload.encode()).hexdigest(),
                        accepted_under_version=state.version,
                        check_mode="committed-exact-obligation",
                    )
                self.send_json(201, {"outcome": "accepted", "event_seq": event["seq"]})
                return

            if self.path == "/effect" and state.mode == "f4":
                request_id = str(data["request_id"])
                payload = str(data["payload"])
                cut = str(data["cut"])
                payload_hash = hashlib.sha256(payload.encode()).hexdigest()
                if cut == "preaccept":
                    with state.lock:
                        state.waiting += 1
                        state.emit_locked("request_waiting_before_accept", request_id=request_id)
                    state.gate.wait(30.0)
                    self.send_json(201, {"outcome": "accepted"})
                    return
                if cut == "early_ack":
                    with state.lock:
                        state.waiting += 1
                        state.emit_locked("early_ack_waiting_before_accept", request_id=request_id)
                    self.send_json(201, {"outcome": "accepted"})
                    state.gate.wait(30.0)
                    return
                with state.lock:
                    event = state.emit_locked(
                        "effect_accepted",
                        request_id=request_id,
                        payload=payload,
                        payload_utf8_hex=payload.encode().hex(),
                        payload_sha256=payload_hash,
                        acceptance_boundary="journal append + fsync returned",
                    )
                    if cut == "after_accept_before_ack":
                        state.waiting += 1
                        state.emit_locked("accepted_waiting_before_ack", request_id=request_id,
                                          accepted_event_seq=event["seq"])
                if cut == "after_accept_before_ack":
                    state.gate.wait(30.0)
                self.send_json(201, {"outcome": "accepted", "event_seq": event["seq"]})
                return

            self.send_json(404, {"error": "unknown route"})

    return Handler


def serve(mode: str, journal: Path) -> int:
    state = SinkState(mode, journal)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
    server.daemon_threads = True
    print(json.dumps({"ready": True, "port": server.server_address[1]}), flush=True)
    try:
        server.serve_forever(poll_interval=0.05)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def call(port: int, method: str, path: str, data: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    body = None if data is None else json.dumps(data).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=body, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=2.0) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


class RunningSink:
    def __init__(self, mode: str, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.journal = root / "sink-effects.jsonl"
        self.process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--server", mode, str(self.journal)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        assert self.process.stdout is not None
        readable, _, _ = select.select([self.process.stdout], [], [], 3.0)
        ready_line = self.process.stdout.readline().strip() if readable else ""
        if not ready_line:
            if self.process.poll() is None:
                self.process.kill()
                self.process.wait(timeout=2.0)
            error = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"sink did not become ready: {error}")
        ready = json.loads(ready_line)
        self.port = int(ready["port"])

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2.0)

    def kill_and_reap(self) -> int:
        if self.process.poll() is None:
            self.process.kill()
        result = self.process.wait(timeout=2.0)
        if self.process.stdout:
            self.process.stdout.close()
        if self.process.stderr:
            self.process.stderr.close()
        return result

    def __enter__(self) -> "RunningSink":
        return self

    def __exit__(self, _type: Any, _value: Any, _tb: Any) -> None:
        self.close()


def wait_for_waiter(sink: RunningSink) -> dict[str, Any]:
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        status, data = call(sink.port, "GET", "/status")
        if status == 200 and data["waiting"] == 1:
            return data
        time.sleep(0.01)
    raise RuntimeError(f"held request did not reach sink: {data}")


def latest_status(sink: RunningSink) -> dict[str, Any]:
    status, data = call(sink.port, "GET", "/status")
    if status != 200:
        raise RuntimeError(f"sink status failed: {status} {data}")
    return data


def run_experiment(output: Path) -> dict[str, Any]:
    scenarios: dict[str, Any] = {}
    assertions: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="ases-t18-") as temp_name:
        root = Path(temp_name)
        with RunningSink("sink-ordered", root / "ordered") as sink:
            live = call(sink.port, "POST", "/submit", {
                "authority_version": 1, "request_id": "live-v1", "payload": "x-live",
            })
            committed = call(sink.port, "POST", "/commit-obligation", {
                "authority_version": 1, "obligation_id": "q-1", "payload": "x-exact-obligation",
            })
            delayed_result: list[tuple[int, dict[str, Any]]] = []
            delayed_error: list[str] = []

            def send_delayed() -> None:
                try:
                    delayed_result.append(call(sink.port, "POST", "/submit", {
                        "authority_version": 1, "request_id": "stale-v1", "payload": "x-stale", "hold": True,
                    }))
                except Exception as exc:  # captured for an explicit inconclusive result
                    delayed_error.append(f"{type(exc).__name__}: {exc}")

            worker = threading.Thread(target=send_delayed, name="delayed-old-request", daemon=True)
            worker.start()
            wait_for_waiter(sink)
            replacement = call(sink.port, "POST", "/replace", {})
            worker.join(timeout=3.0)
            if worker.is_alive():
                raise RuntimeError("ordered delayed request did not finish")
            new_current = call(sink.port, "POST", "/submit", {
                "authority_version": 2, "request_id": "live-v2", "payload": "x-new-current",
            })
            exact_delivery = call(sink.port, "POST", "/deliver-obligation", {"obligation_id": "q-1"})
            status = latest_status(sink)
            scenarios["sink_ordered"] = {
                "live_v1": live,
                "obligation_commit_v1": committed,
                "authority_replacement": replacement,
                "delayed_old_v1": delayed_result[0] if delayed_result else None,
                "delayed_old_error": delayed_error,
                "new_current_v2": new_current,
                "exact_obligation_after_replacement": exact_delivery,
                "status": status,
                "journal": sink.journal.read_text().splitlines(),
            }
            event_names = [event["event"] for event in status["events"]]
            replace_seq = next(event["seq"] for event in status["events"] if event["event"] == "authority_replaced")
            stale_reject = next((event for event in status["events"] if event.get("request_id") == "stale-v1" and event["event"] == "sink_rejected"), None)
            delayed_effect = [effect for effect in status["effects"] if effect.get("request_id") == "stale-v1"]
            q_effect = [effect for effect in status["effects"] if effect.get("obligation_id") == "q-1"]
            assertions.update({
                "live_v1_accepted": live[0] == 201,
                "obligation_committed_before_replacement": committed[0] == 201 and replace_seq > 2,
                "replacement_acknowledged": replacement == (200, {"outcome": "replaced", "authority_version": 2}),
                "delayed_v1_rejected_after_replacement": bool(stale_reject and stale_reject["seq"] > replace_seq) and not delayed_effect and (delayed_result and delayed_result[0][0] == 409),
                "new_v2_accepted": new_current[0] == 201,
                "old_exact_obligation_delivered_after_replacement": exact_delivery[0] == 201 and len(q_effect) == 1 and q_effect[0]["payload"] == "x-exact-obligation" and q_effect[0]["accepted_under_version"] == 2,
                "ordered_effect_set_is_live_new_and_precommitted_only": {effect["request_id"] for effect in status["effects"]} == {"live-v1", "live-v2", "obligation:q-1"},
                "event_log_has_replacement_before_stale_denial": "authority_replaced" in event_names and stale_reject is not None,
            })

        with RunningSink("detached-check", root / "detached") as sink:
            result: list[tuple[int, dict[str, Any]]] = []
            errors: list[str] = []

            def send_detached() -> None:
                try:
                    result.append(call(sink.port, "POST", "/submit", {
                        "authority_version": 1, "request_id": "stale-v1-mutant", "payload": "x-stale-mutant", "hold": True,
                    }))
                except Exception as exc:
                    errors.append(f"{type(exc).__name__}: {exc}")

            worker = threading.Thread(target=send_detached, name="detached-check-request", daemon=True)
            worker.start()
            wait_for_waiter(sink)
            replacement = call(sink.port, "POST", "/replace", {})
            worker.join(timeout=3.0)
            if worker.is_alive():
                raise RuntimeError("detached-check delayed request did not finish")
            status = latest_status(sink)
            stale_effects = [effect for effect in status["effects"] if effect.get("request_id") == "stale-v1-mutant"]
            precheck = next((event for event in status["events"] if event["event"] == "detached_permission_read"), None)
            replace_event = next(event for event in status["events"] if event["event"] == "authority_replaced")
            accepted = stale_effects[0] if stale_effects else None
            scenarios["detached_check_mutation"] = {
                "authority_replacement": replacement,
                "delayed_old_v1": result[0] if result else None,
                "delayed_old_error": errors,
                "status": status,
                "journal": sink.journal.read_text().splitlines(),
            }
            assertions["detached_check_mutation_admits_stale_effect_after_replacement"] = bool(
                result and result[0][0] == 201 and precheck and precheck["allowed"]
                and accepted and accepted["seq"] > replace_event["seq"]
                and accepted["presented_version"] == 1 and accepted["accepted_under_version"] == 2
            )

    result = {
        "schema": "ases.phase-i.t18-sink-order-result.v1",
        "source_commit": "8b3c7e06aaab97122d2fcdaf2ee891e62667154b",
        "preregistration_commit": "a4f1c493d943f4e06d0a8ed5f097ecb9c9265ed2",
        "abstract_fixture_ids": [
            "T18-use-current-sink-order-after-revocation",
            "T18-exact-obligation-delivery-after-replacement",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "kernel": platform.release(),
            "host": "loopback-only disposable subprocess; ephemeral TCP port",
            "journal": "temporary JSONL append + fsync per committed effect/obligation/replacement",
        },
        "scenarios": scenarios,
        "assertions": assertions,
        "pass": all(assertions.values()) and len(assertions) == 9,
        "untested": [
            "Landlock/seccomp/SELinux confinement (no host confinement claim)",
            "OS process kill at the acceptance/ack boundary, machine power loss or storage faults",
            "rollback resistance, remote authentication, network intermediaries or arbitrary sinks",
            "multi-sink total ordering, multiple concurrent revocations or unbounded schedules",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "pass": result["pass"], "assertions": assertions}, indent=2, sort_keys=True))
    return result


def client_main(port: int, request_id: str, payload: str, cut: str) -> int:
    try:
        status, body = call(port, "POST", "/effect", {
            "request_id": request_id, "payload": payload, "cut": cut,
        })
        print(json.dumps({"http_status": status, "body": body}, sort_keys=True), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"http_status": None, "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True), flush=True)
        return 0


def recover_main(journal: Path) -> int:
    raw = journal.read_bytes() if journal.exists() else b""
    records: list[dict[str, Any]] = []
    try:
        if raw and not raw.endswith(b"\n"):
            raise ValueError("journal has an unterminated/truncated final record")
        lines = raw.splitlines(keepends=True)
        for index, line in enumerate(lines, start=1):
            if not line.endswith(b"\n"):
                raise ValueError(f"record {index} is incomplete")
            event = json.loads(line)
            if event.get("seq") != index:
                raise ValueError(f"record sequence mismatch at {index}")
            records.append(event)
        effects = []
        for event in records:
            if event.get("event") != "effect_accepted":
                continue
            payload_bytes = bytes.fromhex(event["payload_utf8_hex"])
            payload_hash = hashlib.sha256(payload_bytes).hexdigest()
            if payload_hash != event.get("payload_sha256"):
                raise ValueError(f"payload hash mismatch at record {event['seq']}")
            effects.append({
                "seq": event["seq"],
                "request_id": event["request_id"],
                "payload_base64": __import__("base64").b64encode(payload_bytes).decode(),
                "payload_utf8_hex": payload_bytes.hex(),
                "payload_sha256": payload_hash,
            })
        result = {"ok": True, "journal_bytes": len(raw), "record_count": len(records), "effects": effects}
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "journal_bytes": len(raw), "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True), flush=True)
        return 2


def read_child_json(proc: subprocess.Popen[str], label: str) -> tuple[dict[str, Any], str]:
    try:
        stdout, stderr = proc.communicate(timeout=4.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate(timeout=2.0)
        raise RuntimeError(f"{label} exceeded timeout; stdout={stdout!r} stderr={stderr!r}")
    if not stdout.strip():
        raise RuntimeError(f"{label} produced no result (exit {proc.returncode}): {stderr}")
    return json.loads(stdout.strip().splitlines()[-1]), stderr


def wait_for_event(sink: RunningSink, event_name: str, timeout: float = 2.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last = latest_status(sink)
        if any(event.get("event") == event_name for event in last["events"]):
            return last
        time.sleep(0.01)
    raise RuntimeError(f"sink did not reach {event_name}: {last}")


def cold_recover(journal: Path) -> tuple[dict[str, Any], int, str]:
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--recover", str(journal)],
        text=True, capture_output=True, timeout=4.0,
    )
    if not proc.stdout.strip():
        raise RuntimeError(f"cold recovery produced no output: {proc.stderr}")
    return json.loads(proc.stdout.strip().splitlines()[-1]), proc.returncode, proc.stderr


def run_f4_experiment(output: Path) -> dict[str, Any]:
    scenarios: dict[str, Any] = {}
    assertions: dict[str, bool] = {}
    payload = "phase-i-t18-effect-π\nimmutable payload"
    cases = ("uninterrupted", "preaccept", "accepted_before_ack", "early_ack_mutant")
    with tempfile.TemporaryDirectory(prefix="ases-t18-f4-") as temporary:
        root = Path(temporary)
        for case in cases:
            case_root = root / case
            journal = case_root / "sink-effects.jsonl"
            cut = {
                "uninterrupted": "normal",
                "preaccept": "preaccept",
                "accepted_before_ack": "after_accept_before_ack",
                "early_ack_mutant": "early_ack",
            }[case]
            sink = RunningSink("f4", case_root)
            client = None
            try:
                client = subprocess.Popen(
                    [sys.executable, str(Path(__file__).resolve()), "--client", str(sink.port),
                     f"effect-{case}", payload, cut],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                )
                if case == "uninterrupted":
                    client_result, client_stderr = read_child_json(client, "uninterrupted client")
                    kill_status = sink.kill_and_reap()
                elif case == "preaccept":
                    wait_for_event(sink, "request_waiting_before_accept")
                    kill_status = sink.kill_and_reap()
                    client_result, client_stderr = read_child_json(client, "preaccept client")
                elif case == "accepted_before_ack":
                    wait_for_event(sink, "accepted_waiting_before_ack")
                    kill_status = sink.kill_and_reap()
                    client_result, client_stderr = read_child_json(client, "accepted-before-ack client")
                else:
                    wait_for_event(sink, "early_ack_waiting_before_accept")
                    client_result, client_stderr = read_child_json(client, "early-ack mutant client")
                    kill_status = sink.kill_and_reap()
            finally:
                if client is not None and client.poll() is None:
                    client.kill()
                    client.wait(timeout=2.0)
                if sink.process.poll() is None:
                    sink.kill_and_reap()

            recovered, recovery_status, recovery_stderr = cold_recover(journal)
            scenario = {
                "client_observation": client_result,
                "client_stderr": client_stderr,
                "sink_process_returncode": kill_status,
                "cold_recovery_process_returncode": recovery_status,
                "cold_recovery_stderr": recovery_stderr,
                "recovered": recovered,
                "journal_raw_hex": journal.read_bytes().hex() if journal.exists() else "",
                "journal_sha256": hashlib.sha256(journal.read_bytes() if journal.exists() else b"").hexdigest(),
            }
            scenarios[case] = scenario
            effect_count = len(recovered.get("effects", []))
            expected_ack = case in ("uninterrupted", "early_ack_mutant")
            observed_ack = client_result.get("http_status") == 201
            expected_effect = 0 if case in ("preaccept", "early_ack_mutant") else 1
            effect_valid = effect_count == expected_effect
            exact_payload_valid = all(
                item.get("payload_utf8_hex") == payload.encode().hex()
                and item.get("payload_sha256") == hashlib.sha256(payload.encode()).hexdigest()
                for item in recovered.get("effects", [])
            )
            assertions[f"{case}_ack_observation"] = observed_ack == expected_ack
            assertions[f"{case}_cold_effect_count"] = effect_valid
            assertions[f"{case}_cold_effect_bytes_and_hash"] = exact_payload_valid
            assertions[f"{case}_fresh_recovery_process_succeeded"] = recovery_status == 0 and recovered.get("ok") is True
            assertions[f"{case}_sink_was_killed_and_reaped"] = kill_status == -9

    result = {
        "schema": "ases.phase-i.t18-f4-sink-cut-result.v1",
        "source_commit": "8b3c7e06aaab97122d2fcdaf2ee891e62667154b",
        "t18_experiment_commit": "b631bfae01faff1f32a8f81993386cdc3a36eb63",
        "f4_preregistration_commit": "b7404d7a2a73b2f4dd5e39ffcafaedb29f98f97f",
        "boundary": "sink effect record appended and fsync returned; HTTP success follows",
        "retry_semantics": "No retry was issued after an unknown accepted-before-ACK result; duplicate remains possible under a permissive sink and is not suppressed or ruled out.",
        "payload_reference_sha256": hashlib.sha256(payload.encode()).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "kernel": platform.release(),
            "host": "loopback-only disposable child sink; ephemeral TCP port",
        },
        "scenarios": scenarios,
        "assertions": assertions,
        "pass": all(assertions.values()) and len(assertions) == 20,
        "untested": [
            "retry after ambiguous accepted-before-ACK (documented as duplicate-possible, not run)",
            "power-loss/device-cache durability, kernel crash, filesystem faults, journal corruption/rollback",
            "host confinement, production/F3 sink conformance, remote authentication, arbitrary effects",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "pass": result["pass"], "assertions": assertions}, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--server", nargs=2, metavar=("MODE", "JOURNAL"))
    parser.add_argument("--f4-output", type=Path)
    parser.add_argument("--client", nargs=4, metavar=("PORT", "REQUEST_ID", "PAYLOAD", "CUT"))
    parser.add_argument("--recover", type=Path)
    args = parser.parse_args()
    if args.server:
        return serve(args.server[0], Path(args.server[1]))
    if args.client:
        return client_main(int(args.client[0]), args.client[1], args.client[2], args.client[3])
    if args.recover:
        return recover_main(args.recover)
    if args.f4_output:
        result = run_f4_experiment(args.f4_output)
        return 0 if result["pass"] else 1
    output = args.output or Path("results.json")
    result = run_experiment(output)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
