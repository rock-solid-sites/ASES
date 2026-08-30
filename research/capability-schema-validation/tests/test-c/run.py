#!/usr/bin/env python3
"""Test C — Schema drift / versioning runner (C1-C4).

Loads v0 schemas + variant C descriptions (stale) and v1 mutated schemas
for each case under schemas/{c1,c2,c3,c4}/schemas.json. Submits v0-shaped
calls through sandbox → runtime validation → policy → execution and where
applicable output validation. Records per-call log entries and a summary.

Invocation:
  python research/capability-schema-validation/tests/test-c/run.py
  python research/capability-schema-validation/tests/test-c/run.py --case c1

Logs: research/capability-schema-validation/logs/test-c/{c1,c2,c3,c4,summary}.json
Exit 0 if all acceptance criteria met; 1 if blocking failure (C1 valid reached
execution failure or C2-C4 invalid reached execution).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # research/capability-schema-validation/
HARNESS_DIR = ROOT / "harness"
LOGS_DIR = ROOT / "logs" / "test-c"
SCHEMAS_DIR = HERE / "schemas"

# Ensure harness imports work
sys.path.insert(0, str(HARNESS_DIR))
from runtime import Runtime, Harness  # type: ignore
from sandbox import Sandbox  # type: ignore


def _harness_for(schemas_path: Path) -> Harness:
    runtime = Runtime(schemas_path=schemas_path)
    sandbox = Sandbox(schemas_path=schemas_path)
    return Harness(sandbox=sandbox, runtime=runtime)


def run_c1() -> List[Dict[str, Any]]:
    schemas_path = SCHEMAS_DIR / "c1" / "schemas.json"
    harness = _harness_for(schemas_path)
    logs: List[Dict[str, Any]] = []

    # v0-shaped calls without new optionals — should still execute under v1 (backward compatible)
    cases = [
        ("search_artefacts no new param", "search_artefacts", {"query": "hello", "limit": 5}, None, True, "executed:ok"),
        ("get_artefact normal", "get_artefact", {"id": "art_abc-123"}, None, True, "executed:ok"),
        ("create_artefact without priority", "create_artefact", {"type": "spec", "title": "My Spec"}, None, True, "executed:ok"),
        ("query_metrics normal", "query_metrics", {"filter": {"type": "spec"}}, None, True, "executed:ok"),
    ]
    for label, op, args, payload_version, expect_executed, expect_validation in cases:
        res = harness.call(op, args, payload_version=payload_version)
        entry = {
            "case": "C1",
            "label": label,
            "op_id": op,
            "arguments": args,
            "payload_version": payload_version,
            "validation_result": res["validation_result"],
            "error": res["error"],
            "executed": res["executed"],
            "result": res["result"],
            "latency_ms": res["latency_ms"],
            "schema_version": res["version"],
            "trace": res["trace"],
            "expect_executed": expect_executed,
            "expect_validation": expect_validation,
            "pass": res["executed"] == expect_executed and expect_validation in res["validation_result"],
        }
        logs.append(entry)

    # Additional: call with new optional param should also execute
    res = harness.call("search_artefacts", {"query": "hi", "sort_order": "desc"})
    logs.append({
        "case": "C1",
        "label": "search_artefacts with new sort_order",
        "op_id": "search_artefacts",
        "arguments": {"query": "hi", "sort_order": "desc"},
        "payload_version": None,
        "validation_result": res["validation_result"],
        "error": res["error"],
        "executed": res["executed"],
        "result": res["result"],
        "latency_ms": res["latency_ms"],
        "schema_version": res["version"],
        "trace": res["trace"],
        "expect_executed": True,
        "expect_validation": "executed:ok",
        "pass": res["executed"] is True,
    })
    res2 = harness.call("create_artefact", {"type": "spec", "title": "T2", "priority": "high"})
    logs.append({
        "case": "C1",
        "label": "create_artefact with new priority",
        "op_id": "create_artefact",
        "arguments": {"type": "spec", "title": "T2", "priority": "high"},
        "payload_version": None,
        "validation_result": res2["validation_result"],
        "error": res2["error"],
        "executed": res2["executed"],
        "result": res2["result"],
        "latency_ms": res2["latency_ms"],
        "schema_version": res2["version"],
        "trace": res2["trace"],
        "expect_executed": True,
        "expect_validation": "executed:ok",
        "pass": res2["executed"] is True,
    })

    # Version check: stale payload_version=0.1.0 against 0.2.0 mutated op should yield VersionMismatch
    res3 = harness.call("search_artefacts", {"query": "hi"}, payload_version="0.1.0")
    logs.append({
        "case": "C1",
        "label": "version check stale 0.1.0 vs 0.2.0 mutated op",
        "op_id": "search_artefacts",
        "arguments": {"query": "hi"},
        "payload_version": "0.1.0",
        "validation_result": res3["validation_result"],
        "error": res3["error"],
        "executed": res3["executed"],
        "result": res3["result"],
        "latency_ms": res3["latency_ms"],
        "schema_version": res3["version"],
        "trace": res3["trace"],
        "expect_executed": False,
        "expect_validation": "rejected:validation",
        "expect_code": "VersionMismatch",
        "pass": res3["error"] is not None and res3["error"].get("code") == "VersionMismatch" and res3["executed"] is False,
    })

    return logs


def run_c2() -> List[Dict[str, Any]]:
    schemas_path = SCHEMAS_DIR / "c2" / "schemas.json"
    harness = _harness_for(schemas_path)
    logs: List[Dict[str, Any]] = []

    # Each case violates exactly one tightened constraint — v0-valid, v1-invalid
    cases = [
        (
            "create_artefact title too long (60 > 50 new max)",
            "create_artefact",
            {"type": "spec", "title": "A" * 60},
            "title", "maxLength",
        ),
        (
            "search_artefacts query too long (60 > 50 new max)",
            "search_artefacts",
            {"query": "q" * 60},
            "query", "maxLength",
        ),
        (
            "create_review rationale too short (20 < 100 new min)",
            "create_review",
            {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Short rationale 20ch."},
            "rationale", "minLength",
        ),
        (
            "link_artefacts removed enum relates_to",
            "link_artefacts",
            {"source_id": "art_abc-123", "target_ids": ["art_def-456"], "relation": "relates_to"},
            "relation", "enum",
        ),
        (
            "search_artefacts limit too high (50 > 20 new max)",
            "search_artefacts",
            {"query": "hi", "limit": 50},
            "limit", "maximum",
        ),
    ]
    for label, op, args, expect_field, expect_constraint in cases:
        res = harness.call(op, args)
        err = res["error"] or {}
        field_ok = expect_field in (err.get("field") or "") if expect_field else True
        constraint_ok = err.get("constraint") == expect_constraint
        logs.append({
            "case": "C2",
            "label": label,
            "op_id": op,
            "arguments": args,
            "payload_version": None,
            "validation_result": res["validation_result"],
            "error": err,
            "executed": res["executed"],
            "result": res["result"],
            "latency_ms": res["latency_ms"],
            "schema_version": res["version"],
            "trace": res["trace"],
            "expect_executed": False,
            "expect_code": "ValidationFailed",
            "expect_field": expect_field,
            "expect_constraint": expect_constraint,
            "pass": res["executed"] is False and err.get("code") == "ValidationFailed" and field_ok and constraint_ok,
            "field_ok": field_ok,
            "constraint_ok": constraint_ok,
        })

    # Version check: explicit stale version should also be VersionMismatch before constraint check
    res = harness.call("create_artefact", {"type": "spec", "title": "hi"}, payload_version="0.1.0")
    logs.append({
        "case": "C2",
        "label": "version check stale 0.1.0 vs 0.2.0",
        "op_id": "create_artefact",
        "arguments": {"type": "spec", "title": "hi"},
        "payload_version": "0.1.0",
        "validation_result": res["validation_result"],
        "error": res["error"],
        "executed": res["executed"],
        "result": res["result"],
        "latency_ms": res["latency_ms"],
        "schema_version": res["version"],
        "trace": res["trace"],
        "expect_code": "VersionMismatch",
        "pass": res["error"] is not None and res["error"].get("code") == "VersionMismatch" and res["executed"] is False,
    })

    return logs


def run_c3() -> List[Dict[str, Any]]:
    schemas_path = SCHEMAS_DIR / "c3" / "schemas.json"
    runtime = Runtime(schemas_path=schemas_path)
    sandbox = Sandbox(schemas_path=schemas_path)
    harness = Harness(sandbox=sandbox, runtime=runtime)
    logs: List[Dict[str, Any]] = []

    # For C3, input validation still passes (mutation is output-only), execution succeeds,
    # but output validation against v1 outputSchema must fail.
    for label, op, args in [
        ("query_metrics — v0 total shape vs v1 count shape", "query_metrics", {"filter": {"type": "spec"}}),
        ("search_artefacts — v0 items shape vs v1 results shape", "search_artefacts", {"query": "hello"}),
    ]:
        res = harness.call(op, args)
        # If execution succeeded, validate output against v1 outputSchema
        output_valid = None
        output_error = None
        catching = None
        if res["executed"] and res["result"] is not None:
            ok, err = runtime.validate_output(op, res["result"])
            output_valid = ok
            output_error = err
            catching = "output_schema" if not ok else "none"
        else:
            # If input already rejected, that's not the expected path for C3 (inputs unchanged)
            output_valid = False
            catching = "input_rejected_unexpected"

        # Acceptance: input should execute, output validation should FAIL (mismatch caught)
        passed = res["executed"] is True and output_valid is False
        logs.append({
            "case": "C3",
            "label": label,
            "op_id": op,
            "arguments": args,
            "validation_result": res["validation_result"],
            "error": res["error"],
            "executed": res["executed"],
            "result": res["result"],
            "output_valid": output_valid,
            "output_error": output_error,
            "catching_mechanism": catching,
            "latency_ms": res["latency_ms"],
            "schema_version": res["version"],
            "trace": res["trace"],
            "expect_executed": True,
            "expect_output_valid": False,
            "pass": passed,
        })

    # Also test that a v1-shaped output would pass (sanity: new schema is valid)
    # query_metrics v1 expects count not total, and count string? Actually items[].count is string
    v1_output = {"items": [{"key": "spec", "count": "1"}], "count": 1}
    ok, err = runtime.validate_output("query_metrics", v1_output)
    logs.append({
        "case": "C3",
        "label": "sanity: v1-shaped output passes v1 schema",
        "op_id": "query_metrics",
        "arguments": None,
        "validation_result": "sanity",
        "error": err,
        "executed": None,
        "result": v1_output,
        "output_valid": ok,
        "output_error": err,
        "catching_mechanism": "none" if ok else "failed",
        "latency_ms": 0,
        "schema_version": runtime.version,
        "trace": [],
        "expect_output_valid": True,
        "pass": ok is True,
    })

    return logs


def run_c4() -> List[Dict[str, Any]]:
    schemas_path = SCHEMAS_DIR / "c4" / "schemas.json"
    harness = _harness_for(schemas_path)
    logs: List[Dict[str, Any]] = []

    # Removed operation
    res = harness.call("create_review", {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for validation"})
    logs.append({
        "case": "C4",
        "label": "removed operation create_review",
        "op_id": "create_review",
        "arguments": {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for validation"},
        "validation_result": res["validation_result"],
        "error": res["error"],
        "executed": res["executed"],
        "result": res["result"],
        "latency_ms": res["latency_ms"],
        "schema_version": res["version"],
        "trace": res["trace"],
        "expect_executed": False,
        "expect_code": "UnknownOperation",
        "pass": res["executed"] is False and res["error"] is not None and res["error"].get("code") == "UnknownOperation",
    })

    # Renamed old ID
    res2 = harness.call("search_artefacts", {"query": "hello"})
    logs.append({
        "case": "C4",
        "label": "renamed old ID search_artefacts (now search)",
        "op_id": "search_artefacts",
        "arguments": {"query": "hello"},
        "validation_result": res2["validation_result"],
        "error": res2["error"],
        "executed": res2["executed"],
        "result": res2["result"],
        "latency_ms": res2["latency_ms"],
        "schema_version": res2["version"],
        "trace": res2["trace"],
        "expect_executed": False,
        "expect_code": "UnknownOperation",
        "pass": res2["executed"] is False and res2["error"] is not None and res2["error"].get("code") == "UnknownOperation",
    })

    # New ID should succeed
    res3 = harness.call("search", {"query": "hello"})
    logs.append({
        "case": "C4",
        "label": "new ID search succeeds",
        "op_id": "search",
        "arguments": {"query": "hello"},
        "validation_result": res3["validation_result"],
        "error": res3["error"],
        "executed": res3["executed"],
        "result": res3["result"],
        "latency_ms": res3["latency_ms"],
        "schema_version": res3["version"],
        "trace": res3["trace"],
        "expect_executed": True,
        "expect_code": None,
        "pass": res3["executed"] is True and res3["validation_result"] == "executed:ok",
    })

    # Fuzzy / typo should not route (D4-style check within C4)
    res4 = harness.call("Search_Artefacts", {"query": "hi"})
    logs.append({
        "case": "C4",
        "label": "typo/casing Search_Artefacts must not fuzzy-match",
        "op_id": "Search_Artefacts",
        "arguments": {"query": "hi"},
        "validation_result": res4["validation_result"],
        "error": res4["error"],
        "executed": res4["executed"],
        "result": res4["result"],
        "latency_ms": res4["latency_ms"],
        "schema_version": res4["version"],
        "trace": res4["trace"],
        "expect_executed": False,
        "expect_code": "UnknownOperation",
        "pass": res4["executed"] is False and res4["error"] is not None and res4["error"].get("code") == "UnknownOperation",
    })

    # Version check on removed op: should still be UnknownOperation even with version
    res5 = harness.call("create_review", {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for validation"}, payload_version="0.1.0")
    logs.append({
        "case": "C4",
        "label": "removed op with stale payload_version still UnknownOperation",
        "op_id": "create_review",
        "arguments": {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for validation"},
        "payload_version": "0.1.0",
        "validation_result": res5["validation_result"],
        "error": res5["error"],
        "executed": res5["executed"],
        "result": res5["result"],
        "latency_ms": res5["latency_ms"],
        "schema_version": res5["version"],
        "trace": res5["trace"],
        "expect_executed": False,
        "expect_code": "UnknownOperation",
        "pass": res5["executed"] is False and res5["error"] is not None and res5["error"].get("code") == "UnknownOperation",
    })

    return logs


def main():
    parser = argparse.ArgumentParser(description="Test C drift runner")
    parser.add_argument("--case", choices=["c1", "c2", "c3", "c4"], help="Run single case")
    args = parser.parse_args()

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    runners = {
        "c1": run_c1,
        "c2": run_c2,
        "c3": run_c3,
        "c4": run_c4,
    }

    to_run = [args.case] if args.case else ["c1", "c2", "c3", "c4"]
    all_logs: Dict[str, List[Dict[str, Any]]] = {}
    overall_pass = True
    total = 0
    passed = 0

    for case in to_run:
        fn = runners[case]
        logs = fn()
        all_logs[case] = logs
        # write per-case log
        out = LOGS_DIR / f"{case}.json"
        out.write_text(json.dumps(logs, indent=2))
        print(f"\n=== {case.upper()} ===")
        for entry in logs:
            status = "PASS" if entry.get("pass") else "FAIL"
            err = entry.get("error") or {}
            code = err.get("code", "-")
            field = err.get("field", "")
            constraint = err.get("constraint", "")
            out_valid = entry.get("output_valid")
            print(f"[{status}] {entry['label']}: executed={entry.get('executed')} validation={entry.get('validation_result')} code={code} field={field} constraint={constraint} output_valid={out_valid} trace={entry.get('trace')}")
            total += 1
            if entry.get("pass"):
                passed += 1
            else:
                overall_pass = False

    # summary
    summary = {
        "cases": to_run,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "overall_pass": overall_pass,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (LOGS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nSummary: {passed}/{total} passed, overall_pass={overall_pass}")
    if not overall_pass:
        print("BLOCKING: some drift cases did not meet acceptance criteria", file=sys.stderr)
        sys.exit(1)
    print("All Test C drift cases PASSED")


if __name__ == "__main__":
    main()
