"""Run the admitted three local cases against the pinned native F3/F4 prototype."""

from hashlib import sha256
from importlib import util
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time
import traceback


PIN = "0bd51a34700164a5eb77efe98158fa37d1a74e23"
LIMIT_BYTES = 128 * 1024 * 1024
PROBE = Path("docs/research/phase-ii-native-ownership/probe.py")


def load_probe(repo):
    git = lambda *args: subprocess.check_output(["git", "-C", repo, *args], text=True).strip()
    if git("rev-parse", "HEAD") != PIN or git("status", "--porcelain"):
        raise ValueError("expected clean pinned native worktree")
    module_spec = util.spec_from_file_location("native_rollback_base", repo / PROBE)
    module = util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    return module


def owner_snapshot(base, root):
    owner = base.OwnerProcess(root)
    try:
        return owner.snapshot()
    finally:
        owner.close()


def effect(snapshot, request_id):
    return snapshot["state"]["native_owner"]["effects"].get(request_id)


def identity(path):
    stat = path.stat()
    return {"dev": stat.st_dev, "ino": stat.st_ino}


def retained_files(root):
    paths = sorted(p for p in (root / "owner" / "protected").rglob("*")
                   if p.is_file() and p.name != "CURRENT")
    paths.append(root / "f1" / "store.sqlite")
    return {str(p.relative_to(root)): dict(identity(p), sha256=sha256(p.read_bytes()).hexdigest())
            for p in paths}


def witness_cut(f4):
    result = f4.http(f4.witness_socket, "/status")
    assert result["status"] == 200, result
    return {name: result["body"][name] for name in ("pid", "revision", "current")}


def run_case(base, root, cell, report):
    setup = base.setup_native_f3(root)
    owner_root = Path(setup["owner_root"])
    domain = setup["owner_ready"]["snapshot"]["state"]["native_owner"]["domain_id"]
    request_id = domain + ":selection-rollback"
    f4 = base.NativeF4(root / "f4", owner_root, domain)
    try:
        before = owner_snapshot(base, owner_root)
        assert before["state"]["native_owner"]["sink_binding"]
        assert effect(before, request_id) is None
        envelope = base.native_envelope(before, request_id)
        submit = f4.submit(envelope)
        report["original"] = submit
        response = submit["response"]
        assert response["status"] == 201 and response["body"]["outcome"] == "accepted", response
        assert response["body"]["owner_effect"]["status"] == "published", response
        settled = owner_snapshot(base, owner_root)
        sequence = response["body"]["event_seq"]
        assert effect(settled, request_id)["status"] == "published"
        assert effect(settled, request_id)["seq"] == sequence
        journal = f4.journal.read_bytes()
        events = [json.loads(line) for line in journal.splitlines()]
        accepted = [event for event in events if event.get("event") == "effect_accepted"]
        assert len(accepted) == 1 and accepted[0]["seq"] == sequence
        assert accepted[0]["request_id"] == request_id
        assert accepted[0]["payload"] == submit["request"]["payload"]

        protected = owner_root / "protected"
        local = []
        for path in sorted(protected.glob("record-*.json")):
            state = json.loads(path.read_bytes())
            pending = state["native_owner"]["effects"].get(request_id, {})
            if pending.get("status") == "local" and pending.get("seq") == sequence:
                local.append({"selector": path.name, "sha256": sha256(path.read_bytes()).hexdigest()})
        assert len(local) == 1, local
        selected = {"R0": settled["generation"], "R1": local[0], "R2": before["generation"]}[cell]
        assert sha256((protected / selected["selector"]).read_bytes()).hexdigest() == selected["sha256"]
        report.update(selected=selected, pre_reservation=before["generation"], owner_local=local[0],
                      original_owner=settled, accepted_event=accepted[0],
                      owner_identity=identity(owner_root), inventory_identity=identity(protected),
                      retained_before=retained_files(root), witness_before=witness_cut(f4))
        assert report["witness_before"]["current"]["journal_sha256"] == sha256(journal).hexdigest()

        report["stopped_original_sink"] = f4.sink.close(kill=True)
        if cell != "R0":
            (protected / "CURRENT").write_bytes((selected["selector"] + "\n").encode())
        restored = owner_snapshot(base, owner_root)
        report["restored_owner"] = restored
        assert restored["generation"] == selected
        assert retained_files(root) == report["retained_before"]
        assert identity(owner_root) == report["owner_identity"]
        assert identity(protected) == report["inventory_identity"]
        assert f4.journal.read_bytes() == journal
        assert witness_cut(f4) == report["witness_before"]

        report["cold_ready"] = f4.cold_restart()
        assert report["cold_ready"].get("ready") is True, report["cold_ready"]
        retry = f4.submit(envelope)
        report.update(retry=retry, owner_after=owner_snapshot(base, owner_root),
                      witness_after=witness_cut(f4),
                      journal_before_sha256=sha256(journal).hexdigest(),
                      journal_after_sha256=sha256(f4.journal.read_bytes()).hexdigest(),
                      retained_after=retained_files(root))
        assert retry["request"] == submit["request"]
        assert f4.journal.read_bytes() == journal, "retry changed the accepted journal"
        assert report["witness_after"] == report["witness_before"], "retry advanced the F4 cut"
        if cell == "R0":
            replay = retry["response"]
            assert replay["status"] == 200 and replay["body"]["outcome"] == "already-accepted"
            assert replay["body"]["event_seq"] == sequence
            assert replay["body"]["owner_effect"]["status"] == "published"
            assert report["owner_after"]["generation"] == restored["generation"]
        report["classification"] = "OBSERVED"
    finally:
        f4.close()
        report["witness_process"] = f4.witness.meta
        report["final_sink_process"] = f4.sink.meta


def main():
    repo, retention_dir = (Path(arg).resolve() for arg in sys.argv[1:])
    output = retention_dir / "state"
    output.mkdir(mode=0o700)
    base = load_probe(repo)
    receipt = {
        "source": PIN,
        "started_ns": time.monotonic_ns(),
        "source_manifest": base.source_manifest(),
        "harness_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "sqlite": sqlite3.sqlite_version,
        "uid": os.getuid(),
        "cases": {},
    }
    status = 0
    for cell in ("R0", "R1", "R2"):
        report = {}
        receipt["cases"][cell] = report
        try:
            run_case(base, output / cell, cell, report)
        except Exception:
            report.update(classification="INCONCLUSIVE_OR_ADVERSE", error=traceback.format_exc())
            status = 1
        finally:
            receipt["finished_ns"] = time.monotonic_ns()
            (retention_dir / "raw.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(cell, report["classification"], report.get("retry", {}).get("response"), flush=True)
        if cell == "R0" and status:
            break
        assert sum(p.stat().st_size for p in retention_dir.rglob("*") if p.is_file()) < LIMIT_BYTES
    return status


def deadline(_signal, _frame):
    raise TimeoutError("admitted wall-time limit reached")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, deadline)
    raise SystemExit(main())
