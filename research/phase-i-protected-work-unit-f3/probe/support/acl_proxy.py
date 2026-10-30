"""acl_proxy — the concrete access-control point for the F3 probe.

Listens on a filesystem UNIX socket inside the disposable root. The activity
issues requests on that socket; the proxy resolves them *as the holder of
superior authority* and answers on the activity's behalf.

The policy is the one deliberate concrete ACL in this probe:

  OPEN rel flags   -> canonicalise ROOT/rel; must stay inside ROOT; no path
                      component may be in DENY; if the canonical path lies in a
                      READ-ONLY subtree, flags must contain no write/creat/trunc.
  STAT rel         -> canonicalise; inside ROOT; no DENY component.
  READDIR rel      -> same as STAT.

The proxy deliberately only mediates *its own socket*. It does not, and by
construction cannot, police relative paths that an activity hands to a sibling
process which resolves them in its own working directory. Section 4 of the
report treats that as a real, expected bypass of the claim.

usage: acl_proxy.py ROOT SOCK DENY=<comp>,<comp> RO=<subtree>,<subtree>
"""
import os
import socket
import struct
import sys

WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND


def inside(path, root):
    return path == root or path.startswith(root + "/")


def denied(canon, root, deny):
    rel = canon[len(root):].strip("/")
    return [c for c in rel.split("/") if c in deny]


def resolve(root, rel, deny):
    joined = os.path.join(root, rel)
    canon = os.path.realpath(joined)
    if not inside(canon, root) or canon == root:
        return None, "FAIL ESCAPE"
    if denied(canon, root, deny):
        return None, "FAIL DENY-COMPONENT"
    return canon, None


def serve_conn(conn, root, deny, ro):
    try:
        for line in conn.makefile("r", newline="\n"):
            parts = line.rstrip("\n").split("\x1d")
            cmd = parts[0]
            code, payload = "ERR", "unknown"
            if cmd == "OPEN":
                flags = int(parts[2]) if len(parts) > 2 else os.O_RDONLY
                canon, err = resolve(root, parts[1], deny)
                if err:
                    code, payload = "FAIL", err
                elif any(inside(canon, r) for r in ro) and flags & WRITE_FLAGS:
                    code, payload = "FAIL", "FAIL ACL-RO"
                else:
                    try:
                        fd = os.open(canon, flags & ~(os.O_CREAT | os.O_EXCL), 0)
                    except OSError as exc:
                        code, payload = "FAIL", "FAIL ACL-OPEN(%s)" % exc.strerror
                    else:
                        code, payload = "OK", str(fd)
                        os.close(fd)
            elif cmd in ("STAT", "READDIR"):
                canon, err = resolve(root, parts[1], deny)
                if err:
                    code, payload = "FAIL", err
                else:
                    try:
                        if cmd == "STAT":
                            code, payload = "OK", str(os.stat(canon).st_size)
                        else:
                            code, payload = "OK", " ".join(sorted(os.listdir(canon)))
                    except OSError as exc:
                        code, payload = "FAIL", "FAIL ACL-%s(%s)" % (cmd, exc.strerror)
            conn.sendall(("%s %s\n" % (code, payload)).encode())
    except (BrokenPipeError, ConnectionResetError):
        pass
    finally:
        conn.close()


def main():
    root, sock_path, deny_spec, ro_spec = sys.argv[1:5]
    root = os.path.realpath(root)
    deny = {c for c in deny_spec.split(",") if c}
    ro = [os.path.realpath(os.path.join(root, p)) for p in ro_spec.split(",") if p]
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        os.unlink(sock_path)
    except FileNotFoundError:
        pass
    srv.bind(sock_path)
    srv.listen(8)
    while True:
        try:
            conn, _ = srv.accept()
        except InterruptedError:
            continue
        serve_conn(conn, root, deny, ro)


if __name__ == "__main__":
    main()
