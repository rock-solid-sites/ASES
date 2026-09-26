#!/usr/bin/env python3
"""Regression tests for alloy_xml_slice.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alloy_xml_slice import selection_errors, slice_document


FIXTURE = """\
<alloy>
  <instance command="Check Safe" filename="model.als" tracelength="3" looplength="1">
    <sig label="this/Node" ID="4">
      <atom label="this/Node$0"/><atom label="this/Node$1"/>
      <atom label="this/Node$2"/><atom label="this/Node$3"/>
    </sig>
    <field label="demoLink" ID="5" parentID="4">
      <tuple><atom label="this/Node$0"/><atom label="this/Node$1"/></tuple>
      <tuple><atom label="this/Node$1"/><atom label="this/Node$2"/></tuple>
      <tuple><atom label="this/Node$2"/><atom label="this/Node$3"/></tuple>
    </field>
    <field label="demoEmpty" ID="6" parentID="4" var="yes"/>
    <skolem label="$Safe_n"><tuple><atom label="this/Node$0"/></tuple></skolem>
    <skolem label="$Other_n"><tuple><atom label="this/Node$3"/></tuple></skolem>
  </instance>
</alloy>
"""


class SliceDocumentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name) / "instance.xml"
        self.path.write_text(FIXTURE, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_prefix_and_zero_depth_keep_only_the_first_edge(self) -> None:
        result = slice_document(self.path, ["$Safe_"], set(), 0)
        instance = result["instances"][0]
        self.assertEqual(["$Safe_n"], [item["label"] for item in instance["skolems"]])
        self.assertEqual(
            [["this/Node$0", "this/Node$1"]],
            instance["fields"][0]["tuples"],
        )

    def test_one_expansion_adds_one_more_edge_not_the_whole_graph(self) -> None:
        result = slice_document(self.path, ["$Safe_"], {"demoLink"}, 1)
        self.assertEqual(
            [
                ["this/Node$0", "this/Node$1"],
                ["this/Node$1", "this/Node$2"],
            ],
            result["instances"][0]["fields"][0]["tuples"],
        )

    def test_requested_empty_field_is_distinct_from_a_missing_field(self) -> None:
        empty = slice_document(self.path, ["$Safe_"], {"demoEmpty"}, 0)
        field = empty["instances"][0]["fields"][0]
        self.assertEqual(0, field["total_tuple_count"])
        self.assertEqual(0, field["selected_tuple_count"])
        self.assertEqual([], field["tuples"])
        self.assertEqual([], selection_errors(empty))

        missing = slice_document(self.path, ["$Safe_"], {"missing"}, 0)
        self.assertEqual(["missing"], missing["unmatched_field_labels"])
        self.assertTrue(selection_errors(missing))

    def test_unmatched_skolem_and_temporal_metadata_are_reported(self) -> None:
        result = slice_document(self.path, ["$Missing_"], {"demoLink"}, 0)
        self.assertEqual(["$Missing_"], result["unmatched_skolem_prefixes"])
        self.assertEqual("3", result["instances"][0]["attributes"]["tracelength"])
        self.assertTrue(selection_errors(result))

    def run_cli(self, xml: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        path = Path(self.temporary.name) / "cli.xml"
        path.write_text(xml, encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("alloy_xml_slice.py")),
                str(path),
                *arguments,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def test_cli_fails_closed_for_unusable_documents_and_empty_selector(self) -> None:
        cases = [
            ("<document/>", ("--all-skolems",), "expected <alloy> root"),
            ("<alloy/>", ("--all-skolems",), "no <instance>"),
            ("<alloy><instance/></alloy>", ("--all-skolems",), "no labeled skolems"),
            (FIXTURE, ("--skolem-prefix", ""), "cannot be empty"),
        ]
        for xml, arguments, message in cases:
            with self.subTest(message=message):
                completed = self.run_cli(xml, *arguments)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(message, completed.stderr)

    def test_cli_unmatched_selectors_exit_nonzero_with_machine_output(self) -> None:
        completed = self.run_cli(
            FIXTURE,
            "--skolem-prefix",
            "$Missing_",
            "--field",
            "missing",
        )
        self.assertEqual(2, completed.returncode)
        self.assertEqual(
            ["$Missing_"],
            json.loads(completed.stdout)["unmatched_skolem_prefixes"],
        )
        self.assertIn("unmatched skolem prefixes", completed.stderr)


if __name__ == "__main__":
    unittest.main()
