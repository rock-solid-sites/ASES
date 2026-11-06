#!/usr/bin/env python3
"""Isolated guards around original L5 worker/manager; no hostile-process claim."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True

SOURCE = Path(__file__).resolve().parents[2] / "phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/worker.py"
spec = importlib.util.spec_from_file_location("original_l5_guard_dependency", SOURCE)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
original_manager = worker.l5.manager_roundtrip


def refuse(client, server, request, reason):
    client.sendall((json.dumps(request, sort_keys=True) + "\n").encode())
    received = json.loads(server.makefile("rb", buffering=0).readline())
    reply = dict(result="DENY", reason=reason)
    server.sendall((json.dumps(reply, sort_keys=True) + "\n").encode())
    return received, reply


def generation_manager(client, server, request, state, root):
    before, _ = worker.l5.load_current(root)
    claims = root / "writer-generations"
    claims.mkdir(exist_ok=True)
    claim = claims / (before + ".claim")
    try:
        fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return refuse(client, server, request, "generation-reserved")
    with os.fdopen(fd, "w") as stream:
        stream.write(json.dumps(dict(pid=os.getpid(), selected=before)) + "\n")
    # Reservation wins before the original compare/prepare/publish/reply sequence.
    result = original_manager(client, server, request, state, root)
    if result[1]["result"] != "COMMITTED" and worker.l5.load_current(root)[0] == before:
        claim.unlink()  # Only the owner releases a normal, definitely unused reservation.
    return result  # Successful/uncertain claims survive; no guessed stale-owner reset.


def main():
    mode, root, phase = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    fd = None
    if mode == "exclusive":
        fd = os.open(root / "management-writer.lock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            print(json.dumps(dict(event="REFUSED", reason="writer-busy", pid=os.getpid())), flush=True)
            return 75
    elif mode == "generation":
        worker.l5.manager_roundtrip = generation_manager
    else:
        raise ValueError("unsupported experimental guard")
    sys.argv = [str(SOURCE), str(root), phase]
    try:
        worker.main()
    finally:
        if fd is not None:
            os.close(fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
