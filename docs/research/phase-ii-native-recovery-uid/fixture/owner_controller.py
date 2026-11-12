#!/usr/bin/env python3
"""UID-2000 owner controller for the bounded native recovery cases."""
from __future__ import annotations

import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path("/opt/owned-src/docs/research/phase-ii-native-ownership")
FIXTURE = Path("/opt/owned-src/docs/research/phase-ii-native-recovery-uid/fixture")
RECONCILE = Path("/opt/owned-src/docs/research/phase-ii-native-publication-reconcile/reconcile.py")
OBSERVE = Path("/opt/owned-src/docs/research/phase-ii-native-local-observation/observe_local.py")
GATED_SINK = FIXTURE / "test_sink_gate.py"
sys.path.insert(0, str(ROOT))
import probe


def emit(value):
    print(json.dumps(value, sort_keys=True), flush=True)


class NativeManager:
    def __init__(self, kind: str, request_id: str):
        if kind not in ("local", "reserved"):
            raise ValueError("unsupported-fixed-case")
        if not isinstance(request_id, str) or not request_id or len(request_id.encode()) > 128:
            raise ValueError("bounded-request-id-required")
        self.kind = kind
        self.request_id = request_id
        self.case_root = Path(os.environ["ASES_UID_CASE_ROOT"])
        self.prepared = probe.setup_native_f3(self.case_root / "native", world="A", activate=True)
        self.owner_root = Path(self.prepared["owner_root"])
        initial = self.prepared["owner_ready"]["snapshot"]
        self.witness_root = initial["state"]["native_owner"]["domain_id"]
        self.owner = probe.OwnerProcess(self.owner_root)
        if kind == "reserved":
            probe.NATIVE_SINK = GATED_SINK
        else:
            probe.NATIVE_SINK = ROOT / "native_sink.py"
        self.f4 = probe.NativeF4(self.case_root / "f4", self.owner_root, self.witness_root,
                                 gate="after-append" if kind == "local" else None)
        self.recovered = False
        self.transitioned = False
        self.first_write = None
        self.recovery_frame = None
        self.cold_ready = None
        self.forwarded_operations = []

    def snapshot(self):
        owner_frame = self.owner.call({"op": "read"})
        return {
            "owner_frame": owner_frame,
            "owner_tree": probe.tree(self.owner_root),
            "f1": probe.f1_raw(Path(self.prepared["f1_root"]) / "store.sqlite"),
            "journal": probe.file_record(self.f4.journal) if self.f4.journal.exists() else None,
            "witness": self.f4.witness_call("/status"),
            "sink_process": self.f4.sink.meta,
            "witness_process": self.f4.witness.meta,
            "f4_socket_dir": self.f4.socket_dir_meta,
        }

    @staticmethod
    def indexed_event(journal, request_id):
        """Read the actual sink replay parser's request index without mutation."""
        retry = probe.load_module(
            "uid_recovery_retry_state",
            ROOT.parent / "phase-i-effect-retry" / "candidate.py",
        )
        state = retry.RetryState(journal, True)
        event = state.request_index.get(request_id)
        if event is None:
            raise ValueError("gated-request-missing-from-actual-retry-index")
        return event

    def gated_first_write(self, request_id):
        if self.first_write is not None:
            raise ValueError("initial-effect-already-attempted")
        if not isinstance(request_id, str) or not request_id or len(request_id.encode()) > 128:
            raise ValueError("bounded-request-id-required")
        owner_before = self.owner.call({"op": "read"})
        envelope = probe.native_envelope(owner_before["reply"]["snapshot"], request_id)
        gate_stage = "after-append" if self.kind == "local" else "before-owner-local-observation"
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.f4.submit, envelope)
            gate = json.loads(self.f4.sink.read(timeout=20))
            if gate.get("event") != "GATE" or gate.get("stage") != gate_stage:
                raise RuntimeError("actual-native-sink-gate-mismatch:" + json.dumps(gate, sort_keys=True))
            owner_at_gate = self.owner.call({"op": "read"})
            journal_at_gate = probe.file_record(self.f4.journal)
            indexed_event_at_gate = self.indexed_event(self.f4.journal, request_id)
            witness_at_gate = self.f4.witness_call("/status")
            dead_sink = self.f4.sink.close(kill=True)
            try:
                submit_result = future.result(timeout=10)
            except Exception as error:
                submit_result = {"future_error": type(error).__name__ + ":" + str(error)}
        self.first_write = {"request_id": request_id, "envelope": envelope, "gate": gate,
                            "owner_before": owner_before, "owner_at_gate": owner_at_gate,
                            "journal_at_gate": journal_at_gate,
                            "indexed_event_at_gate": indexed_event_at_gate,
                            "witness_at_gate": witness_at_gate,
                            "dead_sink": dead_sink, "submit_result": submit_result}
        return self.first_write

    def current_write(self, request_id):
        if not self.recovered or not self.transitioned:
            raise ValueError("current-write-requires-recovery-and-transition")
        owner_frame = self.owner.call({"op": "read"})
        envelope = probe.native_envelope(owner_frame["reply"]["snapshot"], request_id)
        before = probe.file_record(self.f4.journal)
        call = self.f4.call("/submit", {"authority_version": 2, "request_id": request_id,
                                        "payload": probe.canonical(envelope)})
        after = probe.file_record(self.f4.journal)
        result = {"request_id": request_id, "envelope": envelope, "before": before,
                  "call": call, "after": after, "owner_after": self.owner.call({"op": "read"})}
        self.forwarded_operations.append(result)
        return result

    def recover(self):
        if not self.first_write:
            raise ValueError("recovery-requires-gated-native-effect")
        before = self.snapshot()
        script = RECONCILE if self.kind == "local" else OBSERVE
        argv = [sys.executable, "-B", str(script), str(self.owner_root), self.first_write["request_id"]]
        started = time.monotonic_ns()
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30, check=False)
        parsed = None
        try:
            parsed = json.loads(result.stdout.strip().splitlines()[-1]) if result.stdout.strip() else None
        except json.JSONDecodeError:
            pass
        command = {"argv": argv, "start_ns": started, "end_ns": time.monotonic_ns(),
                   "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
                   "frame": parsed}
        if result.returncode != 0 or not isinstance(parsed, dict) or parsed.get("status") != "published":
            raise RuntimeError("manager-native-recovery-failed:" + json.dumps(command, sort_keys=True))
        self.recovered = True
        cold = self.f4.cold_restart()
        self.cold_ready = cold
        after = self.snapshot()
        self.recovery_frame = {"event": "RESPONSE", "op": "recover", "before": before,
                               "command": command, "cold_restart_ready": cold,
                               "after": after, "status": parsed.get("status")}
        return self.recovery_frame

    def transition(self):
        if not self.recovered:
            raise ValueError("transition-requires-recovery")
        f4_replace = self.f4.call("/replace", {"holder": "uid-recovery-current"})
        f4_activate = self.f4.call("/activate", {"authority_version": 2})
        native_steps = [self.owner.call({"op": op}) for op in ("seal", "move", "activate")]
        self.transitioned = True
        frame = {"event": "RESPONSE", "op": "transition", "f4_replace": f4_replace,
                 "f4_activate": f4_activate, "native_steps": native_steps,
                 "after": self.snapshot()}
        return frame

    def exact_old(self):
        if not self.recovered:
            raise ValueError("historical-lookup-requires-recovery")
        event = self.indexed_event(self.f4.journal, self.first_write["request_id"])
        before = probe.file_record(self.f4.journal)
        request = {"authority_version": event["accepted_under_version"],
                   "request_id": event["request_id"], "payload": event["payload"]}
        call = self.f4.call("/submit", request)
        after = probe.file_record(self.f4.journal)
        return {"event": "RESPONSE", "op": "exact_old", "actual_index_event": event,
                "request": request, "before": before, "call": call, "after": after,
                "owner_after": self.owner.call({"op": "read"})}

    def operation(self, request):
        if not isinstance(request, dict) or not isinstance(request.get("op"), str):
            raise ValueError("fixed-manager-request-required")
        op = request["op"]
        if op == "snapshot" and set(request) == {"op"}:
            return {"event": "RESPONSE", "op": op, "snapshot": self.snapshot()}
        if op == "write" and set(request) == {"op", "payload"}:
            if self.first_write is None:
                return {"event": "RESPONSE", "op": op,
                        "first_write": self.gated_first_write(request["payload"])}
            return {"event": "RESPONSE", "op": op,
                    "current_write": self.current_write(request["payload"])}
        if op == "recover" and set(request) == {"op"}:
            return self.recover()
        if op == "transition" and set(request) == {"op"}:
            return self.transition()
        if op == "exact_old" and set(request) == {"op"}:
            return self.exact_old()
        if op == "stop" and set(request) == {"op"}:
            return {"event": "STOP", "op": op}
        raise ValueError("unsupported-fixed-manager-operation")

    def close(self):
        # F4 services and the owner are children of this UID-2000 manager.
        self.f4.close(kill=True)
        self.owner.close(kill=False)
        return {"owner_process": self.owner.meta, "sink_process": self.f4.sink.meta,
                "witness_process": self.f4.witness.meta,
                "owner_tree": probe.tree(self.owner_root),
                "journal": probe.file_record(self.f4.journal) if self.f4.journal.exists() else None,
                "f1": probe.f1_raw(Path(self.prepared["f1_root"]) / "store.sqlite")}


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: owner_controller.py {local|reserved} REQUEST_ID")
    kind, request_id = argv[1:]
    controller = NativeManager(kind, request_id)
    emit({"event": "READY", "case_kind": kind, "request_id": request_id,
          "uid": os.getuid(), "owner_root": str(controller.owner_root),
          "f1_db": str(Path(controller.prepared["f1_root"]) / "store.sqlite"),
          "sink_socket": str(controller.f4.sink_socket),
          "witness_socket": str(controller.f4.witness_socket),
          "owner_server_pid": controller.owner.p.pid,
          "snapshot": controller.snapshot(), "f4_lifecycle": controller.f4.lifecycle_calls})
    try:
        for line in sys.stdin:
            request = json.loads(line)
            if request.get("op") == "stop":
                break
            try:
                emit(controller.operation(request))
            except BaseException as error:
                emit({"event": "ERROR", "op": request.get("op"), "error": type(error).__name__,
                      "message": str(error), "traceback": traceback.format_exc()[-8192:]})
    finally:
        cleanup = controller.close()
        emit({"event": "STOPPED", "cleanup": cleanup})


if __name__ == "__main__":
    main(sys.argv)
