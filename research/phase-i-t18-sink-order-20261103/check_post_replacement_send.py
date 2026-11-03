#!/usr/bin/env python3
"""Read-only mapping of post-replacement client/sink observations to T18."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FIXTURE=ROOT/'docs/architecture/core-substrate/fixtures-f2/fixtures.json'
PIN='5fb690d4ba7544a4a7eb5fce9ca1e54485543d64'

class Incomplete(Exception): pass

def need(value, reason):
    if not value: raise Incomplete(reason)


def check(case):
    try:
        need(isinstance(case,dict),'case missing')
        need(case.get('sink_exit') == -9 and type(case.get('sink_pid')) is int,'missing sink kill/reap')
        steps=case['steps']; need(isinstance(steps,list) and len(steps)==4,'four recorded calls required')
        requests=[('/submit',1,'before-current','before-x'),('/replace',None,None,None),
                  ('/submit',1,'after-stale','stale-x'),('/submit',2,'after-current','current-x')]
        expected_status=(201,200,None,201)
        for i,(step,(path,version,rid,payload)) in enumerate(zip(steps,requests)):
            need(isinstance(step,dict) and all(k in step for k in ('request','response','start_monotonic_ns','completion_monotonic_ns','sink_snapshot')),'missing client/sink observation')
            start,end=step['start_monotonic_ns'],step['completion_monotonic_ns']
            need(type(start) is int and type(end) is int and 0 < start <= end,'invalid client time interval')
            if i: need(steps[i-1]['completion_monotonic_ns'] < start,'calls not demonstrably sequential')
            req=step['request']; need(req.get('method')=='POST' and req.get('path')==path and isinstance(req.get('body'),dict),'unexpected call')
            body=req['body']
            if version is None: need(body=={},'replacement body mismatch')
            else: need(body=={'authority_version':version,'request_id':rid,'payload':payload},'request identity mismatch')
            response=step['response']; need(isinstance(response,dict) and 'status' in response and isinstance(response.get('body'),dict),'missing response')
            if expected_status[i] is not None: need(response['status']==expected_status[i],'missing expected positive/replace response')
            if i==1: need(response['body'].get('outcome')=='replaced' and response['body'].get('authority_version')==2,'replacement ACK invalid')
        # Completion of the replacement ACK precedes invocation of the old request.
        need(steps[1]['completion_monotonic_ns'] < steps[2]['start_monotonic_ns'],'post-replacement start not proved')
        snap=steps[-1]['sink_snapshot']
        need(isinstance(snap,dict) and isinstance(snap.get('events'),list) and isinstance(snap.get('effects'),list),'missing final sink snapshot')
        events=snap['events']; need(len(events)==4 and all(isinstance(e,dict) for e in events),'missing or extra event')
        need([e.get('seq') for e in events]==[1,2,3,4],'event sequence gap')
        for i,step in enumerate(steps):
            snapshot=step['sink_snapshot']
            need(isinstance(snapshot,dict) and snapshot.get('events')==events[:i+1],'snapshot/event prefix mismatch')
        before,replace,stale,after=events
        need(before.get('event')=='effect_accepted' and before.get('request_id')=='before-current' and before.get('presented_version')==before.get('accepted_under_version')==1,'initial positive missing')
        need(replace.get('event')=='authority_replaced' and (replace.get('previous_version'),replace.get('current_version'))==(1,2),'replacement event missing')
        need(after.get('event')=='effect_accepted' and after.get('request_id')=='after-current' and after.get('presented_version')==after.get('accepted_under_version')==2,'new current positive missing')
        need(before.get('payload')=='before-x' and after.get('payload')=='current-x','positive payload mismatch')
        for i,event in ((0,before),(3,after)):
            body=steps[i]['response']['body']
            need(body.get('outcome')=='accepted' and body.get('event_seq')==event['seq'],'positive ACK mismatch')
        need(stale.get('request_id')=='after-stale' and stale.get('presented_version')==1,'stale event identity/version missing')
        need(snap['effects']==[e for e in events if e.get('event')=='effect_accepted'],'effect snapshot mismatch')
        try: raw=bytes.fromhex(case['journal_raw_hex'])
        except (KeyError,ValueError,TypeError): raise Incomplete('missing/invalid journal')
        need(hashlib.sha256(raw).hexdigest()==case.get('journal_sha256'),'journal hash mismatch')
        need(raw.endswith(b'\n'),'incomplete journal framing')
        try: journal=[json.loads(line) for line in raw.splitlines()]
        except (ValueError,UnicodeError): raise Incomplete('malformed journal')
        need(journal==[e for e in events if e.get('event') in ('effect_accepted','authority_replaced','obligation_committed')],'journal and event mismatch')
        stale_status=steps[2]['response']['status']; stale_body=steps[2]['response']['body']
        if stale.get('event')=='sink_rejected':
            need(stale.get('current_version')==2 and stale_status==409 and stale_body.get('outcome')=='rejected','stale denial mismatch')
            need(not any(e.get('request_id')=='after-stale' for e in snap['effects']),'stale effect observed despite denial')
            status, reason='SUPPORTED_SELECTED_MAPPING','post-replacement stale request rejected, no stale effect'
        elif stale.get('event')=='effect_accepted':
            need(stale.get('accepted_under_version')==2 and stale.get('payload')=='stale-x' and stale_status==201 and stale_body.get('outcome')=='accepted' and stale_body.get('event_seq')==stale['seq'],'stale acceptance mismatch')
            status, reason='VIOLATION','post-replacement stale request accepted under new current version'
        else: raise Incomplete('stale outcome event missing')
        return {'status':status,'reason':reason,'sequence':{'replacement':replace['seq'],'stale':stale['seq'],'new_current':after['seq']},
                'replacement_ack_complete_ns':steps[1]['completion_monotonic_ns'],
                'stale_call_start_ns':steps[2]['start_monotonic_ns'],
                'scope':'version invalidation is selected revoke analogue; initial F2 create/grant/activate are trusted bootstrap and not observed'}
    except (Incomplete,KeyError,TypeError) as e: return {'status':'INCOMPLETE','reason':str(e)}


def main():
    raw_path=HERE/'post-replacement-send-raw.json'
    raw=json.loads(raw_path.read_text()); fixtures=json.loads(FIXTURE.read_text())
    item=next(x for x in fixtures['fixtures'] if x['id']=='T18-use-current-sink-order-after-revocation')
    assert item['status']=='prepared-only' and [e['ev'] for e in item['events']][:2]==['revoke','sink_send']
    assert item['expected_observation']['sink']=='rejected' and item['expected_observation']['store']['content.x.sink_accept']==0
    original=check(raw['cases']['reference']); mutant=check(raw['cases']['bypass_mutant'])
    missing=copy.deepcopy(raw['cases']['reference']); missing['steps'][-1]['sink_snapshot']['events'].pop(2)
    trunc=copy.deepcopy(raw['cases']['reference']); b=bytes.fromhex(trunc['journal_raw_hex'])[:-1]
    trunc['journal_raw_hex']=b.hex(); trunc['journal_sha256']=hashlib.sha256(b).hexdigest()
    no_time=copy.deepcopy(raw['cases']['reference']); del no_time['steps'][2]['start_monotonic_ns']
    controls={'missing_event':check(missing),'truncated_journal':check(trunc),'missing_send_time':check(no_time)}
    assert original['status']=='SUPPORTED_SELECTED_MAPPING' and mutant['status']=='VIOLATION'
    assert all(c['status']=='INCOMPLETE' for c in controls.values())
    pinned=subprocess.run(['git','show',PIN+':docs/architecture/core-substrate/fixtures-f2/fixtures.json'],cwd=ROOT,capture_output=True,check=True).stdout
    fixture_hash=hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert hashlib.sha256(pinned).hexdigest()==fixture_hash
    source_hash=hashlib.sha256((HERE/'run.py').read_bytes()).hexdigest()
    assert raw['source_sha256']==source_hash
    source=(HERE/'run.py').read_text()
    needle='''                    if token != state.version:
                        state.emit_locked(
                            "sink_rejected",'''
    replacement='''                    if False and token != state.version:
                        state.emit_locked(
                            "sink_rejected",'''
    assert source.count(needle)==1
    expected_mutant=hashlib.sha256(source.replace(needle,replacement,1).encode()).hexdigest()
    assert raw['mutant_sha256']==expected_mutant
    out={'reference':original,'bypass_mutant':mutant,'incomplete_controls':controls,
         'fixture':{'id':item['id'],'status_preserved':item['status'],'commit':PIN,'sha256':fixture_hash},
         'provenance':{'raw_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),
                       'sink_source_sha256':source_hash,'mutant_source_sha256':raw['mutant_sha256']},
         'limits':['no independently recorded F2 bootstrap create/grant/activate',
                   'version invalidation is a selected analogue of revocation',
                   'monotonic client invocation markers are not packet timestamps',
                   'no host confinement, F3/F2 aggregate acceptance or power-loss claim']}
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
