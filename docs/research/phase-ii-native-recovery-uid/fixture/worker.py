#!/usr/bin/env python3
"""One-shot UID-2001 direct-access audit for a real native recovery fixture."""
from __future__ import annotations

import errno
import fcntl
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys

OWNED = Path("/opt/owned-src/docs/research")
STRICT_CLI = OWNED / "phase-ii-native-publication-reconcile/reconcile.py"
OBSERVE_CLI = OWNED / "phase-ii-native-local-observation/observe_local.py"


def process_status(pid="self"):
    result = {"pid": os.getpid() if pid == "self" else int(pid)}
    with open(f"/proc/{pid}/status", "r", encoding="utf-8") as stream:
        for line in stream:
            key, sep, value = line.partition(":")
            if sep and key in {"Uid", "Gid", "Groups", "CapPrm", "CapEff", "CapBnd", "NoNewPrivs"}:
                result[key] = value.strip()
    return result


def fd_facts(pid="self"):
    root = Path(f"/proc/{pid}/fd")
    facts = []
    for name in sorted(root.iterdir(), key=lambda p: int(p.name)):
        fd = int(name.name)
        item = {"fd": fd}
        try:
            item["target"] = os.readlink(name)
            st = os.fstat(fd)
            item["kind"] = ("regular" if stat.S_ISREG(st.st_mode) else
                            "directory" if stat.S_ISDIR(st.st_mode) else
                            "socket" if stat.S_ISSOCK(st.st_mode) else "other")
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            item["flags"] = flags
            item["access_mode"] = flags & os.O_ACCMODE
            item["writable_regular"] = (item["kind"] == "regular"
                                        and item["access_mode"] in (os.O_WRONLY, os.O_RDWR))
        except OSError as error:
            item.update(error=type(error).__name__, errno=error.errno,
                        errno_name=errno.errorcode.get(error.errno))
        facts.append(item)
    return facts


def inspect_process_fds(pid):
    root = Path(f"/proc/{pid}/fd")
    try:
        entries = []
        for entry in sorted(root.iterdir(), key=lambda p: int(p.name)):
            try:
                entries.append({"fd": int(entry.name), "target": os.readlink(entry)})
            except OSError as error:
                entries.append({"fd": int(entry.name), "error": type(error).__name__,
                                "errno": error.errno,
                                "errno_name": errno.errorcode.get(error.errno)})
        return {"result": "listed", "entries": entries}
    except OSError as error:
        return {"result": "denied", "error": type(error).__name__, "errno": error.errno,
                "errno_name": errno.errorcode.get(error.errno), "message": str(error)}


def open_without_writing(path):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CLOEXEC)
    except OSError as error:
        return {"result": "denied", "errno": error.errno,
                "errno_name": errno.errorcode.get(error.errno),
                "error": type(error).__name__, "message": str(error)}
    else:
        os.close(fd)
        return {"result": "allowed", "note": "opened without writing"}


def connect_without_sending(path):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(os.fspath(path))
        return {"result": "allowed", "note": "connected without sending"}
    except OSError as error:
        return {"result": "denied", "errno": error.errno,
                "errno_name": errno.errorcode.get(error.errno),
                "error": type(error).__name__, "message": str(error)}
    finally:
        sock.close()


def direct_cli(name, script, owner_root, request_id):
    argv = [sys.executable, "-B", str(script), str(owner_root), request_id]
    try:
        completed = subprocess.run(argv, capture_output=True, text=True,
                                   timeout=15, check=False, close_fds=True,
                                   cwd="/opt/probe")
        stdout = completed.stdout
        stderr = completed.stderr
        try:
            frame = json.loads(stdout.strip().splitlines()[-1]) if stdout.strip() else None
        except (IndexError, json.JSONDecodeError):
            frame = None
        return {"name": name, "argv": argv, "returncode": completed.returncode,
                "stdout": stdout, "stderr": stderr, "frame": frame}
    except BaseException as error:
        return {"name": name, "argv": argv, "result": "launch-error",
                "error": type(error).__name__, "message": str(error)}


DESCENDANT = r'''import errno,json,os,socket,stat,subprocess,sys
owner,sink,witness,request_id,strict_cli,observe_cli=sys.argv[1:]
status={"pid":os.getpid()}
for line in open("/proc/self/status"):
 k,sep,v=line.partition(":")
 if sep and k in {"Uid","Gid","Groups","CapPrm","CapEff","CapBnd","NoNewPrivs"}: status[k]=v.strip()
fds=[]
for p in sorted(__import__("pathlib").Path("/proc/self/fd").iterdir(),key=lambda x:int(x.name)):
 fd=int(p.name); item={"fd":fd}
 try:
  item["target"]=os.readlink(p); st=os.fstat(fd)
  item["kind"]="regular" if stat.S_ISREG(st.st_mode) else "directory" if stat.S_ISDIR(st.st_mode) else "socket" if stat.S_ISSOCK(st.st_mode) else "other"
  flags=__import__("fcntl").fcntl(fd,__import__("fcntl").F_GETFL); item["access_mode"]=flags&os.O_ACCMODE
  item["writable_regular"]=item["kind"]=="regular" and item["access_mode"] in (os.O_WRONLY,os.O_RDWR)
 except OSError as e: item.update(error=type(e).__name__,errno=e.errno)
 fds.append(item)
def opened(path):
 try:
  fd=os.open(path,os.O_WRONLY|os.O_CLOEXEC); os.close(fd); return {"result":"allowed"}
 except OSError as e: return {"result":"denied","errno":e.errno,"errno_name":errno.errorcode.get(e.errno),"error":type(e).__name__,"message":str(e)}
def connected(path):
 s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
 try: s.connect(path); return {"result":"allowed"}
 except OSError as e: return {"result":"denied","errno":e.errno,"errno_name":errno.errorcode.get(e.errno),"error":type(e).__name__,"message":str(e)}
 finally: s.close()
try: os.setuid(2000); status["setuid"]={"result":"allowed"}
except OSError as e: status["setuid"]={"result":"denied","errno":e.errno,"errno_name":errno.errorcode.get(e.errno)}
cli={}
for name,path in (("strict",strict_cli),("observer",observe_cli)):
 argv=[sys.executable,"-B",path,owner,request_id]
 p=subprocess.run(argv,capture_output=True,text=True,timeout=15,check=False,close_fds=True,cwd="/opt/probe")
 try: frame=json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else None
 except Exception: frame=None
 cli[name]={"argv":argv,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"frame":frame}
print(json.dumps({"status":status,"descriptors":fds,"direct_owner_current_open":opened(owner+"/protected/CURRENT"),"sink_socket":connected(sink),"witness_socket":connected(witness),"direct_cli":cli},sort_keys=True))
'''


def fork_exec_descendant(owner_root, sink_socket, witness_socket, owner_pid, request_id):
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin"}
    argv = [sys.executable, "-I", "-B", "-c", DESCENDANT,
            str(owner_root), str(sink_socket), str(witness_socket), request_id,
            str(STRICT_CLI), str(OBSERVE_CLI)]
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, env=env,
                                   timeout=30, check=False, close_fds=True,
                                   cwd="/opt/probe")
        try:
            value = json.loads(completed.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            value = None
        return {"argv": argv, "returncode": completed.returncode,
                "stdout": completed.stdout, "stderr": completed.stderr,
                "value": value}
    except BaseException as error:
        return {"argv": argv, "error": type(error).__name__, "message": str(error)}


def main(argv):
    if len(argv) != 6:
        raise SystemExit("usage: worker.py OWNER_ROOT SINK_SOCKET WITNESS_SOCKET OWNER_PID REQUEST_ID")
    owner_root = Path(argv[1])
    sink_socket, witness_socket = Path(argv[2]), Path(argv[3])
    owner_pid = int(argv[4])
    request_id = argv[5]
    if (not owner_root.is_absolute() or not sink_socket.is_absolute()
            or not witness_socket.is_absolute() or not request_id
            or len(request_id.encode("utf-8")) > 128):
        raise SystemExit("invalid fixed native audit arguments")
    status = process_status()
    owner_status = process_status(owner_pid)
    descriptors = fd_facts()
    writable_regular_fds = [item for item in descriptors if item.get("writable_regular")]
    direct = {
        "owner_current_open": open_without_writing(owner_root / "protected/CURRENT"),
        "owner_process_fds": inspect_process_fds(owner_pid),
        "sink_socket": connect_without_sending(sink_socket),
        "witness_socket": connect_without_sending(witness_socket),
        "reconcile": direct_cli("strict-reconcile", STRICT_CLI, owner_root, request_id),
        "observe_local": direct_cli("observe-local", OBSERVE_CLI, owner_root, request_id),
    }
    descendant = fork_exec_descendant(owner_root, sink_socket, witness_socket,
                                     owner_pid, request_id)
    print(json.dumps({"event": "UID_RECOVERY_WORKER_AUDIT", "uid": os.getuid(), "euid": os.geteuid(),
                      "process_status": status, "owner_process_status": owner_status,
                      "descriptors": descriptors, "writable_authority_regular_fds": writable_regular_fds,
                      "direct": direct,
                      "fork_exec_descendant": descendant}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
