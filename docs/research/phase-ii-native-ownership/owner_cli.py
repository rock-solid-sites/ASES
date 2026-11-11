#!/usr/bin/env python3
"""Trusted native-owner management entrypoint; worker routing is separate."""
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from native_owner import Owner


def emit(value): print(json.dumps(value, sort_keys=True), flush=True)


def main(argv):
    if len(argv) == 6 and argv[1] == "--establish":
        state = Owner.establish(Path(argv[2]), Path(argv[3]), argv[4], argv[5])
        emit(dict(event="ESTABLISHED", snapshot=state.view())); return 0
    if len(argv) not in (3, 4) or argv[1] != "--owner":
        raise SystemExit("usage: --establish ROOT F1 CREATED_BY PROJECT | --owner ROOT [--recover]")
    state = Owner(Path(argv[2]))
    if len(argv) == 4:
        if argv[3] != "--recover": raise ValueError("unsupported startup option")
        state.apply(dict(op="recover"))
    emit(dict(event="READY", snapshot=state.view()))
    for line in sys.stdin:
        request = json.loads(line)
        if request.get("op") == "stop": break
        before = state.view()
        try:
            reply = state.apply(request)
        except Exception as error:
            after = state.view()
            durable_inventory = lambda view: {k: v for k, v in view["inventory"].items()
                                              if k != "observation_ns"}
            changed = (after["selector"] != before["selector"]
                       or durable_inventory(after) != durable_inventory(before))
            reply = dict(result="RECOVERY_REQUIRED" if changed else "DENY",
                         reason=str(error), error=type(error).__name__,
                         owner_selection_changed=after["selector"] != before["selector"],
                         durable_phase_changed=changed)
        emit(dict(event="RESPONSE", request=request, reply=reply, snapshot=state.view()))
    return 0


if __name__ == "__main__": raise SystemExit(main(sys.argv))
