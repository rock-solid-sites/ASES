#!/usr/bin/env python3
"""UID-2000 trusted controller for the actual native F1/F3/F4 stack."""
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path("/opt/owned-src/docs/research/phase-ii-native-ownership")
sys.path.insert(0, str(ROOT))
import probe


def emit(value):
    print(json.dumps(value, sort_keys=True), flush=True)


def main():
    case = Path(os.environ["ASES_UID_CASE_ROOT"])
    case.mkdir(mode=0o700, parents=True, exist_ok=True)
    prepared = probe.setup_native_f3(case / "native", world="A", activate=True)
    owner_root = Path(prepared["owner_root"])
    view = prepared["owner_ready"]["snapshot"]
    witness_root = view["state"]["native_owner"]["domain_id"]
    f4 = probe.NativeF4(case / "f4", owner_root, witness_root)
    owner = probe.OwnerProcess(owner_root)
    counter = 0
    emit({"event": "READY", "uid": os.getuid(), "owner_root": str(owner_root),
          "f1_db": str(Path(prepared["f1_root"]) / "store.sqlite"),
          "witness_socket": str(f4.witness_socket), "sink_socket": str(f4.sink_socket),
          "owner_server_pid": owner.p.pid, "sink_pid": f4.sink.p.pid,
          "witness_pid": f4.witness.p.pid, "snapshot": owner.snapshot(),
          "f1_accept": prepared["f1_accept"], "f3_accept": prepared["owner_accept"],
          "f4_lifecycle": f4.lifecycle_calls})
    try:
        for line in sys.stdin:
            q = json.loads(line)
            op = q.get("op")
            if op == "stop":
                break
            if op == "read":
                frame = owner.call({"op": "read"})
                emit({"event": "RESPONSE", "op": op, "frame": frame,
                      "f4": f4.snapshot()})
            elif op == "write" and set(q) == {"op", "payload"} and isinstance(q["payload"], str) \
                    and bool(q["payload"]) \
                    and len(q["payload"].encode("utf-8")) <= 128:
                counter += 1
                request_id = q["payload"]
                frame = owner.call({"op": "read"})
                snapshot = frame["reply"]["snapshot"]
                envelope = probe.native_envelope(snapshot, request_id)
                envelope["kind"] = "use-current-descendant"
                call = f4.submit(envelope)
                journal = f4.snapshot()["journal"]
                actual_events = []
                if journal.get("exists"):
                    for raw_line in bytes.fromhex(journal["raw_hex"]).splitlines():
                        if raw_line:
                            actual_events.append(json.loads(raw_line))
                matching = [event for event in actual_events
                            if event.get("event") == "effect_accepted"
                            and event.get("request_id") == request_id]
                emit({"event": "RESPONSE", "op": op, "request_id": request_id,
                      "payload": q["payload"], "envelope": envelope, "call": call,
                      "owner_after": owner.call({"op": "read"}),
                      "journal": journal, "matching_actual_events": matching})
            elif op == "attenuate" and set(q) == {"op"}:
                steps = [owner.call({"op": name}) for name in ("seal", "move", "activate")]
                emit({"event": "RESPONSE", "op": op, "steps": steps,
                      "snapshot": owner.call({"op": "read"})})
            else:
                emit({"event": "RESPONSE", "op": op, "result": "DENY",
                      "reason": "controller-route-only-D-write-or-management"})
    finally:
        f4.close(kill=True)
        owner.close()
    emit({"event": "STOPPED", "owner": owner.meta, "sink": f4.sink.meta,
          "witness": f4.witness.meta, "owner_tree": probe.tree(owner_root),
          "f4_journal": probe.file_record(f4.journal) if f4.journal.exists() else None})


if __name__ == "__main__":
    main()
