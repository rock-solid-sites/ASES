#!/usr/bin/env python3
"""Independent observation rules, not imported acceptance assertions.

Separates malformed evidence, native local behavior and proposed composition claims.
Same investigator, separately derived rules: this is not a clean-room review.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

HERE = Path(__file__).resolve().parent


class BadEvidence(ValueError):
    pass


def require(value, why):
    if not value:
        raise BadEvidence(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(value):
    require(value["exists"] is True, "missing bytes")
    raw = bytes.fromhex(value["raw_hex"])
    require(digest(raw) == value["sha256"], "byte digest")
    if "size" in value:
        require(len(raw) == value["size"], "byte count")
    return raw


def f1_pair(reader):
    view_raw = bytes.fromhex(reader["view_utf8_hex"])
    obs_raw = bytes.fromhex(reader["observation_utf8_hex"])
    require(digest(view_raw) == reader["view_sha256"], "F1 view hash")
    require(digest(obs_raw) == reader["observation_sha256"], "F1 observation hash")
    view, observed = json.loads(view_raw), json.loads(obs_raw)
    require(view == reader["view"], "F1 parsed view")
    return view["content"], observed


def l5_state(frame):
    snapshot = frame["snapshot"]
    selected = snapshot["selected"]
    files = snapshot["files"]
    current = bytes.fromhex(files["CURRENT"]["raw_hex"])
    require(digest(current) == files["CURRENT"]["sha256"], "L5 selector hash")
    require(current.decode().strip() == selected, "L5 selector")
    raw = bytes.fromhex(files[selected]["raw_hex"])
    require(digest(raw) == files[selected]["sha256"], "L5 selected hash")
    state = json.loads(raw)
    require(state == snapshot["state"], "L5 decoded selected record")
    return state


def descendant_can_write(state):
    # Derive the intersection and enabledness directly from the selected hierarchy.
    units = state["work_units"]
    current, visited, rights, enabled = "D", set(), {"read", "write"}, True
    while current is not None:
        require(current in units and current not in visited, "invalid descendant path")
        visited.add(current)
        unit = units[current]
        require(unit["id"] == current, "unit identity")
        enabled = enabled and unit["active"] and not unit["sealed"]
        rights &= set(unit["grants"])
        if "latent_ceiling" in unit:
            rights &= set(unit["latent_ceiling"])
        current = unit["parent"]
    return bool(enabled and state["current_ingress"] == "W-L5" and "write" in rights)


def joined_identity(case):
    envelope = case["envelope"]
    content, observations = f1_pair(case["f1"]["recovered"])
    require(content == observations["accepted_content"] == envelope["content"], "F1 accepted content binding")
    require(observations["required"] == envelope["accepted_observations"], "F1 accepted evidence identity")
    require(digest(content.encode()) == envelope["content_sha256"], "envelope content hash")
    state = l5_state(case["l5_write"])
    require(state["work_units"]["D"]["parent"] == "C", "descendant identity")
    meta = state["work_units"]["C"]["accepted_contents"][0]
    require(meta["identity"] == envelope["causal_id"] and meta["bridge_envelope"] == envelope, "L5 causal identity")
    data = case["l5_write"]["snapshot"]["files"][meta["object"]]
    raw = bytes.fromhex(data["raw_hex"])
    require(digest(raw) == data["sha256"] == meta["sha256"] == envelope["content_sha256"], "L5 content hash")
    require(raw == content.encode() and len(raw) == meta["size"], "L5 accepted bytes")
    require(case["binding"]["l6_envelope"] == envelope, "test-only L6 binding")
    inv = case["inventory_before"]
    row, = [x for x in inv["dependencies"] if x["name"] == "x"]
    require(row["kind"] == "accepted" and row["disposed"] == 0, "L6 accepted dependency")
    require(row["sha256"] == envelope["content_sha256"] and
            bytes.fromhex(inv["files"]["x"]["raw_hex"]) == content.encode(), "L6 accepted bytes")
    expected = descendant_can_write(state)
    reply = case["l5_write"]["result"]["reply"]
    require(reply["allowed"] is expected and reply["result"] == ("COMMITTED" if expected else "DENY"), "L5 decision differs from path authority")
    return expected


def publication(case):
    pub = case["publication"]
    raw = decode(pub["local"])
    require(raw.endswith(b"\n"), "journal framing")
    rows = [json.loads(line) for line in raw.splitlines()]
    seq = [x["seq"] for x in rows]
    require(all(type(x) is int for x in seq) and seq == sorted(set(seq)), "journal ordering")
    # Rejections are volatile events; durable sequence numbers need not be contiguous.
    require([x["event"] for x in rows[:3]] == ["managed_created", "managed_granted", "managed_activated"], "management prefix")
    effects = [x for x in rows if x["event"] == "effect_accepted"]
    envelope = case["envelope"]
    for effect in effects:
        require(effect["unit"] == "C" and effect["position"] == "p", "sink route identity")
        require(effect["request_id"] == envelope["causal_id"], "effect causal identity")
        require(digest(effect["payload"].encode()) == effect["payload_sha256"], "effect payload digest")
        require(json.loads(effect["payload"]) == envelope, "effect accepted envelope")
        require(effect["accepted_under_version"] == effect["presented_version"] == 1, "flat token fence")
    exchanges = pub["witness"]["body"]["log"]
    successful_acks = 0
    for call in pub["calls"]:
        after = decode(call["after"])
        if call["before"]["exists"]:
            require(after.startswith(decode(call["before"])), "journal prefix rewrote")
        reply = call["response"]
        if reply["status"] not in (200, 201):
            continue
        successful_acks += 1
        body = reply["body"]
        require(body["published_journal_sha256"] == digest(after), "ACK journal digest")
        remote = [e for e in exchanges if e["path"] == "/publish" and
                  e["request"]["candidate"]["journal_sha256"] == digest(after) and
                  e["response"].get("published") is True and e["status"] == 200]
        require(len(remote) == 1, "ACK without unique successful witness exchange")
        exchange, = remote
        require(exchange["request"]["root"] == exchange["response"]["root"] == envelope["causal_id"], "publication root identity")
        require(exchange["request"]["nonce"] == exchange["response"]["nonce"], "publication nonce")
        require(exchange["response"]["revision"] == body["published_revision"] == exchange["request"]["expected_revision"] + 1, "publication revision")
        require(exchange["response"]["current"] == exchange["request"]["candidate"], "receipt selected cut")
        require(json.loads(after.splitlines()[-1])["seq"] == body["event_seq"], "ACK event sequence")
    if case.get("fault"):
        suppressed = [e for e in exchanges if e["path"] == "/publish" and e.get("reply_suppressed")]
        first = case["submit"]
        if case["fault"]["body"].get("configured") and case["fault"]["body"].get("current"):
            require(first["status"] == 503 and first["body"]["local_control_committed"] is True, "uncertain/rejected publication mislabeled")
        if suppressed:
            require(len(suppressed) == 1 and suppressed[0]["response"]["published"] is True, "suppression without remote commit")
            require(case["retry"]["status"] == 201 and len(effects) == 2, "lost receipt retry observation")
            require(pub["witness"]["body"]["current"]["journal_sha256"] == digest(raw), "lost receipt current cut")
        else:
            require(case["retry"]["status"] == 503 and case["retry"]["body"]["local_control_committed"] is False, "rejected publication later mutation")
            require(pub["startup"]["ready"] is False and pub["startup"]["reason"] == "published-cut-unavailable", "divergent cold startup")
    return dict(sequence=seq, effects=len(effects), success_acks=successful_acks)


def negative_controls(cases):
    positive = cases["authorized-neighbor"]
    joined_identity(positive)
    publication(positive)
    controls = []
    transforms = [
        ("swapped_causal_identity", lambda c: c["envelope"].update(causal_id="other-run:C"), joined_identity),
        ("different_opaque_world", lambda c: c["envelope"]["accepted_observations"].update(consumer_evidence="other world"), joined_identity),
        ("wrong_inventory_alias", lambda c: c["binding"]["l6_envelope"].update(unit="D"), joined_identity),
        ("forged_source_permission", lambda c: c["l5_write"]["result"]["reply"].update(allowed=False), joined_identity),
        ("forged_ACK_hash", lambda c: c["publication"]["calls"][-1]["response"]["body"].update(published_journal_sha256="0" * 64), publication),
        ("wrong_receipt_revision", lambda c: c["publication"]["calls"][-1]["response"]["body"].update(published_revision=999), publication),
        ("missing_remote_publication", lambda c: c["publication"]["witness"]["body"].update(log=[]), publication),
        ("corrupt_journal_bytes", lambda c: c["publication"]["local"].update(raw_hex="7b7d0a"), publication),
    ]
    for label, mutate, checker in transforms:
        value = copy.deepcopy(positive)
        mutate(value)
        try:
            checker(value)
        except BadEvidence as error:
            controls.append(dict(control=label, verdict="REJECTED", reason=str(error)))
        else:
            raise BadEvidence("invalid control escaped: " + label)
    return controls


def evaluate(cases):
    result = {}
    for name, case in cases.items():
        if "publication" in case:
            source = joined_identity(case)
            local = publication(case)
            violated = []
            if case["submit"]["status"] == 201:
                if not source:
                    violated.append("downstream effect despite no descendant write authority")
                if not case["inventory_after"]["live"]:
                    violated.append("downstream effect despite inventory unit removed")
            result[name] = dict(identity="MATCHED_BY_TEST_ADAPTER", local_publication=local,
                                source_write=source, inventory_live=case["inventory_after"]["live"],
                                proposed_composition_violations=violated)
        elif name.startswith("recovered-accept-"):
            content, observed = f1_pair(case["final"])
            paired = content == observed["accepted_content"]
            result[name] = dict(ack=case["accept"]["outcome"], paired=paired,
                                consumer_query=case["final"]["query"]["status"],
                                new_content=content, stored_binding=observed["accepted_content"])
        elif "nonaccept" in case:
            before, old = f1_pair(case["f1"]["recovered"])
            after, new = f1_pair(case["final"])
            result[name] = dict(content_unchanged=before == after, accepted_evidence_unchanged=old == new,
                                operation=case["nonaccept"]["outcome"])
        elif name == "competing-l5-managers":
            state = l5_state(case["cold"])
            result[name] = dict(move_ack=case["move_response"]["result"]["reply"]["result"],
                                actual_parent=state["work_units"]["C"]["parent"],
                                actual_active=state["work_units"]["C"]["active"],
                                move_receipt_hash_matches_selected=case["move_response"]["result"]["reply"]["record_sha256"] == case["cold"]["snapshot"]["files"][case["cold"]["snapshot"]["selected"]]["sha256"])
        elif name.startswith("f1-kill-"):
            content, observed = f1_pair(case["f1"]["recovered"])
            result[name] = dict(ack=case["f1"]["accept"], paired=content == observed["accepted_content"],
                                accepted_target=content == case["envelope"]["content"], downstream=case["downstream_files"])
        elif name == "l6-kill-before-catalog":
            result[name] = dict(unknown=case["inventory"]["unknown_files"], live=case["inventory"]["live"],
                                removal=case["removal"]["reply"]["result"])
        elif name.startswith("removal-race-"):
            result[name] = dict(creator=case["creator"]["reply"]["result"], removal=case["removal"]["reply"]["result"],
                                live=case["inventory"]["live"], files=sorted(case["inventory"]["files"]))
        else:
            raise BadEvidence("unclassified case " + name)
    return result


def persisted_readback(capture, cases):
    checked = []
    for name, case in cases.items():
        reader = case.get("final") if "original" in case or "nonaccept" in case else case.get("f1", {}).get("recovered")
        if not reader or "view" not in reader:
            continue
        path = capture / "state" / name / "f1/store.sqlite"
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
            raw, = db.execute("SELECT view FROM kernel WHERE id=1").fetchone()
            observed, = db.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()
            require(db.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "SQLite integrity")
        require(raw.encode().hex() == reader["view_utf8_hex"] and observed.encode().hex() == reader["observation_utf8_hex"], "SQLite capture disagrees with reader")
        checked.append(name)
    return checked


def prior_checker_probe(cases):
    path = HERE.parent / "phase-i-assurance/f4_trace_refinement.py"
    spec = importlib.util.spec_from_file_location("prior_checker_instrument_under_test", path)
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    results = {}
    # Import is ONLY the instrument under adversarial test, never this observer's oracle.
    for name in ("authorized-neighbor", "valid-rejection-gap"):
        snapshot = cases[name]["publication"]["local"]
        publication(cases[name])
        try:
            prior.journal(snapshot)
        except prior.BadF4Trace as error:
            results[name] = dict(prior="REJECTED", independent="VALID_LOCAL_HISTORY", reason=str(error))
        else:
            results[name] = dict(prior="ACCEPTED", independent="VALID_LOCAL_HISTORY")
    return results


def check_findings(results):
    """Verify reproduction of findings, never label the unsafe system invariant green."""
    require(results["authorized-neighbor"]["source_write"] and not
            results["authorized-neighbor"]["proposed_composition_violations"], "authorized neighbor did not work")
    require(not results["attenuated-descendant"]["source_write"] and
            len(results["attenuated-descendant"]["proposed_composition_violations"]) == 1, "authority counterexample not reproduced")
    require(not results["removed-inventory"]["inventory_live"] and
            len(results["removed-inventory"]["proposed_composition_violations"]) == 1, "lifecycle counterexample not reproduced")
    require(results["competing-l5-managers"]["move_ack"] == "COMMITTED" and
            results["competing-l5-managers"]["actual_parent"] == "P", "stale manager counterexample not reproduced")
    require(results["same-observations"]["accepted_evidence_unchanged"] and not
            results["changed-observations"]["accepted_evidence_unchanged"], "evidence lifetime contrast not reproduced")
    require(results["recovered-accept-missing-observations"]["ack"] == "commit" and not
            results["recovered-accept-missing-observations"]["paired"] and
            results["recovered-accept-fresh-observations"]["paired"], "recovery accept contrast not reproduced")
    require(results["f1-kill-durable"]["paired"] and results["f1-kill-durable"]["accepted_target"] and
            results["f1-kill-prepared"]["paired"] and not results["f1-kill-prepared"]["accepted_target"], "F1 crash prefix contrast")
    require(results["l6-kill-before-catalog"] == dict(unknown=["x"], live=True, removal="DENY"), "L6 debris guard")
    require(results["removal-race-guarded"]["creator"] == "DENY" and
            results["removal-race-guarded"]["removal"] == "COMMITTED" and
            results["removal-race-creator-first"]["creator"] == "COMMITTED" and
            results["removal-race-creator-first"]["removal"] == "DENY", "valid inventory orderings")
    require(not results["removal-race-detached"]["live"] and
            results["removal-race-detached"]["files"] == ["x"], "detached mutation did not strand content")
    return "FINDINGS_REPRODUCED_INCLUDING_UNSAFE_HISTORIES"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("captures", nargs="+", type=Path)
    args = parser.parse_args()
    cases, readbacks = {}, {}
    for capture in args.captures:
        raw = json.loads((capture / "raw.json").read_text())
        require(raw["execution"] == "PASS", "execution is not complete")
        require(not set(cases) & set(raw["cases"]), "duplicate case identity")
        cases.update(raw["cases"])
        readbacks[capture.name] = persisted_readback(capture, raw["cases"])
    results = evaluate(cases)
    controls = negative_controls(cases)
    print(json.dumps(dict(cases=results, invalid_controls=controls, persisted_sqlite_readbacks=readbacks,
                          prior_checker_probe=prior_checker_probe(cases),
                          reproduction=check_findings(results),
                          scope="selected native histories; trusted test import; same-investigator independent rules; no universal refinement"), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
