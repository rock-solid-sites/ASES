#!/usr/bin/env python3
"""Validate corpus-530 40-line corpus: 24 well-formed in 6×4 + 12 malformed + 4 adversarial."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
corp = ROOT / "corpus.jsonl"
lines=[json.loads(l) for l in open(corp) if l.strip()]
kinds={}
for r in lines:
    kinds[r["kind"]]=kinds.get(r["kind"],0)+1
print(f"corpus.jsonl: {len(lines)} lines — {kinds}")
# check counts
assert len(lines)==40, f"expected 40 got {len(lines)}"
assert kinds.get("well_formed",0)==24, kinds
assert kinds.get("malformed",0)==12, kinds
assert kinds.get("adversarial",0)==4, kinds
# check well-formed 6×4
wf=[l for l in lines if l["kind"]=="well_formed"]
from collections import Counter
classes=Counter(l["class"] for l in wf)
print(f"well-formed classes: {classes}")
assert classes[1]==4 and classes[2]==4 and classes[3]==4 and classes[4]==4 and classes[5]==4 and classes[6]==4
# check IDs stable
import pathlib as pl
tasks=json.loads((ROOT/"tasks.json").read_text())
assert len(tasks["tasks"])==24
mal=json.loads((ROOT/"malformed-recovery.json").read_text())
assert len(mal["cases"])==12
adv=json.loads((ROOT/"adversarial.json").read_text())
assert len(adv["cases"])==4
# check op_ids exist in authoritative
schemas=json.loads((ROOT/"schemas/authoritative.json").read_text())
allowed={c["op_id"] for c in schemas["capabilities"]}
for r in lines:
    if r["kind"] in ("well_formed","malformed"):
        assert r["op"] in allowed or r["expected_code"]=="UnknownOperation", f"{r['id']} op {r['op']} not in allowed {allowed}"
# check adversarial distinct codes
codes=set(a["expected_code"] for a in json.loads((ROOT/"adversarial.json").read_text())["cases"])
assert codes=={"UnknownOperation","ValidationFailed","PolicyDenied","OutputValidationFailed"}, codes
print(f"adversarial distinct codes: {codes}")
# check minimal ≤20w summaries
minimal=json.loads((ROOT/"schemas/minimal.json").read_text())
for c in minimal["capabilities"]:
    wc=len(c["summary"].split())
    assert wc<=20, f"{c['op_id']} summary {wc} words >20: {c['summary']}"
print(f"minimal summaries all ≤20w")
# check enum literals preserved in minimal
for c in minimal["capabilities"]:
    auth = next(x for x in schemas["capabilities"] if x["op_id"]==c["op_id"])
    for pname, pschema in auth["inputSchema"]["properties"].items():
        if "enum" in pschema:
            mparam=next((p for p in c["params"] if p["name"]==pname), None)
            assert mparam and "enum" in mparam and mparam["enum"]==pschema["enum"], f"{c['op_id']}.{pname} enum not preserved visibly"
print("enum literals preserved visibly in minimal")
# hidden constraints present
hc=schemas.get("hidden_constraints",{})
assert "numeric_range" in hc and "string_pattern_format" in hc and "mutually_constrained_fields" in hc and "schema_constraints_causing_validation_failed" in hc
print("hidden constraints documented (numeric range, pattern/format, mutually constrained, schema constraint)")
print("PASS: corpus validation 40 lines, 6×4, enums, ≤20w, hidden constraints, distinct codes")
