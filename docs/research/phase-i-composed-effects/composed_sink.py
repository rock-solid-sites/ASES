#!/usr/bin/env python3
"""Minimal test-only composition of the independently exercised local candidates."""
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ADMISSION = HERE.parent / "phase-i-effect-admission"
RETRY = HERE.parent / "phase-i-effect-retry"
sys.path.insert(0, str(ADMISSION))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


admission = load("composed_admission_sink", ADMISSION / "admission_sink.py")
retry = load("composed_retry_sink", RETRY / "candidate.py")

# Both candidates retain the same pinned managed journal transition code.
# Retry observation never calls emit_locked; a new effect still reaches the
# admission hook inside the original managed append and receipt-aware wrapper.
admission.cut.ORIGINAL_STATE = retry.RetryState

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--witness":
        admission.cut.witness_server(sys.argv[2])
    elif len(sys.argv) == 8 and sys.argv[1] == "--sink":
        config = admission.decode(Path(sys.argv[7]).read_text())
        raise SystemExit(admission.serve(config, Path(sys.argv[3]), sys.argv[2] == "recover",
                                        int(sys.argv[4]), sys.argv[6]))
    else:
        raise SystemExit("usage: --witness ROOT | --sink MODE JOURNAL PORT published-cut ROOT CONFIG")
