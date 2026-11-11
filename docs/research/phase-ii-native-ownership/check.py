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
    forged_attempt = frame_reply(case["caller_pair_acceptance_attempt"])
    forged_view = case["view_after_forged_acceptance"]
    need(forged_attempt.get("result") == "DENY"
         and forged_view.get("selector") == initial.get("selector")
         and stable_inventory(forged_view.get("inventory", {}))
         == stable_inventory(initial.get("inventory", {})),
         "caller-supplied pair changed native acceptance/material before actual F1 reread")

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
        for key, reason in (("stale_epoch_call", "stale-native-epoch"),
                            ("stale_selector_call", "stale-native-selector")):
            value = case[key]
            need(value["response"].get("status") == 409
                 and value["response"].get("body", {}).get("outcome") == "admission-denied"
                 and value["response"]["body"].get("reason") == reason
                 and value["response"]["body"].get("local_control_committed") is False,
                 key + ": native F4 did not enforce exact stale epoch/selector reason")
            need(value["before"].get("sha256") == value["after"].get("sha256"),
                 key + ": stale native envelope changed journal")
        before_stale = case["attached_snapshot"]
        after_stale = case["owner_after_stale"]
        need(before_stale.get("selector") == after_stale.get("selector")
             and owner_record(before_stale).get("effects") == owner_record(after_stale).get("effects"),
             "stale native request changed owner selector or effect reservation")
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
    elif label == "native-f4-receipt-cold":
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
    else:
        gate = case["gate"]
        need(gate.get("event") == "GATE" and gate.get("stage") == "after-append",
             "actual after-append return-boundary gate missing")
        request_id = case["envelope"]["request_id"]
        local = owner_record(case["owner_local_at_gate"]).get("effects", {}).get(request_id)
        need(isinstance(local, dict) and local.get("status") == "local" and local.get("seq") == 4
             and isinstance(local.get("payload_sha256"), str),
             "owner did not retain the actual append sequence at return-boundary gate")
        response = case["error_response"]["response"]
        need(response.get("status") == 503
             and response.get("body", {}).get("outcome") == "native-effect-requires-reconciliation"
             and response["body"].get("local_control_committed") is True
             and response["body"].get("local_event_seq") == 4,
             "EOF at append return was not reported as committed local effect requiring reconciliation")
        ready = case["cold_ready"]
        need(ready.get("ready") is False and ready.get("reason") == "published-cut-unavailable"
             and ready.get("local_parse_complete") is True,
             "cold start accepted an append whose witness cut was not published")
        owner_final = owner_record(case["owner_final"])
        need(owner_final.get("effects", {}).get(request_id) == local,
             "cold refusal erased the local pending effect")
        local_journal = check_file_record(label + "/journal", case["f4_tree"]["sink-effects.jsonl"])
        accepted_rows = [json.loads(row) for row in local_journal.splitlines()
                         if row and json.loads(row).get("event") == "effect_accepted"]
        need(len(accepted_rows) == 1 and accepted_rows[0].get("seq") == 4
             and accepted_rows[0].get("request_id") == request_id,
             "after-append error did not preserve exactly one actual local F4 row")
        current_cut = case["final_snapshot"]["witness_status"]["body"]["current"]["journal_sha256"]
        need(current_cut != sha(local_journal),
             "witness cut unexpectedly advanced past the pre-publication failure")
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


def check_preparation_crash(case: dict, label: str, precommit: bool) -> None:
    gate = case["gate_frame"]
    need(gate.get("event") == "GATE", label + ": no actual native L6 gate")
    if precommit:
        need(gate.get("phase") == "file-fsynced-row-uncommitted" and gate.get("in_transaction") is True,
             label + ": did not stop at the native fsynced-file/uncommitted-row boundary")
        expected_unknown = ["objecta"]
    else:
        need(gate.get("phase", gate.get("stage")) == "material-prepared",
             label + ": did not stop after native L6 commit before owner CURRENT")
        expected_unknown = []
    initial = case["cold_initial_view"]
    inventory = initial["inventory"]
    need(inventory.get("unknown_files") == expected_unknown,
         label + ": cold native inventory did not classify interrupted physical bytes")
    if precommit:
        need("objecta" in inventory.get("files", {}) and
             not any(row["name"] == "objecta" for row in inventory.get("dependencies", [])),
             label + ": unknown file was silently catalogued")
        need(frame_reply(case["prepare_before_disposition"]).get("result") == "DENY",
             label + ": later candidate creation ignored unknown file")
    else:
        rows = [row for row in inventory.get("dependencies", []) if row["name"] == "objecta"]
        need(len(rows) == 1 and rows[0].get("kind") == "candidate" and rows[0].get("disposed") == 0,
             label + ": catalogued but unselected candidate not retained as dependency")
        second = frame_reply(case["prepare_before_disposition"])
        need(second.get("result") == "COMMITTED" and second.get("accepted") is False
             and second.get("name") != "objecta",
             label + ": post-recovery candidate preparation was not a fresh native identity")
    refused = frame_reply(case["remove_before_disposition"])
    need(refused.get("result") == "DENY" and refused.get("reason") == "native-inventory-not-empty",
         label + ": removal ignored surviving prepared/unknown material")
    initial_selector = initial.get("selector")
    need(frame_snapshot(case["remove_before_disposition"]).get("selector") == initial_selector,
         label + ": refusal changed native CURRENT")
    dispositions = case["explicit_disposition"]
    need(isinstance(dispositions, list) and dispositions and
         all(frame_reply(item).get("result") == "COMMITTED" for item in dispositions),
         label + ": explicit native dispositions were not committed")
    need(frame_reply(case["cleanup"]).get("result") == "COMMITTED",
         label + ": native cleanup did not finish explicit dispositions")
    need(frame_reply(case["remove_after_disposition"]).get("result") == "COMMITTED",
         label + ": authorized dispositions did not unblock removal")
    final = case["final_view"]
    final_inventory = final.get("inventory", {})
    need(owner_record(final).get("lifecycle") == "removed"
         and final_inventory.get("live") is False and not final_inventory.get("files")
         and not final_inventory.get("unknown_files"),
         label + ": cold final owner/inventory state not removed and empty")
    before, after = case["f1_before"], case["f1_after"]
    need(before["view"] == after["view"] and before["selected"] == after["selected"]
         and before["retained"] == after["retained"] and before["integrity"] == after["integrity"] == "ok",
         label + ": native crash/disposition altered source F1 observations")
    # Independently inspect the actual SQLite bytes captured after owner kill.
    catalog_record = case["owner_tree_after_kill"].get("protected/catalog.sqlite")
    need(catalog_record is not None, label + ": raw pre-recovery L6 catalog missing")
    catalog_bytes = check_file_record(label + "/catalog-after-kill", catalog_record)
    db = sqlite3.connect(":memory:")
    try:
        db.deserialize(catalog_bytes)
        raw_rows = db.execute("SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name").fetchall()
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        db.close()
    need(integrity == "ok", label + ": raw post-kill catalog integrity")
    if precommit:
        need(not any(row[0] == "objecta" for row in raw_rows),
             label + ": pre-COMMIT crash left a cataloged row")
    else:
        need(any(row[0] == "objecta" and row[1] == "candidate" and row[4] == 0 for row in raw_rows),
             label + ": post-COMMIT crash lacks durable candidate row")


def check_candidate_removal_race(case: dict, label: str, creator_first: bool) -> None:
    tree = case["owner_tree"]
    selector, selected = selected_state_from_tree(label, tree)
    final = case["final_view"]
    need(selector == final.get("selector") and selected == owner_state(final),
         label + ": final raw CURRENT differs from cold owner view")
    if creator_first:
        gate = case["creator_gate"]
        need(gate.get("event") == "GATE" and gate.get("phase") == "file-fsynced-row-uncommitted",
             label + ": candidate creator did not hold actual native L6 precommit gate")
        contender = frame_reply(case["contender_remove_while_busy"])
        need(contender.get("result") == "DENY" and contender.get("reason") == "database is locked"
             and contender.get("owner_selection_changed") is False
             and contender.get("durable_phase_changed") is False,
             label + ": real remove contender did not fail without mutation while creator held guards")
        created = frame_reply(case["creator_commit"])
        need(created.get("result") == "COMMITTED" and created.get("accepted") is False
             and created.get("name") == "objecta", label + ": unaccepted candidate creation did not commit")
        blocked = frame_reply(case["remove_after_create"])
        need(blocked.get("result") == "DENY" and blocked.get("reason") == "native-inventory-not-empty",
             label + ": creator-first order did not make removal ineligible")
        need(frame_reply(case["dispose_candidate"]).get("result") == "COMMITTED"
             and frame_reply(case["cleanup"]).get("result") == "COMMITTED"
             and frame_reply(case["remove_after_disposition"]).get("result") == "COMMITTED",
             label + ": explicit candidate disposition did not allow removal to complete")
        need(owner_record(final).get("lifecycle") == "removed"
             and final["inventory"].get("files") == {},
             label + ": creator-first final state did not remove all dependent bytes")
    else:
        gate = case["remover_gate"]
        need(gate.get("event") == "GATE"
             and gate.get("phase", gate.get("stage")) == "domain-removal-selected",
             label + ": remover did not hold native logical-removal gate")
        contender = frame_reply(case["contender_create_while_busy"])
        need(contender.get("result") == "DENY" and contender.get("reason") == "database is locked"
             and contender.get("owner_selection_changed") is False
             and contender.get("durable_phase_changed") is False,
             label + ": real create contender did not fail without mutation while remover held guards")
        need(frame_reply(case["remover_commit"]).get("result") == "COMMITTED",
             label + ": remover-first order did not complete")
        denied = frame_reply(case["create_after_remove"])
        need(denied.get("result") == "DENY" and denied.get("reason") == "native-domain-removed"
             and denied.get("owner_selection_changed") is False
             and denied.get("durable_phase_changed") is False,
             label + ": later native candidate creation was not denied by removed source lifecycle")
        need(owner_record(final).get("lifecycle") == "removed"
             and final["inventory"].get("files") == {},
             label + ": remover-first final inventory is not empty")
    need(case["f1_setup"]["state"]["view"] == case["f1_after"]["view"]
         and case["f1_setup"]["state"]["selected"] == case["f1_after"]["selected"]
         and case["f1_setup"]["state"]["retained"] == case["f1_after"]["retained"],
         label + ": competing native owner operations altered source F1 evidence")
    catalog_bytes = check_file_record(label + "/final-catalog", tree["protected/catalog.sqlite"])
    db = sqlite3.connect(":memory:")
    try:
        db.deserialize(catalog_bytes)
        unit_live = db.execute("SELECT live FROM unit").fetchone()[0]
        deps = db.execute("SELECT name,disposed FROM dependencies ORDER BY name").fetchall()
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        db.close()
    need(integrity == "ok" and unit_live == 0 and all(disposed for _, disposed in deps),
         label + ": actual final L6 catalog not removed with disposed dependencies")


def catalog_rows_from_tree(label: str, tree: dict) -> tuple[int, list[tuple], str]:
    raw_catalog = check_file_record(label + "/catalog.sqlite", tree["protected/catalog.sqlite"])
    db = sqlite3.connect(":memory:")
    try:
        db.deserialize(raw_catalog)
        unit_live = db.execute("SELECT live FROM unit").fetchone()[0]
        deps = db.execute("SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name").fetchall()
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        db.close()
    return unit_live, deps, integrity


def check_acceptance_selected_crash(case: dict) -> None:
    gate = case["gate_frame"]
    need(gate.get("event") == "GATE" and gate.get("phase", gate.get("stage")) == "acceptance-selected",
         "F3 acceptance lost-ack gate did not follow actual native CURRENT selection")
    cold = case["cold_view"]
    selected = owner_record(cold).get("selected")
    registrations = owner_record(cold).get("registrations", [])
    reg = next((item for item in registrations if item.get("id") == selected), None)
    need(reg is not None and reg.get("status") == "live",
         "cold read after acceptance gate lost the actual F3 registration")
    f1 = case["f1_after_accept"]
    check_f1_state("acceptance-gate F1", f1)
    need(reg.get("pair") == f1.get("pair"),
         "crash-selected F3 registration did not derive from actual selected F1 subject")
    material = reg["metadata"]
    name = Path(material["object"]).name
    inventory = cold["inventory"]
    row = next((item for item in inventory.get("dependencies", []) if item.get("name") == name), None)
    need(row is not None and row.get("disposed") == 0 and row.get("sha256") == material["sha256"]
         and row.get("size") == material["size"],
         "acceptance gate lacks actual durable native L6 material row")
    object_record = inventory.get("files", {}).get(name)
    need(object_record is not None and check_file_record("accepted native material", object_record)
         == f1["pair"]["accepted_content"].encode(),
         "accepted F3 registration does not resolve to exact native bytes")
    unit_live, raw_rows, integrity = catalog_rows_from_tree(
        "acceptance tree", case["owner_tree_after_kill"])
    need(unit_live == 1 and integrity == "ok"
         and any(item[0] == name and item[1] == "candidate" and item[4] == 0 for item in raw_rows),
         "raw post-kill L6 catalog did not retain prepared accepted material")
    retry = frame_reply(case["retry"])
    after = frame_snapshot(case["retry"])
    need(retry.get("result") == "COMMITTED" and retry.get("duplicate") is True
         and owner_record(after).get("selected") == selected,
         "exact post-crash accept retry did not observe the selected registration as duplicate")
    need(stable_inventory(after.get("inventory", {})) == stable_inventory(inventory)
         and owner_record(after).get("epoch") == owner_record(cold).get("epoch"),
         "post-crash duplicate added material or advanced epoch")
    need(case["f1_after"]["view"] == f1["view"]
         and case["f1_after"]["selected"] == f1["selected"]
         and case["f1_after"]["retained"] == f1["retained"],
         "accepted-before-reply recovery altered retained source F1 observations")


def check_disposition_crash(case: dict, label: str, inventory_disposed: bool) -> None:
    gate = case["gate_frame"]
    expected = "disposition-committed-before-unlink-reply" if inventory_disposed else "disposition-selected"
    need(gate.get("event") == "GATE" and gate.get("phase", gate.get("stage")) == expected,
         label + ": actual native logical/L6 disposition gate missing")
    cold = case["cold_view"]
    reg = next((item for item in owner_record(cold).get("registrations", [])
                if item.get("id") == case["registration_id"]), None)
    need(reg is not None and reg.get("status") == "disposed"
         and owner_record(cold).get("selected") is None,
         label + ": cold state did not retain logical registration disposition")
    name = Path(reg["metadata"]["object"]).name
    row = next((item for item in cold["inventory"].get("dependencies", [])
                if item.get("name") == name), None)
    file_present = name in cold["inventory"].get("files", {})
    need(row is not None and file_present and row.get("disposed") == int(inventory_disposed),
         label + ": cold inventory does not show the actual interrupted side of L6 unlink")
    if inventory_disposed:
        need(gate.get("in_transaction") is False,
             label + ": post-L6-COMMIT gate unexpectedly reports open transaction")
    else:
        need(gate.get("phase") == "disposition-selected",
             label + ": owner CURRENT gate occurred after the L6 disposition")
    need(frame_reply(case["cleanup"]).get("result") == "COMMITTED"
         and frame_reply(case["remove"]).get("result") == "COMMITTED",
         label + ": explicit cold cleanup did not finish retained disposition and removal")
    final = case["final_view"]
    need(owner_record(final).get("lifecycle") == "removed"
         and final.get("inventory", {}).get("live") is False
         and not final.get("inventory", {}).get("files")
         and final.get("inventory", {}).get("objects_directory_exists") is False,
         label + ": cleanup did not converge on removed/empty native storage")
    unit_live, raw_rows, integrity = catalog_rows_from_tree(label, case["owner_tree_after_kill"])
    need(integrity == "ok" and unit_live == 1
         and any(item[0] == name and item[4] == int(inventory_disposed) for item in raw_rows),
         label + ": raw post-kill L6 catalog disagrees with actual disposition point")
    need(case["f1_after"]["view"] == case["f1_after_accept"]["view"]
         and case["f1_after"]["selected"] == case["f1_after_accept"]["selected"]
         and case["f1_after"]["retained"] == case["f1_after_accept"]["retained"],
         label + ": interrupted disposal changed source F1 observations")


def check_removal_selected_crash(case: dict) -> None:
    gate = case["gate_frame"]
    need(gate.get("event") == "GATE"
         and gate.get("phase", gate.get("stage")) == "domain-removal-selected",
         "native removal did not gate after logical CURRENT and before L6 cleanup")
    cold = case["cold_view"]
    need(owner_record(cold).get("lifecycle") == "removed"
         and cold["inventory"].get("live") is True
         and not cold["inventory"].get("files"),
         "cold removal interruption does not retain the mixed logical/native phase")
    live, rows, integrity = catalog_rows_from_tree("removal selected", case["owner_tree_after_kill"])
    need(live == 1 and not rows and integrity == "ok",
         "raw post-kill L6 catalog differs from the actual pre-removal cleanup point")
    need(frame_reply(case["cleanup"]).get("result") == "COMMITTED",
         "cold removed-domain cleanup did not finish selected physical removal")
    final = case["final_view"]
    need(owner_record(final).get("lifecycle") == "removed"
         and final["inventory"].get("live") is False
         and final["inventory"].get("objects_directory_exists") is False,
         "cold selected-removal cleanup did not remove the data envelope")
    need(case["f1_before"]["view"] == case["f1_after"]["view"]
         and case["f1_before"]["selected"] == case["f1_after"]["selected"]
         and case["f1_before"]["retained"] == case["f1_after"]["retained"],
         "selected removal cleanup altered source F1 observations")


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
    if "native-unknown-precommit" in cases:
        check_preparation_crash(cases["native-unknown-precommit"], "unknown pre-COMMIT", True)
    if "native-candidate-after-catalog" in cases:
        check_preparation_crash(cases["native-candidate-after-catalog"], "candidate post-COMMIT", False)
    if "native-candidate-creator-first" in cases:
        check_candidate_removal_race(cases["native-candidate-creator-first"], "creator-first race", True)
    if "native-candidate-remover-first" in cases:
        check_candidate_removal_race(cases["native-candidate-remover-first"], "remover-first race", False)
    if "native-acceptance-selected-crash" in cases:
        check_acceptance_selected_crash(cases["native-acceptance-selected-crash"])
    if "native-disposition-selected-crash" in cases:
        check_disposition_crash(cases["native-disposition-selected-crash"],
                                "logical disposition", False)
    if "native-inventory-disposed-crash" in cases:
        check_disposition_crash(cases["native-inventory-disposed-crash"],
                                "L6 committed disposition", True)
    if "native-removal-selected-crash" in cases:
        check_removal_selected_crash(cases["native-removal-selected-crash"])
    if "native-f4-authorized-denied" in cases:
        case = cases["native-f4-authorized-denied"]
        check_native_f4(case, "native-f4-authorized-denied")
        verify_live_storage(raw, case, case["owner_after_denial"], "native-f4-authorized-denied")
    if "native-f4-receipt-cold" in cases:
        case = cases["native-f4-receipt-cold"]
        check_native_f4(case, "native-f4-receipt-cold")
        verify_live_storage(raw, case, case["moved_snapshot"], "native-f4-receipt-cold")
    if "native-f4-after-append-eof" in cases:
        case = cases["native-f4-after-append-eof"]
        check_native_f4(case, "native-f4-after-append-eof")
        verify_live_storage(raw, case, case["owner_final"], "native-f4-after-append-eof")
    result = {"status": "PASS", "case_count": len(cases), "source_count": len(sources),
              "raw_sha256": sha(raw_path.read_bytes())}
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise
