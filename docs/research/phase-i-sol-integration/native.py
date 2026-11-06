#!/usr/bin/env python3
"""Bounded native-component experiment; trusted fixture import is NOT native F3 acceptance.

No source checker/model imports and no replacements of component transition code.
Run from a Git checkout containing the pinned objects. See PLAN.md and REPORT.md.
"""
import argparse
import concurrent.futures
import ctypes
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import platform
import select
import socket
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PINS = {
    "f1": ("29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a", "docs/research/phase-i-f1", "docs/research/kernel-0"),
    "l5": ("51b34aface9340b7e6821b8c40dc62ca38da15e2", "research/phase-i-protected-work-unit-f3"),
    "l6": ("0f348fda050e67f3d9081a7fc22078eddc547a61", "research/phase-i-protected-work-unit-f3"),
    "f4": ("26db6db361be986cdd168045f510f5567ee9df53", "research/phase-i-t18-sink-order-20261103"),
    "receipt": ("9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9", "research/phase-i-t18-sink-order-20261103"),
}
CONTENT = "accepted\x00one\n"  # One of F1's two native admitted values, not a patched input domain.
CHILDREN = []
PROCESSES = []
EVENTS = []


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def event(kind, **fields):
    value = dict(index=len(EVENTS), ns=time.monotonic_ns(), kind=kind, **fields)
    EVENTS.append(value)
    return value


def blob(path):
    if not path.exists():
        return dict(exists=False)
    raw = path.read_bytes()
    return dict(exists=True, raw_hex=raw.hex(), sha256=sha(raw), size=len(raw))


def module(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def export_sources(destination):
    hashes = {}
    for key, (commit, *paths) in PINS.items():
        root = destination / key
        root.mkdir()
        archive = subprocess.check_output(["git", "archive", commit, *paths], cwd=REPO)
        archive_path = destination / (key + ".tar")
        archive_path.write_bytes(archive)
        with tarfile.open(archive_path) as stream:
            stream.extractall(root, filter="data")
        archive_path.unlink()
        hashes[key] = dict(commit=commit, paths=paths, files={
            str(p.relative_to(root)): sha(p.read_bytes()) for p in sorted(root.rglob("*.py"))})
    return hashes


class Child:
    def __init__(self, argv, pass_fds=(), ready="json"):
        self.meta = dict(argv=[str(x) for x in argv], start_ns=time.monotonic_ns(), frames=[])
        self.p = subprocess.Popen(self.meta["argv"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, pass_fds=pass_fds, bufsize=0)
        self.meta["pid"] = self.p.pid
        CHILDREN.append(self)
        first = self.read()
        if ready == "literal":
            if first != "ready\n":
                raise RuntimeError("F1 startup: " + first)
            self.ready = first
        else:
            self.ready = json.loads(first)
        self.meta["ready_ns"] = time.monotonic_ns()

    def read(self):
        if not select.select([self.p.stdout], [], [], 5)[0]:
            raise TimeoutError("child frame: " + str(self.p.pid))
        raw = self.p.stdout.readline(4 * 1024 * 1024)
        if not raw:
            raise RuntimeError("child EOF: " + self.p.stderr.read().decode())
        value = raw.decode()
        self.meta["frames"].append(dict(received_ns=time.monotonic_ns(), raw=value))
        return value

    def ask(self, **request):
        start = time.monotonic_ns()
        self.p.stdin.write((canonical(request) + "\n").encode())
        reply = json.loads(self.read())
        event("stdio", pid=self.p.pid, start_ns=start, request=request, response=reply)
        return reply

    def resume(self):
        self.p.stdin.write(b"continue\n")
        return json.loads(self.read())

    def close(self, kill=True):
        if "exit" in self.meta:
            return self.meta
        if self.p.poll() is None:
            if kill:
                self.p.kill()
            else:
                self.p.stdin.write(b'{"op":"stop"}\n')
        try:
            self.meta["exit"] = self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.p.kill()
            self.meta["exit"] = self.p.wait(timeout=3)
            self.meta["forced_timeout_kill"] = True
        self.meta.update(exit_ns=time.monotonic_ns(), stdout_tail=self.p.stdout.read().decode(),
                         stderr=self.p.stderr.read().decode(), eof_ns=time.monotonic_ns())
        self.p.stdin.close()
        self.p.stdout.close()
        self.p.stderr.close()
        PROCESSES.append(self.meta)
        return self.meta


def http(port, path, data=None):
    start = time.monotonic_ns()
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    raw = None if data is None else canonical(data).encode()
    try:
        conn.request("GET" if data is None else "POST", path, raw,
                     {} if raw is None else {"Content-Type": "application/json"})
        reply = conn.getresponse()
        body = reply.read().decode()
        value = dict(status=reply.status, body=json.loads(body), raw=body)
    finally:
        conn.close()
    event("http", start_ns=start, port=port, path=path, request=data, response=value)
    return value


class F1:
    def __init__(self, source, root, observations, context=0, gate=None):
        self.client, server = socket.socketpair()
        self.client.settimeout(5)
        self.reader = self.client.makefile("rb", buffering=0)
        self.event_read, event_write = os.pipe()
        release_read, self.release_write = os.pipe()
        config = dict(path=str(root / "store.sqlite"), root="work", profile="independent",
                      channels=[[context, server.fileno()]], observation_mode="atomic",
                      trace=str(root / ("sql-" + str(time.monotonic_ns()) + ".jsonl")))
        if observations is not None:
            config["observations"] = observations
        fds = [server.fileno()]
        if gate:
            config["gate"] = dict(lane=0, kind="accept", stage=gate,
                                  event_fd=event_write, release_fd=release_read)
            fds += [event_write, release_read]
        self.child = Child([sys.executable, source, canonical(config)], fds, "literal")
        server.close()
        os.close(event_write)
        os.close(release_read)

    def call(self, kind, target=0, value=0, other=0):
        request = dict(kind=kind) if kind == "read" else dict(kind=kind, target=target, value=value, other=other)
        start = time.monotonic_ns()
        self.client.sendall((canonical(request) + "\n").encode())
        raw = self.reader.readline()
        response = json.loads(raw) if raw else None
        event("f1", pid=self.child.p.pid, start_ns=start, request=request,
              response=response, wire_hex=raw.hex())
        return response

    def close(self):
        self.child.close()
        self.reader.close()
        self.client.close()
        os.close(self.event_read)
        os.close(self.release_write)


def f1_boot(source, root, observations, gate=None):
    root.mkdir(parents=True)
    persistent = source.parent.parent.parent / "kernel-0/kernel0_recovery_service.py"
    config = dict(path=str(root / "store.sqlite"), root="work", profile="independent")
    subprocess.run([sys.executable, str(persistent), "--initialize", canonical(config)], check=True, timeout=5)
    with sqlite3.connect(root / "store.sqlite") as db:
        db.execute("CREATE TABLE consumer_observations(id INTEGER PRIMARY KEY CHECK(id=1),record TEXT NOT NULL)")
    admin = F1(source, root, observations, -1)
    try:
        establish = admin.call("establish")
        grant = admin.call("grant", value=7)
    finally:
        admin.close()
    writer = F1(source, root, observations, gate=gate)
    if gate:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            pending = executor.submit(writer.call, "accept", value=CONTENT)
            if not select.select([writer.event_read], [], [], 5)[0]:
                raise TimeoutError("F1 commit gate")
            marker = os.read(writer.event_read, 1)
            event("f1_gate", stage=gate, pid=writer.child.p.pid, raw_hex=marker.hex())
            writer.child.close()
            accepted = pending.result(timeout=5)
        writer.close()
    else:
        try:
            accepted = writer.call("accept", value=CONTENT)
        finally:
            writer.close()
    return dict(establish=establish, grant=grant, accept=accepted, recovered=f1_read(source, root))


def f1_read(source, root):
    proc = subprocess.run([sys.executable, str(source), "--reader", str(root / "store.sqlite")],
                          capture_output=True, text=True, timeout=5, check=True)
    result = json.loads(proc.stdout)
    event("f1_independent_reader", response=result)
    return result


class F4:
    def __init__(self, source, root, identity):
        self.source, self.root, self.identity = source, root, identity
        root.mkdir(parents=True)
        self.journal = root / "sink-effects.jsonl"
        self.w = Child([sys.executable, source, "--witness", identity])
        self.wp = self.w.ready["port"]
        genesis = dict(authority=dict(created=False, granted=False, active=False,
                                     authority_version=0, holder="old"), journal_sha256=sha(b""))
        self.wcall("/init", cut=genesis)
        self.start(False)
        self.calls = []
        self.call("/create", {})
        self.call("/grant", {})
        self.call("/activate", dict(authority_version=1))

    def wcall(self, path, **data):
        return http(self.wp, path, dict(root=self.identity, nonce="probe-" + str(time.monotonic_ns()), **data))

    def start(self, recover=True):
        self.sink = Child([sys.executable, self.source, "--sink", "recover" if recover else "fresh",
                           self.journal, self.wp, "published-cut", self.identity])
        self.port = self.sink.ready.get("port")

    def call(self, path, data):
        before = blob(self.journal)
        reply = http(self.port, path, data)
        self.calls.append(dict(path=path, request=data, response=reply, before=before, after=blob(self.journal)))
        return reply

    def submit(self, envelope, version=1):
        return self.call("/submit", dict(authority_version=version,
                                        request_id=envelope["causal_id"], payload=canonical(envelope)))

    def snapshot(self):
        return dict(calls=self.calls, local=blob(self.journal), sink=http(self.port, "/status"),
                    witness=http(self.wp, "/status"))

    def close(self):
        self.sink.close()
        self.w.close()


def run(sources, out):
    f1 = sources / "f1/docs/research/phase-i-f1/c11-sqlite/c11_service.py"
    l5dir = sources / "l5/research/phase-i-protected-work-unit-f3/lifecycle/l5"
    l6dir = sources / "l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory"
    f4dir = "research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py"
    l5 = module("l5_integrated", l5dir / "l5_integrated.py")
    fixture = module("test_management_conformance", l5dir / "test_management_conformance.py")
    inventory = module("inventory_bootstrap", l6dir / "store.py")
    cases = {}

    def origin(name, stage=None):
        root = out / "state" / name
        root.mkdir(parents=True)
        cid = "sol-20261106:" + name
        obs = dict(identity_genesis="work:C:" + cid, created_by="trusted-test-supervisor",
                   project="ASES-independent-integration", consumer_evidence=canonical(dict(causal_id=cid, content_sha256=sha(CONTENT.encode()))))
        accepted = f1_boot(f1, root / "f1", obs, stage)
        envelope = dict(causal_id=cid, unit="C", descendant="D", sink_position="p",
                        content=CONTENT, content_sha256=sha(CONTENT.encode()), accepted_observations=obs)
        return root, accepted, envelope

    def imported(root, envelope, parent_write=False):
        target = root / "l5"
        target.mkdir()
        state = fixture.state(parent="P", parent_grants=["read", "write"] if parent_write else ["read"])
        meta = dict(identity=envelope["causal_id"], object="objects/x.bin", sha256=envelope["content_sha256"],
                    size=len(CONTENT.encode()), bridge_envelope=envelope)
        state["work_units"]["C"]["accepted_contents"] = [meta]
        fixture.publish(target, state)
        (target / "protected/objects").mkdir()
        (target / "protected/objects/x.bin").write_bytes(CONTENT.encode())
        inv = root / "l6"
        inventory.bootstrap(inv)
        child = Child([sys.executable, l6dir / "race/race_store.py", inv])
        try:
            put = child.ask(op="put", name="x", kind="accepted", payload=CONTENT)
        finally:
            child.close(False)
        mapping = dict(test_only=True, l5_unit="C", l5_identity=meta["identity"],
                       l6_name="x", l6_envelope=envelope, sink_unit="C", sink_position="p",
                       route_from_descendant="D")
        (root / "adapter-binding.json").write_text(canonical(mapping) + "\n")
        event("trusted_test_import", root=str(root), mapping=mapping, inventory_reply=put)
        return target, inv, mapping

    # Non-accept changes should not manufacture a different accepted evidence world.
    for label in ("same-observations", "changed-observations"):
        root, accepted, env = origin(label)
        obs = dict(env["accepted_observations"])
        if label == "changed-observations":
            obs["consumer_evidence"] = "different future acceptance; never accepted here"
        manager = F1(f1, root / "f1", obs, -1)
        try:
            before = manager.call("read")
            mutation = manager.call("restrict", value=3)
        finally:
            manager.close()
        cases[label] = dict(f1=accepted, envelope=env, readonly_restart=before,
                            nonaccept=mutation, final=f1_read(f1, root / "f1"))

    # One causal envelope spans the real stores. Fixture import remains explicit.
    for label in ("authorized-neighbor", "attenuated-descendant", "removed-inventory", "stale-token", "valid-rejection-gap", "lost-receipt", "publication-rejected"):
        root, accepted, env = origin(label)
        target, inv, mapping = imported(root, env, parent_write=label != "attenuated-descendant")
        worker = Child([sys.executable, l5dir / "move-cuts/worker.py", target, "none"])
        move = None
        if label == "attenuated-descendant":
            move = worker.ask(op="move")
        activation = worker.ask(op="activate")
        write = worker.ask(op="write", payload=canonical(env))
        worker.close(False)
        inv_before = inventory.snapshot(inv)
        removal = None
        if label == "removed-inventory":
            remover = Child([sys.executable, l6dir / "race/race_store.py", inv])
            dispose = remover.ask(op="dispose", name="x")
            removal = remover.ask(op="remove")
            remover.close(False)
        receipt = label in ("lost-receipt", "publication-rejected")
        pub = F4(sources / ("receipt" if receipt else "f4") / f4dir, root / "f4", env["causal_id"])
        stale = retry = fault = None
        if label in ("stale-token", "valid-rejection-gap"):
            stale = pub.submit(env, version=0)
        if receipt:
            fault = pub.wcall("/fault", reject_publish=label == "publication-rejected", drop_publish_reply_once=label == "lost-receipt")
        reply = pub.submit(env)
        if receipt:
            retry = pub.submit(env)
            pub.sink.close()
            pub.start(True)
        # Both detached acceptance and the adapter's possible suppression are recorded.
        source_allowed = write["result"]["reply"]["result"] == "COMMITTED"
        inv_after = inventory.snapshot(inv)
        cases[label] = dict(f1=accepted, envelope=env, binding=mapping, move=move,
                            activation=activation, l5_write=write, inventory_before=inv_before,
                            removal=removal, inventory_after=inv_after, stale=stale, fault=fault,
                            submit=reply, retry=retry, publication=pub.snapshot() if pub.port else dict(startup=pub.sink.ready, calls=pub.calls, local=blob(pub.journal), witness=http(pub.wp, "/status")),
                            adapter_would_send=source_allowed and inv_after["live"],
                            adapter_is_production=False)
        pub.close()

    # Commit prefixes survive real kills; no manufactured downstream completion.
    for stage in ("prepared", "durable"):
        root, accepted, env = origin("f1-kill-" + stage, stage)
        cases["f1-kill-" + stage] = dict(f1=accepted, envelope=env,
            downstream_files=list(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and "f1" not in p.relative_to(root).parts))
    root, accepted, env = origin("l6-kill-before-catalog")
    inv = root / "l6"
    inventory.bootstrap(inv)
    creator = Child([sys.executable, l6dir / "race/race_store.py", inv])
    gate = creator.ask(op="put", name="x", kind="accepted", payload=CONTENT, gate="precommit")
    creator.close()
    cold = Child([sys.executable, l6dir / "race/race_store.py", inv])
    denied = cold.ask(op="remove")
    cold.close(False)
    cases["l6-kill-before-catalog"] = dict(f1=accepted, envelope=env, gate=gate, removal=denied, inventory=inventory.snapshot(inv))

    # Original L5 manager compare/replace race: the gate changes scheduling only.
    root, accepted, env = origin("competing-l5-managers")
    target, inv, mapping = imported(root, env)
    mover = Child([sys.executable, l5dir / "move-cuts/worker.py", target, "after_record"])
    other = Child([sys.executable, l5dir / "move-cuts/worker.py", target, "none"])
    gate = mover.ask(op="move")
    rival = other.ask(op="activate")
    moved = mover.resume()
    mover.close(False)
    other.close(False)
    cold = Child([sys.executable, l5dir / "move-cuts/worker.py", target, "none"])
    cases["competing-l5-managers"] = dict(f1=accepted, envelope=env, gate=gate, rival=rival,
                                         move_response=moved, cold=cold.ready)
    cold.close(False)

    # Native L6 locking neighbor and the pinned detached-scan mutation.
    for label in ("guarded", "creator-first", "detached"):
        root, accepted, env = origin("removal-race-" + label)
        inv = root / "l6"
        inventory.bootstrap(inv)
        remover = Child([sys.executable, l6dir / "race/race_store.py", inv])
        creator = Child([sys.executable, l6dir / "race/race_store.py", inv])
        if label == "creator-first":
            put = creator.ask(op="put", name="x", kind="accepted", payload=CONTENT)
            removed = remover.ask(op="remove")
            gate = None
        else:
            gate = remover.ask(op="remove", profile="detached-scan" if label == "detached" else "directory-inventory", gate="scan")
            put = creator.ask(op="put", name="x", kind="accepted", payload=CONTENT)
            removed = remover.resume()
        remover.close(False)
        creator.close(False)
        cases["removal-race-" + label] = dict(f1=accepted, envelope=env, gate=gate, creator=put,
                                             removal=removed, inventory=inventory.snapshot(inv))
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True, help="new, nonexistent evidence directory")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    libc = ctypes.CDLL(None, use_errno=True)
    abi = libc.syscall(444, None, 0, 1)
    data = dict(schema="ases.sol.native-components.v1", started_ns=time.monotonic_ns(),
                harness_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                harness_sha256=sha(Path(__file__).read_bytes()), pins=PINS,
                environment=dict(python=sys.version, executable=sys.executable,
                                 executable_sha256=sha(Path(sys.executable).read_bytes()), sqlite=sqlite3.sqlite_version,
                                 platform=platform.platform(), landlock_abi=abi, landlock_errno=ctypes.get_errno()))
    code = 0
    try:
        with tempfile.TemporaryDirectory(prefix="ases-native-sources-") as directory:
            sources = Path(directory)
            data["sources"] = export_sources(sources)
            data["cases"] = run(sources, out)
    except BaseException:
        data["harness_error"] = traceback.format_exc()
        code = 1
    finally:
        for child in CHILDREN:
            child.close()
        data.update(processes=PROCESSES, events=EVENTS, finished_ns=time.monotonic_ns(), execution="ERROR" if code else "PASS")
        (out / "raw.json").write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    print(canonical(dict(execution=data["execution"], cases=len(data.get("cases", {})), output=str(out))))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
