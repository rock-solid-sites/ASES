import ctypes, json, os, platform, socket, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "fixture")
TARGET = os.path.join(ROOT, "attached.txt")
ALIAS = os.path.join(ROOT, "alias.txt")
CONTENT = b"landlock-disposable-attachment\n"
SYS_CREATE, SYS_RESTRICT = 444, 446
READ_FILE, READ_DIR = 1 << 2, 1 << 3


def mediator(path, sockfd):
    s = socket.socket(fileno=sockfd)
    request = s.recv(128)
    if request != b"READ\n":
        s.sendall(b"ERR bad-request\n")
        return 2
    try:
        fd = os.open(path, os.O_RDONLY)
        try:
            data = os.read(fd, 256)
        finally:
            os.close(fd)
        s.sendall(b"OK " + data)
        return 0
    except OSError as exc:
        s.sendall(("ERR errno=%d %s\n" % (exc.errno, exc.strerror)).encode())
        return 1


def worker(path, alias, retained_fd, sockfd):
    out = {"pid": os.getpid()}
    libc = ctypes.CDLL(None, use_errno=True)
    handled = READ_FILE | READ_DIR
    attr = ctypes.create_string_buffer(handled.to_bytes(8, "little"))
    ruleset = libc.syscall(SYS_CREATE, ctypes.byref(attr), ctypes.c_size_t(8), ctypes.c_uint(0))
    if ruleset < 0:
        e = ctypes.get_errno()
        out["landlock_setup"] = {"error": e, "detail": os.strerror(e)}
        print(json.dumps(out, sort_keys=True), flush=True)
        return 2
    if libc.prctl(38, 1, 0, 0, 0) != 0:
        e = ctypes.get_errno()
        out["no_new_privs"] = {"error": e, "detail": os.strerror(e)}
        os.close(ruleset)
        print(json.dumps(out, sort_keys=True), flush=True)
        return 2
    if libc.syscall(SYS_RESTRICT, ctypes.c_int(ruleset), ctypes.c_uint(0)) != 0:
        e = ctypes.get_errno()
        out["landlock_restrict"] = {"error": e, "detail": os.strerror(e)}
        os.close(ruleset)
        print(json.dumps(out, sort_keys=True), flush=True)
        return 2
    os.close(ruleset)
    out["landlock_restrict"] = "entered ABI-1 empty read_file/read_dir policy"

    for name, candidate in (("direct_target", path), ("symlink_alias", alias)):
        try:
            fd = os.open(candidate, os.O_RDONLY)
            try:
                out[name] = {"result": "allowed", "bytes": repr(os.read(fd, 256))}
            finally:
                os.close(fd)
        except OSError as exc:
            out[name] = {"result": "denied", "errno": exc.errno, "detail": exc.strerror}

    try:
        os.lseek(retained_fd, 0, os.SEEK_SET)
        out["retained_preopened_fd"] = {"result": "readable", "bytes": repr(os.read(retained_fd, 256))}
    except OSError as exc:
        out["retained_preopened_fd"] = {"result": "error", "errno": exc.errno, "detail": exc.strerror}

    s = socket.socket(fileno=sockfd)
    s.sendall(b"READ\n")
    s.shutdown(socket.SHUT_WR)
    response = b""
    while True:
        block = s.recv(256)
        if not block:
            break
        response += block
    out["per_operation_mediator"] = response.decode("utf-8", "replace").strip()
    print(json.dumps(out, sort_keys=True), flush=True)
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--mediator":
        return mediator(sys.argv[2], int(sys.argv[3]))
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        return worker(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))

    if not sys.platform.startswith("linux") or platform.machine() not in ("x86_64", "amd64"):
        print(json.dumps({"status": "unsupported-platform-no-syscall-attempt", "machine": platform.machine()}))
        return 0
    os.makedirs(ROOT, exist_ok=True)
    with open(TARGET, "wb") as f:
        f.write(CONTENT)
    try:
        os.unlink(ALIAS)
    except FileNotFoundError:
        pass
    os.symlink("attached.txt", ALIAS)

    retained = os.open(TARGET, os.O_RDONLY)
    left, right = socket.socketpair()
    mediator_proc = subprocess.Popen([sys.executable, __file__, "--mediator", TARGET, str(right.fileno())],
                                     pass_fds=(right.fileno(),), stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True, close_fds=True)
    right.close()
    worker_proc = None
    try:
        worker_proc = subprocess.Popen([sys.executable, __file__, "--worker", TARGET, ALIAS,
                                        str(retained), str(left.fileno())],
                                       pass_fds=(retained, left.fileno()), stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, close_fds=True)
        left.close()
        output, _ = worker_proc.communicate(timeout=4)
        mediator_output, _ = mediator_proc.communicate(timeout=4)
        print(json.dumps({"status": "completed", "worker_exit": worker_proc.returncode,
                          "worker_observation": json.loads(output.strip()),
                          "mediator_exit": mediator_proc.returncode,
                          "mediator_stdout": mediator_output.strip()}, sort_keys=True))
        return 0
    except subprocess.TimeoutExpired:
        for proc in (worker_proc, mediator_proc):
            if proc is not None and proc.poll() is None:
                proc.kill()
        print(json.dumps({"status": "timeout", "timeout_seconds": 4}))
        return 124
    finally:
        if worker_proc is not None and worker_proc.poll() is None:
            worker_proc.kill()
            worker_proc.wait(timeout=2)
        if mediator_proc.poll() is None:
            mediator_proc.kill()
            mediator_proc.wait(timeout=2)
        os.close(retained)
        try:
            left.close()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())