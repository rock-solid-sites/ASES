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
            (root / 'all.jsonl').write_text('\n'.join(map(json.dumps, rows)))
            build(root, db)
            self.assertEqual(graph_details(db), [])
            self.assertEqual(len(graph_details(db, True)), 1)
