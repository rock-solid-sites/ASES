#!/usr/bin/env python3
"""Independent read-only audit of the sink-witness probe's raw histories."""
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESEARCH = ROOT / "research/phase-i-t18-sink-order-20261103"
INPUTS = {
    "sink-witness/witness_sink.py": RESEARCH / "sink-witness/witness_sink.py",
    "sink-witness/probe.py": RESEARCH / "sink-witness/probe.py",
    "managed-revocation/managed_sink.py": RESEARCH / "managed-revocation/managed_sink.py",
    "managed-revocation/replay_probe.py": RESEARCH / "managed-revocation/replay_probe.py",
    "managed-revocation/probe.py": RESEARCH / "managed-revocation/probe.py",
    "run.py": RESEARCH / "run.py",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def journal(snapshot):
    raw = bytes.fromhex(snapshot["raw_hex"])
    require(snapshot["exists"] and raw.endswith(b"\n"), "journal absent or incomplete")
    require(hashlib.sha256(raw).hexdigest() == snapshot["sha256"], "journal digest mismatch")
    rows = [json.loads(line) for line in raw.splitlines()]
    return raw, rows


def events_from(rows, name):
    return [row for row in rows if row.get("event") == name]


def audit_case(name, case, witness_pids):
    profile = case["profile"]
    require(profile == name, f"{name}: profile mismatch")
    writer, retained = case["writer"], case["retained"]
    recovered, cold = case["recovery"], case["cold"]
    live = case["witness"]
    status = case["witness_status"]

    # Process identity and lifetime establish an actually surviving external process.
    require(case["witness_alive_after_all_sink_restarts"] is True, f"{name}: witness not live")
    require(live["pid"] == status["pid"] and live["pid"] not in witness_pids,
            f"{name}: witness process identity mismatch/reuse")
    witness_pids.add(live["pid"])
    sink_pids = [writer["pid"], retained["pid"], recovered["pid"], cold["pid"]]
    require(len(set(sink_pids + [live["pid"]])) == 5, f"{name}: process identities overlap")
    require(live["start_ns"] < writer["start_ns"] < cold["exit_ns"] < live["exit_ns"],
            f"{name}: witness did not span all sink sessions")
    require(all(s["exit"] == -9 for s in (writer, retained, recovered, cold)),
            f"{name}: sink child termination not recorded")

    # Revoke ACK precedes successful external publication; both precede the rollback attempt.
    writer_steps = {step["label"]: step for step in writer["steps"]}
    revoke = writer_steps["revoke"]
    publish = case["revoke_publish"]
    require(revoke["response"]["status"] == 200, f"{name}: revoke not ACKed")
    require(publish["status"] == 200 and publish["response"]["publication"] == 2,
            f"{name}: post-revoke publication missing")
    require(revoke["end_ns"] < publish["start_ns"] < publish["end_ns"] < writer["exit_ns"],
            f"{name}: revoke/publication order invalid")
    _, writer_rows = journal(writer["final_journal"])
    revoke_rows = events_from(writer_rows, "managed_revoked")
    require(len(revoke_rows) == 1 and revoke_rows[0]["current_version"] == 1,
            f"{name}: acknowledged revoke/version evidence absent")
    require(status["publication"] == 2 and status["current"]["authority_version"] == 1,
            f"{name}: witness current publication/version mismatch")
    require(status["current"]["granted"] is False and status["current"]["active"] is False,
            f"{name}: live witness does not expose revoked state")

    # The independent raw bytes prove an earlier acknowledged prefix was restored and replayed.
    older = case["rollback"]["old_actual_acknowledged"]
    restored = case["rollback"]["restored"]
    old_raw, old_rows = journal(older)
    restored_raw, restored_rows = journal(restored)
    require(old_raw == restored_raw and case["rollback"]["before"] != restored,
            f"{name}: rollback did not restore earlier actual bytes")
    require(any(row.get("request_id") == "before-positive" and row.get("payload") == "before-witness-x"
                for row in events_from(old_rows, "effect_accepted")),
            f"{name}: earlier accepted positive absent from rollback prefix")
    require(recovered["ready_journal"] == restored and recovered["ready_status"]["authority_version"] == 1,
            f"{name}: recovered sink did not start from rolled-back state")
    candidate = recovered["ready_status"]
    require(candidate["granted"] is True and candidate["active"] is True,
            f"{name}: rolled-back candidate is not locally eligible")
    retained_step = next(step for step in retained["steps"] if step["label"] == "retained-revoke")
    require(retained_step["response"]["status"] == 409
            and not retained_step["observed"]["witness_log"],
            f"{name}: current retained revoke control failed")

    # The sink's actual query and the witness's own log carry the same nonce and identity.
    target = next(step for step in recovered["steps"] if step["label"] == "post-revoke-rolled")
    exchanges = target["observed"]["witness_log"]
    require(len(exchanges) == 1, f"{name}: expected one actual witness query")
    exchange = exchanges[0]
    query, reply = exchange["request"], exchange["response"]
    require(target["start_ns"] < exchange["start_ns"] < exchange["end_ns"] < target["end_ns"],
            f"{name}: witness exchange outside submit interval")
    require(query["profile"] == profile and query["root"] == "selected-root-A"
            and query["candidate"] == {key: candidate[key] for key in
                                        ("created", "granted", "active", "authority_version", "holder")}
            and query["nonce"] == reply["nonce"], f"{name}: query identity/nonce mismatch")
    require(exchange["response_status"] == 200 and exchange["valid"] is True
            and reply["pid"] == live["pid"] and reply["profile"] == profile
            and reply["root"] == "selected-root-A" and reply["publication"] == 2
            and reply["current"] == status["current"], f"{name}: reply is not current live-witness evidence")
    require(any(entry["path"] == "/check" and entry["request"] == query
                and entry["response"] == reply for entry in status["log"]),
            f"{name}: witness process did not record actual query/reply")

    # Compare HTTP outcome with the durable row and cold replay outcome.
    actual_raw, actual_rows = journal(target["journal"])
    del actual_raw
    accepted_rows = events_from(actual_rows, "effect_accepted")
    require(target["observed"]["effects"] == accepted_rows,
            f"{name}: sink status effects disagree with raw journal")
    x_rows = [row for row in accepted_rows if row.get("request_id") == "post-revoke-rolled"
              and row.get("payload") == "x"]
    accepted = target["response"]["status"] == 201
    require(accepted == exchange["admitted"] == reply["allowed"] == bool(x_rows),
            f"{name}: HTTP/witness/journal disagree")
    if accepted:
        require(target["response"]["body"]["event_seq"] == x_rows[0]["seq"],
                f"{name}: ACK sequence is not the durable x effect")
    else:
        require(target["response"]["status"] == 409 and not x_rows,
                f"{name}: denied stale request left effect")
    cold_raw, cold_rows = journal(cold["ready_journal"])
    require(cold["ready_journal"] == recovered["final_journal"]
            and cold["final_journal"] == recovered["final_journal"],
            f"{name}: cold replay did not preserve recovery journal")
    cold_effects = events_from(cold_rows, "effect_accepted")
    require(cold["ready_status"]["effects"] == cold_effects
            and cold["final_status"]["effects"] == cold_effects,
            f"{name}: cold replay status effects disagree with its journal")
    cold_x = [row for row in cold_effects
              if row.get("request_id") == "post-revoke-rolled" and row.get("payload") == "x"]
    require(bool(cold_x) == accepted, f"{name}: cold replay effect differs from ACK")
    return {
        "rolled_submit_status": target["response"]["status"],
        "witness_process_pid": live["pid"],
        "witness_publication": status["publication"],
        "witness_revoked_at_same_generation": status["current"]["authority_version"] == 1
            and status["current"]["granted"] is False and status["current"]["active"] is False,
        "actual_query_nonce_echoed": query["nonce"] == reply["nonce"],
        "durable_x_effect": bool(x_rows),
        "cold_replay_preserved_x_effect": bool(cold_x),
    }


def audit_protocol(controls):
    session = controls["session"]
    steps = {step["label"]: step for step in session["steps"]}
    require([steps[label]["response"]["status"] for label in
             ("positive", "wrong-nonce", "positive-after-reset", "missing-witness")] == [201, 409, 201, 409],
            "protocol controls did not produce expected ordinary sink responses")
    wrong = steps["wrong-nonce"]["observed"]["witness_log"][-1]
    missing = steps["missing-witness"]["observed"]["witness_log"][-1]
    require(wrong["response"]["allowed"] is True and wrong["valid"] is False
            and wrong["admitted"] is False, "wrong-nonce protocol fault was not detected")
    require(missing["response"] is None and missing["valid"] is False
            and missing["admitted"] is False, "missing-witness protocol fault was not detected")
    require(controls["witness"]["exit_ns"] < steps["missing-witness"]["start_ns"],
            "missing-witness attempt preceded witness death")
    kept = events_from(journal(steps["missing-witness"]["journal"])[1], "effect_accepted")
    require([event["payload"] for event in kept] == ["protocol-positive", "protocol-reset-positive"],
            "protocol fault controls changed durable effects")
    return "positive, bad nonce, reset, and missing-witness controls matched actual sink outcomes"


def main():
    raw_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "raw.json"
    raw = json.loads(raw_path.read_bytes())
    require(raw["schema"] == "ases.sink-witness-history" and raw["version"] == 1,
            "unexpected raw evidence schema")
    require(raw["execution_sha"] == "7ee48372c38da079cfdf8aca8c186956f80a2de8",
            "probe used an unexpected source checkout")
    source_hashes = {key: hashlib.sha256(path.read_bytes()).hexdigest()
                     for key, path in INPUTS.items()}
    require(raw["source_hashes"] == source_hashes, "raw source hashes do not match audited inputs")
    require(set(raw["cases"]) == {"generation", "eligibility"}, "unexpected profile set")
    witness_pids = set()
    cases = {name: audit_case(name, value, witness_pids) for name, value in raw["cases"].items()}
    require(cases["generation"]["rolled_submit_status"] == 201
            and cases["eligibility"]["rolled_submit_status"] == 409,
            "profiles did not discriminate on actual sink acceptance")
    protocol = audit_protocol(raw["protocol_controls"])
    print(json.dumps({
        "schema": "ases.sink-witness-independent-audit",
        "version": 1,
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "execution_sha": raw["execution_sha"],
        "source_hashes": source_hashes,
        "cases": cases,
        "protocol_controls": protocol,
        "verdict": "generation-only live witness failed to stop actual post-revoke acceptance; eligibility-tuple comparison denied it",
        "scope_limit": "selected trusted supervisor/endpoint and synchronized publication premise; process liveness was observed, independent source authentication was not tested",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
