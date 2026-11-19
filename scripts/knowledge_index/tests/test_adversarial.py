"""Red/green reproductions of the 2026-11-19 Phoenix Grove findings.

These are local deterministic tests of code behavior, not a service ACL audit.
"""
import json
import tempfile
import unittest
from pathlib import Path

from indexer import IndexErrorData, build, metadata, query, source_records, graph
from graph_view import public_projection, render_mermaid

FIX=Path(__file__).resolve().parents[1]/"fixtures/records.jsonl"

def records():
    return [json.loads(x) for x in FIX.read_text(encoding="utf-8").splitlines() if x.strip()]

class AdversarialFindingsTests(unittest.TestCase):
    def test_pg_ki_01_jsonl_meta_prefix_cannot_forge_public_edge(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[-1]["id"]="meta:forged-by-jsonl"
            rows[-1].pop("visibility",None)
            (root/"data.jsonl").write_text("\n".join(map(json.dumps,rows)))
            db=root/"index.sqlite"
            build(root,db)
            self.assertEqual(public_projection(db)["edges"],[])
            self.assertEqual(graph(db),[])

    def test_jsonl_cannot_spoof_internal_metadata_derivation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[-1]["id"]="meta:also-forged"
            rows[-1]["_derived_metadata"]=True
            rows[-1].pop("visibility",None)
            (root/"data.jsonl").write_text("\n".join(map(json.dumps,rows)))
            db=root/"index.sqlite"
            build(root,db)
            self.assertEqual(public_projection(db)["edges"],[])

    def test_pg_ki_01_cannot_spoof_internal_metadata_provenance(self):
        # A JSONL payload must not be able to opt into the metadata-derived
        # visibility exception by supplying an implementation-shaped field.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[-1]["id"]="meta:attacker-shaped"
            rows[-1]["_derived_metadata"]=True
            rows[-1].pop("visibility",None)
            (root/"data.jsonl").write_text("\n".join(map(json.dumps,rows)))
            db=root/"index.sqlite"
            build(root,db)
            self.assertEqual(public_projection(db)["edges"],[])

    def test_pg_ki_02_malformed_edge_endpoints_are_domain_errors(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[-1]["from"]=[]
            (root/"data.jsonl").write_text("\n".join(map(json.dumps,rows)))
            with self.assertRaises(IndexErrorData):
                build(root,root/"index.sqlite")

    def test_mimo_authority_markdown_image_syntax_escaped(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[0]["authority"]="Verified\n![pixel](https://tracker.invalid/pixel)"
            (root/"data.jsonl").write_text("\n".join(map(json.dumps,rows)))
            db=root/"index.sqlite"
            build(root,db)
            markdown=render_mermaid(db)
            self.assertNotIn("![pixel]",markdown)
            self.assertNotIn("\n![pixel]",markdown)

    def test_pg_ki_02_include_outside_jsonl_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)
            root=parent/"repo"
            root.mkdir()
            (parent/"outside.jsonl").write_text(json.dumps(records()[0])+"\n")
            with self.assertRaises(IndexErrorData):
                source_records(root,include_paths=["../outside.jsonl"])

    def test_pg_ki_02_file_symlink_outside_root_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)
            root=parent/"repo"
            root.mkdir()
            external=parent/"outside.jsonl"
            external.write_text(json.dumps(records()[0])+"\n")
            (root/"link.jsonl").symlink_to(external)
            with self.assertRaises(IndexErrorData):
                source_records(root,include_paths=["link.jsonl"])

    def test_pg_ki_03_partial_index_cannot_impersonate_registered_id(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            registry=root/"scripts/knowledge_index"
            registry.mkdir(parents=True)
            reserved="edases:doc:reserved"
            (registry/"identities.json").write_text(json.dumps({"version":1,"entries":[
                {"id":reserved,"path":"reserved.md","aliases":[]}
            ]}))
            (root/"intruder.md").write_text("---\nknowledge_id: "+reserved+"\n---\n# Intruder")
            with self.assertRaises(IndexErrorData):
                source_records(root,include_paths=["intruder.md"])

    def test_pg_ki_04_unquoted_trailing_apostrophe_is_not_removed(self):
        fields,warning=metadata("---\nknowledge_id: note:O'Brien'\n---\n# Text")
        self.assertIsNone(warning)
        self.assertEqual(fields["knowledge_id"],"note:O'Brien'")

    def test_pg_ki_05_bad_jsonl_records_give_domain_error(self):
        for content in ("42","[]",'{"id": []}'):
            with self.subTest(payload=content):
                with tempfile.TemporaryDirectory() as d:
                    root=Path(d)
                    (root/"bad.jsonl").write_text(content+"\n")
                    with self.assertRaises(IndexErrorData):
                        build(root,root/"out.sqlite")

    def test_pg_ki_06_search_with_fts_syntax_punctuation_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            db=root/"index.sqlite"
            build(FIX,db)
            for term in ('"', 'a AND','near(', ')'):
                with self.subTest(term=term):
                    self.assertIsInstance(query(db,term),list)

    def test_pg_ki_07_non_string_evidence_reference_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[-1]["evidence_refs"]=[None]
            (root/"bad.jsonl").write_text("\n".join(map(json.dumps,rows)))
            with self.assertRaises(IndexErrorData):
                build(root,root/"index.sqlite")

    def test_mimo_authority_markup_is_escaped(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[0]["authority"]="<img src=//tracker.invalid/p>"
            (root/"data.jsonl").write_text("\n".join(map(json.dumps,rows)))
            db=root/"index.sqlite"
            build(root,db)
            markdown=render_mermaid(db)
            self.assertNotIn("<img ",markdown)
            self.assertIn("&lt;img",markdown)


class IdentityAndVisibilityFollowups(unittest.TestCase):
    def test_jsonl_internal_metadata_fields_cannot_create_public_edges(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=records()
            rows[0]["_path"]="forged.md"
            rows[1]["_path"]="target.md"
            rows[0]["_metadata"]={"related_documents":["Central task assignment"]}
            rows[0]["_aliases"]=["forged.md"]
            (root/"records.jsonl").write_text("\n".join(map(json.dumps,rows)))
            db=root/"index.sqlite"
            build(root,db)
            self.assertEqual(len(public_projection(db)["edges"]),1)
            self.assertFalse(any(e["id"].startswith("meta:") for e in public_projection(db)["edges"]))

    def test_fresh_glm_jsonl_cannot_impersonate_reserved_partial_index_id(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            folder=root/"scripts/knowledge_index"
            folder.mkdir(parents=True)
            reserved="edases:doc:reserved-jsonl"
            (folder/"identities.json").write_text(json.dumps({"version":1,"entries":[
                {"id":reserved,"path":"registered.md","aliases":[]}
            ]}))
            fake={"id":reserved,"kind":"source","title":"Imposter",
                  "source_system":"github:rock-solid-sites/ASES",
                  "source_uri":"https://example.org/imposter",
                  "visibility":"public","content":"Injected content"}
            (root/"unregistered.jsonl").write_text(json.dumps(fake)+"\n")
            with self.assertRaisesRegex(IndexErrorData,"reserved"):
                build(root,root/"index.sqlite",include_paths=["unregistered.jsonl"])

    def test_fresh_glm_rejects_invalid_github_namespace_characters(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"note.md").write_text("# Document")
            for bad in ("github:owner/re po", "github:owner /repo",
                        "github:owner/repo/extra"):
                with self.subTest(namespace=bad):
                    with self.assertRaises(IndexErrorData):
                        source_records(root,namespace=bad,include_paths=["note.md"])

    def test_retired_registry_alias_is_not_an_active_source_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            location=root/"scripts/knowledge_index"
            location.mkdir(parents=True)
            stable="edases:doc:original"
            (location/"identities.json").write_text(json.dumps({"version":1,"entries":[
                {"id":stable,"path":"active.md","aliases":["retired.md"]}
            ]}))
            (root/"retired.md").write_text("---\nknowledge_id: "+stable+"\n---\n# New document")
            with self.assertRaises(IndexErrorData):
                source_records(root,include_paths=["retired.md"])

    def test_unsupported_frontmatter_cannot_promote_private_to_public(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"secret.md").write_text("---\nvisibility: private\nnested:\n  property: unsupported\n---\n# Secret")
            nodes,edges,warnings=source_records(root,default_visibility="public")
            self.assertTrue(warnings)
            self.assertEqual(nodes[0]["visibility"],"private")

    def test_unparseable_explicit_identity_fails_instead_of_reassigning(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"id.md").write_text("---\nknowledge_id: notes:stable\nnested:\n  property: unsupported\n---\n# Something")
            with self.assertRaises(IndexErrorData):
                source_records(root)

    def test_missing_mandatory_registry_is_reported(self):
        from registry import read_registry,RegistryError
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RegistryError):
                read_registry(Path(d),required=True)

    def test_registry_symlink_escape_fails(self):
        from registry import read_registry,RegistryError
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)
            folder=parent/"root"/"scripts"/"knowledge_index"
            folder.mkdir(parents=True)
            outside=parent/"outside.json"
            outside.write_text(json.dumps({"version":1,"entries":[]}))
            (folder/"identities.json").symlink_to(outside)
            with self.assertRaises(RegistryError):
                read_registry(parent/"root")

if __name__ == "__main__":
    unittest.main()
