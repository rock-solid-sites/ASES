#!/usr/bin/env python3
"""Trusted root driver: fixed UID split around the original native L5 manager."""
import ctypes
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time

STORE_UID = 2000
WORKER_UID = 2001
BASE = Path("/run/custody")
SRC = Path("/opt/probe/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle")
L5DIR = SRC / "l5"
MANAGER = L5DIR / "move-cuts/worker.py"
MANAGER_VARIANT = Path("/opt/probe/src/docs/research/phase-i-f1-recovery-repair/l5/worker_variant.py")
OWNER_SUPERVISOR = Path("/opt/probe/owner_supervisor.py")
FIXTURE_PATH = L5DIR / "test_management_conformance.py"
WORKER_SCRIPT = Path("/opt/probe/worker_agent.py")
CAPS_EXPECTED = "00000000000000c3"
PROCESSES = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_status(pid):
    values = {}
    for line in Path(f"/proc/{pid}/status").read_text().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key] = value.strip()
    return {key: values.get(key) for key in
            ("Uid", "Gid", "Groups", "CapPrm", "CapEff", "CapBnd", "NoNewPrivs")}


def load_fixture():
    sys.path.insert(0, str(L5DIR))
    spec = importlib.util.spec_from_file_location("native_l5_fixture", FIXTURE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


fixture = load_fixture()


def reset_store(name, parent_grants):
    case = BASE / "cases" / name
    store = case / "store"
    if case.exists():
        import shutil
        shutil.rmtree(case)
    case.mkdir(parents=True)
    os.chmod(case, 0o711)
    store.mkdir(mode=0o700)
    state = fixture.state(parent="P", parent_grants=parent_grants)
    accepted = b"accepted-object-custody-fixture\n"
    state["work_units"]["C"]["accepted_contents"] = [
        {"identity": "x", "object": "objects/x.bin", "sha256": sha(accepted), "size": len(accepted)}]
    fixture.publish(store, state)
    objects = store / "protected/objects"
    objects.mkdir()
    (objects / "x.bin").write_bytes(accepted)
    lock = store / "management-writer.lock"
    fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
    os.close(fd)
    for path in sorted(store.rglob("*"), reverse=True):
        os.chmod(path, 0o700 if path.is_dir() else 0o600)
        os.chown(path, STORE_UID, STORE_UID)
    os.chmod(store, 0o700)
    os.chown(store, STORE_UID, STORE_UID)
    return case, store, accepted


def preexec(uid):
    os.setgroups([])
    os.setgid(uid)
    os.setuid(uid)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_NO_NEW_PRIVS)")
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (4, 4))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (8, 8))
    os.chdir("/opt/probe")


CHILD_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}


class Child:
    def __init__(self, argv, uid, env=None, pass_fds=()):
        self.argv = [str(item) for item in argv]
        self.uid = uid
        self.stop_message = {"op": "stop"}
        self.start_ns = time.monotonic_ns()
        self.p = subprocess.Popen(self.argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1,
                                  env=dict(CHILD_ENV, **(env or {})), close_fds=True,
                                  pass_fds=tuple(pass_fds), preexec_fn=lambda: preexec(uid),
                                  cwd="/opt/probe")
        self.pid = self.p.pid
        PROCESSES.append(self)
        try:
            self.status = read_status(self.pid)
        except FileNotFoundError:
            self.status = {"process_exited_before_status_read": True}

    def line(self, timeout=5):
        if not select.select([self.p.stdout], [], [], timeout)[0]:
            raise TimeoutError("child JSON frame timeout")
        line = self.p.stdout.readline()
        if not line:
            err = self.p.stderr.read()
            raise RuntimeError("child stdout ended: " + err[-1024:])
        return json.loads(line)

    def send(self, data):
        self.p.stdin.write(json.dumps(data, sort_keys=True) + "\n")
        self.p.stdin.flush()

    def operation(self, data):
        self.send(data)
        return self.line()

    def stop(self, kill=False):
        if self.p.poll() is None:
            if kill:
                self.p.kill()
            else:
                self.p.stdin.write(json.dumps(self.stop_message) + "\n")
                self.p.stdin.flush()
        code = self.p.wait(timeout=5)
        self.exit = code
        self.exit_ns = time.monotonic_ns()
        self.killed = kill
        self.stdout_tail = self.p.stdout.read()[-2048:]
        self.stderr = self.p.stderr.read()[-2048:]
        self.stdin_closed = self.p.stdin.closed


def start_manager(store, phase="none", original=False):
    mode = "original" if original else "exclusive"
    supervisor = Child([sys.executable, "-I", "-B", str(OWNER_SUPERVISOR),
                        mode, str(store), phase], STORE_UID)
    frame = supervisor.line()
    if frame.get("event") != "OWNER_READY":
        raise RuntimeError("UID-2000 owner supervisor failed: " + repr(frame))
    return Owner(supervisor, frame)


class Owner:
    """Root-controlled pipe to a same-UID supervisor that owns native kill/reap."""
    def __init__(self, supervisor, ready):
        self.supervisor = supervisor
        self.ready = ready["manager_ready"]
        self.manager_pid = ready["manager_pid"]
        self.status = read_status(self.manager_pid)
        self.pid = supervisor.pid
        self.uid = STORE_UID
        self.argv = supervisor.argv

    def operation(self, request):
        self.supervisor.send({"cmd": "manager", "request": request})
        frame = self.supervisor.line()
        if frame.get("event") != "MANAGER_FRAME":
            raise RuntimeError("unexpected owner event: " + repr(frame))
        return frame["frame"]

    def kill_manager(self):
        self.supervisor.send({"cmd": "kill-manager"})
        result = self.supervisor.line()
        self.manager_exit = result["exit"]
        self.manager_reaped = result.get("still_running") is False
        self.manager_exit_ns = time.monotonic_ns()
        return result

    def stop(self):
        self.supervisor.send({"cmd": "stop"})
        self.owner_stopped = self.supervisor.line()
        child = self.supervisor
        child.exit = child.p.wait(timeout=5)
        child.exit_ns = time.monotonic_ns()
        child.killed = False
        child.stdout_tail = child.p.stdout.read()[-2048:]
        child.stderr = child.p.stderr.read()[-2048:]
        child.p.stdin.close(); child.p.stdout.close(); child.p.stderr.close()


def lock_id(store):
    info = (store / "management-writer.lock").stat()
    return {"device": info.st_dev, "inode": info.st_ino, "uid": info.st_uid,
            "gid": info.st_gid, "mode": oct(info.st_mode & 0o777)}


def path_id(path):
    path = Path(path)
    info = path.stat()
    return {"device": info.st_dev, "inode": info.st_ino, "uid": info.st_uid,
            "gid": info.st_gid, "mode": oct(info.st_mode & 0o777),
            "is_dir": path.is_dir()}


def current(store):
    path = store / "protected/CURRENT"
    name = path.read_text().strip()
    raw = (store / "protected" / name).read_bytes()
    state = json.loads(raw)
    objects = []
    for metadata in state["work_units"]["C"]["accepted_contents"]:
        blob = (store / "protected" / metadata["object"]).read_bytes()
        objects.append({"metadata": metadata, "raw_hex": blob.hex(), "sha256": sha(blob)})
    effect = (store / "effects/D.bin").read_bytes() if (store / "effects/D.bin").exists() else None
    return {"selector": name, "selector_raw_hex": path.read_bytes().hex(),
            "record_sha256": sha(raw), "record_raw_hex": raw.hex(),
            "accepted_objects": objects,
            "effect_sha256": sha(effect) if effect is not None else None,
            "effect_raw_hex": effect.hex() if effect is not None else None}


def role_worker():
    child = Child([sys.executable, "-I", "-B", str(WORKER_SCRIPT), "role"], WORKER_UID)
    child.stop_message = {"task": "stop"}
    return child


def mediate(worker, manager, request):
    worker.send({"task": "request", "request": request})
    item = worker.line()
    message = item["request"]
    if (not isinstance(message, dict) or set(message) != {"op", "payload"}
            or message.get("op") != "write" or not isinstance(message.get("payload"), str)
            or len(message["payload"].encode("utf-8")) > 128):
        response = {"result": "DENY", "reason": "worker-route-only-D-write"}
    else:
        result = manager.operation({"op": "write", "payload": message["payload"]})
        response = result["result"]["reply"]
    worker.send(response)
    worker_response = worker.line()
    return {"input": item, "driver_decision": response,
            "worker_response": worker_response}


def manager_authorize(manager, op):
    frame = manager.operation({"op": op})
    return frame


def uid_path_case(name, grants, move):
    case, store, expected = reset_store(name, grants)
    mgr = start_manager(store)
    setup = {"ready": mgr.ready, "uid_status": mgr.status, "lock": lock_id(store)}
    if move:
        setup["move"] = manager_authorize(mgr, "move")
    setup["activation"] = manager_authorize(mgr, "activate")
    worker = role_worker()
    before_audit = current(store)
    worker.send({"task": "audit-fds", "store": str(store)})
    fds = worker.line()
    after_audit = current(store)
    request = mediate(worker, mgr, {"op": "write", "payload": name + "-payload"})
    before_deny = current(store)
    denied_management = mediate(worker, mgr, {"op": "move", "destination": "Q"})
    after_deny = current(store)
    final = current(store)
    worker.stop()
    mgr.stop()
    return {"setup": setup, "worker_status": worker.status, "worker_fds": fds,
            "direct_ebadf_and_path_control": {"before": before_audit,
                                               "after": after_audit,
                                               "unchanged": before_audit == after_audit},
            "write_route": request, "management_route": denied_management,
            "management_route_unchanged": before_deny == after_deny,
            "expected_object_hex": expected.hex(), "final": final,
            "store_identity": path_id(store),
            "protected_identity": path_id(store / "protected"),
            "case_parent_identity": path_id(case),
            "store_lock_after": lock_id(store), "owner_process": process_meta(mgr),
            "worker_process": process_meta(worker)}


def process_meta(child):
    if isinstance(child, Owner):
        return {"supervisor_pid": child.pid, "manager_pid": child.manager_pid,
                "manager_uid_status": child.status,
                "manager_exit": getattr(child, "manager_exit", None),
                "manager_reaped": getattr(child, "manager_reaped", None),
                "supervisor": process_meta(child.supervisor)}
    return {"argv": child.argv, "pid": child.pid, "uid": child.uid,
            "status": child.status, "exit": getattr(child, "exit", None),
            "exit_ns": getattr(child, "exit_ns", None),
            "killed": getattr(child, "killed", False),
            "stderr": getattr(child, "stderr", "")}


def attack_case():
    case, store, _ = reset_store("attacks", ["read", "write"])
    mgr = start_manager(store)
    current_before = current(store)
    root_before = store.stat(); lock_before = lock_id(store)
    attacker = Child([sys.executable, "-I", "-B", str(WORKER_SCRIPT), "attack",
                      str(store), str(mgr.manager_pid), str(L5DIR / "l5_integrated.py")], WORKER_UID)
    observation = attacker.line()
    attacker.stop_message = {"task": "stop"}
    attacker.stop()
    root_after = store.stat(); lock_after = lock_id(store)
    final = current(store)
    mgr.stop()
    return {"manager_ready": mgr.ready, "manager_pid": mgr.manager_pid,
            "worker_status": attacker.status, "attack": observation,
            "root_inode_before": root_before.st_ino, "root_inode_after": root_after.st_ino,
            "lock_before": lock_before, "lock_after": lock_after,
            "store_identity": path_id(store), "protected_identity": path_id(store / "protected"),
            "case_parent_identity": path_id(case),
            "current_before": current_before, "current_after": final,
            "store_snapshot_unchanged": current_before == final,
            "owner_process": process_meta(mgr),
            "attacker_process": process_meta(attacker)}


def contender_case():
    _, store, _ = reset_store("contender", ["read", "write"])
    owner = start_manager(store)
    lock_owner = lock_id(store)
    contender = Child([sys.executable, "-I", "-B", str(MANAGER_VARIANT), "exclusive", str(store), "none"], STORE_UID)
    refusal = contender.line()
    contender.stop()
    before = current(store)
    owner.stop()
    return {"owner_ready": owner.ready, "contender_frame": refusal,
            "lock_owner": lock_owner, "lock_after": lock_id(store),
            "current_unchanged": before == current(store),
            "owner_process": process_meta(owner), "contender_process": process_meta(contender)}


def owner_kill_case(name, phase, expected_selector, successor_op):
    _, store, _ = reset_store(name, ["read", "write"])
    owner = start_manager(store, phase=phase)
    gate = owner.operation({"op": "move"})
    at_gate = current(store)
    pid = owner.manager_pid
    reaped = owner.kill_manager().get("still_running") is False
    owner.stop()
    successor = start_manager(store)
    progress = manager_authorize(successor, successor_op)
    after = current(store)
    successor.stop()
    return {"owner_pid": pid, "gate": gate, "at_gate": at_gate,
            "owner_exit": owner.manager_exit, "owner_reaped": reaped,
            "successor_ready": successor.ready, "successor_operation": progress,
            "selected_expected_before_successor": at_gate["selector"] == expected_selector,
            "after_successor": after, "owner_process": process_meta(owner),
            "successor_process": process_meta(successor)}


def unguarded_bypass_case():
    _, store, _ = reset_store("unguarded-bypass", ["read", "write"])
    guarded = start_manager(store)
    lock_before = lock_id(store)
    bypass = start_manager(store, original=True)
    bypass_move = manager_authorize(bypass, "move")
    selected = current(store)
    bypass.stop()
    guarded.stop()
    return {"guarded_pid": guarded.manager_pid, "unguarded_pid": bypass.manager_pid,
            "unguarded_move": bypass_move, "selected": selected,
            "lock_held_inode": lock_before, "lock_after": lock_id(store),
            "processes": [process_meta(guarded), process_meta(bypass)]}


def fd_mutant_case():
    # Fully separate store fixture: the descriptor control may modify its record.
    _, store, _ = reset_store("fd-mutant", ["read", "write"])
    target = store / "protected/record-000001.json"
    fd = os.open(target, os.O_WRONLY | os.O_APPEND)
    mutant = Child([sys.executable, "-I", "-B", "-c",
                    "import os,json,fcntl; fd=int(os.environ['PASS_FD']); mode=fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE; n=os.write(fd,bytes([10])+b'fd-mutant-write'); print(json.dumps({'uid':os.getuid(),'fd':fd,'access_mode':mode,'write_bytes':n}),flush=True)"],
                   WORKER_UID, env={"PASS_FD": str(fd)}, pass_fds=(fd,))
    frame = mutant.line()
    mutant.stop(); os.close(fd)
    return {"fixture": str(store), "passed_fd": fd,
            "worker_status": mutant.status, "mutant_write": frame,
            "record_bytes_after_mutant_hex": target.read_bytes().hex(),
            "process": process_meta(mutant)}


def runtime_facts():
    status = read_status(os.getpid())
    source_files = [MANAGER, MANAGER_VARIANT, OWNER_SUPERVISOR, WORKER_SCRIPT,
                    Path("/opt/probe/driver.py"), L5DIR / "l5_integrated.py",
                    SRC / "l1/l1.py", FIXTURE_PATH]
    layout_paths = [Path("/opt/probe"), Path("/opt/probe/src"),
                    Path("/opt/probe/src/docs"), Path("/opt/probe/src/docs/research"),
                    Path("/opt/probe/src/docs/research/phase-i-sol-integration"),
                    Path("/opt/probe/src/docs/research/phase-i-f1-recovery-repair"),
                    Path("/opt/probe/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle"),
                    Path("/opt/probe/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l1"),
                    L5DIR, L5DIR / "move-cuts", Path("/opt/probe/src/docs/research/phase-i-f1-recovery-repair/l5")]
    layout_paths.extend(path for path in Path("/opt/probe").rglob("*") if path.is_dir())
    layout_paths += source_files
    return {"driver_uid": os.getuid(), "driver_status": status,
            "cap_expected_hex": CAPS_EXPECTED,
            "cap_exact": status.get("CapEff", "").lower() == CAPS_EXPECTED
            and status.get("CapPrm", "").lower() == CAPS_EXPECTED
            and status.get("CapBnd", "").lower() == CAPS_EXPECTED,
            "python": sys.version, "kernel": os.uname().release,
            "native_l5_commit": "51b34aface9340b7e6821b8c40dc62ca38da15e2",
            "image_digest": "sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b",
            "native_source_hashes": {str(p): sha(p.read_bytes()) for p in source_files},
            "layout": {str(p): {"uid": p.stat().st_uid, "gid": p.stat().st_gid,
                                "mode": oct(p.stat().st_mode & 0o777),
                                "is_dir": p.is_dir()} for p in layout_paths}}


def main():
    os.umask(0o077)
    if os.getuid() != 0:
        raise RuntimeError("trusted root driver is not uid 0")
    BASE.mkdir(mode=0o711, parents=True, exist_ok=True)
    (BASE / "cases").mkdir(mode=0o711, exist_ok=True)
    os.chmod(BASE, 0o711); os.chmod(BASE / "cases", 0o711)
    if not runtime_facts()["cap_exact"]:
        raise RuntimeError("driver capabilities differ from CHOWN,DAC_OVERRIDE,SETUID,SETGID")
    raw = {"runtime": runtime_facts(), "cases": {}}
    raw["cases"]["allowed-native-path"] = uid_path_case("allowed", ["read", "write"], False)
    raw["cases"]["moved-attenuated-native-path"] = uid_path_case("attenuated", ["read"], True)
    raw["cases"]["direct-and-descendant-attacks"] = attack_case()
    raw["cases"]["guarded-contender"] = contender_case()
    raw["cases"]["kill-before-selector"] = owner_kill_case(
        "kill-before-selector", "after_record", "record-000001.json", "activate")
    raw["cases"]["kill-after-selector"] = owner_kill_case(
        "kill-after-selector", "after_selector", "record-000002.json", "activate")
    raw["cases"]["unguarded-same-uid-bypass"] = unguarded_bypass_case()
    raw["cases"]["writable-fd-mutant"] = fd_mutant_case()
    raw["execution"] = "PASS"
    print(json.dumps(raw, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
