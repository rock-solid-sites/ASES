#!/usr/bin/env python3
"""Altered-control qualification for the independent raw checker."""
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("independent_tail_raw_check", HERE / "check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
raw = json.loads((HERE / "evidence/final/raw.json").read_text())


def rejected(name, mutate):
    altered = copy.deepcopy(raw)
    mutate(altered)
    try:
        checker.check(altered, check_sources=False)
    except AssertionError:
        return {"control": name, "checker_rejected": True}
    raise AssertionError("checker accepted altered control: " + name)


controls = [
    rejected("discarded-partial-quarantine-byte",
             lambda data: data["cases"]["actual-partial-write"]["quarantine"][0].__setitem__(
                 "raw_hex", data["cases"]["actual-partial-write"]["quarantine"][0]["raw_hex"][:-2])),
    rejected("complete-unpublished-row-misreported-as-recovered",
             lambda data: data["cases"]["complete-row-fsync-error"]["explicit_recovery"].update(
                 ready=True, reason="ready")),
    rejected("busy-writer-allowed",
             lambda data: data["cases"]["busy-writer-refusal"]["attempt"].update(
                 ready=True, reason="ready")),
    rejected("acknowledged-truncation-mutated-by-repair",
             lambda data: data["cases"]["acknowledged-record-truncation"].update(
                 bytes_unchanged=False)),
    rejected("kill-before-prefix-selection-lost-quarantine",
             lambda data: data["cases"]["recovery-kill-prepared"].update(
                 exact_quarantine_present=False)),
]
print(json.dumps({"result": "PASS", "controls": controls}, sort_keys=True))
