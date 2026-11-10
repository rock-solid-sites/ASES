#!/usr/bin/env python3
"""Real native local/joint inventory and admission order histories."""
import argparse
import concurrent.futures
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "phase-i-sol-integration"))
import native as n
CAPTURE = HERE.parent / "phase-i-sol-integration/evidence/sources"
L5DIR = CAPTURE / "l5/research/phase-i-protected-work-unit-f3/lifecycle/l5"
L6DIR = CAPTURE / "l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory"
ADMISSION = HERE.parent / "phase-i-effect-admission/admission_sink.py"
REPAIR = HERE.parent / "phase-i-f1-recovery-repair"
domain = n.module("joint_domain_worker", HERE / "domain_worker.py")
fixture = n.module("joint_fixture", L5DIR / "test_management_conformance.py")
inventory = n.module("joint_inventory", L6DIR / "store.py")
repair = n.module("joint_f1_probe", REPAIR / "probe.py")


def tree(root):
    return {str(p.relative_to(root)): n.blob(p) for p in sorted(root.rglob("*")) if p.is_file()}


def setup(root, occupied=False, local=False, accepted_pair=None):
    root.mkdir(parents=True)
    l5root = root / "l5"
    l5root.mkdir()
    state = fixture.state(parent_grants=["read", "write"])
    for unit in state["work_units"].values():
        unit["accepted_contents"] = []
    objects = l5root / "protected/objects"
    meta = dict(identity="joint-import", object="objects/x.bin", sha256=n.sha(n.CONTENT.encode()),
                size=len(n.CONTENT.encode()))
    if accepted_pair is not None:
        meta["accepted_pair"] = accepted_pair
    if occupied:
        state["work_units"]["C"]["accepted_contents"] = [meta]
    fixture.publish(l5root, state)
    objects.mkdir()
    if occupied:
        (objects / "x.bin").write_bytes(n.CONTENT.encode())
    lock = l5root / "management-writer.lock"
    lock.touch()
    l6root = root / "l6"
    inventory.bootstrap(l6root)
    config = dict(profile="joint-domain-experiment-v1", test_only=True, domain_id="joint-import",
                  l5_root=str(l5root), l5_lock=str(lock), l6_root=str(l6root),
                  custody=[[str(p), domain.identity(p)] for p in (l5root, lock, l6root, l6root / "catalog.sqlite")])
    path = root / "domain-config.json"
    path.write_text(n.canonical(config))
    result = dict(root=root, config=config, path=path)
    if local:
        child = local_worker(result)
        result["put"] = child.ask(op="put", name="x", kind="accepted", payload=n.CONTENT)
        child.close(False)
    return result


def local_worker(case):
    return n.Child([sys.executable, "-B", L6DIR / "race/race_store.py", case["root"] / "l6"])


def joint_worker(case):
    return n.Child([sys.executable, "-B", HERE / "domain_worker.py", case["path"]])


def snapshot(case):
    return dict(l6=inventory.snapshot(case["root"] / "l6"), l5=tree(case["root"] / "l5"))


def remove(case):
    child = joint_worker(case)
    before = snapshot(case)
    reply = child.ask(op="remove", scope="local-inventory")
    child.close(False)
    return dict(before=before, response=reply, after=snapshot(case))


def run(out):
    cases = {}
    for label, joint in (("local-removal-survivor", False), ("joint-refuses-survivor", True)):
        case = setup(out / label, occupied=True, local=True)
        child = local_worker(case)
        disposed = child.ask(op="dispose", name="x")
        if joint:
            child.close(False)
            result = remove(case)
        else:
            before = snapshot(case)
            response = child.ask(op="remove")
            child.close(False)
            result = dict(before=before, response=response, after=snapshot(case))
        cases[label] = dict(result, disposition=disposed)

    case = setup(out / "empty-neighbor")
    result = remove(case)
    creator = local_worker(case)
    result["later_create"] = creator.ask(op="put", name="x", kind="candidate", payload="new")
    creator.close(False)
    cases["empty-neighbor"] = result

    case = setup(out / "creator-first", local=True)
    cases["creator-first"] = remove(case)

    case = setup(out / "remover-first")
    remover = joint_worker(case)
    gate = remover.ask(op="remove", scope="local-inventory", gate="scan")
    creator = local_worker(case)
    overlap = creator.ask(op="put", name="x", kind="candidate", payload="new")
    creator.close(False)
    removed = remover.resume()
    remover.close(False)
    creator = local_worker(case)
    late = creator.ask(op="put", name="x", kind="candidate", payload="new")
    creator.close(False)
    cases["remover-first"] = dict(gate=gate, overlap=overlap, response=removed,
                                  later_create=late, after=snapshot(case))

    case = setup(out / "put-kill-orphan")
    creator = local_worker(case)
    gate = creator.ask(op="put", name="x", kind="candidate", payload="orphan", gate="precommit")
    process = creator.close(True)
    cases["put-kill-orphan"] = dict(remove(case), gate=gate, process=process)

    case = setup(out / "dispose-kill-cleanup", local=True)
    disposer = local_worker(case)
    gate = disposer.ask(op="dispose", name="x", gate="postcommit")
    process = disposer.close(True)
    before_cleanup = remove(case)
    cleanup = local_worker(case)
    cleaned = cleanup.ask(op="cleanup", name="x")
    cleanup.close(False)
    cases["dispose-kill-cleanup"] = dict(before_cleanup=before_cleanup, cleanup=cleaned,
                                         after_cleanup=remove(case), gate=gate, process=process)

    case = setup(out / "missing-l5-reference", occupied=True)
    (case["root"] / "l5/protected/objects/x.bin").unlink()
    cases["missing-l5-reference"] = remove(case)
    case = setup(out / "unknown-l5-material")
    (case["root"] / "l5/protected/objects/unknown").write_bytes(b"not inventoried in catalog")
    cases["unknown-l5-material"] = remove(case)

    case = setup(out / "unknown-l5-directory")
    (case["root"] / "l5/protected/objects/empty-directory").mkdir()
    cases["unknown-l5-directory"] = remove(case)
    case = setup(out / "empty-shared-child")
    child = joint_worker(case)
    before = snapshot(case)
    response = child.ask(op="remove", scope="shared-work-unit")
    child.close(False)
    cases["empty-shared-child"] = dict(before=before, response=response, after=snapshot(case))

    # Actual F4 append admission and L6 removal share the same participating guards.
    root = out / "effect-vs-removal"
    source_root = out / "effect-source"
    repair.bootstrap(source_root, REPAIR / "repaired_service.py", repaired=True)
    pair = repair.snapshot(source_root / "store.sqlite")["rows"]["observation"]
    pair = json.loads(pair)
    case = setup(root, occupied=True, local=True, accepted_pair=pair)
    manager = n.Child([sys.executable, "-B", L5DIR / "move-cuts/worker.py", root / "l5", "none"])
    activation = manager.ask(op="activate")
    manager.close(False)
    selector, state = domain.l5.load_current(root / "l5")
    generation = dict(selector=selector, sha256=n.sha((root / "l5/protected" / selector).read_bytes()))
    config = dict(profile="experimental-import-v1", test_only=True, import_id="joint-import", epoch="joint-epoch",
                  pair=pair, f1=str(source_root / "store.sqlite"), l5_root=str(root / "l5"),
                  l5_lock=str(root / "l5/management-writer.lock"), l6=str(root / "l6/catalog.sqlite"), l6_name="x",
                  custody=case["config"]["custody"] + [[str(source_root / "store.sqlite"), domain.identity(source_root / "store.sqlite")]],
                  gate="guarded")
    config_path = root / "admission-config.json"
    config_path.write_text(n.canonical(config))
    witness = n.Child([sys.executable, "-B", ADMISSION, "--witness", "joint-import"])
    wp = witness.ready["port"]
    genesis = dict(authority=dict(created=False, granted=False, active=False, authority_version=0, holder="old"), journal_sha256=n.sha(b""))
    n.http(wp, "/init", dict(root="joint-import", nonce="init-joint", cut=genesis))
    journal = root / "f4/effects.jsonl"
    sink = n.Child([sys.executable, "-B", ADMISSION, "--sink", "fresh", journal, wp, "published-cut", "joint-import", config_path])
    port = sink.ready["port"]
    n.http(port, "/create", {})
    n.http(port, "/grant", {})
    n.http(port, "/activate", dict(authority_version=1))
    envelope = dict(kind="use-current-descendant", import_id="joint-import", epoch="joint-epoch", pair=pair,
                    l5=generation, request_id="joint-effect")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(n.http, port, "/submit", dict(authority_version=1, request_id="joint-effect", payload=n.canonical(envelope)))
        gate = json.loads(sink.read())
        busy = remove(case)
        sink.p.stdin.write(b"continue\n")
        effect = future.result(timeout=8)
    sink.close(True)
    witness_state = n.http(wp, "/status")
    witness.close(True)
    # Native local-only removal is the deliberately incomplete port.
    remover = local_worker(case)
    dispose = remover.ask(op="dispose", name="x")
    local_remove = remover.ask(op="remove")
    remover.close(False)
    config.pop("gate")
    config_path.write_text(n.canonical(config))
    # A later fresh sink is not needed: native append guard directly reads this
    # actual removed state under the same order; preserve its observed refusal.
    from_admission = n.module("joint_append_admission", HERE.parent / "phase-i-effect-admission/admission.py")
    admission = from_admission.Admission(config)
    envelope["request_id"] = "joint-effect-later"
    try:
        with admission.guard(dict(payload=n.canonical(envelope), request_id="joint-effect-later")):
            raise AssertionError("removed local domain admitted")
    except from_admission.Denied as error:
        reason = str(error)
    cases["effect-vs-removal"] = dict(activation=activation, gate=gate, removal_while_guarded=busy,
                                      effect=effect, journal=n.blob(journal), witness=witness_state,
                                      local_remove=local_remove, dispose=dispose, later_effect_denied=reason,
                                      after=snapshot(case))
    return cases


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    out = p.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    result = dict(profile="test-only-fixed-joint-domain", pins=n.PINS,
                  source_hashes={str(path): n.sha(path.read_bytes()) for path in (Path(__file__), HERE / "domain_worker.py", L6DIR / "store.py", L5DIR / "l5_integrated.py", ADMISSION)},
                  start_ns=time.monotonic_ns())
    try:
        result["cases"] = run(out / "state")
        result["execution"] = "PASS"
    except BaseException:
        result["execution"] = "ERROR"
        result["error"] = traceback.format_exc()
    finally:
        for child in n.CHILDREN:
            child.close(True)
        result.update(processes=n.PROCESSES, events=n.EVENTS, end_ns=time.monotonic_ns())
        (out / "raw.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(n.canonical(dict(execution=result["execution"], error=result.get("error"), cases=len(result.get("cases", {})))))
    return 0 if result["execution"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
