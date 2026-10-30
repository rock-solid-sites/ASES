import ctypes, errno, json, os, platform, struct, sys

# Linux Landlock syscall probe, run only in this disposable child.
# x86_64 Linux syscall numbers; stop rather than guess on other architectures.
out = {"pid": os.getpid(), "uid": os.getuid(), "machine": platform.machine()}
if not sys.platform.startswith("linux") or platform.machine() not in ("x86_64", "amd64"):
    out.update(status="unsupported-platform-no-syscall-attempt")
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0)
libc = ctypes.CDLL(None, use_errno=True)
SYS_CREATE, SYS_RESTRICT = 444, 446
VERSION_FLAG = 1
abi = libc.syscall(SYS_CREATE, ctypes.c_void_p(), ctypes.c_size_t(0), ctypes.c_uint(VERSION_FLAG))
if abi < 0:
    e = ctypes.get_errno()
    out.update(status="abi-query-failed", errno=e, error=os.strerror(e))
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0)
out["abi"] = abi
if abi == 0:
    out.update(status="landlock-unavailable")
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0)
# Handle only read_file/read_dir to discriminate fresh path access.
handled = (1 << 2) | (1 << 3)
attr = struct.pack("Q", handled)
buf = ctypes.create_string_buffer(attr)
rsfd = libc.syscall(SYS_CREATE, ctypes.byref(buf), ctypes.c_size_t(len(attr)), ctypes.c_uint(0))
if rsfd < 0:
    e = ctypes.get_errno()
    out.update(status="ruleset-create-failed", errno=e, error=os.strerror(e))
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0)
out["ruleset_fd"] = rsfd
if libc.prctl(38, 1, 0, 0, 0) != 0: # PR_SET_NO_NEW_PRIVS
    e = ctypes.get_errno()
    out.update(status="no_new_privs-failed", errno=e, error=os.strerror(e))
    os.close(rsfd)
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0)
if libc.syscall(SYS_RESTRICT, ctypes.c_int(rsfd), ctypes.c_uint(0)) != 0:
    e = ctypes.get_errno()
    out.update(status="restrict-self-failed", errno=e, error=os.strerror(e))
else:
    out.update(status="empty-read-deny-ruleset-entered", result="restriction-entry-succeeded")
os.close(rsfd)
print(json.dumps(out, sort_keys=True))