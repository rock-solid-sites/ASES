#!/usr/bin/env python3
"""Interpretation discriminator checked from native record/journal bytes."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys


def need(value, reason):
    if not value:
        raise ValueError(reason)


def blob(value):
    raw = bytes.fromhex(value["raw_hex"])
    need(hashlib.sha256(raw).hexdigest() == value["sha256"] and len(raw) == value["size"], "bad byte capture")
    return raw


def check(before, after):
    need(before["execution"] == after["execution"] == "PASS", "incomplete probe")
    need(before["source_hash"] != after["source_hash"], "source guard was not changed")
    result = {}
    for label in ("valid", "future", "string", "boolean", "missing"):
        old, new = before["cases"][label], after["cases"][label]
        current_raw = blob(new["injected_selected_record"])
        current = json.loads(current_raw)
        need(new["envelope"]["l5"]["sha256"] == hashlib.sha256(current_raw).hexdigest(), "request used stale generation")
        need(old["response"]["status"] == 201 and len([r for r in map(json.loads, blob(old["local"]).splitlines()) if r["event"] == "effect_accepted"]) == 1,
             "old implementation did not execute deciding acceptance")
        schema = current.get("schema")
        supported = type(schema) is int and schema == 1
        need(supported == (label == "valid"), "bad selected interpretation control")
        if supported:
            need(new["response"]["status"] == 201, "valid schema no longer useful")
        else:
            need(new["response"]["status"] == 409 and new["response"]["body"]["reason"] == "unsupported-l5-interpretation"
                 and blob(new["local"]) == blob(new["journal_before"]), "unsupported interpretation appended an effect")
        result[label] = dict(before=old["response"]["status"], after=new["response"]["status"], supported=supported)
    return result


if __name__ == "__main__":
    before, after = [json.loads(gzip.decompress(Path(p).read_bytes()) if p.endswith(".gz")
                               else Path(p).read_bytes()) for p in sys.argv[1:3]]
    result = check(before, after)
    altered = copy.deepcopy(after)
    altered["cases"]["future"]["response"]["status"] = 201
    try:
        check(before, altered)
    except ValueError:
        pass
    else:
        raise ValueError("success-for-unsupported control was not rejected")
    altered = copy.deepcopy(after)
    altered["cases"]["boolean"]["injected_selected_record"]["sha256"] = "0" * 64
    try:
        check(before, altered)
    except ValueError:
        pass
    else:
        raise ValueError("wrong-record-hash control was not rejected")
    print(json.dumps(dict(verdict="PASS", cases=result, altered_controls_rejected=2), sort_keys=True, indent=2))
