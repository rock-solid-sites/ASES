#!/usr/bin/env python3
"""Actual original L5 overlap, guarded neighbors, kills and unguarded bypass."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import select
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/worker.py"
VARIANT = HERE / "worker_variant.py"
PROCESSES = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


fixture = load("test_management_conformance", SOURCE.parent.parent / "test_management_conformance.py")


def setup(root):
    root.mkdir(parents=True)
    state = fixture.state(parent="P", parent_grants=["read"])
    raw = b"accepted-writer-exclusion-fixture\n"
    state["work_units"]["C"]["accepted_contents"] = [dict(identity="x", object="objects/x.bin", sha256=sha(raw), size=len(raw))]
    fixture.publish(root, state)
    (root / "protected/objects").mkdir()
    (root / "protected/objects/x.bin").write_bytes(raw)


class Child:
    def __init__(self, root, mode="original", phase="none"):
        argv = [sys.executable, "-B", str(SOURCE), str(root), phase] if mode == "original" else [sys.executable, "-B", str(VARIANT), mode, str(root), phase]
        self.meta = dict(argv=argv, mode=mode, phase=phase, start_ns=time.monotonic_ns(), frames=[])
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        PROCESSES.append(self)
        self.meta["pid"] = self.p.pid
        self.ready = self.read()

    def read(self):
        if not select.select([self.p.stdout], [], [], 5)[0]:
            raise TimeoutError("L5 frame")
        raw = self.p.stdout.readline(2 * 1024 * 1024)
        if not raw:
            raise RuntimeError("L5 EOF: " + self.p.stderr.read().decode())
        result = json.loads(raw)
        self.meta["frames"].append(dict(received_ns=time.monotonic_ns(), raw_hex=raw.hex(), frame=result))
        return result

    def ask(self, op):
        self.p.stdin.write((json.dumps(dict(op=op)) + "\n").encode())
        return self.read()

    def resume(self):
        self.p.stdin.write(b"continue\n")
        return self.read()

    def close(self, kill=False):
        if "exit" in self.meta:
            return
        if self.p.poll() is None:
            if kill:
                self.p.kill()
            else:
                self.p.stdin.write(b'{"op":"stop"}\n')
        self.meta.update(exit=self.p.wait(timeout=5), exit_ns=time.monotonic_ns(),
                         stdout_tail=self.p.stdout.read().decode(), stderr=self.p.stderr.read().decode())
        self.p.stdin.close()
        self.p.stdout.close()
        self.p.stderr.close()


def one(root, mode, schedule):
    setup(root)
    phase = "after_selector" if schedule == "kill-after-selector" else "none" if schedule == "serial" else "after_record"
    owner = Child(root, mode, phase)
    result = dict(mode=mode, schedule=schedule, before=owner.ready)
    if schedule == "serial":
        result["move"] = owner.ask("move")
        result["activate"] = owner.ask("activate")
        owner.close()
    else:
        result["gate"] = owner.ask("move")
        if schedule.startswith("kill-"):
            owner.close(True)
            successor = Child(root, mode)
            result["successor_ready"] = successor.ready
            result["successor_operation"] = successor.ask("activate" if phase == "after_selector" else "move")
            successor.close()
        else:
            rival = Child(root, "original" if schedule == "bypass" else mode)
            result["rival_ready"] = rival.ready
            if rival.ready["event"] == "READY":
                result["rival_operation"] = rival.ask("activate")
            rival.close()
            result["move"] = owner.resume()
            owner.close()
    cold = Child(root)
    result["cold"] = cold.ready
    cold.close()
    result["guard_files"] = {str(p.relative_to(root)):dict(raw_hex=p.read_bytes().hex(), sha256=sha(p.read_bytes()))
                             for p in root.rglob("*") if p.is_file() and "protected" not in p.relative_to(root).parts}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    data = dict(start_ns=time.monotonic_ns(), pin="51b34aface9340b7e6821b8c40dc62ca38da15e2",
                source_hashes={str(p):sha(p.read_bytes()) for p in (SOURCE, VARIANT, SOURCE.parent.parent / "l5_integrated.py", SOURCE.parent.parent / "test_management_conformance.py")},
                environment=dict(python=sys.version, platform=platform.platform(), executable_sha256=sha(Path(sys.executable).read_bytes())), cases={})
    code = 0
    try:
        data["cases"]["original-overlap"] = one(out / "state/original-overlap", "original", "overlap")
        for mode in ("exclusive", "generation"):
            for schedule in ("overlap", "serial", "kill-after-record", "kill-after-selector", "bypass"):
                name = mode + "-" + schedule
                data["cases"][name] = one(out / "state" / name, mode, schedule)
        data["execution"] = "PASS"
    except BaseException:
        data.update(execution="ERROR", error=traceback.format_exc())
        code = 1
    finally:
        for process in PROCESSES:
            process.close(True)
        data.update(processes=[p.meta for p in PROCESSES], ended_ns=time.monotonic_ns())
        (out / "raw.json").write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(execution=data["execution"], cases=len(data["cases"]))))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
