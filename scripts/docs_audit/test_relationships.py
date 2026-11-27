"""Relationship extraction negative controls and reverse-lookup checks."""
import unittest
from relationships import relationship_graph, observations


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
