#!/usr/bin/env python3
"""Independent, read-only audit of the captured sink-writer run."""
import hashlib
import json
from pathlib import Path
import sys

EXPECTED = {
    "run.py": "3dcb7f66f7e712778e275034e13cf21e845b0348a2c15fcd93bc465fd8823149",
    "writer-exclusion/guarded_sink.py": "08cfe9d019631448f9570e418762d48326959bbedf89ac37fc41f380b2ef4133",
    "writer-exclusion/probe.py": "d31473bcd0d70553351e18b927d96d4d842a890d6bd3cced7ac25e0c78f48f32",
    "writer-exclusion/check.py": "586682823a8b487163ec8d756feb7b90f2e3b35a6d68c0df8af25b39c63615a1",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rows(snapshot):
    raw = bytes.fromhex(snapshot["raw_hex"])
    require(snapshot["exists"] and raw.endswith(b"\n"), "journal absent or not line complete")
    require(hashlib.sha256(raw).hexdigest() == snapshot["sha256"], "journal digest mismatch")
    return [json.loads(line) for line in raw.splitlines()]


def ack(call, request_id, sequence):
    require(call["response"]["status"] == 201, "missing actual HTTP 201 acknowledgement")
    require(call["response"]["body"]["event_seq"] == sequence, "ACK sequence differs")
    require(call["request"]["request_id"] == request_id, "request identity differs")
    require(call["start_ns"] < call["end_ns"], "request timestamps invalid")
    matches = [r for r in rows(call["journal"])
               if r.get("request_id") == request_id and r.get("payload") == call["request"]["payload"]
               and r.get("seq") == sequence and r.get("event") == "effect_accepted"]
    require(len(matches) == 1, "ACK not tied to exact journal payload and event")


def identity(p, name):
    require(type(p["ready"]) is bool and p["start_ns"] < p["startup_observed_ns"] < p["exit_ns"],
            f"{name}: startup observation order invalid")
    require(bool(p["startup_raw_hex"]) == (p["startup_frame"] is not None), f"{name}: startup frame/raw mismatch")
    if p["startup_raw_hex"]:
        require(json.loads(bytes.fromhex(p["startup_raw_hex"])) == p["startup_frame"],
                f"{name}: decoded startup frame differs from raw")


def main(raw_path):
    d = json.loads(Path(raw_path).read_bytes())
    require(d["schema"] == "ases.sink-writer-exclusion" and d["version"] == 1, "unexpected raw schema")
    require(d["execution_sha"] == "55aee5131141c82c9a6cd2e6418e02890a6291d8", "baseline execution pin differs")
    require(d["source_hashes"] == {k: EXPECTED[k] for k in ("run.py", "writer-exclusion/guarded_sink.py", "writer-exclusion/probe.py")},
            "probe source hashes differ from pre-run capture")

    original = d["cases"]["original_overlap"]
    for name in ("A", "B", "cold"):
        identity(original[name], name)
    require(original["A"]["ready"] and original["B"]["ready"] and not original["cold"]["ready"],
            "unguarded startup/readiness result differs")
    require(original["A"]["startup_observed_ns"] < original["B"]["start_ns"] <
            original["B"]["startup_observed_ns"] < original["journal_before_requests"]["ns"] <
            original["first"]["start_ns"] < original["second"]["start_ns"],
            "both processes were not ready before either request")
    require(original["A"]["journal_path"] == original["B"]["journal_path"] == original["cold"]["journal_path"],
            "unguarded processes did not share a journal")
    require(not original["journal_after_A_ready"]["exists"] and not original["journal_before_requests"]["exists"],
            "fresh journal existed before requests")
    ack(original["first"], "A", 1)
    ack(original["second"], "B", 1)
    original_rows = rows(original["after"])
    require([r["seq"] for r in original_rows] == [1, 1] and
            [r["request_id"] for r in original_rows] == ["A", "B"], "duplicate sequence bytes absent")
    require(original["cold"]["exit"] == 1 and "invalid durable sequence" in original["cold"]["stderr"],
            "cold recovery did not strictly refuse duplicate sequence")
    require(original["after"]["raw_hex"] == original["after_cold"]["raw_hex"] and
            original["after"]["sha256"] == original["after_cold"]["sha256"],
            "strict refusal changed journal bytes")

    guarded = d["cases"]["guarded_restart"]
    for name in ("A", "blocked_B", "fresh_refusal", "recovered", "cold"):
        identity(guarded[name], name)
    require(guarded["A"]["ready"] and not guarded["blocked_B"]["ready"], "second cooperative owner was not blocked")
    require(guarded["blocked_B"]["exit"] == 75 and
            guarded["blocked_B"]["startup_frame"]["reason"] == "writer-guard-busy", "guard refusal differs")
    require(not guarded["journal_before"]["exists"] and not guarded["journal_after_block"]["exists"] and
            guarded["blocked_B"]["exit_ns"] < guarded["first"]["start_ns"],
            "guard was not held before first append")
    ack(guarded["first"], "first", 1)
    require(guarded["A"]["exit"] == -9, "serving process was not killed/reaped")
    require(not guarded["fresh_refusal"]["ready"] and guarded["fresh_refusal"]["exit"] == 1 and
            "existing journal requires explicit recovery mode" in guarded["fresh_refusal"]["startup_frame"]["reason"],
            "fresh restart did not refuse existing journal")
    require(guarded["first"]["journal"]["raw_hex"] == guarded["after_fresh"]["raw_hex"] ==
            guarded["recovered_ready_journal"]["raw_hex"], "current journal changed before recovery")
    require(guarded["restored"]["effects"] == rows(guarded["first"]["journal"]), "recovered owner lost prior ACK")
    ack(guarded["second"], "second", 2)
    final_rows = rows(guarded["final_journal"])
    require([r["request_id"] for r in final_rows] == ["first", "second"] and
            [r["seq"] for r in final_rows] == [1, 2] and guarded["final"]["effects"] == final_rows,
            "current-journal restart did not retain ACKs at sequence 1 then 2")
    guard_frames = [guarded[k]["startup_frame"]["guard"] for k in ("A", "blocked_B", "fresh_refusal", "recovered", "cold")]
    require(all(g == guard_frames[0] for g in guard_frames), "trusted history changed guard identity")

    mixed = d["cases"]["nonparticipating_writer"]
    for name in ("A", "B", "cold"):
        identity(mixed[name], name)
    require(mixed["A"]["ready"] and mixed["B"]["ready"] and mixed["A"]["startup_frame"]["guard"] and
            mixed["B"]["startup_frame"].get("guard") is None, "mixed participation was not established")
    ack(mixed["first"], "A", 1)
    ack(mixed["second"], "B", 1)
    require([r["seq"] for r in rows(mixed["after"])] == [1, 1], "nonparticipant did not bypass cooperative guard")

    distinct = d["cases"]["distinct_roots"]
    require(distinct["A"]["startup_frame"]["guard"]["inode"] !=
            distinct["B"]["startup_frame"]["guard"]["inode"], "distinct roots share a guard file")
    ack(distinct["first"], "root-A", 1)
    ack(distinct["second"], "root-B", 1)
    for entry, name in zip(distinct["cold"], ("root-A", "root-B")):
        identity(entry["process"], "process")
        require(entry["process"]["ready"] and [e["request_id"] for e in entry["status"]["effects"]] == [name],
                "distinct-root recovery mixed or lost effects")

    result = {
        "audit": "PASS",
        "execution_sha": d["execution_sha"],
        "source_hashes_pre_run_verified": True,
        "original_overlap": "COUNTEREXAMPLE: both ready before requests; two actual HTTP 201/seq=1; strict cold recovery refuses and leaves the two acknowledged records byte-identical",
        "guarded_restart": "SUPPORTED: same guard device/inode through profile; second cooperative startup exits 75 before append; fresh mode refuses; kill/recovery resumes same journal at seq=2",
        "nonparticipating_writer": "COUNTEREXAMPLE: unguarded writer joins despite guarded owner and produces a second ACK at seq=1",
        "distinct_roots": "SUPPORTED: different guard inodes and independently recovered effects",
        "owned_children": len(d["children"]),
        "scope_limit": "Advisory flock coordinates participating processes only. No untrusted-host confinement, root authentication, power-loss behavior, or aggregate F4/F1/cross-family claim. Strict refusal does not mean accepted contents disappeared.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1])
