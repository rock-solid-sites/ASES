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

# The outer cut check can refuse before RetryState sees an existing request.
# Preserve the prior local commitment in that outcome instead of accidentally
# presenting the duplicate as proof that no local acceptance happened.
managed = admission.cut.managed
original_serve = managed.serve


def serve_with_retained_outcome(journal, recover=False):
    generated = managed.State

    class OutcomeState(generated):
        def apply(self, path, data):
            previous = None
            if path == "/submit" and isinstance(data, dict):
                request_id, payload = data.get("request_id"), data.get("payload")
                if retry.RetryState._valid_text(request_id) and request_id:
                    previous = self.request_index.get(request_id)
                if previous is not None and previous["payload"] != payload:
                    return 409, dict(outcome="request-id-conflict", event_seq=previous["seq"],
                                     new_local_effect=False)
            status, reply = super().apply(path, data)
            if previous is not None and reply.get("outcome") == "published-cut-unavailable":
                reply = dict(reply, outcome="retry-observation-unresolved", local_control_committed=True,
                             local_event_seq=previous["seq"], new_local_effect=False)
            return status, reply

    managed.State = OutcomeState
    try:
        return original_serve(journal, recover)
    finally:
        managed.State = generated


managed.serve = serve_with_retained_outcome

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--witness":
        admission.cut.witness_server(sys.argv[2])
    elif len(sys.argv) == 8 and sys.argv[1] == "--sink":
        config = admission.decode(Path(sys.argv[7]).read_text())
        raise SystemExit(admission.serve(config, Path(sys.argv[3]), sys.argv[2] == "recover",
                                        int(sys.argv[4]), sys.argv[6]))
    else:
        raise SystemExit("usage: --witness ROOT | --sink MODE JOURNAL PORT published-cut ROOT CONFIG")
