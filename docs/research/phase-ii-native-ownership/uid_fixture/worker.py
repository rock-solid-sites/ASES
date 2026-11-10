#!/usr/bin/env python3
"""Fixed UID-2001 attack probe; it accepts no caller-selected paths or code."""
import errno
import json
import os
from pathlib import Path
import socket
import subprocess
import sys


def attempt(label, fn):
    try:
        return {"name": label, "result": "allowed", "value": fn()}
    except OSError as error:
        return {"name": label, "result": "denied", "errno": error.errno,
                "errno_name": errno.errorcode.get(error.errno)}
    except BaseException as error:
        return {"name": label, "result": "error", "error": type(error).__name__,
                "message": str(error)}


def main():
    owner, sink, witness, owner_pid = sys.argv[1:]
    owner = Path(owner)
    cli = subprocess.run(
        [sys.executable, "-B", "/opt/owned-src/docs/research/phase-ii-native-ownership/owner_cli.py",
         "--owner", str(owner)], input='{"op":"remove"}\n', text=True,
        capture_output=True, timeout=2, check=False)
    cli_refused_at_owner_store = (cli.returncode != 0 and "PermissionError" in cli.stderr
                                 and str(owner / "protected") in cli.stderr)
    actions = [
        attempt("protected-current-append", lambda: (owner / "protected/CURRENT").open("ab").write(b"tamper")),
        attempt("management-lock-unlink", lambda: (owner / "management-writer.lock").unlink()),
        {"name": "owner-cli-direct", "result": "refused" if cli_refused_at_owner_store else "allowed",
         "returncode": cli.returncode, "stdout": cli.stdout[-512:], "stderr": cli.stderr[-1024:]},
        attempt("sink-unix-connect", lambda: connect(sink)),
        attempt("witness-unix-connect", lambda: connect(witness)),
        attempt("setuid-controller", lambda: os.setuid(2000)),
    ]
    proc_fds = []
    for fd in range(16):
        proc_fds.append(attempt("owner-proc-fd-" + str(fd),
                                lambda fd=fd: os.open(f"/proc/{owner_pid}/fd/{fd}", os.O_WRONLY)))
    child_code = r'''import errno,json,os
r={"uid":os.getuid(),"euid":os.geteuid()}
for line in open('/proc/self/status'):
 if line.startswith(('Uid:','Gid:','Groups:','CapPrm:','CapEff:','NoNewPrivs:')): r[line.split(':',1)[0]]=line.split(':',1)[1].strip()
try: os.setuid(2000); r["setuid"]="allowed"
except OSError as e: r["setuid"]={"errno":e.errno,"name":errno.errorcode.get(e.errno)}
try: open(os.environ["ASES_OWNER_CURRENT"],"ab").write(b"descendant") ; r["write"]="allowed"
except OSError as e: r["write"]={"errno":e.errno,"name":errno.errorcode.get(e.errno)}
print(json.dumps(r,sort_keys=True))
'''
    descendant = subprocess.run([sys.executable, "-I", "-B", "-c", child_code],
                                env={"PATH": "/usr/local/bin:/usr/bin:/bin",
                                     "ASES_OWNER_CURRENT": str(owner / "protected/CURRENT")},
                                capture_output=True, text=True, timeout=3, check=False,
                                close_fds=True, cwd="/opt/probe")
    print(json.dumps({"event": "ATTACK", "uid": os.getuid(), "euid": os.geteuid(),
                      "actions": actions, "owner_proc_fds": proc_fds,
                      "fork_exec_descendant": {"returncode": descendant.returncode,
                          "stdout": descendant.stdout.strip(), "stderr": descendant.stderr[-512:]}},
                     sort_keys=True), flush=True)


def connect(path):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(path)
        return "connected"
    finally:
        sock.close()


if __name__ == "__main__":
    main()
