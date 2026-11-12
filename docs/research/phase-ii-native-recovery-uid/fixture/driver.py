#!/usr/bin/env python3
"""Root fixture driver for the bounded native UID recovery histories."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import traceback

BASE_DRIVER = Path("/opt/probe/driver.py")
RESEARCH = Path("/opt/owned-src/docs/research")
FIXTURE = RESEARCH / "phase-ii-native-recovery-uid/fixture"
CONTROLLER = FIXTURE / "owner_controller.py"
WORKER = FIXTURE / "worker.py"
CASE_ROOT = Path("/run/ases-native-recovery")


def load_base():
    spec = importlib.util.spec_from_file_location("pinned_uid_base_driver", BASE_DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("pinned base driver unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_base()


def frame(child, expected=None):
    value = child.line(timeout=30)
    if expected is not None and value.get("event") != expected:
        raise RuntimeError("unexpected controller frame: " + repr(value))
    return value


class ControllerProxy:
    """Allow the pinned D-write mediation path to issue only bounded writes."""
    def __init__(self, child):
        self.child = child
        self.forwarded = 0
        self.forwarded_records = []

    def operation(self, request):
        self.forwarded += 1
        self.child.send(request)
        response = frame(self.child, "RESPONSE")
        self.forwarded_records.append(response)
        # The pinned mediate helper consumes manager.operation(...)[result][reply].
        return {"result": {"reply": response}}


def op(controller, name, **fields):
    controller.child.send(dict(op=name, **fields))
    return frame(controller.child, "RESPONSE")


def process_record(child):
    return {
        "argv": child.argv, "pid": child.pid, "uid": child.uid,
        "status": child.status, "exit": getattr(child, "exit", None),
        "exit_ns": getattr(child, "exit_ns", None),
        "killed": getattr(child, "killed", False),
        "stderr": getattr(child, "stderr", ""),
        "stdout_tail": getattr(child, "stdout_tail", ""),
    }


def finish_one_shot(child):
    """Wait for the audit process's natural exit; it has no pipe protocol."""
    child.exit = child.p.wait(timeout=30)
    child.exit_ns = time.monotonic_ns()
    child.killed = False
    child.stdout_tail = child.p.stdout.read()[-4096:]
    child.stderr = child.p.stderr.read()[-4096:]
    if child.p.stdin is not None:
        child.p.stdin.close()
    child.p.stdout.close()
    child.p.stderr.close()


def start_controller(kind, request_id, root):
    root.mkdir(parents=True, mode=0o711, exist_ok=False)
    os.chmod(root, 0o711)
    os.chown(root, 2000, 2000)
    controller = base.Child(
        [sys.executable, "-I", "-B", str(CONTROLLER), kind, request_id],
        2000, env={"ASES_UID_CASE_ROOT": str(root)},
    )
    ready = frame(controller, "READY")
    if ready.get("uid") != 2000 or ready.get("case_kind") != kind or ready.get("request_id") != request_id:
        controller.stop(kill=True)
        raise RuntimeError("controller READY identity mismatch: " + repr(ready))
    return controller, ready


def one_shot_worker(ready, request_id):
    worker = base.Child(
        [sys.executable, "-I", "-B", str(WORKER), ready["owner_root"],
         ready["sink_socket"], ready["witness_socket"],
         str(ready["owner_server_pid"]), request_id], 2001,
    )
    audit = None
    error = None
    try:
        audit = frame(worker, "UID_RECOVERY_WORKER_AUDIT")
    except BaseException as exc:
        error = type(exc).__name__ + ":" + str(exc)
    finish_one_shot(worker)
    record = process_record(worker)
    if error:
        record["frame_error"] = error
    return audit, record


def final_snapshot(controller):
    return op(controller, "snapshot")["snapshot"]


def run_case(kind, request_id):
    root = CASE_ROOT / kind
    controller_child, ready = start_controller(kind, request_id, root)
    controller = ControllerProxy(controller_child)
    worker = base.role_worker()
    case = {"case_kind": kind, "request_id": request_id,
            "manager_ready": ready, "manager_process": process_record(controller_child)}
    try:
        # The initial native effect is created only through the existing worker D-write route.
        initial_route = base.mediate(worker, controller, {"op": "write", "payload": request_id})
        case["initial_write_route"] = initial_route
        if not controller.forwarded_records:
            raise RuntimeError("initial mediated D write did not reach UID-2000 controller")
        case["initial_effect"] = controller.forwarded_records[-1]

        # Capture the actual owner/material/journal/witness cut around every denied attempt.
        case["manager_before_denials"] = final_snapshot(controller)
        audit, worker_status = one_shot_worker(ready, request_id)
        case["worker_audit"] = audit
        case["worker_process"] = worker_status

        before_count = controller.forwarded
        management = base.mediate(worker, controller, {"op": "move", "destination": "Q"})
        after_count = controller.forwarded
        case["worker_management_attempt"] = {
            **management,
            "controller_op_count_before": before_count,
            "controller_op_count_after": after_count,
        }
        case["manager_after_denials"] = final_snapshot(controller)

        recovery = op(controller, "recover")
        case["recovery"] = recovery
        case["cold_restart"] = {
            "ready": recovery.get("cold_restart_ready"),
            "after": recovery.get("after"),
        }
        case["transition"] = op(controller, "transition")

        fresh_id = request_id + "-fresh"
        fresh_route = base.mediate(worker, controller, {"op": "write", "payload": fresh_id})
        case["fresh_denial"] = {
            "route": fresh_route,
            "controller_effect": controller.forwarded_records[-1] if controller.forwarded_records else None,
        }
        case["exact_old"] = op(controller, "exact_old")
        case["final_snapshot"] = final_snapshot(controller)
    finally:
        worker.stop(kill=False)
        controller_child.send({"op": "stop"})
        try:
            stopped = frame(controller_child, "STOPPED")
            case["manager_cleanup"] = stopped.get("cleanup")
        except BaseException as exc:
            case["manager_cleanup_error"] = type(exc).__name__ + ":" + str(exc)
        controller_child.stop(kill=False)
        case["manager_process_final"] = process_record(controller_child)
        case["controller_forwarded_operations"] = controller.forwarded_records
    return case


def main():
    os.umask(0o077)
    if os.getuid() != 0:
        raise RuntimeError("trusted fixture driver must run as UID 0")
    CASE_ROOT.mkdir(parents=True, mode=0o711, exist_ok=True)
    os.chmod(CASE_ROOT, 0o711)
    raw = {"schema": "ases4-native-recovery-uid-driver-v1", "status": "FAIL",
           "cases": {}, "outer": {"uid": os.getuid(), "driver_status": base.read_status(os.getpid()),
                                    "base_driver": str(BASE_DRIVER), "case_root": str(CASE_ROOT)}}
    try:
        raw["cases"]["local"] = run_case("local", "uid-recovery-local")
        raw["cases"]["reserved"] = run_case("reserved", "uid-recovery-reserved")
        raw["status"] = "PASS"
    except BaseException as error:
        raw["failure"] = {"type": type(error).__name__, "message": str(error),
                           "traceback": traceback.format_exc()[-16000:]}
    print(json.dumps(raw, sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if raw["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
