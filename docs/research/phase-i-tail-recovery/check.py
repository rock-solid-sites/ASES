#!/usr/bin/env python3
"""Independent raw-evidence checker; imports no candidate or repair module."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RAW = HERE / "evidence/final/raw.json"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check(data, check_sources=True):
    require(data.get("execution") == "PASS", "probe did not pass")
    cases = data["cases"]
    required = {"actual-partial-write", "complete-row-fsync-error",
                "recovery-kill-quarantined", "recovery-kill-prepared",
                "recovery-kill-selected", "busy-writer-refusal",
                "invalid-complete-prefix-plus-tail", "no-complete-prefix",
                "witness-mismatch-with-tail", "acknowledged-record-truncation"}
    require(required <= set(cases), "required raw cases absent")

    partial = cases["actual-partial-write"]
    require(partial["failed_attempt"]["status"] == 503, "partial native write did not fail")
    require(partial["after_native_fault"]["raw_hex"] != partial["before"]["raw_hex"],
            "partial native write left no raw effect")
    require(partial["ordinary_restart_bytes_unchanged"], "strict cold refusal changed bytes")
    require(partial["explicit_recovery"].get("ready") is True, "explicit tail recovery failed")
    original = bytes.fromhex(partial["after_native_fault"]["raw_hex"])
    require(len(partial["quarantine"]) == 1, "partial original not quarantined")
    require(bytes.fromhex(partial["quarantine"][0]["raw_hex"]) == original,
            "quarantine is not exact original bytes")
    require(partial["fresh_retry_after_recovery"]["response"]["outcome"] == "accepted",
            "never-completed request was not accepted once")
    first = partial["fresh_retry_after_recovery"]["response"]
    retry = partial["exact_retry_after_recovery"]["response"]
    require(retry["outcome"] == "already-accepted" and retry["event_seq"] == first["event_seq"],
            "exact retry did not observe the single accepted event")
    accepted = [event for event in partial["capture"]["journal"]["events"]
                if event.get("request_id") == "actual-partial-write-id"]
    require(len(accepted) == 1, "retry produced more than one completed effect")

    complete = cases["complete-row-fsync-error"]
    require(complete["failed_attempt"]["status"] == 503, "fsync fault did not surface")
    require(complete["ordinary_restart_bytes_unchanged"], "strict fsync recovery changed bytes")
    require(complete["explicit_recovery"].get("ready") is False
            and complete["explicit_recovery"].get("reason") == "published-cut-unavailable",
            "complete unpublished record was not refused by live witness")
    require(bytes.fromhex(complete["after_native_fault"]["raw_hex"]).endswith(b"\n"),
            "fsync failure did not leave a complete newline-terminated record")
    require(complete["quarantine"] == [], "complete record was quarantined or truncated")

    for stage in ("quarantined", "prepared", "selected"):
        item = cases["recovery-kill-" + stage]
        require(item["gate"]["stage"] == stage, "wrong recovery crash gate")
        require(item["exact_quarantine_present"], "crash gate lost exact quarantine")
        require(item["retry_start"].get("ready") is True, "recovery did not resume after kill")
        require(item["final_equals_validated_prefix"], "post-kill selection was not prefix exact")

    busy = cases["busy-writer-refusal"]
    require(busy["attempt"].get("reason") == "writer-guard-busy" and busy["bytes_unchanged"],
            "busy writer was not refused unchanged")
    require(busy["stable_lock_inode"], "busy refusal did not identify the stable writer lock inode")
    for name in ("invalid-complete-prefix-plus-tail", "no-complete-prefix",
                 "witness-mismatch-with-tail", "acknowledged-record-truncation"):
        item = cases[name]
        require(item["attempt"].get("ready") is False and item["bytes_unchanged"],
                name + " was not refused unchanged")
        require(item["quarantine_count"] == 0, name + " created a quarantine")
    require(cases["witness-mismatch-with-tail"]["attempt"].get("reason") == "published-cut-unavailable",
            "tail witness mismatch did not fail exact live cut check")
    require(cases["acknowledged-record-truncation"]["attempt"].get("reason") == "published-cut-unavailable",
            "acknowledged truncation did not fail exact live cut check")

    if check_sources:
        for relative, expected in data["source_hashes"].items():
            source = (HERE.parent / relative).resolve()
            require(source.is_file(), "source missing: " + relative)
            require(hashlib.sha256(source.read_bytes()).hexdigest() == expected,
                    "source hash mismatch: " + relative)
    return {"result": "PASS", "checked_cases": len(cases),
            "source_hashes_checked": len(data["source_hashes"]) if check_sources else 0}


def main():
    data = json.loads(RAW.read_text())
    print(json.dumps(check(data), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise
