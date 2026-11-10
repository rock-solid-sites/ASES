#!/usr/bin/env python3
"""Root-trusted bounded UID split around the actual native F1/F3/F4 stack."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import traceback

DRIVER_PATH = Path("/opt/probe/driver.py")
SRC = Path("/opt/owned-src/docs/research/phase-ii-native-ownership/uid_fixture")
OWNER_CLI = SRC.parent / "owner_cli.py"


def load_driver():
    spec = importlib.util.spec_from_file_location("pinned_uid_driver", DRIVER_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class Controller:
    def __init__(self, child):
        self.child = child

    def operation(self, request):
        if set(request) != {"op", "payload"} or request.get("op") != "write":
            raise ValueError("root-controller accepts fixed D-write only")
        frame = self.child.operation({"op": "write", "payload": request["payload"]})
        self.last_frame = frame
        body = frame.get("call", {}).get("response", {})
        return {"result": {"reply": body}}


def main():
    base = load_driver()
    case = Path("/run/ases-native-uid")
    if case.exists():
        raise RuntimeError("fixed runtime path already exists")
    case.mkdir(mode=0o700, parents=True)
    os.chmod(case, 0o711)
    os.chown(case, base.STORE_UID, base.STORE_UID)
    controller = base.Child([sys.executable, "-B", str(SRC / "owner_controller.py")],
                            base.STORE_UID,
                            env={"ASES_UID_CASE_ROOT": str(case)})
    report = {"base_image_driver": str(DRIVER_PATH), "case_path": str(case),
              "controller_status": controller.status}
    try:
        ready = controller.line(timeout=30)
        report["controller_ready"] = ready
        if controller.status.get("NoNewPrivs") != "1":
            raise RuntimeError("UID-2000 controller missing no-new-privileges")
        owner_root = ready["owner_root"]
        worker = base.role_worker()
        report["worker_status"] = worker.status
        verify_worker_status(worker.status)
        worker.send({"task": "audit-fds", "store": owner_root})
        report["fd_audit"] = worker.line()
        manager = Controller(controller)
        report["authorized_neighbor"] = base.mediate(
            worker, manager, {"op": "write", "payload": "uid-authorized-neighbor"})
        report["authorized_controller_frame"] = manager.last_frame
        authorized_body = report["authorized_neighbor"]["driver_decision"]
        if (authorized_body.get("status") != 201
                or authorized_body.get("body", {}).get("owner_effect", {}).get("status") != "published"
                or report["authorized_controller_frame"].get("matching_actual_events", [{}])[0].get("request_id")
                != "uid-authorized-neighbor"):
            raise RuntimeError("worker D-use did not produce its exact actual published F4 event")
        report["after_neighbor"] = controller.operation({"op": "read"})
        report["worker_management_attempt"] = base.mediate(
            worker, manager, {"op": "move", "destination": "Q"})
        report["after_worker_management_attempt"] = controller.operation({"op": "read"})
        before_bad = report["after_neighbor"]["f4"]["journal"]
        after_bad = report["after_worker_management_attempt"]["f4"]["journal"]
        if before_bad != after_bad:
            raise RuntimeError("worker management command changed actual F4 journal")
        attack = base.Child([sys.executable, "-I", "-B", str(SRC / "worker.py"),
                             owner_root, ready["sink_socket"], ready["witness_socket"],
                             str(ready["owner_server_pid"])], base.WORKER_UID)
        report["attack_status"] = attack.status
        report["attack"] = attack.line(timeout=10)
        attack_actions = {item["name"]: item for item in report["attack"]["actions"]}
        if any(attack_actions[name]["result"] != "denied" for name in
               ("protected-current-append", "management-lock-unlink", "sink-unix-connect",
                "witness-unix-connect", "setuid-controller")):
            raise RuntimeError("UID-2001 attack unexpectedly crossed a native boundary")
        attack.stop(kill=False)
        report["attack_process"] = {"exit": attack.exit, "stderr": attack.stderr}
        worker.stop(kill=False)
        report["worker_process"] = {"exit": worker.exit, "stderr": worker.stderr}
        report["trusted_attenuation"] = controller.operation({"op": "attenuate"})
        denied_worker = base.role_worker()
        report["denied_worker_status"] = denied_worker.status
        verify_worker_status(denied_worker.status)
        report["post_attenuation_write"] = base.mediate(
            denied_worker, manager, {"op": "write", "payload": "uid-denied-after-move"})
        denied_worker.stop(kill=False)
        report["denied_worker_process"] = {"exit": denied_worker.exit, "stderr": denied_worker.stderr}
        report["after_denial"] = controller.operation({"op": "read"})
        denied = report["post_attenuation_write"]["driver_decision"]
        if (denied.get("status") != 409
                or report["after_denial"]["f4"]["journal"] != after_bad):
            raise RuntimeError("post-attenuation D-use was not a no-append 409")
        controller.send({"op": "stop"})
        report["controller_stopped"] = controller.line(timeout=20)
        controller.p.wait(timeout=10)
        report["controller_exit"] = controller.p.returncode
        report["controller_stderr"] = controller.p.stderr.read()[-4096:]
        report["worker_capability_partition"] = {"controller": controller.status,
                                                  "worker": report["worker_status"],
                                                  "denied_worker": report["denied_worker_status"]}
        report["status"] = "PASS"
        print(json.dumps(report, sort_keys=True), flush=True)
        return 0
    except BaseException:
        try:
            controller.send({"op": "stop"})
            controller.p.wait(timeout=10)
        except BaseException:
            pass
        print(json.dumps({"status": "FAIL", "report": report,
                          "traceback": traceback.format_exc()}, sort_keys=True), flush=True)
        return 1


def verify_worker_status(status):
    if (status.get("Uid", "").split() != ["2001"] * 4
            or status.get("Gid", "").split() != ["2001"] * 4
            or status.get("Groups") != ""
            or status.get("CapPrm") != "0000000000000000"
            or status.get("CapEff") != "0000000000000000"
            or status.get("NoNewPrivs") != "1"):
        raise RuntimeError("UID-2001 worker does not match frozen capability boundary: " + repr(status))


if __name__ == "__main__":
    raise SystemExit(main())
