"""Adversarial evidence contract tests; qualification and provenance fail closed."""
from pathlib import Path
import tempfile
import unittest
from evidence_contract import classify, manifest, verify_manifest


def example(**overrides):
    record = {"execution": "PASS", "frozen_claim": "C11",
              "artifacts": [{"path": "trace.json", "sha256": "a"*64,
                             "size": 12, "capture_complete": True}],
              "artifact_integrity_verified": True,
              "controls": {"valid_neighbor_accepted": True,
                           "invalid_evidence_rejected": True,
                           "oracle_independent": True},
              "off_provider_archive_verified": False}
    record.update(overrides)
    return record


class AssuranceContractTests(unittest.TestCase):
    def test_valid_control(self):
        outcome = classify(example())
        self.assertEqual(outcome["claim_evaluation"], "SUPPORTED_WITHIN_SCOPE")
        self.assertEqual(outcome["evidence_quality"], "QUALIFIED")
        self.assertFalse(outcome["archive_complete"])
        self.assertIsNone(outcome["acceptance"])

    def test_missing_artifact(self):
        self.assertEqual(classify(example(artifacts=[]))["evidence_quality"], "UNQUALIFIED")

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
        files = [{"path": "evidence", "sha256": "a"*64, "size": 1, "capture_complete": False}]
        self.assertEqual(classify(example(artifacts=files))["evidence_quality"], "UNQUALIFIED")

    def test_failure_not_automatically_contradiction(self):
        self.assertEqual(classify(example(execution="FAIL"))["claim_evaluation"], "UNRESOLVED")

    def test_observed_violation(self):
        self.assertEqual(classify(example(execution="FAIL", violation_observed=True))["claim_evaluation"], "CONTRADICTED")

    def test_unverified_violation_not_contradiction(self):
        self.assertEqual(classify(example(execution="FAIL", violation_observed=True,
                                          artifact_integrity_verified=False))["claim_evaluation"], "UNRESOLVED")

    def test_timeout_not_pass(self):
        self.assertEqual(classify(example(execution="INCONCLUSIVE"))["claim_evaluation"], "UNRESOLVED")

    def test_unknown_status(self):
        with self.assertRaises(ValueError):
            classify(example(execution="SUCCESS"))

    def test_no_implicit_acceptance(self):
        self.assertIsNone(classify(example())["acceptance"])

    def test_nonhex_sha_rejected(self):
        files = [{**example()["artifacts"][0], "sha256": "z"*64}]
        self.assertEqual(classify(example(artifacts=files))["evidence_quality"], "UNQUALIFIED")

    def test_bad_artifact_types(self):
        for artifacts in ([None], ["str"], "str", {}, [3]):
            with self.subTest(artifacts=artifacts):
                self.assertEqual(classify(example(artifacts=artifacts))["evidence_quality"], "UNQUALIFIED")

    def test_boolean_size_not_int(self):
        files = [{**example()["artifacts"][0], "size": True}]
        self.assertEqual(classify(example(artifacts=files))["evidence_quality"], "UNQUALIFIED")

    def test_duplicate_paths_rejected(self):
        self.assertEqual(classify(example(artifacts=example()["artifacts"]*2))["evidence_quality"], "UNQUALIFIED")

    def test_traversal_rejected(self):
        for name in ("../secret", "/tmp/private", "a/../secret", "a\\b", "./data"):
            with self.subTest(path=name):
                files = [{**example()["artifacts"][0], "path": name}]
                self.assertEqual(classify(example(artifacts=files))["evidence_quality"], "UNQUALIFIED")

    def test_frozen_claim_required(self):
        self.assertEqual(classify(example(frozen_claim="  "))["claim_evaluation"], "UNRESOLVED")

    def test_false_external_archive_attestation_cannot_claim_archive(self):
        self.assertFalse(classify(example(off_provider_archive_verified=True))["archive_complete"])

    def test_manifest_hash_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text('{"a":1}')
            files = manifest(tmp)
            self.assertTrue(verify_manifest(tmp, files))
            path.write_text('{"a":2}')
            self.assertFalse(verify_manifest(tmp, files))

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "link.txt").symlink_to(root.parent / "outside-model-fixture.txt")
            with self.assertRaises(ValueError):
                manifest(root)

    def test_secret_path_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".env.prod").write_text("sensitive")
            with self.assertRaises(ValueError):
                manifest(tmp)


if __name__ == "__main__":
    unittest.main()
