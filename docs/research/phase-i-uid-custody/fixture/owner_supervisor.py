#!/usr/bin/env python3
"""Fixed UID-2000 supervisor; same-UID owner for native manager kill/reap."""
import json
import os
from pathlib import Path
import subprocess
import sys

variant = Path("/opt/probe/src/docs/research/phase-i-f1-recovery-repair/l5/worker_variant.py")
native = Path("/opt/probe/src/docs/research/phase-i-sol-integration/evidence/sources/l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/worker.py")
mode, store, phase = sys.argv[1], sys.argv[2], sys.argv[3]
program = native if mode == "original" else variant
argv = ([sys.executable, "-I", "-B", str(program), store, phase] if mode == "original"
        else [sys.executable, "-I", "-B", str(program), "exclusive", store, phase])
manager = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, bufsize=1,
                           env={"PATH": "/usr/local/bin:/usr/bin:/bin",
                                "PYTHONDONTWRITEBYTECODE": "1"}, close_fds=True,
                           cwd="/opt/probe")
ready_line = manager.stdout.readline()
if not ready_line:
    print(json.dumps({"event": "OWNER_START_FAILED", "exit": manager.poll(),
                      "stderr": manager.stderr.read()[-1024:]}, sort_keys=True), flush=True)
    raise SystemExit(1)
ready = json.loads(ready_line)
print(json.dumps({"event": "OWNER_READY", "manager_pid": manager.pid,
                  "manager_ready": ready}, sort_keys=True), flush=True)
for line in sys.stdin:
    message = json.loads(line)
    command = message.get("cmd")
    if command == "manager":
        manager.stdin.write(json.dumps(message["request"], sort_keys=True) + "\n")
        manager.stdin.flush()
        frame = json.loads(manager.stdout.readline())
        print(json.dumps({"event": "MANAGER_FRAME", "frame": frame}, sort_keys=True), flush=True)
    elif command == "continue":
        manager.stdin.write("continue\n")
        manager.stdin.flush()
        frame = json.loads(manager.stdout.readline())
        print(json.dumps({"event": "MANAGER_FRAME", "frame": frame}, sort_keys=True), flush=True)
    elif command == "kill-manager":
        manager.kill()
        code = manager.wait(timeout=5)
        print(json.dumps({"event": "MANAGER_REAPED", "pid": manager.pid,
                          "exit": code, "still_running": manager.poll() is None}, sort_keys=True), flush=True)
    elif command == "stop":
        if manager.poll() is None:
            manager.stdin.write('{"op":"stop"}\n')
            manager.stdin.flush()
            code = manager.wait(timeout=5)
        else:
            code = manager.returncode
        print(json.dumps({"event": "OWNER_STOPPED", "manager_exit": code}, sort_keys=True), flush=True)
        break
    else:
        print(json.dumps({"event": "OWNER_REFUSED", "reason": "unsupported-supervisor-command"}, sort_keys=True), flush=True)
