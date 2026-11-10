#!/usr/bin/env python3
"""Bounded native F1→F3 ownership histories; no imported graph or alias."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import sqlite3
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REPAIR = REPO / "docs/research/phase-i-f1-recovery-repair"
REPAIRED_F1 = REPAIR / "repaired_service.py"
L5 = REPO / "docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5"
L6 = REPO / "docs/research/phase-i-sol-integration/evidence/sources/l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory"
OWNER_CLI = HERE / "owner_cli.py"
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


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


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
        return self.read()

    def gate_call(self, request: dict, stage: str):
        value = self.call(dict(request, gate=stage))
        if value.get("event") != "GATE" or value.get("stage") != stage:
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
        "owner_cli": OWNER_CLI,
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
        case = {"root": str(ownerroot), "initial_view": owner.call({"op": "view"})}
        case["accept_first"] = owner.call({"op": "accept"})
        case["view_after_first"] = owner.call({"op": "view"})
        case["accept_duplicate"] = owner.call({"op": "accept"})
        case["view_after_duplicate"] = owner.call({"op": "view"})
        changed_bundle = repair.configuration("C", CONTENT, True)["acceptance_bundle"]
        case["native_f1_same_bytes_changed_world"] = native_f1_accept(f1root, changed_bundle, CONTENT)
        case["f1_after_world_change"] = f1_raw(f1root / "store.sqlite")
        case["accept_changed_world"] = owner.call({"op": "accept"})
        case["view_after_changed_world"] = owner.call({"op": "view"})
        case["source_after_acceptance"] = f1_raw(f1root / "store.sqlite")
        raw["cases"]["native-no-f4"] = case
        raw["cases"]["native-no-f4"]["owner_tree_after_acceptance"] = tree(ownerroot)
        owner.close()
        raw["cases"]["native-no-f4"]["owner_process"] = owner.meta
        raw["cases"]["native-no-f4"]["owner_tree_after_close"] = tree(ownerroot)
        raw["status"] = "HARNESS_READY_FIRST_NATIVE_CASE"
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
