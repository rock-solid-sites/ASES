#!/usr/bin/env python3
"""Altered raw-evidence controls for the independent checker."""
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("uid_raw_checker", HERE / "check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
raw = json.loads(checker.RAW_DEFAULT.read_text())


def rejected(name, mutate):
    altered = copy.deepcopy(raw)
    mutate(altered)
    try:
        checker.check(altered, check_host_sources=False)
    except AssertionError:
        return {"control": name, "rejected": True}
    raise AssertionError("checker accepted altered claim: " + name)


def add_writable_fd(data):
    audit = data["cases"]["allowed-native-path"]["worker_fds"]
    audit["descriptors"].append({"fd": 4, "kind": "regular",
                                 "target": "/run/custody/cases/allowed/store/x",
                                 "access_mode": 1, "writable": True})


def contradict_fd_summary(data):
    data["cases"]["allowed-native-path"]["worker_fds"]["writable_store_fds"] = [
        {"fd": 9, "target": "/run/custody/cases/allowed/store/x"}]


controls = [
    rejected("writable-store-fd-hidden-from-worker-audit",
             add_writable_fd),
    rejected("fd-summary-contradicts-raw-descriptors",
             contradict_fd_summary),
    rejected("attenuated-write-changed-to-commit",
             lambda data: data["cases"]["moved-attenuated-native-path"]["final"].update(
                 effect_raw_hex="776f726b65722d657363617065")),
    rejected("manager-kill-reap-omitted",
             lambda data: data["cases"]["kill-before-selector"]["owner_process"].update(
                 manager_reaped=False)),
    rejected("effective-worker-uid-is-root",
             lambda data: data["cases"]["allowed-native-path"]["worker_status"].update(
                 Uid="0\t0\t0\t0")),
    rejected("worker-replaced-lock-inode",
             lambda data: data["cases"]["direct-and-descendant-attacks"]["lock_after"].update(
                 inode=-1)),
    rejected("same-uid-bypass-hidden",
             lambda data: data["cases"]["unguarded-same-uid-bypass"]["unguarded_move"]["result"].update(
                 reply={"result": "DENY"})),
    rejected("inherited-fd-mutant-did-not-write",
             lambda data: data["cases"]["writable-fd-mutant"]["mutant_write"].update(
                 write_bytes=0)),
]
print(json.dumps({"result": "PASS", "controls": controls}, sort_keys=True))
