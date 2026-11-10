#!/usr/bin/env python3
"""Isolated append hook around the pinned real F4 published-cut implementation."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from admission import Admission, CAPTURE, Denied, decode

SOURCE = CAPTURE / "receipt/research/phase-i-t18-sink-order-20261103/published-cut/cut_sink.py"
spec = importlib.util.spec_from_file_location("admitted_cut", SOURCE)
cut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cut)


def serve(config, journal, recover, port, root):
    admission = Admission(config)
    original = cut.ORIGINAL_STATE

    class State(original):
        def apply(self, path, data):
            # No exact-obligation or diagnostic route may silently become D use.
            if path in ("/commit-obligation", "/deliver-obligation"):
                return 409, dict(outcome="unsupported-effect-kind", local_control_committed=False)
            try:
                return super().apply(path, data)
            except Denied as error:
                return 409, dict(outcome="admission-denied", reason=str(error), local_control_committed=False)

        def emit_locked(self, name, **fields):
            if name != "effect_accepted":
                return super().emit_locked(name, **fields)
            with admission.guard(fields) as certificate:
                return super().emit_locked(name, admission=certificate, **fields)

        def snapshot(self):
            return dict(super().snapshot(), admission_trace=list(admission.trace),
                        admission_profile="experimental-import-v1", import_is_native_authority=False)

    cut.ORIGINAL_STATE = State
    return cut.serve_sink(journal, recover, port, root)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--witness":
        cut.witness_server(sys.argv[2])
    elif len(sys.argv) == 8 and sys.argv[1] == "--sink":
        raise SystemExit(serve(decode(Path(sys.argv[7]).read_text()), Path(sys.argv[3]),
                              sys.argv[2] == "recover", int(sys.argv[4]), sys.argv[6]))
    else:
        raise SystemExit("usage: --witness ROOT | --sink MODE JOURNAL PORT published-cut ROOT CONFIG")
