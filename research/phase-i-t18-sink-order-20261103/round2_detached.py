#!/usr/bin/env python3
"""Same original detached mode; only schedule differs from November 3."""
import hashlib
import json
from pathlib import Path
import platform
import tempfile
import post_replacement_send as post

with tempfile.TemporaryDirectory(prefix='ases-round2-detached-') as td:
    m=post.load(post.SOURCE,'original_detached_sink')
    s=m.RunningSink('detached-check',Path(td))
    try:
        steps=[]
        for path,body in [('/submit',{'authority_version':1,'request_id':'before','payload':'positive-v1'}),
                          ('/replace',{}),
                          ('/submit',{'authority_version':1,'request_id':'stale','payload':'stale-v1'}),
                          ('/submit',{'authority_version':2,'request_id':'current','payload':'positive-v2'})]:
            step=post.invoke(m,s.port,path,body)
            step['status']=m.latest_status(s)
            steps.append(step)
        raw=s.journal.read_bytes()
    finally:
        code=s.kill_and_reap()
    events=steps[-1]['status']['events']
    precheck=next(e for e in events if e['event']=='detached_permission_read' and e['request_id']=='stale')
    replace=next(e for e in events if e['event']=='authority_replaced')
    assert [x['response']['status'] for x in steps]==[201,200,409,201]
    assert steps[1]['completion_monotonic_ns']<steps[2]['start_monotonic_ns']
    assert replace['seq']<precheck['seq'] and precheck['observed_version']==2 and not precheck['allowed']
    assert {r['request_id'] for r in steps[-1]['status']['effects']}=={'before','current'}
    assert not any(r.get('request_id')=='stale' for r in map(json.loads,raw.splitlines()))
    print(json.dumps({'schema':'ases.t18-detached-postsend.v1','source_sha256':hashlib.sha256(post.SOURCE.read_bytes()).hexdigest(),
                      'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'environment':platform.platform(),'steps':steps,'sink_exit':code,'journal_raw_hex':raw.hex(),
                      'journal_sha256':hashlib.sha256(raw).hexdigest(),
                      'interpretation':'Original detached mutant does not discriminate in post-replacement initiation schedule'},indent=2))
