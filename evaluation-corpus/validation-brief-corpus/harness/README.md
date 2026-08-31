# Harness — Validation Brief Corpus

**Purpose:** Thin, reusable harness for the `validation-brief-corpus` (issue #530). It validates corpus integrity and provides a minimal runner for model-agnostic comparison — it does **not** implement the EDASES methodology.

## Layout

```
harness/
├── README.md      # This file
├── validate.py    # Corpus validator: manifest ↔ corpus.jsonl ↔ files
├── scoring.md     # Rubric
└── run.py         # Thin runner: ingest corpus.jsonl, emit results.jsonl (and compare)
```

## Quick start

```bash
# 1. Validate corpus integrity (no model needed)
python evaluation-corpus/validation-brief-corpus/harness/validate.py
# Checks: manifest ↔ corpus.jsonl ↔ files, ID uniqueness, schema, expected_recovery presence, frontmatter validity

# 2. Validate corpus.jsonl is well-formed JSONL
python -c "import json; [json.loads(l) for l in open('evaluation-corpus/validation-brief-corpus/corpus.jsonl')]; print('JSONL OK')"

# 3. Run against a system under test (SUT) — thin runner
python evaluation-corpus/validation-brief-corpus/harness/run.py \
  --corpus evaluation-corpus/validation-brief-corpus/corpus.jsonl \
  --out /tmp/results.jsonl

# 4. Compare two runs (model A vs model B, or before/after)
python evaluation-corpus/validation-brief-corpus/harness/run.py \
  --compare /tmp/run-a.jsonl /tmp/run-b.jsonl \
  --out /tmp/delta.md
```

## What the harness does and does not do

- **Does:** Validate that the corpus is well-formed, ingest `corpus.jsonl` one record at a time, emit a `results.jsonl` with per-brief pass/fail per criterion (the SUT is expected to implement the actual task; the harness only checks outputs against `manifest.json` expected values for malformed/adversarial, and checks file existence/content for well-formed).
- **Does not:** Implement artefact lifecycle, provenance, workflow gates, or any methodology. The methodology lives in the SUT; the harness is a checker.

## For EDASES comparison

Same corpus + same harness → different SUTs → delta in `results.jsonl` is the comparison signal. Always report **per-class** deltas (AL/PE/WV/KD/OO/SR), not just total, to locate where enforcement diverges.

## Dependencies

- Python 3.10+
- `pyyaml` for frontmatter validation (`pip install pyyaml`) — if absent, `validate.py` falls back to a minimal parser and warns.

## WHAT-NOT-TESTED

- `validate.py` does not run the tasks — it only checks corpus integrity.
- `run.py` in this corpus is a **stub runner** that emits `not_run` for each brief; a real SUT integration replaces the `TODO` in `run.py` with actual system calls. The stub is intentional: it makes the harness runnable without a SUT while making the integration point explicit.
