"""Provider registry v0: strict core envelope, extensible typed capabilities.

Research prototype. Validation is intentionally independent of any provider SDK.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone

ID = re.compile(r"^[a-z][a-z0-9._-]{0,95}$")
KINDS = {"execution", "inference", "deployment", "orchestration", "storage",
         "billing", "observability", "provisioning", "other"}
STATES = {"candidate", "documented", "account_verified", "active", "degraded",
          "draining", "retired"}
SOURCES = {"official_documentation", "provider_api", "provider_invoice",
           "runtime_observation", "manual", "inferred"}
REQUIRED = {"schema_version", "provider_id", "revision", "state", "products", "facts"}
OPTIONAL = {"display_name", "relationships", "extensions"}
PRODUCT = {"product_id", "kind", "capabilities", "meters"}
FACT = {"key", "value", "source", "observed_at", "status"}
METER = {"meter_id", "unit", "measurement", "period"}
MEASUREMENTS = {"wall_time", "active_cpu_time", "core_time", "provisioned_memory_time",
                "storage_time", "requests", "tokens", "builds", "currency",
                "events", "custom"}
PERIODS = {"per_event", "daily", "monthly", "billing_cycle", "rolling", "lifetime", "custom"}
STATUSES = {"verified", "unverified", "unknown", "stale", "disputed"}

def _id(value, field):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError(f"invalid {field}: {value!r}")

def _object(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be object")

def _fields(value, required, optional, name):
    _object(value, name)
    if not required <= value.keys() or value.keys() - required - optional:
        raise ValueError(f"invalid fields for {name}")

def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be string")
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("invalid timestamp") from e
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError("timestamp must be timezone aware")

def validate(manifest):
    _fields(manifest, REQUIRED, OPTIONAL, "manifest")
    if manifest["schema_version"] != 1:
        raise ValueError("unsupported schema version")
    _id(manifest["provider_id"], "provider_id")
    if type(manifest["revision"]) is not int or manifest["revision"] < 1:
        raise ValueError("invalid revision")
    if manifest["state"] not in STATES:
        raise ValueError("invalid state")
    products = manifest["products"]
    if not isinstance(products, list):
        raise ValueError("products must be array")
    seen_products = set()
    for p in products:
        _fields(p, PRODUCT, {"configuration_policy", "configurations", "lifecycle",
                             "dependencies", "extensions"}, "product")
        _id(p["product_id"], "product_id")
        if p["product_id"] in seen_products:
            raise ValueError("duplicate product")
        seen_products.add(p["product_id"])
        if p["kind"] not in KINDS:
            raise ValueError("invalid product kind")
        if not isinstance(p["capabilities"], list) or not all(isinstance(c, dict) and
            isinstance(c.get("type"), str) and c["type"] and
            isinstance(c.get("parameters", {}), dict) for c in p["capabilities"]):
            raise ValueError("invalid capabilities")
        if not isinstance(p["meters"], list):
            raise ValueError("invalid meters")
        meter_ids = set()
        for m in p["meters"]:
            _fields(m, METER, {"billing_owner", "pricing", "extensions"}, "meter")
            _id(m["meter_id"], "meter_id")
            if m["meter_id"] in meter_ids:
                raise ValueError("duplicate meter")
            meter_ids.add(m["meter_id"])
            if not isinstance(m["unit"], str) or not m["unit"]:
                raise ValueError("invalid unit")
            if m["measurement"] not in MEASUREMENTS or m["period"] not in PERIODS:
                raise ValueError("invalid measurement or period")
        if "configurations" in p:
            if not isinstance(p["configurations"], list):
                raise ValueError("invalid configurations")
            config_ids = set()
            for c in p["configurations"]:
                _fields(c, {"configuration_id", "properties"}, {"extensions"}, "configuration")
                _id(c["configuration_id"], "configuration_id")
                if c["configuration_id"] in config_ids or not isinstance(c["properties"], dict):
                    raise ValueError("invalid or duplicate configuration")
                config_ids.add(c["configuration_id"])
    if not isinstance(manifest["facts"], list):
        raise ValueError("facts must be array")
    for f in manifest["facts"]:
        _fields(f, FACT, {"effective_at", "expires_at", "reference", "extensions"}, "fact")
        if not isinstance(f["key"], str) or not f["key"]:
            raise ValueError("invalid fact key")
        if f["source"] not in SOURCES or f["status"] not in STATUSES:
            raise ValueError("invalid fact source or status")
        _timestamp(f["observed_at"])
        for key in ("effective_at", "expires_at"):
            if key in f:
                _timestamp(f[key])
        if f["status"] == "unknown" and f["value"] is not None:
            raise ValueError("unknown facts must have null value")
        if f["status"] == "verified" and f["source"] == "inferred":
            raise ValueError("inference cannot be provider-verified")
    if "relationships" in manifest:
        if not isinstance(manifest["relationships"], list):
            raise ValueError("invalid relationships")
        for r in manifest["relationships"]:
            _fields(r, {"type", "from", "to"}, {"parameters"}, "relationship")
            if not all(isinstance(r[k], str) and r[k] for k in ("type", "from", "to")):
                raise ValueError("invalid relationship")
    if "extensions" in manifest and not isinstance(manifest["extensions"], dict):
        raise ValueError("invalid extensions")
    # No NaN, infinity, arbitrary Python objects or non-JSON wire types.
    json.dumps(manifest, allow_nan=False)
    return True

def schedulable(manifest):
    validate(manifest)
    return manifest["state"] == "active"
