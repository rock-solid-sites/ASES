#!/usr/bin/env python3
"""Controlled direct-versus-one-hop source attribution on Linux Unix sockets."""
import array
import json
import os
import platform
import select
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from unix_source_mechanism import CRED, TOKEN, proc_parent, receive


def worker(path):
    replacement, old_control = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    replacement.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
    old_pid = os.fork()
    if old_pid == 0:
        replacement.close()
        try:
            data, ancillary, flags, _ = old_control.recvmsg(8, socket.CMSG_SPACE(array.array("i").itemsize))
            fds = array.array("i")
            for level, kind, value in ancillary:
                if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                    fds.frombytes(value[:len(value) - len(value) % fds.itemsize])
            if data != b"fd" or len(fds) != 1 or flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC):
                os._exit(11)
            with socket.socket(fileno=fds[0]) as sink:
                sink.sendall(TOKEN)  # direct old case
                old_control.sendall(TOKEN)  # independently credentialed proxy request
                if old_control.recv(8) != b"done":
                    os._exit(12)
            os._exit(0)
        except BaseException:
            os._exit(13)
    old_control.close()
    try:
        print(json.dumps({"replacement_pid": os.getpid(), "old_pid": old_pid}), flush=True)
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as sink:
            sink.connect(path)
            sink.sendall(TOKEN)  # authorized self-request
            fds = array.array("i", [sink.fileno()])
            replacement.sendmsg([b"fd"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds)])
            proxy = receive(replacement)  # kernel observes direct sender on control channel
            if proxy["message_pid"] != old_pid or proxy["payload"] != TOKEN.decode():
                raise RuntimeError(f"unexpected proxy input: {proxy}")
            sink.sendall(proxy["payload"].encode())  # same bytes forwarded by replacement
            print(json.dumps({"control_channel_observation": proxy}), flush=True)
            if sys.stdin.buffer.read(1) != b"x":
                raise RuntimeError("missing completion signal")
            replacement.sendall(b"done")
        _, status = os.waitpid(old_pid, 0)
        if status != 0:
            raise RuntimeError(f"old child status {status}")
    finally:
        replacement.close()


def main():
    with tempfile.TemporaryDirectory(prefix="ases-proxy-") as directory:
        path = str(Path(directory) / "sink.sock")
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            listener.bind(path)
            listener.listen(1)
            listener.settimeout(10)
            child = subprocess.Popen([sys.executable, __file__, "--worker", path],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1)
            try:
                if not select.select([child.stdout], [], [], 10)[0]:
                    raise TimeoutError("replacement startup")
                ids = json.loads(child.stdout.readline())
                assert ids["replacement_pid"] == child.pid
                with listener.accept()[0] as sink:
                    sink.settimeout(10)
                    messages = [receive(sink), receive(sink), receive(sink)]
                    control = json.loads(child.stdout.readline())["control_channel_observation"]
                    parent_pid = proc_parent(ids["old_pid"])
                    assert parent_pid == child.pid
                    assert [m["message_pid"] for m in messages] == [child.pid, ids["old_pid"], child.pid]
                    assert all(m["payload"] == TOKEN.decode() for m in messages)
                    assert control["message_pid"] == ids["old_pid"] and control["payload"] == TOKEN.decode()
                    assert len({(m["message_uid"], m["message_gid"]) for m in messages + [control]}) == 1
                    names = ("replacement_self", "old_direct", "old_via_replacement")
                    originators = (child.pid, ids["old_pid"], ids["old_pid"])
                    results = []
                    for name, origin, message in zip(names, originators, messages):
                        results.append({"case": name, **message, "fixture_origin_pid": origin,
                                        "direct_peer_rule_admits": message["message_pid"] == child.pid,
                                        "originator_is_authorized_replacement": origin == child.pid})
                    assert [r["direct_peer_rule_admits"] for r in results] == [True, False, True]
                    child.stdin.write("x")
                    child.stdin.flush()
                _, stderr = child.communicate(timeout=10)
                if child.returncode != 0:
                    raise RuntimeError(f"worker exit {child.returncode}: {stderr}")
                print(json.dumps({"platform": platform.platform(), "python": sys.version.split()[0],
                                  **ids, "old_parent_pid_while_alive": parent_pid,
                                  "control_channel_observation": control,
                                  "sink_observations_and_rule_evaluations": results,
                                  "worker_exit": child.returncode}, indent=2, sort_keys=True))
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=10)

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        worker(sys.argv[2])
    else:
        main()
