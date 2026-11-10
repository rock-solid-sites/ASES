#!/usr/bin/env python3
"""Independent raw-evidence checks for the bounded ASES-4 native probe."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def check_file_record(name: str, record: dict) -> bytes:
    value = bytes.fromhex(record["raw_hex"])
    need(len(value) == record.get("size"), f"{name}: raw size mismatch")
    need(sha(value) == record.get("sha256"), f"{name}: raw digest mismatch")
    return value


def check_f1_state(name: str, value: dict) -> None:
    need(value.get("integrity") == "ok", f"{name}: SQLite integrity")
    pair = value.get("pair")
    selected = value.get("selected")
    view = value.get("view")
    need(isinstance(pair, dict) and isinstance(selected, dict) and isinstance(view, dict),
         f"{name}: selected F1 evidence missing")
    need(pair == {"accepted_content": view.get("content"), "required": selected.get("required")},
         f"{name}: selected F1 pair not reconstructed from native rows")
    retained = value.get("retained")
    need(isinstance(retained, list), f"{name}: retained F1 observations missing")
    decoded = [json.loads(item) if isinstance(item, str) else item for item in retained]
    need(selected in decoded, f"{name}: selected F1 observation is not retained")


def frame_reply(frame: dict) -> dict:
    return frame.get("reply", frame)


def frame_snapshot(frame: dict) -> dict:
    return frame.get("snapshot") or frame_reply(frame).get("snapshot") or {}


def owner_state(snapshot: dict) -> dict:
    return snapshot.get("state", {})


def owner_record(snapshot: dict) -> dict:
    return owner_state(snapshot).get("native_owner", {})


def stable_inventory(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "observation_ns"}


def retained_pairs(f1_state: dict) -> set[str]:
    out = set()
    for item in f1_state.get("retained", []):
        observation = json.loads(item) if isinstance(item, str) else item
        pair = {"accepted_content": observation.get("accepted_content"),
                "required": observation.get("required")}
        out.add(json.dumps(pair, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return out


def derive_permissions(state: dict, unit: str) -> set[str]:
    units = state["work_units"]
    result = {"read", "write"}
    seen = set()
    current = unit
    while current is not None:
        need(current in units and current not in seen, "invalid live L5 ancestry")
        seen.add(current)
        value = units[current]
        result &= set(value["grants"])
        if "latent_ceiling" in value:
            result &= set(value["latent_ceiling"])
        current = value["parent"]
    return result


def selected_state_from_tree(name: str, tree: dict) -> tuple[str, dict]:
    current = check_file_record(name + "/protected/CURRENT", tree["protected/CURRENT"]).decode().strip()
    record = tree.get("protected/" + current)
    need(record is not None, name + ": selected CURRENT record absent")
    state = json.loads(check_file_record(name + "/protected/" + current, record))
    need(type(state.get("schema")) is int and state["schema"] == 1,
         name + ": selected native L5 schema")
    return current, state


def check_material_files(root: Path, inventory: dict, name: str) -> None:
    for filename, record in inventory.get("files", {}).items():
        content = check_file_record(name + "/objects/" + filename, record)
        path = root / "protected" / "objects" / filename
        need(path.is_file() and not path.is_symlink(), name + ": inventory object missing")
        need(path.read_bytes() == content, name + ": raw object differs from actual object")


def check_native_no_f4(case: dict, raw: dict) -> None:
    initial = case["initial_view"]
    initial_owner = owner_record(initial)
    need(initial_owner.get("registrations") == [] and initial_owner.get("selected") is None,
         "owner bootstrap imported an accepted-object fixture")
    need(initial_owner.get("children", {}).get("D") == "live", "issuer did not create native D")
    need(initial.get("inventory", {}).get("dependencies") == [], "bootstrap inventory not empty")

    first = frame_reply(case["accept_first"])
    duplicate = frame_reply(case["accept_duplicate"])
    changed = frame_reply(case["accept_changed_world"])
    first_reg, changed_reg = first.get("registration"), changed.get("registration")
    need(first.get("result") == "COMMITTED" and first.get("duplicate") is False,
         "first native F3 acceptance did not publish a new registration")
    need(duplicate.get("result") == "COMMITTED" and duplicate.get("duplicate") is True,
         "exact F1-pair retry was not a duplicate observation")
    need(changed.get("result") == "COMMITTED" and changed.get("duplicate") is False,
         "same-byte new-world F1 pair did not receive a distinct registration")
    need(isinstance(first_reg, dict) and isinstance(changed_reg, dict), "native registration frames missing")
    need(first_reg["id"] != changed_reg["id"], "changed F1 world reused registration identity")

    first_pair = raw["f1_after_accept"]["pair"]
    changed_pair = case["f1_after_world_change"]["pair"]
    check_f1_state("F1 after first accept", raw["f1_after_accept"])
    check_f1_state("F1 same-byte changed world", case["f1_after_world_change"])
    need(first_reg.get("pair") == first_pair, "F3 first registration does not match actual F1 selected pair")
    need(changed_reg.get("pair") == changed_pair, "F3 second registration does not match actual F1 selected pair")
    need(first_pair["accepted_content"] == changed_pair["accepted_content"]
         and first_pair["required"] != changed_pair["required"],
         "same-byte/different-world F1 discriminator missing")
    pairs = retained_pairs(case["f1_after_remove"])
    for value in (first_pair, changed_pair):
        need(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) in pairs,
             "owner accepted a pair absent from retained native F1 observations")

    first_snapshot = frame_snapshot(case["accept_first"])
    duplicate_snapshot = frame_snapshot(case["accept_duplicate"])
    need(first_snapshot.get("selector") == duplicate_snapshot.get("selector"),
         "duplicate acceptance advanced CURRENT")
    need(stable_inventory(first_snapshot.get("inventory", {}))
         == stable_inventory(duplicate_snapshot.get("inventory", {})),
         "duplicate acceptance changed native material inventory")
    first_owner = owner_record(first_snapshot)
    duplicate_owner = owner_record(duplicate_snapshot)
    need(first_owner.get("epoch") == duplicate_owner.get("epoch"), "duplicate acceptance changed native epoch")
    changed_snapshot = frame_snapshot(case["accept_changed_world"])
    need(owner_record(changed_snapshot).get("epoch", -1) > first_owner.get("epoch", -1),
         "changed-world acceptance failed to advance epoch")

    move_snapshot = frame_snapshot(case["move"])
    moved_state = owner_state(move_snapshot)
    units = moved_state.get("work_units", {})
    need(units.get("C", {}).get("parent") == "Q" and units.get("D", {}).get("parent") == "C",
         "actual L5 manager did not move complete C/D subtree")
    need(derive_permissions(moved_state, "D") == {"read"},
         "post-move full D ancestry does not derive read-only authority")
    need(frame_reply(case["move"]).get("result") == "COMMITTED",
         "native L5 manager did not commit the move")
    need(frame_reply(case["activate"]).get("result") == "COMMITTED",
         "native L5 activation did not commit")

    active_block = frame_reply(case["remove_blocked_active_domain"])
    child_block = frame_reply(case["remove_blocked_live_child"])
    material_block = frame_reply(case["remove_blocked_live_material"])
    need(active_block.get("result") == "DENY", "removal while active did not refuse")
    need(child_block.get("result") == "DENY" and child_block.get("reason") == "native-child-remains",
         "sealed removal did not refuse the live D child")
    need(material_block.get("result") == "DENY" and material_block.get("reason") == "native-content-remains",
         "removal after D disposition did not refuse live accepted material")
    before_child = case["seal_for_disposition"]["reply"]["snapshot"]
    after_child = case["snapshot_after_child_remove_block"]
    need(before_child.get("selector") == after_child.get("selector"),
         "live-child removal refusal changed owner CURRENT")
    before_material = frame_snapshot(case["dispose_child"])
    after_material = case["snapshot_after_material_remove_block"]
    need(before_material.get("selector") == after_material.get("selector"),
         "live-content removal refusal changed owner CURRENT")

    dispositions = [frame_reply(value) for value in case["dispose_content"]]
    need(len(dispositions) == 2 and all(value.get("result") == "COMMITTED" for value in dispositions),
         "explicit native content dispositions missing")
    removed = frame_reply(case["remove"])
    need(removed.get("result") == "COMMITTED", "native owner removal did not complete")
    final_view = case["cold_view"]
    final_owner = owner_record(final_view)
    need(final_owner.get("lifecycle") == "removed" and final_owner.get("selected") is None,
         "cold readback does not retain logical removed state")
    final_state = owner_state(final_view)
    need("D" not in final_state.get("work_units", {}) and "C" not in final_state.get("work_units", {}),
         "disposed C/D remain in the live owner graph")
    tombstones = final_owner.get("disposed_units", {})
    need("D" in tombstones and "C" in tombstones and final_owner.get("children", {}).get("D") == "disposed",
         "native logical removal lacks actual disposed C/D tombstones")
    need(final_view.get("inventory", {}).get("live") is False
         and not final_view.get("inventory", {}).get("files")
         and final_view.get("inventory", {}).get("unknown_files") == [],
         "cold readback inventory is not physically empty")
    need(final_view.get("inventory", {}).get("objects_directory_exists") is False,
         "native data envelope directory survived removal")
    need(not final_owner.get("effects"), "no-F4 native owner unexpectedly has effect state")

    tree = case["owner_tree_final"]
    selector, final_record = selected_state_from_tree("native owner", tree)
    need(selector == final_view.get("selector") and final_record == owner_state(final_view),
         "raw native CURRENT record differs from cold owner readback")
    owner_root = Path(case["root"])
    catalog = owner_root / "protected" / "catalog.sqlite"
    need(catalog.is_file(), "native L6 catalog missing after envelope removal")
    with sqlite3.connect(catalog.resolve().as_uri() + "?mode=ro", uri=True) as db:
        unit = db.execute("SELECT live,sealed FROM unit").fetchone()
        deps = db.execute("SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name").fetchall()
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    need(unit == (0, 1) and integrity == "ok", "native L6 catalog did not retain disposed removed state")
    need(len(deps) == 2 and all(row[4] == 1 for row in deps), "native L6 dependencies not disposed")
    need(not (owner_root / "protected" / "objects").exists(), "native L6 object directory remains")


def check_native_f4(case: dict, label: str) -> None:
    if label == "native-f4-authorized-denied":
        authorized = case["authorized_call"]
        need(authorized["response"].get("status") == 201, "authorized native F4 effect not accepted")
        need(authorized["response"]["body"].get("owner_effect", {}).get("status") == "published",
             "authorized effect did not reach owner published state")
        for key in ("forged_call", "denied_call"):
            value = case[key]
            need(value["response"].get("status") == 409, key + ": expected native admission denial")
            need(value["response"]["body"].get("outcome") == "admission-denied"
                 and value["response"]["body"].get("local_control_committed") is False,
                 key + ": caller or moved path was not denied before local acceptance")
            need(value["before"].get("sha256") == value["after"].get("sha256"),
                 key + ": denial changed F4 journal bytes")
        moved_state = case["after_move_snapshot"]["state"]
        need(derive_permissions(moved_state, "D") == {"read"},
             "F4 denied request did not use actual read-only moved D path")
        tree = case["f4_tree"]
    else:
        lost = case["lost_reply_call"]
        need("transport_error" in lost["response"], "gate kill did not lose caller reply")
        gate = case["gate_and_owner_local_commit"]["frame"]
        need(gate.get("event") == "GATE" and gate.get("stage") == "before-settlement",
             "owner settlement interruption gate missing")
        pending = owner_record(case["gate_and_owner_local_commit"]["owner_after_kill"])["effects"]
        request_id = case["envelope"]["request_id"]
        need(pending.get(request_id, {}).get("status") == "local"
             and pending[request_id].get("seq") == 4,
             "owner did not retain local accepted-but-unpublished effect after kill")
        retry = case["retry"]
        need(retry["response"].get("status") == 200
             and retry["response"]["body"].get("outcome") == "already-accepted"
             and retry["response"]["body"].get("event_seq") == 4,
             "cold exact retry did not observe original accepted F4 event")
        need(retry["response"]["body"].get("owner_effect", {}).get("status") == "published",
             "cold retry failed to settle native owner publication")
        need(retry["before"].get("sha256") == retry["after"].get("sha256"),
             "cold exact retry appended a second effect")
        historical = case["historical_retry_after_move"]
        need(historical["response"].get("status") == 200
             and historical["response"]["body"].get("outcome") == "already-accepted"
             and historical["response"]["body"].get("event_seq") == 4
             and historical["response"]["body"].get("owner_effect", {}).get("replayed") is True,
             "historical retry ceased to be an exact published observation after source move")
        need(historical["before"].get("sha256") == historical["after"].get("sha256"),
             "historical retry after move appended a new local effect")
        need(case["denied_after_cold"]["before"].get("sha256")
             == case["denied_after_cold"]["after"].get("sha256"),
             "post-cold new-ID denial changed journal")
        reopened = case["post_cold_reopen"]
        need(len(reopened) == 2
             and all(item["response"].get("status") == 200 for item in reopened)
             and reopened[0]["response"]["body"].get("authority_version") == 2
             and reopened[1]["response"]["body"].get("authority_version") == 2,
             "cold managed F4 authority did not perform real replacement and activation to v2")
        need(case["denied_after_cold"]["response"].get("status") == 409
             and case["denied_after_cold"]["response"]["body"].get("reason") == "native-current-path-denied",
             "fresh post-cold request did not reach the native moved-descendant guard")
        need(case["snapshot_after_retry"]["witness_status"]["body"]["current"]["journal_sha256"]
             == case["retry"]["after"]["sha256"], "cold retry not freshly checked against published witness cut")
        disposal = case["disposition_transitions"]
        need(frame_reply(disposal["dispose_child"]).get("result") == "COMMITTED"
             and len(disposal["dispose_content"]) == 1
             and frame_reply(disposal["dispose_content"][0]).get("result") == "COMMITTED"
             and frame_reply(disposal["remove"]).get("result") == "COMMITTED",
             "F4 owner history did not explicitly dispose D/content and remove the domain")
        removed_owner = case["owner_after_disposal"]
        removed_state = owner_state(removed_owner)
        removed_record = owner_record(removed_owner)
        need(removed_record.get("lifecycle") == "removed" and removed_record.get("selected") is None
             and "D" not in removed_state.get("work_units", {})
             and "D" in removed_record.get("disposed_units", {}),
             "F4 source domain did not reach native removed state with D tombstone")
        after_disposal_retry = case["historical_retry_after_disposal"]
        need(after_disposal_retry["response"].get("status") == 200
             and after_disposal_retry["response"]["body"].get("outcome") == "already-accepted"
             and after_disposal_retry["response"]["body"].get("event_seq") == 4
             and after_disposal_retry["before"].get("sha256") == after_disposal_retry["after"].get("sha256"),
             "published historical F4 effect did not remain an exact retry after native source disposal")
        after_disposal_new = case["denied_after_disposal"]
        need(after_disposal_new["response"].get("status") == 409
             and after_disposal_new["response"]["body"].get("reason") == "native-domain-not-live"
             and after_disposal_new["before"].get("sha256") == after_disposal_new["after"].get("sha256"),
             "new ID at current F4 v2 against removed source missed native lifecycle denial")
        tree = case["f4_tree"]
    journal_record = tree.get("sink-effects.jsonl")
    need(journal_record is not None, label + ": raw F4 journal absent")
    journal = check_file_record(label + "/sink-effects.jsonl", journal_record)
    events = [json.loads(line) for line in journal.splitlines() if line]
    effects = [event for event in events if event.get("event") == "effect_accepted"]
    need(len(effects) == 1, label + ": expected exactly one native F4 effect row")
    effect = effects[0]
    envelope = json.loads(effect["payload"])
    need(envelope["request_id"] == effect["request_id"], label + ": effect envelope identity mismatch")
    need(effect.get("admission", {}).get("profile") == "native-f3-owner-v1"
         and effect["admission"].get("native_registration") is True,
         label + ": journal lacks actual native owner admission evidence")
    need(effect["admission"].get("import_id") == envelope.get("import_id")
         and effect["admission"].get("epoch") == envelope.get("epoch")
         and effect["admission"].get("presented_l5") == envelope.get("l5"),
         label + ": F4 append certificate does not bind exact native envelope")


def verify_live_storage(raw: dict, case: dict, snapshot: dict, label: str) -> None:
    root = Path(case.get("root", case.get("setup", {}).get("owner_root", "")))
    need(str(root) not in ("", "."), label + ": native owner root missing")
    owner = owner_record(snapshot)
    f1_path = Path(owner["source"]["db"])
    need(f1_path.is_file(), label + ": actual F1 DB missing")
    with sqlite3.connect(f1_path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        version, view_raw = db.execute("SELECT version,view FROM kernel WHERE id=1").fetchone()
        selected_raw = db.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()[0]
        retained_raw = [item[0] for item in db.execute("SELECT record FROM retained_observations ORDER BY record")]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    expected_f1 = case["f1_after_remove"] if label == "native-no-f4" else case["f1_after"]
    need(integrity == "ok" and json.loads(view_raw) == expected_f1["view"]
         and json.loads(selected_raw) == expected_f1["selected"]
         and retained_raw == expected_f1["retained"], label + ": actual F1 selected/retained evidence differs")
    need([f1_path.stat().st_dev, f1_path.stat().st_ino] == owner["source"]["identity"],
         label + ": protected F1 source identity changed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--mutant", choices=("forged-world", "missing-child", "removed-survivor"))
    args = parser.parse_args()
    raw_path = args.raw.resolve()
    raw = json.loads(raw_path.read_text())
    if args.mutant:
        if args.mutant == "forged-world":
            raw["cases"]["native-no-f4"]["accept_changed_world"]["reply"]["registration"]["pair"]["required"]["project"] = "forged-world"
        elif args.mutant == "missing-child":
            raw["cases"]["native-no-f4"]["cold_view"]["state"]["native_owner"].setdefault("disposed_units", {}).pop("D", None)
            raw["cases"]["native-no-f4"]["cold_view"]["state"]["work_units"]["D"] = dict(id="D", parent="C")
        else:
            inventory = raw["cases"]["native-no-f4"]["cold_view"]["inventory"]
            inventory["live"] = True
            inventory["files"]["ghost"] = dict(raw_hex="00", sha256=sha(b"\x00"), size=1)
    try:
        result = validate(raw, raw_path)
    except (AssertionError, KeyError, OSError, TypeError, ValueError) as error:
        if args.mutant:
            print(json.dumps({"status": "MUTANT_REJECTED", "mutant": args.mutant,
                              "reason": str(error)}, sort_keys=True))
            return 0
        raise
    if args.mutant:
        raise ValueError("altered evidence control was not rejected: " + args.mutant)
    print(json.dumps(result, sort_keys=True))
    return 0


def validate(raw: dict, raw_path: Path) -> dict:
    need(raw.get("schema") == "ases4-native-owner-probe-v1", "raw schema")
    need(raw.get("status") == "PASS", "native probe did not pass")
    sources = raw.get("sources")
    need(isinstance(sources, dict) and sources, "source manifest missing")
    for name, source in sources.items():
        path = Path(source["path"])
        if not path.is_absolute():
            path = REPO / path
        need(path.is_file(), f"source missing: {name}")
        need(sha(path.read_bytes()) == source.get("sha256"), f"source changed: {name}")
    need(isinstance(raw.get("processes"), list), "process evidence missing")
    for process in raw["processes"]:
        need(isinstance(process.get("pid"), int), "process PID missing")
        need(isinstance(process.get("frames"), list), "process frames missing")
        if "exit" in process:
            need(isinstance(process.get("exit_ns"), int), "process exit timestamp missing")
    cases = raw.get("cases")
    need(isinstance(cases, dict) and cases, "native cases missing")
    if "f1_before_owner" in raw:
        check_f1_state("F1 pre-owner", raw["f1_before_owner"])
    if "f1_after_accept" in raw:
        check_f1_state("F1 accepted", raw["f1_after_accept"])
    if "native_f1_accept" in raw:
        need(raw["native_f1_accept"]["response"]["response"].get("outcome") == "commit",
             "native F1 accept did not commit")
        need(raw["f1_after_accept"]["pair"]["accepted_content"] !=
             raw["f1_before_owner"]["pair"]["accepted_content"],
             "test F1 accept did not advance the selected accepted content")
    if "native-no-f4" in cases:
        case = cases["native-no-f4"]
        check_native_no_f4(case, raw)
        verify_live_storage(raw, case, case["cold_view"], "native-no-f4")
        if "f1_after_world_change" in case:
            check_f1_state("F1 same-byte changed-world", case["f1_after_world_change"])
            before = raw["f1_after_accept"]["pair"]
            after = case["f1_after_world_change"]["pair"]
            need(before["accepted_content"] == after["accepted_content"],
                 "same-byte world control changed accepted bytes")
            need(before["required"] != after["required"],
                 "same-byte world control did not change opaque F1 world")
        for key in ("owner_tree_final", "owner_tree_after_close"):
            if key not in case:
                continue
            tree = case[key]
            for relative, record in tree.items():
                check_file_record(relative, record)
            current_record = tree.get("protected/CURRENT")
            if current_record:
                selector = check_file_record("protected/CURRENT", current_record).decode().strip()
                selected = tree.get(f"protected/{selector}")
                need(selected is not None, "CURRENT target missing from raw owner tree")
                selected_bytes = check_file_record(f"protected/{selector}", selected)
                state = json.loads(selected_bytes)
                need(type(state.get("schema")) is int and state["schema"] == 1,
                     "selected native L5 record schema")
    if "native-f4-authorized-denied" in cases:
        case = cases["native-f4-authorized-denied"]
        check_native_f4(case, "native-f4-authorized-denied")
        verify_live_storage(raw, case, case["owner_after_denial"], "native-f4-authorized-denied")
    if "native-f4-receipt-cold" in cases:
        case = cases["native-f4-receipt-cold"]
        check_native_f4(case, "native-f4-receipt-cold")
        verify_live_storage(raw, case, case["moved_snapshot"], "native-f4-receipt-cold")
    result = {"status": "PASS", "case_count": len(cases), "source_count": len(sources),
              "raw_sha256": sha(raw_path.read_bytes())}
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise
