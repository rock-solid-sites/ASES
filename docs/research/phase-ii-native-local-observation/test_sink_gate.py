#!/usr/bin/env python3
"""Pause the actual F4 sink after append/fsync, before native owner callback."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
NATIVE_SINK = REPO / "docs/research/phase-ii-native-ownership/native_sink.py"


def load_sink():
    spec = importlib.util.spec_from_file_location("local_observation_test_native_sink", NATIVE_SINK)
    if spec is None or spec.loader is None:
        raise RuntimeError("pinned native sink unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv):
    sink = load_sink()
    original = sink.NativeAdmission.after_append

    def gate_before_owner_local(self, event):
        frame = {"event": "GATE", "stage": "before-owner-local-observation",
                 "pid": os.getpid(), "request_id": event.get("request_id"),
                 "event_seq": event.get("seq"), "journal_event": event.get("event")}
        print(json.dumps(frame, sort_keys=True), flush=True)
        if sys.stdin.readline() != "continue\n":
            os._exit(86)
        # This is the genuine NativeAdmission callback. The wrapper inserts
        # only the pause before it; no event or owner state is fabricated.
        return original(self, event)

    sink.NativeAdmission.after_append = gate_before_owner_local
    return sink.main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
