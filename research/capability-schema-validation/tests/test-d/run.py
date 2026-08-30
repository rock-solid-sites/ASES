#!/usr/bin/env python3
"""Test D runner — Capability / authority separation (D1-D4).

Checks (design §5.5):
  D1 — Absent capability (sandbox gate)
  D2 — Policy-denied capability (policy gate after validation pass)
  D3 — Malformed bypass attempt (validation gate before policy)
  D4 — Operation-identifier manipulation (exact-match only)

Usage:
  python research/capability-schema-validation/tests/test-d/run.py
  python research/capability-schema-validation/tests/test-d/run.py --json
  python research/capability-schema-validation/tests/test-d/run.py --case D2
  python research/capability-schema-validation/tests/test-d/run.py --output logs/test-d

Exit code 0 if all cases PASS (or FAILs recorded as findings with no crash).
Exit code 1 only on harness error / unexpected exception.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # research/capability-schema-validation
HARNESS_DIR = ROOT / "harness"
LOG_DIR_DEFAULT = ROOT / "logs" / "test-d"

# --- import harness (supports both `python -m` and direct `python path/run.py`) ---
try:
    from harness.sandbox import Sandbox  # when run as module
    from harness.runtime import Runtime, Harness
except ImportError:
    sys.path.insert(0, str(HARNESS_DIR))
    from sandbox import Sandbox  # type: ignore
    from runtime import Runtime, Harness  # type: ignore


# ---------------------------------------------------------------------------
# Case definitions — each case carries explicit expected_code / boundary
# ---------------------------------------------------------------------------
def build_cases():
    """Return ordered list of (check, case_id, spec) dicts."""
    cases: List[Dict[str, Any]] = []

    # ---- D1: Absent capability — restricted sandbox (10 allowed, 4 excluded) ----
    allowed_10 = {
        "search_artefacts",
        "get_artefact",
        "create_artefact",
        "create_review",
        "set_severity",
        "query_metrics",
        "list_reviews",
        "get_capability_schema",
        "submit_evidence",
        "link_artefacts",
    }
    # D1 uses a restricted sandbox; other checks use full sandbox
    d1_common = dict(check="D1", sandbox_allowed=allowed_10, expected_code="UnknownOperation", expected_boundary="sandbox", expect_executed=False, expected_validation_result="rejected:sandbox")
    cases.append({**d1_common, "case_id": "D1.1", "op_id": "archive_artefact", "arguments": {"artefact_id": "art_abc-123", "reason": "superseded by new design for clarity"}, "policy": None, "description": "excluded op archive_artefact with valid args — must be UnknownOperation at sandbox"})
    cases.append({**d1_common, "case_id": "D1.2", "op_id": "set_artefact_state", "arguments": {"artefact_id": "art_abc-123", "state": "active"}, "description": "excluded op set_artefact_state — sandbox UnknownOperation"})
    cases.append({**d1_common, "case_id": "D1.3", "op_id": "update_artefact_status", "arguments": {"id": "art_abc-123", "status": "active"}, "description": "excluded op update_artefact_status — sandbox UnknownOperation"})
    cases.append({**d1_common, "case_id": "D1.4", "op_id": "delete_artefact", "arguments": {"id": "art_abc-123"}, "description": "hallucinated op not in registry at all — sandbox UnknownOperation"})
    cases.append({"check": "D1", "case_id": "D1.5", "op_id": "search_artefacts", "arguments": {"query": "hello"}, "policy": None, "sandbox_allowed": allowed_10, "expected_code": None, "expected_boundary": None, "expect_executed": True, "expected_validation_result": "executed:ok", "description": "control: allowed op still executes under restricted sandbox"})

    # ---- D2: Policy-denied (op-level and resource-level) ----
    for cid, op_id, args, pol, desc in [
        ("D2.1", "search_artefacts", {"query": "hello"}, {"deny": ["search_artefacts"]}, "op-level deny search_artefacts — PolicyDenied at policy after validation:pass"),
        ("D2.2", "create_artefact", {"type": "spec", "title": "Test"}, {"deny": ["create_artefact"]}, "op-level deny create_artefact — PolicyDenied at policy"),
        ("D2.3", "get_artefact", {"id": "art_denied-001"}, {"deny_resources": ["art_denied-001"]}, "resource-level deny get_artefact art_denied-001 — PolicyDenied"),
        ("D2.4", "archive_artefact", {"artefact_id": "art_secret-001", "reason": "cleanup reason long enough"}, {"deny_resources": ["art_secret-001"]}, "resource-level deny archive_artefact art_secret-001 — PolicyDenied"),
    ]:
        cases.append({"check": "D2", "case_id": cid, "op_id": op_id, "arguments": args, "policy": pol, "sandbox_allowed": None, "expected_code": "PolicyDenied", "expected_boundary": "policy", "expect_executed": False, "expected_validation_result": "rejected:policy", "description": desc})
    # D2 controls — same ops without deny must execute
    cases.append({"check": "D2", "case_id": "D2.5a", "op_id": "search_artefacts", "arguments": {"query": "hello"}, "policy": None, "sandbox_allowed": None, "expected_code": None, "expected_boundary": None, "expect_executed": True, "expected_validation_result": "executed:ok", "description": "control: search_artefacts without deny executes"})
    cases.append({"check": "D2", "case_id": "D2.5b", "op_id": "create_artefact", "arguments": {"type": "spec", "title": "Test"}, "policy": None, "sandbox_allowed": None, "expected_code": None, "expected_boundary": None, "expect_executed": True, "expected_validation_result": "executed:ok", "description": "control: create_artefact without deny executes"})
    cases.append({"check": "D2", "case_id": "D2.5c", "op_id": "get_artefact", "arguments": {"id": "art_abc-123"}, "policy": None, "sandbox_allowed": None, "expected_code": None, "expected_boundary": None, "expect_executed": True, "expected_validation_result": "executed:ok", "description": "control: get_artefact without deny executes"})

    # ---- D3: Malformed bypass attempt (must be ValidationFailed before policy) ----
    d3_cases = [
        ("D3.1", "search_artefacts", {}, "missing required query — ValidationFailed/required"),
        ("D3.2", "search_artefacts", {"query": 123}, "wrong type query:number — ValidationFailed/type"),
        ("D3.3", "create_artefact", {"type": "invalid", "title": "t"}, "enum violation type=invalid — ValidationFailed/enum"),
        ("D3.4", "get_artefact", {"id": "art_abc-123", "admin": True, "role": "superuser"}, "extra unknown params — ValidationFailed/additionalProperties (privilege escalation probe)"),
        ("D3.5", "search_artefacts", {"query": "hi", "limit": 999}, "constraint violation limit>100 — ValidationFailed/maximum"),
        ("D3.6", "get_artefact", {"id": "BAD_ID; DROP TABLE"}, "pattern violation — ValidationFailed/pattern (injection probe)"),
        ("D3.7", "submit_evidence", {"artefact_id": "art_abc-123", "evidence_items": [{"source": "", "content": ""}]}, "nested minLength violation — ValidationFailed"),
        ("D3.8", "create_review", {"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "Rationale long enough for check", "escalate": True}, "extra param escalate — ValidationFailed/additionalProperties"),
    ]
    for cid, op_id, args, desc in d3_cases:
        cases.append({"check": "D3", "case_id": cid, "op_id": op_id, "arguments": args, "policy": None, "sandbox_allowed": None, "expected_code": "ValidationFailed", "expected_boundary": "runtime", "expect_executed": False, "expected_validation_result": "rejected:validation", "description": desc})
    # ordering probe: D3 with deny policy must still be validation-rejected, not policy-rejected
    cases.append({"check": "D3", "case_id": "D3.9", "op_id": "search_artefacts", "arguments": {}, "policy": {"deny": ["search_artefacts"]}, "sandbox_allowed": None, "expected_code": "ValidationFailed", "expected_boundary": "runtime", "expect_executed": False, "expected_validation_result": "rejected:validation", "description": "ordering probe: malformed with deny policy — still ValidationFailed before policy"})

    # ---- D4: Operation-identifier manipulation (exact-match only → UnknownOperation) ----
    mani_cases = [
        ("D4.1a", "search_artefact", {"query": "hi"}, "typo missing s — UnknownOperation"),
        ("D4.1b", "search_artefactsx", {"query": "hi"}, "typo extra char — UnknownOperation"),
        ("D4.2a", "Search_Artefacts", {"query": "hi"}, "casing Pascal — UnknownOperation"),
        ("D4.2b", "SEARCH_ARTEFACTS", {"query": "hi"}, "casing upper — UnknownOperation"),
        ("D4.2c", "search_Artefacts", {"query": "hi"}, "casing mixed — UnknownOperation"),
        ("D4.3a", "internal__search_artefacts", {"query": "hi"}, "prefix injection — UnknownOperation"),
        ("D4.3b", "admin_search_artefacts", {"query": "hi"}, "prefix admin — UnknownOperation"),
        ("D4.4a", "../search_artefacts", {"query": "hi"}, "path traversal ../ — UnknownOperation"),
        ("D4.4b", "search_artefacts/../admin", {"query": "hi"}, "path traversal mid — UnknownOperation"),
        ("D4.4c", "search_artefacts%2Fadmin", {"query": "hi"}, "encoded slash — UnknownOperation"),
        ("D4.5a", "0", {"query": "hi"}, "numeric guess 0 — UnknownOperation"),
        ("D4.5b", "1", {"query": "hi"}, "numeric guess 1 — UnknownOperation"),
        ("D4.5c", "999", {"query": "hi"}, "numeric guess 999 — UnknownOperation"),
        ("D4.6a", "", {"query": "hi"}, "empty string — UnknownOperation"),
        ("D4.6b", " search_artefacts", {"query": "hi"}, "leading space — UnknownOperation"),
        ("D4.6c", "search_artefacts ", {"query": "hi"}, "trailing space — UnknownOperation"),
        ("D4.7a", "getArtefact", {"id": "art_abc-123"}, "alias camelCase — UnknownOperation"),
        ("D4.7b", "get-artefact", {"id": "art_abc-123"}, "alias kebab — UnknownOperation"),
        ("D4.7c", "artefact.get", {"id": "art_abc-123"}, "alias dotted — UnknownOperation"),
    ]
    for cid, op_id, args, desc in mani_cases:
        cases.append({"check": "D4", "case_id": cid, "op_id": op_id, "arguments": args, "policy": None, "sandbox_allowed": None, "expected_code": "UnknownOperation", "expected_boundary": "sandbox", "expect_executed": False, "expected_validation_result": "rejected:sandbox", "description": desc})
    # D4 control: exact valid op must execute
    cases.append({"check": "D4", "case_id": "D4.9", "op_id": "search_artefacts", "arguments": {"query": "hello"}, "policy": None, "sandbox_allowed": None, "expected_code": None, "expected_boundary": None, "expect_executed": True, "expected_validation_result": "executed:ok", "description": "control: exact valid op_id search_artefacts executes"})

    return cases


def run_one(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single spec and return a log entry."""
    case_id = spec["case_id"]
    op_id = spec["op_id"]
    arguments = spec["arguments"]
    policy = spec.get("policy")
    expected_code = spec.get("expected_code")
    expected_boundary = spec.get("expected_boundary")
    expect_executed = spec.get("expect_executed", False)
    expected_validation_result = spec.get("expected_validation_result")
    sandbox_allowed = spec.get("sandbox_allowed")

    # Build harness with appropriate sandbox
    if sandbox_allowed is not None:
        sandbox = Sandbox(allowed_op_ids=set(sandbox_allowed))
    else:
        sandbox = Sandbox()
    runtime = Runtime()
    harness = Harness(sandbox=sandbox, runtime=runtime)

    res = harness.call(op_id, arguments, policy=policy)

    executed = res["executed"]
    error = res.get("error")
    actual_code = (error or {}).get("code") if error else None
    actual_boundary = (error or {}).get("boundary") if error else None
    validation_result = res.get("validation_result")
    trace = res.get("trace", [])

    # --- pass logic ---
    # For expect_executed==True: executed must be True, error must be None, trace must include execution:ok
    # For expect_executed==False: executed must be False, actual_code must match expected_code, boundary matches, validation_result matches
    reasons: List[str] = []
    passed = True

    if expect_executed:
        if not executed:
            passed = False
            reasons.append(f"expected executed==True but got executed==False (error={actual_code})")
        if actual_code is not None:
            passed = False
            reasons.append(f"expected no error but got code={actual_code}")
        if expected_validation_result and validation_result != expected_validation_result:
            passed = False
            reasons.append(f"expected validation_result {expected_validation_result!r} got {validation_result!r}")
    else:
        if executed:
            passed = False
            reasons.append("BLOCKING: malformed/absent/policy-denied call reached execution (executed==True)")
        if actual_code != expected_code:
            passed = False
            reasons.append(f"expected error code {expected_code!r} got {actual_code!r}")
        if expected_boundary and actual_boundary != expected_boundary:
            passed = False
            reasons.append(f"expected boundary {expected_boundary!r} got {actual_boundary!r}")
        if expected_validation_result and validation_result != expected_validation_result:
            passed = False
            reasons.append(f"expected validation_result {expected_validation_result!r} got {validation_result!r}")

    # boundary-ordering audits (design §5.5 acceptance: wrong boundary rejection is a finding)
    # D2 must have trace sandbox:allowed → validation:pass → policy:rejected
    # D3 must NOT have policy:rejected in trace; must be validation:rejected immediately after sandbox
    if passed:
        if spec["check"] == "D2" and not expect_executed and expected_code == "PolicyDenied":
            expected_trace = ["sandbox:allowed", "validation:pass", "policy:rejected:PolicyDenied"]
            if trace != expected_trace:
                passed = False
                reasons.append(f"D2 trace ordering failure: expected {expected_trace} got {trace}")
        if spec["check"] == "D3" and expected_code == "ValidationFailed":
            if len(trace) != 2 or trace[0] != "sandbox:allowed" or not trace[1].startswith("validation:rejected:ValidationFailed"):
                passed = False
                reasons.append(f"D3 trace ordering failure: expected [sandbox:allowed, validation:rejected:ValidationFailed] got {trace}")
        if spec["check"] == "D1" and expected_code == "UnknownOperation":
            if trace != ["sandbox:rejected:UnknownOperation"]:
                passed = False
                reasons.append(f"D1 trace failure: expected [sandbox:rejected:UnknownOperation] got {trace}")
        if spec["check"] == "D4" and expected_code == "UnknownOperation":
            if trace != ["sandbox:rejected:UnknownOperation"]:
                passed = False
                reasons.append(f"D4 trace failure: expected [sandbox:rejected:UnknownOperation] got {trace}")

    entry: Dict[str, Any] = {
        "check": spec["check"],
        "case_id": case_id,
        "op_id": op_id,
        "arguments": arguments,
        "policy": policy,
        "expected_code": expected_code,
        "expected_boundary": expected_boundary,
        "expected_validation_result": expected_validation_result,
        "expect_executed": expect_executed,
        "description": spec.get("description", ""),
        "validation_result": validation_result,
        "error": error,
        "executed": executed,
        "result": res.get("result"),
        "latency_ms": res.get("latency_ms"),
        "version": res.get("version"),
        "trace": trace,
        "pass": passed,
        "fail_reasons": reasons,
    }
    return entry


def main():
    ap = argparse.ArgumentParser(description="Test D — Capability / authority separation (D1-D4)")
    ap.add_argument("--json", action="store_true", help="Emit raw JSONL to stdout (one entry per line)")
    ap.add_argument("--case", type=str, default=None, help="Filter by check prefix (e.g. D1, D2, D3, D4) or exact case_id (e.g. D4.1a)")
    ap.add_argument("--output", type=str, default=None, help="Log directory (default: research/capability-schema-validation/logs/test-d)")
    ap.add_argument("--verbose", action="store_true", help="Verbose trace output")
    args = ap.parse_args()

    cases = build_cases()
    prefix = args.case
    if prefix:
        orig = build_cases()
        filtered: List[Dict[str, Any]] = []
        for c in orig:
            if c["case_id"] == prefix or c["check"] == prefix or c["case_id"].startswith(prefix + "."):
                filtered.append(c)
        if not filtered:
            filtered = [c for c in orig if prefix in c["case_id"]]
        cases = filtered
    if args.case and not cases:
        print(f"no cases matched filter {args.case!r}", file=sys.stderr)
        sys.exit(2)

    entries: List[Dict[str, Any]] = []
    for spec in cases:
        entry = run_one(spec)
        entries.append(entry)
        if not args.json:
            status = "PASS" if entry["pass"] else "FAIL"
            trace_str = " → ".join(entry["trace"])
            err_code = (entry["error"] or {}).get("code", "-")
            boundary = (entry["error"] or {}).get("boundary", "-")
            reasons = "; ".join(entry["fail_reasons"]) if entry["fail_reasons"] else ""
            suffix = f" | {reasons}" if reasons else ""
            print(f"[{status}] {entry['case_id']} op={entry['op_id']} executed={entry['executed']} error={err_code} boundary={boundary} trace=[{trace_str}]{suffix}")
            if args.verbose and entry["error"]:
                print(f"       error: {json.dumps(entry['error'])[:300]}")

    if args.json:
        for e in entries:
            print(json.dumps(e))

    # --- write logs (always, unless --json filtered single-case ad-hoc) ---
    out_dir = Path(args.output) if args.output else LOG_DIR_DEFAULT
    out_dir.mkdir(parents=True, exist_ok=True)
    # Only write full logs when running full suite (no --case filter) or when --case covers a full check
    # To keep reproduction clean, write filtered subset with suffix when --case present
    if args.case:
        # write to a temp-style file but still commit-track path: write filtered to same files + filtered marker
        fname = f"filtered-{prefix}.jsonl"
        with open(out_dir / fname, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
    else:
        # full suite: per-check JSONL + combined all.jsonl
        combined: List[Dict[str, Any]] = []
        for check in ("D1", "D2", "D3", "D4"):
            subset = [e for e in entries if e["check"] == check]
            with open(out_dir / f"{check.lower()}.jsonl", "w") as f:
                for e in subset:
                    f.write(json.dumps(e) + "\n")
            combined.extend(subset)
        with open(out_dir / "all.jsonl", "w") as f:
            for e in combined:
                f.write(json.dumps(e) + "\n")
        # summary json for results.md convenience
        summary = {
            "total": len(entries),
            "passed": sum(1 for e in entries if e["pass"]),
            "failed": sum(1 for e in entries if not e["pass"]),
            "per_check": {
                chk: {"total": len([e for e in entries if e["check"] == chk]), "passed": len([e for e in entries if e["check"] == chk and e["pass"]]), "failed": len([e for e in entries if e["check"] == chk and not e["pass"]])}
                for chk in ("D1", "D2", "D3", "D4")
            },
        }
        with open(out_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        passed = summary["passed"]
        failed = summary["failed"]
        print(f"\nSummary: {passed} passed, {failed} failed out of {summary['total']}")
        if failed:
            print("One or more checks FAILED — see fail_reasons above (failures are findings per protocol, not a silent pass).")
        else:
            print("All D1-D4 checks PASSED: sandbox/policy/validation boundaries are correctly separated with correct error codes.")

    # Exit code: 0 if all PASS, 1 if any FAIL but still produced logs.
    # The protocol says a FAIL is a finding, not a reason to withhold commit — so we return
    # non-zero only to make CI visible, while still having written logs for commit.
    # For the research workflow, a FAIL means the claim is falsified/narrowed, but runner succeeded.
    # We therefore exit 0 on all-pass, 1 on any fail so that a human reviews.
    if any(not e["pass"] for e in entries):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
