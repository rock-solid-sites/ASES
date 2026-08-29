"""Runtime — authoritative validation + policy + dispatch.

Architecture:
  model (variant C only) -> sandbox (allowed ∈ preselected) -> runtime validation
    (authoritative JSON Schema) -> policy -> execution

Invariants:
- No silent reshape/coercion/retry before runtime validation sees the call.
- Authoritative schema text is never exposed to the model path.
- Every call logs {op_id, arguments, validation_result, error, executed, latency_ms, version}.
- executed == false for every expected-rejection case; execution of invalid call is blocking failure.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema  # type: ignore
    from jsonschema import Draft7Validator  # type: ignore

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMAS = HERE.parent / "capabilities" / "authoritative" / "schemas.json"

# In-memory artefact store for execution simulation (not authoritative persistence)
_ARTEFACT_STORE: Dict[str, Dict[str, Any]] = {}
_REVIEW_STORE: List[Dict[str, Any]] = []


class Runtime:
    def __init__(self, schemas_path: Optional[Path] = None, version: Optional[str] = None):
        path = schemas_path or DEFAULT_SCHEMAS
        data = json.loads(path.read_text())
        self.version: str = version or data.get("version", "0.1.0")
        # index by op_id -> capability dict
        self.capabilities: Dict[str, Dict[str, Any]] = {c["op_id"]: c for c in data["capabilities"]}
        self.validators: Dict[str, Any] = {}
        if HAS_JSONSCHEMA:
            for op_id, cap in self.capabilities.items():
                schema = cap.get("inputSchema")
                if schema is not None:
                    # Draft7Validator handles the authoritative input schema
                    self.validators[op_id] = Draft7Validator(schema)

    def validate(self, op_id: str, arguments: Dict[str, Any], payload_version: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate against authoritative schema. Returns (ok, error)."""
        if op_id not in self.capabilities:
            return False, {
                "code": "UnknownOperation",
                "op_id": op_id,
                "hint": "op_id not in authoritative registry",
                "boundary": "runtime",
            }
        # version check if payload carries version (drift tests C)
        if payload_version is not None and payload_version != self.capabilities[op_id].get("version", self.version):
            return False, {
                "code": "VersionMismatch",
                "op_id": op_id,
                "expected_version": self.capabilities[op_id].get("version", self.version),
                "actual_version": payload_version,
                "boundary": "runtime",
            }
        # also check global version drift: authoritative version mismatch
        # (when derived description is stale) — the harness caller can pass payload_version

        cap = self.capabilities[op_id]
        schema = cap.get("inputSchema")
        if schema is None:
            return True, None

        if HAS_JSONSCHEMA:
            validator = self.validators[op_id]
            errors = sorted(validator.iter_errors(arguments), key=lambda e: list(e.path))
            if errors:
                e = errors[0]
                field = ".".join(str(p) for p in e.path) if e.path else (".".join(str(p) for p in e.absolute_path) if e.absolute_path else None)
                # constraint name
                constraint = e.validator
                got = e.instance
                # truncate got for logging
                try:
                    got_repr = json.dumps(got)[:200]
                except Exception:
                    got_repr = str(got)[:200]
                return False, {
                    "code": "ValidationFailed",
                    "field": field,
                    "constraint": constraint,
                    "got": got_repr,
                    "message": e.message,
                    "schema_version": cap.get("version", self.version),
                    "op_id": op_id,
                    "boundary": "runtime",
                }
            return True, None
        else:
            # minimal fallback validation (no jsonschema lib) — checks required + types + enum + patterns
            return self._fallback_validate(schema, arguments, op_id, cap.get("version", self.version))

    def _fallback_validate(self, schema: Dict[str, Any], args: Dict[str, Any], op_id: str, schema_version: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        # Very small subset: required, additionalProperties, type, enum, pattern, minLength/maxLength, minimum/maximum
        import re as regex

        required = schema.get("required", [])
        for r in required:
            if r not in args:
                return False, {"code": "ValidationFailed", "field": r, "constraint": "required", "got": None, "message": f"'{r}' is required", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            for k in args:
                if k not in allowed:
                    return False, {"code": "ValidationFailed", "field": k, "constraint": "additionalProperties", "got": k, "message": f"Additional property '{k}' not allowed", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
        props = schema.get("properties", {})
        for pname, pschema in props.items():
            if pname not in args:
                continue
            val = args[pname]
            expected_type = pschema.get("type")
            if expected_type:
                if expected_type == "string" and not isinstance(val, str):
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "type", "got": type(val).__name__, "message": f"'{pname}' should be string", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if expected_type == "integer" and not isinstance(val, int):
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "type", "got": type(val).__name__, "message": f"'{pname}' should be integer", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if expected_type == "number" and not isinstance(val, (int, float)):
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "type", "got": type(val).__name__, "message": f"'{pname}' should be number", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if expected_type == "boolean" and not isinstance(val, bool):
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "type", "got": type(val).__name__, "message": f"'{pname}' should be boolean", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if expected_type == "array" and not isinstance(val, list):
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "type", "got": type(val).__name__, "message": f"'{pname}' should be array", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if expected_type == "object" and not isinstance(val, dict):
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "type", "got": type(val).__name__, "message": f"'{pname}' should be object", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
            if "enum" in pschema and val not in pschema["enum"]:
                return False, {"code": "ValidationFailed", "field": pname, "constraint": "enum", "got": val, "message": f"'{val}' is not one of {pschema['enum']}", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
            if isinstance(val, str):
                if "minLength" in pschema and len(val) < pschema["minLength"]:
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "minLength", "got": val[:50], "message": f"'{pname}' too short", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if "maxLength" in pschema and len(val) > pschema["maxLength"]:
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "maxLength", "got": val[:50], "message": f"'{pname}' too long", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if "pattern" in pschema:
                    if not regex.match(pschema["pattern"], val):
                        return False, {"code": "ValidationFailed", "field": pname, "constraint": "pattern", "got": val, "message": f"'{pname}' does not match pattern {pschema['pattern']}", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
            if isinstance(val, int) and not isinstance(val, bool):
                if "minimum" in pschema and val < pschema["minimum"]:
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "minimum", "got": val, "message": f"'{pname}' below minimum", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
                if "maximum" in pschema and val > pschema["maximum"]:
                    return False, {"code": "ValidationFailed", "field": pname, "constraint": "maximum", "got": val, "message": f"'{pname}' above maximum", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
            # array items check shallow
            if isinstance(val, list) and "items" in pschema:
                items_schema = pschema["items"]
                for idx, item in enumerate(val):
                    if "pattern" in items_schema and isinstance(item, str):
                        if not regex.match(items_schema["pattern"], item):
                            return False, {"code": "ValidationFailed", "field": f"{pname}[{idx}]", "constraint": "pattern", "got": item, "message": f"item does not match pattern", "schema_version": schema_version, "op_id": op_id, "boundary": "runtime"}
        return True, None

    def policy_check(self, op_id: str, arguments: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Policy boundary — only reached if validation passed.

        Default policy: deny if op_id in policy['deny'] or resource not owned.
        Tests pass explicit deny sets to exercise D2.
        """
        if policy is None:
            return True, None
        denied = set(policy.get("deny", []))
        if op_id in denied:
            return False, {
                "code": "PolicyDenied",
                "policy": policy.get("policy_name", "test-deny"),
                "reason": f"op {op_id} denied by policy",
                "op_id": op_id,
                "boundary": "policy",
            }
        # per-resource deny example: artefact_id ownership check
        denied_resources = set(policy.get("deny_resources", []))
        for key in ("id", "artefact_id", "source_id"):
            if key in arguments and arguments[key] in denied_resources:
                return False, {
                    "code": "PolicyDenied",
                    "policy": policy.get("policy_name", "resource-ownership"),
                    "reason": f"resource {arguments[key]} denied",
                    "op_id": op_id,
                    "boundary": "policy",
                }
        return True, None

    def execute(self, op_id: str, arguments: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Simulated execution — only reached if both boundaries passed.

        Returns (ok, result_or_error). Simulated side-effects are isolated to
        the in-memory store and are not persisted beyond the process.
        """
        # Minimal simulation: return canned shaped outputs matching outputSchema
        # for smoke tests; real logic not required for validation tests.
        now = "2026-08-29T00:00:00Z"
        if op_id == "search_artefacts":
            return True, {"items": [], "total": 0, "has_more": False}
        if op_id == "get_artefact":
            aid = arguments.get("id", "art_unknown")
            # simulate not-found for specific id pattern
            if aid == "art_missing" or aid.startswith("art_notfound"):
                return False, {"code": "NotFound", "resource_type": "artefact", "resource_id": aid}
            return True, {"id": aid, "type": "spec", "title": "Example", "status": "draft", "created_at": now}
        if op_id == "create_artefact":
            import uuid

            nid = f"art_{uuid.uuid4().hex[:8]}"
            return True, {"id": nid, "type": arguments["type"], "title": arguments["title"], "status": "draft"}
        if op_id == "update_artefact_status":
            return True, {"id": arguments["id"], "previous_status": "draft", "new_status": arguments["status"]}
        if op_id == "create_review":
            import uuid

            rid = f"rev_{uuid.uuid4().hex[:8]}"
            return True, {"review_id": rid, "artefact_id": arguments["artefact_id"], "verdict": arguments["verdict"], "created_at": now}
        if op_id == "set_severity":
            return True, {"artefact_id": arguments["artefact_id"], "previous_level": "low", "new_level": arguments["level"]}
        if op_id == "set_artefact_state":
            return True, {"artefact_id": arguments["artefact_id"], "previous_state": "draft", "new_state": arguments["state"]}
        if op_id == "query_metrics":
            return True, {"items": [{"key": arguments.get("group_by", "all"), "count": 1, "avg_score": 0.5}], "total": 1}
        if op_id == "list_reviews":
            return True, {"reviews": [], "total": 0}
        if op_id == "get_capability_schema":
            target = arguments["op_id"]
            if target not in self.capabilities:
                return False, {"code": "NotFound", "resource_type": "capability", "resource_id": target}
            cap = self.capabilities[target]
            # version mismatch check if version requested
            if "version" in arguments and arguments["version"] != cap.get("version", self.version):
                return False, {"code": "VersionMismatch", "expected_version": cap.get("version", self.version), "actual_version": arguments["version"], "op_id": target}
            return True, {"op_id": target, "version": cap.get("version", self.version), "schema": cap.get("inputSchema")}
        if op_id == "submit_evidence":
            aids = arguments.get("evidence_items", [])
            import uuid

            eids = [f"ev_{uuid.uuid4().hex[:6]}" for _ in aids]
            return True, {"artefact_id": arguments["artefact_id"], "accepted_count": len(eids), "evidence_ids": eids}
        if op_id == "link_artefacts":
            linked = [{"target_id": tid, "relation": arguments["relation"]} for tid in arguments["target_ids"]]
            return True, {"source_id": arguments["source_id"], "linked": linked, "created": len(linked)}
        if op_id == "archive_artefact":
            if arguments["artefact_id"] == "art_already_archived":
                return False, {"code": "Conflict", "reason": "already archived"}
            return True, {"artefact_id": arguments["artefact_id"], "archived_at": now, "previous_status": "active"}
        if op_id == "validate_payload":
            # delegate to validate logic for the inner op
            inner_op = arguments["op_id"]
            payload = arguments["payload"]
            strict = arguments.get("strict", True)
            ok, err = self.validate(inner_op, payload)
            if ok:
                return True, {"valid": True, "normalized": payload}
            else:
                return True, {"valid": False, "errors": [{"field": err.get("field", ""), "code": err.get("code", "ValidationFailed"), "constraint": err.get("constraint", "")}]}
        # default: echo
        return True, {"op_id": op_id, "arguments": arguments, "executed_at": now}


class Harness:
    """End-to-end harness: sandbox → runtime validation → policy → execution with logging."""

    def __init__(self, sandbox: Optional["Sandbox"] = None, runtime: Optional[Runtime] = None):
        if sandbox is not None:
            self.sandbox = sandbox
        else:
            try:
                from .sandbox import Sandbox as _Sandbox
                self.sandbox = _Sandbox()
            except ImportError:
                import sys as _sys
                from pathlib import Path as _Path
                _sys.path.insert(0, str(_Path(__file__).resolve().parent))
                from sandbox import Sandbox as _Sandbox
                self.sandbox = _Sandbox()
        if runtime is not None:
            self.runtime = runtime
        else:
            self.runtime = Runtime()

    def call(
        self,
        op_id: str,
        arguments: Dict[str, Any],
        payload_version: Optional[str] = None,
        policy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Full call: returns dict with validation_result, error, executed, result, latency_ms, version."""
        start = time.time()
        trace: List[str] = []

        # 1) sandbox gate
        ok, err = self.sandbox.check(op_id)
        trace.append("sandbox:allowed" if ok else f"sandbox:rejected:{err['code'] if err else ''}")
        if not ok:
            latency = int((time.time() - start) * 1000)
            return {
                "op_id": op_id,
                "arguments": arguments,
                "validation_result": "rejected:sandbox",
                "error": err,
                "executed": False,
                "result": None,
                "latency_ms": latency,
                "version": self.runtime.version,
                "trace": trace,
            }

        # 2) runtime validation
        ok, err = self.runtime.validate(op_id, arguments, payload_version)
        trace.append("validation:pass" if ok else f"validation:rejected:{err['code'] if err else ''}")
        if not ok:
            latency = int((time.time() - start) * 1000)
            return {
                "op_id": op_id,
                "arguments": arguments,
                "validation_result": "rejected:validation",
                "error": err,
                "executed": False,
                "result": None,
                "latency_ms": latency,
                "version": self.runtime.version,
                "trace": trace,
            }

        # 3) policy
        ok, err = self.runtime.policy_check(op_id, arguments, policy)
        trace.append("policy:pass" if ok else f"policy:rejected:{err['code'] if err else ''}")
        if not ok:
            latency = int((time.time() - start) * 1000)
            return {
                "op_id": op_id,
                "arguments": arguments,
                "validation_result": "rejected:policy",
                "error": err,
                "executed": False,
                "result": None,
                "latency_ms": latency,
                "version": self.runtime.version,
                "trace": trace,
            }

        # 4) execution
        ok, result = self.runtime.execute(op_id, arguments)
        trace.append("execution:ok" if ok else f"execution:error:{result.get('code') if isinstance(result, dict) else ''}")
        latency = int((time.time() - start) * 1000)
        if not ok:
            # execution-level errors (NotFound, Conflict) — still counted as executed==True? No, execution attempted.
            # For gate semantics: execution happened but returned typed error.
            # Keep executed=True to distinguish from validation-rejected.
            return {
                "op_id": op_id,
                "arguments": arguments,
                "validation_result": "executed:error",
                "error": result,
                "executed": True,
                "result": None,
                "latency_ms": latency,
                "version": self.runtime.version,
                "trace": trace,
            }
        return {
            "op_id": op_id,
            "arguments": arguments,
            "validation_result": "executed:ok",
            "error": None,
            "executed": True,
            "result": result,
            "latency_ms": latency,
            "version": self.runtime.version,
            "trace": trace,
        }
