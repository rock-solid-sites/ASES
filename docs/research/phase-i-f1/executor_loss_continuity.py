#!/usr/bin/env python3
"""Bounded actual producer/holder loss using the existing Kernel-0 harness."""
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile

KERNEL = Path(__file__).resolve().parent.parent / "kernel-0"
sys.path.insert(0, str(KERNEL))
import kernel0_finite_model as model
import kernel0_recovery_check as check
import kernel0_service as core


def executor(fd):
    with socket.socket(fileno=int(fd)) as conn:
        conn.settimeout(10)
        conn.sendall(check.packet({"kind": "read"}))
        read = check.receive(conn)
        if read["outcome"] != "read":
            raise RuntimeError("fresh read denied")
        value = read["state"]["content"]
        if value not in core.CONTENTS:
            raise RuntimeError("retained content outside finite universe")
        other = next(candidate for candidate in core.CONTENTS if candidate != value)
        def resume(candidate):
            conn.sendall(check.packet({"kind": "resume", "target": 0, "value": candidate, "other": 0}))
            return check.receive(conn)
        wrong = resume(other)
        correct = resume(value)
        print(json.dumps({"fresh_executor_pid": os.getpid(), "read": read,
                          "different_atom": other, "wrong_resume": wrong,
                          "retained_resume": correct}), flush=True)


def main():
    with tempfile.TemporaryDirectory(prefix="ases-retain-") as directory:
        path = Path(directory) / "store.db"
        check.setup(path)
        holder = check.Holder(path)
        producer = check.Worker()
        try:
            producer.attach(holder.clients[1])  # context 0
            accepted = producer.request(model.Request("accept", 0, value=1))
            assert accepted["outcome"] == "commit"
            expected_bytes = accepted["state"]["content"]
            assert expected_bytes == core.CONTENTS[1]
            old_pid = producer.proc.pid
            producer.close()  # SIGKILL and reap via the inherited harness
            assert producer.proc.returncode == -9
            old_holder_pid = holder.kill()
            holder = check.Holder(path)
            assert holder.proc.pid != old_holder_pid
            recovered_before = holder.call({"kind": "read"})["state"]
            assert recovered_before == accepted["state"]
            replacement = holder.request(model.Request("replace", target=0, other=1))
            assert replacement["outcome"] == "commit"
            assert replacement["state"]["rights"][0] == 0
            assert replacement["state"]["rights"][1] != 0
            fd = holder.clients[2].fileno()  # trusted context 1
            fresh = subprocess.run([sys.executable, __file__, "--executor", str(fd)],
                                   pass_fds=[fd], capture_output=True, text=True, timeout=10, check=True)
            result = json.loads(fresh.stdout)
            assert result["fresh_executor_pid"] != old_pid
            assert result["read"]["state"]["content"] == expected_bytes
            assert result["wrong_resume"]["outcome"] == "deny"
            assert result["wrong_resume"]["state"] == result["read"]["state"]
            assert result["retained_resume"]["outcome"] == "commit"
            assert result["retained_resume"]["state"]["data"][0] == 1
            assert result["retained_resume"]["state"]["content"] == expected_bytes
            assert holder.call({"kind": "read"})["state"] == result["retained_resume"]["state"]
            print(json.dumps({"platform": platform.platform(), "python": sys.version.split()[0],
                              "accepted": accepted, "producer_pid": old_pid,
                              "producer_exit": producer.proc.returncode,
                              "holder_killed_pid": old_holder_pid,
                              "holder_restarted_pid": holder.proc.pid,
                              "recovered_before_replacement": recovered_before,
                              "replacement": replacement, "fresh_executor": result,
                              "fresh_executor_exit": fresh.returncode}, indent=2, sort_keys=True))
        finally:
            if producer.proc.poll() is None:
                producer.close()
            if holder.proc.poll() is None:
                holder.kill()

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--executor":
        executor(sys.argv[2])
    else:
        main()
