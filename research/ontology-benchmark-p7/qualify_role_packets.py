#!/usr/bin/env python3
"""P7 post-hoc benchmark packet blinding qualification.

The primary P7 CI result is immutable. This checks a corrected v2 reviewer
packet after observing hint leakage in v1, with independent valid neighbors.
Not an independent ontology reviewer or general model performance test.
"""
import argparse
import copy
import json
from pathlib import Path
import hashlib
import time

HERE=Path(__file__).resolve().parent
BASE=json.loads((HERE/"blind-cases.json").read_text())
DESIGN=json.loads((HERE/"design-review-packet.json").read_text())
CONF=json.loads((HERE/"conformance-review-packet-v2.json").read_text())
SEEN_KEYWORDS={"expected","answer_key","ground_truth","defect_label","planted_fault","is_clean"}
PROHIBITED_CONFORMANCE_HINTS={"observed_trace","relevant_trace","design_rationale",
                              "expected_failure","builder_history","prior_review"}
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(pkt,role,original):
    if pkt.get("role")!=role: raise ValueError("ROLE_MISMATCH")
    cases=pkt.get("cases")
    if not isinstance(cases,list) or len(cases)!=3: raise ValueError("WRONG_CASE_COUNT")
    if len({c.get("id") for c in cases})!=3: raise ValueError("DUPLICATE_IDS")
    if {c["id"] for c in cases}!={c["id"] for c in original}: raise ValueError("CASE_MEMBERSHIP")
    originals={c["id"]:c for c in original}
    for c in cases:
        if c.get("role")!=role: raise ValueError("CROSS_ROLE_CASE")
        if SEEN_KEYWORDS.intersection(c): raise ValueError("ANSWER_LABEL_PRESENT")
        context=c.get("context",{})
        artifact=c.get("candidate",{})
        if SEEN_KEYWORDS.intersection(context)|SEEN_KEYWORDS.intersection(artifact):
            raise ValueError("ANSWER_LABEL_PRESENT")
        reference=originals[c["id"]]
        if role=="conformance":
            if "design_rationale" in context or "design_rationale" in artifact:
                raise ValueError("HISTORY_LEAKAGE")
            if PROHIBITED_CONFORMANCE_HINTS.intersection(artifact):
                raise ValueError("RESULT_HINT_LEAKAGE")
            if not context.get("specific_invariant") or not context.get("frozen_concepts"):
                raise ValueError("MISSING_FROZEN_COMPARATOR")
            expected={k:v for k,v in reference["candidate"].items()
                      if k not in ("observed_trace","relevant_trace")}
            if artifact!=expected: raise ValueError("NON_HINT_ARTIFACT_CHANGED")
        else:
            if not context.get("canonical_requirements") or not context.get("design_rationale"):
                raise ValueError("DESIGN_CONTEXT_ABSENT")
            if c["candidate"]!=reference["candidate"]: raise ValueError("DESIGN_ARTIFACT_CHANGED")
    return {"role":role,"checked":len(cases),"status":"PASS"}

def negative(base,role,original,name,mutate,reason):
    data=copy.deepcopy(base);mutate(data)
    try: validate(data,role,original)
    except ValueError as e:
        if str(e)!=reason: raise AssertionError(name+": unexpected "+str(e))
        return {"name":name,"status":"DETECTED","reason":str(e)}
    raise AssertionError(name+": invalid review packet escaped")

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",required=True)
    args=parser.parse_args();t=time.monotonic()
    original={role:[c for c in BASE["cases"] if c["role"]==role]
              for role in ["design","conformance"]}
    good=[validate(DESIGN,"design",original["design"]),
          validate(CONF,"conformance",original["conformance"])]
    bad=[
        negative(CONF,"conformance",original["conformance"],
                 "leaked_result_trace",lambda x:x["cases"][0]["candidate"].update(
                 observed_trace=["No violation observed"]), "RESULT_HINT_LEAKAGE"),
        negative(CONF,"conformance",original["conformance"],
                 "leaked_builder_history",lambda x:x["cases"][0]["context"].update(
                 design_rationale="Builder says this is correct"),"HISTORY_LEAKAGE"),
        negative(CONF,"conformance",original["conformance"],
                 "no_frozen_invariant",lambda x:x["cases"][0]["context"].pop(
                 "specific_invariant"),"MISSING_FROZEN_COMPARATOR"),
        negative(DESIGN,"design",original["design"],
                 "cross_role_record",lambda x:x["cases"][0].update(role="conformance"),
                 "CROSS_ROLE_CASE"),
        negative(DESIGN,"design",original["design"],
                 "answer_label_leak",lambda x:x["cases"][0].update(
                 expected="DEFECT"),"ANSWER_LABEL_PRESENT"),
        negative(CONF,"conformance",original["conformance"],
                 "artifact_mutated",lambda x:x["cases"][0]["candidate"].update(
                 implementation_excerpt=["replace actual source"]), "NON_HINT_ARTIFACT_CHANGED"),
    ]
    report={"status":"PASS","study":"EDASES-P7-PACKET-QUALIFICATION",
            "classification":"POST_HOC_CORRECTION_NOT_PREREGISTERED",
            "positive":good,"negative":bad,
            "source_packets":{
              "original_full_sha256":digest(HERE/"blind-cases.json"),
              "design_sha256":digest(HERE/"design-review-packet.json"),
              "conformance_v2_sha256":digest(HERE/"conformance-review-packet-v2.json")},
            "reviewer_runs":"NOT_RUN",
            "specificity":"Role-specific packet and source integrity only; no claim of model independence",
            "execution_ms":round((time.monotonic()-t)*1000,3)}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ASES_P7_PACKET_SUMMARY="+json.dumps({
      "status":"PASS","positive":len(good),"negative":len(bad),
      "execution_ms":report["execution_ms"],"out_bytes":out.stat().st_size,
      "reviewers":"NOT_RUN"},sort_keys=True))
if __name__=="__main__":main()
