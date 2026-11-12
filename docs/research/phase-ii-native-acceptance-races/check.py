#!/usr/bin/env python3
"""Raw-evidence checks for native duplicate acceptance and producer overlap."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FROZEN = "f7b16ddbf34034ce1a0967c37cd92d5869f7e399"
CURRENT_PROBE = "docs/research/phase-ii-native-acceptance-races/probe.py"
REQUIRED_SOURCES = {
    "docs/research/phase-i-f1-recovery-repair/repaired_service.py",
    "docs/research/phase-i-f1-recovery-repair/probe.py",
    "docs/research/phase-i-sol-integration/evidence/sources/f1/docs/research/phase-i-f1/c11-sqlite/c11_service.py",
    "docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py",
    "docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/worker.py",
    "docs/research/phase-i-sol-integration/evidence/sources/l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/store.py",
    "docs/research/phase-i-sol-integration/evidence/sources/l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/race/race_store.py",
    "docs/research/phase-i-sol-integration/native.py",
    "docs/research/phase-ii-native-ownership/native_owner.py",
    "docs/research/phase-ii-native-ownership/owner_cli.py",
    "docs/research/phase-ii-native-ownership/native_sink.py",
    "docs/research/phase-ii-native-ownership/unix_transport.py",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify_sources(sources: dict) -> None:
    need(isinstance(sources, dict) and sources, "source manifest missing")
    normalized = []
    found = set()
    for key, item in sources.items():
        if isinstance(item, str):
            path, digest = key, item
        else:
            need(isinstance(item, dict), f"invalid source record: {key}")
            path, digest = item.get("path"), item.get("sha256")
        need(isinstance(path, str) and isinstance(digest, str), f"incomplete source record: {key}")
        source_path = Path(path)
        if source_path.is_absolute():
            source_path = source_path.resolve().relative_to(REPO)
        relative = source_path.as_posix()
        found.add(relative)
        normalized.append((relative, digest))
    need(REQUIRED_SOURCES <= found, "source manifest omits required frozen F1/F3/L5/L6/F4 inputs")
    need(CURRENT_PROBE in found, "source manifest omits the executed acceptance-races probe")
    for path, expected in normalized:
        if path == CURRENT_PROBE:
            actual = (REPO / path).read_bytes()
        else:
            actual = subprocess.run(["git", "show", f"{FROZEN}:{path}"], cwd=REPO,
                                     check=True, stdout=subprocess.PIPE).stdout
        need(sha(actual) == expected, f"source differs from frozen parent/current probe: {path}")


def checked_raw(name: str, record: dict, *, size_key: str = "size",
                hash_key: str = "sha256") -> bytes:
    raw = bytes.fromhex(record["raw_hex"])
    need(len(raw) == record.get(size_key), f"{name}: byte size mismatch")
    need(sha(raw) == record.get(hash_key), f"{name}: SHA-256 mismatch")
    return raw


def selected_owner(name: str, snapshot: dict) -> dict:
    current = bytes.fromhex(snapshot["current_raw_hex"])
    selector = current.decode("utf-8").strip()
    need(selector == snapshot.get("selector"), f"{name}: CURRENT selector mismatch")
    record = bytes.fromhex(snapshot["record_raw_hex"])
    need(sha(record) == snapshot.get("record_sha256"), f"{name}: selected record hash mismatch")
    state = json.loads(record)
    need(state == snapshot.get("state"), f"{name}: parsed state differs from selected record bytes")
    need(state.get("native_owner") == snapshot.get("native_owner")
         and state.get("current_ingress") == snapshot.get("current_ingress"),
         f"{name}: direct fields differ from selected owner record")
    tree = snapshot.get("record_files", {})
    current_file = tree.get("CURRENT") or tree.get("protected/CURRENT")
    record_file = tree.get(selector) or tree.get("protected/" + selector)
    need(current_file is not None and checked_raw(name + "/tree CURRENT", current_file) == current,
         f"{name}: owner tree does not bind direct CURRENT bytes")
    need(record_file is not None and checked_raw(name + "/tree selected", record_file) == record,
         f"{name}: owner tree does not bind selected record bytes")
    return state


def sqlite_queries(name: str, snapshot: dict) -> dict:
    raw = bytes.fromhex(snapshot["snapshot_raw_hex"])
    need(len(raw) == snapshot.get("snapshot_size"), f"{name}: SQLite image size mismatch")
    need(sha(raw) == snapshot.get("snapshot_sha256"), f"{name}: SQLite image hash mismatch")
    need(snapshot.get("integrity_check") == "ok", f"{name}: SQLite integrity check failed")
    queries = snapshot["queries"]
    # Re-run the fixed read-only selections against the serialized backup so
    # query summaries cannot replace the captured SQLite state.
    db = sqlite3.connect(":memory:")
    db.deserialize(raw)
    need(db.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
         f"{name}: serialized SQLite image failed integrity check")
    if set(queries) == {"kernel", "selected", "retained"}:
        actual = {
            "kernel": [list(row) for row in db.execute(
                "SELECT id,root,profile,version,view FROM kernel ORDER BY id")],
            "selected": [list(row) for row in db.execute(
                "SELECT id,record FROM consumer_observations ORDER BY id")],
            "retained": [list(row) for row in db.execute(
                "SELECT record FROM retained_observations ORDER BY record")],
        }
    elif set(queries) == {"unit", "dependencies"}:
        actual = {
            "unit": [list(row) for row in db.execute("SELECT live,sealed FROM unit")],
            "dependencies": [list(row) for row in db.execute(
                "SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name")],
        }
    else:
        db.close()
        raise ValueError(f"{name}: unexpected SQLite query set")
    db.close()
    need(actual == queries, f"{name}: captured query rows differ from serialized SQLite image")
    return queries


def selected_f1(name: str, snapshot: dict) -> tuple[dict, dict, list[dict]]:
    queries = sqlite_queries(name, snapshot)
    kernels = queries.get("kernel", [])
    selected_rows = queries.get("selected", [])
    retained_rows = queries.get("retained", [])
    need(len(kernels) == 1 and len(selected_rows) == 1, f"{name}: ambiguous/missing selected F1 rows")
    view = json.loads(kernels[0][4])
    selected = json.loads(selected_rows[0][1])
    retained = [json.loads(row[0]) for row in retained_rows]
    pair = {"accepted_content": view["content"], "required": selected["required"]}
    need(selected in retained, f"{name}: selected F1 observation is not retained")
    return pair, selected, retained


def l6_contents(name: str, snapshot: dict) -> tuple[tuple, list, dict]:
    queries = sqlite_queries(name + " L6", snapshot["l6_sqlite"])
    units = queries.get("unit", [])
    deps = queries.get("dependencies", [])
    need(len(units) == 1, f"{name}: L6 unit row absent")
    files = snapshot.get("l6_files")
    need(isinstance(files, dict), f"{name}: captured L6 object bytes missing")
    for filename, value in files.items():
        content = checked_raw(name + "/" + filename, value)
    live = {row[0]: row for row in deps if row[4] == 0}
    need(set(files) == set(live), f"{name}: live L6 rows do not match captured object inventory")
    for filename, value in files.items():
        need(value["sha256"] == live[filename][2] and value["size"] == live[filename][3],
             f"{name}: inventory digest/size does not bind {filename}")
    return units[0], deps, files


def f1_fingerprint(snapshot: dict) -> str:
    return snapshot["f1_sqlite"]["snapshot_sha256"]


def stable_material_and_f1(name: str, before: dict, after: dict) -> None:
    need(f1_fingerprint(before) == f1_fingerprint(after), f"{name}: F1 snapshot changed")
    left = l6_contents(name + " before", before)
    right = l6_contents(name + " after", after)
    need(left == right, f"{name}: L6 catalog or material changed")


def permission_set(state: dict, unit: str) -> set[str]:
    units = state["work_units"]
    current = unit
    seen: set[str] = set()
    result = {"read", "write"}
    while current is not None:
        need(current in units and current not in seen, "invalid L5 parent path")
        seen.add(current)
        row = units[current]
        result &= set(row["grants"])
        if "latent_ceiling" in row:
            result &= set(row["latent_ceiling"])
        current = row["parent"]
    return result


def checked_journal(name: str, snapshot: dict) -> tuple[bytes, list[dict]]:
    raw = checked_raw(name, snapshot)
    events = [json.loads(line) for line in raw.splitlines() if line]
    need(events == snapshot.get("events"), f"{name}: event list differs from raw journal bytes")
    return raw, events


def effect_rows(events: list[dict]) -> list[dict]:
    return [event for event in events if event.get("event") == "effect_accepted"]


def reply(frame: dict) -> dict:
    return frame.get("reply", frame)


def body(response: dict) -> dict:
    return response.get("body", {}) if isinstance(response, dict) else {}


def f1_summary(name: str, snapshot: dict) -> tuple[dict, list[dict]]:
    need(snapshot.get("integrity") == "ok", f"{name}: F1 integrity summary failed")
    pair, selected, retained = selected_f1(name + " SQLite", snapshot["sqlite"])
    need(pair == snapshot.get("pair") and selected == snapshot.get("selected"),
         f"{name}: F1 summary differs from selected SQLite rows")
    view = json.loads(snapshot["sqlite"]["queries"]["kernel"][0][4])
    need(view == snapshot.get("view"), f"{name}: F1 view differs from selected SQLite rows")
    summary_retained = [json.loads(item) if isinstance(item, str) else item
                        for item in snapshot.get("retained", [])]
    need(retained == summary_retained, f"{name}: F1 retained records differ from SQLite rows")
    return pair, retained


def registration_for(owner: dict, registration_id: str) -> dict:
    matches = [item for item in owner.get("registrations", []) if item.get("id") == registration_id]
    need(len(matches) == 1, f"expected one selected registration {registration_id}")
    return matches[0]


def check_registration_material(label: str, state: dict, registration: dict,
                                pair: dict, files: dict, deps: list) -> None:
    metadata = registration["metadata"]
    need(registration.get("status") == "live" and registration.get("pair") == pair
         and metadata.get("accepted_pair") == pair and metadata.get("identity") == registration.get("id"),
         f"{label}: registration does not bind actual F1 pair")
    filename = Path(metadata["object"]).name
    need(filename in files, f"{label}: registration material absent from L6 owned bytes")
    content = checked_raw(label + " material", files[filename])
    need(content == pair["accepted_content"].encode("utf-8")
         and metadata.get("sha256") == sha(content) and metadata.get("size") == len(content),
         f"{label}: registration metadata does not bind its owned accepted bytes")
    row = next((row for row in deps if row[0] == filename), None)
    need(row is not None and row[1] == "candidate" and row[2] == sha(content)
         and row[3] == len(content) and row[4] == 0,
         f"{label}: registration does not bind a live native L6 inventory row")
    accepted = state["work_units"]["C"].get("accepted_contents", [])
    if registration.get("id") == state["native_owner"].get("selected"):
        need(accepted == [metadata], f"{label}: selected C content is not selected by actual L5 state")


def state_pair_identity(owner: dict) -> tuple:
    return (owner.get("epoch"), owner.get("selected"),
            tuple((item.get("id"), item.get("status"), item.get("pair"), item.get("metadata"))
                  for item in owner.get("registrations", [])), owner.get("effects"))


def frame_values(process: dict) -> list[dict]:
    return [item.get("value", {}) for item in process.get("frames", []) if isinstance(item, dict)]


def assert_process_frame(process: dict, event: dict, what: str) -> None:
    values = frame_values(process)
    need(any(value == event for value in values), f"{what}: captured process frames omit actual event")


def assert_f1_pair_retained(name: str, pair: dict, retained: list[dict], *required: dict) -> None:
    need(pair in retained, f"{name}: actual selected F1 world is not retained")
    for value in required:
        need(value in retained, f"{name}: required historical F1 world is not retained")


def check_duplicate_acceptance(case: dict) -> None:
    need(case.get("label") == "duplicate-acceptance", "duplicate fixture label")
    gate = case["initiator_gate"]
    need(gate.get("event") == "GATE" and gate.get("phase") == "material-prepared",
         "duplicate fixture did not pause at actual material-prepared gate")
    need(gate == case["initiator_process_before_gate"], "duplicate gate frame changed between captures")
    need(case["initiator_process"].get("pid") == gate.get("pid"),
         "duplicate gate not emitted by actual initiating owner process")
    assert_process_frame(case["initiator_process"], gate, "duplicate first owner")

    before = selected_owner("duplicate before preparation", case["owner_before_guard"])
    at_gate = selected_owner("duplicate at preparation gate", case["owner_at_gate"])
    c_f1, _selected_c, c_retained = selected_f1(
        "duplicate F1 at gate", case["owner_at_gate"]["f1_sqlite"])
    a_f1, a_retained = f1_summary("earlier A F1", case["setup"]["f1_after_a"])
    need(c_f1 == case["f1_at_gate"]["pair"] and c_f1 == case["setup"]["f1_after_c"]["pair"],
         "duplicate: current F1 C does not match direct selected/producer records")
    need(c_f1["accepted_content"] == a_f1["accepted_content"]
         and c_f1["required"] != a_f1["required"],
         "duplicate: C must preserve A bytes while identifying a distinct F1 world")
    assert_f1_pair_retained("duplicate gate", c_f1, c_retained, a_f1)
    assert_f1_pair_retained("earlier A retained", a_f1, a_retained, a_f1)
    need(before["current_ingress"] is None and at_gate["current_ingress"] is None,
         "duplicate: owner must be sealed at preparation boundary")
    owner_before = before["native_owner"]
    owner_gate = at_gate["native_owner"]
    need(owner_gate["registrations"] == owner_before["registrations"]
         and owner_gate["selected"] == owner_before["selected"]
         and owner_gate["epoch"] == owner_before["epoch"],
         "duplicate: gate selected C before the actual owner commit")
    need(len(owner_before["registrations"]) == 1,
         "duplicate: expected only original A registration before C commit")
    a_registration = owner_before["registrations"][0]
    a_pair = a_registration["pair"]
    need(a_pair == a_f1, "duplicate: original native registration does not bind actual F1 A")

    unit_before, deps_before, files_before = l6_contents("duplicate pre-prepare", case["owner_before_guard"])
    unit_gate, deps_gate, files_gate = l6_contents("duplicate material-prepared", case["owner_at_gate"])
    need(unit_before[0] == 1 and unit_gate[0] == 1, "duplicate: L6 authority is not live")
    before_names, gate_names = set(files_before), set(files_gate)
    need(gate_names - before_names == {"objectb"} and before_names == {"objecta"},
         "duplicate: preparation gate did not add exactly one C material object")
    need({row[0] for row in deps_gate} - {row[0] for row in deps_before} == {"objectb"},
         "duplicate: L6 catalog did not add exactly one C material dependency")
    need(bytes.fromhex(files_gate["objectb"]["raw_hex"]) == c_f1["accepted_content"].encode("utf-8")
         and bytes.fromhex(files_gate["objecta"]["raw_hex"]) == a_f1["accepted_content"].encode("utf-8"),
         "duplicate: A/C physical material bytes are not preserved and equal")
    need(case["owner_at_gate"]["selector"] == case["owner_before_guard"]["selector"]
         and case["owner_at_gate"]["record_raw_hex"] == case["owner_before_guard"]["record_raw_hex"],
         "duplicate: CURRENT advanced before C registration commit")
    stable_material_and_f1("duplicate prepared contender baseline",
                           case["contender_before_request"], case["owner_after_contender"])
    contender_after = selected_owner("duplicate after refused contender", case["owner_after_contender"])
    contender_before = selected_owner("duplicate before refused contender", case["contender_before_request"])
    need(case["contender_before_request"]["current_raw_hex"] == case["owner_at_gate"]["current_raw_hex"]
         and contender_before == at_gate and contender_after == at_gate,
         "duplicate: refused contender changed CURRENT/native owner state")
    need(case["contender_before_request"]["l6_files"] == files_gate
         and case["owner_after_contender"]["l6_files"] == files_gate,
         "duplicate: refused contender changed prepared material")

    contender_request = case["contender_request"]
    contender_response = case["contender_reply"]
    contender_process = case["contender_process"]
    need(contender_process.get("pid") != case["initiator_process"].get("pid")
         and contender_process.get("start_ns", 0) < gate.get("ns", case["gate_ns"]),
         "duplicate: second owner was not a separate process started before the guard")
    need(contender_request.get("op") == "accept"
         and case["gate_ns"] <= contender_request.get("started_ns", 0)
         < contender_request.get("finished_ns", 0) <= case["release_ns"],
         "duplicate: actual competing accept did not overlap the held owner guard")
    need(contender_response.get("event") == "RESPONSE"
         and reply(contender_response).get("result") == "DENY"
         and "locked" in reply(contender_response).get("reason", "").lower()
         and reply(contender_response).get("owner_selection_changed") is False
         and reply(contender_response).get("durable_phase_changed") is False,
         "duplicate: actual competing issuer did not return unchanged busy/refusal")
    assert_process_frame(contender_process, contender_response, "duplicate contender")

    accepted_frame = case["first_accept_reply"]
    accepted_reply = reply(accepted_frame)
    accepted_state = selected_owner("duplicate after first C acceptance", case["owner_after_first_accept"])
    need(accepted_reply.get("result") == "COMMITTED" and accepted_reply.get("duplicate") is False,
         "duplicate: first native C issuer did not commit a new registration")
    c_registration = accepted_reply.get("registration")
    need(isinstance(c_registration, dict), "duplicate: first C registration frame missing")
    need(accepted_state["native_owner"].get("epoch") == owner_before["epoch"] + 1
         and accepted_state["native_owner"].get("selected") == c_registration.get("id"),
         "duplicate: first C registration did not advance CURRENT/epoch exactly once")
    need(accepted_state["native_owner"].get("registrations") == [a_registration, c_registration],
         "duplicate: selected owner state does not contain exactly one A and one C registration")
    c_registration_actual = registration_for(accepted_state["native_owner"], c_registration["id"])
    need(c_registration_actual == c_registration and c_registration_actual["pair"] == c_f1,
         "duplicate: committed C registration does not bind actual selected F1 C at gate")
    unit_after, deps_after, files_after = l6_contents("duplicate after C acceptance", case["owner_after_first_accept"])
    check_registration_material("original A registration", accepted_state, a_registration,
                                a_pair, files_after, deps_after)
    check_registration_material("new C registration", accepted_state, c_registration_actual,
                                c_f1, files_after, deps_after)
    need(unit_after[0] == 1 and set(files_after) == {"objecta", "objectb"},
         "duplicate: A/C material inventory is incomplete or contains extra material")
    f1_after_first, retained_after_first = f1_summary("duplicate F1 after first commit",
                                                       case["f1_after_first_accept"])
    need(f1_after_first == c_f1, "duplicate: F1 C changed during first native acceptance")
    assert_f1_pair_retained("duplicate after first commit", f1_after_first,
                            retained_after_first, a_f1)
    need(case["owner_after_first_accept"]["f1_sqlite"]["snapshot_sha256"]
         == case["owner_at_gate"]["f1_sqlite"]["snapshot_sha256"],
         "duplicate: F1 changed across a native-only acceptance")

    before_retry = selected_owner("duplicate before idempotent retry", case["owner_before_duplicate_retry"])
    after_retry = selected_owner("duplicate after idempotent retry", case["owner_after_duplicate_retry"])
    retry_reply = reply(case["duplicate_retry_reply"])
    need(case["duplicate_retry_request"].get("op") == "accept"
         and case["duplicate_retry_request"].get("started_ns", 0) >= case["first_accept_commit_ns"],
         "duplicate: exact duplicate retry did not follow first C commit")
    need(retry_reply.get("result") == "COMMITTED" and retry_reply.get("duplicate") is True
         and retry_reply.get("registration") == c_registration,
         "duplicate: retry did not return the exact already-selected C registration")
    need(before_retry == accepted_state and after_retry == accepted_state
         and case["owner_before_duplicate_retry"]["current_raw_hex"]
         == case["owner_after_duplicate_retry"]["current_raw_hex"],
         "duplicate: idempotent retry changed owner CURRENT or native state")
    stable_material_and_f1("duplicate retry", case["owner_before_duplicate_retry"],
                           case["owner_after_duplicate_retry"])
    need(case["owner_before_duplicate_retry"]["l6_files"]
         == case["owner_after_duplicate_retry"]["l6_files"] == files_after,
         "duplicate: retry added or removed owned material")
    f1_after_retry, retained_after_retry = f1_summary("duplicate F1 after duplicate retry",
                                                       case["f1_after_duplicate_retry"])
    need(f1_after_retry == c_f1 and retained_after_retry == retained_after_first,
         "duplicate: retry changed F1 current or retained observations")
    need(case["owner_before_duplicate_retry"]["native_owner"]["epoch"]
         == case["owner_after_duplicate_retry"]["native_owner"]["epoch"]
         == accepted_state["native_owner"]["epoch"],
         "duplicate: retry advanced native epoch")


def check_producer_overlap(case: dict) -> None:
    need(case.get("label") == "producer-overlap", "producer fixture label")
    gate = case["initiator_gate"]
    need(gate.get("event") == "GATE" and gate.get("phase") == "material-prepared"
         and gate.get("pid") == case["initiator_process"].get("pid"),
         "producer fixture did not pause first C acceptance at actual material-prepared gate")
    assert_process_frame(case["initiator_process"], gate, "producer fixture owner")
    owner_before = selected_owner("producer before C preparation", case["owner_before_guard"])
    owner_gate = selected_owner("producer C preparation gate", case["owner_at_gate"])
    c_f1, _selected_c, c_retained = selected_f1(
        "producer C at owner gate", case["owner_at_gate"]["f1_sqlite"])
    a_f1, a_retained = f1_summary("producer earlier A F1", case["setup"]["f1_after_a"])
    gate_summary, gate_retained = f1_summary("producer F1 at gate", case["f1_before_producer"])
    before_release, before_release_retained = f1_summary("producer F1 before gate release",
                                                          case["f1_at_gate_before_release"])
    need(gate_summary == before_release == c_f1 and gate_retained == before_release_retained,
         "producer: current F1 C changed while owner held acceptance guard")
    need(c_f1["accepted_content"] == a_f1["accepted_content"]
         and c_f1["required"] != a_f1["required"],
         "producer: C did not preserve A bytes with a distinct F1 world")
    assert_f1_pair_retained("producer C at gate", c_f1, c_retained, a_f1)
    assert_f1_pair_retained("producer A retained", a_f1, a_retained, a_f1)
    need(owner_gate["native_owner"]["registrations"] == owner_before["native_owner"]["registrations"]
         and owner_gate["native_owner"]["selected"] == owner_before["native_owner"]["selected"]
         and case["owner_at_gate"]["selector"] == case["owner_before_guard"]["selector"],
         "producer: C became selected before its first native acceptance committed")
    _, deps_before, files_before = l6_contents("producer before C preparation", case["owner_before_guard"])
    _, deps_gate, files_gate = l6_contents("producer at C material gate", case["owner_at_gate"])
    need(set(files_gate) - set(files_before) == {"objectb"}
         and set(files_before) == {"objecta"}
         and {row[0] for row in deps_gate} - {row[0] for row in deps_before} == {"objectb"},
         "producer: F3 C preparation did not add exactly one owned object")
    need(bytes.fromhex(files_gate["objectb"]["raw_hex"]) == c_f1["accepted_content"].encode("utf-8"),
         "producer: prepared C bytes do not equal selected F1 content")

    operation = case["producer_operation"]
    need(operation.get("request") == "actual-f1-accept-world-D"
         and operation.get("requested_bundle", {}).get("accepted_content") == c_f1["accepted_content"]
         and operation.get("requested_bundle", {}).get("required")
         != c_f1["required"],
         "producer: overlapping request is not a distinct same-byte D world")
    producer_proc = operation.get("producer_process", {})
    first = operation.get("first_attempt", {})
    first_result = first.get("result") or {}
    producer_operation = first_result.get("operation")
    need(producer_proc.get("pid") and producer_proc.get("pid") != case["initiator_process"].get("pid")
         and operation.get("producer_process_ready_ns", 0) < gate.get("ns", case["gate_ns"]),
         "producer: real F1 Holder was not prestarted before owner acceptance gate")
    need(isinstance(producer_operation, dict), "producer: actual F1 operation wire/timing record missing")
    producer_start = producer_operation.get("start_ns", 0)
    producer_end = producer_operation.get("end_ns", 0)
    release = operation.get("release_ns", 0)
    need(case["gate_ns"] <= producer_start < release
         and operation.get("producer_process_ready_ns", 0) < case["gate_ns"],
         "producer: actual F1 accept operation did not begin while native acceptance guard was held")
    need(operation.get("observation_ns", 0) <= release
         and operation.get("disposition_at_release") in ("pending", "completed"),
         "producer: overlap disposition/timing was not recorded at release")
    if operation["disposition_at_release"] == "pending":
        need(operation.get("observed_complete_before_release") is False
             and producer_end > release
             and operation.get("observed_outcome") == "pending-at-release-committed-after-release",
             "producer: pending request did not actually settle after guard release")
    else:
        need(operation.get("observed_complete_before_release") is True
             and producer_end <= release,
             "producer: completed-at-release disposition conflicts with operation times")

    f1_after_first, retained_after_first = f1_summary("producer first D attempt",
                                                       case["f1_after_first_producer_attempt"])
    retry = case.get("producer_retry")
    if f1_after_first["required"] == operation["requested_bundle"]["required"]:
        need(retry is None, "producer: retried D despite first actual D update already selecting it")
        d_f1, d_retained = f1_summary("producer selected D", case["f1_after_producer"])
        need(d_f1 == f1_after_first and d_retained == retained_after_first,
             "producer: selected F1 D changed after first operation completed")
        first_response = producer_operation.get("response", {})
        need(first_response.get("outcome") == "commit"
             and first_response.get("consumer_query", {}).get("required")
             == operation["requested_bundle"]["required"]
             and producer_end > release
             and case["first_c_accept_commit_ns"] < producer_end,
             "producer: pending D request did not commit after release and C registration commit")
    else:
        need(retry is not None, "producer: busy/error first attempt was not retried")
        d_f1, d_retained = f1_summary("producer selected D after retry", case["f1_after_producer"])
        first_response = producer_operation.get("response", {})
        first_error = first.get("error") or first_result.get("error")
        need(first_error is not None or first_response.get("outcome") != "commit",
             "producer: F1 current remained C without a recorded busy/error outcome")
        need(operation["disposition_at_release"] == "completed" and producer_end <= release,
             "producer: refused F1 update was not observed complete before release")
        need(retry.get("started_ns", 0) > case["first_c_accept_commit_ns"],
             "producer: D retry began before C acceptance committed")
        retry_meta = retry.get("result", {})
        retry_response = retry_meta.get("response", {})
        retry_result = retry_response.get("response", retry_response)
        need(retry_result.get("outcome") == "commit" and retry_result.get("consumer_query", {}).get("required")
             == operation["requested_bundle"]["required"],
             "producer: actual post-C retry did not commit D")
        need(d_f1["required"] == operation["requested_bundle"]["required"],
             "producer: retried F1 update did not select D")
    need(d_f1["accepted_content"] == c_f1["accepted_content"]
         and d_f1["required"] != c_f1["required"],
         "producer: F1 D is not a distinct world with same accepted bytes")
    assert_f1_pair_retained("producer final D", d_f1, d_retained, a_f1, c_f1)
    owner_after_producer = selected_owner("producer after F1 D update", case["owner_after_producer"])
    owner_after_c_accept = selected_owner("producer after C acceptance", case["owner_after_c_accept"])
    need(owner_after_producer["native_owner"].get("selected")
         == owner_after_c_accept["native_owner"].get("selected")
         and len(owner_after_producer["native_owner"].get("registrations", [])) == 2,
         "producer: native selected C identity changed during producer-only D update")
    current_d, _selected_d, _retained_d = selected_f1("producer owner direct F1 D",
                                                        case["owner_before_c_mismatch"]["f1_sqlite"])
    need(current_d == d_f1, "producer: direct native owner snapshot does not see actual current F1 D")

    c_owner = selected_owner("producer before C mismatch", case["owner_before_c_mismatch"])
    c_owner_after = selected_owner("producer after C mismatch", case["owner_after_c_mismatch"])
    c_reg_id = c_owner["native_owner"].get("selected")
    c_reg = registration_for(c_owner["native_owner"], c_reg_id)
    need(c_reg["pair"] == c_f1 and c_reg_id != c_owner["native_owner"]["registrations"][0]["id"],
         "producer: selected native registration is not distinct world C")
    need(c_owner["native_owner"].get("epoch") == c_owner_after["native_owner"].get("epoch")
         and state_pair_identity(c_owner["native_owner"]) == state_pair_identity(c_owner_after["native_owner"])
         and case["owner_before_c_mismatch"]["current_raw_hex"]
         == case["owner_after_c_mismatch"]["current_raw_hex"],
         "producer: denied C-world request changed native owner selection/reservation")
    stable_material_and_f1("producer C mismatch denial", case["owner_before_c_mismatch"],
                           case["owner_after_c_mismatch"])
    c_pair, _c_selected, _c_retained = selected_f1("producer F1 D at mismatch",
                                                     case["owner_before_c_mismatch"]["f1_sqlite"])
    need(c_pair == d_f1 and c_pair["accepted_content"] == c_reg["pair"]["accepted_content"]
         and c_pair["required"] != c_reg["pair"]["required"],
         "producer: selected F1 D does not differ from native C while bytes stay equal")
    active = case["selected_c_active_snapshot"]
    active_state = active["state"]
    need(active_state["native_owner"].get("selected") == c_reg_id
         and active_state["work_units"]["D"].get("active") is True
         and permission_set(active_state, "D") == {"read", "write"},
         "producer: native C was not actually active on the D write-granting path")
    c_envelope = case["c_envelope"]
    need(c_envelope.get("import_id") == c_reg_id
         and c_envelope.get("pair") == c_reg["pair"]
         and c_envelope.get("epoch") == c_owner["native_owner"].get("epoch")
         and c_envelope.get("l5") == {"selector": case["owner_before_c_mismatch"]["selector"],
                                      "sha256": case["owner_before_c_mismatch"]["record_sha256"]},
         "producer: rejected request is not a fresh current-selector native C envelope")
    c_call = case["c_mismatch_request"]
    c_response = c_call.get("response", {})
    need(c_call.get("path") == "/submit"
         and c_call.get("request", {}).get("authority_version") == 1
         and json.loads(c_call["request"]["payload"]) == c_envelope,
         "producer: C-world request did not use exact current outer F4 authority/envelope")
    need(c_response.get("status") == 409 and body(c_response).get("outcome") == "admission-denied"
         and body(c_response).get("reason") == "native-f1-selected-retained-mismatch"
         and body(c_response).get("local_control_committed") is False,
         "producer: current C request did not fail specifically at actual F1 selected/retained comparison")
    mismatch_before, mismatch_events_before = checked_journal("journal before C mismatch",
                                                                case["journal_before_c_mismatch"])
    mismatch_after, mismatch_events_after = checked_journal("journal after C mismatch",
                                                              case["journal_after_c_mismatch"])
    need(mismatch_before == mismatch_after and mismatch_events_before == mismatch_events_after
         and not effect_rows(mismatch_events_after)
         and c_call["before"]["sha256"] == c_call["after"]["sha256"] == sha(mismatch_after),
         "producer: F1 mismatch denial reserved or appended an F4 effect")
    need(c_reg_id not in c_owner["native_owner"].get("effects", {})
         and c_envelope["request_id"] not in c_owner_after["native_owner"].get("effects", {}),
         "producer: F1 mismatch request left an owner effect reservation")

    sealed = reply(case["seal_c_before_d"])
    need(sealed.get("result") == "COMMITTED", "producer: owner did not seal C before accepting D")
    sealed_state = selected_owner("producer after C seal", case["owner_after_seal_c"])
    need(sealed_state["native_owner"].get("selected") == c_reg_id
         and sealed_state["native_owner"].get("epoch") == c_owner["native_owner"].get("epoch") + 1
         and sealed_state["current_ingress"] is None,
         "producer: C seal changed selected registration unexpectedly or did not revoke ingress")
    d_accept_frame = case["accept_d_reply"]
    d_accept = reply(d_accept_frame)
    d_registration = d_accept.get("registration")
    need(d_accept.get("result") == "COMMITTED" and d_accept.get("duplicate") is False
         and isinstance(d_registration, dict), "producer: actual native D acceptance did not commit")
    after_d_accept = selected_owner("producer after native D acceptance", case["owner_after_d_accept"])
    need(after_d_accept["native_owner"].get("epoch") == sealed_state["native_owner"].get("epoch") + 1
         and after_d_accept["native_owner"].get("selected") == d_registration.get("id")
         and d_registration.get("pair") == d_f1,
         "producer: D acceptance did not select current F1 D as new native registration")
    need(len(after_d_accept["native_owner"].get("registrations", [])) == 3,
         "producer: native owner does not retain exactly A, C and D issuer registrations")
    regs = after_d_accept["native_owner"]["registrations"]
    need(len({item.get("id") for item in regs}) == 3,
         "producer: A, C and D did not receive distinct issuer registration identities")
    pair_by_required = [item["pair"]["required"] for item in regs]
    need(len({json.dumps(item, sort_keys=True) for item in pair_by_required}) == 3,
         "producer: A, C and D registrations do not identify three distinct F1 worlds")
    unit_d, deps_d, files_d = l6_contents("producer after D acceptance", case["owner_after_d_accept"])
    need(unit_d[0] == 1 and set(files_d) == {"objecta", "objectb", "objectc"},
         "producer: final A/C/D material inventory is incomplete")
    for reg in regs:
        check_registration_material("producer registration " + reg["id"], after_d_accept,
                                    reg, reg["pair"], files_d, deps_d)
        need(reg["pair"]["accepted_content"] == d_f1["accepted_content"],
             "producer: retained registration content bytes differ across worlds")
    need(set(files_d) == {Path(reg["metadata"]["object"]).name for reg in regs},
         "producer: physical material inventory contains unaccounted issuer objects")
    f1_post_accept, retained_post_accept = f1_summary("producer F1 after D accept",
                                                       case["f1_after_d_accept"])
    need(f1_post_accept == d_f1, "producer: F1 D changed during native D acceptance")
    assert_f1_pair_retained("producer D accepted", d_f1, retained_post_accept, a_f1, c_f1)

    activate = reply(case["activate_d_reply"])
    need(activate.get("result") == "COMMITTED", "producer: D unit activation did not commit")
    before_effect = selected_owner("producer before D effect", case["owner_before_d_effect"])
    before_effect_state = before_effect
    d_registration_actual = registration_for(before_effect["native_owner"],
                                              before_effect["native_owner"].get("selected"))
    d_envelope = case["d_envelope"]
    need(d_registration_actual.get("id") == d_registration.get("id")
         and d_envelope.get("import_id") == d_registration_actual.get("id")
         and d_envelope.get("pair") == d_f1
         and d_envelope.get("epoch") == before_effect["native_owner"].get("epoch")
         and before_effect["current_ingress"] is not None
         and before_effect["work_units"]["D"].get("active") is True
         and permission_set(before_effect, "D") == {"read", "write"},
         "producer: authorized D envelope is not current on an active write-granting native D path")
    d_call = case["d_effect_request"]
    d_response = d_call.get("response", {})
    need(d_call.get("path") == "/submit"
         and d_call.get("request", {}).get("authority_version") == 1
         and json.loads(d_call["request"]["payload"]) == d_envelope,
         "producer: D effect request does not bind current F4 authority and D envelope")
    need(d_response.get("status") == 201 and body(d_response).get("outcome") == "accepted"
         and body(d_response).get("owner_effect", {}).get("status") == "published",
         "producer: valid D-world F4 append did not publish")
    before_journal, before_events = checked_journal("journal before authorized D append",
                                                      case["journal_before_d_effect"])
    after_journal, after_events = checked_journal("journal after authorized D append",
                                                   case["journal_after_d_effect"])
    need(d_call["before"]["sha256"] == sha(before_journal)
         and d_call["after"]["sha256"] == sha(after_journal)
         and before_journal == checked_raw("D request before journal", d_call["before"]),
         "producer: D request journal byte snapshots diverge")
    accepted = effect_rows(after_events)
    need(len(accepted) == 1 and after_events[:len(before_events)] == before_events
         and len(after_events) == len(before_events) + 1,
         "producer: journal does not contain exactly one appended accepted effect")
    event = accepted[0]
    need(event.get("request_id") == d_envelope.get("request_id")
         and json.loads(event.get("payload", "{}")) == d_envelope,
         "producer: actual accepted event does not bind the D-world envelope")
    need(event.get("seq") == body(d_response).get("event_seq")
         and event.get("accepted_under_version") == 1
         and event.get("payload_sha256") == sha(event["payload"].encode("utf-8"))
         and body(d_response).get("published_journal_sha256") == sha(after_journal),
         "producer: append reply does not bind the exact accepted event/journal bytes")
    admission = event.get("admission", {})
    pair_digest = sha(json.dumps(d_envelope["pair"], sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=True).encode("utf-8"))
    need(admission.get("profile") == "native-f3-owner-v1"
         and admission.get("native_registration") is True
         and admission.get("domain_id") == before_effect["native_owner"].get("domain_id")
         and admission.get("import_id") == d_registration_actual.get("id")
         and admission.get("epoch") == d_envelope.get("epoch")
         and admission.get("presented_l5") == d_envelope.get("l5")
         and admission.get("pair_sha256") == pair_digest,
         "producer: F4 journal admission facts do not bind selected D registration/envelope")
    after_effect = selected_owner("producer after D effect", case["owner_after_d_effect"])
    effect_record = after_effect["native_owner"].get("effects", {}).get(d_envelope["request_id"])
    need(effect_record is not None and effect_record.get("status") == "published"
         and effect_record.get("seq") == event.get("seq")
         and set(after_effect["native_owner"].get("effects", {})) == {d_envelope["request_id"]},
         "producer: owner has not published exactly the journaled D effect")
    need(after_effect["native_owner"].get("selected") == d_registration_actual.get("id")
         and after_effect["native_owner"].get("epoch") == before_effect["native_owner"].get("epoch"),
         "producer: F4 append changed native selection/epoch unexpectedly")
    final_journal = case["f4_final_snapshot"]["journal"]
    final_bytes = checked_raw("final F4 journal", final_journal)
    need(final_bytes == after_journal, "producer: final F4 journal differs from actual D append")
    sink_status = case["f4_final_snapshot"].get("sink_status", {})
    witness_status = case["f4_final_snapshot"].get("witness_status", {})
    cut = body(sink_status).get("actual_cut", {})
    witness_cut = body(witness_status).get("current", {})
    need(sink_status.get("status") == 200 and witness_status.get("status") == 200
         and cut.get("authority", {}).get("active") is True
         and cut.get("authority", {}).get("authority_version") == 1
         and cut.get("journal_sha256") == sha(final_bytes)
         and witness_cut.get("journal_sha256") == sha(final_bytes),
         "producer: current outer F4 authority/witness did not publish exact final journal cut")


def require_mutation_rejected(raw: dict, label: str) -> None:
    try:
        if label == "duplicate-insertion":
            check_duplicate_acceptance(raw["cases"]["duplicate_acceptance"])
        elif label == "mismatched-world-append":
            check_producer_overlap(raw["cases"]["producer_overlap"])
        else:
            raise ValueError("unknown altered-evidence control")
    except (ValueError, KeyError, TypeError, AssertionError):
        return
    raise ValueError(f"altered-evidence control was accepted: {label}")


def write_jsonl(snapshot: dict, events: list[dict]) -> bytes:
    raw = b"".join((json.dumps(event, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=True) + "\n").encode("utf-8") for event in events)
    snapshot.update(raw_hex=raw.hex(), size=len(raw), sha256=sha(raw), events=events)
    return raw


def refresh_selected_record(snapshot: dict, state: dict) -> None:
    raw = json.dumps(state, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    selector = snapshot["selector"]
    snapshot.update(record_raw_hex=raw.hex(), record_sha256=sha(raw), state=state,
                    native_owner=state["native_owner"], current_ingress=state["current_ingress"])
    tree = snapshot["record_files"]
    old = tree[selector] if selector in tree else tree["protected/" + selector]
    replacement = dict(old, raw_hex=raw.hex(), size=len(raw), sha256=sha(raw))
    if selector in tree:
        tree[selector] = replacement
    else:
        tree["protected/" + selector] = replacement


def add_l6_duplicate_material(snapshot: dict, source_name: str, new_name: str) -> None:
    files = snapshot["l6_files"]
    source = files[source_name]
    raw = bytes.fromhex(source["raw_hex"])
    duplicate = dict(source, raw_hex=raw.hex(), size=len(raw), sha256=sha(raw),
                     inode=max((item.get("inode", 0) for item in files.values()), default=0) + 1)
    files[new_name] = duplicate
    image = snapshot["l6_sqlite"]
    db = sqlite3.connect(":memory:")
    db.deserialize(bytes.fromhex(image["snapshot_raw_hex"]))
    db.execute("INSERT INTO dependencies(name,kind,sha256,size,disposed) VALUES(?,?,?,?,0)",
               (new_name, "candidate", sha(raw), len(raw)))
    db.commit()
    sqlite_raw = db.serialize()
    image.update(snapshot_raw_hex=sqlite_raw.hex(), snapshot_size=len(sqlite_raw),
                 snapshot_sha256=sha(sqlite_raw), integrity_check="ok")
    image["queries"]["dependencies"] = [list(row) for row in db.execute(
        "SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name")]
    db.close()
    tree = snapshot["record_files"]
    source_key = "objects/" + source_name
    duplicate_key = "objects/" + new_name
    tree[duplicate_key] = dict(tree[source_key], raw_hex=raw.hex(), size=len(raw), sha256=sha(raw),
                               inode=duplicate["inode"])


def altered_controls(raw: dict) -> None:
    # Add a second C registration and independently inventoried same-byte
    # object to the selected first-accept snapshot. Keep the selected owner
    # record and SQLite image internally hash-consistent.
    duplicate = copy.deepcopy(raw)
    case = duplicate["cases"]["duplicate_acceptance"]
    snap = case["owner_after_first_accept"]
    state = copy.deepcopy(snap["state"])
    native = state["native_owner"]
    c_reg = next(item for item in native["registrations"]
                 if item["pair"]["required"].get("consumer_evidence") == "C:consumer_evidence")
    invented = copy.deepcopy(c_reg)
    invented_id = native["domain_id"] + ":invented-C"
    invented["id"] = invented_id
    invented["metadata"]["identity"] = invented_id
    invented["metadata"]["object"] = "objects/objectc"
    native["registrations"].append(invented)
    native["epoch"] += 1
    state["events"].append({"op": "native-accept-f1-subject", "registration_id": invented_id})
    add_l6_duplicate_material(snap, Path(c_reg["metadata"]["object"]).name, "objectc")
    refresh_selected_record(snap, state)
    require_mutation_rejected(duplicate, "duplicate-insertion")

    # Inject a coherent accepted journal row for the C envelope while the raw
    # direct F1 SQLite cut is D. Rehash the journal bytes and request-after
    # record so rejection rests on no-effect/world assertions, not bad hashes.
    mismatch = copy.deepcopy(raw)
    case = mismatch["cases"]["producer_overlap"]
    before_events = case["journal_after_c_mismatch"]["events"]
    valid_d_row = effect_rows(case["journal_after_d_effect"]["events"])[0]
    forged = copy.deepcopy(valid_d_row)
    envelope = copy.deepcopy(case["c_envelope"])
    forged["request_id"] = envelope["request_id"]
    forged["payload"] = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    forged["payload_sha256"] = sha(forged["payload"].encode("utf-8"))
    forged["seq"] = len(before_events) + 1
    c_owner = case["owner_before_c_mismatch"]["native_owner"]
    c_registration = registration_for(c_owner, c_owner["selected"])
    forged["admission"] = dict(forged.get("admission", {}),
                               domain_id=c_owner["domain_id"], import_id=c_registration["id"],
                               epoch=c_owner["epoch"], presented_l5=envelope["l5"],
                               pair_sha256=sha(json.dumps(envelope["pair"], sort_keys=True,
                                                          separators=(",", ":"),
                                                          ensure_ascii=True).encode("utf-8")))
    after = case["journal_after_c_mismatch"]
    encoded = write_jsonl(after, list(before_events) + [forged])
    case["c_mismatch_request"]["after"].update(
        exists=True, raw_hex=encoded.hex(), size=len(encoded), sha256=sha(encoded))
    require_mutation_rejected(mismatch, "mismatched-world-append")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    args = parser.parse_args()
    path = args.raw.resolve()
    raw = json.loads(path.read_text())
    need(raw.get("schema") == "ases4-native-acceptance-races-v1", "raw schema mismatch")
    need(raw.get("status") == "PASS", "probe did not complete successfully")
    verify_sources(raw.get("sources", {}))
    cases = raw.get("cases", {})
    need(set(cases) == {"duplicate_acceptance", "producer_overlap"}, "expected both isolated histories")
    check_duplicate_acceptance(cases["duplicate_acceptance"])
    check_producer_overlap(cases["producer_overlap"])
    altered_controls(raw)
    print(json.dumps({"status": "PASS", "histories": 2, "altered_evidence_controls_rejected": 2,
                      "source_count": len(raw["sources"]), "raw_sha256": sha(path.read_bytes()),
                      "frozen_parent": FROZEN}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise
