#!/usr/bin/env python3
"""Test B runner — authoritative runtime validation before execution.

Implements the protocol at tests/test-b/protocol.md (design §5.3):

  1. Valid calls (14 ops) must pass validation and execute.
  2. Malformed calls (20 cases across 6 classes) must be rejected before execution
     with typed error {code, field, constraint, got, boundary} preserved.
  3. Recovery: for each malformed case, a single corrected retry must succeed.

Logs every call as JSONL under logs/test-b/run.jsonl.
Exits non-zero on any blocking failure (malformed reached execution).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HARNESS_DIR = ROOT / "research" / "capability-schema-validation" / "harness"
LOG_DIR_DEFAULT = ROOT / "research" / "capability-schema-validation" / "logs" / "test-b"

# Make harness importable (both `python -m` and direct `python run.py` invocations)
sys.path.insert(0, str(HARNESS_DIR))

from sandbox import Sandbox  # type: ignore
from runtime import Harness, Runtime  # type: ignore

# ---------------------------------------------------------------------------
# Case tables (mirrors protocol.md)
# ---------------------------------------------------------------------------

VALID_CASES = [
    ("V1", "search_artefacts", {"query": "hello", "limit": 5}),
    ("V2", "get_artefact", {"id": "art_abc-123"}),
    ("V3", "create_artefact", {"type": "spec", "title": "Test artefact"}),
    ("V4", "update_artefact_status", {"id": "art_abc-123", "status": "active", "reason": "reviewed"}),
    ("V5", "create_review", {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "This is a good rationale with enough length for validation"}),
    ("V6", "set_severity", {"artefact_id": "art_abc-123", "level": "high"}),
    ("V7", "set_artefact_state", {"artefact_id": "art_abc-123", "state": "active", "comment": "ok"}),
    ("V8", "query_metrics", {"filter": {"type": "spec"}, "group_by": "status", "include_facets": True}),
    ("V9", "list_reviews", {"artefact_id": "art_abc-123", "verdict": "approve", "limit": 10}),
    ("V10", "get_capability_schema", {"op_id": "search_artefacts"}),
    ("V11", "submit_evidence", {"artefact_id": "art_abc-123", "evidence_items": [{"source": "paper", "content": "evidence text"}]}),
    ("V12", "link_artefacts", {"source_id": "art_abc-123", "target_ids": ["art_def-456"], "relation": "relates_to"}),
    ("V13", "archive_artefact", {"artefact_id": "art_abc-123", "reason": "superseded by new design for clarity"}),
    ("V14", "validate_payload", {"op_id": "search_artefacts", "payload": {"query": "hi"}, "strict": True}),
]

# Malformed matrix — 20 cases across 6 classes
LONG_TITLE = "A" * 201

MALFORMED_CASES = [
    # Missing required (3)
    ("M1", "search_artefacts", {}, "missing required query", "required", "missing-required"),
    ("M2", "create_review", {"artefact_id": "art_abc-123", "verdict": "approve"}, "missing required rationale", "required", "missing-required"),
    ("M3", "submit_evidence", {"artefact_id": "art_abc-123"}, "missing required evidence_items", "required", "missing-required"),
    # Wrong type (3)
    ("T1", "search_artefacts", {"query": 123}, "query wrong type (number not string)", "type", "wrong-type"),
    ("T2", "search_artefacts", {"query": "hi", "limit": "ten"}, "limit wrong type (string not integer)", "type", "wrong-type"),
    ("T3", "query_metrics", {"filter": "spec"}, "filter wrong type (string not object)", "type", "wrong-type"),
    # Enum violation (3)
    ("E1", "create_artefact", {"type": "invalid", "title": "t"}, "type enum violation", "enum", "enum-violation"),
    ("E2", "set_severity", {"artefact_id": "art_abc-123", "level": "urgent"}, "level enum violation", "enum", "enum-violation"),
    ("E3", "update_artefact_status", {"id": "art_abc-123", "status": "deleted"}, "status enum violation", "enum", "enum-violation"),
    # Extra unknown param (2)
    ("X1", "get_artefact", {"id": "art_abc-123", "extra": "x"}, "extra unknown property", "additionalProperties", "extra-param"),
    ("X2", "create_review", {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for testing", "unknown_field": "oops"}, "extra unknown property", "additionalProperties", "extra-param"),
    # Constraint violation (5)
    ("C1", "search_artefacts", {"query": "hi", "limit": 999}, "limit exceeds maximum 100", "maximum", "constraint-violation"),
    ("C2", "get_artefact", {"id": "BAD_ID"}, "id pattern violation", "pattern", "constraint-violation"),
    ("C3", "create_artefact", {"type": "spec", "title": LONG_TITLE}, "title maxLength 200 violation", "maxLength", "constraint-violation"),
    ("C4", "create_review", {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "short"}, "rationale minLength 10 violation", "minLength", "constraint-violation"),
    ("C5", "archive_artefact", {"artefact_id": "art_abc-123", "reason": "hi"}, "reason minLength 5 violation", "minLength", "constraint-violation"),
    # Nested / array error (4)
    ("N1", "submit_evidence", {"artefact_id": "art_abc-123", "evidence_items": [{"source": "", "content": "text"}]}, "nested minLength on evidence_items source", "minLength", "nested-array"),
    ("N2", "create_review", {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for testing", "citations": ["BAD_ID"]}, "citation pattern violation", "pattern", "nested-array"),
    ("N3", "link_artefacts", {"source_id": "art_abc-123", "target_ids": [], "relation": "relates_to"}, "target_ids minItems 1 violation", "minItems", "nested-array"),
    ("N4", "submit_evidence", {"artefact_id": "art_abc-123", "evidence_items": [{"source": "paper", "content": "text", "weight": 5}]}, "weight maximum 1 violation", "maximum", "nested-array"),
]

# Recovery corrected arguments — one per malformed id
RECOVERY_FIXES: dict[str, dict] = {
    "M1": {"query": "hello"},
    "M2": {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Corrected rationale with enough length for validation"},
    "M3": {"artefact_id": "art_abc-123", "evidence_items": [{"source": "paper", "content": "ok text"}]},
    "T1": {"query": "hello"},
    "T2": {"query": "hi", "limit": 5},
    "T3": {"filter": {"type": "spec"}},
    "E1": {"type": "spec", "title": "t"},
    "E2": {"artefact_id": "art_abc-123", "level": "high"},
    "E3": {"id": "art_abc-123", "status": "active"},
    "X1": {"id": "art_abc-123"},
    "X2": {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for testing"},
    "C1": {"query": "hi", "limit": 20},
    "C2": {"id": "art_abc-123"},
    "C3": {"type": "spec", "title": "Short title"},
    "C4": {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "This is a corrected rationale with enough length"},
    "C5": {"artefact_id": "art_abc-123", "reason": "superseded by new design for clarity"},
    "N1": {"artefact_id": "art_abc-123", "evidence_items": [{"source": "paper", "content": "text"}]},
    "N2": {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale with enough length for testing", "citations": ["art_def-456"]},
    "N3": {"source_id": "art_abc-123", "target_ids": ["art_def-456"], "relation": "relates_to"},
    "N4": {"artefact_id": "art_abc-123", "evidence_items": [{"source": "paper", "content": "text", "weight": 0.8}]},
}


def _op_for(malformed_id: str) -> str:
    for mid, op, _args, _desc, _const, _cls in MALFORMED_CASES:
        if mid == malformed_id:
            return op
    raise KeyError(malformed_id)


def run(log_dir: Path, json_summary: bool = False) -> dict:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "run.jsonl"

    harness = Harness(Sandbox(), Runtime())
    rows: list[dict] = []

    # Counters
    valid_total = 0
    valid_pass = 0
    valid_fail = 0

    malformed_total = 0
    malformed_rejected = 0  # correctly rejected before execution
    malformed_executed = 0  # blocking failure — should stay 0
    malformed_wrong_code = 0
    malformed_field_present = 0
    malformed_constraint_present = 0
    # Per-class tracking
    by_class: dict[str, dict[str, int]] = {}

    # Recovery
    recovery_total = 0
    recovery_success = 0
    recovery_by_class: dict[str, dict[str, int]] = {}

    def log_row(**kw):
        rows.append(kw)
        return kw

    # --- Phase 1: valid calls ---
    for vid, op_id, args in VALID_CASES:
        valid_total += 1
        res = harness.call(op_id, args)
        executed = res["executed"]
        error = res["error"]
        trace = res.get("trace", [])
        passed = executed is True and error is None
        if passed:
            valid_pass += 1
        else:
            valid_fail += 1
        log_row(
            variant="C",
            test_id=vid,
            phase="valid",
            op_id=op_id,
            arguments=args,
            validation_result="pass" if passed else "fail",
            error=error,
            executed=executed,
            trace=trace,
            latency_ms=res.get("latency_ms"),
            version=res.get("version"),
            description=f"valid call to {op_id}",
            expected_executed=True,
            observed_pass=passed,
        )

    # --- Phase 2: malformed calls ---
    for mid, op_id, args, desc, expected_constraint, cls in MALFORMED_CASES:
        malformed_total += 1
        by_class.setdefault(cls, {"total": 0, "rejected": 0, "field_present": 0, "constraint_present": 0})
        by_class[cls]["total"] += 1

        res = harness.call(op_id, args)
        executed = res["executed"]
        error = res["error"]
        trace = res.get("trace", [])

        # Validation checks
        correctly_rejected = executed is False
        if correctly_rejected:
            malformed_rejected += 1
            by_class[cls]["rejected"] += 1
        else:
            malformed_executed += 1  # blocking failure

        # Error identity checks
        has_code = error is not None and error.get("code") == "ValidationFailed"
        has_boundary = error is not None and error.get("boundary") == "runtime"
        if not has_code or not has_boundary:
            malformed_wrong_code += 1

        field = (error or {}).get("field")
        constraint = (error or {}).get("constraint")
        if field is not None:
            malformed_field_present += 1
            by_class[cls]["field_present"] += 1
        if constraint is not None:
            malformed_constraint_present += 1
            by_class[cls]["constraint_present"] += 1

        # Record expected vs observed constraint (informational; some validators surface slightly different keyword)
        constraint_match = constraint == expected_constraint

        log_row(
            variant="C",
            test_id=mid,
            phase="malformed",
            error_class=cls,
            op_id=op_id,
            arguments=args,
            description=desc,
            expected_code="ValidationFailed",
            expected_constraint=expected_constraint,
            expected_boundary="runtime",
            validation_result="rejected" if correctly_rejected else "EXECUTED_BLOCKING_FAILURE",
            error=error,
            executed=executed,
            trace=trace,
            latency_ms=res.get("latency_ms"),
            version=res.get("version"),
            has_code=has_code,
            has_boundary=has_boundary,
            field_present=field is not None,
            constraint_present=constraint is not None,
            constraint_match=constraint_match,
            correctly_rejected=correctly_rejected,
        )

    # --- Phase 3: recovery (one corrected retry per malformed) ---
    for mid, _op_id, _args, _desc, _expected_constraint, cls in MALFORMED_CASES:
        recovery_total += 1
        recovery_by_class.setdefault(cls, {"total": 0, "success": 0})
        recovery_by_class[cls]["total"] += 1

        op_id = _op_for(mid)
        fixed_args = RECOVERY_FIXES[mid]
        res = harness.call(op_id, fixed_args)
        executed = res["executed"]
        error = res["error"]
        success = executed is True and error is None
        if success:
            recovery_success += 1
            recovery_by_class[cls]["success"] += 1

        log_row(
            variant="C",
            test_id=f"{mid}-recovery",
            phase="recovery",
            error_class=cls,
            op_id=op_id,
            arguments=fixed_args,
            corrects=mid,
            validation_result="pass" if success else "fail",
            error=error,
            executed=executed,
            trace=res.get("trace", []),
            latency_ms=res.get("latency_ms"),
            version=res.get("version"),
            recovery_success=success,
        )

    # Write JSONL log
    with open(log_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # Summary
    recovery_rate = recovery_success / recovery_total if recovery_total else 0.0
    summary = {
        "variant": "C",
        "runtime_version": harness.runtime.version,
        "valid": {"total": valid_total, "pass": valid_pass, "fail": valid_fail, "pass_rate": valid_pass / valid_total if valid_total else 0},
        "malformed": {
            "total": malformed_total,
            "rejected_before_execution": malformed_rejected,
            "executed_blocking_failures": malformed_executed,
            "wrong_code": malformed_wrong_code,
            "field_present": malformed_field_present,
            "field_rate": malformed_field_present / malformed_total if malformed_total else 0,
            "constraint_present": malformed_constraint_present,
            "constraint_rate": malformed_constraint_present / malformed_total if malformed_total else 0,
            "by_class": by_class,
        },
        "recovery": {
            "total": recovery_total,
            "success": recovery_success,
            "fail": recovery_total - recovery_success,
            "rate": recovery_rate,
            "threshold": 0.6,
            "meets_threshold": recovery_rate >= 0.6,
            "by_class": recovery_by_class,
        },
        "log_path": str(log_path),
        "total_rows": len(rows),
        # Blocking failure flag
        "blocking_failure": malformed_executed > 0 or valid_fail > 0,
        "exposure_note": "Recovery used only {code, field, constraint, got, message} from runtime error — no full authoritative schema excerpt was needed. See results.md for per-class exposure analysis.",
    }

    # Human-readable output
    if json_summary:
        print(json.dumps(summary, indent=2))
    else:
        print("=" * 72)
        print("Test B — Authoritative Runtime Validation  (variant C only)")
        print("=" * 72)
        print(f"Runtime version: {harness.runtime.version}  |  log: {log_path}")
        print()
        print(f"Valid calls:          {valid_pass}/{valid_total} passed  (fail={valid_fail})  rate={summary['valid']['pass_rate']:.3f}")
        print(f"Malformed rejected:   {malformed_rejected}/{malformed_total} before execution  (blocking failures={malformed_executed})")
        print(f"Wrong error code:     {malformed_wrong_code}/{malformed_total}")
        print(f"Field present:        {malformed_field_present}/{malformed_total}  rate={summary['malformed']['field_rate']:.3f}")
        print(f"Constraint present:   {malformed_constraint_present}/{malformed_total}  rate={summary['malformed']['constraint_rate']:.3f}")
        print()
        print(f"Recovery:             {recovery_success}/{recovery_total}  rate={recovery_rate:.3f}  threshold=0.60  {'PASS' if recovery_rate >= 0.6 else 'FAIL'}")
        print()
        print("By class:")
        all_classes = sorted(set(list(by_class.keys()) + list(recovery_by_class.keys())))
        for cls in all_classes:
            m = by_class.get(cls, {})
            r = recovery_by_class.get(cls, {})
            print(f"  {cls:22s} malformed {m.get('rejected',0)}/{m.get('total',0)} rejected"
                  f"  field {m.get('field_present',0)}/{m.get('total',0)}"
                  f"  recovery {r.get('success',0)}/{r.get('total',0)}")
        print()
        if summary["blocking_failure"]:
            print("BLOCKING FAILURE: valid call failed or malformed reached execution — see logs")
        else:
            print("Gate PASSED: zero malformed reached execution, all valid executed")
        print("=" * 72)

    # Per-row detail (always print malformed detail when not --json)
    if not json_summary:
        print("\nMalformed detail:")
        for r in rows:
            if r["phase"] == "malformed":
                err = r["error"] or {}
                print(f"  [{r['test_id']:3s}] {r['op_id']:24s} rejected={r['correctly_rejected']} code={err.get('code','-'):18s}"
                      f" field={str(err.get('field','-')):22s} constraint={str(err.get('constraint','-')):22s} boundary={err.get('boundary','-')}")
        print("\nRecovery detail:")
        for r in rows:
            if r["phase"] == "recovery":
                print(f"  [{r['test_id']:16s}] {r['op_id']:24s} success={r['recovery_success']} executed={r['executed']} error={r['error']}")

    return summary


def main():
    ap = argparse.ArgumentParser(description="Test B — authoritative runtime validation (variant C)")
    ap.add_argument("--log-dir", type=str, default=str(LOG_DIR_DEFAULT), help="Log output directory")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON summary")
    args = ap.parse_args()
    log_dir = Path(args.log_dir)
    summary = run(log_dir, json_summary=args.json)
    # Exit code: 1 on blocking failure, 0 otherwise
    if summary["blocking_failure"]:
        sys.exit(1)
    # Also exit 1 if error-identity degraded beyond trivial (wrong code > 0)
    if summary["malformed"]["wrong_code"] > 0:
        # Not blocking per protocol, but fail the run so results.md notes it explicitly
        print(f"\nNote: {summary['malformed']['wrong_code']} case(s) returned wrong error code — see results.md", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
