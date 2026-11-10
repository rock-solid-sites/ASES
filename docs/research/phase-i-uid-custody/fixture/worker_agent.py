#!/usr/bin/env python3
"""Untrusted UID-2001 test worker and adversarial descendant controls."""
import errno
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys


def emit(value):
    print(json.dumps(value, sort_keys=True), flush=True)


def role():
    # Driver owns stdin/out pipes. A request is never a manager command stream.
    for line in sys.stdin:
        request = json.loads(line)
        if request.get("task") == "stop":
            return
        if request.get("task") == "audit-fds":
            store = Path(request["store"])
            descriptors = []
            for fd in sorted(int(item) for item in os.listdir("/proc/self/fd")):
                try:
                    st = os.fstat(fd)
                    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                    target = os.readlink(f"/proc/self/fd/{fd}")
                    descriptors.append({"fd": fd, "target": target,
                        "kind": "regular" if __import__("stat").S_ISREG(st.st_mode) else "other",
                        "access_mode": flags & os.O_ACCMODE,
                        "writable": (flags & os.O_ACCMODE) != os.O_RDONLY})
                except OSError as error:
                    descriptors.append({"fd": fd, "errno": error.errno,
                                        "errno_name": errno.errorcode.get(error.errno)})
            try:
                os.write(99, b"fd-mutation")
                direct_fd = {"result": "allowed"}
            except OSError as error:
                direct_fd = {"result": "denied", "errno": error.errno,
                             "errno_name": errno.errorcode.get(error.errno)}
            try:
                with (store / "protected/CURRENT").open("ab") as stream:
                    stream.write(b"path-mutation")
                direct_path = {"result": "allowed"}
            except OSError as error:
                direct_path = {"result": "denied", "errno": error.errno,
                               "errno_name": errno.errorcode.get(error.errno)}
            emit({"event": "worker-fd-audit", "uid": os.getuid(), "euid": os.geteuid(),
                  "descriptors": descriptors,
                  "writable_store_fds": [fd for fd in descriptors
                      if fd.get("writable") and str(store) in fd.get("target", "")],
                  "direct_invalid_fd_write": direct_fd, "direct_path_write": direct_path})
            continue
        emit({"event": "worker-request", "request": request.get("request")})
        response = json.loads(sys.stdin.readline())
        emit({"event": "worker-response", "response": response})


def attempt(label, fn):
    try:
        value = fn()
        return {"name": label, "result": "allowed", "value": value}
    except OSError as error:
        return {"name": label, "result": "denied", "errno": error.errno,
                "errno_name": errno.errorcode.get(error.errno)}
    except BaseException as error:
        return {"name": label, "result": "error", "error": type(error).__name__,
                "message": str(error)}


def attack(store, manager_pid, source):
    store = Path(store)
    current = store / "protected/CURRENT"
    lock = store / "management-writer.lock"
    source = Path(source)
    actions = []
    actions.append(attempt("direct-protected-write", lambda: current.open("ab").write(b"tamper")))
    actions.append(attempt("chmod-current", lambda: os.chmod(current, 0o666)))
    actions.append(attempt("unlink-management-lock", lambda: os.unlink(lock)))
    actions.append(attempt("rename-store-root", lambda: os.rename(store, store.parent / "worker-moved-store")))
    actions.append(attempt("modify-original-manager-source", lambda: source.open("ab").write(b"#tamper")))
    actions.append(attempt("setuid-store-owner", lambda: os.setuid(2000)))
    direct_manager = subprocess.run(
        [sys.executable, "-I", "-B", str(source.parent / "move-cuts/worker.py"),
         str(store), "none"], input='{"op":"move"}\n', check=False,
        capture_output=True, text=True,
        env={"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"},
        close_fds=True, cwd="/opt/probe")
    proc_fd = []
    for fd in range(12):
        proc_fd.append(attempt("open-owner-proc-fd-" + str(fd),
                               lambda fd=fd: os.open(f"/proc/{manager_pid}/fd/{fd}", os.O_WRONLY)))

    child_code = r'''import errno,json,os
result={"uid":os.getuid(),"euid":os.geteuid()}
status=open('/proc/self/status').read().splitlines()
for line in status:
 if line.startswith(('Uid:','Gid:','Groups:','CapPrm:','CapEff:','NoNewPrivs:')): result[line.split(':',1)[0]]=line.split(':',1)[1].strip()
try: os.setuid(2000); result["setuid"]="allowed"
except OSError as e: result["setuid"]={"errno":e.errno,"name":errno.errorcode.get(e.errno)}
try:
 f=open(os.environ["CUSTODY_TARGET"],"ab");f.write(b"descendant-tamper");f.close();result["write"]="allowed"
except OSError as e: result["write"]={"errno":e.errno,"name":errno.errorcode.get(e.errno)}
print(json.dumps(result,sort_keys=True))
'''
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "CUSTODY_TARGET": str(current)}
    child = subprocess.run([sys.executable, "-I", "-B", "-c", child_code],
                           check=False, capture_output=True, text=True, env=env,
                           close_fds=True, cwd="/opt/probe")
    emit({"uid": os.getuid(), "euid": os.geteuid(), "actions": actions,
          "direct_original_manager": {"exit": direct_manager.returncode,
              "stdout": direct_manager.stdout[-1024:], "stderr": direct_manager.stderr[-1024:]},
          "owner_proc_fd_attempts": proc_fd, "fork_exec_descendant": {
              "exit": child.returncode, "stdout": child.stdout.strip(), "stderr": child.stderr[-512:]}})
    sys.stdin.readline()


if __name__ == "__main__":
    if sys.argv[1] == "role":
        role()
    elif sys.argv[1] == "attack":
        attack(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else:
        raise SystemExit("role | attack STORE MANAGER_PID ORIGINAL_SOURCE")
