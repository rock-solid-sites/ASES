"""Relationship extraction negative controls and reverse-lookup checks."""
import unittest
from relationships import relationship_graph, observations, reconciliation_candidates, changed_source_paths


class RelationshipTests(unittest.TestCase):
    def test_reverse_lookup_with_external_and_pinned_references(self):
        core = "docs/core.md"
        skill = "skills/current/a/SKILL.md"
        retired = "SESSION-START.md"
        texts = {
            core: "---\ntitle: Core\nconsumed_by:\n  - " + skill + "\n---\n[old](../SESSION-START.md)",
            skill: "---\ndepends_on:\n  - Core\n---\n[core](../../../docs/core.md)\n`docs/core.md`\n"
                   "[pinned](https://github.com/rock-solid-sites/ASES/blob/" + "a"*40 + "/docs/core.md)\n"
                   "```\n[ignored](../../../docs/core.md)\n```",
            retired: "# retired",
        }
        state = {"revision": "fixture", "dirty": False}
        extra = [("org/private", {"README.md": "[core](https://github.com/rock-solid-sites/ASES/blob/main/docs/core.md)"},
                  {"README.md"}, state)]
        graph = relationship_graph("rock-solid-sites/ASES", texts, set(texts),
                                   [{"path": core, "declared_active": True, "status": "Active"},
                                    {"path": retired, "status": "Deprecated"}], state, extra)
        candidates = graph["incoming_candidates"]["rock-solid-sites/ASES:" + core]
        self.assertEqual({x["consumer"] for x in candidates},
                         {"rock-solid-sites/ASES:" + skill, "org/private:README.md"})
        self.assertEqual(len(graph["review_candidates"]), 1)
        self.assertEqual(sum(e["resolution"] == "pinned_revision" for e in graph["edges"]), 1)
        self.assertFalse(any(e["line"] == 9 and e["source_path"] == skill for e in graph["edges"]))

    def test_ambiguous_symbolic_alias_and_unsupported_list_not_guessed(self):
        texts = {"a.md": "---\ndepends_on:\n  - Common\nsupersedes: [one, two]\n---",
                 "x/Common.md": "# x", "y/Common.md": "# y"}
        graph = relationship_graph("org/repo", texts, set(texts), [], {"revision": "fixture", "dirty": False})
        self.assertEqual({x["resolution"] for x in graph["edges"]},
                         {"ambiguous_alias", "unsupported_metadata"})
        self.assertEqual(graph["incoming_candidates"], {})

    def test_nondefault_ref_and_related_documents_not_current_dependencies(self):
        texts = {"a.md": "---\nrelated_documents:\n  - b.md\n---\n"
                         "[branch](https://github.com/org/repo/blob/feature/b.md)",
                 "b.md": "# b"}
        graph = relationship_graph("org/repo", texts, set(texts), [], {"revision": "fixture", "dirty": False})
        self.assertEqual(graph["incoming_candidates"], {})
        self.assertTrue(any(x["resolution"] == "unverified_remote" for x in graph["edges"]))

    def test_inline_examples_and_fenced_examples_ignored(self):
        self.assertEqual(list(observations("`[old](old.md)`\n~~~\n[old](old.md)\n~~~")), [])


class AdaptationTests(unittest.TestCase):
    def test_pinned_adaptation_is_flagged_not_ordinary_history(self):
        repo = "org/source"
        core = "docs/core.md"
        pin = "a"*40
        url = "https://github.com/org/source/blob/" + pin + "/" + core
        texts = {core: "# Current"}
        state = {"revision": "fixture", "dirty": False}
        consumer = "---\\nadapted_from:\\n  - " + url + "\\n---\\n# Local authority\\nKeep local rules.\\n"
        external = {"AGENTS.md": consumer, "history.md": "[old](" + url + ")"}
        graph = relationship_graph(repo, texts, set(texts), [], state,
                                   [("org/local", external, set(external), state)])
        result = reconciliation_candidates(graph, repo, {core})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["consumer"], "org/local:AGENTS.md")
        self.assertEqual(result[0]["action"], "consider_reconciliation")
        self.assertEqual(result[0]["evidence"]["ref"], pin)
        self.assertEqual(external["AGENTS.md"], consumer)
        self.assertEqual(reconciliation_candidates(graph, repo, {"unrelated.md"}), [])

    def test_deleted_canonical_target_still_triggers_consideration(self):
        state = {"revision": "fixture", "dirty": False}
        external = {"AGENTS.md": "---\\nadapted_from:\\n  - https://github.com/org/source/blob/main/deleted.md\\n---"}
        graph = relationship_graph("org/source", {}, set(), [], state,
                                   [("org/local", external, set(external), state)])
        result = reconciliation_candidates(graph, "org/source", {"deleted.md"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["action"], "consider_reconciliation")
