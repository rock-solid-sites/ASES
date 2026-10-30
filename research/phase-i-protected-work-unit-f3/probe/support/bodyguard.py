"""bodyguard — an engine-independent enforcement point used for the F3 probe.

It creates the two activity processes with PR_SET_PDEATHSIG=SIGKILL, so if the
engine dies the kernel kills the activity children regardless of what the engine
itself had time to record. That is the one piece of *real* host-level
enforcement the probe exercises; it is still confined to processes this probe
created.

usage: bodyguard.py ROOT PROXY DENY=... RO=...
"""
import ctypes
import os
import signal
import subprocess
import sys
import time

PR_SET_PDEATHSIG = 1
libc = ctypes.CDLL(None, use_errno=True)
HERE = os.path.dirname(os.path.abspath(__file__))


def preexec():
    # runs in the child after fork, before exec: arm the parent-death kill
    libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0)


def main():
    root, proxy = sys.argv[1], sys.argv[2]
    deny, ro = sys.argv[3], sys.argv[4]
    children = []
    # The proxy serves the engine's activity; it is created and owned by the
    # bodyguard, never by the engine, so engine death does not remove it either.
    # (The activity itself is created by the engine, with the engine as parent,
    # so PR_SET_PDEATHSIG anchors the activity's death to the *engine*.)
    children.append(subprocess.Popen(
        [sys.executable, os.path.join(HERE, "acl_proxy.py"), root, proxy, deny, ro],
        preexec_fn=preexec))
    print("BODYGUARD READY %d %d" % (children[0].pid, children[1].pid), flush=True)
    try:
        while True:
            time.sleep(0.2)
            if any(c.poll() is not None for c in children):
                print("BODYGUARD CHILD-EXITED", flush=True)
                return 0
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
