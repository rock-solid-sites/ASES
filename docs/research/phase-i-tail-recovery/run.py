#!/usr/bin/env python3
"""Native HTTP/process histories for the isolated durable-request retry candidate."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "phase-i-sol-integration/evidence/sources/receipt/research/phase-i-t18-sink-order-20261103"
CUT_SOURCE = SOURCES / "published-cut/cut_sink.py"
RUN_SOURCE = SOURCES / "run.py"
CANDIDATE = HERE / "candidate.py"
RECOVERY_SOURCE = HERE / "recovery.py"
PROBE_SOURCE = HERE / "run.py"
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


class History:
    def __init__(self, name, root, candidate=True, sink_gate=None):
        self.name = name
        self.path = Path(root)
        self.path.mkdir(parents=True)
        self.journal = self.path / "sink-effects.jsonl"
        self.candidate = candidate
        self.frames = []
        self.children = []
        self.witness = self.start_witness()
        init_req = {"root": ROOT, "nonce": "init-" + name, "cut": GENESIS}
        init_status, init_reply = base.call(self.witness_port, "POST", "/init", init_req)
        self.frames.append({"actor": "probe", "path": "/init", "request": init_req,
                            "status": init_status, "response": init_reply})
        if init_status != 200:
            raise RuntimeError("witness init failed")
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
        return self.witness_port

    def fault(self, **values):
        request = {"root": ROOT, "nonce": "fault-" + self.name, **values}
        status, response = base.call(self.witness_port, "POST", "/fault", request)
        self.frames.append({"actor": "probe", "path": "/fault", "request": request,
                            "status": status, "response": response})
        if status != 200:
            raise RuntimeError("witness fault setup failed")

    def start_sink(self, mode, gate_name=None, write_fault=None, tail_gate=None):
        executable = CANDIDATE if self.candidate else CUT_SOURCE
        args = [sys.executable, "-B", executable, "--sink", mode, self.journal,
                str(self.endpoint()), "published-cut", ROOT]
        env = ({"ASES_RETRY_GATE": gate_name or "", "ASES_TAIL_WRITE_FAULT": write_fault or "",
                "ASES_TAIL_GATE": tail_gate or "", "ASES_TAIL_TEST_ROOT": str(self.path.resolve())} if self.candidate else None)
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
        events = []
        for line in raw.splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                events.append({"invalid_json": True, "raw_hex": line.hex()})
        return {"sha256": sha(raw), "raw_hex": raw.hex(), "size": len(raw),
                "events": events}

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
                 "children": [child.meta for child in self.children]}
        try:
            value["sink_status"] = self.status()[1]
        except Exception as error:
            value["sink_status_error"] = type(error).__name__
        return value

    def close(self, kill_sink=False):
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



def append_tail_case(base_dir, name, fault):
    h = History(name, base_dir / name, candidate=True)
    try:
        # Fault occurs inside native SinkState.emit_locked while writing the
        # next actual effect_accepted journal row.
        h.sink.stop()
        h.start_sink("recover", write_fault=fault)
        h.sink_port = h.sink_ready["port"]
        pre = h.capture_journal()
        failed = h.submit(name + "-id", "payload:" + name)
        after = h.capture_journal()
        h.sink.stop()
        strict = h.start_sink("recover")
        strict_bytes = h.journal.read_bytes()
        h.sink.stop()
        recovered = h.start_sink("recover-tail")
        selected = h.journal.read_bytes()
        qfiles = sorted(h.path.glob("sink-effects.jsonl.quarantine-*"))
        result = {"before": pre, "failed_attempt": failed[2],
                  "after_native_fault": after, "ordinary_strict_restart": strict,
                  "ordinary_restart_bytes_unchanged": strict_bytes == after_raw(after),
                  "explicit_recovery": recovered,
                  "selected_bytes": selected.hex(),
                  "quarantine": [{"name": q.name, "sha256": sha(q.read_bytes()),
                                  "raw_hex": q.read_bytes().hex()} for q in qfiles],
                  "capture": h.result()}
        if fault == "partial-write" and recovered.get("ready"):
            h.sink_port = recovered["port"]
            accepted = h.submit(name + "-id", "payload:" + name)
            retry = h.submit(name + "-id", "payload:" + name)
            result["fresh_retry_after_recovery"] = accepted[2]
            result["exact_retry_after_recovery"] = retry[2]
            result["capture"] = h.result()
        return result
    finally:
        h.close()


def after_raw(capture):
    return bytes.fromhex(capture["raw_hex"])



def recovery_gate_case(base_dir, stage):
    h = History("recovery-gate-" + stage, base_dir / ("gate-" + stage), candidate=True)
    try:
        h.sink.stop()
        h.start_sink("recover", write_fault="partial-write")
        h.sink_port = h.sink_ready["port"]
        failed = h.submit("gate-tail-id", "gate-tail-payload")
        before = h.journal.read_bytes()
        h.sink.stop()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", ASES_RETRY_GATE="",
                   ASES_TAIL_WRITE_FAULT="", ASES_TAIL_GATE=stage,
                   ASES_TAIL_TEST_ROOT=str(h.path.resolve()))
        child = Child([sys.executable, "-B", CANDIDATE, "--sink", "recover-tail",
                       h.journal, str(h.witness_port), "published-cut", ROOT], env)
        h.children.append(child)
        gate_record = child.line(timeout=5)
        if gate_record.get("event") != "tail-gate" or gate_record.get("stage") != stage:
            raise AssertionError("unexpected recovery gate marker")
        gate_raw = h.journal.read_bytes()
        child.stop(kill=True)
        h.sink = child
        after_kill = h.journal.read_bytes()
        # Re-invoke explicit recovery. Before selection it must finish from the
        # old tail; after selection it must validate and report no-tail.
        retry = h.start_sink("recover-tail")
        final = h.journal.read_bytes()
        quarantine = sorted(h.path.glob("sink-effects.jsonl.quarantine-*"))
        qexact = bool(quarantine) and quarantine[-1].read_bytes() == before
        return {"failed_append": failed[2], "gate": gate_record,
                "journal_at_gate_hex": gate_raw.hex(), "journal_after_kill_hex": after_kill.hex(),
                "retry_start": retry, "journal_after_retry_hex": final.hex(),
                "exact_quarantine_present": qexact,
                "quarantine_sha256": [sha(path.read_bytes()) for path in quarantine],
                "final_equals_validated_prefix": final == before[:before.rfind(b"\n") + 1],
                "capture": h.result()}
    finally:
        h.close()


def refused_recovery_case(base_dir, name, mutate):
    h = History(name, base_dir / name, candidate=True)
    try:
        h.sink.stop()
        original = h.journal.read_bytes()
        changed = mutate(original)
        h.journal.write_bytes(changed)
        before_hash = sha(changed)
        attempt = h.start_sink("recover-tail")
        after = h.journal.read_bytes()
        return {"original_sha256": sha(original), "mutated_sha256": before_hash,
                "attempt": attempt, "bytes_unchanged": after == changed,
                "before_hex": changed.hex(), "after_hex": after.hex(),
                "quarantine_count": len(list(h.path.glob("sink-effects.jsonl.quarantine-*"))),
                "capture": h.result()}
    finally:
        h.close()


def execute(out):
    out.mkdir(parents=True, exist_ok=False)
    result = {"source_hashes": {str(path.relative_to(HERE.parent)): sha(path.read_bytes())
                                for path in (CUT_SOURCE, SOURCES / "managed-revocation/managed_sink.py",
                                             RUN_SOURCE, CANDIDATE, PROBE_SOURCE, RECOVERY_SOURCE)},
              "pin": "9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9",
              "runtime": {"python": sys.version, "platform": sys.platform,
                          "uid": os.getuid(), "gid": os.getgid()},
              "cases": {}}
    with tempfile.TemporaryDirectory(prefix="phase-i-effect-retry-") as temp:
        base_dir = Path(temp)
        # Fresh baseline: the real witness commits publication but its reply is dropped.
        h = History("baseline-lost-reply", base_dir / "baseline", candidate=False)
        try:
            h.fault(reject_publish=False, drop_publish_reply_once=True)
            first = h.submit("same-id", "exact-é-payload")
            retry = h.submit("same-id", "exact-é-payload")
            result["cases"]["baseline-lost-reply"] = {"first": first[2], "retry": retry[2],
                                                       "capture": h.result()}
        finally:
            h.close()

        # Candidate: same-process loss, conflict, distinct ID, stale-token denial, revoke observation.
        h = History("candidate-same-process", base_dir / "candidate-same-process", candidate=True)
        try:
            h.fault(reject_publish=False, drop_publish_reply_once=True)
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
        h = History("candidate-cold-retry", base_dir / "candidate-cold-retry", candidate=True)
        try:
            h.fault(reject_publish=False, drop_publish_reply_once=True)
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

        # Obligation routes are explicitly outside this bounded /submit contract.
        # Each refusal must happen before any local journal append.
        h = History("obligation-refusal", base_dir / "obligation-refusal", candidate=True)
        try:
            before = h.capture_journal()
            commit = h.request("/commit-obligation", {"obligation_id": "outside-f4",
                                                       "payload": "must-not-commit"})
            after_commit = h.capture_journal()
            deliver = h.request("/deliver-obligation", {"obligation_id": "outside-f4"})
            after_deliver = h.capture_journal()
            result["cases"]["obligation-refusal"] = {
                "commit": commit[2], "deliver": deliver[2],
                "commit_unchanged_journal": before["sha256"] == after_commit["sha256"],
                "deliver_unchanged_journal": after_commit["sha256"] == after_deliver["sha256"],
                "capture": h.result()}
        finally:
            h.close()

        # Native journal capacity failure must remain an error/unknown attempt,
        # never a retry response claiming no effect occurred.
        h = History("append-failure", base_dir / "append-failure", candidate=True)
        try:
            request_id = "capacity-failure-id"
            payload = "x" * 65536
            first = h.submit(request_id, payload)
            first_after = h.capture_journal()
            retry = h.submit(request_id, payload)
            retry_after = h.capture_journal()
            result["cases"]["append-failure"] = {
                "first": first[2], "retry": retry[2],
                "first_unchanged_journal": first[2]["journal_before_sha256"] == first_after["sha256"],
                "retry_unchanged_journal": first_after["sha256"] == retry_after["sha256"],
                "capture": h.result()}
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

    # Actual partial-row OSError and complete-row fsync OSError, both from
    # native managed F4 append code. The latter must remain unresolved.
    with tempfile.TemporaryDirectory(prefix="phase-i-tail-partial-") as temp:
        result["cases"]["actual-partial-write"] = append_tail_case(Path(temp), "actual-partial-write", "partial-write")
    with tempfile.TemporaryDirectory(prefix="phase-i-tail-fsync-") as temp:
        result["cases"]["complete-row-fsync-error"] = append_tail_case(Path(temp), "complete-row-fsync-error", "complete-write-fsync")

    with tempfile.TemporaryDirectory(prefix="phase-i-tail-gates-") as temp:
        for stage in ("quarantined", "prepared", "selected"):
            result["cases"]["recovery-kill-" + stage] = recovery_gate_case(Path(temp), stage)
    with tempfile.TemporaryDirectory(prefix="phase-i-tail-refusals-") as temp:
        base_dir = Path(temp)
        result["cases"]["busy-writer-refusal"] = None
        h = History("busy-writer", base_dir / "busy-writer", candidate=True)
        try:
            before = h.journal.read_bytes()
            lock_stat = (h.path / "sink-writer.lock").stat()
            refused = h.start_sink("recover-tail")
            refusal_guard = refused.get("guard", {})
            result["cases"]["busy-writer-refusal"] = {
                "attempt": refused, "bytes_unchanged": h.journal.read_bytes() == before,
                "stable_lock_inode": refusal_guard.get("device") == lock_stat.st_dev
                and refusal_guard.get("inode") == lock_stat.st_ino,
                "lock_device": lock_stat.st_dev, "lock_inode": lock_stat.st_ino}
        finally:
            h.close()
        result["cases"]["invalid-complete-prefix-plus-tail"] = refused_recovery_case(
            base_dir, "invalid-complete-prefix-plus-tail", lambda raw: raw + b"not-json\npartial")
        result["cases"]["no-complete-prefix"] = refused_recovery_case(
            base_dir, "no-complete-prefix", lambda raw: b"unterminated")
        result["cases"]["witness-mismatch-with-tail"] = refused_recovery_case(
            base_dir, "witness-mismatch-with-tail",
            lambda raw: raw[:raw.rfind(b"\n", 0, len(raw)-1) + 1] + b"unpublished-tail")
        result["cases"]["acknowledged-record-truncation"] = refused_recovery_case(
            base_dir, "acknowledged-record-truncation",
            lambda raw: raw[:raw.rfind(b"\n", 0, len(raw)-1) + 1])

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
