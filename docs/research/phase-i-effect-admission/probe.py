#!/usr/bin/env python3
"""Bounded native commit-point admission probe. Imports and identity are test-only."""
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "phase-i-sol-integration"))
import native as n

REPAIR_DIR = HERE.parent / "phase-i-f1-recovery-repair"
spec = importlib.util.spec_from_file_location("admission_f1_repair_probe", REPAIR_DIR / "probe.py")
repair = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = repair
spec.loader.exec_module(repair)
REPAIRED_F1 = REPAIR_DIR / "repaired_service.py"
L5DIR = Path(n.__file__).parent / "evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5"
L6DIR = Path(n.__file__).parent / "evidence/sources/l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory"
F4_SOURCE = Path(n.__file__).parent / "evidence/sources/receipt/research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py"
SINK = HERE / "admission_sink.py"
L5_LOCK_VARIANT = REPAIR_DIR / "l5/worker_variant.py"
CONTENT = n.CONTENT
FIELDS = ("identity_genesis", "created_by", "project", "consumer_evidence")
PROCESSES = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return n.canonical(value)


def identity(path):
    st = Path(path).stat()
    return [st.st_dev, st.st_ino]


def tree(root):
    result = {}
    for path in sorted(Path(root).rglob("*")):
        if path.is_file() and not path.is_symlink():
            raw = path.read_bytes()
            st = path.stat()
            result[str(path.relative_to(root))] = dict(raw_hex=raw.hex(), sha256=sha(raw), size=len(raw),
                                                       dev=st.st_dev, ino=st.st_ino)
    return result


def f1_pair(dbpath):
    with sqlite3.connect(Path(dbpath).resolve().as_uri() + "?mode=ro", uri=True) as db:
        kernel_version, view_raw = db.execute("SELECT version,view FROM kernel WHERE id=1").fetchone()
        view = json.loads(view_raw)
        observed = json.loads(db.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()[0])
        retained = [json.loads(row[0]) for row in db.execute("SELECT record FROM retained_observations")]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    pair = dict(accepted_content=view["content"], required=observed["required"])
    return dict(pair=pair, view=view, kernel_version=kernel_version, selected=observed,
                retained=retained, integrity=integrity)


def f1_source_generation(root):
    """Capture the native accepted generation and exact F1 files around an operation."""
    root = Path(root)
    return dict(state=f1_pair(root / "store.sqlite"), files=tree(root),
                database_identity=identity(root / "store.sqlite"))


def native_f1_accept(root, bundle, content):
    """Drive the repaired service's real accept transition in a fresh process."""
    config = {} if bundle is None else dict(acceptance_bundle=bundle)
    holder = repair.Holder(REPAIRED_F1, Path(root), config)
    try:
        response = holder.call("accept", content)
        operations = holder.meta["operations"]
        meta = dict(response=response, operation=operations[-1], process=holder.meta)
    finally:
        holder.close()
    return meta


class L5Worker:
    def __init__(self, root, phase="none"):
        self.child = n.Child([sys.executable, "-B", L5DIR / "move-cuts/worker.py", root, phase])

    def ask(self, op, payload=None):
        request = {"op": op}
        if payload is not None:
            request["payload"] = payload
        self.child.p.stdin.write((canonical(request) + "\n").encode())
        value = json.loads(self.child.read())
        n.event("l5", pid=self.child.p.pid, request=request, response=value)
        return value

    def close(self, kill=False):
        return self.child.close(kill)


class Sink:
    def __init__(self, root, config, recover=False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.journal = self.root / "sink-effects.jsonl"
        self.config_path = self.root / "admission-config.json"
        self.config_path.write_text(canonical(config) + "\n")
        self.witness = n.Child([sys.executable, "-B", SINK, "--witness", str(config["import_id"])])
        self.wp = self.witness.ready["port"]
        genesis = dict(authority=dict(created=False, granted=False, active=False, authority_version=0, holder="old"),
                       journal_sha256=sha(b""))
        self.wcall("/init", cut=genesis)
        self.start(recover)
        self.calls = []
        self.call("/create", {})
        self.call("/grant", {})
        self.call("/activate", dict(authority_version=1))

    def start(self, recover=True):
        argv = [sys.executable, "-B", SINK, "--sink", "recover" if recover else "fresh", self.journal,
                str(self.wp), "published-cut", self.config["import_id"], self.config_path]
        self.sink = n.Child(argv)
        self.port = self.sink.ready.get("port")

    def wcall(self, path, **data):
        return n.http(self.wp, path, dict(root=self.config["import_id"], nonce="admit-" + str(time.monotonic_ns()), **data))

    def call(self, path, data):
        before = n.blob(self.journal)
        response = n.http(self.port, path, data)
        value = dict(path=path, request=data, response=response, before=before, after=n.blob(self.journal))
        self.calls.append(value)
        return response

    def submit(self, envelope):
        return self.call("/submit", dict(authority_version=1, request_id=envelope["request_id"],
                                         payload=canonical(envelope)))

    def snapshot(self):
        return dict(calls=self.calls, local=n.blob(self.journal), sink=n.http(self.port, "/status") if self.port else None,
                    witness=n.http(self.wp, "/status"), config=self.config)

    def stop_sink(self, kill=True):
        self.sink.close(kill)

    def close(self):
        if getattr(self, "sink", None):
            self.sink.close(True)
        self.witness.close(True)


def setup_case(root, name, attenuated=False, activate=True):
    root = Path(root)
    root.mkdir(parents=True)
    f1root = root / "f1"
    f1 = repair.bootstrap(f1root, REPAIRED_F1, repaired=True)
    pair_data = f1_pair(f1root / "store.sqlite")
    pair = pair_data["pair"]
    import_id = "cloud-admission:" + name
    epoch = "epoch-20261110-v1"

    l5root = root / "l5"
    l5root.mkdir()
    fixture = n.module("admission_l5_fixture", L5DIR / "test_management_conformance.py")
    l5state = fixture.state(parent="P", parent_grants=["read"] if attenuated else ["read", "write"])
    raw = CONTENT.encode()
    meta = dict(identity=import_id, object="objects/x.bin", sha256=sha(raw), size=len(raw), accepted_pair=pair)
    l5state["work_units"]["C"]["accepted_contents"] = [meta]
    fixture.publish(l5root, l5state)
    (l5root / "protected/objects").mkdir()
    (l5root / "protected/objects/x.bin").write_bytes(raw)
    lock = l5root / "management-writer.lock"
    lock.touch()
    manager = L5Worker(l5root)
    transition = {}
    if attenuated:
        transition["move"] = manager.ask("move")
    if activate:
        transition["activation"] = manager.ask("activate")
    manager.close(False)
    selector, record = n.module("admission_l5", L5DIR / "l5_integrated.py").load_current(l5root)
    generation = dict(selector=selector, sha256=sha((l5root / "protected" / selector).read_bytes()))

    l6root = root / "l6"
    inv = n.module("admission_l6", L6DIR / "store.py")
    inv.bootstrap(l6root)
    putter = n.Child([sys.executable, "-B", L6DIR / "race/race_store.py", l6root])
    put = putter.ask(op="put", name="x", kind="accepted", payload=CONTENT)
    putter.close(False)

    custody_paths = [f1root, f1root / "store.sqlite", l5root, lock, l6root, l6root / "catalog.sqlite"]
    config = dict(profile="experimental-import-v1", test_only=True, import_id=import_id, epoch=epoch,
                  pair=pair, f1=str(f1root / "store.sqlite"), l5_root=str(l5root), l5_lock=str(lock),
                  l6=str(l6root / "catalog.sqlite"), l6_name="x",
                  custody=[[str(path), identity(path)] for path in custody_paths])
    request_id = import_id + ":effect"
    envelope = dict(kind="use-current-descendant", import_id=import_id, epoch=epoch, pair=pair, l5=generation,
                    request_id=request_id)
    return dict(root=str(root), f1_boot=f1, f1=pair_data, l5_transition=transition,
                l5_generation=generation, l5_state=tree(l5root), l6_put=put,
                config=config, envelope=envelope, request_id=request_id,
                initial_files={"f1": tree(f1root), "l5": tree(l5root), "l6": tree(l6root)})


def l6_change(case, operation):
    root = Path(case["root"])
    l6root = root / "l6"
    if operation == "remove":
        p = n.Child([sys.executable, "-B", L6DIR / "race/race_store.py", l6root])
        dispose = p.ask(op="dispose", name="x")
        remove = p.ask(op="remove")
        p.close(False)
        return dict(dispose=dispose, remove=remove)
    if operation == "unknown":
        (l6root / "objects" / "unknown").write_bytes(b"unregistered material\n")
        return dict(unknown_written=True)
    return None


def run_effect(case, out, label, mutate=None, gate=None, kill_at=None, fault=None, route="/submit",
               gate_release="continue"):
    config = json.loads(json.dumps(case["config"]))
    if gate:
        config["gate"] = gate
    root = Path(case["root"])
    # Snapshot immediately before the native sink begins the request.
    before = dict(l5=tree(root / "l5"), l6=tree(root / "l6"), f1=tree(root / "f1"))
    sink = Sink(root / "f4", config, recover=False)
    if fault:
        fault_reply = sink.wcall("/fault", **fault)
    else:
        fault_reply = None
    journal_before = n.blob(sink.journal)
    envelope = json.loads(json.dumps(case["envelope"]))
    if mutate:
        mutate(envelope, case)
    if route == "/submit":
        req = dict(authority_version=1, request_id=envelope["request_id"], payload=canonical(envelope))
    else:
        req = dict(request_id=envelope["request_id"], payload=canonical(envelope))
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(sink.call, route, req)
        gate_frame = None
        if gate:
            gate_frame = json.loads(sink.sink.read())
            if gate_frame.get("event") != "GATE":
                raise RuntimeError("expected admission gate; got " + canonical(gate_frame))
            if kill_at == "before-append" or (kill_at == "after-append" and gate == "after-append"):
                if kill_at == "after-append":
                    case["append_gate"] = gate_frame
                sink.sink.close(True)
                response = None
            else:
                if label == "stale-generation":
                    worker = L5Worker(root / "l5")
                    move = worker.ask("move")
                    active = worker.ask("activate")
                    worker.close(False)
                    case["interleaved_l5"] = dict(move=move, activation=active, after=tree(root / "l5"))
                if label == "f1-opaque-reaccept":
                    f1root = root / "f1"
                    source_before = f1_source_generation(f1root)
                    new_required = {key: "native-reaccept:" + key for key in FIELDS}
                    accepted = native_f1_accept(f1root,
                                                dict(accepted_content=case["envelope"]["pair"]["accepted_content"],
                                                     required=new_required),
                                                case["envelope"]["pair"]["accepted_content"])
                    case["native_f1_transition"] = dict(before=source_before, operation=accepted,
                                                        after=f1_source_generation(f1root))
                if label == "l6-remove-interleaved":
                    case["interleaved_l6"] = l6_change(case, "remove")
                if label == "guarded-writers":
                    # Independent SQLite writer attempts must fail while admission owns BEGIN IMMEDIATE.
                    attempts = {}
                    for tag, dbpath in (("f1", root / "f1/store.sqlite"), ("l6", root / "l6/catalog.sqlite")):
                        try:
                            with sqlite3.connect(dbpath, timeout=.12, isolation_level=None) as db:
                                db.execute("BEGIN IMMEDIATE")
                                db.execute("ROLLBACK")
                            attempts[tag] = "UNEXPECTEDLY_ACQUIRED"
                        except sqlite3.OperationalError as error:
                            attempts[tag] = str(error)
                    case["writer_attempts"] = attempts
                    # Native L5 guarded contender must be refused on the held stable inode.
                    contender = subprocess.run([sys.executable, "-B", str(L5_LOCK_VARIANT), "exclusive",
                                                str(root / "l5"), "none"], capture_output=True, text=True, timeout=5)
                    case["l5_contender"] = dict(returncode=contender.returncode, stdout=contender.stdout,
                                                 stderr=contender.stderr)
                if gate_release == "eof":
                    case["append_gate"] = gate_frame
                    sink.sink.p.stdin.close()
                    response = future.result(timeout=8)
                else:
                    sink.sink.p.stdin.write(b"continue\n")
                if kill_at == "after-append":
                    appended_gate = json.loads(sink.sink.read())
                    case["append_gate"] = appended_gate
                    sink.sink.close(True)
                    response = None
                else:
                    gate_frame = dict(guarded=gate_frame, append=None)
                    response = future.result(timeout=8)
        else:
            response = future.result(timeout=8)
    local = n.blob(sink.journal)
    witness = n.http(sink.wp, "/status")
    sink_status = None
    if sink.sink.p.poll() is None:
        # process remains alive; server status is separate from journal state.
        sink_status = n.http(sink.port, "/status")
    result = dict(label=label, before=before, after=dict(l5=tree(root / "l5"), l6=tree(root / "l6"), f1=tree(root / "f1")),
                  envelope=envelope, request=req, response=response, gate=gate_frame, fault=fault_reply,
                  journal_before=journal_before,
                  local=local, witness=witness, sink_status=sink_status, sink_process=sink.sink.meta,
                  witness_process=sink.witness.meta,
                  interleaved_l5=case.get("interleaved_l5"), interleaved_l6=case.get("interleaved_l6"),
                  writer_attempts=case.get("writer_attempts"), l5_contender=case.get("l5_contender"),
                  l6_change=case.get("l6_change"), native_f1_transition=case.get("native_f1_transition"),
                  append_gate=case.get("append_gate"))
    if kill_at:
        # Actual cold startup against the same local journal and remote witness.
        try:
            cold = n.Child([sys.executable, "-B", SINK, "--sink", "recover", sink.journal,
                            str(sink.wp), "published-cut", config["import_id"], sink.config_path])
            result["cold"] = dict(ready=cold.ready, process=cold.meta)
            cold.close(True)
        except Exception as error:
            result["cold"] = dict(startup_error=type(error).__name__ + ":" + str(error))
    else:
        if sink.sink.p.poll() is None:
            sink.sink.close(gate_release == "eof")
        if fault:
            cold = n.Child([sys.executable, "-B", SINK, "--sink", "recover", sink.journal,
                            str(sink.wp), "published-cut", config["import_id"], sink.config_path])
            result["cold_after_receipt_loss"] = dict(ready=cold.ready, process=cold.meta)
            cold.close(True)
    result["raw_files"] = {"f4": tree(root / "f4"), "f1": result["after"]["f1"],
                           "l5": result["after"]["l5"], "l6": result["after"]["l6"]}
    sink.witness.close(True)
    return result


def no_change(case, envelope, _):
    return None


def mutate_field(name, value):
    def change(envelope, _):
        if name == "pair-world":
            envelope["pair"]["required"]["consumer_evidence"] += ":alternate-equal-bytes"
        elif name == "subject":
            envelope["import_id"] = value
        elif name == "epoch":
            envelope["epoch"] = value
        elif name == "pair-subject":
            envelope["pair"]["accepted_content"] = value
        return None
    return change


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    n.CHILDREN.clear(); n.PROCESSES.clear(); n.EVENTS.clear(); PROCESSES.clear()
    data = dict(schema="ases.phase-i-effect-admission.v1", started_ns=time.monotonic_ns(),
                parent_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                source_hashes={str(p): sha(p.read_bytes()) for p in (HERE/"admission.py", SINK, Path(__file__),
                    REPAIR_DIR/"probe.py", REPAIRED_F1, L5_LOCK_VARIANT,
                    L5DIR/"l5_integrated.py", L5DIR/"move-cuts/worker.py",
                    L6DIR/"store.py", L6DIR/"race/race_store.py", F4_SOURCE)},
                pins=n.PINS, environment=dict(python=sys.version, executable=sys.executable,
                                             executable_sha256=sha(Path(sys.executable).read_bytes()), sqlite=sqlite3.sqlite_version),
                cases={})
    try:
        # Valid positive and the frozen L5-denied descendant.
        for label, attenuated in (("allowed", False), ("moved-attenuated", True)):
            case = setup_case(out / "state" / label, label, attenuated)
            data["cases"][label] = run_effect(case, out, label)

        # Preflight goes stale while the admission handler is paused before its guards.
        case = setup_case(out / "state/stale-generation", "stale-generation", False, activate=False)
        data["cases"]["stale-generation"] = run_effect(case, out, "stale-generation", gate="before-admission")
        case = setup_case(out / "state/f1-opaque-reaccept", "f1-opaque-reaccept")
        data["cases"]["f1-opaque-reaccept"] = run_effect(
            case, out, "f1-opaque-reaccept", gate="before-admission")
        case = setup_case(out / "state/l6-remove-interleaved", "l6-remove-interleaved")
        data["cases"]["l6-remove-interleaved"] = run_effect(case, out, "l6-remove-interleaved", gate="before-admission")

        for label, field, value in (("wrong-pair-world", "pair-world", None),
                                    ("wrong-pair-subject", "pair-subject", "other accepted bytes"),
                                    ("wrong-epoch", "epoch", "other-epoch"),
                                    ("wrong-subject", "subject", "other-import")):
            case = setup_case(out / "state" / label, label)
            data["cases"][label] = run_effect(case, out, label, mutate=mutate_field(field, value))

        case = setup_case(out / "state/l6-disposed-removed", "l6-disposed-removed")
        case["l6_change"] = l6_change(case, "remove")
        data["cases"]["l6-disposed-removed"] = run_effect(case, out, "l6-disposed-removed")
        case = setup_case(out / "state/l6-unknown-material", "l6-unknown-material")
        case["l6_change"] = l6_change(case, "unknown")
        data["cases"]["l6-unknown-material"] = run_effect(case, out, "l6-unknown-material")

        case = setup_case(out / "state/root-retarget", "root-retarget")
        root = Path(case["root"]); old = root / "l5"; moved = root / "l5-saved"
        old.rename(moved); old.mkdir()
        data["cases"]["root-retarget"] = run_effect(case, out, "root-retarget")

        # Guards are held at the commit point while native writer attempts are recorded.
        case = setup_case(out / "state/guarded-writers", "guarded-writers")
        data["cases"]["guarded-writers"] = run_effect(case, out, "guarded-writers", gate="guarded")

        # Process death on both sides of the irreversible journal append.
        case = setup_case(out / "state/kill-before-append", "kill-before-append")
        data["cases"]["kill-before-append"] = run_effect(case, out, "kill-before-append", gate="guarded", kill_at="before-append")
        case = setup_case(out / "state/kill-after-append", "kill-after-append")
        data["cases"]["kill-after-append"] = run_effect(case, out, "kill-after-append", gate="after-append", kill_at="after-append")

        case = setup_case(out / "state/after-append-eof", "after-append-eof")
        data["cases"]["after-append-eof"] = run_effect(case, out, "after-append-eof",
                                                         gate="after-append", gate_release="eof")

        # Native changed-content accept without a new bundle must preserve the old
        # accepted pair; that still-current pair is then exercised by an F4 neighbor.
        case = setup_case(out / "state/missing-bundle-neighbor", "missing-bundle-neighbor")
        f1root = Path(case["root"]) / "f1"
        source_before = f1_source_generation(f1root)
        missing_bundle = native_f1_accept(f1root, None, repair.B)
        case["native_f1_transition"] = dict(before=source_before, operation=missing_bundle,
                                             after=f1_source_generation(f1root))
        data["cases"]["missing-bundle-neighbor"] = run_effect(case, out, "missing-bundle-neighbor")

        case = setup_case(out / "state/lost-receipt", "lost-receipt")
        data["cases"]["lost-receipt"] = run_effect(case, out, "lost-receipt",
                                                    fault=dict(reject_publish=False, drop_publish_reply_once=True))

        case = setup_case(out / "state/audit-route", "audit-route")
        data["cases"]["audit-route"] = run_effect(case, out, "audit-route", route="/commit-obligation")
        data["execution"] = "PASS"
    except BaseException:
        data["execution"] = "ERROR"
        data["harness_error"] = traceback.format_exc()
    finally:
        for child in n.CHILDREN:
            child.close(True)
        data.update(processes=n.PROCESSES, events=n.EVENTS, finished_ns=time.monotonic_ns())
        (out / "raw.json").write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    print(canonical(dict(execution=data["execution"], cases=len(data["cases"]), output=str(out))))
    return 0 if data["execution"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
