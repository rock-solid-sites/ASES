"""Deliberately adversarial contract tests, including valid controls."""
import unittest
from evidence_contract import classify

def example(**overrides):
    r = {"execution": "PASS", "frozen_claim": "C11",
         "artifacts": [{"sha256": "a" * 64, "size": 12, "capture_complete": True}],
         "controls": {"valid_neighbor_accepted": True,
                      "invalid_evidence_rejected": True, "oracle_independent": True},
         "off_provider_archive_verified": False}
    r.update(overrides)
    return r

class AssuranceContractTests(unittest.TestCase):
    def test_valid_control(self):
        r = classify(example())
        self.assertEqual(r["claim_evaluation"], "SUPPORTED_WITHIN_SCOPE")
        self.assertEqual(r["evidence_quality"], "QUALIFIED")
        self.assertFalse(r["archive_complete"])
        self.assertIsNone(r["acceptance"])
    def test_missing_artifact(self):
        r = classify(example(artifacts=[]))
        self.assertEqual(r["claim_evaluation"], "UNRESOLVED")
        self.assertEqual(r["evidence_quality"], "UNQUALIFIED")
    def test_missing_independent_oracle(self):
        controls = example()["controls"] | {"oracle_independent": False}
        self.assertEqual(classify(example(controls=controls))["claim_evaluation"], "UNRESOLVED")
    def test_mutated_negative_control(self):
        controls = example()["controls"] | {"invalid_evidence_rejected": False}
        self.assertEqual(classify(example(controls=controls))["claim_evaluation"], "UNRESOLVED")
    def test_false_reject_neighbor(self):
        controls = example()["controls"] | {"valid_neighbor_accepted": False}
        self.assertEqual(classify(example(controls=controls))["claim_evaluation"], "UNRESOLVED")
    def test_incomplete_capture(self):
        bad = [{"sha256": "a" * 64, "size": 1, "capture_complete": False}]
        self.assertEqual(classify(example(artifacts=bad))["evidence_quality"], "UNQUALIFIED")
    def test_failure_is_not_automatically_contradiction(self):
        self.assertEqual(classify(example(execution="FAIL"))["claim_evaluation"], "UNRESOLVED")
    def test_observed_violation(self):
        self.assertEqual(classify(example(execution="FAIL", violation_observed=True))["claim_evaluation"], "CONTRADICTED")
    def test_timeout_is_not_pass(self):
        self.assertEqual(classify(example(execution="INCONCLUSIVE"))["claim_evaluation"], "UNRESOLVED")
    def test_unknown_status_rejected(self):
        with self.assertRaises(ValueError):
            classify(example(execution="SUCCESS"))
    def test_no_implicit_acceptance(self):
        self.assertIsNone(classify(example())["acceptance"])

if __name__ == "__main__":
    unittest.main()
