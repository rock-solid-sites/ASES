#!/usr/bin/env bash
set -euo pipefail
task_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
capture_root="${1:-/tmp/ases-f1-repair-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -- "$capture_root"
python3 "$task_dir/probe.py" --mode original --out "$capture_root/original"
original_status=0
python3 "$task_dir/check.py" "$capture_root/original" > "$capture_root/original-check.json" || original_status=$?
test "$original_status" -eq 1
python3 "$task_dir/probe.py" --mode repaired --out "$capture_root/repaired"
python3 "$task_dir/check.py" "$capture_root/repaired" --controls > "$capture_root/repaired-check.json"
python3 "$task_dir/probe.py" --mode mutant --out "$capture_root/mutant"
mutant_status=0
python3 "$task_dir/check.py" "$capture_root/mutant" > "$capture_root/mutant-check.json" || mutant_status=$?
test "$mutant_status" -eq 1
python3 - "$capture_root" <<'PY'
import json
from pathlib import Path
import sys
root = Path(sys.argv[1])
assert set(json.loads((root / 'original-check.json').read_text())['contract_violations']) == {'cold-missing', 'config-nonaccept'}
assert set(json.loads((root / 'mutant-check.json').read_text())['contract_violations']) == {'cold-missing'}
assert json.loads((root / 'repaired-check.json').read_text())['satisfies_tested_contract']
PY
# L5 remains sequenced after the independently checked F1 repair.
python3 "$task_dir/l5/probe.py" --out "$capture_root/l5"
python3 "$task_dir/l5/check.py" "$capture_root/l5" > "$capture_root/l5-check.json"
printf 'Completed bounded reproduction (including expected original/mutant violations): %s\n' "$capture_root"
