import hashlib, json, pathlib, sqlite3, sys, _sqlite3
base = pathlib.Path('docs/research/phase-i-f1')
for path in (base/'round2-commit-busy.raw.json', base/'review-autonomy-20261104-f1-commit-check/reproduction.raw.json'):
    x=json.loads(path.read_text())
    print('RAW',path,'sha256',hashlib.sha256(path.read_bytes()).hexdigest(),'source_revision',x['source_revision'])
    for name in ('held_reader','released_control'):
        c=x['cases'][name]; t=c['trace']; sql=[(e['sql'],e['outcome']) for e in t]
        assert c['prior_ack']['outcome']=='commit' and c['before']['view']==c['prior_ack']['state']
        assert c['lock_info']['stage']=='read_lock_held' and c['lock_info']['view_sha256']==c['before']['view_sha256']
        assert c['before']['integrity']==c['after']['integrity']=='ok'
        assert c['cold_read']['outcome']=='read' and c['cold_read']['state']==c['after']['view']
        assert t[2]['sql'].startswith('UPDATE') and t[2]['outcome']=='completed' and t[2]['in_transaction']
        assert t[2]['end_ns']<t[3]['start_ns'] and t[3]['sql']=='COMMIT'
        if name=='held_reader':
            assert t[3]['outcome']=='error' and t[3]['code']==5 and t[3]['name']=='SQLITE_BUSY' and t[3]['in_transaction']
            assert t[4]['sql']=='ROLLBACK' and t[4]['outcome']=='completed' and not t[4]['in_transaction']
            assert c['client']['kind']=='EOFError' and c['locker_alive_before_release']
            assert c['before']['view_utf8_hex']==c['after']['view_utf8_hex'] and c['after']['view']==c['prior_ack']['state']
        else:
            assert c['lock_release']['exit']==0 and not c['locker_alive_before_release']
            assert t[3]['outcome']=='completed' and not t[3]['in_transaction']
            assert c['client']['kind']=='reply' and c['client']['reply']['outcome']=='commit'
            assert c['after']['view']==c['client']['reply']['state'] and c['after']['view']!=c['before']['view']
        print(name, 'sql=',sql,'client=',c['client']['kind'],'before=',c['before']['view_sha256'],'after=',c['after']['view_sha256'],'cold_matches=True')
    for rel,digest in x['hashes'].items():
        p=base.parent/rel
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual==digest,(p,actual,digest)
    print('embedded source hashes match pinned checkout')
print('local executable',sys.executable,'sha256',hashlib.sha256(pathlib.Path(sys.executable).read_bytes()).hexdigest())
print('local python',sys.version,'sqlite',sqlite3.sqlite_version,'extension_origin',_sqlite3.__spec__.origin)
