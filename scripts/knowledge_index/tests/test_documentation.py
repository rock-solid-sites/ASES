"""Review-readiness checks for the knowledge-index documentation packet.

These tests inspect only committed files in the ASES checkout; they do not
create documentation or modify canonical research sources.
"""
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

from indexer import metadata

REPO = Path(__file__).resolve().parents[3]
DOCUMENTS = [
    "scripts/knowledge_index/TECHNICAL.md",
    "scripts/knowledge_index/README.md",
    "docs/proposals/knowledge-index/Design and Integration Proposal.md",
    "docs/proposals/knowledge-index/Final Review Checklist.md",
    "docs/research/Knowledge Index Prototype - Real Repository Test Record 2026-11-19.md",
]
HEADERS = [
    "title", "program", "layer", "document_type", "status",
    "authority", "canonical_repository", "last_updated"
]


class ReviewDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (REPO / "docs/proposals/knowledge-index/Design and Integration Proposal.md").exists():
            raise AssertionError("Full ASES repo checkout required for design review tests")

    def test_design_and_technical_metadata_classification(self):
        for relative in DOCUMENTS:
            if relative.endswith("/README.md"):
                continue
            with self.subTest(path=relative):
                fields, warning = metadata((REPO / relative).read_text(encoding="utf-8"))
                self.assertIsNone(warning)
                for required in HEADERS:
                    self.assertIn(required, fields)
                    self.assertTrue(fields[required])
                self.assertNotEqual(fields["authority"], "Canonical")
        proposal, _ = metadata((REPO / DOCUMENTS[2]).read_text())
        self.assertEqual(proposal["status"], "Draft")
        self.assertEqual(proposal["layer"], "Architecture")

    def test_all_review_packet_relative_links_exist(self):
        for relative in DOCUMENTS:
            source = REPO / relative
            content = source.read_text(encoding="utf-8")
            no_fences = re.sub(r"[\x60]{3}[\s\S]*?[\x60]{3}", "", content)
            targets = re.findall(r"\]\(([^)\n]+)\)", no_fences)
            for target in targets:
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not clean:
                    continue
                destination = (source.parent / clean).resolve()
                with self.subTest(source=relative, target=target):
                    self.assertTrue(destination.is_relative_to(REPO.resolve()),
                                    "link escapes repository")
                    self.assertTrue(destination.is_file(),
                                    "unresolvable internal documentation link")

    def test_separate_merge_and_integration_decisions_and_no_false_approval(self):
        design = (REPO / DOCUMENTS[2]).read_text(encoding="utf-8")
        review = (REPO / DOCUMENTS[3]).read_text(encoding="utf-8")
        technical = (REPO / DOCUMENTS[0]).read_text(encoding="utf-8")
        self.assertIn("not merged", design)
        self.assertIn("Decision A", review)
        self.assertIn("Decision B", review)
        self.assertIn("UNREVIEWED", review)
        self.assertIn("NOT APPROVED", review)
        self.assertIn("not approved for production integration", technical)
