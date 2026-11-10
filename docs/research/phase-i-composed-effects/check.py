#!/usr/bin/env python3
"""Independent checks over composed native process, journal and witness frames."""
import copy
import hashlib
import json
from pathlib import Path
import sys


class EvidenceError(ValueError):
    pass


def need(value, why):
    if not value:
        raise EvidenceError(why)


def raw_bytes(blob):
    need(blob and blob.get("exists") is True, "captured journal bytes missing")
    value = bytes.fromhex(blob["raw_hex"])
    need(len(value) == blob["size"] and hashlib.sha256(value).hexdigest() == blob["sha256"],
         "captured journal bytes fail digest/size")
    return value


def rows(blob):
    return [json.loads(line) for line in raw_bytes(blob).splitlines()]


def effects(blob):
    return [row for row in rows(blob) if row.get("event") == "effect_accepted"]


def tree_bytes(tree, path):
    item = tree.get(path)
    need(item is not None, "missing captured source path " + path)
    value = bytes.fromhex(item["raw_hex"])
    need(len(value) == item["size"] and hashlib.sha256(value).hexdigest() == item["sha256"],
         "captured source bytes fail digest/size: " + path)
    return value


def source_rights(tree):
    current = tree_bytes(tree, "protected/CURRENT").decode().strip()
    selected = json.loads(tree_bytes(tree, "protected/" + current))
    units = selected["work_units"]
    unit, rights, enabled, seen = "D", {"read", "write"}, True, set()
    while unit is not None:
        need(unit in units and unit not in seen, "bad captured L5 ancestry")
        seen.add(unit)
        state = units[unit]
        enabled = enabled and state["active"] and not state["sealed"]
        rights &= set(state["grants"])
        if "latent_ceiling" in state:
            rights &= set(state["latent_ceiling"])
        unit = state["parent"]
    return bool(enabled and selected["current_ingress"] == "W-L5" and "write" in rights)


def call(case, index):
    value = case["calls"][index]
    return value


def effect_identity(row, request_id, payload):
    need(row["request_id"] == request_id and row["payload"] == payload,
         "journal effect identity/payload differs from original request")
    need(hashlib.sha256(payload.encode()).hexdigest() == row["payload_sha256"],
         "journal effect payload digest mismatch")
    cert = row.get("admission")
    need(isinstance(cert, dict) and cert.get("profile") == "experimental-import-v1"
         and cert.get("test_only") is True and cert.get("import_id") ==
         json.loads(payload)["import_id"], "effect lacks original admission certificate")
    return row


def check(raw):
    need(raw.get("execution") == "PASS", "probe did not complete")
    cases = raw["cases"]
    out = {}

    allowed = cases["allowed"]
    allowed_effects = effects(allowed["local"])
    submit_frame = next(item for item in allowed["calls"] if item["path"] == "/submit")
    allowed_reply = submit_frame["response"]
    need(allowed_reply["status"] == 201 and allowed_reply["body"]["outcome"] == "accepted"
         and len(allowed_effects) == 1, "valid composed effect did not append once")
    allowed_event = effect_identity(allowed_effects[0], submit_frame["request"]["request_id"],
                                    submit_frame["request"]["payload"])
    need(allowed_reply["body"]["event_seq"] == allowed_event["seq"],
         "original F4 reply event identity mismatch")
    need(allowed["witness"]["body"]["current"]["journal_sha256"] == allowed["local"]["sha256"],
         "valid new effect is not at published witness cut")
    protocol = allowed["sink_status"]["body"]["cut_protocol_log"]
    publish = [item for item in protocol if item["path"] == "/publish" and item.get("valid")]
    need(publish and publish[-1]["request"]["candidate"]["journal_sha256"] == allowed["local"]["sha256"],
         "valid original publication frame missing or mismatched")
    pub = publish[-1]
    need(pub["response"]["root"] == pub["request"]["root"]
         and pub["response"]["nonce"] == pub["request"]["nonce"]
         and pub["response"]["published"] is True
         and pub["response"]["current"] == pub["request"]["candidate"]
         and pub["response"]["revision"] == pub["request"]["expected_revision"] + 1
         and allowed_reply["body"]["published_revision"] == pub["response"]["revision"]
         and allowed_reply["body"]["published_journal_sha256"] == allowed["local"]["sha256"],
         "original publication/reply root, nonce, revision or cut identity mismatch")
    out["allowed"] = dict(http=201, effects=1, published=True, event_seq=allowed_event["seq"])

    denied = cases["denied-and-retry-only-negative"]["composed"]
    denied_effects = effects(denied["local"])
    denied_submit = next(item for item in denied["calls"] if item["path"] == "/submit")
    need(not source_rights(denied["before"]["l5"]), "moved denial source is not actually denied")
    need(denied_submit["response"]["status"] == 409 and not denied_effects
         and denied_submit["before"]["raw_hex"] == denied_submit["after"]["raw_hex"],
         "composed admission did not deny source-ineligible new effect without append")
    retry_only = cases["denied-and-retry-only-negative"]["retry_only"]
    retry_effects = retry_only["capture"]["journal"]["events"]
    retry_effects = [row for row in retry_effects if row.get("event") == "effect_accepted"]
    need(retry_only["source_allowed"] is False and retry_only["result"]["status"] == 201
         and len(retry_effects) == 1 and retry_effects[0]["payload"] == retry_only["submitted_payload"],
         "retry-only negative control did not accept the exact source-denied payload")
    out["denied-and-retry-only-negative"] = dict(composed_http=409, composed_effects=0,
                                                  retry_only_http=201, retry_only_effects=1)

    lost = cases["lost-receipt-l6-cold"]
    lost_effects = effects(lost["local"])
    calls = lost["calls"]
    first = next(item for item in calls if item["path"] == "/submit")
    first_reply = first["response"]
    need(first_reply["status"] == 503 and first_reply["body"]["outcome"] == "cut-publication-unknown"
         and first_reply["body"]["local_control_committed"] is True and len(lost_effects) == 1,
         "suppressed publication receipt did not preserve one uncertain local effect")
    event = effect_identity(lost_effects[0], first["request"]["request_id"], first["request"]["payload"])
    witness = lost["witness"]["body"]
    need(witness["current"]["journal_sha256"] == lost["local"]["sha256"],
         "lost-receipt publication did not advance actual witness cut")
    witness_publish = [item for item in witness["log"] if item["path"] == "/publish"]
    need(witness_publish and witness_publish[-1]["reply_suppressed"] is True
         and witness_publish[-1]["response"]["published"] is True
         and witness_publish[-1]["response"]["root"] == witness_publish[-1]["request"]["root"]
         and witness_publish[-1]["response"]["nonce"] == witness_publish[-1]["request"]["nonce"]
         and witness_publish[-1]["response"]["current"] == witness_publish[-1]["request"]["candidate"]
         and witness_publish[-1]["request"]["candidate"] == witness["current"],
         "raw witness does not show exact successful reply-suppressed publication")
    need(lost["l6_change"]["dispose"]["reply"]["result"] == "COMMITTED"
         and lost["l6_change"]["remove"]["reply"]["result"] == "COMMITTED"
         and lost["l6_change"]["remove"]["snapshot"]["live"] is False,
         "native L6 dispose/remove transition did not complete")
    need(lost["l6_before"] != lost["l6_after"], "L6 source bytes did not change")
    same = next(item for item in calls if item["path"] == "/submit" and
                item["response"]["body"].get("outcome") == "already-accepted")
    same_reply = same["response"]
    need(same_reply["status"] == 200 and same_reply["body"]["event_seq"] == event["seq"]
         and same_reply["body"]["verified_journal_sha256"] == lost["local"]["sha256"]
         and same["before"]["raw_hex"] == same["after"]["raw_hex"],
         "same-ID retry after L6 removal did not observe the original with zero append")
    checks = [item for item in lost["sink_status"]["body"]["cut_protocol_log"] if item["path"] == "/check"]
    latest_check = checks[-1]
    need(latest_check["response"]["root"] == latest_check["request"]["root"]
         and latest_check["response"]["nonce"] == latest_check["request"]["nonce"]
         and latest_check["response"]["allowed"] is True
         and latest_check["response"]["current"] == witness["current"],
         "historical observation lacks a fresh matching witness reply identity")
    conflict = next(item for item in calls if item["response"]["body"].get("outcome") == "request-id-conflict")
    need(conflict["response"]["status"] == 409 and conflict["before"]["raw_hex"] == conflict["after"]["raw_hex"]
         and conflict["request"]["request_id"] == first["request"]["request_id"]
         and conflict["request"]["payload"] != first["request"]["payload"],
         "same-ID changed payload was not an unchanged identity conflict")
    new = next(item for item in calls if item["path"] == "/submit" and
               item["request"]["request_id"].endswith(":new-after-removal"))
    need(new["response"]["status"] == 409 and new["response"]["body"]["outcome"] == "admission-denied"
         and new["before"]["raw_hex"] == new["after"]["raw_hex"],
         "new request ID crossed current source guards after L6 removal")
    need(lost["cold"]["ready"].get("ready") is True
         and lost["cold"]["journal_identity_before"] == lost["cold"]["journal_identity_after"],
         "cold sink did not recover same persistent journal and live witness")
    cold_retry = lost["same_retry_after_cold"]
    need(cold_retry["status"] == 200 and cold_retry["body"]["outcome"] == "already-accepted"
         and cold_retry["body"]["event_seq"] == event["seq"]
         and lost["journal_after_new_id"]["raw_hex"] == lost["journal_after_cold_retry"]["raw_hex"],
         "same historical result did not survive cold sink restart without duplicate append")
    out["lost-receipt-l6-cold"] = dict(first_http=503, first_local_effects=1,
        witness_published=True, native_l6_removed=True, same_retry_http=200,
        new_id_http=409, conflict_http=409, cold_retry_http=200, duplicate_effects=0)

    revoked = cases["revoke-history"]
    rev_effects = effects(revoked["local"])
    first_rev = next(item for item in revoked["calls"] if item["path"] == "/submit")
    rev_event = effect_identity(rev_effects[0], first_rev["request"]["request_id"],
                                first_rev["request"]["payload"])
    need(len(rev_effects) == 1 and revoked["revoke"]["status"] == 200,
         "native F4 revoke did not follow one original effect")
    need(revoked["old_observation"]["status"] == 200
         and revoked["old_observation"]["body"]["event_seq"] == rev_event["seq"]
         and revoked["journal_after_revoke"]["raw_hex"] == revoked["journal_after_old_observation"]["raw_hex"],
         "historical observation after F4 revoke failed or appended")
    need(revoked["witness"]["body"]["current"]["authority"]["active"] is False,
         "published native revoke is absent from witness state")
    need(revoked["new_after_revoke"]["status"] == 409
         and revoked["journal_after_new"]["raw_hex"] == revoked["journal_after_old_observation"]["raw_hex"],
         "new effect remained eligible after F4 revoke or appended bytes")
    out["revoke-history"] = dict(revoke_http=200, historical_observation_http=200,
                                 new_id_http=409, effects=1)

    rejected = cases["remote-rejection"]
    rejected_effects = effects(rejected["local"])
    need(len(rejected_effects) == 1 and rejected["first"]["status"] == 503
         and rejected["first"]["body"]["local_control_committed"] is True,
         "remote witness rejection did not report one uncertain local append")
    reject_pub = [item for item in rejected["witness"]["body"]["log"] if item["path"] == "/publish"]
    need(reject_pub and reject_pub[-1]["status"] == 503
         and reject_pub[-1]["response"]["published"] is False,
         "raw witness rejection frame missing")
    need(rejected["same_retry"]["status"] == 503
         and rejected["same_retry"]["body"]["outcome"] == "retry-observation-unresolved"
         and rejected["same_retry"]["body"]["local_control_committed"] is True
         and rejected["same_retry"]["body"]["local_event_seq"] == rejected_effects[0]["seq"]
         and rejected["same_retry"]["body"]["new_local_effect"] is False
         and rejected["journal_after_first"]["raw_hex"] == rejected["journal_after_same"]["raw_hex"],
         "unpublished exact retry lost prior local commitment or appended again")
    need(rejected["conflict"]["status"] == 409
         and rejected["conflict"]["body"]["outcome"] == "request-id-conflict"
         and rejected["conflict"]["body"]["event_seq"] == rejected_effects[0]["seq"]
         and rejected["conflict"]["body"]["new_local_effect"] is False
         and rejected["journal_after_same"]["raw_hex"] == rejected["journal_after_conflict"]["raw_hex"]
         and rejected["cold_ready"].get("ready") is False,
         "known conflict under divergent witness cut changed bytes or cold mismatch was accepted")
    rejected_calls = rejected["calls"]
    initial = next(item for item in rejected_calls if item["path"] == "/submit")
    conflicting = next(item for item in rejected_calls
                       if item["response"]["body"].get("outcome") == "request-id-conflict")
    need(conflicting["request"]["request_id"] == initial["request"]["request_id"]
         and conflicting["request"]["payload"] != initial["request"]["payload"],
         "divergent-cut conflict was not same ID with a changed payload")
    need(rejected["witness_before_conflict"]["body"]["log"] ==
         rejected["witness_after_conflict"]["body"]["log"],
         "known conflicting payload unnecessarily contacted the divergent witness")
    out["remote-rejection"] = dict(first_http=503, local_effects=1, retry_http=503,
                                   retry_outcome="retry-observation-unresolved",
                                   prior_local_sequence=rejected_effects[0]["seq"],
                                   new_local_effect=False,
                                   conflict_while_cut_diverged_http=409,
                                   cold_refused=True, duplicate_effects=0)

    killed = cases["kill-after-local-append"]
    killed_effects = effects(killed["journal_at_gate"])
    need(killed["gate"].get("event") == "gate" and killed["gate"].get("stage") == "after-append"
         and len(killed_effects) == 1 and killed["request_reply"] is None,
         "actual post-append child kill did not capture one local effect and no reply")
    killed_event = effect_identity(killed_effects[0], killed["envelope"]["request_id"],
                                   json.dumps(killed["envelope"], sort_keys=True,
                                              separators=(",", ":"), ensure_ascii=True))
    need(killed["killed_process"]["exit"] == -9
         and killed["gate"].get("pid") == killed["killed_process"]["pid"],
         "post-append gate was not owned by the killed sink process")
    need(killed["witness_at_gate"]["body"]["current"]["journal_sha256"] != killed["journal_at_gate"]["sha256"],
         "witness unexpectedly published at post-append kill gate")
    need(killed["cold_ready"].get("ready") is False,
         "cold sink accepted local append whose publication never occurred")
    out["kill-after-local-append"] = dict(gate="after-append", local_effects=1,
        reply=None, witness_published=False, cold_refused=True)

    return dict(cases=out, checker_controls=[], conclusion="BOUNDED_COMPOSED_ADMISSION_RETRY_OBSERVATIONS",
                scope="test-only import mapping; cooperative native writers; selected histories",
                limitations=[
                    "For a retained exact retry after witness publication rejection, the corrected outer outcome wrapper reports retry-observation-unresolved with the original local_event_seq and new_local_effect=false; the HTTP 503 does not prove remote success.",
                    "Known changed-payload IDs return request-id-conflict before witness observation, including while the witness cut diverges; this conflict path is shown to append no bytes.",
                    "The fixture permits historical result reads after revoke; no production information-access policy is established."])


def qualify(raw):
    controls = []
    def event_seq_mismatch(value):
        target = next(item for item in value["cases"]["lost-receipt-l6-cold"]["calls"]
                      if item["response"]["body"].get("outcome") == "already-accepted")
        target["response"]["body"]["event_seq"] = 999

    def exact_conflict(value):
        case = value["cases"]["lost-receipt-l6-cold"]
        first = next(item for item in case["calls"] if item["path"] == "/submit")
        conflict = next(item for item in case["calls"]
                        if item["response"]["body"].get("outcome") == "request-id-conflict")
        conflict["request"]["payload"] = first["request"]["payload"]

    controls_to_try = (
        ("source-denied-forged-success", lambda r: r["cases"]["denied-and-retry-only-negative"]["composed"]["calls"][-1]["response"].update(status=201)),
        ("retry-event-sequence-mismatch", event_seq_mismatch),
        ("same-id-conflict-made-exact", exact_conflict),
    )
    for name, mutate in controls_to_try:
        altered = copy.deepcopy(raw)
        mutate(altered)
        try:
            check(altered)
        except EvidenceError:
            controls.append(dict(name=name, rejected=True))
        else:
            raise EvidenceError("checker accepted altered control: " + name)
    return controls


def main():
    raw = json.loads(Path(sys.argv[1]).read_text())
    value = check(raw)
    value["checker_controls"] = qualify(raw)
    print(json.dumps(value, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
