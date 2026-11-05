#!/usr/bin/env python3
"""Independent raw-evidence audit; no producer checker imported."""
import copy, hashlib, json, subprocess
from pathlib import Path
p = json.loads(Path('evidence/l6-inventory/raw.json').read_text())
X = 'accepted x with retained identity / μ'.encode()
Z = 'unaccepted durable candidate z / μ'.encode()
def require(v, message):
    if not v: raise ValueError(message)
def frame(e):
    require(json.loads(e['raw_line']) == e['frame'], 'wire/frame contradiction')
    return e['frame']
def state(s):
    require(s['sealed'] and s['integrity_check'] == 'ok', 'unsealed or integrity failure')
    for f in s['files'].values():
        b = bytes.fromhex(f['raw_hex'])
        require(len(b) == f['size'] and hashlib.sha256(b).hexdigest() == f['sha256'], 'bytes/hash contradiction')
    require(s['unknown_files'] == sorted(set(s['files']) - {r['name'] for r in s['dependencies']}), 'unknown inventory contradiction')
def check_orphan(c, weak):
    g = frame(c['gate']); before = c['before_kill']; after = c['after_kill']; final = c['final']
    for s in (before, after, final): state(s)
    sql = [x['sql'] for x in g['sql_trace']]
    require(g['phase'] == 'file-fsynced-row-uncommitted' and g['in_transaction'] and g['local_dependency_rows'] == 1 and 'BEGIN IMMEDIATE' in sql and any(s.startswith('INSERT INTO dependencies') for s in sql) and 'COMMIT' not in sql, 'precommit gate')
    require(c['children'][0]['exit'] == -9 and c['children'][0]['exit_ns'] < after['observation_ns'], 'writer death/reap ordering')
    require(before['dependencies'] == after['dependencies'] == [] and after['unknown_files'] == ['z'] and bytes.fromhex(after['files']['z']['raw_hex']) == Z, 'orphan evidence')
    ready = frame(c['children'][1]['events'][0]); require(ready['snapshot']['reconstruction_status'] == 'unresolved-unregistered-material' and ready['snapshot']['live'] and ready['snapshot']['sealed'], 'reconstruction')
    r = frame(c['removal']); require(final['files'] == after['files'], 'candidate changed')
    require(('SELECT COUNT(*) FROM dependencies WHERE disposed=0' in [t['sql'] for t in r['sql_trace']]), 'catalog query missing')
    if weak: require(r['reply']['result'] == 'COMMITTED' and r['reply']['physical_boundary_removed'] is False and not final['live'] and final['objects_directory_exists'], 'weak control')
    else: require(r['reply']['result'] == 'DENY' and final['live'] and final['unknown_files'] == ['z'] and final['dependencies'] == after['dependencies'], 'directory guard')
require('harness_failure' not in p and p['execution_sha'] == 'b5b91fcb017c31ffec697f357228e3a3eef25313', 'execution identity')
require(set(p['cases']) == {'orphan_reference','orphan_catalog_mutant','interrupted_disposition','empty_positive'}, 'case set')
for name,h in p['source_hashes'].items():
    b = subprocess.check_output(['git','show',p['execution_sha']+':research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/'+name]); require(hashlib.sha256(b).hexdigest()==h, 'source mismatch')
require(0 < p['end_ns']-p['start_ns'] < 45e9 and p['environment']['address_space_bytes'] == 256*1024*1024, 'time/memory metadata')
children = [c for case in p['cases'].values() for c in case['children']]; require(len(children)==len({c['pid'] for c in children})==8, 'children')
timeline=[]
for c in children:
    require(c['start_ns'] < c['ready_ns'] < c['exit_ns'] and not c['stderr'], 'child lifecycle')
    timeline.extend([(c['start_ns'],1),(c['exit_ns'],-1)])
    for e in c['events']:
        f=frame(e); require(f['pid']==c['pid'] and c['start_ns']<e['received_ns']<c['exit_ns'], 'event attribution')
        if f['event']=='READY': require(f['source_sha256']==p['source_hashes']['store.py'], 'child source'); state(f['snapshot'])
        if f['event']=='RESPONSE': require(e['request_started_ns']<f['start_ns']<f['end_ns']<e['received_ns'], 'response ordering'); state(f['snapshot'])
active=maximum=0
for _,delta in sorted(timeline): active+=delta; maximum=max(active,maximum); require(active>=0, 'lifecycle ordering')
require(active==0 and maximum==1, 'concurrency')
for n,w in [('orphan_reference',False),('orphan_catalog_mutant',True)]: check_orphan(p['cases'][n],w)
c=p['cases']['interrupted_disposition']; a=c['after_kill']; state(a)
orig=[frame(e) for e in c['original_steps']]; require([f['reply']['result'] for f in orig]==['COMMITTED','COMMITTED','READ'] and bytes.fromhex(orig[2]['reply']['raw_hex'])==X, 'initial ACK/read')
g=frame(c['gate']); sql=[t['sql'] for t in g['sql_trace']]; require(g['phase']=='disposition-committed-before-unlink-reply' and not g['in_transaction'] and g['local_dependency_rows']==2 and any(s.startswith('UPDATE dependencies SET disposed=1') for s in sql) and 'COMMIT' in sql, 'disposition gate')
require(c['children'][1]['exit']==-9 and c['children'][1]['exit_ns']<a['observation_ns'] and len(c['children'][1]['events'])==2, 'disposer death/observed events')
rows={r['name']:r for r in a['dependencies']}; require(rows['x']['disposed']==1 and rows['z']['disposed']==0 and bytes.fromhex(a['files']['x']['raw_hex'])==X and bytes.fromhex(a['files']['z']['raw_hex'])==Z and a['live'], 'postkill state')
ready=frame(c['recovered_ready'])['snapshot']; require(all(ready[k]==a[k] for k in ('live','sealed','dependencies','files','unknown_files','objects_directory_exists')), 'recovery mismatch')
s=[frame(e) for e in c['recovered_steps']]; require([f['reply']['result'] for f in s]==['DENY','READ','DENY','COMMITTED','DENY','COMMITTED','COMMITTED'], 'continuation')
require(s[0]['reply']['reason']=='logically-disposed' and 'raw_hex' not in s[0]['reply'] and bytes.fromhex(s[1]['reply']['raw_hex'])==Z, 'logical reads')
require(set(s[3]['snapshot']['files'])=={'z'} and s[3]['snapshot']['files']['z']==a['files']['z'] and not c['final']['live'] and not c['final']['objects_directory_exists'], 'cleanup/final')
e=p['cases']['empty_positive']; require(frame(e['removal'])['reply']['result']=='COMMITTED' and not e['final']['live'] and not e['final']['objects_directory_exists'], 'empty positive')
controls={}
for name,change in [('missing',lambda c:c.pop('after_kill')),('contradiction',lambda c:c['after_kill']['files'].pop('z'))]:
    m=copy.deepcopy(p['cases']['orphan_reference']); change(m)
    try: check_orphan(m,False)
    except (KeyError,ValueError): controls[name]='rejected'
    else: raise ValueError('audit control accepted: '+name)
print(json.dumps({'verdict':'SUPPORTED within declared process-loss/store profile','children':len(children),'max_active':maximum,'elapsed_seconds':(p['end_ns']-p['start_ns'])/1e9,'controls':controls,'source_hashes_verified':True,'ack_qualification':'gate collected; source gates reply; transport not separately drained'},indent=2))
