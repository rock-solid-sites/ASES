#!/usr/bin/env python3
"""EDASES-P7: reconstruct P5 from original ZIP bytes and qualify blind review benchmark.

No model calls. Secret scoring labels are read only from the private GitLab checkout.
This is independent programmatic recomputation, NOT independent agent review.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import io
import json
import re
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EVIDENCE = HERE.parent / "testing-assurance-pilot" / "evidence"
PREPLAN = HERE.parent / "testing-assurance-pilot" / "P7-PREREGISTERED-PLAN-2026-11-02.md"
P5_MANIFEST = EVIDENCE / "P5-ARCHIVES-MANIFEST-2026-11-02.json"
PACKET = HERE / "blind-cases.json"
EXPECTED_STATES = {
    "correct": ("PASS", "PASS"),
    "duplicate": ("BEHAVIOR_FAIL", "BEHAVIOR_FAIL"),
    "early_ack": ("PASS", "BEHAVIOR_FAIL")
}
MARKER = {"before": "PREPARED", "after_sync": "DURABLE", "after_ack": "ACK"}
TARGET = {"reserved": 1, "charged": 40, "entries": 1, "ids": 1}
EMPTY = {"reserved": 0, "charged": 0, "entries": 0, "ids": 0}

def hash_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def fail(message: str) -> None:
    raise AssertionError(message)

def require(predicate: bool, message: str) -> None:
    if not predicate:
        fail(message)

def load_original_p5_archives() -> tuple[dict, dict]:
    manifest = json.loads(P5_MANIFEST.read_text())
    require(len(manifest["records"]) == 2, "Expected original two P5 archive records")
    out, archive_status = {}, {}
    for item in manifest["records"]:
        label = item["label"]
        archive = ROOT / item["archive_path"]
        blob = base64.b64decode(archive.read_text().strip(), validate=True)
        require(len(blob) == item["artifact_zip_bytes"], label+": ZIP size mismatch")
        require(hash_bytes(blob) == item["artifact_zip_sha256"], label+": ZIP sha256 mismatch")
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            require(z.testzip() is None, label+": ZIP member CRC mismatch")
            require("results/p5.json" in z.namelist(), label+": raw p5.json missing")
            raw = z.read("results/p5.json")
            report = json.loads(raw)
        out[label] = report
        archive_status[label] = {"source_pipeline":item["source_pipeline_id"],
                                 "source_job":item["source_job_id"],
                                 "zip_sha256":hash_bytes(blob),
                                 "zip_size":len(blob),
                                 "raw_result_sha256":hash_bytes(raw),
                                 "raw_result_bytes":len(raw)}
    return out, archive_status

def derive_check(check: dict) -> bool:
    return check["observed"] == check["expected"]

def derive_a(method: dict) -> dict:
    checks = method["checks"]
    require(len(checks) >= 6, "normal suite missing checks")
    mismatches = [c["check"] for c in checks if not derive_check(c)]
    return {"status":"PASS" if not mismatches else "BEHAVIOR_FAIL",
            "observations":len(checks),
            "mismatch_count":len(mismatches),
            "mismatch_names":mismatches,
            "stored_status_matches":("PASS" if not mismatches else "BEHAVIOR_FAIL") == method["status"]}

def derive_kill(trial: dict) -> dict:
    point = trial["point"]
    require(point in MARKER, "unrecognized checkpoint")
    markers = trial["observed_markers"]
    require(isinstance(markers,list) and MARKER[point] in markers,
            "required milestone not observed")
    require(trial["verified_signal"] == -9, "SIGKILL not observed as -9")
    expected = EMPTY if point == "before" else TARGET
    require(trial["expected_recovered_state"] == expected,
            "stored expected snapshot disagrees with frozen plan")
    state_correct = trial["recovered_state"] == expected
    reply_correct = trial["retry_reply"] == (["ACK"] if point == "before" else ["DUPLICATE"])
    retry_correct = trial["retry_state"] == TARGET
    result = state_correct and reply_correct and retry_correct
    require(result == trial["passed"], "Stored checkpoint pass flag differs from raw outcomes")
    require(len(trial["journal_sha256"]) == 64 and
            trial["journal_bytes"] >= 0, "Journal evidence metadata malformed")
    return {"point":point,"passed":result,
            "state_correct":state_correct,"retry_reply_correct":reply_correct,
            "retry_state_correct":retry_correct}

def derive_b(method: dict) -> dict:
    conventional = derive_a(method["conventional_component"])
    kills = [derive_kill(x) for x in method["kill_trials"]]
    require(len(kills) == 15, "fifteen fault-injection trials required")
    per_point = {point:{"pass":sum(x["passed"] for x in kills if x["point"] == point),
                        "fail":sum(not x["passed"] for x in kills if x["point"] == point)}
                 for point in MARKER}
    require(all(v["pass"]+v["fail"] == 5 for v in per_point.values()),
            "per-checkpoint sample count mismatch")
    status = "PASS" if conventional["status"] == "PASS" and all(x["passed"] for x in kills) else "BEHAVIOR_FAIL"
    return {"status":status,
            "stored_status_matches":status == method["status"],
            "conventional":conventional,
            "per_point":per_point}

def reconstruct():
    archived, provenance = load_original_p5_archives()
    summaries = {}
    for label, report in archived.items():
        expected_run_status = "FAIL" if label=="red_instrument_error" else "PASS"
        require(report["status"] == expected_run_status, "Original P5 aggregate status was changed")
        require(set(report["implementations"])=={"rust","haskell"}, "Source lacks both languages")
        out = {}
        for lang, modes in report["implementations"].items():
            require(set(modes)==set(EXPECTED_STATES), "Missing original and fault modes")
            out[lang] = {}
            for mode, approaches in modes.items():
                observed_a = derive_a(approaches["A"])
                observed_b = derive_b(approaches["B"])
                require(observed_a["stored_status_matches"] and observed_b["stored_status_matches"],
                        "Stored suite labels disagree with raw checks")
                if label == "green_corrected":
                    require((observed_a["status"], observed_b["status"]) == EXPECTED_STATES[mode],
                            f"Corrected {lang}/{mode} coverage differs from frozen P5 predictions")
                if mode == "early_ack" and label == "green_corrected":
                    require(observed_b["per_point"]["after_ack"]["fail"] == 5,
                            "Missing early ACK crash counterexample")
                if mode == "correct" and label == "green_corrected":
                    require(sum(v["fail"] for v in observed_b["per_point"].values())==0,
                            "Correct implementation did not preserve crash invariants")
                out[lang][mode] = {"conventional":observed_a, "qualified":observed_b}
        summaries[label]={"original_aggregate_result":report["status"],
                          "measured_from_per_check":out}
    # Independently compute arithmetic and frozen harness fixtures for the P5
    # mistake; commit IDs are proved by the exact GitHub source revision in CI.
    normal_diff = {"before_fixture_charge_cents":50,
                   "corrected_fixture_charge_cents":90,
                   "empty_journal_current_spend":0,
                   "cap_cents":80,
                   "before_fixture_exceeds_cap":50>80,
                   "corrected_fixture_exceeds_cap":90>80,
                   "classification":"BAD_ORACLE_IN_INITIAL_RUN"}
    require(normal_diff["before_fixture_exceeds_cap"] is False and
            normal_diff["corrected_fixture_exceeds_cap"] is True,
            "Frozen fixture arithmetic incorrect")
    for lang in ("rust","haskell"):
        initial = summaries["red_instrument_error"]["measured_from_per_check"][lang]["correct"]["conventional"]
        corrected = summaries["green_corrected"]["measured_from_per_check"][lang]["correct"]["conventional"]
        require("spend_cap_exceeded_deny" in initial["mismatch_names"],
                "First bad fixture's failing assertion not visible")
        require("spend_cap_exceeded_deny" not in corrected["mismatch_names"],
                "Corrected fixture's earlier mismatch still present")
    return summaries, provenance, normal_diff

def validate_packet(packet, key=None) -> dict:
    require(isinstance(packet,dict) and packet.get("schema_version")==1,
            "Invalid case packet schema_version")
    require(packet.get("reviewer_answer_key_in_packet") is False,
            "Packet claims answer key contamination")
    cases = packet.get("cases")
    require(isinstance(cases,list) and len(cases)==6,
            "Expected exactly six blind cases")
    ids = [case.get("id") for case in cases]
    require(len(set(ids))==6 and all(re.fullmatch(r"S[0-9]{2}",x or "") for x in ids),
            "Duplicate or invalid case ID")
    require(sorted([c.get("role") for c in cases])==["conformance"]*3+["design"]*3,
            "Role counts wrong")
    for case in cases:
        require(set(case)=={"id","role","artifact_type","question","context","candidate"},
                "Extra/unapproved case fields or answer leakage")
        require(isinstance(case["context"],dict) and isinstance(case["candidate"],dict)
                and case["question"] and case["context"] and case["candidate"],
                "Incomplete review context or artifact")
        if case["role"]=="design":
            require(case["artifact_type"]=="proposed_conceptual_model" and
                    "design_rationale" in case["context"] and
                    "canonical_requirements" in case["context"], "Design review context invalid")
        else:
            require(case["artifact_type"].startswith("completed_") and
                    "specific_invariant" in case["context"] and
                    "frozen_concepts" in case["context"] and
                    "design_rationale" not in case["context"],"Conformance clean-room context invalid")
    if key is not None:
        require(key.get("study")=="EDASES-P7" and
                key.get("not_for_reviewer_prompt") is True,
                "Missing private sealed key")
        k = key.get("cases",[])
        require({i["id"] for i in k}==set(ids),"Answer key case IDs inconsistent")
        require(sum(i["expected"]=="DEFECT" for i in k)==4 and
                sum(i["expected"]=="CLEAN" for i in k)==2,
                "Frozen 4/2 split not maintained")
        require(sum(i["role"]=="design" for i in k)==3 and
                sum(i["role"]=="conformance" for i in k)==3,
                "Answer key role mismatch")
        for c in cases:
            require(next(x for x in k if x["id"]==c["id"])["role"]==c["role"],
                    "Key role corrupted")
    return {"cases":len(cases),
            "role_counts":{"design":3,"conformance":3},
            "key_separate":True}

def deterministic_baseline(case: dict) -> dict:
    """Cheap fixed-invariant syntax baseline; NOT an ordinary human/LLM reviewer."""
    if case["role"]!="conformance":
        return {"flagged":False,"reason":"NO_GENERIC_SYNTAX_RULE"}
    raw="\n".join(case["candidate"].get("implementation_excerpt",[]))
    # Two *general* high-confidence rules for simple code-like artifacts.
    ack=raw.find("emit('ACK'")
    sync=raw.find("fsync(")
    if ack>=0 and sync>=0 and ack<sync:
        return {"flagged":True,"reason":"ACK_PRECEDES_FSYNC"}
    lines=raw.splitlines()
    for x in lines:
        if re.search(r"\bauthority_decision\s*=\s*['\"]ACCEPT['\"]",x):
            return {"flagged":True,"reason":"REVIEW_OUTCOME_ASSIGNING_AUTHORITY"}
    return {"flagged":False,"reason":"NO_GENERIC_SYNTAX_RULE"}

def qualify_baseline(packet,key):
    predictions={c["id"]:deterministic_baseline(c) for c in packet["cases"]}
    truth={c["id"]:c for c in key["cases"]}
    scores={"true_positive":0,"false_positive":0,"true_negative":0,"false_negative":0}
    for case in packet["cases"]:
        found=predictions[case["id"]]["flagged"]
        actual=truth[case["id"]]["expected"]=="DEFECT"
        name="true_positive" if found and actual else ("false_positive" if found else ("false_negative" if actual else "true_negative"))
        scores[name]+=1
    require(sum(scores.values())==6,"Expected 6 baseline classifications")
    return predictions,scores

def negative_packet_controls(packet):
    """Test sealed packet structure and role separation without revealing labels."""
    controls=[]
    def expect(label,mutator):
        copy_packet=copy.deepcopy(packet)
        mutator(copy_packet)
        try:
            validate_packet(copy_packet)
        except AssertionError as exc:
            controls.append({"test":label,"detected":True,"reason":str(exc)})
        else:
            fail("Bad case packet escaped validation: "+label)
    expect("duplicate_id", lambda x:x["cases"][1].update(id=x["cases"][0]["id"]))
    expect("unexpected_answer_label", lambda x:x["cases"][0].update(expected="DEFECT"))
    expect("no_frozen_claim", lambda x:x["cases"][1]["context"].pop("specific_invariant"))
    expect("conformance_process_history", lambda x:x["cases"][1]["context"].update(design_rationale="builder says it works"))
    expect("wrong_role", lambda x:x["cases"][0].update(role="conformance"))
    expect("missing_case", lambda x:x["cases"].pop())
    expect("answer_key_claim", lambda x:x.update(reviewer_answer_key_in_packet=True))
    return controls

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--gold",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--private-out",required=True)
    args=parser.parse_args()
    start=time.monotonic()
    packet_raw=PACKET.read_bytes()
    key_raw=Path(args.gold).read_bytes()
    packet=json.loads(packet_raw);key=json.loads(key_raw)
    packet_summary=validate_packet(packet,key)
    reconstruction,original_archives,fixture= reconstruct()
    bad_packets=negative_packet_controls(packet)
    baseline,score=qualify_baseline(packet,key)
    elapsed=round((time.monotonic()-start)*1000,3)
    # Public output intentionally excludes the sealed per-case label and
    # any case ID + prediction linkage to preserve reviewer blinding.
    public={
        "study":"EDASES-P7","result":"PASS_WITH_LIMITS",
        "packet_sha256":hash_bytes(packet_raw),"private_key_sha256":hash_bytes(key_raw),
        "plan_sha256":hash_bytes(PREPLAN.read_bytes()),
        "packet_qualification":packet_summary,
        "original_archives":original_archives,
        "source_first_p5_reconstruction":reconstruction,
        "frozen_fixture_arithmetic":fixture,
        "malformed_packet_controls":bad_packets,
        "baseline_summary": {
            "method":"CHEAP_SYNTAX_HEURISTIC",
            "not_ordinary_review":True,
            "not_an_independent_model":True,
            "aggregate_counts":score,
            "case_predictions_redacted":True
        },
        "review_runs":{
            "ordinary_model_reviewer":"NOT_RUN",
            "ontology_design_reviewer":"NOT_RUN",
            "ontology_conformance_reviewer":"NOT_RUN",
            "independent_P5_human_or_model_review":"NOT_RUN"
        },
        "promoted_method":"NO",
        "known_limits":[
            "Source-first deterministic recomputation by the same assistant is not independently routed model review",
            "Six authored cases do not estimate real-world reviewer performance",
            "A syntax heuristic is not equivalent to baseline ordinary code/model review",
            "Model-family provenance, prompt isolation, token cost and actual clean-room reviewer responses remain NOT_OBSERVED",
            "Ground truth of benchmark case concepts has not been independently validated"
        ],
        "elapsed_ms":elapsed
    }
    private={
        "study":"EDASES-P7","public_sha256":None,
        "expected_labels":key["cases"],"predictions":baseline,
        "score":score,"label_store":"PRIVATE_GITLAB",
        "reviewer_results":"NOT_RUN",
        "key_hash":hash_bytes(key_raw)
    }
    public_path=Path(args.out); public_path.parent.mkdir(parents=True,exist_ok=True)
    public_path.write_text(json.dumps(public,sort_keys=True,indent=2)+"\n")
    private["public_sha256"]=hash_bytes(public_path.read_bytes())
    private_path=Path(args.private_out);private_path.parent.mkdir(parents=True,exist_ok=True)
    private_path.write_text(json.dumps(private,sort_keys=True,indent=2)+"\n")
    print("ASES_P7_SUMMARY="+json.dumps({
        "result":public["result"],"case_count":packet_summary["cases"],
        "p5_original_archives_recovered":len(original_archives),
        "invalid_packets_detected":len(bad_packets),
        "baseline_aggregate":score,
        "real_model_reviews":"NOT_RUN",
        "duration_ms":elapsed,
        "public_bytes":public_path.stat().st_size,
        "private_bytes":private_path.stat().st_size,
        "private_result_present":True
    },sort_keys=True))
if __name__=="__main__":
    main()
