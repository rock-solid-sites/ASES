"""Independent adversarial mutation audit of two existing Phase I checkers.

Mutations target semantic observations, not merely missing JSON keys. Each
must be rejected by the existing checker as VIOLATION or INCOMPLETE.
This is checker sensitivity, NOT a proof of implementation correctness.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

p = argparse.ArgumentParser()
p.add_argument("--case", required=True, choices=("f1", "f4"))
p.add_argument("--source", type=Path, required=True)
args = p.parse_args()
source = args.source.resolve()
spec = importlib.util.spec_from_file_location("target_checker", source / "check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
data = json.loads((source / "raw.json").read_text())
results = []

def mutation(label, baseline, transform, expected, evaluator):
    value = copy.deepcopy(baseline)
    transform(value)
    actual = evaluator(value)["status"]
    results.append({"mutation": label, "expected": sorted(expected), "actual": actual,
                    "detected": actual in expected})
    assert actual in expected, f"{label}: checker returned {actual}; expected {expected}"

if args.case == "f1":
    baseline = data["cases"]["atomic-A"]
    assert checker.case(baseline)["status"] == "SUPPORTED"
    mutation("accepted_content_changed", baseline,
             lambda c: c["recovered_query"]["response"]["consumer_query"].update(accepted_content="tampered"),
             {"VIOLATION"}, checker.case)
    mutation("recovery_supplied_original_tuple", baseline,
             lambda c: c["recovered"]["config"].update(observations={"forged": True}),
             {"VIOLATION"}, checker.case)
    mutation("declared_original_observation_changed", baseline,
             lambda c: c.update(declared_original_observations={"forged": True}),
             {"VIOLATION"}, checker.case)
    mutation("reader_integrity_false", baseline,
             lambda c: c["independent_reader"]["observation"].update(integrity="failed"),
             {"VIOLATION"}, checker.case)
    mutation("reader_digest_changed", baseline,
             lambda c: c["independent_reader"]["observation"].update(view_sha256="0"*64),
             {"VIOLATION"}, checker.case)
    mutation("writer_commit_order_inverted", baseline,
             lambda c: c["writer_trace"].__setitem__(slice(None), [
                 {**x, "start_ns": 0} if x["sql"] == "COMMIT" else x for x in c["writer_trace"]]),
             {"VIOLATION"}, checker.case)
    mutation("missing_accepted_response", baseline,
             lambda c: c["accept"].pop("response"),
             {"INCOMPLETE"}, checker.case)
    mutation("missing_raw_observation", baseline,
             lambda c: c["independent_reader"]["observation"].pop("observation_utf8_hex"),
             {"INCOMPLETE"}, checker.case)
else:
    baseline = data["cases"]["guarded_restart"]
    assert checker.reference(baseline)["status"] == "SUPPORTED"
    mutation("guarded_writer_not_excluded", baseline,
             lambda c: c["blocked_B"].update(exit=0),
             {"VIOLATION"}, checker.reference)
    mutation("second_ack_wrong_sequence", baseline,
             lambda c: c["second"]["response"]["body"].update(event_seq=1),
             {"VIOLATION"}, checker.reference)
    mutation("second_ack_wrong_payload", baseline,
             lambda c: c["second"]["request"].update(payload="forged-payload"),
             {"VIOLATION"}, checker.reference)
    mutation("guard_inode_changed", baseline,
             lambda c: c["cold"]["startup_frame"]["guard"].update(inode=-1),
             {"VIOLATION"}, checker.reference)
    mutation("missing_recovery_bytes", baseline,
             lambda c: c.pop("recovered_ready_journal"),
             {"INCOMPLETE"}, checker.reference)
    mutation("missing_startup_observation", baseline,
             lambda c: c["A"].pop("startup_observed_ns"),
             {"INCOMPLETE"}, checker.reference)
    overlap = data["cases"]["original_overlap"]
    assert checker.overlap(overlap)["status"] == "COUNTEREXAMPLE"
    mutation("duplicate_sequence_not_present", overlap,
             lambda c: c["second"]["response"]["body"].update(event_seq=2),
             {"VIOLATION"}, checker.overlap)
    mutation("overlap_not_observed", overlap,
             lambda c: c["B"].pop("startup_observed_ns"),
             {"INCOMPLETE"}, checker.overlap)

assert len(results) == 8 and all(r["detected"] for r in results)
print(json.dumps({"case": args.case, "source": str(source), "mutations": results,
                  "mutations_detected": len(results), "semantic_scope": "bounded checker mutation audit",
                  "independent_oracle": False}, indent=2))
