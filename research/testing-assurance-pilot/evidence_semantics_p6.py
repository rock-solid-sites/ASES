#!/usr/bin/env python3
"""P6: experimental, dependency-free semantic evidence envelope qualifier.

This is deliberately NOT a universal schema, production gate or independent reviewer.
Replays the ORIGINAL P5 CI artifact ZIPs and appends interpretations separately.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import io
import json
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EVIDENCE = HERE / "evidence"
PLAN = HERE / "P6-PREREGISTERED-PLAN-2026-11-02.md"
P5PLAN = HERE / "P5-PREREGISTERED-PLAN-2026-11-02.md"
MANIFEST = EVIDENCE / "P5-ARCHIVES-MANIFEST-2026-11-02.json"
ALLOWED_KINDS = {"EXECUTION", "ASSERTION", "INSTRUMENT", "CLAIM",
                 "ARCHIVE", "DECISION", "REVIEW", "CORRECTION"}
REQUIRED_KINDS = {"EXECUTION", "ASSERTION", "INSTRUMENT", "CLAIM",
                  "ARCHIVE", "DECISION", "REVIEW"}
P5_SOURCE = {
    "red_instrument_error": "b20bc9dc7829ae7f4c04fe718c371b12ad958fea",
    "green_corrected": "0e25c4b8970a0064af4d4169f68f5ac7e0cfab2e",
}

def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

class InvalidEvidence(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)

def require(condition: bool, code: str) -> None:
    if not condition:
        raise InvalidEvidence(code)

def nonblank(value) -> bool:
    return isinstance(value, str) and bool(value.strip())

def validate(record: dict) -> None:
    require(isinstance(record, dict) and
            set(record) == {"schema_version", "run", "events"}, "ROOT_FIELDS")
    require(record["schema_version"] == 1, "SCHEMA_VERSION")
    run = record["run"]
    require(isinstance(run, dict) and all(nonblank(run.get(x)) for x in
             ("id", "study", "provider", "source_revision", "plan_sha256")),
            "RUN_PROVENANCE")
    events = record["events"]
    require(isinstance(events, list) and events, "NO_EVENTS")
    ids: set[str] = set()
    seen_types: set[str] = set()
    evidence_by_id: dict[str, dict] = {}
    instrument_assessment = None
    for event in events:
        require(isinstance(event, dict) and
                set(event) == {"id", "kind", "run_id", "source_refs", "payload"},
                "EVENT_SHAPE")
        eid, kind = event["id"], event["kind"]
        require(nonblank(eid), "EVENT_ID")
        require(eid not in ids, "DUPLICATE_EVENT")
        require(kind in ALLOWED_KINDS, "BAD_KIND")
        require(event["run_id"] == run["id"], "RUN_MISMATCH")
        require(isinstance(event["source_refs"], list) and
                len(event["source_refs"]) > 0 and
                all(nonblank(x) for x in event["source_refs"]), "NO_EVIDENCE")
        p = event["payload"]
        require(isinstance(p, dict), "PAYLOAD_SHAPE")
        if kind == "EXECUTION":
            require(p.get("job_outcome") in
                    {"SUCCESS", "FAILED", "ERROR", "SKIPPED", "CANCELLED"},
                    "BAD_ENUM")
            require(p.get("suite_result") in
                    {"PASS", "FAIL", "ERROR", "INCONCLUSIVE"}, "BAD_ENUM")
            require(isinstance(p.get("provider_job_id"), int) and
                    nonblank(p.get("source_revision")), "EXECUTION_FIELDS")
        elif kind == "ASSERTION":
            require(p.get("result") in {"PASS", "FAIL", "INCONCLUSIVE"},
                    "BAD_ENUM")
            total, failed = p.get("total_count"), p.get("failed_count")
            require(type(total) is int and type(failed) is int and
                    0 <= failed <= total and total > 0, "ASSERTION_COUNT")
            require(not (p["result"] == "PASS" and failed > 0) and
                    not (p["result"] == "FAIL" and failed == 0),
                    "ASSERTION_INCOHERENCE")
        elif kind == "INSTRUMENT":
            require(p.get("assessment") in
                    {"QUALIFIED_WITHIN_SCOPE", "PARTIALLY_QUALIFIED",
                     "UNQUALIFIED", "UNRESOLVED"}, "BAD_ENUM")
            require(p.get("attribution") == "RESEARCH_INTERPRETATION",
                    "BAD_ATTRIBUTION")
            require(nonblank(p.get("reason")), "INSTRUMENT_REASON")
            basis = p.get("basis_event_ids")
            require(isinstance(basis, list) and len(basis) > 0 and
                    all(x in ids for x in basis), "BAD_REF")
            instrument_assessment = p["assessment"]
        elif kind == "CLAIM":
            require(p.get("assessment") in
                    {"SUPPORTED_WITHIN_SCOPE", "CONTRADICTED",
                     "UNRESOLVED", "NOT_TESTED"}, "BAD_ENUM")
            require(nonblank(p.get("claim_id")) and
                    nonblank(p.get("scope")), "CLAIM_SCOPE")
            require(p.get("attribution") == "RESEARCH_INTERPRETATION",
                    "BAD_ATTRIBUTION")
            basis = p.get("basis_event_ids")
            require(isinstance(basis, list) and len(basis) > 0 and
                    all(x in ids for x in basis), "BAD_REF")
            require(not (instrument_assessment == "UNQUALIFIED" and
                    p["assessment"] == "SUPPORTED_WITHIN_SCOPE" and
                    p["scope"] == "TARGET_BEHAVIOR"),
                    "CLAIM_WITH_UNQUALIFIED")
        elif kind == "ARCHIVE":
            require(p.get("assessment") in {"VERIFIED_COMPLETE",
                    "PARTIAL", "NOT_VERIFIED", "INACCESSIBLE"}, "BAD_ENUM")
            if p["assessment"] == "VERIFIED_COMPLETE":
                require(nonblank(p.get("sha256")) and
                        len(p["sha256"]) == 64 and
                        isinstance(p.get("bytes"), int) and p["bytes"] > 0 and
                        nonblank(p.get("source_sha256")) and
                        p["sha256"] == p["source_sha256"] and
                        nonblank(p.get("independent_store")) and
                        p.get("zip_crc_checked") is True,
                        "ARCHIVE_PROOF")
        elif kind == "DECISION":
            require(p.get("outcome") in
                    {"NOT_RECORDED", "ACCEPT", "REVISE",
                     "DEFER", "REJECT", "ESCALATE"}, "BAD_ENUM")
            if p["outcome"] == "NOT_RECORDED":
                require(p.get("authorized_actor") is None,
                        "FAKE_AUTHORIZATION")
            else:
                require(nonblank(p.get("authorized_actor")) and
                        nonblank(p.get("authority_source")), "AUTH_REQUIRED")
        elif kind == "REVIEW":
            require(p.get("status") in {"NOT_RUN", "BLOCKED", "COMPLETED"},
                    "BAD_ENUM")
            if p["status"] == "COMPLETED":
                require(all(nonblank(p.get(k)) for k in
                    ("reviewer_id", "model_family", "route_proof",
                     "isolation_evidence")), "REVIEW_PROVENANCE")
            else:
                require(p.get("reviewer_id") is None and
                        p.get("model_family") is None,
                        "FAKE_REVIEWER")
        elif kind == "CORRECTION":
            require(nonblank(p.get("prior_run_id")) and
                    p["prior_run_id"] != run["id"] and
                    nonblank(p.get("previous_source")) and
                    nonblank(p.get("corrected_source")) and
                    nonblank(p.get("reason")), "BAD_CORRECTION")
        ids.add(eid)
        seen_types.add(kind)
        evidence_by_id[eid] = event
    require(REQUIRED_KINDS <= seen_types, "MISSING_EVENT_KIND")

def evidence_event(run_id, num, kind, source_refs, payload):
    return {"id": f"e{num:02d}", "kind": kind,
            "run_id": run_id, "source_refs": source_refs, "payload": payload}

def check_archive(source):
    p = ROOT / source["archive_path"]
    raw = base64.b64decode(p.read_text().strip(), validate=True)
    require(len(raw) == source["artifact_zip_bytes"] and
            h(raw) == source["artifact_zip_sha256"], "ARCHIVE_SOURCE_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        require(z.testzip() is None, "ARCHIVE_CRC_ERROR")
        names = z.namelist()
        require("results/p5.json" in names, "P5_RESULT_MISSING")
        report_bytes = z.read("results/p5.json")
        data = json.loads(report_bytes)
    return data, {"sha256": h(raw), "bytes": len(raw),
                  "result_sha256": h(report_bytes),
                  "result_bytes": len(report_bytes),
                  "source_sha256": source["artifact_zip_sha256"],
                  "independent_store": source["archive_path"],
                  "zip_crc_checked": True,
                  "members": names}

def assertion_counts(p5):
    rows = []
    by_candidate = {}
    for lang, modes in p5["implementations"].items():
        by_candidate[lang] = {}
        for mode, methods in modes.items():
            local = []
            a = methods.get("A", {})
            local.extend(a.get("checks", []))
            b = methods.get("B", {})
            local.extend(b.get("conventional_component", {}).get("checks", []))
            local.extend({"pass": x["passed"]}
                         for x in b.get("kill_trials", []))
            rows.extend(local)
            by_candidate[lang][mode] = {
                "checks": len(local),
                "failed": sum(item.get("pass") is False for item in local),
                "planted_fault": mode != "correct"
            }
    require(bool(rows), "NO_CHECKS_IN_ARCHIVE")
    return (len(rows), sum(item.get("pass") is False for item in rows),
            by_candidate)

def assertion_example(p5):
    results = {}
    for lang, modes in p5["implementations"].items():
        checks = modes["correct"]["A"]["checks"]
        entries = [x for x in checks if x["check"] == "spend_cap_exceeded_deny"]
        require(len(entries) == 1, "MISSING_FROZEN_ASSERTION")
        results[lang] = {"expected": entries[0]["expected"],
                         "observed": entries[0]["observed"],
                         "passed": entries[0]["pass"]}
    return results

def make_envelope(source, p5, archived, plan_hash):
    label = source["label"]
    red = label == "red_instrument_error"
    run_id = "p5:" + str(source["source_job_id"])
    expected_job = "FAILED" if red else "SUCCESS"
    expected_suite = "FAIL" if red else "PASS"
    require(p5["status"] == expected_suite, "P5_SOURCE_STATUS")
    require(p5["source_plan_sha256"] == h(P5PLAN.read_bytes()),
            "P5_PLAN_HASH")
    total, failed, by_candidate = assertion_counts(p5)
    # A successful mutation-qualification run still contains intentionally
    # failed assertions in deliberately broken candidates. Distinguish
    # unexpected failures of the correct implementation from expected REDs.
    correct_failures = sum(v["correct"]["failed"] for v in by_candidate.values())
    planted_failures = sum(v[m]["failed"] for v in by_candidate.values()
                           for m in ("duplicate", "early_ack"))
    require((correct_failures > 0) == red and planted_failures > 0
            and failed == correct_failures + planted_failures,
            "P5_CANDIDATE_CLASSIFICATION")
    examples = assertion_example(p5)
    for lang, example in examples.items():
        require(example["expected"] == ["DENY"], "WRONG_GOLDEN")
        require(example["observed"] == (["ACK"] if red else ["DENY"]),
                "P5_FIXTURE_CONTRAST")
    rawref = "sha256:" + archived["result_sha256"]
    zipref = "sha256:" + archived["sha256"]
    base = [
        evidence_event(run_id, 1, "EXECUTION", [rawref], {
            "job_outcome": expected_job, "suite_result": expected_suite,
            "provider_job_id": source["source_job_id"],
            "source_revision": P5_SOURCE[label]}),
        evidence_event(run_id, 2, "ASSERTION", [rawref], {
            "result": "FAIL" if failed else "PASS",
            "total_count": total, "failed_count": failed,
            "by_candidate": by_candidate,
            "unexpected_correct_candidate_failures": correct_failures,
            "intended_negative_control_failures": planted_failures,
            "illustrative_check": examples}),
        evidence_event(run_id, 3, "INSTRUMENT", [rawref,
             "p5-source:" + P5_SOURCE[label]], {
            "assessment": "UNQUALIFIED" if red else "PARTIALLY_QUALIFIED",
            "attribution": "RESEARCH_INTERPRETATION",
            "reason": (
                "P5 spending cap oracle wrongly expected 50 > 80 on empty journal"
                if red else "Corrected cap fixture; selected faults are planted and do not establish unbiased coverage"),
            "basis_event_ids": ["e01", "e02"]}),
        evidence_event(run_id, 4, "CLAIM", [rawref], {
            "claim_id": "P5_ASSURANCE_COMPARISON",
            "assessment": "UNRESOLVED" if red else "SUPPORTED_WITHIN_SCOPE",
            "scope": "TARGET_BEHAVIOR",
            "attribution": "RESEARCH_INTERPRETATION",
            "basis_event_ids": ["e02", "e03"]}),
        evidence_event(run_id, 5, "ARCHIVE", [zipref], {
            "assessment": "VERIFIED_COMPLETE", **{k:archived[k] for k in
                ("sha256", "bytes", "source_sha256", "independent_store",
                 "zip_crc_checked")}}),
        evidence_event(run_id, 6, "DECISION", [
            "p6-plan-sha256:" + plan_hash], {
            "outcome": "NOT_RECORDED", "authorized_actor": None}),
        evidence_event(run_id, 7, "REVIEW", [
            "P5-REVIEWER-PACKET-2026-11-02.md"], {
            "status": "NOT_RUN", "reviewer_id": None, "model_family": None})
    ]
    if not red:
        base.append(evidence_event(run_id, 8, "CORRECTION", [
            "p5-source:" + P5_SOURCE["red_instrument_error"],
            "p5-source:" + P5_SOURCE["green_corrected"]], {
            "prior_run_id": "p5:17650922007",
            "previous_source": P5_SOURCE["red_instrument_error"],
            "corrected_source": P5_SOURCE["green_corrected"],
            "reason": "Research interpretation: invalid 50/80 fixture changed to 90/80; raw earlier failed run preserved"}))
    return {
        "schema_version":1,
        "run": {
            "id":run_id,"study":"EDASES-P5",
            "provider":"GitLab CI",
            "source_revision":P5_SOURCE[label],
            "plan_sha256":p5["source_plan_sha256"]},
        "events":base
    }

def qualify_negative_controls(red, green):
    outcomes = []
    def test(name, source, edit, expected_code):
        x = copy.deepcopy(source)
        edit(x)
        try:
            validate(x)
        except InvalidEvidence as e:
            require(e.code == expected_code,
                    "NEGATIVE_WRONG_REJECTION_" + name)
            outcomes.append({"name":name,"result":"DETECTED","reason":e.code})
        else:
            raise InvalidEvidence("NEGATIVE_ESCAPED_" + name)
    ev = lambda x, kind: next(e for e in x["events"] if e["kind"] == kind)
    test("wrong_top_level_single_status",green,lambda x:x.update(status="PASS"),"ROOT_FIELDS")
    test("wrong_job_enum",green,lambda x:ev(x,"EXECUTION")["payload"].update(job_outcome="APP_DEFECT"),"BAD_ENUM")
    test("wrong_id_duplicate",green,lambda x:x["events"][1].update(id=x["events"][0]["id"]),"DUPLICATE_EVENT")
    test("wrong_run_link",green,lambda x:x["events"][0].update(run_id="other"),"RUN_MISMATCH")
    test("missing_evidence",green,lambda x:ev(x,"ASSERTION").update(source_refs=[]),"NO_EVIDENCE")
    test("assertion_incoherent",red,lambda x:ev(x,"ASSERTION")["payload"].update(result="PASS"),"ASSERTION_INCOHERENCE")
    test("unsupported_target_defect",red,lambda x:ev(x,"CLAIM")["payload"].update(assessment="SUPPORTED_WITHIN_SCOPE"),"CLAIM_WITH_UNQUALIFIED")
    test("missing_basis",green,lambda x:ev(x,"CLAIM")["payload"].update(basis_event_ids=["absent"]),"BAD_REF")
    test("fake_independent_model",green,lambda x:ev(x,"REVIEW")["payload"].update(status="COMPLETED",reviewer_id="fabricated"),"REVIEW_PROVENANCE")
    test("fake_actor",green,lambda x:ev(x,"DECISION")["payload"].update(outcome="ACCEPT"),"AUTH_REQUIRED")
    test("unverified_archive_claim",green,lambda x:ev(x,"ARCHIVE")["payload"].update(sha256=""),"ARCHIVE_PROOF")
    test("false_reviewer_not_run",green,lambda x:ev(x,"REVIEW")["payload"].update(reviewer_id="fictional"),"FAKE_REVIEWER")
    test("future_link",green,lambda x:ev(x,"INSTRUMENT")["payload"].update(basis_event_ids=["e99"]),"BAD_REF")
    test("bad_enum",green,lambda x:ev(x,"INSTRUMENT")["payload"].update(assessment="PROVEN"),"BAD_ENUM")
    test("bad_kind",green,lambda x:ev(x,"REVIEW").update(kind="INDEPENDENT_PASS"),"BAD_KIND")
    test("no_reason_to_change",green,lambda x:ev(x,"CORRECTION")["payload"].update(reason=""),"BAD_CORRECTION")
    return outcomes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    started = time.monotonic()
    manifest = json.loads(MANIFEST.read_text())
    require(len(manifest["records"]) == 2, "MANIFEST_RECORDS")
    plan_hash = h(PLAN.read_bytes())
    records, evidences = {}, {}
    for source in manifest["records"]:
        report, archival = check_archive(source)
        envelope = make_envelope(source, report, archival, plan_hash)
        validate(envelope)
        records[source["label"]] = envelope
        evidences[source["label"]] = {
            "archive":archival, "original_status":report["status"],
            "original_plan_sha256":report["source_plan_sha256"],
            "assertion_example":assertion_example(report)}
    require(set(records) == {"red_instrument_error","green_corrected"}, "BOTH_RUNS_REQUIRED")
    negative = qualify_negative_controls(records["red_instrument_error"],
                                         records["green_corrected"])
    # Valid neighbors: a failed job is acceptable as an honest observation;
    # an incomplete archive must also be expressible without pretending success.
    incomplete = copy.deepcopy(records["green_corrected"])
    archive = next(e for e in incomplete["events"] if e["kind"] == "ARCHIVE")
    archive["payload"] = {"assessment":"NOT_VERIFIED"}
    validate(incomplete)
    result = {
        "study":"EDASES-P6","status":"PASS",
        "preregistered_plan_sha256":plan_hash,
        "source":"Original P5 red and green CI archive ZIPs; not author's narrative",
        "envelopes":records,
        "raw_evidence_checks":evidences,
        "positive_controls":{
            "original_failed_run_is_valid_record":True,
            "corrected_success_run_is_valid_record":True,
            "incomplete_archive_can_be_honestly_represented":True
        },
        "negative_controls":negative,
        "assurance_limits":[
            "This custom validator is not a full JSON Schema validator or a universal ontology",
            "Grounded SHA256/ZIP checks do not prove semantic accuracy of the test oracle",
            "Reclassification of P5 fixture failure is a research interpretation, not independent review",
            "Raw P5 journal fixtures are derived via pinned source, not all embedded in machine outcomes",
            "No authorized human decision or formal independent reviewer has been supplied",
            "No actual resource-provider settlement or production system was tested"
        ],
        "elapsed_ms":round((time.monotonic()-started)*1000,3)
    }
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("ASES_P6_SUMMARY="+json.dumps({
        "status":result["status"],
        "original_job_states":{k:v["original_status"] for k,v in evidences.items()},
        "archives_recovered":len(evidences),
        "positive_controls":len(result["positive_controls"]),
        "negative_controls":len(negative),
        "elapsed_ms":result["elapsed_ms"],
        "result_bytes":path.stat().st_size,
        "plan_sha256":plan_hash
    },sort_keys=True))

if __name__ == "__main__":
    main()
