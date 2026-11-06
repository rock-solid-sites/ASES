#!/usr/bin/env python3
"""Fresh process/SQLite experiment, independent of PR #10's harness/checker."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import select
import socket
import sqlite3
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PIN = "29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a"
ORIGINAL = HERE.parent / "phase-i-sol-integration/evidence/sources/f1/docs/research/phase-i-f1/c11-sqlite/c11_service.py"
A, B = "accepted\x00one\n", "accepted\x00zero\n"
FIELDS = ("identity_genesis", "created_by", "project", "consumer_evidence")
WORLDS = {key: {f: key + ":" + f for f in FIELDS} for key in ("bootstrap", "A", "B", "C")}
PROCESSES = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def snapshot(path):
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        kernel = db.execute("SELECT root,profile,version,view FROM kernel WHERE id=1").fetchone()
        obs = db.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()
        retained = [r[0] for r in db.execute("SELECT record FROM retained_observations ORDER BY record")] if "retained_observations" in tables else None
        result = dict(kernel=kernel, observation=None if obs is None else obs[0], retained=retained,
                      integrity=db.execute("PRAGMA integrity_check").fetchone()[0])
    wire = json.dumps(result, sort_keys=True).encode()
    return dict(pid=os.getpid(), raw_hex=wire.hex(), sha256=sha(wire), rows=result)


def independent(path):
    started = time.monotonic_ns()
    child = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--snapshot", str(path)],
                           text=True, capture_output=True, timeout=5, check=True)
    return dict(start_ns=started, end_ns=time.monotonic_ns(), returncode=child.returncode,
                stdout=child.stdout, stderr=child.stderr, snapshot=json.loads(child.stdout))


class Holder:
    def __init__(self, source, root, config=None, context=0, gate=None):
        self.conn, server = socket.socketpair()
        self.conn.settimeout(5)
        self.stream = self.conn.makefile("rb", buffering=0)
        self.gate_read, gate_write = os.pipe()
        release_read, self.release_write = os.pipe()
        config = dict(config or {})
        config.update(path=str(root / "store.sqlite"), root="work", profile="independent",
                      channels=[[context, server.fileno()]], observation_mode="atomic",
                      trace=str(root / ("sql-" + str(time.monotonic_ns()) + ".jsonl")))
        fds = [server.fileno()]
        if gate:
            config["gate"] = dict(lane=0, kind="accept", stage=gate, event_fd=gate_write, release_fd=release_read)
            fds += [gate_write, release_read]
        self.meta = dict(source=str(source), source_sha256=sha(source.read_bytes()), config=config,
                         start_ns=time.monotonic_ns(), operations=[])
        self.p = subprocess.Popen([sys.executable, str(source), json.dumps(config)],
                                  pass_fds=fds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        PROCESSES.append(self)
        server.close()
        os.close(gate_write)
        os.close(release_read)
        self.meta["pid"] = self.p.pid
        if not select.select([self.p.stdout], [], [], 5)[0]:
            raise TimeoutError("holder startup")
        self.meta["ready_raw"] = self.p.stdout.readline().decode()
        if self.meta["ready_raw"] != "ready\n":
            raise RuntimeError("holder not ready: " + self.p.stderr.read().decode())
        self.meta["ready_ns"] = time.monotonic_ns()

    def call(self, kind, value=0, target=0, other=0):
        request = dict(kind=kind) if kind == "read" else dict(kind=kind, value=value, target=target, other=other)
        record = dict(start_ns=time.monotonic_ns(), request=request)
        self.conn.sendall((json.dumps(request) + "\n").encode())
        try:
            raw = self.stream.readline()
            record.update(wire_hex=raw.hex(), response=json.loads(raw) if raw else None)
        except (OSError, TimeoutError) as error:
            record.update(response=None, error=type(error).__name__)
        record["end_ns"] = time.monotonic_ns()
        self.meta["operations"].append(record)
        return record

    def cut(self, value):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            pending = executor.submit(self.call, "accept", value)
            if not select.select([self.gate_read], [], [], 5)[0]:
                raise TimeoutError("accept gate")
            marker = os.read(self.gate_read, 1)
            self.meta["observed_gate"] = dict(stage=self.meta["config"]["gate"]["stage"],
                                              marker_hex=marker.hex(), ns=time.monotonic_ns())
            self.close(process_only=True)
            result = pending.result(timeout=5)
        self.close()
        return result

    def close(self, process_only=False):
        if "exit" not in self.meta:
            if self.p.poll() is None:
                self.p.kill()
            self.meta.update(exit=self.p.wait(timeout=5), exit_ns=time.monotonic_ns(),
                             stdout_tail=self.p.stdout.read().decode(), stderr=self.p.stderr.read().decode())
            trace = Path(self.meta["config"]["trace"])
            self.meta["sql"] = [json.loads(s) for s in trace.read_text().splitlines()] if trace.exists() else []
            self.p.stdout.close()
            self.p.stderr.close()
        if not process_only and not self.stream.closed:
            self.stream.close()
            self.conn.close()
            os.close(self.gate_read)
            os.close(self.release_write)


def configuration(world, content, repaired=False):
    if repaired:
        return dict(acceptance_bundle=dict(accepted_content=content, required=WORLDS[world]))
    return dict(observations=WORLDS[world])


def bootstrap(root, source, repaired=False):
    root.mkdir(parents=True)
    initialize = ORIGINAL.parent.parent.parent / "kernel-0/kernel0_recovery_service.py"
    path = root / "store.sqlite"
    config = dict(path=str(path), root="work", profile="independent")
    subprocess.run([sys.executable, str(initialize), "--initialize", json.dumps(config)], check=True, timeout=5)
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE consumer_observations(id INTEGER PRIMARY KEY CHECK(id=1),record TEXT NOT NULL)")
    if repaired:
        subprocess.run([sys.executable, str(source), "--prepare", str(path)], check=True, timeout=5, capture_output=True)
    manager = Holder(source, root, configuration("bootstrap", B, repaired), -1)
    try:
        established = manager.call("establish")
        granted = manager.call("grant", value=7)
    finally:
        manager.close()
    writer = Holder(source, root, configuration("A", A, repaired))
    try:
        accepted = writer.call("accept", A)
    finally:
        writer.close()
    return dict(establish=established, grant=granted, accept=accepted, independent=independent(path))


def baseline(out, source=ORIGINAL, repaired=False, only=None):
    cases = {}
    for label in ("cold-missing", "cold-fresh", "readonly", "unchanged", "failed-then-valid", "config-nonaccept"):
        if only and label not in only:
            continue
        root = out / "state" / label
        prefix = bootstrap(root, source, repaired)
        config = configuration("B", B, repaired) if label in ("cold-fresh", "failed-then-valid", "config-nonaccept") else {}
        holder = Holder(source, root, config, -1 if label == "config-nonaccept" else 0)
        try:
            read = holder.call("read")
            denied = holder.call("accept", "outside-native-domain") if label == "failed-then-valid" else None
            after_denial = independent(root / "store.sqlite") if denied else None
            op = holder.call("read") if label == "readonly" else holder.call("restrict", value=3) if label == "config-nonaccept" else holder.call("accept", A if label == "unchanged" else B)
        finally:
            holder.close()
        cases[label] = dict(prefix=prefix, read=read, denied=denied, after_denial=after_denial, operation=op,
                            final=independent(root / "store.sqlite"))
    return cases


def repaired_cases(out, source):
    cases = baseline(out, source, True)
    invalid = {
        "null": None,
        "list": [],
        "wrong-subject": dict(accepted_content=A, required=WORLDS["B"]),
        "non-string-subject": dict(accepted_content=False, required=WORLDS["B"]),
        "missing-field": dict(accepted_content=B, required={k: v for k, v in WORLDS["B"].items() if k != "project"}),
        "bad-field-type": dict(accepted_content=B, required=dict(WORLDS["B"], project=False)),
        "extra-field": dict(accepted_content=B, required=WORLDS["B"], unexpected=True),
    }
    for suffix, bundle in invalid.items():
        label = "invalid-" + suffix
        root = out / "state" / label
        prefix = bootstrap(root, source, True)
        holder = Holder(source, root, dict(acceptance_bundle=bundle))
        try:
            op = holder.call("accept", B)
        finally:
            holder.close()
        cases[label] = dict(prefix=prefix, operation=op, final=independent(root / "store.sqlite"))

    for label in ("stale-subject", "legacy-unbound", "same-content-invalid", "same-bytes-worlds", "kill-prepared", "kill-durable", "fail-current-insert", "fail-retained-insert"):
        root = out / "state" / label
        prefix = bootstrap(root, source, True)
        extra = {}
        if label == "stale-subject":
            first = Holder(source, root, configuration("B", B, True))
            try:
                extra["earlier"] = first.call("accept", B)
            finally:
                first.close()
            extra["before"] = independent(root / "store.sqlite")
            config, value = configuration("A", A, True), B
        elif label == "legacy-unbound":
            config, value = configuration("B", B), B
        elif label == "same-content-invalid":
            config, value = dict(acceptance_bundle=None), A
        elif label == "same-bytes-worlds":
            config, value = configuration("C", A, True), A
        else:
            config, value = configuration("B", B, True), B
        if label.startswith("fail-"):
            table = "consumer_observations" if label == "fail-current-insert" else "retained_observations"
            with sqlite3.connect(root / "store.sqlite") as db:
                db.execute("CREATE TRIGGER injected BEFORE INSERT ON " + table + " BEGIN SELECT RAISE(ABORT,'injected-transaction-failure'); END")
        gate = label.split("-", 1)[1] if label.startswith("kill-") else None
        holder = Holder(source, root, config, gate=gate)
        try:
            op = holder.cut(value) if gate else holder.call("accept", value)
            if label == "same-bytes-worlds":
                extra["after_first"] = independent(root / "store.sqlite")
                extra["duplicate"] = holder.call("accept", value)
        finally:
            holder.close()
        extra["after_operation"] = independent(root / "store.sqlite")
        if label.startswith("fail-"):
            with sqlite3.connect(root / "store.sqlite") as db:
                db.execute("DROP TRIGGER injected")
            fresh = Holder(source, root, configuration("B", B, True))
            try:
                extra["later_valid"] = fresh.call("accept", B)
            finally:
                fresh.close()
        if label == "same-bytes-worlds":
            extra["recoveries"] = []
            for _ in range(2):
                cold = Holder(source, root)
                try:
                    extra["recoveries"].append(dict(read=cold.call("read"), reaccept=cold.call("accept", A)))
                finally:
                    cold.close()
        cases[label] = dict(prefix=prefix, operation=op, final=independent(root / "store.sqlite"), **extra)

    for label in ("prepare-original-valid", "prepare-original-incompatible", "no-auto-prepare"):
        root = out / "state" / label
        prefix = bootstrap(root, ORIGINAL)
        if label == "prepare-original-incompatible":
            original = Holder(ORIGINAL, root)
            try:
                original.call("accept", B)
            finally:
                original.close()
        before = independent(root / "store.sqlite")
        if label == "no-auto-prepare":
            argv = [sys.executable, str(source), json.dumps(dict(path=str(root / "store.sqlite"), root="work", profile="independent", channels=[], trace=str(root / "startup-sql.jsonl")))]
        else:
            argv = [sys.executable, str(source), "--prepare", str(root / "store.sqlite")]
        start = time.monotonic_ns()
        attempt = subprocess.run(argv, text=True, capture_output=True, timeout=5)
        cases[label] = dict(prefix=prefix, before=before, attempt=dict(argv=argv, start_ns=start,
                            end_ns=time.monotonic_ns(), exit=attempt.returncode, stdout=attempt.stdout,
                            stderr=attempt.stderr), final=independent(root / "store.sqlite"))
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--mode", choices=("original", "repaired", "mutant"), default="original")
    args = parser.parse_args()
    if args.snapshot:
        print(json.dumps(snapshot(args.snapshot), sort_keys=True))
        return 0
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    data = dict(pin=PIN, mode=args.mode, started_ns=time.monotonic_ns(), probe_sha256=sha(Path(__file__).read_bytes()),
                commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                environment=dict(python=sys.version, sqlite=sqlite3.sqlite_version, platform=platform.platform(),
                                 executable=sys.executable, executable_sha256=sha(Path(sys.executable).read_bytes())))
    result = 0
    try:
        source = HERE / "repaired_service.py"
        if args.mode == "mutant":
            original_text = source.read_text()
            changed = original_text.replace("elif candidate.content != current.content or retained is None:", "elif False:  # MUTANT: omit missing-bundle admission protection")
            assert changed != original_text
            changed = changed.replace(next(line for line in changed.splitlines() if line.startswith("ORIGINAL = ")), "ORIGINAL = Path(" + repr(str(ORIGINAL)) + ")")
            source = out / "missing_bundle_mutant.py"
            source.write_text(changed)
        data["cases"] = baseline(out) if args.mode == "original" else repaired_cases(out, source) if args.mode == "repaired" else baseline(out, source, True, {"cold-missing"})
        data["source_hashes"] = {str(p): sha(p.read_bytes()) for p in (ORIGINAL, ORIGINAL.parent.parent.parent / "kernel-0/kernel0_recovery_service.py", ORIGINAL.parent.parent.parent / "kernel-0/kernel0_service.py", source) if p.exists()}
        data["execution"] = "PASS"
    except BaseException:
        data.update(execution="ERROR", error=traceback.format_exc())
        result = 1
    finally:
        for process in PROCESSES:
            process.close()
        data.update(processes=[p.meta for p in PROCESSES], ended_ns=time.monotonic_ns())
        (out / "raw.json").write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(execution=data["execution"], cases=len(data.get("cases", {})), out=str(out))))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
