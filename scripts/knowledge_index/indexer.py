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
from collections import Counter
from registry import read_registry, RegistryError

KINDS = {'source', 'concept', 'claim', 'design', 'decision', 'experiment', 'evidence'}
RELATIONS = {'discusses', 'supports', 'challenges', 'tests', 'implements', 'depends_on', 'related_to', 'supersedes'}
VISIBILITIES = {'public', 'private', 'restricted'}
REL_FIELDS = {'depends_on': 'depends_on', 'related_documents': 'related_to', 'supersedes': 'supersedes', 'implements': 'implements'}
SQL = '''
CREATE TABLE nodes (id TEXT PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL,
 source_uri TEXT NOT NULL, source_system TEXT NOT NULL, visibility TEXT NOT NULL,
 source_revision TEXT, authority TEXT, content TEXT NOT NULL);
CREATE TABLE edges (id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES nodes(id),
 target_id TEXT NOT NULL REFERENCES nodes(id), relation TEXT NOT NULL, visibility TEXT NOT NULL,
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
    identities = read_registry(root)
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
        declared_id = fm.get('knowledge_id') if isinstance(fm.get('knowledge_id'), str) else None
        registered = identities.get(relative)
        if registered and declared_id and declared_id != registered['id']:
            raise IndexErrorData(f'{relative}: knowledge_id contradicts identity registry')
        node_id = declared_id or (registered['id'] if registered else None)
        node_id = node_id or f'{namespace}:doc:{relative}'
        node = {'id': node_id, 'kind': 'source', 'title': title,
                'source_uri': f'https://github.com/{namespace.removeprefix("github:")}/blob/main/{quote(relative)}',
                'source_system': namespace, 'visibility': fm.get('visibility') or default_visibility,
                'source_revision': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
                'authority': fm.get('authority') or '', 'content': raw,
                '_metadata': fm, '_path': relative,
                '_aliases': registered['aliases'] if registered else []}
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
        names_for_node = [n['title'], n['_path'], Path(n['_path']).name, Path(n['_path']).stem] + n.get('_aliases', [])
        aliases = {name.casefold() for name in names_for_node}
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
                elif len(matching) > 1:
                    warnings.append(f'{n["_path"]}: {field} ambiguous: {target} ({len(matching)} matches)')
                else:
                    warnings.append(f'{n["_path"]}: {field} unresolved/ambiguous: {target}')
    # Explicit JSONL edges default private. Edges mechanically derived from
    # two public metadata documents may be marked public automatically.
    by_id = {n['id']: n for n in nodes if isinstance(n.get('id'), str)}
    for e in edges:
        if not e.get('visibility'):
            a, b = by_id.get(e.get('from')), by_id.get(e.get('to'))
            public_metadata = (isinstance(e.get('id'), str)
                and e['id'].startswith('meta:') and a and b
                and a.get('visibility') == 'public'
                and b.get('visibility') == 'public')
            e['visibility'] = 'public' if public_metadata else 'private'
    return nodes, edges, warnings


def summarize_diagnostics(warnings, root=None, include_paths=None):
    """Classify warnings conservatively without declaring missing repository sources.

    A reference might exist outside the checkout or in a source with a different
    title. 'unresolved' is NOT a claim that a document does not exist.
    """
    indexed = set(include_paths or [])
    available = set()
    if root is not None:
        available = {p.relative_to(root).as_posix() for p in Path(root).rglob('*.md')}
    stems = {}
    for path in available:
        for token in (path.casefold(), Path(path).stem.casefold(), Path(path).name.casefold()):
            stems.setdefault(token, set()).add(path)
    counts = Counter()
    details = []
    for message in warnings:
        kind = "other"
        if "unterminated frontmatter" in message or "frontmatter exceeds" in message:
            kind = "malformed_frontmatter"
        elif "unsupported frontmatter" in message:
            kind = "unsupported_metadata"
        elif " ambiguous: " in message:
            kind = "ambiguous_reference"
        elif " unresolved/ambiguous: " in message:
            target = message.rsplit(" unresolved/ambiguous: ", 1)[1].strip()
            matches = stems.get(target.casefold(), set())
            if matches and not matches.intersection(indexed):
                kind = "outside_index_scope"
            elif len(matches) > 1:
                kind = "ambiguous_reference"
            else:
                kind = "unresolved_unverified"
        elif "unsupported" in message:
            kind = "unsupported_metadata"
        counts[kind] += 1
        details.append({"kind": kind, "message": message})
    return {"counts": dict(sorted(counts.items())), "details": details}

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
        if e.get('visibility') not in VISIBILITIES:
            problems.append(f'{identifier}: invalid edge visibility')
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
                con.execute('INSERT INTO edges VALUES (?,?,?,?,?,?,?,?,?)', (e['id'], e['from'], e['to'], e['relation'], e['visibility'], e['review_status'], e['assessment'], json.dumps(e['evidence_refs'], sort_keys=True), e.get('explanation', '')))
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
    if not include_private:
        from graph_view import public_projection
        return [(e['from'], e['relation'], e['to'], e['review_status'])
                for e in public_projection(db)['edges']]
    with sqlite3.connect(db) as con:
        sql = 'SELECT e.source_id,e.relation,e.target_id,e.review_status FROM edges e JOIN nodes a ON a.id=e.source_id JOIN nodes b ON b.id=e.target_id'
        if not include_private:
            sql += " WHERE e.visibility='public' AND a.visibility='public' AND b.visibility='public'"
        return con.execute(sql + ' ORDER BY e.id').fetchall()


def graph_details(db, include_private=False):
    """Source-linked candidate graph; raw private access is for trusted local tests only."""
    if not include_private:
        from graph_view import public_projection
        data = public_projection(db)
        urls = {n['id']: n['source_uri'] for n in data['nodes']}
        return [dict(e, from_uri=urls[e['from']], to_uri=urls[e['to']])
                for e in data['edges']]
    with sqlite3.connect(db) as con:
        sql = '''SELECT e.id,e.source_id,e.relation,e.target_id,e.review_status,
                        e.assessment,e.evidence_refs,e.explanation,a.source_uri,b.source_uri
                 FROM edges e JOIN nodes a ON a.id=e.source_id
                              JOIN nodes b ON b.id=e.target_id'''
        if not include_private:
            sql += " WHERE e.visibility='public' AND a.visibility='public' AND b.visibility='public'"
        return [dict(zip(('id','from','relation','to','review_status','assessment',
                          'evidence_refs','explanation','from_uri','to_uri'),
                         (r[0],r[1],r[2],r[3],r[4],r[5],json.loads(r[6]),r[7],r[8],r[9])))
                for r in con.execute(sql + ' ORDER BY e.id')]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('database', type=Path)
    parser.add_argument('--namespace', default='github:rock-solid-sites/ASES')
    parser.add_argument('--default-visibility', choices=sorted(VISIBILITIES), default='private')
    parser.add_argument('--include', action='append', default=None, help='Repository-relative Markdown/JSONL file; repeat for multiple files')
    parser.add_argument('--search')
    parser.add_argument('--diagnostics', action='store_true')
    parser.add_argument('--graph', action='store_true')
    args = parser.parse_args()
    n, e, warnings = build(args.source, args.database, args.namespace, args.default_visibility, args.include)
    print(f'indexed {n} nodes, {e} edges; {len(warnings)} metadata warnings')
    for warning in warnings[:30]:
        print('WARNING:', warning)
    if args.diagnostics:
        print('diagnostics:', json.dumps(summarize_diagnostics(warnings, args.source, args.include), indent=2))
    if args.search:
        print('search:', query(args.database, args.search))
    if args.graph:
        print('graph:', graph(args.database))
