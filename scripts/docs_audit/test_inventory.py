"""Negative controls for read-only documentation inventory."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from inventory import inventory, frontmatter, reference_check, markdown_index


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        return dest

    def active(self, title="Named", version="1.0.0", status="Active",
               authority="Canonical", program="ASES"):
        version_field = "version: " + version + "\n" if version else ""
        return (f"---\ntitle: {title}\nprogram: {program}\nstatus: {status}\n"
                f"authority: {authority}\n{version_field}---\n# {title}\n")

    def by_path(self, data, path):
        return next(doc for doc in data["documents"] if doc["path"] == path)

    def test_active_and_version_are_observed_not_invented(self):
        self.put("docs/methodology/a.md", self.active(version=""))
        doc = self.by_path(inventory(self.root), "docs/methodology/a.md")
        self.assertTrue(doc["declared_active"])
        self.assertIsNone(doc["version"])
        self.assertTrue(any("lacks explicit version" in e for e in doc["warnings"]))

    def test_current_skill_discovered_without_frontmatter_status(self):
        self.put("skills/current/sample/SKILL.md", "# Example\n")
        doc = self.by_path(inventory(self.root), "skills/current/sample/SKILL.md")
        self.assertTrue(doc["declared_active"])
        self.assertEqual(doc["status"], "Current skill")

    def test_historical_and_vendored_excluded(self):
        self.put("fork/opencode-src/AGENTS.md", self.active())
        self.put(".design/reframe-glm52.md", "User supplied an old [AGENTS.md](AGENTS.md) link.\n")
        self.put("docs/historical/AGENTS.md", self.active())
        self.put("docs/methodology/c.md", self.active(title="Current"))
        data = inventory(self.root)
        self.assertEqual(data["counts"]["owned_records"], 1)
        self.assertEqual(data["counts"]["declared_active"], 1)

    def test_duplicate_canonical_identity_distinct_from_matching_filename(self):
        self.put("docs/methodology/x.md", self.active(title="Shared rule"))
        self.put("docs/standards/y.md", self.active(title="Shared rule"))
        self.put("research/fixture/README.md", self.active(title="Different", status="Experimental"))
        data = inventory(self.root)
        self.assertEqual(len(data["duplicate_active_canonical_identities"]), 1)
        self.assertEqual(set(data["duplicate_active_canonical_identities"][0]["paths"]),
                         {"docs/methodology/x.md", "docs/standards/y.md"})

    def test_research_not_promoted_to_current(self):
        self.put("research/experiment/RESULT.md", self.active(status="Experimental"))
        doc = self.by_path(inventory(self.root), "research/experiment/RESULT.md")
        self.assertFalse(doc["declared_active"])

    def test_stale_entrypoint_marker_flagged_not_deleted(self):
        self.put("AGENTS.md", self.active() + "\nRun crosslink session last-handoff.\n")
        doc = self.by_path(inventory(self.root), "AGENTS.md")
        self.assertTrue(any("retired route markers" in e for e in doc["warnings"]))
        self.assertTrue((self.root / "AGENTS.md").read_text().endswith(
            "Run crosslink session last-handoff.\n"))

    def test_broken_relative_link_detected_with_existing_reference(self):
        self.put("docs/methodology/a.md",
                 self.active() + "\n[good](../standards/b.md) [bad](../standards/c.md)\n")
        self.put("docs/standards/b.md", self.active(title="Linked"))
        doc = self.by_path(inventory(self.root), "docs/methodology/a.md")
        self.assertEqual(doc["broken_relative_links"],
                         ["missing relative link: ../standards/c.md"])

    def test_index_records_status_unknown_and_source_revision(self):
        self.put("README.md", "# An unclassified intro\n")
        self.put("docs/standards/c.md", self.active(title="Core"))
        data = inventory(self.root)
        rendered = markdown_index(data)
        self.assertIn("UNVERIFIED", rendered)
        self.assertIn("Core", rendered)
        self.assertIn("diagnostics require review".lower(), rendered.lower())
        self.assertNotIn("[README]", rendered)

    def test_frontmatter_does_not_confuse_body_metadata(self):
        fields = frontmatter("# Notes\nstatus: Active\nversion: 900\n")
        self.assertEqual(fields, {})

    def test_unknown_status_is_diagnostic_not_current(self):
        self.put("docs/requirements/unknown.md", self.active(status="Investigating"))
        doc = self.by_path(inventory(self.root), "docs/requirements/unknown.md")
        self.assertFalse(doc["declared_active"])
        self.assertTrue(any("nonstandard status" in e for e in doc["warnings"]))


if __name__ == "__main__":
    unittest.main()
