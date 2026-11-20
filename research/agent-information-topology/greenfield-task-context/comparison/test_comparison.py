"""Adversarial source/packet mutations for the preregistered synthetic comparison."""
import copy
import unittest

from evaluate import fixture, resolve, packet, evaluate, InvalidGraph, METHODS, TASK_NAMES, run


class CompareFormats(unittest.TestCase):
    def setUp(self):
        self.graph = fixture()

    def test_all_six_packets_pass_frozen_exact_string_gates(self):
        rows = run()
        self.assertEqual(len(rows), 6)
        for row in rows:
            with self.subTest(task=row["task"], method=row["format"]):
                self.assertTrue(row["ok"], row)
                self.assertEqual(row["required_present"], row["required_total"])
                self.assertEqual(row["missing"], [])
                self.assertEqual(row["forbidden"], [])
                self.assertEqual(row["unrelated_source_refs"], [])

    def test_manual_structured_and_graph_are_distinct(self):
        for name, task in TASK_NAMES:
            with self.subTest(task=task):
                bodies = [packet(m, name, self.graph) for m in METHODS]
                self.assertEqual(len(set(bodies)), 3)

    def test_wrong_revision_detected_against_frozen_expected(self):
        broken = copy.deepcopy(self.graph)
        next(s for s in broken["sources"] if s["id"] == "source:docs")["revision"] = "docs-r5"
        with self.assertRaisesRegex(InvalidGraph, "ground truth"):
            evaluate(packet("manual", "docs", self.graph), "task:docs", broken)

    def test_duplicate_rule_id_rejected(self):
        broken = copy.deepcopy(self.graph)
        broken["rules"].append(copy.deepcopy(broken["rules"][0]))
        with self.assertRaisesRegex(InvalidGraph, "duplicate rule"):
            resolve(broken, "task:docs")

    def test_dangling_source_rejected(self):
        broken = copy.deepcopy(self.graph)
        broken["rules"][0]["source"] = "source:missing"
        with self.assertRaisesRegex(InvalidGraph, "dangling source"):
            resolve(broken, "task:docs")

    def test_stale_research_cannot_become_binding_rule(self):
        broken = copy.deepcopy(self.graph)
        r = next(x for x in broken["rules"] if x["id"] == "rule:stale-research")
        r["applies_to"].append("task:review")
        with self.assertRaisesRegex(InvalidGraph, "promoted to rule"):
            resolve(broken, "task:review")

    def test_unauthorized_override_rejected(self):
        broken = copy.deepcopy(self.graph)
        broken["decisions"][0]["status"] = "draft-fixture"
        with self.assertRaisesRegex(InvalidGraph, "unapproved decision"):
            resolve(broken, "task:review")

    def test_wrong_task_override_rejected(self):
        broken = copy.deepcopy(self.graph)
        broken["decisions"][0]["scope_task"] = "task:docs"
        with self.assertRaisesRegex(InvalidGraph, "not applicable"):
            resolve(broken, "task:docs")

    def test_duplicate_target_overrides_rejected(self):
        broken = copy.deepcopy(self.graph)
        d = copy.deepcopy(broken["decisions"][0])
        d["id"] = "decision:another-local-review"
        broken["decisions"].append(d)
        with self.assertRaisesRegex(InvalidGraph, "conflicting overrides"):
            resolve(broken, "task:review")

    def test_superseded_rule_text_is_detected_if_reintroduced(self):
        body = packet("graph", "review", self.graph) + "\nOLD_ROUTE_CANARY: use the superseded upstream review workflow."
        row = evaluate(body, "task:review", self.graph)
        self.assertFalse(row["ok"])
        self.assertTrue(any("OLD_ROUTE_CANARY" in f for f in row["forbidden"]))

    def test_unrelated_rule_text_and_source_ref_detected(self):
        body = (packet("manual", "docs", self.graph)
                + "\nDISTRACTOR_MARKETING: unrelated marketing campaign details."
                + "\nsource:marketing@market-r1")
        row = evaluate(body, "task:docs", self.graph)
        self.assertFalse(row["ok"])
        self.assertTrue(row["forbidden"])
        self.assertEqual(row["unrelated_source_refs"], ["source:marketing@market-r1"])

    def test_missing_evidence_uncertainty_disclosure_detected(self):
        body = packet("structured", "review", self.graph).replace(
            "REVIEW_RUNTIME_NOT_TESTED", "INDETERMINATE")
        row = evaluate(body, "task:review", self.graph)
        self.assertFalse(row["ok"])
        self.assertIn("REVIEW_RUNTIME_NOT_TESTED", row["missing"])

    def test_missing_output_or_evidence_destination_rejected(self):
        broken = copy.deepcopy(self.graph)
        broken["tasks"][1]["destination"] = ""
        with self.assertRaisesRegex(InvalidGraph, "missing output"):
            resolve(broken, "task:review")

    def test_accidental_model_launch_rejected(self):
        broken = copy.deepcopy(self.graph)
        broken["tasks"][1]["model_launch"] = "some-provider/model"
        with self.assertRaisesRegex(InvalidGraph, "unauthorized route"):
            resolve(broken, "task:review")

    def test_packet_without_stop_rule_rejected(self):
        body = packet("manual", "docs", self.graph).replace("FALLBACK=none", "FALLBACK=auto")
        row = evaluate(body, "task:docs", self.graph)
        self.assertFalse(row["ok"])
        self.assertIn("FALLBACK=none", row["missing"])


if __name__ == "__main__":
    unittest.main()
