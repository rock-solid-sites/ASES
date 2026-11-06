#!/usr/bin/env bash
# Research reproduction only. Writes a new capture; never switches/modifies branches.
set -euo pipefail
investigation_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
capture_root="${1:-/tmp/ases-sol-replay-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -- "$capture_root"
python3 - "$investigation_dir" <<'PY'
from pathlib import Path
import runpy
import subprocess
import sys
task = Path(sys.argv[1])
repo = task.parents[2]
pins = runpy.run_path(str(task / 'native.py'))['PINS']
for commit, *_ in pins.values():
    if subprocess.run(['git', 'cat-file', '-e', commit + '^{commit}'], cwd=repo,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        subprocess.run(['git', 'fetch', 'origin', commit], cwd=repo, check=True)
PY
python3 "$investigation_dir/native.py" --out "$capture_root/integration"
python3 "$investigation_dir/native.py" --recovery-only --out "$capture_root/recovery"
python3 "$investigation_dir/observe.py" "$capture_root/integration" "$capture_root/recovery" > "$capture_root/evaluation.json"
printf 'Capture and findings: %s\n' "$capture_root"
