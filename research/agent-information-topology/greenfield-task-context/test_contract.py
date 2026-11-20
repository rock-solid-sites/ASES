"""Contract checks for synthetic topology examples; no real resolver or model invocation."""
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def resolve_fixture(graph, task_id):
    """Tiny test oracle for exact applicability/overrides, not production resolver."""
    nodes = graph["nodes"]
    by_id = {n["id"]: n for n in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate node ID")
    edges = graph["edges"]
    for e in edges:
        if e["from"] not in by_id or e["to"] not in by_id:
            raise ValueError("dangling edge")
    task = by_id.get(task_id)
    if not task or task["kind"] != "task":
        raise ValueError("unknown task")

    rules = sorted(
        (by_id[e["from"]] for e in edges
         if e["type"] == "applies_to" and e["to"] == task_id
         and by_id[e["from"]]["kind"] == "rule"),
        key=lambda n: n["id"]
    )
    if len({n["id"] for n in rules}) != len(rules):
        raise ValueError("duplicate rule applicability")

    applicable_decisions = [
        by_id[e["from"]] for e in edges
        if e["type"] == "applies_to" and e["to"] == task_id
        and by_id[e["from"]]["kind"] == "decision"
    ]
    overrides = {}
    for dec in applicable_decisions:
        if (dec.get("decision_type") != "override"
                or dec.get("scope_task_id") != task_id
                or dec.get("status") != "approved-fixture"
                or not dec.get("authorized_by")):
            raise ValueError("unapproved or mis-scoped decision")
        destinations = [e["to"] for e in edges
                        if e["type"] == "overrides" and e["from"] == dec["id"]]
        if len(destinations) != 1 or destinations[0] in overrides:
            raise ValueError("missing or conflicting override target")
        overrides[destinations[0]] = dec

    applicable_rule_ids = {r["id"] for r in rules}
    if not set(overrides).issubset(applicable_rule_ids):
        raise ValueError("override does not apply to selected rule")

    source_ids = set()
    output = []
    for rule in rules:
        replacement = overrides.get(rule["id"])
        origin = replacement["id"] if replacement else next(
            (e["to"] for e in edges if e["type"] == "derived_from"
             and e["from"] == rule["id"]), None
        )
        if origin is None:
            raise ValueError("rule source missing")
        text = replacement["replacement_text"] if replacement else rule["text"]
        output.append({"rule_id": rule["id"], "origin": origin, "text": text})
        if replacement:
            origins = [e["to"] for e in edges if e["type"] == "derived_from"
                       and e["from"] == replacement["id"]]
            if len(origins) != 1 or by_id[origins[0]]["kind"] != "source":
                raise ValueError("override provenance missing")
            source_ids.add(origins[0])
        else:
            if by_id[origin]["kind"] != "source":
                raise ValueError("rule origin is not source")
            source_ids.add(origin)
    evidence = sorted(e["to"] for e in edges
                      if e["type"] == "supported_by" and e["from"] == task_id)
    return {
        "effective_rules": output,
        "selected_evidence": evidence,
        "receipt": {
            "source_revisions": sorted(
                ({"id": sid, "revision": by_id[sid]["revision"]} for sid in source_ids),
                key=lambda s: s["id"]),
            "selected_rule_ids": [r["id"] for r in rules],
            "override_decision_ids": sorted(d["id"] for d in overrides.values()),
            "replaced_upstream_rule_ids": sorted(overrides)
        }
    }


class ContextTopologyContract(unittest.TestCase):
    def setUp(self):
        self.graph = load("EXAMPLE-GRAPH.json")
        self.views = load("EXAMPLE-VIEWS.json")["views"]

    def test_graph_is_small_and_valid(self):
        self.assertEqual(self.graph["$schema_id"], "ases-context-topology/0.1-experimental")
        self.assertEqual(len(self.graph["nodes"]), 9)
        self.assertEqual(len(self.graph["edges"]), 12)
        self.assertTrue(all(n["id"].startswith(n["kind"] + ":")
                            for n in self.graph["nodes"]))

    def test_views_match_task_scoped_resolution(self):
        for view in self.views:
            with self.subTest(task=view["task_id"]):
                expected = resolve_fixture(self.graph, view["task_id"])
                self.assertEqual(view["effective_rules"], expected["effective_rules"])
                self.assertEqual(view["selected_evidence"], expected["selected_evidence"])
                for key, value in expected["receipt"].items():
                    self.assertEqual(view["receipt"][key], value)

    def test_replaced_text_is_physically_absent_in_alpha_view(self):
        a = next(v for v in self.views if v["task_id"] == "task:alpha")
        b = next(v for v in self.views if v["task_id"] == "task:beta")
        self.assertNotIn("OLD_UPSTREAM_REVIEW_CANARY", json.dumps(a))
        self.assertIn("ALPHA_LOCAL_REVIEW_CANARY", json.dumps(a))
        self.assertIn("OLD_UPSTREAM_REVIEW_CANARY", json.dumps(b))
        self.assertNotIn("ALPHA_LOCAL_REVIEW_CANARY", json.dumps(b))

    def test_no_model_launch_claims(self):
        for view in self.views:
            with self.subTest(task=view["task_id"]):
                self.assertIsNone(view["caller_authority"]["model_route"])
                self.assertIs(view["caller_authority"]["model_launch_authorized"], False)
                self.assertEqual(view["receipt"]["status"], "illustrative-unverified")

    def test_duplicate_nodes_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph["nodes"].append(copy.deepcopy(graph["nodes"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate node"):
            resolve_fixture(graph, "task:alpha")

    def test_dangling_relationship_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph["edges"].append({"type":"applies_to", "from":"rule:missing", "to":"task:alpha"})
        with self.assertRaisesRegex(ValueError, "dangling"):
            resolve_fixture(graph, "task:alpha")

    def test_cross_scope_override_rejected(self):
        graph = copy.deepcopy(self.graph)
        d = next(n for n in graph["nodes"] if n["id"] == "decision:alpha-review")
        d["scope_task_id"] = "task:beta"
        with self.assertRaisesRegex(ValueError, "unapproved or mis-scoped"):
            resolve_fixture(graph, "task:alpha")

    def test_conflicting_overrides_rejected(self):
        graph = copy.deepcopy(self.graph)
        extra = copy.deepcopy(next(n for n in graph["nodes"]
                                   if n["id"] == "decision:alpha-review"))
        extra["id"] = "decision:alpha-review-second"
        graph["nodes"].append(extra)
        graph["edges"].extend([
            {"type":"applies_to", "from":extra["id"], "to":"task:alpha"},
            {"type":"overrides", "from":extra["id"], "to":"rule:review"},
            {"type":"derived_from", "from":extra["id"], "to":"source:project-alpha"},
        ])
        with self.assertRaisesRegex(ValueError, "conflicting override"):
            resolve_fixture(graph, "task:alpha")

    def test_proposal_denies_legacy_as_design_constraint(self):
        proposal = (ROOT / "PROPOSAL.md").read_text(encoding="utf-8")
        self.assertIn("without requiring any existing document names", proposal)
        self.assertIn("No fixed startup or handoff documents are required", proposal)
        self.assertIn("not a universal context server", proposal.lower())


if __name__ == "__main__":
    unittest.main()
