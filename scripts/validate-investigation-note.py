#!/usr/bin/env python3
"""Structural check for the experimental Projektor investigation-note format.

Usage: python scripts/validate-investigation-note.py path/to/note.md
Requires PyYAML (pip install PyYAML). No network or Projektor access required.
This checks record shape, NOT scientific validity or agent decisions.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML missing: install it with 'python -m pip install PyYAML'")

BLOCK = re.compile(r"^\`\`\`yaml[ \t]*\n(.*?)^\`\`\`[ \t]*$", re.MULTILINE | re.DOTALL)
OUTCOMES = {"success", "observed_failure", "inconclusive", "test_error"}
STATUSES = {"planned", "completed", "interrupted"}


def required_text(record, fields, label, errors):
    for field in fields:
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"{label}.{field}: required nonempty text")


def validate(content):
    errors = []
    records = []
    for index, match in enumerate(BLOCK.finditer(content), 1):
        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"YAML block {index}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"YAML block {index}: expected a mapping")
            continue
        records.append((index, data))
    states = [(i, d) for i, d in records if d.get("kind") == "state"]
    if len(states) != 1:
        errors.append(f"expected one kind: state YAML block; found {len(states)}")
    for index, record in records:
        kind = record.get("kind")
        label = f"block {index}"
        if kind == "state":
            required_text(record, ("original_goal", "acceptance"), label, errors)
        elif kind == "experiment":
            required_text(record, ("id", "question", "prediction", "decision_value"), label, errors)
            status = record.get("status")
            if status not in STATUSES:
                errors.append(f"{label}.status: expected one of {sorted(STATUSES)}")
            if status == "completed":
                outcome = record.get("outcome")
                if outcome not in OUTCOMES:
                    errors.append(f"{label}.outcome: expected one of {sorted(OUTCOMES)}")
                required_text(record, ("observation", "implication", "next_action"), label, errors)
            if status == "interrupted":
                required_text(record, ("observation",), label, errors)
        else:
            errors.append(f"{label}.kind: expected state or experiment")
    ids = [d.get("id") for _, d in records if d.get("kind") == "experiment"]
    if len(ids) != len(set(str(x) for x in ids)):
        errors.append("duplicate experiment id")
    return errors


def main(argv):
    if len(argv) != 2:
        sys.exit("Usage: validate-investigation-note.py note.md")
    try:
        content = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        sys.exit(f"Cannot read note: {exc}")
    errors = validate(content)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print("VALID investigation-note structure (semantic reasoning not checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
