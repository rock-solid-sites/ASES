#!/usr/bin/env python3
"""CLI entry point for ad-hoc harness calls.

Usage:
  python -m research.capability-schema-validation.harness.run --help
  python research/capability-schema-validation/harness/run.py --smoke
  python research/capability-schema-validation/harness/run.py --op search_artefacts --args '{"query":"test"}'
  python research/capability-schema-validation/harness/run.py --measure-tokens
  python research/capability-schema-validation/harness/run.py --variant derived/variant-c.json --smoke

Notes:
- --smoke runs valid->execute and malformed->rejected-before-execution gate (Phase 0).
- Authoritative schema text is never printed to model path; variant files are the model-visible artifacts.
- v2 fix: handles missing variants gracefully and enforces PARSE_TIMEOUT_S (lowered per #498).
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_SCHEMAS = ROOT / "capabilities" / "authoritative" / "schemas.json"

# v2 fix: lowered parse timeout per #498 — previously 10s, now 2s to bound
# tail latency on malformed/oversized model outputs.
PARSE_TIMEOUT_S = 2.0


def parse_json_with_timeout(text: str, timeout_s: float = PARSE_TIMEOUT_S):
    """Parse JSON with bounded timeout (daemon thread join).

    Returns (ok, parsed_or_None, error_str_or_None). On timeout, ok=False,
    error_str="ParseTimeout". Thread is daemon so it does not block process exit.
    """
    result: list[object | None] = [None]
    error: list[str | None] = [None]
    success: list[bool] = [False]

    def _target():
        try:
            result[0] = json.loads(text)
            success[0] = True
        except Exception as e:
            error[0] = f"{type(e).__name__}: {e}"
            success[0] = False

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout=timeout_s)
    if t.is_alive():
        return False, None, "ParseTimeout"
    if success[0]:
        return True, result[0], None
    return False, None, error[0]


def measure_tokens():
    """Measure tokens for each derived variant, handling missing variants gracefully.

    v2: missing variants are reported as warnings and skipped (not a crash);
    variant JSON parsing is bounded by PARSE_TIMEOUT_S (lowered).
    """
    derived = ROOT / "capabilities" / "derived"
    results = {}
    for variant in ("variant-a.json", "variant-b.json", "variant-c.json"):
        p = derived / variant
        if not p.exists():
            print(f"missing {p} — skipping {variant} (v2 handles missing variants gracefully)", file=sys.stderr)
            continue
        text = p.read_text()
        # Bound JSON parse to avoid hang on corrupted/large variant files
        ok, parsed, err = parse_json_with_timeout(text, timeout_s=PARSE_TIMEOUT_S)
        if not ok:
            print(f"variant {variant} parse failed ({err}) — skipping", file=sys.stderr)
            continue
        chars = len(text)
        approx = chars // 4
        # try tiktoken
        tcount = None
        tokenizer = "heuristic char/4"
        try:
            import tiktoken  # type: ignore

            enc = tiktoken.get_encoding("cl100k_base")
            tcount = len(enc.encode(text))
            tokenizer = "tiktoken cl100k_base"
        except Exception:
            pass
        # also try model API usage? not here
        results[variant] = {"chars": chars, "approx_tokens": approx, "tiktoken_tokens": tcount, "tokenizer": tokenizer}
        print(f"{variant}: chars={chars} approx={approx} tiktoken={tcount} tokenizer={tokenizer}")
    if len(results) >= 2:
        a = results.get("variant-a.json", {}).get("tiktoken_tokens") or results.get("variant-a.json", {}).get("approx_tokens")
        c = results.get("variant-c.json", {}).get("tiktoken_tokens") or results.get("variant-c.json", {}).get("approx_tokens")
        b = results.get("variant-b.json", {}).get("tiktoken_tokens") or results.get("variant-b.json", {}).get("approx_tokens")
        if a and c:
            print(f"ratio C/A = {c/a:.3f}")
        if a and b:
            print(f"ratio B/A = {b/a:.3f}")
    elif len(results) == 0:
        print("no variant files found — all missing (v2 reports gracefully)", file=sys.stderr)
    else:
        print(f"only {len(results)} variant(s) present — ratios incomplete (missing variants handled)", file=sys.stderr)
    return results


def _imports():
    try:
        from .sandbox import Sandbox
        from .runtime import Runtime, Harness
    except ImportError:
        import sys as _sys
        from pathlib import Path as _Path
        _sys.path.insert(0, str(_Path(__file__).resolve().parent))
        from sandbox import Sandbox
        from runtime import Runtime, Harness
    return Sandbox, Runtime, Harness

def smoke():
    Sandbox, Runtime, Harness = _imports()

    harness = Harness(Sandbox(), Runtime())
    cases = [
        ("valid: search_artefacts", "search_artefacts", {"query": "hello", "limit": 5}, True),
        ("valid: get_artefact", "get_artefact", {"id": "art_abc-123"}, True),
        ("valid: create_artefact", "create_artefact", {"type": "spec", "title": "Test"}, True),
        ("malformed: missing required", "search_artefacts", {}, False),
        ("malformed: wrong type", "search_artefacts", {"query": 123}, False),
        ("malformed: enum violation", "create_artefact", {"type": "invalid", "title": "t"}, False),
        ("malformed: extra property", "get_artefact", {"id": "art_abc", "extra": "x"}, False),
        ("malformed: pattern violation", "get_artefact", {"id": "BAD_ID"}, False),
        ("malformed: constraint violation limit>max", "search_artefacts", {"query": "hi", "limit": 999}, False),
        ("malformed: nested array type error", "submit_evidence", {"artefact_id": "art_abc", "evidence_items": [{"source": "", "content": ""}]}, False),
        ("unknown op", "nonexistent_op", {"x": 1}, False),
        ("policy denied", "search_artefacts", {"query": "hi"}, False, {"deny": ["search_artefacts"]}),
    ]
    passed = 0
    failed = 0
    for entry in cases:
        label = entry[0]
        op_id = entry[1]
        args = entry[2]
        should_execute = entry[3]
        policy = entry[4] if len(entry) > 4 else None
        res = harness.call(op_id, args, policy=policy)
        executed = res["executed"]
        # malformed should NOT have executed (validation_rejected before execution)
        # valid should have executed == True
        # policy denied should have executed == False but error code PolicyDenied
        ok = (executed == should_execute)
        # additionally assert: if not should_execute and policy is None and op known, error code should be ValidationFailed or UnknownOperation
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        err_code = (res["error"] or {}).get("code", "-")
        print(f"[{status}] {label}: op={op_id} executed={executed} expected_execute={should_execute} error={err_code} trace={res['trace']}")
        if not ok:
            print(f"  full: {json.dumps(res, indent=2)[:800]}")
    print(f"\nSmoke: {passed} passed, {failed} failed out of {len(cases)}")
    # blocking failure: any malformed that reached execution is critical
    if failed:
        print("BLOCKING: malformed call reached execution or valid not executed", file=sys.stderr)
        sys.exit(1)
    print("Smoke gate PASSED: valid->execute, malformed->rejected before execution")


def call_one(op_id: str, args_json: str, policy_json: str | None = None, version: str | None = None):
    Sandbox, Runtime, Harness = _imports()

    ok, args, err = parse_json_with_timeout(args_json, timeout_s=PARSE_TIMEOUT_S)
    if not ok:
        print(f"args JSON parse failed ({err}) — ParseTimeout or invalid JSON (timeout {PARSE_TIMEOUT_S}s)", file=sys.stderr)
        sys.exit(2)
    policy = None
    if policy_json:
        ok2, parsed, err2 = parse_json_with_timeout(policy_json, timeout_s=PARSE_TIMEOUT_S)
        if not ok2:
            print(f"policy JSON parse failed ({err2}) — timeout {PARSE_TIMEOUT_S}s", file=sys.stderr)
            sys.exit(2)
        policy = parsed
    harness = Harness(Sandbox(), Runtime())
    res = harness.call(op_id, args, payload_version=version, policy=policy)
    print(json.dumps(res, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Harness CLI")
    ap.add_argument("--smoke", action="store_true", help="Run smoke gate (valid->execute, malformed->rejected)")
    ap.add_argument("--measure-tokens", action="store_true", help="Measure token/char counts for variants A/B/C")
    ap.add_argument("--op", type=str, help="Operation id for single call")
    ap.add_argument("--args", type=str, help="JSON args for single call (e.g. '{\"query\":\"hi\"}')")
    ap.add_argument("--policy", type=str, help="JSON policy for single call")
    ap.add_argument("--payload-version", type=str, help="Payload version for drift tests")
    ap.add_argument("--variant", type=str, help="Unused; documents which variant model saw (C is runtime-invariant)")
    args = ap.parse_args()
    if args.measure_tokens or args.measure_tokens is False and False:
        measure_tokens()
        return
    if args.smoke:
        smoke()
        return
    if args.measure_tokens:
        measure_tokens()
        return
    if args.op:
        if not args.args:
            print("need --args JSON", file=sys.stderr)
            sys.exit(2)
        call_one(args.op, args.args, args.policy, args.payload_version)
        return
    ap.print_help()
    # default: show smoke if no args
    if len(sys.argv) == 1:
        measure_tokens()
        print("\n---\n")
        smoke()


if __name__ == "__main__":
    # support both --measure-tokens and --measure_tokens
    if "--measure-tokens" in sys.argv:
        pass
    # also accept dash variant
    main()
