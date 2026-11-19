import json,sqlite3,tempfile,unittest
from pathlib import Path
from indexer import build,query,graph,IndexErrorData
FIX=Path(__file__).resolve().parents[1]/'fixtures'
class Tests(unittest.TestCase):
 def test_build_search_graph(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'index.sqlite';self.assertEqual(build(FIX,db)[:2],(2,1));self.assertEqual(len(query(db,'coordination')),2);self.assertEqual(len(graph(db)),1)
 def test_rebuild_deterministic(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'index.sqlite';build(FIX,db)
   with sqlite3.connect(db) as c: first=(c.execute('select * from nodes order by id').fetchall(),c.execute('select * from edges').fetchall())
   build(FIX,db)
   with sqlite3.connect(db) as c: second=(c.execute('select * from nodes order by id').fetchall(),c.execute('select * from edges').fetchall())
   self.assertEqual(first,second)
 def test_missing_endpoint_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'src';src.mkdir(); data=[json.loads(x) for x in (FIX/'records.jsonl').read_text().splitlines()];data[-1]['to']='missing';(src/'records.jsonl').write_text('\n'.join(map(json.dumps,data)))
   with self.assertRaisesRegex(IndexErrorData,'missing endpoint'):build(src,Path(d)/'x.sqlite')
 def test_duplicate_id_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'src';src.mkdir();lines=(FIX/'records.jsonl').read_text().splitlines();(src/'records.jsonl').write_text('\n'.join(lines[:1]+lines[:1]))
   with self.assertRaisesRegex(IndexErrorData,'duplicate'):build(src,Path(d)/'x.sqlite')
 def test_private_not_public(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'src';src.mkdir();data=[json.loads(x) for x in (FIX/'records.jsonl').read_text().splitlines()];data[1]['visibility']='private';data[2]['visibility']='private';(src/'records.jsonl').write_text('\n'.join(map(json.dumps,data)))
   db=Path(d)/'x.sqlite';build(src,db);self.assertEqual(graph(db),[]);self.assertEqual(len(graph(db,True)),1);self.assertEqual(query(db,'allocation'),[])
 def test_public_edge_private_endpoint_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'src';src.mkdir();data=[json.loads(x) for x in (FIX/'records.jsonl').read_text().splitlines()];data[1]['visibility']='private';(src/'records.jsonl').write_text('\n'.join(map(json.dumps,data)))
   with self.assertRaisesRegex(IndexErrorData,'exposes'):build(src,Path(d)/'x.sqlite')
 def test_markdown_import(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/'src';src.mkdir();(src/'note.md').write_text('---\ntitle: Example research\nknowledge_id: example:research\nvisibility: public\n---\n\nEvidence test')
   db=Path(d)/'x.sqlite';self.assertEqual(build(src,db)[:2],(1,0));self.assertEqual(query(db,'Evidence')[0][0],'example:research')

# These tests read actual ASES repository files on the remote CI checkout.
# They skip in fixture-only local runs, never count as passed.
from indexer import metadata, source_records
REPO = Path(__file__).resolve().parents[3]
REAL_DOCS = [
    'docs/research/LLM Agents and Distributed Systems - Research Topic.md',
    'docs/research/Cross-Project Knowledge Index - Minimal Schema and Integration Boundaries.md',
    'docs/research/Workflow Topology Design and Reasoning Record.md',
    'docs/standards/Documentation Standard.md',
    'docs/standards/Concept - Levels of Abstraction.md',
    'docs/standards/Canonical Terminology.md',
    'docs/research/EDASES Review Methodology.md',
    'docs/research/Heterogeneous Synthetic Scheduler Comparison 2026-11-01.md',
]
class RealRepositoryTests(unittest.TestCase):
    @unittest.skipUnless((REPO / REAL_DOCS[0]).exists(), 'requires an ASES repository checkout')
    def test_actual_ases_documents(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / 'real.sqlite'
            count, edges, warnings = build(REPO, db, include_paths=REAL_DOCS, default_visibility='public')
            self.assertEqual(count, 8)
            self.assertGreaterEqual(edges, 6)
            self.assertTrue(any('Canonical Terminology.md' in w for w in warnings))
            self.assertGreaterEqual(len(query(db, 'coordination')), 1)
            self.assertTrue(any(r[1] == 'depends_on' for r in graph(db)))
            self.assertTrue(all(r[3] == 'candidate' for r in graph(db)))
            with sqlite3.connect(db) as con:
                count_research = con.execute("SELECT count(*) FROM nodes WHERE authority='Experimental'").fetchone()[0]
                self.assertGreaterEqual(count_research, 3)

    @unittest.skipUnless((REPO / REAL_DOCS[0]).exists(), 'requires an ASES repository checkout')
    def test_real_source_provenance_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / 'real.sqlite'
            build(REPO, db, include_paths=REAL_DOCS, default_visibility='public')
            with sqlite3.connect(db) as con:
                first = (con.execute('SELECT id,title,source_uri,source_revision FROM nodes ORDER BY id').fetchall(),
                         con.execute('SELECT * FROM edges ORDER BY id').fetchall())
            build(REPO, db, include_paths=REAL_DOCS, default_visibility='public')
            with sqlite3.connect(db) as con:
                second = (con.execute('SELECT id,title,source_uri,source_revision FROM nodes ORDER BY id').fetchall(),
                          con.execute('SELECT * FROM edges ORDER BY id').fetchall())
            self.assertEqual(first, second)
            self.assertTrue(all('github.com/rock-solid-sites/ASES' in n[2] for n in first[0]))
            self.assertTrue(all(len(n[3]) == 64 for n in first[0]))

class MetadataRegressionTests(unittest.TestCase):
    def test_multiline_yaml_lists_and_colons(self):
        source = '''---
title: Concept: Levels of Abstraction
depends_on:
  - Documentation Standard
  - Concept: Levels of Abstraction
related_documents:
  * Evaluation Framework
supersedes: []
---
# document'''
        fm, warning = metadata(source)
        self.assertIsNone(warning)
        self.assertEqual(fm['depends_on'], ['Documentation Standard', 'Concept: Levels of Abstraction'])
        self.assertEqual(fm['related_documents'], ['Evaluation Framework'])
        self.assertEqual(fm['supersedes'], [])

    def test_malformed_frontmatter_is_quarantined(self):
        fm, warning = metadata('---\ntitle: Faulty\n' + 'item: value\n' * 100 + '---\n# content')
        self.assertEqual(fm, {})
        self.assertIn('quarantined', warning)

    def test_unresolved_is_warning_not_fabricated_edge(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'one.md').write_text('---\ntitle: Real node\nrelated_documents:\n  - Imaginary node\n---\n# Real')
            nodes, edges, warnings = source_records(root)
            self.assertEqual(len(nodes), 1)
            self.assertEqual(edges, [])
            self.assertTrue(any('unresolved' in w for w in warnings))

    def test_failed_build_preserves_existing_index(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / 'data.sqlite'
            build(FIX, db)
            prior = db.read_bytes()
            root = Path(d) / 'bad'
            root.mkdir()
            (root / 'a.jsonl').write_text('{"id":"duplicate"}\n{"id":"duplicate"}')
            with self.assertRaises(IndexErrorData):
                build(root, db)
            self.assertEqual(db.read_bytes(), prior)

    def test_explicit_identity_survives_rename(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            old = root / 'old.md'
            old.write_text('---\nknowledge_id: topic:test\ntitle: Renamable\n---\n# Content')
            self.assertEqual(source_records(root)[0][0]['id'], 'topic:test')
            old.rename(root / 'new.md')
            self.assertEqual(source_records(root)[0][0]['id'], 'topic:test')


    def test_graph_details_preserve_provenance_and_visibility(self):
        from indexer import graph_details
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rows = [json.loads(x) for x in (FIX / 'records.jsonl').read_text().splitlines()]
            (root / 'all.jsonl').write_text('\n'.join(map(json.dumps, rows)))
            db = root / 'index.sqlite'
            # Build must not recursively ingest an output index.
            build(root, db)
            details = graph_details(db)
            self.assertEqual(len(details), 1)
            self.assertEqual(details[0]['review_status'], 'candidate')
            self.assertEqual(details[0]['evidence_refs'], ['doi:10.1073/pnas.2612825123'])
            self.assertIn('doi.org', details[0]['from_uri'])
            rows[1]['visibility'] = 'private'
            rows[2]['visibility'] = 'private'  # edge cannot advertise private endpoint publicly
            (root / 'all.jsonl').write_text('\n'.join(map(json.dumps, rows)))
            build(root, db)
            self.assertEqual(graph_details(db), [])
            self.assertEqual(len(graph_details(db, True)), 1)


class RegistryAndDiagnosticTests(unittest.TestCase):
    def test_registry_survives_rename_and_content_edit(self):
        from registry import read_registry
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            registry = root / 'scripts/knowledge_index'
            registry.mkdir(parents=True)
            old = root / 'old.md'
            old.write_text('---\ntitle: Fixed identity\n---\n# One')
            stable = 'edases:doc:immutable-test'
            registry_file = registry / 'identities.json'
            registry_file.write_text(json.dumps({'version': 1, 'entries': [
                {'id': stable, 'path': 'old.md', 'aliases': []}]}))
            self.assertEqual(source_records(root)[0][0]['id'], stable)
            (root / 'old.md').rename(root / 'new.md')
            (root / 'new.md').write_text('---\ntitle: New title\n---\n# Two')
            registry_file.write_text(json.dumps({'version': 1, 'entries': [
                {'id': stable, 'path': 'new.md', 'aliases': ['old.md']}]}))
            nodes, edges, warnings = source_records(root)
            self.assertEqual(nodes[0]['id'], stable)
            self.assertEqual(nodes[0]['title'], 'New title')
            self.assertIn('old.md', nodes[0]['_aliases'])

    def test_registry_collision_and_conflicting_inline_id_fail_closed(self):
        from registry import RegistryError
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            loc = root / 'scripts/knowledge_index'
            loc.mkdir(parents=True)
            (root / 'note.md').write_text('---\nknowledge_id: explicit:one\n---\n# Note')
            reg = loc / 'identities.json'
            reg.write_text(json.dumps({'version': 1, 'entries': [
                {'id': 'registered:one', 'path': 'note.md', 'aliases': []}]}))
            with self.assertRaisesRegex(IndexErrorData, 'contradicts'):
                source_records(root)
            reg.write_text(json.dumps({'version': 1, 'entries': [
                {'id': 'registered:one', 'path': 'note.md', 'aliases': []},
                {'id': 'registered:two', 'path': 'other.md', 'aliases': ['note.md']}]}))
            with self.assertRaisesRegex(RegistryError, 'duplicate registered'):
                source_records(root)

    def test_warning_categories_conservatively_classified(self):
        from indexer import summarize_diagnostics
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'Available.md').write_text('# available')
            warnings = [
                'x.md: related_documents unresolved/ambiguous: Available',
                'y.md: related_documents unresolved/ambiguous: Unknown source',
                'z.md: unsupported frontmatter near: bad',
                'w.md: unterminated frontmatter',
                'v.md: related_documents ambiguous: Duplicate (2 matches)',
            ]
            result = summarize_diagnostics(warnings, root, include_paths=['x.md'])
            self.assertEqual(result['counts']['outside_index_scope'], 1)
            self.assertEqual(result['counts']['unresolved_unverified'], 1)
            self.assertEqual(result['counts']['unsupported_metadata'], 1)
            self.assertEqual(result['counts']['malformed_frontmatter'], 1)
            self.assertEqual(result['counts']['ambiguous_reference'], 1)


class GraphProjectionTests(unittest.TestCase):
    def test_public_projection_and_readonly_mermaid(self):
        from graph_view import public_projection, render_mermaid, render_html
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / 'graph.sqlite'
            build(FIX, db)
            p = public_projection(db)
            self.assertEqual(len(p['nodes']), 2)
            self.assertEqual(len(p['edges']), 1)
            self.assertIn('candidate', render_mermaid(db))
            self.assertIn('mermaid', render_mermaid(db))
            self.assertIn('doi.org', render_mermaid(db))
            self.assertIn('aria-label', render_html(db))
            self.assertIn('Content-Security-Policy', render_html(db))

    def test_private_edge_and_private_evidence_not_exported(self):
        from graph_view import public_projection, render_mermaid, render_html
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            raw = [json.loads(x) for x in (FIX / 'records.jsonl').read_text().splitlines()]
            db = root / 'index.sqlite'
            raw[-1]['visibility'] = 'private'
            (root / 'input.jsonl').write_text('\n'.join(map(json.dumps, raw)))
            build(root, db)
            self.assertEqual(public_projection(db)['edges'], [])
            self.assertNotIn('edases:edge:pnas-assignment', render_html(db))
            raw[-1]['visibility'] = 'public'
            raw[-1]['evidence_refs'] = ['secret:archive:uuid']
            (root / 'input.jsonl').write_text('\n'.join(map(json.dumps, raw)))
            build(root, db)
            self.assertEqual(public_projection(db)['edges'], [])
            self.assertNotIn('secret:archive:uuid', render_html(db))
            self.assertNotIn('secret:archive:uuid', render_mermaid(db))

    def test_html_and_mermaid_escape_untrusted_source(self):
        from graph_view import render_mermaid, render_html, public_projection
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            entries=[json.loads(x) for x in (FIX / 'records.jsonl').read_text().splitlines()]
            entries[0]['title']='</script><img src=x onerror=alert(1)>'
            entries[0]['source_uri']='javascript:alert(1)'
            (root / 'input.jsonl').write_text('\n'.join(map(json.dumps, entries)))
            db=root/'graph.sqlite'
            build(root,db)
            html=render_html(db)
            self.assertNotIn('</script><img',html)
            self.assertIn('\\u003c/script',html)
            self.assertNotIn('javascript:alert', html)
            m=render_mermaid(db)
            self.assertNotIn('<img',m)
            self.assertIn('&lt;img',m)
            self.assertNotIn('</script>',m)
            self.assertIn('&lt;/script&gt;',m)
            self.assertNotIn('javascript:alert',m)
            self.assertEqual(public_projection(db)['nodes'][0]['source_uri'],'')

    @unittest.skipUnless((REPO / REAL_DOCS[0]).exists(), 'requires ASES checkout')
    def test_actual_graph_pilot_both_concept_to_design_edges(self):
        from graph_view import public_projection, render_mermaid, render_html
        paths=REAL_DOCS + ['docs/research/ASES Solver Capabilities and Rust Architecture Review 2026-11-01.md',
                           'docs/research/knowledge-index/pilot-2026-11-19.jsonl']
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'pilot.sqlite'
            build(REPO, db, include_paths=paths,default_visibility='public')
            p=public_projection(db)
            names={n['id'] for n in p['nodes']}
            self.assertIn('edases:concept:central-task-assignment',names)
            self.assertIn('edases:concept:information-asymmetry-boundary',names)
            links={(e['from'],e['to']) for e in p['edges']}
            self.assertIn(('edases:concept:central-task-assignment',
                           'github:rock-solid-sites/ASES:doc:docs/research/ASES Solver Capabilities and Rust Architecture Review 2026-11-01.md'),links)
            self.assertIn(('edases:concept:information-asymmetry-boundary',
                           'github:rock-solid-sites/ASES:doc:docs/research/Workflow Topology Design and Reasoning Record.md'),links)
            view=render_mermaid(db,focus=['edases:concept:central-task-assignment',
                                          'edases:concept:information-asymmetry-boundary'])
            self.assertIn('flowchart LR',view)
            self.assertIn('Candidate', view.title())
            self.assertIn('source references',view.lower())
            self.assertTrue(render_html(db).startswith('<!doctype html>'))
