#!/usr/bin/env python3
"""Separate invalid config, committed malformed data, conflicts and startup refusal."""
import copy
import json
from pathlib import Path
import sys

class Incomplete(Exception):pass
class Violation(Exception):pass
def need(v,msg):
    if not v:raise Incomplete(msg)
def expect(v,msg):
    if not v:raise Violation(msg)
def case(value,phase):
    try:
        name=value['name'];writer=value['writer'];request=value['request'];trace=value['writer_trace']
        need(type(writer['ready']) is bool,'missing actual startup result')
        raw=value['diagnostic']['observation']
        expect(raw['diagnostic_only'] is True and raw['integrity']=='ok' and value['diagnostic']['exit']==0,'diagnostic SQL read failed')
        expect(json.loads(bytes.fromhex(raw['view_raw_hex']))==raw['view'],'raw view mismatch')
        expect(json.loads(bytes.fromhex(raw['latest_raw_hex']))==raw['latest'],'raw latest-row mismatch')
        commits=[e for e in trace if e['sql']=='COMMIT'];rollbacks=[e for e in trace if e['sql']=='ROLLBACK']
        if name=='valid':
            expect(writer['ready'] and request['response']['outcome']=='commit','valid admission control failed')
            expect(raw['view']['content']==request['request']['value'] and raw['latest']['required']==value['candidate'],'valid committed data differs')
            expect(value['recovery_query']['response']['consumer_query']['required']==value['candidate'],'valid consumer recovery failed')
            return dict(status='SUPPORTED',observation='well-typed new content/evidence ACKed and recovered')
        if name=='conflict':
            need(request is not None and request['response'] is None and request.get('error'),'missing actual conflict no-ACK observation')
            expect(writer['ready'] and not commits and rollbacks and rollbacks[-1]['in_transaction'] is False,'conflict not rolled back before commitment')
            prior=value['seed']['call']['response']['consumer_query']
            expect(raw['latest']==dict(accepted_content=prior['accepted_content'],required=prior['required']),'conflict altered prior accepted record')
            expect(value['recovery_query']['response']['consumer_query']==prior,'conflict cold query differs from earlier ACK')
            return dict(status='SUPPORTED',observation='same-content conflicting evidence caused no ACK and actual ROLLBACK, prior accepted records retained')
        if phase=='baseline':
            need(writer['ready'] and request is not None and request['response'] is None and request.get('error'),'missing malformed-call/no-ACK evidence')
            expect(len(commits)==1 and commits[0]['in_transaction'] is False and not rollbacks,'malformed new content did not commit as predicted')
            expect(raw['view']['content']==request['request']['value'] and raw['latest']['required']==value['candidate'],'malformed accepted record not actually persisted')
            expect(value['recovered']['ready'] is True and value['recovery_query']['response'] is None,'baseline recovery/query did not expose validation timing')
            expect('incompatible accepted observation record' in writer['stderr'],'failure reason not identified')
            return dict(status='COUNTEREXAMPLE',observation='malformed required fields committed with content before query rejection; startup ready but consumer unavailable')
        need(request is None,'request must not be invented after startup refusal')
        expect(writer['ready'] is False and writer['exit']!=0 and not commits and not rollbacks,'invalid config exposed ready or mutated data')
        prior=value['bootstrap']['calls'][-1]['response']['consumer_query']
        expect(raw['view']['content']==prior['accepted_content'] and raw['latest']['required']==prior['required'],'rejected config changed earlier accepted pair')
        expect(value['recovered']['ready'] and value['recovery_query']['response']['consumer_query']==prior,'earlier valid consumer records not recovered')
        return dict(status='SUPPORTED',observation='invalid required config refused before ready/no RPC; earlier accepted pair retained')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    data=json.loads(Path(sys.argv[1]).read_bytes());phase=data['phase']
    result={k:case(v,phase) for k,v in data['cases'].items()}
    assert all(v['status']==('COUNTEREXAMPLE' if phase=='baseline' and k in ('missing','type') else 'SUPPORTED') for k,v in result.items()),result
    artifact=data['retained_invalid_artifact'];need(artifact['before_sha256']==artifact['after_sha256'],'invalid artifact changed')
    if phase=='baseline':
        assert artifact['process']['ready'] is True and artifact['query']['response'] is None
        artifact_result='ready then consumer query failed on retained malformed database'
    else:
        assert artifact['process']['ready'] is False and artifact['process']['exit']!=0 and artifact['query'] is None
        artifact_result='retained actual malformed database refused before ready, unchanged digest'
    example=data['cases']['missing'];no_ready=copy.deepcopy(example);del no_ready['writer']['ready']
    no_raw=copy.deepcopy(example);del no_raw['diagnostic']['observation']['latest_raw_hex']
    incomplete=dict(missing_startup_observation=case(no_ready,phase),missing_diagnostic_bytes=case(no_raw,phase))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=[]
    for value in data['cases'].values():
        children.append(value['bootstrap']['process'])
        if value['seed']:children.append(value['seed']['process'])
        children += [value['writer'],value['recovered'],value['diagnostic']]
    children.append(artifact['process']);children.sort(key=lambda c:c['start_ns'])
    assert len(children)==len({c['pid'] for c in children})==18
    assert all(c['exit'] in (-9,0,1) for c in children) and all(a['exit_ns']<b['start_ns'] for a,b in zip(children,children[1:]))
    print(json.dumps(dict(phase=phase,cases=result,retained_invalid_artifact=artifact_result,incomplete_controls=incomplete,
                          owned_children=len(children),maximum_observed_child_concurrency=1,
                          qualification='negative input controls outside completed well-typed premise; field presence/types, not source truth/authentication or full C9/C11'),indent=2,sort_keys=True))
if __name__=='__main__':main()
