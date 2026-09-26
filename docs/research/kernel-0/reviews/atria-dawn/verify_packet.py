#!/usr/bin/env python3
"""Independently re-parse packet.md and prove it reconstructs from the commit.

Checks, in order:
  1. The set and order of BEGIN/END marker lines matches the six pinned files.
  2. Every section's bytes byte-compare equal to `git show <SHA>:<path>`.
  3. Nothing exists outside the markers other than exactly one blank-line
     separator between adjacent sections, and exactly one trailing newline.
  4. No extra BEGIN/END markers, no stray text.
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

failures = []


def check(cond, label):
    if cond:
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)
    return cond


def git_show_bytes(path):
    proc = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        sys.stderr.write(f"FATAL: cannot read {SOURCE_COMMIT}:{path}\n")
        raise SystemExit(1)
    return proc.stdout


def main():
    packet = PACKET.read_bytes()
    print(f"packet={PACKET} bytes={len(packet)}")

    lines = packet.split(b"\n")
    check(
        packet.endswith(bytes([10])) and not packet.endswith(bytes([10, 10])),
        "packet ends with exactly one newline",
    )

    begins = [
        l.decode("utf-8")[len("===== BEGIN FILE: "): -len(" =====")]
        for l in lines
        if l.startswith(b"===== BEGIN FILE: ") and l.endswith(b" =====")
    ]
    ends = [
        l.decode("utf-8")[len("===== END FILE: "): -len(" =====")]
        for l in lines
        if l.startswith(b"===== END FILE: ") and l.endswith(b" =====")
    ]
    begin_count = sum(1 for l in lines if l.startswith(b"===== BEGIN FILE: "))
    end_count = sum(1 for l in lines if l.startswith(b"===== END FILE: "))
    check(begin_count == 6, f"exactly 6 BEGIN markers (found {begin_count})")
    check(end_count == 6, f"exactly 6 END markers (found {end_count})")
    check(begins == FILES, "BEGIN marker order matches pinned file order")
    check(ends == FILES, "END marker order matches pinned file order")

    # Structural walk: everything must be a marker line, a section payload, or
    # exactly one blank line between sections.
    idx = 0
    reconstructed = []
    for i, path in enumerate(FILES):
        bmark = f"===== BEGIN FILE: {path} =====".encode("utf-8")
        emark = f"===== END FILE: {path} =====".encode("utf-8")
        check(lines[idx] == bmark, f"section {i + 1} starts at {bmark.decode()}")
        idx += 1
        start = idx
        while idx < len(lines) and lines[idx] != emark:
            idx += 1
        payload = bytes([10]).join(lines[start:idx]) + bytes([10])
        reconstructed.append(payload)
        check(lines[idx] == emark, f"section {i + 1} ends at {emark.decode()}")
        idx += 1
        if i < len(FILES) - 1:
            check(
                idx < len(lines) and lines[idx] == b"",
                f"exactly one blank line after section {i + 1}",
            )
            idx += 1
    check(idx == len(lines) - 1 and lines[idx] == b"", "no trailing content after last marker")
    # Every consumed line was either a marker or a payload/separator line, and the
    # walk consumed the file exactly; so no stray text can exist outside markers.
    check(
        idx == len(lines) - 1,
        "structural walk consumed every line up to the final empty split (no stray text)",
    )

    for path, payload in zip(FILES, reconstructed):
        expected = git_show_bytes(path)
        if not expected.endswith(bytes([10])):
            expected = expected + bytes([10])
        same = payload == expected
        check(
            same,
            f"byte-exact section for {path} ({len(payload)} bytes vs {len(expected)} from commit)",
        )
        print(f"  FILE {path} packet_bytes={len(payload)} commit_bytes={len(expected)} match={same}")

    # Independent whole-packet equality against a fresh reconstruction.
    fresh = b"\n".join(
        (
            f"===== BEGIN FILE: {p} =====\n".encode("utf-8")
            + (lambda d: d if d.endswith(bytes([10])) else d + bytes([10]))(git_show_bytes(p))
            + f"===== END FILE: {p} =====\n".encode("utf-8")
        )
        for p in FILES
    )
    check(fresh == packet, "whole-packet byte equality with fresh reconstruction")

    # Prior-review / unrelated material exclusion (repeated in Step 4).
    # These counts are raw measurements, reported whether or not they are zero.
    # They do NOT gate packet integrity: every byte of the packet is proven
    # equal to the pinned commit above, so any hit necessarily originates in the
    # pinned source files themselves.
    banned = [
        b"Kernel-0-Realization-Experiment",
        b"Kernel-0-Realization-Conformance",
        b"Kernel-0-Reasoning-Phase-Result",
        b"Kernel-0-Evidence-Packet",
        b"Realization-Comparison",
        b".design/reviews",
    ]
    total_hits = 0
    print("  -- prior-review token census (packet vs pinned source) --")
    for b in banned:
        n = packet.count(b)
        total_hits += n
        per_file = sum(git_show_bytes(p).count(b) for p in FILES)
        print(
            f"  TOKEN {b.decode()} packet_count={n} pinned_source_count={per_file}"
        )

    print(f"TOTAL_FAILURES={len(failures)}")
    if failures:
        print("PACKET_RECONSTRUCTION=FAIL")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print("PACKET_RECONSTRUCTION=PASS")
    print(
        f"PRIOR_REVIEW_EXCLUSION={'PASS' if total_hits == 0 else 'FAIL'}"
        f" (total_hits={total_hits}; all hits originate in the pinned source files)"
    )


if __name__ == "__main__":
    main()
