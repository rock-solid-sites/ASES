#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
task_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
out="${1:-$task_dir/evidence/cloud-$(date -u +%Y%m%dT%H%M%SZ)}"
python3 -B "$task_dir/probe.py" --out "$out"
python3 -B "$task_dir/check.py" "$out/raw.json" > "$out/evaluation.json"
gzip -c "$out/raw.json" > "$out/raw.json.gz"
printf 'Capture and independent evaluation: %s\n' "$out"
