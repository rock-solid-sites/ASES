"""Lightweight, read-only document boundary tests for the ASES research pilot."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCH = HERE / "DESIGN-AND-DECISION-BOUNDARIES.md"
SOURCES = (
    "docs/standards/Documentation Standard.md",
    "docs/research/EDASES-Methodology-Feedback-and-Enforcement.md",
    "docs/research/Tools Distribution Architecture Synthesis.md",
    "docs/research/Tools Distribution Architecture Decision Test Framework.md",
)


class DocumentContractTests(unittest.TestCase):
    def test_authority_and_scope_are_explicit(self):
        doc = ARCH.read_text(encoding="utf-8")
        self.assertTrue(doc.startswith("---\n"))
        frontmatter = doc.split("---", 2)[1]
        for field in ("program: ASES", "layer: Research", "status: Experimental",
                      "authority: Experimental", "canonical_repository: ases"):
            self.assertIn(field, frontmatter)
        self.assertIn("WHAT-NOT-TESTED:", doc)
        self.assertIn("not Luna's independent result", doc)
        self.assertIn("not a validation of this policy publisher", doc)

    def test_reconciled_primary_sources_exist(self):
        for p in SOURCES:
            with self.subTest(source=p):
                self.assertTrue((ROOT / p).is_file(), p)
                self.assertIn(p, ARCH.read_text(encoding="utf-8"))

    def test_entrypoint_audit_has_traceable_existing_sources(self):
        audit = (HERE / "DOCUMENT-ENTRYPOINT-AUDIT-2026-11-20.md").read_text(encoding="utf-8")
        self.assertTrue(audit.startswith("---\n"))
        fm = audit.split("---", 2)[1]
        for field in ("status: Experimental", "authority: Experimental",
                      "canonical_repository: ases"):
            self.assertIn(field, fm)
        for source in ("AGENTS.md", "SESSION-START.md", "docs/ORCHESTRATOR.md",
                       ".opencode/opencode.json", ".mcp.json",
                       "skills/current/README.md", "skills/README.md",
                       "plugins/ases-workflow/sources.json",
                       "plugins/ases-workflow/README.md",
                       "plugins/ases-workflow/check_versions.py",
                       ".github/workflows/ases-workflow-skill-drift.yml"):
            with self.subTest(source=source):
                self.assertTrue((ROOT / source).is_file(), source)
                self.assertIn(source, audit)
        self.assertIn("WHAT-NOT-TESTED", audit)

    def test_audit_distinguishes_source_from_loaded_instructions(self):
        audit = (HERE / "DOCUMENT-ENTRYPOINT-AUDIT-2026-11-20.md").read_text(encoding="utf-8")
        self.assertIn("runtime instruction loading", audit)
        self.assertIn("UNVERIFIED", audit)
        self.assertIn("do not", audit.lower())
        self.assertIn("not", audit.lower())
        self.assertIn("source authority", audit)

    def test_does_not_depend_on_active_real_project_edits(self):
        doc = ARCH.read_text(encoding="utf-8")
        self.assertIn("No automatic cross-project push yet", doc)
        self.assertIn("No model call is needed", doc)
        self.assertIn("Luna is reserved for authenticated ChatGPT Plus/Codex", doc)


if __name__ == "__main__":
    unittest.main()
