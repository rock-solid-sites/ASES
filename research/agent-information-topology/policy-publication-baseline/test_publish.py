"""Synthetic, independent negative cases for offline ASES policy publication."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.src = self.root / "source.json"
        self.man = self.root / "consumer.json"
        self.out = self.root / "AGENTS.md"
        self.source = {"schema": "ases-policy-source-v1", "rules": [
            {"id": "git.checkpoint", "text": "Push intermediate remote checkpoints."},
            {"id": "task.destination", "text": "Deliver artifacts to ${destination}."},
            {"id": "review.route", "text": "OBSOLETE_UPSTREAM_REVIEW"},
        ]}
        self.save_source()
        self.consumer = {"schema": "ases-policy-consumer-v1",
            "source_sha256": self.digest,
            "imports": [
                {"id": "git.checkpoint", "mode": "verbatim"},
                {"id": "task.destination", "mode": "parameterized",
                 "params": {"destination": "HMS/reports"}},
                {"id": "review.route", "mode": "override", "text": "LOCAL_APPROVED_REVIEW"},
            ],
            "extensions": [{"id": "hms.guest-data", "text": "Do not disclose guest data."}]}
        self.save_manifest()

    def save_source(self):
        self.src.write_text(json.dumps(self.source, sort_keys=True))
        self.digest = hashlib.sha256(self.src.read_bytes()).hexdigest()

    def save_manifest(self):
        self.man.write_text(json.dumps(self.consumer, sort_keys=True))

    def call(self, mode):
        return subprocess.run([sys.executable, str(HERE / "publish.py"),
            "--source", str(self.src), "--manifest", str(self.man),
            "--output", str(self.out), mode], capture_output=True, text=True)

    def test_effective_output_excludes_overridden_rule(self):
        self.assertEqual(self.call("--update").returncode, 0)
        text = self.out.read_text()
        for expected in ("Push intermediate remote checkpoints.", "HMS/reports",
                         "LOCAL_APPROVED_REVIEW", "Do not disclose guest data."):
            self.assertIn(expected, text)
        self.assertNotIn("OBSOLETE_UPSTREAM_REVIEW", text)
        self.assertEqual(self.call("--check").returncode, 0)

    def test_second_project_has_different_local_policy(self):
        self.consumer["imports"][1]["params"]["destination"] = "Tripn/reports"
        self.consumer["imports"][2]["text"] = "TRIPN_APPROVED_REVIEW"
        self.consumer["extensions"] = [
            {"id": "tripn.booking-parity", "text": "Verify guest count parity."}]
        self.save_manifest()
        self.assertEqual(self.call("--update").returncode, 0)
        text = self.out.read_text()
        self.assertIn("Tripn/reports", text)
        self.assertIn("TRIPN_APPROVED_REVIEW", text)
        self.assertNotIn("LOCAL_APPROVED_REVIEW", text)
        self.assertNotIn("OBSOLETE_UPSTREAM_REVIEW", text)

    def test_missing_then_deterministic_update_and_check(self):
        self.assertNotEqual(self.call("--check").returncode, 0)
        self.assertEqual(self.call("--update").returncode, 0)
        before = self.out.read_bytes()
        self.assertEqual(self.call("--update").returncode, 0)
        self.assertEqual(self.out.read_bytes(), before)
        self.assertEqual(self.call("--check").returncode, 0)

    def test_generated_drift_detected(self):
        self.assertEqual(self.call("--update").returncode, 0)
        self.out.write_text("unauthorized downstream edit")
        self.assertNotEqual(self.call("--check").returncode, 0)
        self.assertEqual(self.out.read_text(), "unauthorized downstream edit")

    def test_changed_source_fails_closed_without_overwrite(self):
        self.assertEqual(self.call("--update").returncode, 0)
        original = self.out.read_bytes()
        self.source["rules"][0]["text"] = "New rule, not authorized"
        self.save_source()
        self.assertNotEqual(self.call("--update").returncode, 0)
        self.assertEqual(original, self.out.read_bytes())

    def test_duplicate_import_fails(self):
        self.consumer["imports"].append(self.consumer["imports"][0].copy())
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_duplicate_upstream_id_fails(self):
        self.source["rules"].append(self.source["rules"][0].copy())
        self.save_source()
        self.consumer["source_sha256"] = self.digest
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_extension_cannot_shadow_upstream(self):
        self.consumer["extensions"][0]["id"] = "review.route"
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_missing_parameter_fails(self):
        self.consumer["imports"][1]["params"] = {}
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_extra_parameter_fails(self):
        self.consumer["imports"][1]["params"]["unneeded"] = "bad"
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_unknown_upstream_id_fails(self):
        self.consumer["imports"][0]["id"] = "unknown.rule"
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_blank_override_fails(self):
        self.consumer["imports"][2]["text"] = ""
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_verbatim_mode_preserves_exact_whitespace(self):
        exact = "  Indented upstream instruction.\nRetain trailing whitespace.  \n"
        self.source["rules"][0]["text"] = exact
        self.save_source()
        self.consumer["source_sha256"] = self.digest
        self.save_manifest()
        self.assertEqual(self.call("--update").returncode, 0)
        self.assertIn(exact, self.out.read_text())

    def test_duplicate_json_object_key_is_rejected(self):
        original = self.man.read_text()
        duplicate_mode = original.replace('"mode": "verbatim"',
            '"mode": "override", "mode": "verbatim"', 1)
        self.man.write_text(duplicate_mode)
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_duplicate_json_source_field_is_rejected(self):
        original = self.src.read_text()
        duplicate_schema = original.replace('"schema": "ases-policy-source-v1"',
            '"schema": "unknown", "schema": "ases-policy-source-v1"', 1)
        self.src.write_text(duplicate_schema)
        self.consumer["source_sha256"] = hashlib.sha256(self.src.read_bytes()).hexdigest()
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)

    def test_schema_and_mode_not_silently_ignored(self):
        self.consumer["schema"] = "unknown"
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)
        self.consumer["schema"] = "ases-policy-consumer-v1"
        self.consumer["imports"][0]["mode"] = "append"
        self.save_manifest()
        self.assertNotEqual(self.call("--update").returncode, 0)


if __name__ == "__main__":
    unittest.main()
