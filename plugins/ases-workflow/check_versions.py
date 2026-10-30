#!/usr/bin/env python3
"""Compare pinned ASES workflow skill blobs to canonical GitHub without executing remote content."""
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = pathlib.Path(__file__).with_name("sources.json")
BASE = "https://raw.githubusercontent.com/rock-solid-sites/ASES/"
TIMEOUT = 12

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def main():
    manifest = json.loads(MANIFEST.read_text())
    ref = manifest["source_commit"]
    failures = []
    for skill in manifest["skills"]:
        path = skill["path"]
        local = ROOT / path
        if not local.is_file():
            failures.append(f"MISSING {path}")
            continue
        data = local.read_bytes()
        if sha256(data) != skill["sha256"]:
            failures.append(f"LOCAL_CHANGED {path}")
            continue
        url = BASE + "main/" + path
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
                latest = response.read(262145)
            if len(latest) > 262144:
                raise ValueError("file too large")
            if sha256(latest) != skill["sha256"]:
                failures.append(f"UPDATE_AVAILABLE {path}")
            else:
                print(f"CURRENT {path}")
        except (OSError, ValueError, urllib.error.URLError) as exc:
            failures.append(f"CHECK_BLOCKED {path}: {type(exc).__name__}")
    print(f"Pinned source commit: {ref}")
    for failure in failures:
        print(failure)
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
