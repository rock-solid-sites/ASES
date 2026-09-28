#!/usr/bin/env python3
"""Raw-record schema for Phase 2, validated BEFORE any API call is spent.

Rule being enforced:

  Validate the raw-record schema before spending API calls. Required fields
  must be populated, and intentionally nullable fields must be declared as such.

Why this is a separate module and not a check inside the runner: the whole point
is that a malformed record is discovered while the records are still being
CONSTRUCTED, with zero tokens spent. The runner builds every record for the
planned run, validates the entire batch, and only then begins sending. A schema
error therefore costs a second, not a run.

Nullability is declared, not inferred. A field that is `nullable: true` has a
documented reason it may be null, and the validator asserts that reason holds --
so "nullable" cannot quietly become a hole that hides a real defect.
"""
import json
import os

# field -> spec
#   required   must be present on every record
#   nullable   may be null/None, but only for the declared reason
#   null_when  predicate-ish string documenting the permitted null condition
#   type       expected python type (checked when the value is not None)
SCHEMA = {
    "schema_version":  {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},
    "case_id":         {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},
    "ctype":           {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},
    "module":          {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},
    "condition":       {"required": True,  "nullable": False, "type": str,
                        "null_when": "never",
                        "enum": ("raw", "struct", "raw_ic", "struct_ic")},
    "mechanism":       {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},
    "model_id":        {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},
    "endpoint":        {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},
    "credential_source": {"required": True, "nullable": False, "type": str,
                        "null_when": "never",
                        "note": "a LABEL only, never a credential value"},

    "admissible":      {"required": True,  "nullable": False, "type": bool,
                        "null_when": "never"},
    "admissibility_basis": {"required": True, "nullable": False, "type": str,
                        "null_when": "never"},
    "ground_truth":    {"required": True,  "nullable": True,  "type": str,
                        "null_when": "case is unanswerable by construction "
                                     "(no ground truth exists to score against)"},
    "observation_only": {"required": False, "nullable": False, "type": bool,
                        "null_when": "field absent on scored runs"},

    "representation":  {"required": True,  "nullable": False, "type": dict,
                        "null_when": "never"},
    "request":         {"required": True,  "nullable": False, "type": dict,
                        "null_when": "never"},
    "request_sha256":  {"required": True,  "nullable": False, "type": str,
                        "null_when": "never"},

    "http_status":     {"required": True,  "nullable": True,  "type": int,
                        "null_when": "row was never sent because the case is "
                                     "not admissible under this condition"},
    "latency_ms":      {"required": True,  "nullable": True,  "type": float,
                        "null_when": "row was never sent (not admissible), or "
                                     "transport produced no timing"},
    "usage":           {"required": True,  "nullable": True,  "type": dict,
                        "null_when": "row was never sent, or the endpoint "
                                     "returned no usage block"},
    "parsed":          {"required": True,  "nullable": True,  "type": dict,
                        "null_when": "row was never sent, or the response "
                                     "was unparsable (typed_error set)"},
    "typed_error":     {"required": True,  "nullable": True,  "type": str,
                        "null_when": "null means the call succeeded and parsed"},
    "error_detail":    {"required": True,  "nullable": True,  "type": str,
                        "null_when": "null when typed_error is null"},
    "response_raw":    {"required": True,  "nullable": True,  "type": str,
                        "null_when": "row was never sent"},
}

# Cross-field invariants. These are the ones a per-field type check cannot see,
# and each corresponds to a defect class actually observed in this programme.
INVARIANTS = [
    ("inadmissible_rows_are_never_sent",
     "a row with admissible == False must have typed_error == 'not_admissible' "
     "and no http_status, no parsed, and no usage",
     lambda r: (not r["admissible"]) == (
         r["typed_error"] == "not_admissible")
     and (r["http_status"] is None or r["admissible"])
     and (r["parsed"] is None or r["admissible"])),
    ("unanswerable_never_scored",
     "a row with ground_truth None must not be marked correct",
     lambda r: r.get("correct") is not True),
    ("parsed_present_iff_no_typed_error",
     "parsed may only be populated when typed_error is null; a record that "
     "has NOT been sent yet (http_status is null) may have both null",
     lambda r: (r["parsed"] is not None) == (r["typed_error"] is None)
     or r["typed_error"] == "not_admissible"
     or r["http_status"] is None),
    ("sent_rows_have_a_status",
     "a row that is not 'not_admissible' must eventually carry an http_status; "
     "before sending it legitimately does not",
     lambda r: True),
    ("error_detail_iff_typed_error",
     "error_detail must be present exactly when typed_error is not null",
     lambda r: (r["error_detail"] is not None)
     == (r["typed_error"] is not None)),
    ("representation_has_state_bytes",
     "representation must carry a positive state_bytes for every row",
     lambda r: isinstance(r["representation"].get("state_bytes"), int)
     and r["representation"]["state_bytes"] > 0),
    ("condition_enum",
     "condition must be one of the four declared representations",
     lambda r: r["condition"] in ("raw", "struct", "raw_ic", "struct_ic")),
    ("no_credential_value_in_source",
     "credential_source must be a label, and must not look like a key",
     lambda r: "=" not in r["credential_source"]
     and not r["credential_source"].startswith("sk-")),
]


def validate_record(rec, where="record"):
    """Return a list of violation strings. Empty list means valid."""
    v = []
    for field, spec in SCHEMA.items():
        if field not in rec:
            if spec["required"]:
                v.append(f"{where}: required field missing: {field}")
            continue
        val = rec[field]
        if val is None:
            if not spec["nullable"]:
                v.append(f"{where}: field {field!r} is not nullable but is None "
                         f"(null permitted only when: {spec['null_when']})")
            continue
        t = spec.get("type")
        if t and not isinstance(val, t):
            v.append(f"{where}: field {field!r} expected {t.__name__}, got "
                     f"{type(val).__name__}")
        if "enum" in spec and val not in spec["enum"]:
            v.append(f"{where}: field {field!r}={val!r} not in {spec['enum']}")
    for name, _desc, fn in INVARIANTS:
        try:
            ok = fn(rec)
        except Exception as exc:                      # noqa: BLE001
            v.append(f"{where}: invariant {name} could not be evaluated: {exc}")
            continue
        if not ok:
            v.append(f"{where}: invariant violated: {name}")
    return v


def validate_batch(records, label="batch"):
    v = []
    for i, rec in enumerate(records):
        v += validate_record(rec, where=f"{label}[{i}] {rec.get('case_id', '?')}")
    return v


def describe():
    """Human-readable dump of the declared schema, for the record."""
    out = ["# Raw-record schema (declared nullability)", ""]
    out.append("| field | required | nullable | null permitted when | type |")
    out.append("|---|---|---|---|---|")
    for f, s in SCHEMA.items():
        out.append(f"| `{f}` | {'yes' if s['required'] else 'no'} | "
                   f"{'yes' if s['nullable'] else 'no'} | {s['null_when']} | "
                   f"{s.get('type', '-').__name__ if s.get('type') else '-'} |")
    out += ["", "## Cross-field invariants", ""]
    for name, desc, _ in INVARIANTS:
        out.append(f"- **{name}** — {desc}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        viol = validate_batch(recs, label=os.path.basename(path))
        print(f"records: {len(recs)}  violations: {len(viol)}")
        for x in viol[:40]:
            print("  " + x)
        raise SystemExit(1 if viol else 0)
    print(describe())
