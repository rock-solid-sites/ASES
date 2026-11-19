#!/usr/bin/env python3
"""Disposable read-only research-index prototype; never an authorization service."""
import argparse
import hashlib
import json
import re
import sqlite3
import tempfile
from pathlib import Path
from urllib.parse import quote

KINDS = {'source', 'concept', 'claim', 'design', 'decision', 'experiment', 'evidence'}
RELATIONS = {'discusses', 'supports', 'challenges', 'tests', 'implements', 'depends_on', 'related_to', 'supersedes'}
VISIBILITIES = {'public', 'private', 'restricted'}
REL_FIELDS = {'depends_on': 'depends_on', 'related_documents': 'related_to', 'supersedes': 'supersedes', 'implements': 'implements'}
SQL = '''
CREATE TABLE nodes (id TEXT PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL,
 source_uri TEXT NOT NULL, source_system TEXT NOT NULL, visibility TEXT NOT NULL,
 source_revision TEXT, authority TEXT, content TEXT NOT NULL);
CREATE TABLE edges (id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES nodes(id),
 target_id TEXT NOT NULL REFERENCES nodes(id), relation TEXT NOT NULL,
 review_status TEXT NOT NULL, assessment TEXT NOT NULL,
 evidence_refs TEXT NOT NULL, explanation TEXT NOT NULL);
CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,title,content);
'''

class IndexErrorData(ValueError):
    pass

def metadata(raw):
    """Parse only the deliberately small scalar/flat-list subset of EDASES YAML.

    Return (metadata, warning). Unsupported/malformed input is not silently
    interpreted as a relationship. No general YAML compatibility is claimed.
    """
    if not raw.startswith('---\n'):
        return {}, None
    lines = raw.splitlines()
    try:
        end = lines.index('---', 1)
    except ValueError:
        return {}, 'unterminated frontmatter'
    if end > 90:
        return {}, 'frontmatter exceeds 90 lines; quarantined'
    result = {}
    key = None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'([\w-]+):(?:\s+(.*))?', line)
        if match:
            key, val = match.groups()
            val = (val or '').strip()
            result[key] = [] if not val else ([] if val == '[]' else val.strip('\"\''))
            continue
        match = re.fullmatch(r'\s+[-*]\s+(.+?)\s*', line)
        if match and key and isinstance(result.get(key), list):
            result[key].append(match.group(1).strip().strip('\"\''))
            continue
        return {}, f'unsupported frontmatter near: {line[:90]}'
    return result, None

def source_records(root, namespace='github:rock-solid-sites/ASES', default_visibility='private', include_paths=None):
    nodes, edges, warnings = [], [], []
    paths = sorted((root / rel for rel in include_paths)) if include_paths is not None else sorted(root.rglob('*.md'))
    for path in paths:
        if not path.is_file():
            raise IndexErrorData(f'missing source file: {path}')
        if path.suffix != '.md':
            continue
        raw = path.read_text(encoding='utf-8')
        fm, warning = metadata(raw)
        relative = path.relative_to(root).as_posix()
        if warning:
            warnings.append(f'{relative}: {warning}')
        heading = re.search(r'^#\s+(.+)$', raw, re.MULTILINE)
        title = fm.get('title') if isinstance(fm.get('title'), str) else None
        title = title or (heading.group(1) if heading else path.stem)
        node_id = fm.get('knowledge_id') if isinstance(fm.get('knowledge_id'), str) else None
        node_id = node_id or f'{namespace}:doc:{relative}'
        node = {'id': node_id, 'kind': 'source', 'title': title,
                'source_uri': f'https://github.com/{namespace.removeprefix("github:")}/blob/main/{quote(relative)}',
                'source_system': namespace, 'visibility': fm.get('visibility') or default_visibility,
                'source_revision': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
                'authority': fm.get('authority') or '', 'content': raw,
                '_metadata': fm, '_path': relative}
        nodes.append(node)
    jsonl_paths = sorted((root / rel for rel in include_paths if rel.endswith('.jsonl'))) if include_paths is not None else sorted(root.rglob('*.jsonl'))
    for path in jsonl_paths:
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise IndexErrorData(f'{path}:{lineno}: {exc}') from exc
            if data.get('record_type') == 'edge' or ('from' in data and 'to' in data):
                edges.append(data)
            else:
                nodes.append(data)
    # Resolve only unambiguous metadata refs to indexed documents; never assert
    # a semantic relationship from a guessed title or lexical similarity.
    names = {}
    for n in nodes:
        if not n.get('_path'):
            continue
        aliases = {n['title'].casefold(), n['_path'].casefold(), Path(n['_path']).name.casefold(), Path(n['_path']).stem.casefold()}
        for alias in aliases:
            names.setdefault(alias, set()).add(n['id'])
    for n in nodes:
        if not n.get('_metadata'):
            continue
        for field, relation in REL_FIELDS.items():
            values = n['_metadata'].get(field, [])
            if isinstance(values, str):
                values = [values]
            for target in values:
                if not isinstance(target, str):
                    warnings.append(f'{n["_path"]}: unsupported {field} value')
                    continue
                matching = names.get(target.casefold(), set())
                if len(matching) == 1:
                    target_id = next(iter(matching))
                    edge_id = hashlib.sha256(f'{n["id"]}\0{relation}\0{target_id}'.encode()).hexdigest()[:24]
                    edges.append({'record_type': 'edge', 'id': f'meta:{edge_id}',
                                  'from': n['id'], 'to': target_id, 'relation': relation,
                                  'review_status': 'candidate', 'assessment': 'observed',
                                  'evidence_refs': [n['id']],
                                  'explanation': f'Unreviewed explicit {field} metadata: {target}'})
                else:
                    warnings.append(f'{n["_path"]}: {field} unresolved/ambiguous: {target}')
    return nodes, edges, warnings

def validate(nodes, edges):
    problems, known, edge_ids = [], {}, set()
    for n in nodes:
        identifier = n.get('id')
        if not isinstance(identifier, str) or not identifier or identifier in known:
            problems.append(f'duplicate/missing node id: {identifier}')
        known[identifier] = n
        for field in ('title', 'source_uri', 'source_system', 'visibility'):
            if not isinstance(n.get(field), str) or not n[field]:
                problems.append(f'{identifier}: missing {field}')
        if n.get('kind') not in KINDS:
            problems.append(f'{identifier}: invalid kind')
        if n.get('visibility') not in VISIBILITIES:
            problems.append(f'{identifier}: invalid visibility')
    for e in edges:
        identifier = e.get('id')
        if not identifier or identifier in edge_ids:
            problems.append(f'duplicate/missing edge id: {identifier}')
        edge_ids.add(identifier)
        a, b = e.get('from'), e.get('to')
        if a not in known or b not in known:
            problems.append(f'{identifier}: missing endpoint {a} -> {b}')
        if e.get('relation') not in RELATIONS:
            problems.append(f'{identifier}: invalid relation')
        if e.get('review_status') not in ('candidate', 'reviewed'):
            problems.append(f'{identifier}: invalid review status')
        if e.get('assessment') not in ('observed', 'inferred', 'hypothesized', 'disputed'):
            problems.append(f'{identifier}: invalid assessment')
        if not isinstance(e.get('evidence_refs'), list):
            problems.append(f'{identifier}: evidence_refs must be list')
        if a in known and b in known and e.get('visibility') == 'public' and (known[a]['visibility'] != 'public' or known[b]['visibility'] != 'public'):
            problems.append(f'{identifier}: public edge exposes non-public endpoint')
    if problems:
        raise IndexErrorData('\n'.join(problems))

def build(root, db, namespace='github:rock-solid-sites/ASES', default_visibility='private', include_paths=None):
    nodes, edges, warnings = source_records(root, namespace, default_visibility, include_paths)
    validate(nodes, edges)
    db.parent.mkdir(parents=True, exist_ok=True)
    # Atomic swap; failed builds do not destroy a prior successful projection.
    with tempfile.NamedTemporaryFile(prefix='.knowledge-', suffix='.sqlite', dir=db.parent, delete=False) as handle:
        tmp = Path(handle.name)
    try:
        con = sqlite3.connect(tmp)
        try:
            con.executescript(SQL)
            con.execute('PRAGMA foreign_keys=ON')
            for n in sorted(nodes, key=lambda x: x['id']):
                con.execute('INSERT INTO nodes VALUES (?,?,?,?,?,?,?,?,?)', tuple(n.get(k, '') for k in ('id', 'kind', 'title', 'source_uri', 'source_system', 'visibility', 'source_revision', 'authority', 'content')))
                con.execute('INSERT INTO search VALUES (?,?,?)', (n['id'], n['title'], n.get('content', '')))
            for e in sorted(edges, key=lambda x: x['id']):
                con.execute('INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)', (e['id'], e['from'], e['to'], e['relation'], e['review_status'], e['assessment'], json.dumps(e['evidence_refs'], sort_keys=True), e.get('explanation', '')))
            con.commit()
        finally:
            con.close()
        tmp.replace(db)
    finally:
        tmp.unlink(missing_ok=True)
    return len(nodes), len(edges), warnings

def query(db, term, include_private=False):
    with sqlite3.connect(db) as con:
        sql = 'SELECT n.id,n.title,n.source_uri FROM search s JOIN nodes n ON n.id=s.id WHERE search MATCH ?'
        if not include_private:
            sql += " AND n.visibility='public'"
        return con.execute(sql + ' ORDER BY rank', (term,)).fetchall()

def graph(db, include_private=False):
    with sqlite3.connect(db) as con:
        sql = 'SELECT e.source_id,e.relation,e.target_id,e.review_status FROM edges e JOIN nodes a ON a.id=e.source_id JOIN nodes b ON b.id=e.target_id'
        if not include_private:
            sql += " WHERE a.visibility='public' AND b.visibility='public'"
        return con.execute(sql + ' ORDER BY e.id').fetchall()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('database', type=Path)
    parser.add_argument('--namespace', default='github:rock-solid-sites/ASES')
    parser.add_argument('--default-visibility', choices=sorted(VISIBILITIES), default='private')
    parser.add_argument('--include', action='append', default=None, help='Repository-relative Markdown/JSONL file; repeat for multiple files')
    parser.add_argument('--search')
    parser.add_argument('--graph', action='store_true')
    args = parser.parse_args()
    n, e, warnings = build(args.source, args.database, args.namespace, args.default_visibility, args.include)
    print(f'indexed {n} nodes, {e} edges; {len(warnings)} metadata warnings')
    for warning in warnings[:30]:
        print('WARNING:', warning)
    if args.search:
        print('search:', query(args.database, args.search))
    if args.graph:
        print('graph:', graph(args.database))
