#!/usr/bin/env python3
"""Disposable Linux Unix-socket source attribution mechanism experiment."""
import array
import json
import os
import platform
import select
import socket
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

TOKEN = b"current-evidence"
CRED = struct.Struct("3i")


def worker(path):
    tx, rx = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    old_pid = os.fork()
    if old_pid == 0:
        tx.close()
        try:
            data, anc, flags, _ = rx.recvmsg(32, socket.CMSG_SPACE(array.array("i").itemsize))
            if data != b"fd" or flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC):
                os._exit(11)
            fds = array.array("i")
            for level, typ, payload in anc:
                if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
                    fds.frombytes(payload[:len(payload) - len(payload) % fds.itemsize])
            if len(fds) != 1:
                os._exit(12)
            with socket.socket(fileno=fds[0]) as conn:
                conn.sendall(TOKEN)
                rx.sendall(b"sent")
                if rx.recv(8) != b"done":
                    os._exit(13)
            os._exit(0)
        except BaseException:
            os._exit(14)
    rx.close()
    try:
        print(json.dumps({"replacement_pid": os.getpid(), "old_pid": old_pid}), flush=True)
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
            conn.connect(path)
            conn.sendall(TOKEN)
            fds = array.array("i", [conn.fileno()])
            tx.sendmsg([b"fd"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds)])
            if tx.recv(8) != b"sent" or sys.stdin.buffer.read(1) != b"x":
                raise RuntimeError("synchronization failed")
            tx.sendall(b"done")
        _, status = os.waitpid(old_pid, 0)
        if status != 0:
            raise RuntimeError(f"old child status {status}")
    finally:
        tx.close()


def proc_parent(pid):
    # Comm can contain spaces and parentheses; the suffix starts after its last ')'.
    stat = Path(f"/proc/{pid}/stat").read_text()
    return int(stat[stat.rfind(")") + 2:].split()[1])


def receive(conn):
    data, ancillary, flags, _ = conn.recvmsg(256, socket.CMSG_SPACE(CRED.size))
    if flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC):
        raise RuntimeError("truncated data or ancillary credentials")
    credentials = [CRED.unpack(payload[:CRED.size]) for level, typ, payload in ancillary
                   if level == socket.SOL_SOCKET and typ == socket.SCM_CREDENTIALS]
    if len(credentials) != 1:
        raise RuntimeError(f"expected exactly one credentials record: {credentials}")
    pid, uid, gid = credentials[0]
    return {"payload": data.decode(), "message_pid": pid, "message_uid": uid, "message_gid": gid}


def main():
    with tempfile.TemporaryDirectory(prefix="ases-source-") as directory:
        path = str(Path(directory) / "ingress.sock")
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
                with listener.accept()[0] as conn:
                    conn.settimeout(10)
                    peer_pid, peer_uid, peer_gid = CRED.unpack(conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, CRED.size))
                    messages = [receive(conn), receive(conn)]
                    old_parent = proc_parent(ids["old_pid"])
                    assert old_parent == child.pid
                    assert peer_pid == child.pid
                    assert [m["message_pid"] for m in messages] == [child.pid, ids["old_pid"]]
                    assert all(m["payload"] == TOKEN.decode() for m in messages)
                    assert all((m["message_uid"], m["message_gid"]) == (peer_uid, peer_gid) for m in messages)
                    results = []
                    for name, message in zip(("replacement", "old_after_transfer"), messages):
                        results.append({"case": name, **message,
                                        "current_token_and_peer_pid_rule": message["payload"] == TOKEN.decode() and peer_pid == child.pid,
                                        "current_token_and_message_pid_rule": message["payload"] == TOKEN.decode() and message["message_pid"] == child.pid})
                    assert [r["current_token_and_peer_pid_rule"] for r in results] == [True, True]
                    assert [r["current_token_and_message_pid_rule"] for r in results] == [True, False]
                    child.stdin.write("x")
                    child.stdin.flush()
                _, stderr = child.communicate(timeout=10)
                if child.returncode != 0:
                    raise RuntimeError(f"worker exit {child.returncode}: {stderr}")
                print(json.dumps({"platform": platform.platform(), "python": sys.version.split()[0],
                                  "replacement_pid": child.pid, "old_pid": ids["old_pid"],
                                  "old_parent_pid_while_alive": old_parent,
                                  "peer_credentials": {"pid": peer_pid, "uid": peer_uid, "gid": peer_gid},
                                  "observations_and_rule_evaluations": results,
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
