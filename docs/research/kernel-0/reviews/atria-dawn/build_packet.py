#!/usr/bin/env python3
"""Build the clean-room review packet from a pinned commit object.

The packet contains exactly six files, in a fixed order, each wrapped in
neutral file-boundary markers. Nothing else is added: no commentary, no
prior-review material, no repository history, no issue discussion.

Source bytes are read from the git commit object (not the working tree) so the
packet is a function of the commit alone.
"""

import subprocess
import sys
from pathlib import Path

SOURCE_COMMIT = "e2e3bc110b1370f3505aa0838990713520bf3f7c"

FILES = [
    "docs/research/kernel-0/Kernel-0-Abstract-Semantics.md",
    "docs/research/kernel-0/Kernel-0-Verification-Obligations.md",
    "docs/research/kernel-0/Kernel-0-Finite-Model.md",
    "docs/research/kernel-0/kernel0_finite_model.py",
    "docs/research/kernel-0/kernel0_service.py",
    "docs/research/kernel-0/kernel0_realization_check.py",
]

ED = Path(__file__).resolve().parent
PACKET = ED / "packet.md"


def git_show_bytes(commit, path):
    """Return the exact bytes of <path> as stored in the commit object."""
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        sys.stderr.write(
            f"FATAL: git show {commit}:{path} failed "
            f"(rc={proc.returncode}): {proc.stderr.decode('utf-8', 'replace')}\n"
        )
        raise SystemExit(1)
    return proc.stdout


def section(path, data):
    """One wrapped section: BEGIN marker, exact bytes, END marker."""
    if not data.endswith(b"\n"):
        data = data + b"\n"
    return (
        f"===== BEGIN FILE: {path} =====\n".encode("utf-8")
        + data
        + f"===== END FILE: {path} =====\n".encode("utf-8")
    )


def build(commit=SOURCE_COMMIT, files=FILES):
    sections = [section(p, git_show_bytes(commit, p)) for p in files]
    # Exactly one blank line between sections; packet ends with exactly one \n.
    return b"\n".join(sections)


def main():
    packet = build()
    PACKET.write_bytes(packet)
    print(f"PACKET_PATH={PACKET}")
    print(f"PACKET_BYTES={len(packet)}")
    for p in FILES:
        print(f"  {p} {len(git_show_bytes(SOURCE_COMMIT, p))}")


if __name__ == "__main__":
    main()
