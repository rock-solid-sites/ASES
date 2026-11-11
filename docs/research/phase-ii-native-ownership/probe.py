#!/usr/bin/env python3
"""Bounded native F1→F3 ownership histories; no imported graph or alias."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REPAIR = REPO / "docs/research/phase-i-f1-recovery-repair"
REPAIRED_F1 = REPAIR / "repaired_service.py"
L5 = REPO / "docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5"
L6 = REPO / "docs/research/phase-i-sol-integration/evidence/sources/l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory"
OWNER_CLI = HERE / "owner_cli.py"
NATIVE_SINK = HERE / "native_sink.py"
UNIX_TRANSPORT = HERE / "unix_transport.py"
NATIVE_HELPERS_PATH = REPO / "docs/research/phase-i-sol-integration/native.py"
CONTENT = "accepted\x00one\n"
PROCESSES: list[dict] = []


def load_module(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pinned helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


repair = load_module("ownership_f1_repair_probe", REPAIR / "probe.py")
native = load_module("ownership_native_helpers", NATIVE_HELPERS_PATH)
unix_transport = load_module("ownership_unix_transport", UNIX_TRANSPORT)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_from_frame(frame: dict) -> dict:
    """Unwrap the fixed CLI response envelope while retaining the raw frame."""
    for key in ("reply", "view", "snapshot"):
        value = frame.get(key)
        if isinstance(value, dict) and ("result" in value or "state" in value or "selector" in value):
            return value
    return frame


def file_record(path: Path) -> dict:
    raw = path.read_bytes()
    st = path.stat()
    return {"raw_hex": raw.hex(), "sha256": sha(raw), "size": len(raw), "dev": st.st_dev, "ino": st.st_ino}


def tree(root: Path) -> dict:
    result = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            result[str(path.relative_to(root))] = file_record(path)
    return result


def f1_raw(dbpath: Path) -> dict:
    """Read the real F1 selected subject and retained observations read-only."""
    with sqlite3.connect(dbpath.resolve().as_uri() + "?mode=ro", uri=True) as db:
        version, raw_view = db.execute("SELECT version,view FROM kernel WHERE id=1").fetchone()
        selected = db.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()
        retained = [row[0] for row in db.execute("SELECT record FROM retained_observations ORDER BY record")]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    view = json.loads(raw_view)
    observation = json.loads(selected[0]) if selected else None
    return {"version": version, "view": view, "selected": observation, "retained": retained,
            "pair": None if observation is None else {"accepted_content": view["content"], "required": observation["required"]},
            "integrity": integrity}


class OwnerProcess:
    """One real owner CLI process, retaining exact stdio frames and exit state."""

    def __init__(self, root: Path, recover=False, gate: str | None = None):
        argv = [sys.executable, "-B", str(OWNER_CLI), "--owner", str(root)]
        if recover:
            argv.append("--recover")
        if gate:
            argv += ["--gate", gate]
        self.meta = {"argv": argv, "start_ns": time.monotonic_ns(), "frames": []}
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, bufsize=0)
        self.meta["pid"] = self.p.pid
        PROCESSES.append(self.meta)
        ready = self.read(timeout=10)
        self.meta["ready"] = ready
        self.last_frame = ready

    def read(self, timeout=10):
        if not select.select([self.p.stdout], [], [], timeout)[0]:
            raise TimeoutError(f"owner frame timeout pid={self.p.pid}")
        raw = self.p.stdout.readline(4 * 1024 * 1024)
        if not raw:
            raise RuntimeError("owner EOF: " + self.p.stderr.read().decode(errors="replace")[-4096:])
        value = json.loads(raw)
        self.meta["frames"].append({"ns": time.monotonic_ns(), "raw": raw.decode(errors="replace"), "value": value})
        return value

    def call(self, request: dict):
        self.p.stdin.write((canonical(request) + "\n").encode())
        self.p.stdin.flush()
        self.last_frame = self.read()
        return self.last_frame

    def snapshot(self):
        return self.last_frame.get("snapshot")

    def gate_call(self, request: dict, stage: str):
        value = self.call(dict(request, gate=stage))
        actual = value.get("phase", value.get("stage"))
        if value.get("event") != "GATE" or actual != stage:
            raise RuntimeError(f"expected native gate {stage}, got {value!r}")
        return value

    def resume(self):
        self.p.stdin.write(b"continue\n")
        self.p.stdin.flush()
        return self.read()

    def close(self, kill=False):
        if "exit" in self.meta:
            return self.meta
        if self.p.poll() is None:
            if kill:
                self.p.kill()
            else:
                self.p.stdin.write(b'{"op":"stop"}\n')
                self.p.stdin.flush()
        self.meta["exit"] = self.p.wait(timeout=10)
        self.meta["exit_ns"] = time.monotonic_ns()
        self.meta["stdout_tail"] = self.p.stdout.read().decode(errors="replace")[-4096:]
        self.meta["stderr"] = self.p.stderr.read().decode(errors="replace")[-8192:]
        self.p.stdin.close()
        self.p.stdout.close()
        self.p.stderr.close()
        return self.meta


class NativeF4:
    """Real parent-owned F4/witness processes using only the native-owner profile."""
    def __init__(self, root: Path, owner_root: Path, witness_root: str, gate: str | None = None):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=False)
        os.chmod(self.root, 0o700)
        # Linux AF_UNIX pathname sockets have a short sun_path limit. Keep
        # only endpoints in a fresh private /tmp directory; durable journal,
        # config, and raw evidence remain under this capture's output root.
        self.socket_dir = Path(tempfile.mkdtemp(prefix="a4u-", dir="/tmp"))
        os.chmod(self.socket_dir, 0o700)
        self.socket_dir_meta = {
            "path": str(self.socket_dir), "uid": os.stat(self.socket_dir).st_uid,
            "mode": oct(os.stat(self.socket_dir).st_mode & 0o777),
            "dev": os.stat(self.socket_dir).st_dev, "ino": os.stat(self.socket_dir).st_ino,
        }
        self.journal = self.root / "sink-effects.jsonl"
        self.config_path = self.root / "native-config.json"
        self.witness_root = witness_root
        self.config = {"profile": "native-f3-owner-v1", "owner_root": str(owner_root)}
        if gate:
            self.config["gate"] = gate
        self.config_path.write_text(canonical(self.config) + "\n")
        self.witness_socket = self.socket_dir / "witness.sock"
        self.witness = UnixChild([sys.executable, "-B", str(NATIVE_SINK), "--witness", witness_root],
                                self.witness_socket)
        self.witness_port = self.witness.ready.get("port", 0)
        self.witness_init = self.http(self.witness_socket, "/init", dict(
            root=witness_root, nonce="native-init-" + str(time.monotonic_ns()),
            cut=dict(authority=dict(created=False, granted=False, active=False,
                                    authority_version=0, holder="old"),
                     journal_sha256=sha(b""))))
        self.calls = []
        self.start(recover=False)
        self.lifecycle_calls = [self.call("/create", {}), self.call("/grant", {}),
                                self.call("/activate", {"authority_version": 1})]

    def start(self, recover: bool):
        socket_name = "sink-cold.sock" if recover else "sink.sock"
        self.sink_socket = self.socket_dir / socket_name
        argv = [sys.executable, "-B", str(NATIVE_SINK), "--sink", "recover" if recover else "fresh",
                str(self.journal), str(self.witness_port), "published-cut", self.witness_root,
                str(self.config_path)]
        self.sink = UnixChild(argv, self.sink_socket, self.witness_socket)
        self.port = self.sink.ready.get("port", 0)
        return self.sink.ready

    @staticmethod
    def http(socket_path: Path, path: str, request: dict | None = None):
        method = "GET" if request is None else "POST"
        status, body = unix_transport.call_unix(socket_path, method, path, request)
        return {"status": status, "body": body, "raw": canonical(body)}

    def call(self, path: str, request: dict):
        before = native.blob(self.journal)
        try:
            response = self.http(self.sink_socket, path, request)
        except Exception as error:
            response = {"transport_error": type(error).__name__ + ":" + str(error)}
        value = {"path": path, "request": request, "before": before,
                 "after": native.blob(self.journal), "response": response}
        self.calls.append(value)
        return value

    def witness_call(self, path: str, **fields):
        return self.http(self.witness_socket, path,
                         dict(root=self.witness_root, nonce="native-" + str(time.monotonic_ns()), **fields))

    def snapshot(self):
        try:
            status = self.http(self.sink_socket, "/status")
        except Exception as error:
            status = {"transport_error": type(error).__name__ + ":" + str(error)}
        return {"journal": native.blob(self.journal), "sink_status": status,
                "witness_status": self.http(self.witness_socket, "/status"),
                "calls": self.calls, "sink_process": self.sink.meta,
                "witness_process": self.witness.meta, "config": self.config,
                "socket_dir": self.socket_dir_meta,
                "config_file_sha256": sha(self.config_path.read_bytes())}

    def submit(self, envelope: dict, authority_version: int = 1):
        return self.call("/submit", dict(authority_version=authority_version,
                                          request_id=envelope["request_id"],
                                          payload=canonical(envelope)))

    def cold_restart(self):
        self.dead_sink = self.sink.meta
        self.config.pop("gate", None)
        self.config_path.write_text(canonical(self.config) + "\n")
        return self.start(recover=True)

    def close(self, kill=True):
        if getattr(self, "sink", None):
            self.sink.close(kill)
        self.witness.close(True)


class UnixChild:
    """Native source process on one private AF_UNIX socket with raw stdio capture."""
    def __init__(self, argv, listen_socket: Path, witness_socket: Path | None = None):
        env = os.environ.copy()
        env["ASES_NATIVE_LISTEN_SOCKET"] = str(listen_socket)
        if witness_socket is not None:
            env["ASES_NATIVE_WITNESS_SOCKET"] = str(witness_socket)
        else:
            env.pop("ASES_NATIVE_WITNESS_SOCKET", None)
        self.meta = {"argv": [str(v) for v in argv], "start_ns": time.monotonic_ns(),
                     "listen_socket": str(listen_socket),
                     "witness_socket": None if witness_socket is None else str(witness_socket),
                     "frames": []}
        self.p = subprocess.Popen(self.meta["argv"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  env=env, bufsize=0)
        self.meta["pid"] = self.p.pid
        PROCESSES.append(self.meta)
        self.ready = self.read_json(10)
        self.meta["ready"] = self.ready
        try:
            st = os.lstat(listen_socket)
            self.meta["listen_socket_stat"] = {"dev": st.st_dev, "ino": st.st_ino,
                                               "uid": st.st_uid, "mode": oct(st.st_mode & 0o777)}
        except FileNotFoundError:
            self.meta["listen_socket_stat"] = None
        if witness_socket is not None:
            try:
                st = os.lstat(witness_socket)
                self.meta["witness_socket_stat"] = {"dev": st.st_dev, "ino": st.st_ino,
                                                    "uid": st.st_uid, "mode": oct(st.st_mode & 0o777)}
            except FileNotFoundError:
                self.meta["witness_socket_stat"] = None

    def read_json(self, timeout=10):
        if not select.select([self.p.stdout], [], [], timeout)[0]:
            raise TimeoutError("native AF_UNIX child readiness/frame timeout")
        raw = self.p.stdout.readline(4 * 1024 * 1024)
        if not raw:
            raise RuntimeError("native AF_UNIX child EOF: " + self.p.stderr.read().decode(errors="replace")[-4096:])
        value = json.loads(raw)
        self.meta["frames"].append({"ns": time.monotonic_ns(), "raw": raw.decode(errors="replace"), "value": value})
        return value

    def read(self, timeout=20):
        if not select.select([self.p.stdout], [], [], timeout)[0]:
            raise TimeoutError("native child frame timeout")
        raw = self.p.stdout.readline(4 * 1024 * 1024)
        line = raw.decode(errors="replace")
        if raw:
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                value = None
            self.meta["frames"].append({"ns": time.monotonic_ns(), "raw": line, "value": value})
        return line

    def close(self, kill=True):
        if "exit" in self.meta:
            return self.meta
        if self.p.poll() is None:
            if kill:
                self.p.kill()
            else:
                if self.p.stdin is not None:
                    self.p.stdin.write(b'{"op":"stop"}\n')
        self.meta["exit"] = self.p.wait(timeout=10)
        self.meta["exit_ns"] = time.monotonic_ns()
        self.meta["stdout_tail"] = self.p.stdout.read().decode(errors="replace")[-4096:]
        self.meta["stderr"] = self.p.stderr.read().decode(errors="replace")[-8192:]
        if self.p.stdin is not None:
            self.p.stdin.close()
        return self.meta


def native_envelope(snapshot: dict, request_id: str) -> dict:
    state = snapshot["state"]
    owner = state["native_owner"]
    registration = next(r for r in owner["registrations"] if r["id"] == owner["selected"])
    return {"kind": "use-current-descendant", "import_id": registration["id"],
            "epoch": owner["epoch"], "pair": registration["pair"],
            "l5": snapshot["generation"], "request_id": request_id}


def setup_native_f3(case_root: Path, world="A", activate=True) -> dict:
    case_root.mkdir(parents=True, exist_ok=False)
    f1root, ownerroot = case_root / "f1", case_root / "owner"
    f1 = setup_f1(f1root)
    establishment = establish_owner(ownerroot, f1root / "store.sqlite")
    bundle = repair.configuration(world, CONTENT, True)["acceptance_bundle"]
    accepted_f1 = native_f1_accept(f1root, bundle, CONTENT)
    owner = OwnerProcess(ownerroot)
    accepted_f3 = owner.call({"op": "accept"})
    activated = owner.call({"op": "activate"}) if activate else None
    result = {"f1": f1, "f1_accept": accepted_f1, "establish": establishment,
              "owner_accept": accepted_f3, "activation": activated,
              "owner_ready": owner.meta["ready"], "owner_process": owner.meta,
              "owner_root": str(ownerroot), "f1_root": str(f1root)}
    owner.close()
    result["owner_process"] = owner.meta
    result["owner_tree_before_f4"] = tree(ownerroot)
    return result


def preparation_crash(out: Path, label: str, gate: str) -> dict:
    """Kill a real owner at either side of the native L6 put commit point."""
    root = out / "state" / label
    root.mkdir(parents=True)
    f1root, ownerroot = root / "f1", root / "owner"
    boot = setup_f1(f1root)
    before = f1_raw(f1root / "store.sqlite")
    establishment = establish_owner(ownerroot, f1root / "store.sqlite")
    owner = OwnerProcess(ownerroot)
    sealed = owner.call({"op": "seal"})
    child_disposed = owner.call({"op": "dispose_child", "unit": "D"})
    interrupted = owner.call({"op": "prepare_candidate", "payload": "unaccepted-native",
                              "gate": gate})
    gate_frame = interrupted
    if interrupted.get("event") != "GATE":
        raise RuntimeError(f"prepare crash did not reach native gate {gate}: {interrupted!r}")
    if gate == "material-before-catalog" and interrupted.get("phase") != "file-fsynced-row-uncommitted":
        raise RuntimeError(f"expected actual L6 precommit GATE, got {interrupted!r}")
    if gate == "material-prepared" and interrupted.get("phase", interrupted.get("stage")) != "material-prepared":
        raise RuntimeError(f"expected post-catalog/pre-CURRENT gate, got {interrupted!r}")
    killed = owner.close(kill=True)
    after_kill_tree = tree(ownerroot)
    cold = OwnerProcess(ownerroot)
    cold_view = cold.snapshot()
    if gate == "material-before-catalog":
        name = "objecta"
        removal_before = cold.call({"op": "remove"})
        repeat_before = cold.call({"op": "prepare_candidate", "payload": "second"})
        dispositions = [cold.call({"op": "dispose_unknown", "name": name})]
        cleanup = cold.call({"op": "cleanup"})
    else:
        name = "objecta"
        removal_before = cold.call({"op": "remove"})
        repeat_before = cold.call({"op": "prepare_candidate", "payload": "second"})
        names = [name]
        second = repeat_before.get("reply", {}).get("name")
        if repeat_before.get("reply", {}).get("result") == "COMMITTED" and second:
            names.append(second)
        dispositions = [cold.call({"op": "dispose_candidate", "name": candidate})
                        for candidate in names]
        cleanup = cold.call({"op": "cleanup"})
    removed = cold.call({"op": "remove"})
    final_view = cold.call({"op": "read"})["reply"]["snapshot"]
    cold.close()
    after = f1_raw(f1root / "store.sqlite")
    return {"root": str(ownerroot), "f1_root": str(f1root), "f1_boot": boot,
            "f1_before": before, "establish": establishment, "sealed": sealed,
            "child_disposed": child_disposed, "gate": gate, "gate_frame": gate_frame,
            "killed_owner": killed, "owner_tree_after_kill": after_kill_tree,
            "cold_ready": cold.meta["ready"], "cold_initial_view": cold_view,
            "remove_before_disposition": removal_before,
            "prepare_before_disposition": repeat_before,
            "explicit_disposition": dispositions, "cleanup": cleanup,
            "remove_after_disposition": removed, "final_view": final_view,
            "owner_tree_final": tree(ownerroot), "f1_after": after}


def candidate_removal_race(out: Path, label: str, creator_first: bool) -> dict:
    """Hold real owner/L6 guards at a shared eligible state and contend."""
    root = out / "state" / label
    root.mkdir(parents=True)
    f1root, ownerroot = root / "f1", root / "owner"
    setup = setup_f1(f1root)
    establishment = establish_owner(ownerroot, f1root / "store.sqlite")
    prepare = OwnerProcess(ownerroot)
    sealed = prepare.call({"op": "seal"})
    child_disposed = prepare.call({"op": "dispose_child", "unit": "D"})
    prepare.close()
    if creator_first:
        creator = OwnerProcess(ownerroot)
        gate = creator.call({"op": "prepare_candidate", "payload": "race-candidate",
                             "gate": "material-before-catalog"})
        if gate.get("event") != "GATE" or gate.get("phase") != "file-fsynced-row-uncommitted":
            raise RuntimeError("creator-first race did not reach native L6 precommit gate")
        contender = OwnerProcess(ownerroot)
        competing_remove = contender.call({"op": "remove"})
        creator_commit = creator.resume()
        creator.close()
        contender.close()
        after_create = OwnerProcess(ownerroot)
        remove_after_create = after_create.call({"op": "remove"})
        dispose = after_create.call({"op": "dispose_candidate", "name": "objecta"})
        cleanup = after_create.call({"op": "cleanup"})
        final_remove = after_create.call({"op": "remove"})
        final_view = after_create.call({"op": "read"})["reply"]["snapshot"]
        after_create.close()
        return {"root": str(ownerroot), "f1_root": str(f1root), "f1_setup": setup,
                "establish": establishment, "seal": sealed, "dispose_child": child_disposed,
                "order": "creator-first", "creator_gate": gate,
                "contender_remove_while_busy": competing_remove, "creator_commit": creator_commit,
                "remove_after_create": remove_after_create, "dispose_candidate": dispose,
                "cleanup": cleanup, "remove_after_disposition": final_remove,
                "final_view": final_view, "owner_tree": tree(ownerroot),
                "f1_after": f1_raw(f1root / "store.sqlite")}
    remover = OwnerProcess(ownerroot)
    gate = remover.gate_call({"op": "remove"}, "domain-removal-selected")
    contender = OwnerProcess(ownerroot)
    competing_create = contender.call({"op": "prepare_candidate", "payload": "race-candidate"})
    remover_commit = remover.resume()
    remover.close()
    contender.close()
    cold = OwnerProcess(ownerroot)
    create_after_remove = cold.call({"op": "prepare_candidate", "payload": "race-candidate"})
    final_view = cold.call({"op": "read"})["reply"]["snapshot"]
    cold.close()
    return {"root": str(ownerroot), "f1_root": str(f1root), "f1_setup": setup,
            "establish": establishment, "seal": sealed, "dispose_child": child_disposed,
            "order": "remover-first", "remover_gate": gate,
            "contender_create_while_busy": competing_create, "remover_commit": remover_commit,
            "create_after_remove": create_after_remove, "final_view": final_view,
            "owner_tree": tree(ownerroot), "f1_after": f1_raw(f1root / "store.sqlite")}


def accepted_before_reply(out: Path, label: str) -> dict:
    root = out / "state" / label
    root.mkdir(parents=True)
    f1root, ownerroot = root / "f1", root / "owner"
    f1_setup = setup_f1(f1root)
    before = f1_raw(f1root / "store.sqlite")
    establishment = establish_owner(ownerroot, f1root / "store.sqlite")
    bundle = repair.configuration("A", CONTENT, True)["acceptance_bundle"]
    f1_accept = native_f1_accept(f1root, bundle, CONTENT)
    f1_after_accept = f1_raw(f1root / "store.sqlite")
    owner = OwnerProcess(ownerroot)
    interrupted = owner.call({"op": "accept", "gate": "acceptance-selected"})
    if interrupted.get("event") != "GATE" or interrupted.get("phase", interrupted.get("stage")) != "acceptance-selected":
        raise RuntimeError("F3 acceptance did not reach actual CURRENT-selected/pre-ACK gate")
    killed = owner.close(kill=True)
    tree_after_kill = tree(ownerroot)
    cold = OwnerProcess(ownerroot)
    cold_view = cold.snapshot()
    retry = cold.call({"op": "accept"})
    after_retry = cold.snapshot()
    cold.close()
    return {"root": str(ownerroot), "f1_root": str(f1root), "f1_setup": f1_setup,
            "f1_before": before, "establish": establishment, "f1_accept": f1_accept,
            "f1_after_accept": f1_after_accept, "gate_frame": interrupted,
            "killed_owner": killed, "owner_tree_after_kill": tree_after_kill,
            "cold_view": cold_view, "retry": retry, "after_retry": after_retry,
            "owner_tree_final": tree(ownerroot), "f1_after": f1_raw(f1root / "store.sqlite")}


def disposition_crash(out: Path, label: str, gate: str) -> dict:
    root = out / "state" / label
    root.mkdir(parents=True)
    f1root, ownerroot = root / "f1", root / "owner"
    f1_setup = setup_f1(f1root)
    before = f1_raw(f1root / "store.sqlite")
    establishment = establish_owner(ownerroot, f1root / "store.sqlite")
    bundle = repair.configuration("A", CONTENT, True)["acceptance_bundle"]
    f1_accept = native_f1_accept(f1root, bundle, CONTENT)
    f1_after_accept = f1_raw(f1root / "store.sqlite")
    owner = OwnerProcess(ownerroot)
    accepted = owner.call({"op": "accept"})
    registration = accepted.get("reply", accepted)["registration"]["id"]
    sealed = owner.call({"op": "seal"})
    child = owner.call({"op": "dispose_child", "unit": "D"})
    interrupted = owner.call({"op": "dispose_content", "id": registration, "gate": gate})
    expected_phase = "disposition-committed-before-unlink-reply" if gate == "inventory-disposed" else gate
    if interrupted.get("event") != "GATE" or interrupted.get("phase", interrupted.get("stage")) != expected_phase:
        raise RuntimeError(f"disposition did not reach expected actual gate {expected_phase}: {interrupted!r}")
    killed = owner.close(kill=True)
    tree_after_kill = tree(ownerroot)
    cold = OwnerProcess(ownerroot)
    cold_view = cold.snapshot()
    cleanup = cold.call({"op": "cleanup"})
    removal = cold.call({"op": "remove"})
    final = cold.call({"op": "read"})["reply"]["snapshot"]
    cold.close()
    return {"root": str(ownerroot), "f1_root": str(f1root), "f1_setup": f1_setup,
            "f1_before": before, "establish": establishment, "f1_accept": f1_accept,
            "f1_after_accept": f1_after_accept, "accepted": accepted, "registration_id": registration,
            "seal": sealed, "dispose_child": child, "gate": gate, "gate_frame": interrupted,
            "killed_owner": killed, "owner_tree_after_kill": tree_after_kill,
            "cold_view": cold_view, "cleanup": cleanup, "remove": removal,
            "final_view": final, "owner_tree_final": tree(ownerroot),
            "f1_after": f1_raw(f1root / "store.sqlite")}


def removal_selected_crash(out: Path, label: str) -> dict:
    root = out / "state" / label
    root.mkdir(parents=True)
    f1root, ownerroot = root / "f1", root / "owner"
    f1_setup = setup_f1(f1root)
    before = f1_raw(f1root / "store.sqlite")
    establishment = establish_owner(ownerroot, f1root / "store.sqlite")
    owner = OwnerProcess(ownerroot)
    sealed = owner.call({"op": "seal"})
    child = owner.call({"op": "dispose_child", "unit": "D"})
    interrupted = owner.call({"op": "remove", "gate": "domain-removal-selected"})
    if interrupted.get("event") != "GATE" or interrupted.get("phase", interrupted.get("stage")) != "domain-removal-selected":
        raise RuntimeError("logical owner removal did not reach native selected/pre-cleanup gate")
    killed = owner.close(kill=True)
    tree_after_kill = tree(ownerroot)
    cold = OwnerProcess(ownerroot)
    cold_view = cold.snapshot()
    cleanup = cold.call({"op": "cleanup"})
    final = cold.call({"op": "read"})["reply"]["snapshot"]
    cold.close()
    return {"root": str(ownerroot), "f1_root": str(f1root), "f1_setup": f1_setup,
            "f1_before": before, "establish": establishment, "seal": sealed,
            "dispose_child": child, "gate_frame": interrupted, "killed_owner": killed,
            "owner_tree_after_kill": tree_after_kill, "cold_view": cold_view,
            "cleanup": cleanup, "final_view": final, "owner_tree_final": tree(ownerroot),
            "f1_after": f1_raw(f1root / "store.sqlite")}


def setup_f1(root: Path) -> dict:
    """Create actual F1 service after bootstrap/grant, before test-content accept."""
    root.mkdir(parents=True, exist_ok=False)
    dbpath = root / "store.sqlite"
    initialize = repair.ORIGINAL.parent.parent.parent / "kernel-0/kernel0_recovery_service.py"
    config = {"path": str(dbpath), "root": "work", "profile": "independent"}
    subprocess.run([sys.executable, "-B", str(initialize), "--initialize", json.dumps(config)],
                   check=True, timeout=5, capture_output=True)
    with sqlite3.connect(dbpath) as db:
        db.execute("CREATE TABLE consumer_observations(id INTEGER PRIMARY KEY CHECK(id=1),record TEXT NOT NULL)")
    subprocess.run([sys.executable, "-B", str(REPAIRED_F1), "--prepare", str(dbpath)],
                   check=True, timeout=5, capture_output=True)
    manager = repair.Holder(REPAIRED_F1, root, repair.configuration("bootstrap", repair.B, True), -1)
    try:
        established = manager.call("establish")
        granted = manager.call("grant", value=7)
    finally:
        manager.close()
    boot = {"establish": established, "grant": granted}
    state = f1_raw(root / "store.sqlite")
    if state["integrity"] != "ok" or state["selected"] is None or state["pair"]["accepted_content"] != repair.B:
        raise RuntimeError("native F1 bootstrap was not the expected pre-test-accept state")
    return {"boot": boot, "state": state, "source": str(REPAIRED_F1),
            "source_sha256": sha(REPAIRED_F1.read_bytes()), "database": file_record(root / "store.sqlite")}


def native_f1_accept(root: Path, bundle: dict, content: str) -> dict:
    """Use the pinned F1 repaired service's real accept process and SQLite transaction."""
    holder = repair.Holder(REPAIRED_F1, root, dict(acceptance_bundle=bundle))
    try:
        response = holder.call("accept", content)
        meta = {"response": response, "operation": holder.meta["operations"][-1],
                "process": holder.meta}
    finally:
        holder.close()
    return meta


def establish_owner(root: Path, f1_db: Path, created_by="ases4-test-issuer", project="native-owner-probe") -> dict:
    argv = [sys.executable, "-B", str(OWNER_CLI), "--establish", str(root), str(f1_db), created_by, project]
    start = time.monotonic_ns()
    child = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = child.communicate(timeout=20)
    exit_code = child.returncode
    frame = None
    if stdout.strip():
        try:
            frame = json.loads(stdout.strip().splitlines()[-1])
        except json.JSONDecodeError:
            pass
    record = {"argv": argv, "pid": child.pid, "start_ns": start, "end_ns": time.monotonic_ns(),
              "exit": exit_code, "stdout": stdout, "stderr": stderr, "frame": frame}
    PROCESSES.append({"pid": child.pid, "argv": argv, "start_ns": start, "exit_ns": record["end_ns"],
                      "exit": exit_code, "frames": [{"ns": record["end_ns"], "raw": stdout,
                                                                  "value": frame}]})
    if exit_code != 0 or not isinstance(frame, dict):
        raise RuntimeError("native owner establishment failed: " + json.dumps(record, sort_keys=True))
    return record


def source_manifest() -> dict:
    sources = {
        "f1_repaired": REPAIRED_F1,
        "f1_original": repair.ORIGINAL,
        "l5_manager": L5 / "move-cuts/worker.py",
        "l5_core": L5 / "l5_integrated.py",
        "l6_store": L6 / "store.py",
        "l6_race_store": L6 / "race/race_store.py",
        "native_owner": HERE / "native_owner.py",
        "owner_cli": OWNER_CLI,
        "native_f4_sink": HERE / "native_sink.py",
        "unix_transport": UNIX_TRANSPORT,
    }
    return {name: {"path": str(path), "sha256": sha(path.read_bytes())}
            for name, path in sources.items() if path.is_file()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing nonempty output directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    raw = {"schema": "ases4-native-owner-probe-v1", "started_ns": time.monotonic_ns(),
           "sources": source_manifest(), "cases": {}, "processes": PROCESSES}
    try:
        # First discriminator: real F1 evidence, then owner-issued F3 identities
        # and real native L5/L6 transitions with no parent F4 route configured.
        state = out / "state" / "native-no-f4"
        state.mkdir(parents=True)
        f1root = state / "f1"
        ownerroot = state / "owner"
        f1 = setup_f1(f1root)
        raw["f1_boot"] = f1
        raw["f1_before_owner"] = f1_raw(f1root / "store.sqlite")
        raw["establish"] = establish_owner(ownerroot, f1root / "store.sqlite")
        initial_bundle = repair.configuration("A", CONTENT, True)["acceptance_bundle"]
        raw["native_f1_accept"] = native_f1_accept(f1root, initial_bundle, CONTENT)
        raw["f1_after_accept"] = f1_raw(f1root / "store.sqlite")
        owner = OwnerProcess(ownerroot)
        raw["owner_ready"] = owner.meta["ready"]
        case = {"root": str(ownerroot), "initial_view": owner.snapshot()}
        case["caller_pair_acceptance_attempt"] = owner.call({
            "op": "accept", "pair": {"accepted_content": CONTENT,
                                      "required": {"project": "caller-forged"}}})
        case["view_after_forged_acceptance"] = owner.snapshot()
        case["accept_first"] = owner.call({"op": "accept"})
        case["view_after_first"] = owner.snapshot()
        case["accept_duplicate"] = owner.call({"op": "accept"})
        case["view_after_duplicate"] = owner.snapshot()
        changed_bundle = repair.configuration("C", CONTENT, True)["acceptance_bundle"]
        case["native_f1_same_bytes_changed_world"] = native_f1_accept(f1root, changed_bundle, CONTENT)
        case["f1_after_world_change"] = f1_raw(f1root / "store.sqlite")
        case["accept_changed_world"] = owner.call({"op": "accept"})
        case["view_after_changed_world"] = owner.snapshot()
        state_view = payload_from_frame(case["view_after_changed_world"])
        owner_state = state_view.get("state", state_view)
        native_record = owner_state.get("native_owner", {})
        registration_ids = [r["id"] for r in native_record.get("registrations", [])]
        for response in (case["accept_first"], case["accept_changed_world"]):
            value = payload_from_frame(response)
            registration_id = value.get("registration_id")
            if registration_id and registration_id not in registration_ids:
                registration_ids.append(registration_id)
        case["registration_ids"] = registration_ids
        case["seal"] = owner.call({"op": "seal"})
        case["move"] = owner.call({"op": "move"})
        case["activate"] = owner.call({"op": "activate"})
        case["remove_blocked_active_domain"] = owner.call({"op": "remove"})
        case["snapshot_after_active_remove_block"] = owner.call({"op": "read"})["reply"]["snapshot"]
        case["seal_for_disposition"] = owner.call({"op": "seal"})
        case["remove_blocked_live_child"] = owner.call({"op": "remove"})
        case["snapshot_after_child_remove_block"] = owner.call({"op": "read"})["reply"]["snapshot"]
        case["dispose_child"] = owner.call({"op": "dispose_child", "unit": "D"})
        case["remove_blocked_live_material"] = owner.call({"op": "remove"})
        case["snapshot_after_material_remove_block"] = owner.call({"op": "read"})["reply"]["snapshot"]
        case["dispose_content"] = []
        for registration_id in registration_ids:
            case["dispose_content"].append(owner.call({"op": "dispose_content", "id": registration_id}))
        case["remove"] = owner.call({"op": "remove"})
        case["source_after_acceptance"] = f1_raw(f1root / "store.sqlite")
        raw["cases"]["native-no-f4"] = case
        raw["cases"]["native-no-f4"]["owner_tree_after_operations"] = tree(ownerroot)
        owner.close()
        raw["cases"]["native-no-f4"]["owner_process"] = owner.meta
        raw["cases"]["native-no-f4"]["owner_tree_after_close"] = tree(ownerroot)
        # Constructor/read is nonmutating. Recovery is deliberately omitted
        # after logical removal; removed domains are not eligible to recover.
        readback = OwnerProcess(ownerroot)
        raw["cases"]["native-no-f4"]["cold_ready"] = readback.meta["ready"]
        raw["cases"]["native-no-f4"]["cold_view"] = readback.snapshot()
        readback.close()
        raw["cases"]["native-no-f4"]["cold_process"] = readback.meta
        raw["cases"]["native-no-f4"]["f1_after_remove"] = f1_raw(f1root / "store.sqlite")
        raw["cases"]["native-no-f4"]["owner_tree_final"] = tree(ownerroot)

        # Native L6 interruption controls on opposite sides of its catalog
        # commit. Both require explicit, digest-bound disposition before the
        # issuer may complete removal.
        raw["cases"]["native-unknown-precommit"] = preparation_crash(
            out, "native-unknown-precommit", "material-before-catalog")
        raw["cases"]["native-candidate-after-catalog"] = preparation_crash(
            out, "native-candidate-after-catalog", "material-prepared")
        raw["cases"]["native-candidate-creator-first"] = candidate_removal_race(
            out, "native-candidate-creator-first", True)
        raw["cases"]["native-candidate-remover-first"] = candidate_removal_race(
            out, "native-candidate-remover-first", False)
        raw["cases"]["native-acceptance-selected-crash"] = accepted_before_reply(
            out, "native-acceptance-selected-crash")
        raw["cases"]["native-disposition-selected-crash"] = disposition_crash(
            out, "native-disposition-selected-crash", "disposition-selected")
        raw["cases"]["native-inventory-disposed-crash"] = disposition_crash(
            out, "native-inventory-disposed-crash", "inventory-disposed")
        raw["cases"]["native-removal-selected-crash"] = removal_selected_crash(
            out, "native-removal-selected-crash")

        # Integrate the parent-owned real F4 sink: one authorized append, a
        # caller-forged F1-world denial, then a fresh post-move D-write denial.
        f4root = out / "state" / "native-f4-authorized-denied"
        prepared = setup_native_f3(f4root, world="A", activate=True)
        f4_owner = Path(prepared["owner_root"])
        owner_snapshot = prepared["owner_ready"]["snapshot"]
        witness_root = owner_snapshot["state"]["native_owner"]["domain_id"]
        f4 = NativeF4(f4root / "f4", f4_owner, witness_root)
        attached_owner = OwnerProcess(f4_owner)
        attached_snapshot = attached_owner.call({"op": "read"})["reply"]["snapshot"]
        authorized_envelope = native_envelope(attached_snapshot, witness_root + ":authorized-1")
        stale_epoch_envelope = dict(authorized_envelope,
                                    request_id=witness_root + ":stale-epoch",
                                    epoch=authorized_envelope["epoch"] - 1)
        stale_epoch_call = f4.submit(stale_epoch_envelope)
        stale_selector_envelope = dict(authorized_envelope,
                                       request_id=witness_root + ":stale-selector",
                                       l5=prepared["owner_accept"]["reply"]["snapshot"]["generation"])
        stale_selector_call = f4.submit(stale_selector_envelope)
        owner_after_stale = attached_owner.call({"op": "read"})["reply"]["snapshot"]
        authorized_call = f4.submit(authorized_envelope)
        owner_after_authorized = attached_owner.call({"op": "read"})["reply"]["snapshot"]
        forged = native_envelope(owner_after_authorized, witness_root + ":forged-world")
        forged["pair"] = dict(forged["pair"], required=dict(forged["pair"]["required"],
                                                                project="caller-forged-world"))
        forged_call = f4.submit(forged)
        transitions = {"seal": attached_owner.call({"op": "seal"}),
                       "move": attached_owner.call({"op": "move"}),
                       "activate": attached_owner.call({"op": "activate"})}
        after_move = attached_owner.call({"op": "read"})["reply"]["snapshot"]
        denied_envelope = native_envelope(after_move, witness_root + ":denied-after-move")
        denied_call = f4.submit(denied_envelope)
        owner_after_denial = attached_owner.call({"op": "read"})["reply"]["snapshot"]
        raw["cases"]["native-f4-authorized-denied"] = {
            "setup": prepared, "witness_root": witness_root, "f4_lifecycle": f4.lifecycle_calls,
            "f4_ready": f4.sink.ready, "witness_init": f4.witness_init,
            "attached_snapshot": attached_snapshot, "authorized_envelope": authorized_envelope,
            "stale_epoch_envelope": stale_epoch_envelope, "stale_epoch_call": stale_epoch_call,
            "stale_selector_envelope": stale_selector_envelope,
            "stale_selector_call": stale_selector_call, "owner_after_stale": owner_after_stale,
            "authorized_call": authorized_call, "owner_after_authorized": owner_after_authorized,
            "forged_envelope": forged, "forged_call": forged_call,
            "transitions": transitions, "after_move_snapshot": after_move,
            "denied_envelope": denied_envelope, "denied_call": denied_call,
            "owner_after_denial": owner_after_denial, "f4_snapshot": f4.snapshot(),
            "f4_tree": tree(f4.root), "owner_tree": tree(f4_owner),
            "f1_after": f1_raw(Path(prepared["f1_root"]) / "store.sqlite")}
        attached_owner.close()
        f4.close(True)

        # Lost service reply after actual F4/witness publication but before the
        # owner-side publication record. Cold recovery plus exact retry must
        # settle one original journal event and never append a second one.
        receipt_root = out / "state" / "native-f4-receipt-cold"
        receipt_setup = setup_native_f3(receipt_root, world="A", activate=True)
        receipt_owner = Path(receipt_setup["owner_root"])
        receipt_snapshot = receipt_setup["owner_ready"]["snapshot"]
        receipt_witness_root = receipt_snapshot["state"]["native_owner"]["domain_id"]
        receipt_f4 = NativeF4(receipt_root / "f4", receipt_owner, receipt_witness_root,
                              gate="before-settlement")
        current_owner = OwnerProcess(receipt_owner)
        current_snapshot = current_owner.call({"op": "read"})["reply"]["snapshot"]
        receipt_envelope = native_envelope(current_snapshot, receipt_witness_root + ":lost-reply-1")
        receipt_before = native.blob(receipt_f4.journal)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(receipt_f4.submit, receipt_envelope)
            gate_line = receipt_f4.sink.read()
            gate_raw = json.loads(gate_line)
            if gate_raw.get("event") != "GATE" or gate_raw.get("phase", gate_raw.get("stage")) != "before-settlement":
                raise RuntimeError("expected actual post-publication before-settlement gate: " + canonical(gate_raw))
            receipt_f4.sink.close(True)
            lost_reply_call = pending.result(timeout=10)
        owner_at_gate = current_owner.call({"op": "read"})["reply"]["snapshot"]
        receipt_at_gate = {"frame": gate_raw, "journal": native.blob(receipt_f4.journal),
                           "witness": receipt_f4.witness_call("/status"),
                           "owner_after_kill": owner_at_gate}
        cold_ready = receipt_f4.cold_restart()
        # Cold recovery starts sealed. Reopen the managed sink through its
        # actual replacement/activation transitions so fresh-ID requests reach
        # the native owner guard instead of dying at the outer cold gate.
        post_cold_reopen = [receipt_f4.call("/replace", {"holder": "native-cold-recovery-holder"}),
                            receipt_f4.call("/activate", {"authority_version": 2})]
        retry = receipt_f4.submit(receipt_envelope)
        after_retry_snapshot = receipt_f4.snapshot()
        owner_check = OwnerProcess(receipt_owner)
        owner_after_retry = owner_check.snapshot()
        owner_check.close()
        # A current-generation envelope after move is a new request and must be
        # denied; exact historical retry remains a one-event observation.
        transitions_receipt = {"seal": current_owner.call({"op": "seal"}),
                               "move": current_owner.call({"op": "move"}),
                               "activate": current_owner.call({"op": "activate"})}
        moved_snapshot = current_owner.call({"op": "read"})["reply"]["snapshot"]
        fresh_denied = native_envelope(moved_snapshot, receipt_witness_root + ":after-move-denied")
        denied_after_cold = receipt_f4.submit(fresh_denied, authority_version=2)
        historical_retry = receipt_f4.submit(receipt_envelope)
        # Converge the exact published effect through owner-selected disposal,
        # then distinguish a historic retry from a fresh request against the
        # now-removed native authority domain.
        transitions_disposal = {"seal": current_owner.call({"op": "seal"}),
                                "dispose_child": current_owner.call({"op": "dispose_child", "unit": "D"})}
        disposal_owner_snapshot = current_owner.call({"op": "read"})["reply"]["snapshot"]
        disposal_registration_ids = [r["id"] for r in
                                      disposal_owner_snapshot["state"]["native_owner"]["registrations"]]
        transitions_disposal["dispose_content"] = [
            current_owner.call({"op": "dispose_content", "id": registration_id})
            for registration_id in disposal_registration_ids]
        transitions_disposal["remove"] = current_owner.call({"op": "remove"})
        removed_owner_snapshot = current_owner.call({"op": "read"})["reply"]["snapshot"]
        historical_after_disposal = receipt_f4.submit(receipt_envelope)
        removed_new_id = dict(receipt_envelope, request_id=receipt_witness_root + ":new-after-removal",
                              epoch=removed_owner_snapshot["state"]["native_owner"]["epoch"],
                              l5=removed_owner_snapshot["generation"])
        denied_after_disposal = receipt_f4.submit(removed_new_id, authority_version=2)
        raw["cases"]["native-f4-receipt-cold"] = {
            "setup": receipt_setup, "witness_root": receipt_witness_root,
            "f4_lifecycle": receipt_f4.lifecycle_calls, "initial_ready": receipt_f4.witness.ready,
            "witness_init": receipt_f4.witness_init, "envelope": receipt_envelope,
            "journal_before": receipt_before, "lost_reply_call": lost_reply_call,
            "gate_and_owner_local_commit": receipt_at_gate, "cold_ready": cold_ready,
            "post_cold_reopen": post_cold_reopen,
            "retry": retry, "snapshot_after_retry": after_retry_snapshot,
            "owner_after_retry": owner_after_retry, "transitions_after_retry": transitions_receipt,
            "moved_snapshot": moved_snapshot, "new_request_after_move": fresh_denied,
            "denied_after_cold": denied_after_cold, "historical_retry_after_move": historical_retry,
            "disposition_transitions": transitions_disposal,
            "owner_after_disposal": removed_owner_snapshot,
            "historical_retry_after_disposal": historical_after_disposal,
            "new_id_after_disposal": removed_new_id,
            "denied_after_disposal": denied_after_disposal,
            "final_snapshot": receipt_f4.snapshot(), "f4_tree": tree(receipt_f4.root),
            "owner_tree": tree(receipt_owner), "f1_after": f1_raw(Path(receipt_setup["f1_root"]) / "store.sqlite"),
            "dead_sink_process": receipt_f4.dead_sink, "cold_sink_process": receipt_f4.sink.meta}
        current_owner.close()
        receipt_f4.close(True)

        # Actual accepted append followed by EOF at the native return boundary:
        # this must return reconciliation-required with the known local seq,
        # then cold exact retry must settle that same event without a second row.
        append_root = out / "state" / "native-f4-after-append-eof"
        append_setup = setup_native_f3(append_root, world="A", activate=True)
        append_owner = Path(append_setup["owner_root"])
        append_owner_view = OwnerProcess(append_owner)
        append_snapshot = append_owner_view.snapshot()
        append_owner_view.close()
        append_witness_root = append_snapshot["state"]["native_owner"]["domain_id"]
        append_f4 = NativeF4(append_root / "f4", append_owner, append_witness_root,
                             gate="after-append")
        append_attached_owner = OwnerProcess(append_owner)
        append_snapshot = append_attached_owner.call({"op": "read"})["reply"]["snapshot"]
        append_attached_owner.close()
        append_id = append_witness_root + ":append-eof-1"
        append_envelope = native_envelope(append_snapshot, append_id)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            append_pending = pool.submit(append_f4.submit, append_envelope)
            try:
                append_line = append_f4.sink.read(timeout=15)
            except TimeoutError:
                no_gate_result = append_pending.result(timeout=10)
                raise RuntimeError("expected post-append gate, no sink frame; submit result="
                                   + canonical(no_gate_result))
            append_gate = json.loads(append_line)
            if append_gate.get("event") != "GATE" or append_gate.get("stage") != "after-append":
                raise RuntimeError("expected actual post-append/pre-return gate: " + canonical(append_gate))
            append_owner_process = OwnerProcess(append_owner)
            append_local_snapshot = append_owner_process.snapshot()
            append_owner_process.close()
            append_f4.sink.p.stdin.close()
            append_error_call = append_pending.result(timeout=10)
        append_f4.sink.close(True)
        append_cold_ready = append_f4.cold_restart()
        # This gate is deliberately before a witness publish. Retain the
        # actual cold refusal: the complete local row is not a published cut.
        append_cold_process = append_f4.sink.close(True)
        append_final = append_f4.snapshot()
        append_owner_cold = OwnerProcess(append_owner)
        append_owner_final = append_owner_cold.snapshot()
        append_owner_cold.close()
        raw["cases"]["native-f4-after-append-eof"] = {
            "setup": append_setup, "witness_root": append_witness_root,
            "f4_lifecycle": append_f4.lifecycle_calls, "witness_init": append_f4.witness_init,
            "envelope": append_envelope, "gate": append_gate,
            "owner_local_at_gate": append_local_snapshot,
            "error_response": append_error_call, "cold_ready": append_cold_ready,
            "cold_sink_exit": append_cold_process, "final_snapshot": append_final,
            "owner_final": append_owner_final, "f4_tree": tree(append_f4.root),
            "owner_tree": tree(append_owner),
            "f1_after": f1_raw(Path(append_setup["f1_root"]) / "store.sqlite"),
            "dead_sink_process": append_f4.dead_sink, "cold_sink_process": append_f4.sink.meta}
        append_f4.close(True)
        raw["native_helper_events"] = native.EVENTS
        raw["status"] = "PASS"
    except BaseException as error:
        raw["failure"] = {"type": type(error).__name__, "message": str(error),
                          "traceback": traceback.format_exc()}
        raw["status"] = "PROBE_FAILED"
        raw["processes"] = PROCESSES
        (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
        raise
    raw["finished_ns"] = time.monotonic_ns()
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": raw["status"], "raw": str(out / "raw.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
