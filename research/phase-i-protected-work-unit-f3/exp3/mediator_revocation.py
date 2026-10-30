import ctypes, json, os, socket, struct, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "fixture")
TARGET = os.path.join(ROOT, "target.txt")
ALIAS = os.path.join(ROOT, "alias.txt")
CONTENT = b"revocable-mediator-sentinel\n"
SYS_CREATE, SYS_ADD, SYS_RESTRICT = 444, 445, 446
READ_FILE, READ_DIR = 1 << 2, 1 << 3

WORKER = r'''
import errno, json, os, socket, sys, time
TARGET, ALIAS, SOCK = sys.argv[1], sys.argv[2], int(sys.argv[3])
out = {"pid": os.getpid()}
for label, path in (("direct_target", TARGET), ("symlink_alias", ALIAS)):
    try:
        fd = os.open(path, os.O_RDONLY)
        try: out[label] = {"result": "allowed", "data": repr(os.read(fd, 128))}
        finally: os.close(fd)
    except OSError as exc:
        out[label] = {"result": "denied", "errno": exc.errno, "detail": exc.strerror}
s = socket.socket(fileno=SOCK)
def recvline():
    b = bytearray()
    while True:
        ch = s.recv(1)
        if not ch: break
        if ch == b"\n": break
        b += ch
    return bytes(b)
s.sendall(b"READ\n")
out["initial_request"] = recvline().decode("utf-8", "replace")
# Keep the restricted process and channel alive until authorization was revoked.
time.sleep(0.1)
s.sendall(b"READ\n")
out["after_revoke_request"] = recvline().decode("utf-8", "replace")
print(json.dumps(out, sort_keys=True), flush=True)
'''

NEGATIVE = r'''
import json, os, sys
fd = int(sys.argv[1])
print(json.dumps({"pid": os.getpid(), "preopened_fd_bypass": repr(os.read(fd, 128))}, sort_keys=True))
'''


def recvline(sock):
    b = bytearray()
    while True:
        ch = sock.recv(1)
        if not ch:
            break
        if ch == b"\n":
            break
        b += ch
    return bytes(b)


def broker(path, client_fd, control_fd):
    client = socket.socket(fileno=client_fd)
    control = socket.socket(fileno=control_fd)
    authorized = True
    req = recvline(client)
    if req != b"READ":
        client.sendall(b"DENY bad-request\n")
        return 2
    if authorized:
        fd = os.open(path, os.O_RDONLY)
        try:
            data = os.read(fd, 256)
        finally:
            os.close(fd)
        client.sendall(b"OK " + data)
        control.sendall(b"READ_DONE\n")
    command = recvline(control)
    if command != b"REVOKE":
        client.sendall(b"DENY revoke-not-received\n")
        return 3
    authorized = False
    control.sendall(b"REVOKED\n")
    next_req = recvline(client)
    if next_req == b"READ" and not authorized:
        client.sendall(b"DENY authorization-revoked\n")
    else:
        client.sendall(b"DENY invalid-request\n")
    print(json.dumps({"first_request": req.decode(), "authorization_after_control": authorized,
                      "second_request": next_req.decode()}, sort_keys=True), flush=True)
    return 0


def add_allow_rule(libc, ruleset, path):
    if not os.path.exists(path):
        return
    fd = os.open(path, getattr(os, "O_PATH", 0o10000000) | os.O_CLOEXEC)
    try:
        class PathBeneath(ctypes.Structure):
            _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int)]
        rights = READ_FILE if os.path.isfile(path) else READ_FILE | READ_DIR
        rule = PathBeneath(rights, fd)
        if libc.syscall(SYS_ADD, ctypes.c_int(ruleset), ctypes.c_int(1),
                        ctypes.byref(rule), ctypes.c_uint(0)) != 0:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e), path)
    finally:
        os.close(fd)


def confine_before_exec():
    libc = ctypes.CDLL(None, use_errno=True)
    attr = ctypes.c_uint64(READ_FILE | READ_DIR)
    ruleset = libc.syscall(SYS_CREATE, ctypes.byref(attr), ctypes.c_size_t(ctypes.sizeof(attr)), ctypes.c_uint(0))
    if ruleset < 0:
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e), "landlock_create_ruleset")
    try:
        for path in ("/usr", "/lib", "/lib64", "/etc/ld.so.cache"):
            add_allow_rule(libc, ruleset, path)
        if libc.prctl(38, 1, 0, 0, 0) != 0:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e), "PR_SET_NO_NEW_PRIVS")
        if libc.syscall(SYS_RESTRICT, ctypes.c_int(ruleset), ctypes.c_uint(0)) != 0:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e), "landlock_restrict_self")
    finally:
        os.close(ruleset)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--broker":
        return broker(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    os.makedirs(ROOT, exist_ok=True)
    with open(TARGET, "wb") as f:
        f.write(CONTENT)
    try:
        os.unlink(ALIAS)
    except FileNotFoundError:
        pass
    os.symlink("target.txt", ALIAS)

    client_parent, client_broker = socket.socketpair()
    control_parent, control_broker = socket.socketpair()
    broker_proc = subprocess.Popen([sys.executable, __file__, "--broker", TARGET,
                                    str(client_broker.fileno()), str(control_broker.fileno())],
                                   pass_fds=(client_broker.fileno(), control_broker.fileno()),
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, close_fds=True)
    client_broker.close()
    control_broker.close()
    worker_proc = None
    output = broker_out = ""
    try:
        cmd = [sys.executable, "-S", "-c", WORKER, TARGET, ALIAS, str(client_parent.fileno())]
        worker_proc = subprocess.Popen(cmd, pass_fds=(client_parent.fileno(),), preexec_fn=confine_before_exec,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, close_fds=True)
        done = recvline(control_parent)
        control_parent.sendall(b"REVOKE\n")
        revoked = recvline(control_parent)
        output, _ = worker_proc.communicate(timeout=6)
        broker_out, _ = broker_proc.communicate(timeout=6)

        # Independent negative control: deliberately pass a preopened descriptor to a separate,
        # unconfined process. This descriptor is never passed to the Landlock child.
        fd = os.open(TARGET, os.O_RDONLY)
        try:
            neg = subprocess.run([sys.executable, "-S", "-c", NEGATIVE, str(fd)], pass_fds=(fd,),
                                 capture_output=True, text=True, timeout=3, check=False)
        finally:
            os.close(fd)
        record = {"status": "completed", "supervisor_received": done.decode(),
                  "supervisor_revocation_ack": revoked.decode(), "worker_exit": worker_proc.returncode,
                  "worker": json.loads(output.strip()), "broker_exit": broker_proc.returncode,
                  "broker": json.loads(broker_out.strip()), "separate_negative_control_exit": neg.returncode,
                  "separate_negative_control": json.loads(neg.stdout.strip()) if neg.stdout.strip() else neg.stderr.strip()}
        print(json.dumps(record, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc),
                          "worker_output": output, "broker_output": broker_out}, sort_keys=True))
        return 2
    finally:
        for proc in (worker_proc, broker_proc):
            if proc is not None and proc.poll() is None:
                proc.kill()
                proc.wait(timeout=2)
        client_parent.close()
        control_parent.close()


if __name__ == "__main__":
    raise SystemExit(main())