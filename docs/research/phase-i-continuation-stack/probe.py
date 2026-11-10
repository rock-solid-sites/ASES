#!/usr/bin/env python3
"""Native F1/L5/L6/F4 histories with retry observation and cold activation."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ADMISSION_DIR = HERE.parent / "phase-i-effect-admission"
COMPOSED_DIR = HERE.parent / "phase-i-composed-effects"
COLD_DIR = HERE.parent / "phase-i-cold-activation"
SINK = HERE / "continuation_sink.py"
NATIVE_SOURCES = HERE.parent / "phase-i-sol-integration" / "evidence" / "sources"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


compose = load("continuation_composed_probe", COMPOSED_DIR / "probe.py")
admit = compose.admit
n = admit.n
CONTENT = admit.CONTENT


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def http_or_error(port, path, data=None):
    try:
        return n.http(port, path, data)
    except Exception as error:
        return {"transport_error": type(error).__name__ + ":" + str(error)}


class Sink:
    def __init__(self, case, recover=False):
        self.case = case
        self.root = Path(case["root"])
        self.root_f4 = self.root / "f4"
        self.root_f4.mkdir(parents=True, exist_ok=True)
        self.config = case["config"]
        self.journal = self.root_f4 / "sink-effects.jsonl"
        self.config_path = self.root_f4 / "admission-config.json"
        self.config_path.write_text(canonical(self.config) + "\n")
        self.witness = n.Child([sys.executable, "-B", SINK, "--witness", self.config["import_id"]])
        self.wp = self.witness.ready["port"]
        genesis = dict(authority=dict(created=False, granted=False, active=False,
                                     authority_version=0, holder="old"), journal_sha256=sha(b""))
        self.wcall("/init", cut=genesis)
        self.calls = []
        self.processes = []
        self.start(recover)
        if not recover:
            self.call("/create", {})
            self.call("/grant", {})
            self.call("/activate", {"authority_version": 1})

    def start(self, recover=True):
        argv = [sys.executable, "-B", SINK, "--sink", "recover" if recover else "fresh",
                self.journal, str(self.wp), "published-cut", self.config["import_id"], self.config_path]
        self.sink = n.Child(argv)
        self.port = self.sink.ready.get("port")
        self.processes.append(self.sink.meta)
        return copy.deepcopy(self.sink.ready)

    def wcall(self, path, **data):
        return n.http(self.wp, path, dict(root=self.config["import_id"],
                                          nonce="continuation-" + str(time.monotonic_ns()), **data))

    def call(self, path, data):
        before = n.blob(self.journal)
        response = n.http(self.port, path, data)
        frame = dict(path=path, request=data, response=response, before=before, after=n.blob(self.journal))
        self.calls.append(frame)
        return response

    def submit(self, envelope, version=1):
        return self.call("/submit", dict(authority_version=version, request_id=envelope["request_id"],
                                          payload=canonical(envelope)))

    def kill_recover(self):
        before = [self.journal.stat().st_dev, self.journal.stat().st_ino]
        stopped = self.sink.close(True)
        self.start(True)
        return dict(stopped=stopped, ready=copy.deepcopy(self.sink.ready),
                    journal_identity_before=before,
                    journal_identity_after=[self.journal.stat().st_dev, self.journal.stat().st_ino])

    def close_sink(self):
        if self.sink.p.poll() is None:
            return self.sink.close(True)
        return self.sink.meta

    def close(self):
        self.close_sink()
        self.witness.close(True)


def changed_request(case, suffix, payload_suffix=None):
    value = copy.deepcopy(case["envelope"])
    value["request_id"] += suffix
    if payload_suffix is not None:
        value["epoch"] += payload_suffix
    return value


def source_frame(case):
    root = Path(case["root"])
    return dict(f1=admit.tree(root / "f1"), l5=admit.tree(root / "l5"),
                l6=admit.tree(root / "l6"))


def finish(case, sink, before, actions):
    status = http_or_error(sink.port, "/status") if sink.sink.p.poll() is None else None
    witness = http_or_error(sink.wp, "/status")
    raw_files = {"f1": admit.tree(Path(case["root"]) / "f1"),
                 "l5": admit.tree(Path(case["root"]) / "l5"),
                 "l6": admit.tree(Path(case["root"]) / "l6"),
                 "f4": admit.tree(Path(case["root"]) / "f4")}
    sink.close()
    final = dict(name=Path(case["root"]).name, envelope=case["envelope"], config=case["config"],
                 before=before, after=source_frame(case), actions=actions, calls=sink.calls,
                 local=n.blob(sink.journal), sink_status=status, witness=witness,
                 sink_processes=copy.deepcopy(sink.processes), witness_process=sink.witness.meta,
                 raw_files=raw_files)
    return final


def valid_cold_continue(out):
    case = admit.setup_case(out / "state/valid-cold-continue", "valid-cold-continue")
    before = source_frame(case)
    sink = Sink(case)
    actions = {}
    actions["fault"] = sink.wcall("/fault", reject_publish=False, drop_publish_reply_once=True)
    actions["first"] = sink.submit(case["envelope"])
    actions["first_local"] = n.blob(sink.journal)
    actions["first_witness"] = n.http(sink.wp, "/status")
    actions["cold"] = sink.kill_recover()
    actions["cold_status"] = n.http(sink.port, "/status")["body"]
    active_before = n.blob(sink.journal)
    actions["activate_only_active_prefix"] = sink.call("/activate", {"authority_version": 1})
    actions["activate_only_journal_before"] = active_before
    actions["activate_only_journal_after"] = n.blob(sink.journal)
    actions["historical_while_sealed"] = sink.submit(case["envelope"])
    actions["historical_journal_after"] = n.blob(sink.journal)
    conflict = copy.deepcopy(case["envelope"])
    conflict["epoch"] += ":conflicting-payload"
    witness_log_before = n.http(sink.wp, "/status")["body"]["log"]
    actions["conflict_while_sealed"] = sink.submit(conflict)
    witness_log_after = n.http(sink.wp, "/status")["body"]["log"]
    actions["witness_log_before_conflict"] = witness_log_before
    actions["witness_log_after_conflict"] = witness_log_after
    actions["witness_log_unchanged_for_conflict"] = witness_log_before == witness_log_after
    b = changed_request(case, ":new-B")
    actions["new_B_while_sealed"] = sink.submit(b)
    actions["after_sealed_B"] = n.blob(sink.journal)
    actions["replace"] = sink.call("/replace", {"holder": "cold-continued-holder"})
    actions["after_replace"] = n.http(sink.port, "/status")["body"]
    actions["activate"] = sink.call("/activate", {"authority_version": 2})
    actions["new_B_after_activation"] = sink.submit(b, version=2)
    c = changed_request(case, ":old-token-new-ID")
    actions["old_version_new_id"] = sink.submit(c, version=1)
    actions["historical_A_after_v2"] = sink.submit(case["envelope"], version=2)
    return finish(case, sink, before, actions)


def source_removed_cold(out):
    case = admit.setup_case(out / "state/source-removed-cold", "source-removed-cold")
    before = source_frame(case)
    sink = Sink(case)
    actions = {"first": sink.submit(case["envelope"])}
    actions["journal_after_first"] = n.blob(sink.journal)
    actions["l6_before_remove"] = admit.tree(Path(case["root"]) / "l6")
    actions["l6_remove"] = admit.l6_change(case, "remove")
    actions["l6_after_remove"] = admit.tree(Path(case["root"]) / "l6")
    actions["cold"] = sink.kill_recover()
    actions["historical_A_source_removed_sealed"] = sink.submit(case["envelope"])
    actions["journal_after_historical"] = n.blob(sink.journal)
    actions["replace"] = sink.call("/replace", {"holder": "source-disposed-holder"})
    actions["activate"] = sink.call("/activate", {"authority_version": 2})
    b = changed_request(case, ":new-B-source-disposed")
    actions["new_B_after_v2_and_disposal"] = sink.submit(b, version=2)
    actions["journal_after_new_B"] = n.blob(sink.journal)
    actions["historical_A_after_source_denial"] = sink.submit(case["envelope"], version=2)
    return finish(case, sink, before, actions)


def inactive_prefix_cold(out):
    case = admit.setup_case(out / "state/inactive-prefix-cold", "inactive-prefix-cold")
    before = source_frame(case)
    sink = Sink(case)
    actions = {"first": sink.submit(case["envelope"])}
    actions["cold_active"] = sink.kill_recover()
    actions["replace_v2"] = sink.call("/replace", {"holder": "before-inactive-recovery"})
    actions["replaced_status"] = n.http(sink.port, "/status")["body"]
    actions["kill_between"] = sink.kill_recover()
    actions["cold_inactive_status"] = n.http(sink.port, "/status")["body"]
    before_activate = n.blob(sink.journal)
    actions["activate_only_inactive_prefix"] = sink.call("/activate", {"authority_version": 2})
    actions["inactive_activate_before"] = before_activate
    actions["inactive_activate_after"] = n.blob(sink.journal)
    actions["historical_A_inactive_sealed"] = sink.submit(case["envelope"], version=2)
    actions["replace_v3"] = sink.call("/replace", {"holder": "after-inactive-recovery"})
    actions["activate_v3"] = sink.call("/activate", {"authority_version": 3})
    b = changed_request(case, ":new-B-v3")
    actions["new_B_v3"] = sink.submit(b, version=3)
    c = changed_request(case, ":stale-v2")
    actions["new_C_stale_v2"] = sink.submit(c, version=2)
    return finish(case, sink, before, actions)


def remote_rejection(out):
    case = admit.setup_case(out / "state/remote-rejection", "remote-rejection")
    before = source_frame(case)
    sink = Sink(case)
    actions = {"fault": sink.wcall("/fault", reject_publish=True)}
    actions["first"] = sink.submit(case["envelope"])
    actions["local_after_first"] = n.blob(sink.journal)
    actions["witness_after_first"] = n.http(sink.wp, "/status")
    actions["same_retry"] = sink.submit(case["envelope"])
    actions["local_after_same"] = n.blob(sink.journal)
    conflict = copy.deepcopy(case["envelope"])
    conflict["epoch"] += ":known-conflict"
    witness_before = n.http(sink.wp, "/status")["body"]["log"]
    actions["conflict"] = sink.submit(conflict)
    witness_after = n.http(sink.wp, "/status")["body"]["log"]
    actions["witness_log_before_conflict"] = witness_before
    actions["witness_log_after_conflict"] = witness_after
    actions["witness_calls_unchanged_by_conflict"] = witness_before == witness_after
    stopped = sink.sink.close(True)
    sink.processes[-1] = stopped
    actions["cold_start"] = sink.start(True)
    actions["cold_start_error"] = sink.sink.ready
    # Keep process alive only if it unexpectedly reached ready; always preserve
    # startup frame and actual process return code.
    return finish(case, sink, before, actions)


def unsupported_schema_v2(out):
    case = admit.setup_case(out / "state/unsupported-schema-v2", "unsupported-schema-v2")
    original_a = copy.deepcopy(case["envelope"])
    before = source_frame(case)
    sink = Sink(case)
    actions = {"first": sink.submit(case["envelope"])}
    actions["accepted_before_schema_change"] = n.blob(sink.journal)
    l5root = Path(case["root"]) / "l5"
    l5_source = admit.L5DIR / "l5_integrated.py"
    l5 = n.module("continuation_schema_l5", l5_source)
    fixture = n.module("continuation_schema_fixture", admit.L5DIR / "test_management_conformance.py")
    selector, state = l5.load_current(l5root)
    actions["previous_generation"] = dict(selector=selector,
        sha256=sha((l5root / "protected" / selector).read_bytes()), state=state)
    malformed = copy.deepcopy(state)
    malformed["schema"] = 2
    new_record = fixture.publish(l5root, malformed, name="record-000003.json")
    selector, current = l5.load_current(l5root)
    generation = dict(selector=selector, sha256=sha(new_record.read_bytes()))
    # This is a test-only malformed current image, not a native authorized move.
    actions["malformed_current"] = dict(kind="test-only-malformed-recovery-image",
        native_authorized_migration=False, generation=generation,
        selected_schema=current.get("schema"), graph_valid=l5.graph_valid(current),
        selected_record_raw_hex=new_record.read_bytes().hex(),
        selected_record_sha256=sha(new_record.read_bytes()))
    b = copy.deepcopy(original_a)
    b["l5"] = generation
    b["request_id"] += ":new-B-schema-2"
    actions["historical_A_after_schema_change"] = sink.submit(original_a)
    actions["replace_v2"] = sink.call("/replace", {"holder": "schema-changed-holder"})
    actions["activate_v2"] = sink.call("/activate", {"authority_version": 2})
    # B carries the actual selected record generation, so equality checks do
    # not mask the interpretation/schema refusal.
    actions["new_B_envelope"] = b
    actions["new_B_v2_actual_generation"] = sink.submit(b, version=2)
    actions["journal_after_new_B"] = n.blob(sink.journal)
    actions["historical_A_after_schema_denial"] = sink.submit(original_a, version=2)
    return finish(case, sink, before, actions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    n.CHILDREN.clear(); n.PROCESSES.clear(); n.EVENTS.clear()
    source_paths = {
        SINK, HERE / "probe.py", HERE / "check.py",
        COLD_DIR / "cold_sink.py", COMPOSED_DIR / "composed_sink.py",
        COMPOSED_DIR / "probe.py", COMPOSED_DIR / "check.py",
        ADMISSION_DIR / "admission.py", ADMISSION_DIR / "admission_sink.py",
        ADMISSION_DIR / "probe.py", ADMISSION_DIR / "check.py",
        HERE.parent / "phase-i-effect-retry" / "candidate.py",
        HERE.parent / "phase-i-effect-retry" / "probe.py",
        HERE.parent / "phase-i-effect-retry" / "check.py",
        HERE.parent / "phase-i-sol-integration" / "native.py",
    }
    source_paths.update(p for p in NATIVE_SOURCES.rglob("*.py") if p.is_file())
    data = dict(schema="ases.phase-i-continuation-stack.v1", execution="RUNNING",
                started_ns=time.monotonic_ns(), branch=subprocess.check_output(
                    ["git", "branch", "--show-current"], cwd=REPO, text=True).strip(),
                commits={"admission": "671ecc09", "retry": "16e6460f",
                         "composed": "0e724a6c", "cold": "4485a834"},
                source_hashes={str(path.relative_to(REPO)): sha(path.read_bytes())
                               for path in sorted(source_paths)},
                pins=n.PINS, python=sys.version, cases={})
    try:
        data["cases"]["valid-cold-continue"] = valid_cold_continue(out)
        data["cases"]["source-removed-cold"] = source_removed_cold(out)
        data["cases"]["inactive-prefix-cold"] = inactive_prefix_cold(out)
        data["cases"]["remote-rejection"] = remote_rejection(out)
        data["cases"]["unsupported-schema-v2"] = unsupported_schema_v2(out)
        data["execution"] = "PASS"
    except BaseException:
        data["execution"] = "ERROR"
        data["harness_error"] = traceback.format_exc()
    finally:
        data.update(events=n.EVENTS, processes=n.PROCESSES, finished_ns=time.monotonic_ns())
        (out / "raw.json").write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    print(canonical(dict(execution=data["execution"], cases=len(data["cases"]), output=str(out))))
    return 0 if data["execution"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
