#!/usr/bin/env python3
"""Secret-exposure scan for the Atria review evidence.

The API key is read in-process from ~/.secrets/atria.env. It is never passed as
a command-line argument, never written to disk, and never printed. Only counts
and verdicts are emitted.

Scanned surfaces:
  * every regular file under the evidence directory
  * the staged diff
  * the full diff of every commit made on top of the pinned source commit
"""

import re
import subprocess
import sys

from pathlib import Path

ED = Path(__file__).resolve().parent
REPO = ED.parents[4]
SECRET_PATH = Path.home() / ".secrets" / "atria.env"
SOURCE_COMMIT = "e2e3bc110b1370f3505aa0838990713520bf3f7c"
TOKEN_RE = re.compile(r"atr_[A-Za-z0-9]{16,}")


def load_key():
    if not SECRET_PATH.is_file():
        sys.exit("ERROR: secret file missing; cannot run the exact-value scan.")
    key = None
    for raw in SECRET_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if line.startswith("ATRIA_API_KEY="):
            value = line[len("ATRIA_API_KEY="):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            key = value
            break
    if not key:
        sys.exit("ERROR: ATRIA_API_KEY not defined; cannot run the exact-value scan.")
    return key


def git(args):
    proc = subprocess.run(
        ["git"] + args, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return proc.stdout, proc.returncode


def commits_on_top():
    out, rc = git(["rev-list", f"{SOURCE_COMMIT}..HEAD"])
    if rc != 0:
        return []
    return [c for c in out.decode().split() if c]


def main():
    key = load_key()
    key_bytes = key.encode("utf-8")

    exact_hits = 0
    token_hits = 0
    files_scanned = 0
    file_list = []

    for path in sorted(ED.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith(".pyc") or "__pycache__" in path.parts:
            continue
        data = path.read_bytes()
        files_scanned += 1
        file_list.append(path)
        if key_bytes in data:
            exact_hits += 1
            print(f"  EXACT-VALUE HIT IN FILE: {path.relative_to(REPO)}")
        for m in TOKEN_RE.finditer(data.decode("utf-8", "replace")):
            token_hits += 1
            print(f"  TOKEN PATTERN HIT IN FILE: {path.relative_to(REPO)}")

    print(f"files_under_ED={files_scanned}")

    # Staged diff
    staged, rc = git(["diff", "--cached"])
    staged_exact = key_bytes in staged
    staged_tokens = len(TOKEN_RE.findall(staged.decode("utf-8", "replace")))
    print(f"staged_diff_bytes={len(staged)} exact_hits={int(staged_exact)} token_hits={staged_tokens}")

    # Commit diffs
    commits = commits_on_top()
    print(f"commits_on_top_of_source={len(commits)}")
    for sha in commits:
        d, rc = git(["show", sha])
        e = key_bytes in d
        t = len(TOKEN_RE.findall(d.decode("utf-8", "replace")))
        print(f"  commit {sha} diff_bytes={len(d)} exact_hits={int(e)} token_hits={t}")
        if e:
            exact_hits += 1
        token_hits += t

    # Secret location must be outside the repo and untracked.
    try:
        secret_rel = SECRET_PATH.resolve().relative_to(REPO.resolve())
        inside = True
    except ValueError:
        secret_rel = None
        inside = False
    print(f"secret_file_inside_repo={inside} secret_file={SECRET_PATH}")
    listed, rc = git(["ls-files"])
    listed_paths = listed.decode().split()
    secret_tracked = any(".secrets" in p for p in listed_paths)
    print(f"any_.secrets_path_tracked_in_git={secret_tracked}")

    # Non-empty working-tree status must be confined to the evidence directory.
    status, rc = git(["status", "--porcelain"])
    lines = [l for l in status.decode().splitlines() if l.strip()]
    ED_REL = "docs/research/kernel-0/reviews/atria-dawn/"
    outside = []
    for line in lines:
        p = line[3:].strip().strip('"')
        if p.endswith("/"):
            continue
        if p.startswith(ED_REL):
            continue
        if "__pycache__" in p:
            continue
        outside.append(line)
    print(f"porcelain_lines={len(lines)} outside_ED={len(outside)}")
    for line in outside:
        print(f"  OUTSIDE_ED: {line}")

    total_exact = exact_hits + int(staged_exact) + (0 if inside else 0)
    total_token = token_hits + staged_tokens
    verdict = (
        "PASS"
        if total_exact == 0 and total_token == 0 and not outside
        and not inside and not secret_tracked
        else "FAIL"
    )
    print(f"TOTAL_EXACT_VALUE_HITS={total_exact}")
    print(f"TOTAL_TOKEN_PATTERN_HITS={total_token}")
    print(f"SECRET_SCAN={verdict} files={files_scanned}")


if __name__ == "__main__":
    main()
