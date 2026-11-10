#!/usr/bin/env python3
"""Test-only joint inventory hook; native L6 transaction/commit stay unchanged."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CAPTURE = HERE.parent / "phase-i-sol-integration/evidence/sources"
L6 = CAPTURE / "l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/store.py"
L5 = CAPTURE / "l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py"


def load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


native = load("joint_domain_l6", L6)
l5 = load("joint_domain_l5", L5)
local_snapshot = native.snapshot


def identity(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("retargeted-domain-root")
    st = path.stat()
    return [st.st_dev, st.st_ino]


class DomainStore(native.Store):
    def __init__(self, config):
        if (config.get("profile") != "joint-domain-experiment-v1"
                or config.get("test_only") is not True):
            raise ValueError("unsupported-domain-profile")
        self.config = config
        self.joint_observations = []
        self.scan_gate = False
        super().__init__(Path(config["l6_root"]))

    def foreign_inventory(self):
        for path, expected in self.config["custody"]:
            if identity(path) != expected:
                raise ValueError("changed-domain-root")
        root = Path(self.config["l5_root"])
        selector, current = l5.load_current(root)
        if not l5.graph_valid(current):
            raise ValueError("invalid-selected-l5-graph")
        references = []
        for unit, value in sorted(current["work_units"].items()):
            for meta in value.get("accepted_contents", []):
                # Never treat missing retained bytes as an authorized disposition.
                raw = l5.verified_content(root, meta)
                references.append(dict(unit=unit, metadata=meta, size=len(raw)))
        descendants = []
        for unit in current["work_units"]:
            parent = current["work_units"][unit]["parent"]
            while parent is not None:
                if parent == "C":
                    descendants.append(unit)
                    break
                parent = current["work_units"][parent]["parent"]
        objects = root / "protected/objects"
        material = []
        if objects.exists():
            if objects.is_symlink() or not objects.is_dir():
                raise ValueError("unsupported-object-boundary")
            for path in sorted(objects.rglob("*")):
                if path.is_symlink() or not (path.is_file() or path.is_dir()):
                    raise ValueError("unsupported-dependent-material")
                if path.is_file():
                    raw = path.read_bytes()
                    material.append(dict(path=str(path.relative_to(objects)),
                                         kind="file", sha256=native.digest(raw), size=len(raw)))
                else:
                    material.append(dict(path=str(path.relative_to(objects)), kind="directory"))
        observation = dict(ns=time.monotonic_ns(), domain_id=self.config["domain_id"],
                           test_only=True, selector=selector,
                           record_sha256=native.digest((root / "protected" / selector).read_bytes()),
                           accepted_references=references, object_material=material,
                           dependent_units=sorted(descendants),
                           l6_in_transaction=self.cx.in_transaction)
        self.joint_observations.append(observation)
        return observation

    def scan(self, root):
        # The inherited remove calls this after BEGIN IMMEDIATE, before COMMIT.
        value = local_snapshot(root)
        foreign = self.foreign_inventory()
        value["joint_domain"] = foreign
        # Add distinct inventory entries solely to the original nonempty guard.
        # These are named observations, not synthetic files or accepted identities.
        files = dict(value["files"])
        for i, ref in enumerate(foreign["accepted_references"]):
            files["foreign-l5-reference:" + str(i)] = ref
        for item in foreign["object_material"]:
            files["foreign-l5-material:" + item["path"]] = item
        if self.removal_scope == "shared-work-unit":
            for name in foreign["dependent_units"]:
                files["foreign-l5-child:" + name] = dict(unit=name, disposition="not-implemented")
        value["files"] = files
        if self.scan_gate:
            self.scan_gate = False
            native.emit(dict(event="GATE", phase="joint-inventory-under-native-transaction",
                             in_transaction=self.cx.in_transaction, pid=os.getpid(),
                             ns=time.monotonic_ns(), joint=foreign, local=local_snapshot(root)))
            if sys.stdin.readline().strip() != "continue":
                raise RuntimeError("scan-not-continued")
        return value

    def apply(self, request):
        if request.get("op") != "remove":
            return super().apply(request)
        # The original deliberate catalog-only/detached mutants are not this port.
        if "profile" in request:
            return dict(result="DENY", reason="unsupported-removal-profile")
        self.removal_scope = request.get("scope", "shared-work-unit")
        if self.removal_scope not in ("shared-work-unit", "local-inventory"):
            return dict(result="DENY", reason="unsupported-removal-scope")
        fd = os.open(self.config["l5_lock"], os.O_RDWR | os.O_NOFOLLOW)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return dict(result="DENY", reason="joint-domain-busy")
            self.scan_gate = request.get("gate") == "scan"
            native.snapshot = self.scan
            try:
                result = super().apply(request)
                if result.get("result") == "COMMITTED":
                    result = dict(result, joint_empty_observed=True,
                                  native_global_destruction=False, test_only_domain=True)
                return result
            except (ValueError, OSError) as error:
                if self.cx.in_transaction:
                    self.cx.execute("ROLLBACK")
                return dict(result="DENY", reason="joint-inventory-unresolved", detail=str(error))
            finally:
                native.snapshot = local_snapshot
                self.scan_gate = False
        finally:
            os.close(fd)


def main():
    config = json.loads(Path(sys.argv[1]).read_text())
    state = DomainStore(config)
    native.emit(dict(event="READY", pid=os.getpid(), snapshot=local_snapshot(state.root),
                     native_global_identity=False))
    try:
        for line in sys.stdin:
            request = json.loads(line)
            if request.get("op") == "stop":
                break
            before = time.monotonic_ns()
            result = state.apply(request)
            native.emit(dict(event="RESPONSE", pid=os.getpid(), start_ns=before,
                             end_ns=time.monotonic_ns(), request=request, reply=result,
                             snapshot=local_snapshot(state.root),
                             joint_observations=list(state.joint_observations),
                             sql_trace=list(state.trace)))
    finally:
        state.cx.close()


if __name__ == "__main__":
    main()
