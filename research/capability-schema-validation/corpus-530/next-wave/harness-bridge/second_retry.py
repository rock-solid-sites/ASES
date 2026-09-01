#!/usr/bin/env python3
"""Second-retry harness for corpus-530 recovery — scaffolding only, no live model call.

On minLength/pattern empty-string failures, second retry with full constraint text
(field + constraint + message + similar valid example) without exposing full schema.

Usage:
  python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --self-test
  python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --check-examples
  python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --dry-enrich --field query --constraint minLength --got '""'
  python research/capability-schema-validation/corpus-530/next-wave/harness-bridge/second_retry.py --dry-enrich --field evidence_items.0.content --constraint minLength --got '""'

Design is in ../SECOND_RETRY.md. No full schema is ever leaked in the enriched prompt.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
NEXT_WAVE = HERE.parent
CORPUS_530 = NEXT_WAVE.parent
# load corpus for example picker
TASKS_PATH = CORPUS_530 / "tasks.json"
MALFORMED_PATH = CORPUS_530 / "malformed-recovery.json"

# Deterministic example map — field path suffix -> valid example value
# Sourced from malformed-recovery.json corrected_args and tasks.json expected_args
EXAMPLES: dict[str, str] = {
    # field name or suffix -> single example value (stringified for prompt)
    "query": "hello",
    "id": "art_abc-123",
    "artefact_id": "art_abc-123",
    "source_id": "art_abc-123",
    "target_ids": '["art_def-456"]',  # will be unwrapped per prompt formatter
    "content": "evidence text from experiment",
    "evidence_items": '[{"source": "paper", "content": "evidence text from experiment"}]',
    "evidence_items.0.content": "evidence text from experiment",
    "rationale": "This rationale has enough length to pass hidden minLength ten",
    "reason": "superseded by new design for clarity",
    "title": "My Spec",
    "cursor": "cur_abc123",
    "limit": "20",
}

# Trigger predicate: constraints that with empty string warrant second retry
TRIGGER_CONSTRAINTS = {"minLength", "pattern"}


def should_second_retry(error: dict | None, args_corrected: dict | None = None, corrected_got: str | None = None) -> bool:
    """Return True iff second retry should fire for this ValidationFailed error.

    error is the runtime error dict: {code, field, constraint, got, message, ...}
    corrected_got is the json.dumps of the failing field's corrected value (or error['got']).
    For scaffolding tests, we treat '""' as empty-string signal.
    """
    if not error or error.get("code") != "ValidationFailed":
        return False
    constraint = error.get("constraint")
    if constraint not in TRIGGER_CONSTRAINTS:
        return False
    # got is the value that failed validation; for first retry empty-string corrections, got == '""'
    got = error.get("got")
    # Normalize: if args_corrected provided, we can derive got from field-dotted path, but we trust error.got
    # Allow caller to override via corrected_got
    if corrected_got is not None:
        got = corrected_got
    # Detect empty string: json.dumps("") == '""'
    # Also accept plain "" or "'' should be non-empty" message signal
    if got == '""' or got == "" or got == "''":
        return True
    # Also check args_corrected directly if error.got is missing/empty-ish
    if args_corrected is not None and error.get("field"):
        # resolve dotted path suffix
        field = error["field"]
        # last segment
        last = field.split(".")[-1]
        # try to find that key in args_corrected at any nesting — shallow check
        # For evidence_items.0.content we look for content emptiness
        val = None
        # Simple resolver: walk dotted ignoring numeric indices
        try:
            cur: object = args_corrected
            for part in field.split("."):
                if part.isdigit():
                    if isinstance(cur, list):
                        cur = cur[int(part)]
                    else:
                        cur = None  # type: ignore[assignment]
                        break
                elif isinstance(cur, dict):
                    cur = cur.get(part)  # type: ignore[assignment]
                else:
                    cur = None  # type: ignore[assignment]
                    break
            val = cur
        except Exception:  # noqa: BLE001
            val = None  # type: ignore[assignment]
        if val == "":
            return True
        # also flat lookup fallback
        if last in args_corrected and args_corrected[last] == "":
            return True
    return False


def pick_example(field: str) -> str:
    """Pick a similar valid example for field path without exposing schema.

    Uses deterministic map; falls back to generic. No schema excerpt is returned.
    """
    # exact suffix match first (longest key)
    for key in sorted(EXAMPLES, key=len, reverse=True):
        if field == key or field.endswith("." + key) or field.endswith(key):
            return EXAMPLES[key]
        # also match last segment
        if field.split(".")[-1] == key:
            return EXAMPLES[key]
    return "valid non-empty text"


def build_second_retry_prompt(
    field: str,
    constraint: str,
    message: str,
    got: str,
    parent_prompt_hint: str | None = None,  # unused but kept for signature parity
) -> str:
    """Build the second-retry enrichment text (no full schema, at most 3 new sentences)."""
    example = pick_example(field)
    # Format example as JSON-ish single-field snippet for prompt clarity
    # Do not leak schema; only field + valid example
    if field in ("target_ids", "evidence_items"):
        example_snippet = example  # already JSON-like
    elif "." in field and "content" in field:
        example_snippet = json.dumps(example)
    else:
        # Use json.dumps for string examples so quotes are visible
        example_snippet = json.dumps(example) if isinstance(example, str) and not example.startswith("[") and not example.startswith("{") else example
    lines = [
        f'## Second Retry — Full Constraint for Field "{field}"',
        "",
        "The previous correction failed with empty string.",
        "",
        f'- Field: "{field}"',
        f"- Constraint: {constraint}",
        f"- Runtime message: {message}",
        "- Example valid value for this field (from corpus, not schema):",
        f"  {example_snippet}",
        "",
        f'Instruction: Replace the empty string for field "{field}" with a substantive, non-empty value matching the example\'s shape (do NOT copy the example verbatim if it contains a specific identifier; generate a plausible value of similar shape). Keep all other fields unchanged; do not invent unrelated params. Respond with JSON {{"op_id":"...","arguments":{{...}}}}.',
    ]
    return "\n".join(lines)


def enrichment_exposes_schema(enrichment: str) -> bool:
    """Guard: ensure enrichment never leaks full schema markers."""
    banned = ["$schema", '"inputSchema"', '"outputSchema"', '"additionalProperties"', '"properties":', '"$defs"', '"allOf"']
    low = enrichment.lower()
    for b in banned:
        if b.lower() in low:
            return True
    # also reject if enrichment contains a full JSON Schema block (heuristic: has both type string and pattern length markers together in schema-like JSON)
    # we allow example snippets that contain type-like fields in evidence_items arrays — those are not schema.
    return False


# --- self-tests (no live call) ---


def self_test() -> int:
    print("second_retry self-test (no live model, no network)")
    # R01, R05, R10 should trigger second retry: minLength + got '""'
    cases_trigger = [
        {"field": "query", "constraint": "minLength", "got": '""', "expected": True},
        {"field": "evidence_items.0.content", "constraint": "minLength", "got": '""', "expected": True},
        {"field": "rationale", "constraint": "minLength", "got": '""', "expected": True},
        # pattern empty not observed live but should trigger if empty
        {"field": "id", "constraint": "pattern", "got": '""', "expected": True},
    ]
    # Should NOT trigger: enum, type, required, maximum, or non-empty got
    cases_no = [
        {"field": "type", "constraint": "enum", "got": '"invalid"', "expected": False},
        {"field": "query", "constraint": "type", "got": "123", "expected": False},
        {"field": "limit", "constraint": "maximum", "got": "999", "expected": False},
        {"field": "query", "constraint": "required", "got": "{}", "expected": False},
        {"field": "query", "constraint": "minLength", "got": '"hello"', "expected": False},
    ]
    failed = 0
    for c in cases_trigger + cases_no:
        err = {"code": "ValidationFailed", "field": c["field"], "constraint": c["constraint"], "got": c["got"], "message": "stub", "boundary": "runtime"}
        got_trigger = should_second_retry(err)
        ok = got_trigger == c["expected"]
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"  {status}: should_second_retry field={c['field']} constraint={c['constraint']} got={c['got']} -> {got_trigger} expected={c['expected']}")
    # prompt builder non-schema leak check
    for field in ["query", "evidence_items.0.content", "rationale", "id"]:
        msg = "'' should be non-empty" if field != "id" else "'BAD_ID' does not match '^art_[a-z0-9-]+$'"
        prompt = build_second_retry_prompt(field, "minLength" if field != "id" else "pattern", "minLength" if field != "id" else "pattern", '""',)
        # we pass message via prompt builder; message is not used directly in prompt except as line — use actual message
        # rebuild with proper message
        prompt = build_second_retry_prompt(field, "minLength" if field != "id" else "pattern", msg, '""')
        if enrichment_exposes_schema(prompt):
            print(f"  FAIL: enrichment leaks schema for field {field}")
            failed += 1
        else:
            print(f"  PASS: enrichment clean for field {field} example={pick_example(field)[:40]!r}")
        if pick_example(field) == "valid non-empty text" and field not in ("query", "rationale"):
            # query/rationale have map entries; id has art_abc-123
            pass
    # example picker covers known failure fields
    for f in ["query", "evidence_items.0.content", "rationale"]:
        ex = pick_example(f)
        if ex == "valid non-empty text":
            print(f"  FAIL: example missing for known failing field {f}")
            failed += 1
        else:
            print(f"  PASS: example for {f} -> {ex[:40]!r}")
    print(f"self-test: {0 if failed == 0 else failed} failures")
    return 1 if failed else 0


def check_examples() -> int:
    print("check-examples (guard that enrichment never leaks full schema)")
    # simulate enrichments for all mapped fields
    failures = 0
    for field in list(EXAMPLES.keys()) + ["unknown_field_xyz"]:
        prompt = build_second_retry_prompt(field, "minLength", "'' should be non-empty", '""')
        if enrichment_exposes_schema(prompt):
            print(f"  FAIL: field={field} leaks schema")
            failures += 1
        else:
            print(f"  PASS: field={field} clean, example={pick_example(field)[:50]!r}")
    # verify no authoritative.json block slipped
    if (CORPUS_530 / "schemas" / "authoritative.json").exists():
        auth = (CORPUS_530 / "schemas" / "authoritative.json").read_text()
        assert '"$schema"' in auth
        # check that our prompts never include that
        sample = build_second_retry_prompt("query", "minLength", "'' should be non-empty", '""')
        assert '"$schema"' not in sample
        print("  PASS: authoritative.json contains $schema but enrichment does not")
    print(f"check-examples: {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Second-retry harness (scaffolding)")
    ap.add_argument("--self-test", action="store_true", help="run self-test")
    ap.add_argument("--check-examples", action="store_true", help="check examples and schema-leak guard")
    ap.add_argument("--dry-enrich", action="store_true", help="print enriched prompt for given field/constraint/got")
    ap.add_argument("--field", type=str, default="query")
    ap.add_argument("--constraint", type=str, default="minLength")
    ap.add_argument("--got", type=str, default='""')
    ap.add_argument("--message", type=str, default=None)
    args = ap.parse_args()

    if args.self_test:
        raise SystemExit(self_test())
    if args.check_examples:
        raise SystemExit(check_examples())
    if args.dry_enrich:
        msg = args.message or ("'' should be non-empty" if args.constraint == "minLength" else "'BAD_ID' does not match '^art_[a-z0-9-]+$'")
        print(build_second_retry_prompt(args.field, args.constraint, msg, args.got))
        if enrichment_exposes_schema(build_second_retry_prompt(args.field, args.constraint, msg, args.got)):
            print("\n[WARN] enrichment would leak schema — check EXAMPLES map", file=sys.stderr)
        raise SystemExit(0)
    ap.print_help()
