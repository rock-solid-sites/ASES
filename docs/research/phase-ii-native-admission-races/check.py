#!/usr/bin/env python3
"""Focused raw-evidence checks for native seal versus F4 append histories."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FROZEN = "f7b16ddbf34034ce1a0967c37cd92d5869f7e399"
ESSENTIAL_PINNED = {
    "docs/research/phase-i-f1-recovery-repair/repaired_service.py",
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
CURRENT_PROBE = "docs/research/phase-ii-native-admission-races/probe.py"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest_record(name: str, value: dict) -> bytes:
    raw = bytes.fromhex(value["raw_hex"])
    need(len(raw) == value.get("size"), f"{name}: size mismatch")
    need(sha(raw) == value.get("sha256"), f"{name}: SHA-256 mismatch")
    return raw


def frozen_sources(sources: dict) -> None:
    need(isinstance(sources, dict) and sources, "source manifest missing")
    found: set[str] = set()
    rows = []
    for key, value in sources.items():
        if isinstance(value, str):
            path, expected = key, value
        else:
            need(isinstance(value, dict), f"invalid source record: {key}")
            path, expected = value.get("path"), value.get("sha256")
        need(isinstance(path, str) and isinstance(expected, str), f"incomplete source record: {key}")
        source_path = Path(path)
        if source_path.is_absolute():
            source_path = source_path.resolve().relative_to(REPO)
        relative = source_path.as_posix()
        found.add(relative)
        rows.append((relative, expected))
    need(ESSENTIAL_PINNED <= found, "source manifest omits essential frozen F1/F3/F4 inputs")
    need(CURRENT_PROBE in found, "source manifest omits the actual native race probe")
    for path, expected in rows:
        if path == CURRENT_PROBE:
            actual = (REPO / path).read_bytes()
        else:
            actual = subprocess.run(["git", "show", f"{FROZEN}:{path}"], cwd=REPO,
                                     check=True, stdout=subprocess.PIPE).stdout
        need(sha(actual) == expected, f"source differs from frozen parent/current probe: {path}")


def selected_direct(name: str, snap: dict) -> dict:
    current = bytes.fromhex(snap["current_raw_hex"])
    selector = current.decode("utf-8").strip()
    need(selector == snap.get("selector"), f"{name}: CURRENT selection mismatch")
    raw = bytes.fromhex(snap["record_raw_hex"])
    need(sha(raw) == snap.get("record_sha256"), f"{name}: selected record digest mismatch")
    state = json.loads(raw)
    need(state == snap.get("state"), f"{name}: selected record differs from parsed state")
    need(state.get("native_owner") == snap.get("native_owner"), f"{name}: native owner is not selected state")
    files = snap.get("record_files", {})
    current_file = files.get("CURRENT") or files.get("protected/CURRENT")
    if current_file is not None:
        need(digest_record(name + "/CURRENT", current_file) == current,
             f"{name}: tree CURRENT differs from direct CURRENT")
    record_file = files.get(selector) or files.get("protected/" + selector)
    need(record_file is not None, f"{name}: selected file absent from retained owner tree")
    need(digest_record(name + "/selected", record_file) == raw,
         f"{name}: selected file differs from direct bytes")
    return state


def parsed_sqlite(name: str, image: dict) -> dict:
    raw = bytes.fromhex(image["snapshot_raw_hex"])
    need(len(raw) == image.get("snapshot_size"), f"{name}: SQLite image size mismatch")
    need(sha(raw) == image.get("snapshot_sha256"), f"{name}: SQLite image digest mismatch")
    need(image.get("integrity_check") == "ok", f"{name}: SQLite integrity check failed")
    return image["queries"]


def f1_evidence(name: str, image: dict) -> tuple[dict, list[dict]]:
    queries = parsed_sqlite(name, image)
    kernel = queries.get("kernel", [])
    selected_rows = queries.get("selected", [])
    retained_rows = queries.get("retained", [])
    need(len(kernel) == 1 and len(selected_rows) == 1, f"{name}: F1 selected rows absent or ambiguous")
    view = json.loads(kernel[0][4])
    selected = json.loads(selected_rows[0][1])
    retained = [json.loads(row[0]) for row in retained_rows]
    pair = {"accepted_content": view["content"], "required": selected["required"]}
    need(selected in retained, f"{name}: selected F1 record is not retained")
    return pair, retained


def l6_evidence(name: str, snap: dict) -> tuple[list, dict]:
    queries = parsed_sqlite(name, snap["l6_sqlite"])
    unit_rows = queries.get("unit", [])
    deps = queries.get("dependencies", [])
    need(len(unit_rows) == 1, f"{name}: native L6 unit row absent")
    files = snap.get("l6_files")
    need(isinstance(files, dict), f"{name}: owned L6 material bytes absent")
    for filename, value in files.items():
        raw = bytes.fromhex(value["raw_hex"])
        need(len(raw) == value.get("size") and sha(raw) == value.get("sha256"),
             f"{name}: owned material hash mismatch for {filename}")
    live_dependencies = {row[0]: row for row in deps if row[4] == 0}
    need(set(files) == set(live_dependencies), f"{name}: L6 live inventory differs from owned bytes")
    for filename, value in files.items():
        row = live_dependencies[filename]
        need(value["sha256"] == row[2] and value["size"] == row[3],
             f"{name}: L6 row does not bind owned bytes for {filename}")
    return unit_rows[0], files


def permissions(state: dict, unit: str) -> set[str]:
    units = state["work_units"]
    current = unit
    seen: set[str] = set()
    grants = {"read", "write"}
    while current is not None:
        need(current in units and current not in seen, "invalid live L5 ancestry")
        seen.add(current)
        row = units[current]
        grants &= set(row["grants"])
        if "latent_ceiling" in row:
            grants &= set(row["latent_ceiling"])
        current = row["parent"]
    return grants


def assert_owner_stable(name: str, before: dict, after: dict) -> None:
    left = selected_direct(name + " before", before)
    right = selected_direct(name + " after", after)
    need(before["current_raw_hex"] == after["current_raw_hex"]
         and before["record_raw_hex"] == after["record_raw_hex"]
         and left == right, f"{name}: refused contender changed owner CURRENT selection")
    need(before["f1_sqlite"]["snapshot_sha256"] == after["f1_sqlite"]["snapshot_sha256"],
         f"{name}: refused contender changed F1 evidence")
    need(before["l6_sqlite"]["snapshot_sha256"] == after["l6_sqlite"]["snapshot_sha256"]
         and before["l6_files"] == after["l6_files"],
         f"{name}: refused contender changed L6 catalog/material")


def journal(name: str, value: dict) -> tuple[bytes, list[dict]]:
    raw = digest_record(name, value)
    events = [json.loads(line) for line in raw.splitlines() if line]
    need(events == value.get("events"), f"{name}: decoded journal differs from captured event list")
    return raw, events


def effects(events: list[dict]) -> list[dict]:
    return [item for item in events if item.get("event") == "effect_accepted"]


def response_body(value: dict) -> dict:
    return value.get("body", {}) if isinstance(value, dict) else {}


def owner_reply(frame: dict) -> dict:
    return frame.get("reply", frame)


def check_case(case: dict, label: str) -> None:
    need(case.get("label") == label.replace("_", "-"), f"{label}: case label")
    need(case.get("authority_version") == 1, f"{label}: expected current outer F4 authority version")
    initial = selected_direct(label + " initial", case["initial_owner_direct"])
    gate = case["append_attempt"]["gate"]
    expected_gate = "guarded" if label == "append_first" else "before-admission"
    need(gate.get("event") == "GATE" and gate.get("stage") == expected_gate,
         f"{label}: actual native F4 gate missing")
    request_id = case["initial_envelope"]["request_id"]
    need(case["append_attempt"]["envelope"] == case["initial_envelope"],
         f"{label}: gated request differs from current initial envelope")
    request = case["append_attempt"]["request"]
    need(request.get("request_id") == request_id
         and json.loads(request["payload"]) == case["initial_envelope"],
         f"{label}: F4 request frame does not bind envelope")
    initial_pair, retained = f1_evidence(label + " initial F1", case["initial_owner_direct"]["f1_sqlite"])
    owner = initial["native_owner"]
    reg = next((x for x in owner.get("registrations", []) if x.get("id") == owner.get("selected")), None)
    need(reg is not None and reg.get("status") == "live" and reg.get("pair") == initial_pair,
         f"{label}: current F3 registration does not match actual selected F1 pair")
    need(reg["pair"] in [dict(accepted_content=x.get("accepted_content"), required=x.get("required"))
                          for x in retained], f"{label}: selected F1 pair is not retained")
    need(case["initial_envelope"].get("import_id") == reg.get("id"),
         f"{label}: request does not bind selected native registration")
    need(case["initial_envelope"].get("pair") == initial_pair
         and case["initial_envelope"].get("epoch") == owner.get("epoch"),
         f"{label}: initial request does not bind current selected F1 pair and owner epoch")
    initial_generation = case["initial_owner_snapshot"].get("generation", {})
    need(initial_generation.get("selector") == case["initial_owner_direct"]["selector"]
         and initial_generation.get("sha256") == case["initial_owner_direct"]["record_sha256"],
         f"{label}: initial F4 envelope snapshot differs from actual selected CURRENT record")
    need(permissions(initial, "D") == {"read", "write"}
         and initial["work_units"]["D"].get("active") is True,
         f"{label}: initial D is not active and write-capable")
    unit, files = l6_evidence(label + " initial L6", case["initial_owner_direct"])
    need(unit[0] == 1 and bool(files), f"{label}: initial L6 authority/material not live")
    object_name = Path(reg["metadata"]["object"]).name
    object_bytes = bytes.fromhex(files[object_name]["raw_hex"])
    need(object_bytes.decode("utf-8") == initial_pair["accepted_content"]
         and sha(object_bytes) == reg["metadata"]["sha256"]
         and len(object_bytes) == reg["metadata"]["size"],
         f"{label}: selected accepted content is not backed by the actual owned bytes")

    at_gate = selected_direct(label + " at gate", case["owner_at_gate"])
    after_contender = selected_direct(label + " after contender", case["owner_after_contender"])
    if label == "append_first":
        assert_owner_stable(label + " refused seal", case["owner_at_gate"], case["owner_after_contender"])
    contender_reply = owner_reply(case["contender"]["reply"])
    need(case["contender"]["process"].get("pid"), f"{label}: separate owner contender process absent")
    if label == "append_first":
        need(contender_reply.get("result") == "DENY", f"{label}: competing seal was not refused")
        need("busy" in str(contender_reply).lower() or "locked" in str(contender_reply).lower(),
             f"{label}: seal refusal does not expose busy/lock outcome")
        need(contender_reply.get("owner_selection_changed") is False
             and contender_reply.get("durable_phase_changed") is False,
             f"{label}: contender did not report unchanged selection/durable phase")
    else:
        need(contender_reply.get("result") == "COMMITTED",
             f"{label}: seal-first owner contender did not commit revocation")
        need(case["owner_at_gate"]["current_raw_hex"] != case["owner_after_contender"]["current_raw_hex"]
             and after_contender["native_owner"].get("epoch", 0) > at_gate["native_owner"].get("epoch", 0),
             f"{label}: seal-first contender did not advance selected owner authority")
        need(after_contender["current_ingress"] is None
             and all(not row.get("active") and row.get("sealed")
                     for row in after_contender["work_units"].values()),
             f"{label}: successful contender did not seal native ingress")
        need(case["owner_at_gate"]["l6_files"] == case["owner_after_contender"]["l6_files"]
             and case["owner_at_gate"]["f1_sqlite"]["snapshot_sha256"]
             == case["owner_after_contender"]["f1_sqlite"]["snapshot_sha256"],
             f"{label}: seal-first contender changed F1 evidence or owned material")

    at_gate_effects = at_gate["native_owner"].get("effects", {})
    if label == "append_first":
        reserved = at_gate_effects.get(request_id)
        need(reserved is not None and reserved.get("status") in ("reserved", "local"),
             "append-first: owner did not reserve effect before guarded gate")
    else:
        need(request_id not in at_gate_effects,
             "seal-first: before-admission gate already reserved the request")
    gate_journal, gate_events = journal(label + " journal at gate", case["journal_at_gate"])
    contender_journal, contender_events = journal(label + " journal after contender", case["journal_after_contender"])
    need(gate_journal == contender_journal and gate_events == contender_events,
         f"{label}: refused seal contender changed the F4 journal")

    after_seal = selected_direct(label + " after seal", case["owner_after_seal"])
    need(after_seal["native_owner"].get("lifecycle") == "live"
         and after_seal["current_ingress"] is None
         and all(not row.get("active") and row.get("sealed") for row in after_seal["work_units"].values()),
         f"{label}: owner seal did not revoke active ingress")
    seal_frame = case["seal_retry"] if label == "append_first" else case["seal"]
    need(owner_reply(seal_frame).get("result") == "COMMITTED",
         f"{label}: actual owner seal did not commit")
    if label == "append_first":
        need(after_seal["native_owner"].get("effects", {}).get(request_id, {}).get("status") == "published",
             "append-first: effect was not published before later seal")
    else:
        need(request_id not in after_seal["native_owner"].get("effects", {}),
             "seal-first: seal unexpectedly reserved the request")

    append_reply = case["append_reply"]["response"]
    response = response_body(append_reply)
    moved_name = "move"
    activated = case["activate"]
    need(append_reply.get("status") == (201 if label == "append_first" else 409),
         f"{label}: F4 append response status mismatch")
    if label == "append_first":
        need(response.get("owner_effect", {}).get("status") == "published",
             "append-first: successful append lacks owner publication result")
    else:
        need(response.get("outcome") == "admission-denied"
             and response.get("local_control_committed") is False,
             "seal-first: old envelope was not denied before F4 append")
        need(response.get("reason") == "stale-native-epoch",
             "seal-first: stale envelope did not fail against the newly selected native epoch")
        need(request_id not in after_seal["native_owner"].get("effects", {}),
             "seal-first: denied envelope left an owner effect reservation")
    need(owner_reply(case[moved_name]).get("result") == "COMMITTED"
         and owner_reply(activated).get("result") == "COMMITTED",
         f"{label}: actual move to Q and activation did not commit")
    moved = selected_direct(label + " after current denial", case["owner_after_current_denial"])
    need(moved["work_units"].get("C", {}).get("parent") == "Q"
         and moved["work_units"].get("D", {}).get("parent") == "C",
         f"{label}: current selected native state does not show actual C/D move to Q")
    need(permissions(moved, "D") == {"read"}, f"{label}: moved D path is not read-only")
    moved_generation = case["post_move_owner_snapshot"].get("generation", {})
    need(moved_generation.get("selector") == case["owner_after_current_denial"]["selector"]
         and moved_generation.get("sha256") == case["owner_after_current_denial"]["record_sha256"],
         f"{label}: fresh post-move envelope was not built from the current selected record")
    need(case["current_envelope"].get("l5") == moved_generation,
         f"{label}: post-move new-ID request does not carry current L5 selector/hash")
    denied_call = case["denied_current"]["result"]
    denied = denied_call["response"]
    denied_body = response_body(denied)
    need(denied.get("status") == 409 and denied_body.get("outcome") == "admission-denied"
         and denied_body.get("local_control_committed") is False,
         f"{label}: current-envelope post-move request was not refused by native path")
    need(denied_body.get("reason") in ("native-current-path-denied", "native-read-only-path"),
         f"{label}: denial did not identify current native path guard")
    need(denied_call["before"].get("sha256") == denied_call["after"].get("sha256"),
         f"{label}: current-envelope denial changed the journal")
    need(after_seal["native_owner"].get("effects", {})
         == moved["native_owner"].get("effects", {}),
         f"{label}: post-move denial changed native effect history")
    if label == "seal_first":
        fresh_call = case["denied_fresh_sealed"]["result"]
        fresh = fresh_call["response"]
        need(fresh.get("status") == 409
             and response_body(fresh).get("outcome") == "admission-denied"
             and response_body(fresh).get("local_control_committed") is False,
             "seal-first: freshly selected sealed envelope was not denied")
        need(fresh_call["before"].get("sha256") == fresh_call["after"].get("sha256"),
             "seal-first: fresh sealed denial changed the journal")

    current_journal_key = "journal_after_append" if label == "append_first" else "journal_after_denial"
    final_raw, final_events = journal(label + " final journal", case["journal_final"])
    _, after_contender_events = journal(label + " contender journal", case["journal_after_contender"])
    _, settled_events = journal(label + " settled journal", case[current_journal_key])
    effect_rows = effects(final_events)
    expected_count = 1 if label == "append_first" else 0
    need(len(effect_rows) == expected_count, f"{label}: expected {expected_count} accepted journal effects")
    need(final_events == settled_events, f"{label}: final journal contains a later unaccounted mutation")
    need(final_events[:len(after_contender_events)] == after_contender_events,
         f"{label}: journal is not append-only from refused contender cut")
    if label == "append_first":
        row = effect_rows[0]
        envelope = json.loads(row["payload"])
        admission = row.get("admission", {})
        need(row.get("request_id") == request_id and envelope == case["initial_envelope"],
             "append-first: actual journal row does not bind exact successful envelope")
        need(admission.get("profile") == "native-f3-owner-v1"
             and admission.get("native_registration") is True
             and admission.get("domain_id") == owner.get("domain_id")
             and admission.get("epoch") == case["initial_envelope"].get("epoch")
             and admission.get("presented_l5") == case["initial_envelope"].get("l5"),
             "append-first: F4 event admission facts do not bind native owner/envelope")
        retry = case["historical_exact_retry"]
        retry_response = retry["response"]
        retry_body = response_body(retry_response)
        retry_request = retry["request"]
        need(retry.get("path") == "/submit" and retry_request.get("authority_version") == 1
             and retry_request.get("request_id") == request_id
             and json.loads(retry_request["payload"]) == case["initial_envelope"],
             "append-first: post-revocation retry did not resubmit the exact original envelope at current F4 v1")
        need(retry_response.get("status") == 200 and retry_body.get("outcome") == "already-accepted"
             and retry_body.get("event_seq") == row.get("seq")
             and retry_body.get("owner_effect", {}).get("status") == "published"
             and retry_body.get("owner_effect", {}).get("replayed") is True,
             "append-first: historical exact-ID retry was not a published observation of the original effect")
        need(retry_body.get("verified_journal_sha256") == sha(final_raw),
             "append-first: historical retry response did not verify the original journal cut")
        for edge in ("before", "after"):
            retry_raw = digest_record("historical retry " + edge, retry[edge])
            need(retry_raw == final_raw, f"append-first: historical retry {edge} changed journal bytes")
        for edge in ("historical_exact_retry_before", "historical_exact_retry_after"):
            cut = case[edge]
            cut_raw, _ = journal("historical retry cut " + edge, cut["journal"])
            need(cut_raw == final_raw, f"append-first: {edge} journal differs from original accepted cut")
            sink_cut = response_body(cut["sink_status"]).get("actual_cut", {})
            witness_cut = response_body(cut["witness_status"]).get("current", {})
            need(sink_cut.get("journal_sha256") == sha(final_raw)
                 and witness_cut.get("journal_sha256") == sha(final_raw),
                 f"append-first: {edge} sink/witness did not retain the original published cut")
        historical = case["historical_status"]
        body = response_body(historical)
        historical_row = next((x for x in body.get("effects", []) if x.get("request_id") == request_id), None)
        need(historical.get("status") == 200
             and body.get("actual_cut", {}).get("journal_sha256") == sha(final_raw)
             and historical_row == row
             and body.get("request_index", {}).get(request_id) == row.get("seq"),
             "append-first: historical status does not identify the one retained journal effect")
        witness_status = case["f4_final_snapshot"].get("witness_status", {})
        witness_body = response_body(witness_status)
        need(witness_status.get("status") == 200
             and witness_body.get("current", {}).get("journal_sha256") == sha(final_raw),
             "append-first: actual witness publication does not identify final journal cut")
        need(body.get("actual_cut", {}).get("authority", {}).get("active") is True
             and body["actual_cut"]["authority"].get("authority_version") == 1,
             "append-first: outer F4 authority was not current at historical lookup")
        need(after_seal["native_owner"]["effects"][request_id].get("seq") == row.get("seq"),
             "append-first: owner published sequence differs from actual journal row")
        need(body.get("events") == final_events,
             "append-first: retained historical result events differ from actual final journal")
    else:
        need(case["journal_after_denial"]["sha256"] == case["journal_at_gate"]["sha256"],
             "seal-first: stale request changed local journal")

    sink_status = case["f4_final_snapshot"].get("sink_status", {})
    final_authority = response_body(sink_status).get("actual_cut", {}).get("authority", {})
    need(sink_status.get("status") == 200 and final_authority.get("active") is True
         and final_authority.get("authority_version") == 1,
         f"{label}: outer F4 authority was not current after native denial")

    # The owner still retains its accepted bytes and F1 observations through revocation/move.
    retained_snapshots = ["owner_at_gate", "owner_after_contender", "owner_after_seal",
                          "owner_after_current_denial"]
    if label == "append_first":
        retained_snapshots.append("owner_after_append")
    else:
        retained_snapshots.append("owner_after_denial")
    for key in retained_snapshots:
        snap = case[key]
        state = selected_direct(label + " " + key, snap)
        pair, retained_now = f1_evidence(label + " " + key + " F1", snap["f1_sqlite"])
        unit_now, files_now = l6_evidence(label + " " + key + " L6", snap)
        need(pair == initial_pair and retained_now == retained,
             f"{label}: F1 selected/retained evidence changed at {key}")
        need(unit_now[0] == 1 and files_now == files,
             f"{label}: owned material changed at {key}")
        need(state["native_owner"].get("lifecycle") == "live",
             f"{label}: source domain unexpectedly ceased to be live")


def expect_reject(label: str, raw: dict) -> None:
    try:
        check_case(raw["cases"][label], label)
    except (ValueError, KeyError, TypeError, AssertionError):
        return
    raise ValueError(f"altered-evidence control was accepted: {label}")


def altered_controls(raw: dict) -> None:
    # Control A: manufacture a new accepted effect after revocation. Keep its
    # raw bytes, digest, and decoded event list self-consistent.
    label = "append_first"
    mutant = copy.deepcopy(raw)
    case = mutant["cases"][label]
    final = case["journal_final"]
    events = list(final["events"])
    source = effects(events)[0]
    forged = dict(source, seq=source.get("seq", 0) + 1,
                  request_id=case["current_envelope"]["request_id"])
    payload = json.loads(source["payload"])
    payload["request_id"] = forged["request_id"]
    forged["payload"] = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    events.append(forged)
    encoded = b"".join((json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n").encode()
                      for event in events)
    final.update(raw_hex=encoded.hex(), size=len(encoded), sha256=sha(encoded), events=events)
    expect_reject(label, mutant)

    # Control B: point the refused contender snapshot at a different, real
    # historical CURRENT record and maintain byte/digest consistency.
    label = "append_first"
    mutant = copy.deepcopy(raw)
    snap = mutant["cases"][label]["owner_after_contender"]
    tree = snap["record_files"]
    current = bytes.fromhex(snap["current_raw_hex"]).decode().strip()
    entries = [key for key in tree if key.endswith("record-000001.json") or key.endswith("record-000002.json")]
    alternate = next((key.split("/")[-1] for key in entries if key.split("/")[-1] != current), None)
    need(alternate is not None, "changed-selection control lacks a second retained owner record")
    prefix = "protected/" if "protected/" + alternate in tree else ""
    alternate_record = tree[prefix + alternate]
    record_raw = bytes.fromhex(alternate_record["raw_hex"])
    current_raw = (alternate + "\n").encode()
    snap.update(selector=alternate, current_raw_hex=current_raw.hex(),
                record_raw_hex=record_raw.hex(), record_sha256=sha(record_raw),
                state=json.loads(record_raw), native_owner=json.loads(record_raw)["native_owner"])
    current_key = prefix + "CURRENT"
    tree[current_key] = {"raw_hex": current_raw.hex(), "size": len(current_raw),
                         "sha256": sha(current_raw)}
    expect_reject(label, mutant)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    args = parser.parse_args()
    path = args.raw.resolve()
    raw = json.loads(path.read_text())
    need(raw.get("schema") == "ases4-native-revocation-append-v1", "raw schema mismatch")
    need(raw.get("status") == "PASS", "probe did not complete successfully")
    frozen_sources(raw.get("sources", {}))
    cases = raw.get("cases", {})
    need(set(cases) == {"append_first", "seal_first"}, "expected exactly the two requested histories")
    check_case(cases["append_first"], "append_first")
    check_case(cases["seal_first"], "seal_first")
    altered_controls(raw)
    print(json.dumps({"status": "PASS", "histories": 2, "altered_evidence_controls_rejected": 2,
                      "raw_sha256": sha(path.read_bytes()), "frozen_parent": FROZEN}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise
