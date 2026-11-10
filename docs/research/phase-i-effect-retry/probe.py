#!/usr/bin/env python3
"""Native HTTP/process histories for the isolated durable-request retry candidate."""
import argparse
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import select
import socket
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "phase-i-sol-integration/evidence/sources/f4/research/phase-i-t18-sink-order-20261103"
CUT_SOURCE = SOURCES / "published-cut/cut_sink.py"
RUN_SOURCE = SOURCES / "run.py"
CANDIDATE = HERE / "candidate.py"
PROBE_SOURCE = HERE / "probe.py"
ROOT = "phase-i-effect-retry-local-root"
GENESIS = {
    "authority": {"created": False, "granted": False, "active": False,
                  "authority_version": 0, "holder": "old"},
    "journal_sha256": hashlib.sha256(b"").hexdigest(),
}
PROCESSES = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load("retry_pinned_run", RUN_SOURCE)


class Child:
    def __init__(self, argv, env=None):
        task_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        if env:
            task_env.update(env)
        self.meta = {"argv": [str(item) for item in argv], "start_ns": time.monotonic_ns(),
                     "stdout_lines": [], "stderr": ""}
        self.process = subprocess.Popen([str(item) for item in argv], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
                                        env=task_env)
        PROCESSES.append(self)
        self.meta["pid"] = self.process.pid

    def line(self, timeout=5):
        if self.process.stdout is None or not select.select([self.process.stdout], [], [], timeout)[0]:
            raise TimeoutError("child stdout line")
        raw = self.process.stdout.readline(1024 * 1024)
        if not raw:
            raise RuntimeError("child stdout EOF")
        line = raw.decode().strip()
        self.meta["stdout_lines"].append(line)
        return json.loads(line)

    def ready(self):
        record = self.line()
        self.meta["ready"] = record
        return record

    def stop(self, kill=False):
        if self.meta.get("exit_ns") is not None:
            return
        if self.process.poll() is None:
            if kill:
                self.process.kill()
            else:
                self.process.terminate()
        code = self.process.wait(timeout=5)
        stdout_tail = self.process.stdout.read().decode() if self.process.stdout else ""
        stderr = self.process.stderr.read().decode() if self.process.stderr else ""
        self.meta.update(exit=code, exit_ns=time.monotonic_ns(), stdout_tail=stdout_tail,
                         stderr=stderr, killed=kill)


class LossProxy:
    """Local disposable relay that commits at the real witness then drops one reply."""
    def __init__(self, witness_port):
        self.witness_port = witness_port
        self.drop_next_publish = False
        self.log = []
        owner = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"
            def log_message(self, *_args):
                return
            def do_GET(self):
                self._forward("GET")
            def do_POST(self):
                self._forward("POST")
            def _forward(self, method):
                raw = self.rfile.read(int(self.headers.get("Content-Length", "0"))) if method == "POST" else b""
                request = json.loads(raw) if raw else None
                try:
                    status, response = base.call(owner.witness_port, method, self.path, request)
                    event = {"method": method, "path": self.path, "request": request,
                             "upstream_status": status, "upstream_response": response,
                             "start_ns": time.monotonic_ns()}
                    drop = self.path == "/publish" and owner.drop_next_publish
                    if drop:
                        owner.drop_next_publish = False
                        event["response_dropped_after_upstream_commit"] = True
                        owner.log.append(event)
                        self.close_connection = True
                        try:
                            self.connection.shutdown(socket.SHUT_RDWR)
                        except OSError:
                            pass
                        self.connection.close()
                        return
                    body = json.dumps(response, sort_keys=True).encode()
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    self.wfile.flush()
                    event["response_dropped_after_upstream_commit"] = False
                    event["end_ns"] = time.monotonic_ns()
                    owner.log.append(event)
                except Exception as error:
                    owner.log.append({"method": method, "path": self.path,
                                      "error": type(error).__name__, "start_ns": time.monotonic_ns()})
                    self.send_error(502)

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class History:
    def __init__(self, name, root, candidate=True, proxy=False, sink_gate=None):
        self.name = name
        self.path = Path(root)
        self.path.mkdir(parents=True)
        self.journal = self.path / "sink-effects.jsonl"
        self.candidate = candidate
        self.proxy = None
        self.frames = []
        self.children = []
        self.witness = self.start_witness()
        init_req = {"root": ROOT, "nonce": "init-" + name, "cut": GENESIS}
        init_status, init_reply = base.call(self.witness_port, "POST", "/init", init_req)
        self.frames.append({"actor": "probe", "path": "/init", "request": init_req,
                            "status": init_status, "response": init_reply})
        if init_status != 200:
            raise RuntimeError("witness init failed")
        if proxy:
            self.proxy = LossProxy(self.witness_port)
        self.drop_enabled = False
        self.start_sink("fresh", sink_gate)
        self.port = self.sink_ready["port"]
        self.management_setup()

    def start_witness(self):
        proc = Child([sys.executable, "-B", CANDIDATE, "--witness", ROOT])
        self.children.append(proc)
        result = proc.ready()
        self.witness_port = result["port"]
        return proc

    def endpoint(self):
        return self.proxy.port if self.proxy else self.witness_port

    def start_sink(self, mode, gate_name=None):
        executable = CANDIDATE if self.candidate else CUT_SOURCE
        args = [sys.executable, "-B", executable, "--sink", mode, self.journal,
                str(self.endpoint()), "published-cut", ROOT]
        env = {"ASES_RETRY_GATE": gate_name or ""} if self.candidate else None
        proc = Child(args, env)
        self.children.append(proc)
        ready = proc.ready()
        self.sink = proc
        self.sink_ready = ready
        if ready.get("ready") is False:
            return ready
        self.sink_port = ready["port"]
        return ready

    def capture_journal(self):
        raw = self.journal.read_bytes() if self.journal.exists() else b""
        return {"sha256": sha(raw), "raw_hex": raw.hex(), "size": len(raw),
                "events": [json.loads(line) for line in raw.splitlines()]}

    def request(self, path, data=None, method="POST"):
        before = self.capture_journal()
        try:
            status, reply = base.call(self.sink_port, method, path, data)
            error = None
        except Exception as exc:
            status, reply, error = None, None, type(exc).__name__
        after = self.capture_journal()
        frame = {"actor": "probe", "method": method, "path": path, "request": data,
                 "status": status, "response": reply, "transport_error": error,
                 "journal_before_sha256": before["sha256"], "journal_after_sha256": after["sha256"],
                 "journal_before_size": before["size"], "journal_after_size": after["size"],
                 "start_ns": time.monotonic_ns(), "end_ns": time.monotonic_ns()}
        self.frames.append(frame)
        return status, reply, frame

    def management_setup(self):
        for path, data in (("/create", {}), ("/grant", {}),
                           ("/activate", {"authority_version": 1})):
            status, reply, _ = self.request(path, data)
            if status not in (200, 201):
                raise RuntimeError(f"management setup failed: {path} {status} {reply}")

    def submit(self, request_id, payload, token=1):
        return self.request("/submit", {"request_id": request_id, "payload": payload,
                                         "authority_version": token})

    def status(self):
        return self.request("/status", method="GET")

    def witness_status(self):
        status, reply = base.call(self.witness_port, "GET", "/status")
        return {"status": status, "response": reply}

    def result(self):
        value = {"name": self.name, "candidate": self.candidate,
                 "frames": self.frames, "journal": self.capture_journal(),
                 "witness": self.witness_status(),
                 "proxy_log": [] if self.proxy is None else self.proxy.log,
                 "children": [child.meta for child in self.children]}
        try:
            value["sink_status"] = self.status()[1]
        except Exception as error:
            value["sink_status_error"] = type(error).__name__
        return value

    def close(self, kill_sink=False):
        if self.proxy:
            self.proxy.close()
        for child in reversed(self.children):
            if child.process.poll() is None:
                child.stop(kill=kill_sink if child is getattr(self, "sink", None) else True)


def threaded_submit(history, request_id, payload, token=1):
    output = []
    thread = threading.Thread(target=lambda: output.append(history.submit(request_id, payload, token)), daemon=True)
    thread.start()
    return thread, output


def kill_at_gate(history, stage, request_id):
    thread, output = threaded_submit(history, request_id, "payload:" + request_id)
    gate_record = history.sink.line(timeout=5)
    if gate_record.get("event") != "gate" or gate_record.get("stage") != stage:
        raise AssertionError(f"unexpected gate marker: {gate_record}")
    journal_at_gate = history.capture_journal()
    history.sink.stop(kill=True)
    thread.join(timeout=3)
    return {"gate": gate_record, "journal_at_gate": journal_at_gate,
            "request_thread_alive_after_reap": thread.is_alive(),
            "request_result": output[0] if output else None,
            "owner_pid": history.sink.meta["pid"], "owner_exit": history.sink.meta["exit"],
            "owner_exit_ns": history.sink.meta["exit_ns"]}


def execute(out):
    out.mkdir(parents=True, exist_ok=False)
    result = {"source_hashes": {str(path.relative_to(HERE.parent)): sha(path.read_bytes())
                                for path in (CUT_SOURCE, SOURCES / "managed-revocation/managed_sink.py",
                                             RUN_SOURCE, CANDIDATE, PROBE_SOURCE)},
              "pin": "9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9",
              "runtime": {"python": sys.version, "platform": sys.platform,
                          "uid": os.getuid(), "gid": os.getgid()},
              "cases": {}}
    with tempfile.TemporaryDirectory(prefix="phase-i-effect-retry-") as temp:
        base_dir = Path(temp)
        # Fresh baseline: the real witness commits publication but its reply is dropped.
        h = History("baseline-lost-reply", base_dir / "baseline", candidate=False, proxy=True)
        try:
            h.proxy.drop_next_publish = True
            first = h.submit("same-id", "exact-é-payload")
            retry = h.submit("same-id", "exact-é-payload")
            result["cases"]["baseline-lost-reply"] = {"first": first[2], "retry": retry[2],
                                                       "capture": h.result()}
        finally:
            h.close()

        # Candidate: same-process loss, conflict, distinct ID, stale-token denial, revoke observation.
        h = History("candidate-same-process", base_dir / "candidate-same-process", candidate=True, proxy=True)
        try:
            h.proxy.drop_next_publish = True
            first = h.submit("same-id", "exact-é-payload")
            retry = h.submit("same-id", "exact-é-payload")
            conflict = h.submit("same-id", "exact-e\u0301-payload")
            new_id = h.submit("new-id", "second-payload")
            h.request("/revoke", {})
            stale_new = h.submit("after-revoke", "new-payload", token=1)
            old_observation = h.submit("same-id", "exact-é-payload", token=1)
            empty_id = h.submit("", "payload")
            result["cases"]["candidate-same-process"] = {
                "first": first[2], "retry": retry[2], "conflict": conflict[2],
                "new_id": new_id[2], "stale_new_id": stale_new[2],
                "post_revoke_observation": old_observation[2], "empty_id": empty_id[2],
                "capture": h.result()}
        finally:
            h.close()

        # Candidate: lost client receipt followed by sink process loss and cold recovery.
        h = History("candidate-cold-retry", base_dir / "candidate-cold-retry", candidate=True, proxy=True)
        try:
            h.proxy.drop_next_publish = True
            first = h.submit("cold-id", "cold-payload")
            h.sink.stop(kill=True)
            restart = h.start_sink("recover")
            h.sink_port = restart["port"]
            retry = h.submit("cold-id", "cold-payload") if restart.get("ready") else (None, None, None)
            result["cases"]["candidate-cold-retry"] = {
                "first": first[2], "restart": restart, "retry": retry[2], "capture": h.result()}
        finally:
            h.close()

        # Actual child kill before durable append, then safe new use after cold recovery.
        h = History("kill-before-append", base_dir / "kill-before-append", candidate=True, sink_gate="before-append")
        try:
            gate = kill_at_gate(h, "before-append", "before-id")
            restart = h.start_sink("recover")
            h.sink_port = restart["port"]
            follow = h.submit("before-id", "payload:before-id") if restart.get("ready") else (None, None, None)
            result["cases"]["kill-before-append"] = {"kill": gate, "restart": restart,
                                                        "follow": follow[2], "capture": h.result()}
        finally:
            h.close()

        # Actual child kill after local fsync and identity update, before witness publication.
        h = History("kill-after-append", base_dir / "kill-after-append", candidate=True, sink_gate="after-append")
        try:
            gate = kill_at_gate(h, "after-append", "after-append-id")
            restart = h.start_sink("recover")
            result["cases"]["kill-after-append"] = {"kill": gate, "restart": restart,
                                                      "capture": h.result()}
        finally:
            h.close()

        # Actual child kill after witness CAS succeeded and before caller reply.
        h = History("kill-after-publication", base_dir / "kill-after-publication", candidate=True,
                    sink_gate="after-publication-before-reply")
        try:
            gate = kill_at_gate(h, "after-publication-before-reply", "published-id")
            restart = h.start_sink("recover")
            h.sink_port = restart["port"]
            retry = h.submit("published-id", "payload:published-id") if restart.get("ready") else (None, None, None)
            result["cases"]["kill-after-publication"] = {"kill": gate, "restart": restart,
                                                           "retry": retry[2], "capture": h.result()}
        finally:
            h.close()

        # A real witness rejection leaves a committed local event, never a no-effect denial.
        h = History("remote-rejection", base_dir / "remote-rejection", candidate=True)
        try:
            fault = {"root": ROOT, "nonce": "reject-on", "reject_publish": True}
            fault_status, fault_reply = base.call(h.witness_port, "POST", "/fault", fault)
            first = h.submit("rejected-publication-id", "still-committed")
            before = h.capture_journal()
            conflict = h.submit("rejected-publication-id", "changed-payload")
            after_conflict = h.capture_journal()
            exact_retry = h.submit("rejected-publication-id", "still-committed")
            after_exact = h.capture_journal()
            blocked = h.submit("must-not-append", "payload")
            after = h.capture_journal()
            h.sink.stop()
            restart = h.start_sink("recover")
            result["cases"]["remote-rejection"] = {
                "fault": {"status": fault_status, "response": fault_reply},
                "first": first[2], "conflict": conflict[2], "exact_retry": exact_retry[2],
                "blocked": blocked[2],
                "conflict_unchanged_journal": before["sha256"] == after_conflict["sha256"],
                "exact_retry_unchanged_journal": after_conflict["sha256"] == after_exact["sha256"],
                "blocked_request_unchanged_journal": after_exact["sha256"] == after["sha256"],
                "restart": restart, "capture": h.result()}
        finally:
            h.close()

        # Prior accepted effect remains observable after native witness revoke.
        # Covered in same-process case; isolate witness restart with no durable state.
        h = History("witness-restart-empty", base_dir / "witness-restart-empty", candidate=True)
        try:
            accepted = h.submit("witness-bound-id", "payload")
            h.sink.stop()
            h.witness.stop(kill=True)
            h.witness = Child([sys.executable, "-B", CANDIDATE, "--witness", ROOT])
            h.children.append(h.witness)
            replacement_ready = h.witness.ready()
            h.witness_port = replacement_ready["port"]
            restart = h.start_sink("recover")
            result["cases"]["witness-restart-empty"] = {
                "accepted": accepted[2], "replacement_witness": replacement_ready,
                "sink_restart": restart, "capture": h.result()}
        finally:
            h.close()

        # The weak baseline can create an actual duplicate-ID journal; candidate recovery rejects it.
        h = History("duplicate-journal", base_dir / "duplicate-journal", candidate=False)
        try:
            first = h.submit("duplicate-id", "same-payload")
            second = h.submit("duplicate-id", "same-payload")
            h.sink.stop()
            h.candidate = True
            restart = h.start_sink("recover")
            result["cases"]["duplicate-journal"] = {
                "first": first[2], "second": second[2], "candidate_restart": restart,
                "capture": h.result()}
        finally:
            h.close()

    result["execution"] = "PASS"
    result["processes"] = [child.meta for child in PROCESSES]
    result["ended_ns"] = time.monotonic_ns()
    (out / "raw.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = execute(args.out.resolve())
        print(json.dumps({"execution": result["execution"], "cases": list(result["cases"])}))
        return 0
    except BaseException:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "error.txt").write_text(traceback.format_exc())
        raise


if __name__ == "__main__":
    raise SystemExit(main())
