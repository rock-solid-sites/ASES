#!/usr/bin/env python3
"""Raw process/journal/source checks; does not import candidate guard code."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def need(value, why):
    if not value:
        raise AssertionError(why)


def bytes_blob(value, label):
    need(isinstance(value, dict) and value.get("exists") is True, label + ": bytes absent")
    raw = bytes.fromhex(value["raw_hex"])
    need(len(raw) == value["size"] and hashlib.sha256(raw).hexdigest() == value["sha256"],
         label + ": byte length/hash mismatch")
    return raw


def rows(blob, label):
    return [json.loads(line) for line in bytes_blob(blob, label).splitlines()]


def effect_rows(case, label):
    return [row for row in rows(case["local"], label) if row.get("event") == "effect_accepted"]


def effect_for(effects, request_id):
    found = [item for item in effects if item.get("request_id") == request_id]
    need(len(found) == 1, "expected one effect for request ID " + request_id)
    return found[0]


def request_frames(case, request_id):
    return [item for item in case["calls"] if item.get("path") == "/submit"
            and item.get("request", {}).get("request_id") == request_id]


def check_effect(row, envelope, version, label):
    payload = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    need(row["payload"] == payload and row["request_id"] == envelope["request_id"],
         label + ": original effect identity or payload bytes differ")
    need(hashlib.sha256(payload.encode()).hexdigest() == row["payload_sha256"],
         label + ": original effect payload digest differs")
    need(row["accepted_under_version"] == version, label + ": effect authority version differs")
    cert = row.get("admission")
    need(isinstance(cert, dict) and cert.get("profile") == "experimental-import-v1"
         and cert.get("test_only") is True and cert.get("import_id") == envelope["import_id"]
         and cert.get("epoch") == envelope["epoch"] and cert.get("l5") == envelope["l5"]
         and cert.get("l6_name") == "x", label + ": admission certificate does not bind tested sources")
    return cert


def witness_matches(case, label):
    local = case["sink_status"]["body"]["actual_cut"]
    witness = case["witness"]["body"]["current"]
    need(witness == local, label + ": raw witness current cut differs from local cut")
    need(witness["journal_sha256"] == case["local"]["sha256"],
         label + ": witness does not identify captured raw journal")
    return witness


def tree_raw(tree, path, label):
    item = tree.get(path)
    need(item is not None, label + ": missing source file " + path)
    raw = bytes.fromhex(item["raw_hex"])
    need(len(raw) == item["size"] and hashlib.sha256(raw).hexdigest() == item["sha256"],
         label + ": captured source file digest differs " + path)
    return raw


def l6_rows(tree, label):
    raw = tree_raw(tree, "catalog.sqlite", label)
    db = sqlite3.connect(":memory:")
    try:
        db.deserialize(raw)
        unit = db.execute("SELECT live,sealed FROM unit").fetchall()
        deps = db.execute("SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name").fetchall()
        return unit, deps
    finally:
        db.close()


def source_mutation(case):
    before, after = case["before"]["l6"], case["actions"]["l6_after_remove"]
    before_db = tree_raw(before, "catalog.sqlite", "initial L6")
    after_db = tree_raw(after, "catalog.sqlite", "mutated L6")
    need(before_db != after_db, "L6 native source mutation left database bytes unchanged")
    before_unit, before_deps = l6_rows(before, "initial L6")
    unit, deps = l6_rows(after, "mutated L6")
    before_x = [row for row in before_deps if row[0] == "x"]
    x_rows = [row for row in deps if row[0] == "x"]
    need(before_unit == [(1, 1)] and unit == [(0, 1)] and len(before_x) == len(x_rows) == 1
         and before_x[0][4] == 0 and x_rows[0][4] == 1
         and before_x[0][1:4] == x_rows[0][1:4],
         "native L6 removal is not visible in captured current catalog")
    need("objects/x" not in after, "disposed L6 physical x remained in source capture")


def check(raw):
    for relative, expected in raw["source_hashes"].items():
        source = REPO / relative
        need(source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == expected,
             "source hash differs from captured runtime input: " + relative)
    cases = raw["cases"]
    valid = cases["valid-cold-continue"]
    valid_effects = effect_rows(valid, "valid continuation")
    a = effect_for(valid_effects, valid["envelope"]["request_id"])
    cert_a = check_effect(a, valid["envelope"], 1, "accepted A")
    actions = valid["actions"]
    need(actions["first"]["status"] == 503
         and actions["first"]["body"]["outcome"] == "cut-publication-unknown"
         and actions["first"]["body"]["local_control_committed"] is True,
         "receipt suppression did not preserve uncertain original A")
    publish = [x for x in actions["first_witness"]["body"]["log"] if x["path"] == "/publish"]
    need(publish and publish[-1]["reply_suppressed"] is True
         and publish[-1]["response"]["published"] is True,
         "actual witness did not suppress the committed publication reply")
    need(actions["cold"]["stopped"]["exit"] == -9
         and actions["cold"]["ready"].get("ready") is True
         and actions["cold"]["journal_identity_before"] == actions["cold"]["journal_identity_after"],
         "sink was not reaped and recovered against the same journal")
    need(actions["cold_status"]["active"] is True and actions["cold_status"]["authority_version"] == 1
         and actions["cold_status"]["cold_admission_open"] is False,
         "active-prefix recovery did not retain authority while sealing new use")
    need(actions["activate_only_active_prefix"]["status"] == 409
         and actions["activate_only_active_prefix"]["body"]["outcome"] == "fresh-replacement-required"
         and bytes_blob(actions["activate_only_journal_before"], "active activate before") ==
         bytes_blob(actions["activate_only_journal_after"], "active activate after"),
         "activate-only on active prefix changed bytes or opened cold gate")
    same_a = actions["historical_while_sealed"]
    same_a_frame = next(item for item in request_frames(valid, valid["envelope"]["request_id"])
                        if item["response"]["body"] == same_a["body"])
    need(same_a["status"] == 200 and same_a["body"]["outcome"] == "already-accepted"
         and same_a["body"]["event_seq"] == a["seq"]
         and same_a["body"]["accepted_authority_version"] == 1
         and same_a["body"]["verified_journal_sha256"] == same_a_frame["before"]["sha256"]
         and same_a_frame["before"]["raw_hex"] == same_a_frame["after"]["raw_hex"],
         "cold-sealed exact A observation failed or appended")
    need(actions["conflict_while_sealed"]["status"] == 409
         and actions["conflict_while_sealed"]["body"]["outcome"] == "request-id-conflict"
         and actions["witness_log_before_conflict"] == actions["witness_log_after_conflict"],
         "known conflicting A was not decided before remote observation")
    conflict_frame = [item for item in request_frames(valid, valid["envelope"]["request_id"])
                      if item["response"]["body"].get("outcome") == "request-id-conflict"][-1]
    need(conflict_frame["before"]["raw_hex"] == conflict_frame["after"]["raw_hex"],
         "known conflict changed journal bytes")
    b = valid["envelope"].copy()
    b["request_id"] += ":new-B"
    need(actions["new_B_while_sealed"]["status"] == 409
         and actions["new_B_while_sealed"]["body"].get("outcome") != "already-accepted"
         and len(valid_effects) == 2,
         "new ID crossed cold gate while sealed")
    # The only second local effect must be B after replacement and activation.
    effect_b = effect_for(valid_effects, b["request_id"])
    check_effect(effect_b, b, 2, "new B after activation")
    need(actions["replace"]["status"] == 200 and actions["activate"]["status"] == 200
         and actions["after_replace"]["authority_version"] == 2
         and actions["after_replace"]["active"] is False,
         "native replacement/activation sequence did not advance to v2")
    need(actions["new_B_after_activation"]["status"] == 201
         and actions["old_version_new_id"]["status"] == 409,
         "new current version failed or old version remained eligible")
    historical_after = actions["historical_A_after_v2"]
    need(historical_after["status"] == 200 and historical_after["body"]["event_seq"] == a["seq"]
         and historical_after["body"]["accepted_authority_version"] == 1,
         "A was recertified as new v2 use instead of retained outcome observation")
    current_witness = witness_matches(valid, "valid continued sink")
    need(current_witness["authority"]["authority_version"] == 2 and current_witness["authority"]["active"] is True,
         "valid continued witness does not publish v2 active cut")

    removed = cases["source-removed-cold"]
    removed_actions = removed["actions"]
    removed_effects = effect_rows(removed, "source removed")
    removed_a = effect_for(removed_effects, removed["envelope"]["request_id"])
    check_effect(removed_a, removed["envelope"], 1, "A before L6 removal")
    source_mutation(removed)
    need(removed_actions["cold"]["stopped"]["exit"] == -9
         and removed_actions["historical_A_source_removed_sealed"]["status"] == 200,
         "retained A was not observable after native L6 source removal and cold recovery")
    need(removed_actions["historical_A_source_removed_sealed"]["body"]["verified_journal_sha256"] ==
         removed_actions["journal_after_first"]["sha256"],
         "source-removed historical lookup did not freshly verify the retained journal cut")
    source_history = next(item for item in request_frames(removed, removed["envelope"]["request_id"])
                          if item["response"]["body"] == removed_actions["historical_A_source_removed_sealed"]["body"])
    need(source_history["before"]["raw_hex"] == source_history["after"]["raw_hex"],
         "historical A after source removal appended bytes")
    need(removed_actions["new_B_after_v2_and_disposal"]["status"] == 409
         and removed_actions["new_B_after_v2_and_disposal"]["body"]["outcome"] == "admission-denied",
         "new ID crossed disposed L6 source guard after fresh F4 version")
    need(len(removed_effects) == 1 and
         removed_actions["journal_after_new_B"]["raw_hex"] == removed["local"]["raw_hex"],
         "source-denied B added an effect event")
    need(removed_actions["historical_A_after_source_denial"]["status"] == 200
         and removed_actions["historical_A_after_source_denial"]["body"]["event_seq"] == removed_a["seq"],
         "source mutation retroactively hid accepted A")
    witness_matches(removed, "source-removed sink")

    inactive = cases["inactive-prefix-cold"]
    ia = inactive["actions"]
    ieffects = effect_rows(inactive, "inactive prefix")
    ia_row = effect_for(ieffects, inactive["envelope"]["request_id"])
    check_effect(ia_row, inactive["envelope"], 1, "A before inactive prefix")
    need(ia["cold_active"]["stopped"]["exit"] == -9 and ia["kill_between"]["stopped"]["exit"] == -9
         and ia["cold_inactive_status"]["active"] is False
         and ia["cold_inactive_status"]["authority_version"] == 2
         and ia["cold_inactive_status"]["cold_admission_open"] is False,
         "intermediate recovery did not retain inactive v2 prefix sealed")
    need(ia["activate_only_inactive_prefix"]["status"] == 409
         and ia["activate_only_inactive_prefix"]["body"]["outcome"] == "fresh-replacement-required"
         and bytes_blob(ia["inactive_activate_before"], "inactive activate before") ==
         bytes_blob(ia["inactive_activate_after"], "inactive activate after"),
         "activate-only on inactive prefix bypassed new replacement")
    need(ia["historical_A_inactive_sealed"]["status"] == 200
         and ia["replace_v3"]["status"] == 200 and ia["activate_v3"]["status"] == 200
         and ia["new_B_v3"]["status"] == 201 and ia["new_C_stale_v2"]["status"] == 409,
         "fresh v3 continuation or stale v2 denial failed")
    ib = inactive["envelope"].copy(); ib["request_id"] += ":new-B-v3"
    check_effect(effect_for(ieffects, ib["request_id"]), ib, 3, "new B after inactive recovery")
    witness_matches(inactive, "inactive prefix sink")

    rejected = cases["remote-rejection"]
    ra = rejected["actions"]
    reffects = effect_rows(rejected, "rejected witness")
    rrow = effect_for(reffects, rejected["envelope"]["request_id"])
    check_effect(rrow, rejected["envelope"], 1, "rejected witness A")
    need(ra["first"]["status"] == 503 and ra["first"]["body"]["local_control_committed"] is True
         and ra["same_retry"]["status"] == 503
         and ra["same_retry"]["body"]["outcome"] == "retry-observation-unresolved"
         and ra["same_retry"]["body"]["local_event_seq"] == rrow["seq"]
         and ra["same_retry"]["body"]["new_local_effect"] is False
         and ra["local_after_first"]["raw_hex"] == ra["local_after_same"]["raw_hex"],
         "witness rejection lost the original local outcome or appended on retry")
    need(ra["conflict"]["status"] == 409 and ra["conflict"]["body"]["outcome"] == "request-id-conflict"
         and ra["witness_log_before_conflict"] == ra["witness_log_after_conflict"],
         "known conflict after rejection contacted witness or was not resolved")
    conflict_frame = next(item for item in request_frames(rejected, rejected["envelope"]["request_id"])
                          if item["response"]["body"] == ra["conflict"]["body"])
    need(conflict_frame["before"]["raw_hex"] == conflict_frame["after"]["raw_hex"],
         "known conflict after rejection changed local bytes")
    need(ra["cold_start_error"].get("ready") is False,
         "cold recovery accepted a divergent local/witness cut")
    witness = ra["witness_after_first"]["body"]
    need(witness["current"]["journal_sha256"] != ra["local_after_first"]["sha256"],
         "rejection control did not preserve a divergent witness cut")
    rejected_publish = [entry for entry in witness["log"] if entry["path"] == "/publish"]
    need(rejected_publish and rejected_publish[-1]["status"] == 503
         and rejected_publish[-1]["response"].get("published") is False,
         "raw witness rejection response was not captured")

    schema = cases["unsupported-schema-v2"]
    sa = schema["envelope"]
    seffects = effect_rows(schema, "unsupported schema")
    schema_a = effect_for(seffects, sa["request_id"])
    check_effect(schema_a, sa, 1, "A before selected schema mutation")
    malformed = schema["actions"]["malformed_current"]
    need(malformed["kind"] == "test-only-malformed-recovery-image"
         and malformed["native_authorized_migration"] is False and malformed["selected_schema"] == 2,
         "unsupported-schema control is not identified as a test-only malformed current image")
    selector_raw = bytes.fromhex(schema["after"]["l5"]["protected/CURRENT"]["raw_hex"])
    selector = selector_raw.decode().strip()
    selected_raw = tree_raw(schema["after"]["l5"], "protected/" + selector, "unsupported L5 record")
    selected_state = json.loads(selected_raw)
    actual_generation = dict(selector=selector, sha256=hashlib.sha256(selected_raw).hexdigest())
    need(actual_generation == malformed["generation"] == schema["actions"]["new_B_envelope"]["l5"]
         and selected_state["schema"] == 2 and malformed["graph_valid"] is True,
         "unsupported selected schema control lacks updated real generation hash")
    new_b = schema["actions"]["new_B_envelope"]
    need(new_b["request_id"] != sa["request_id"]
         and schema["actions"]["new_B_v2_actual_generation"]["status"] == 409
         and schema["actions"]["new_B_v2_actual_generation"]["body"]["outcome"] == "admission-denied"
         and schema["actions"]["new_B_v2_actual_generation"]["body"]["reason"] ==
         "unsupported-l5-interpretation"
         and schema["actions"]["replace_v2"]["status"] == 200
         and schema["actions"]["activate_v2"]["status"] == 200
         and len(seffects) == 1,
         "new ID with a new F4 version bypassed unsupported selected source interpretation")
    need(schema["actions"]["journal_after_new_B"]["raw_hex"] == schema["local"]["raw_hex"],
         "unsupported-schema new effect changed journal bytes")
    need(schema["actions"]["historical_A_after_schema_change"]["status"] == 200
         and schema["actions"]["historical_A_after_schema_denial"]["status"] == 200
         and schema["actions"]["historical_A_after_schema_denial"]["body"]["event_seq"] == schema_a["seq"]
         and schema["actions"]["historical_A_after_schema_denial"]["body"]["accepted_authority_version"] == 1,
         "unsupported current source schema retroactively blocked historical A")
    schema_history = next(item for item in request_frames(schema, sa["request_id"])
                          if item["response"]["body"] ==
                          schema["actions"]["historical_A_after_schema_change"]["body"])
    need(schema_history["before"]["raw_hex"] == schema_history["after"]["raw_hex"],
         "historical A after schema mutation appended bytes")
    schema_new_frame = next(item for item in request_frames(schema, new_b["request_id"]))
    need(schema_new_frame["request"]["payload"] ==
         json.dumps(new_b, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
         and schema_new_frame["before"]["raw_hex"] == schema_new_frame["after"]["raw_hex"],
         "schema denial request did not use current record hash or appended bytes")
    witness_matches(schema, "unsupported schema sink")

    return {"valid_retry_cold_activation_and_v2_effect": True,
            "historical_lookup_survives_source_disposition": True,
            "new_id_still_requires_current_source": True,
            "active_and_inactive_activate_only_denials": True,
            "remote_rejection_retains_local_outcome": True,
            "source_bytes_certificates_versions_witnesses_checked": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--mutant", choices=("cold-seal-bypass", "history-as-new-effect",
                                              "fabricated-current-source", "schema-bypass"))
    args = parser.parse_args()
    data = json.loads(args.raw.read_text())
    if args.mutant == "cold-seal-bypass":
        data["cases"]["valid-cold-continue"]["actions"]["activate_only_active_prefix"]["status"] = 200
    elif args.mutant == "history-as-new-effect":
        data["cases"]["valid-cold-continue"]["actions"]["historical_while_sealed"]["body"]["outcome"] = "accepted"
        data["cases"]["valid-cold-continue"]["actions"]["historical_while_sealed"]["body"]["event_seq"] = 999
    elif args.mutant == "fabricated-current-source":
        case = data["cases"]["source-removed-cold"]
        case["actions"]["l6_after_remove"] = case["before"]["l6"]
    elif args.mutant == "schema-bypass":
        case = data["cases"]["unsupported-schema-v2"]
        case["actions"]["new_B_v2_actual_generation"]["status"] = 201
        case["actions"]["new_B_v2_actual_generation"]["body"]["outcome"] = "accepted"
    print(json.dumps(check(data), sort_keys=True))


if __name__ == "__main__":
    main()
