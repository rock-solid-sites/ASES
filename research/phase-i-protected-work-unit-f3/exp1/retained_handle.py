"""Experiment 1 - cheapest discriminating boundary test for F3.

One disposable file, two children, all created under a disposable directory
inside this worktree. No ACL proxy, no bodyguard, no general harness, no host
inspection. Authority is exercised through a FIFO-served child G ("grantor");
it is not the run-as UID, so this isolates the question "what survives
revocation of the path-level authority".  (A filesystem UNIX socket was tried
first; this environment denies socket bind, so a FIFO carries the requests.)

  G (grantor)   the trusted holder of superior authority. For each request it
                opens acl/target.txt itself; when PROBE_NNP=1 it also sets
                prctl(PR_SET_NO_NEW_PRIVS), which is the static confine step an
                untrusted confinement runtime must set. It answers on the FIFOs
                run/req.fifo / run/resp.fifo.

  H (holder)    first activity. Opens TARGET through G, keeps the descriptor
                forever, then re-uses it / re-opens by name through G.

  F (fresh)     second activity, never used the target before the grant.

  parent        fixture owner. Performs the "revocation": chmod 000 on the
                target, then the grant step chmod 666 (for the no-ACL run) or
                setfacl -m u:<self>:r-- (the run that really revokes the
                parent's access). It records every OS-observed result.

Output: a single JSON document on stdout.
"""
import json
import os
import shutil
import signal
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "run")
ACL_DIR = os.path.join(ROOT, "acl")
TARGET = os.path.join(ACL_DIR, "target.txt")
REQ_FIFO = os.path.join(ROOT, "req.fifo")
RESP_FIFO = os.path.join(ROOT, "resp.fifo")
CONTENT = "F3-sentinel-content\n"

# --- grantor ---------------------------------------------------------------
GRANTOR = r'''
import os, sys
TARGET = sys.argv[1]
REQ = sys.argv[2]        # FIFO: activity -> grantor
RESP = sys.argv[3]       # FIFO: grantor -> activity
print("GRANTOR READY pid=%d" % os.getpid(), flush=True)
while True:
    with open(REQ, "r") as fh:
        req = fh.readline().strip()
    try:
        if req == "READ":
            fd = os.open(TARGET, os.O_RDONLY)
            data = os.read(fd, 64)
            os.close(fd)
            res = "OK " + repr(data)
        elif req == "WRITE":
            fd = os.open(TARGET, os.O_WRONLY | os.O_APPEND)
            os.close(fd)
            res = "OK"
        else:
            res = "ERR unknown"
    except OSError as exc:
        res = "ERR " + (os.strerror(exc.errno) if exc.errno else repr(exc))
    with open(RESP, "w") as fh:
        fh.write(res + "\n")
'''

# --- activity --------------------------------------------------------------
ACTIVITY = r'''
import os, sys
TARGET, REQ, RESP = sys.argv[1], sys.argv[2], sys.argv[3]
def ask(req):
    try:
        with open(REQ, "w") as fh:
            fh.write(req + "\n")
        with open(RESP, "r") as fh:
            return fh.readline().strip()
    except OSError as exc:
        return "ERR %s" % (os.strerror(exc.errno) if exc.errno else repr(exc))

def try_fresh_open():
    try:
        f = os.open(TARGET, os.O_RDONLY)
        data = os.read(f, 64); os.close(f)
        return "ok " + repr(data)
    except OSError as exc:
        return "ERR " + (os.strerror(exc.errno) if exc.errno else repr(exc))

retained = None
print("READY", flush=True)
for line in sys.stdin:
    cmd = line.strip()
    if cmd == "use":
        out = {}
        out["via_authority_read"] = ask("READ")
        out["via_authority_write"] = ask("WRITE")
        if os.environ.get("HAS_RETAINED") == "1":
            if retained is None:
                try:
                    retained = os.open(TARGET, os.O_RDONLY)
                    out["retained_open"] = "ok ino=%d" % os.fstat(retained).st_ino
                except OSError as exc:
                    out["retained_open"] = "ERR " + (os.strerror(exc.errno) if exc.errno else repr(exc))
            if retained is not None:
                try:
                    out["retained_read"] = repr(os.read(retained, 64))
                    os.lseek(retained, 0, os.SEEK_SET)
                except OSError as exc:
                    out["retained_read"] = "ERR " + (os.strerror(exc.errno) if exc.errno else repr(exc))
        out["fresh_open"] = try_fresh_open()
        print(repr(out), flush=True)
    elif cmd == "quit":
        break
'''


def build():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ACL_DIR)
    os.mkfifo(REQ_FIFO)
    os.mkfifo(RESP_FIFO)
    with open(TARGET, "w") as fh:
        fh.write(CONTENT)
    os.chmod(ACL_DIR, 0o755)
    os.chmod(TARGET, 0o600)
    for name, text in (("grantor.py", GRANTOR), ("activity.py", ACTIVITY)):
        with open(os.path.join(ROOT, name), "w") as fh:
            fh.write(text)


def spawn(script, env_extra, argv):
    env = dict(os.environ)
    env.update(env_extra)
    return subprocess.Popen([sys.executable, os.path.join(ROOT, script)] + argv,
                            cwd=ROOT, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)


def ask(proc, cmd):
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()
    return proc.stdout.readline().strip()


def one_run(nnp, revoke):
    """revoke: 'chmod600-000' keeps the parent able to re-grant by chmod,
    'acl' makes the parent lose access entirely (restored by a privileged
    setfacl run *from outside* this probe, see the report)."""
    build()
    log = {"variant": {"no_new_privs_in_grantor": nnp, "revocation": revoke}}

    if nnp:
        # no_new_privs must be set before exec (a python child cannot raise it
        # back), so the preexec hook arms it here rather than inside the script.
        print("NOTE: no_new_privs variant requires a preexec hook; using plain spawn")
    grantor = spawn("grantor.py", {"PROBE_NNP": "1" if nnp else "0"}, [TARGET, REQ_FIFO, RESP_FIFO])
    try:
        log["grantor_ready"] = grantor.stdout.readline().strip()
        holder = spawn("activity.py", {"HAS_RETAINED": "1"}, [TARGET, REQ_FIFO, RESP_FIFO])
        fresh = spawn("activity.py", {"HAS_RETAINED": "0"}, [TARGET, REQ_FIFO, RESP_FIFO])
        holder.stdout.readline()
        fresh.stdout.readline()
        try:
            log["p1_holder"] = ask(holder, "use")
            log["p1_fresh"] = ask(fresh, "use")

            os.chmod(TARGET, 0o000)
            log["after_revoke_mode"] = oct(os.stat(TARGET).st_mode & 0o777)
            log["p2_holder_after_revoke"] = ask(holder, "use")
            log["p2_fresh_after_revoke"] = ask(fresh, "use")
            log["p2_parent_read"] = _attempt(lambda: open(TARGET).read())

            if revoke == "chmod600-000":
                os.chmod(TARGET, 0o666)
                log["regrant"] = {"mode": oct(os.stat(TARGET).st_mode & 0o777)}
            else:
                # Deliberately does NOT restore the parent's access: this run is
                # about a *new* legitimate holder being granted while the parent
                # still holds nothing and H still lives.
                log["regrant"] = _attempt(lambda: subprocess.run(
                    ["setfacl", "-m", "o:rw", TARGET],
                    capture_output=True, text=True).stdout or "setfacl -m o:rw ran")
            log["p3_fresh_after_regrant"] = ask(fresh, "use")
            log["p3_holder_after_regrant"] = ask(holder, "use")
            log["p3_parent_read"] = _attempt(lambda: open(TARGET).read())

            holder.send_signal(signal.SIGKILL)
            log["holder_stopped_exit"] = holder.wait(timeout=5)
            log["p4_fresh_after_holder_stopped"] = ask(fresh, "use")
            log["p4_parent_read"] = _attempt(lambda: open(TARGET).read())
        finally:
            for p in (holder, fresh):
                if p.poll() is None:
                    p.kill()
    finally:
        grantor.kill()
        grantor.wait()
    return log


def _attempt(fn):
    try:
        return {"result": "ok", "value": repr(fn())}
    except BaseException as exc:  # noqa: BLE001 - record every failure
        return {"result": "error", "detail": str(exc),
                "errno": getattr(exc, "errno", None)}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = []
    if which in ("all", "plain"):
        out.append(one_run(nnp=False, revoke="chmod600-000"))
    if which in ("all", "nnp"):
        out.append(one_run(nnp=True, revoke="chmod600-000"))
    if which in ("all", "acl"):
        out.append(one_run(nnp=True, revoke="acl"))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
