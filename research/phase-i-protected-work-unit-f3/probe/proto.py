"""F3 cheapest boundary probe: shared protocol vocabulary.

All processes in this probe live inside ONE disposable root created under the
worktree. Nothing here inspects or depends on host state.
"""
DISPATCH = b"\x1e\x00"   # ASCII RS + NUL

def recv_line(sock):
    buf = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            raise EOFError
        if ch == b"\n":
            return buf.decode("utf-8", "replace")
        buf += ch

def op(engine_path, sub, *rest, prefix=True):
    """An activity-issued request: [prefix?] OP sub [args...]."""
    parts = [("!" if prefix else "") + sub] + [str(r) for r in rest]
    return "\x1d".join(parts)
