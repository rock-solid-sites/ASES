#!/usr/bin/env python3
import copy,hashlib,json,subprocess,sys
from pathlib import Path
class Incomplete(Exception):pass
class Violation(Exception):pass
def need(v,msg):
    if not v:raise Incomplete(msg)
def expect(v,msg):
    if not v:raise Violation(msg)
def check(c,phase):
    try:
        before=c['before']['response'];attempt=c['attempt'];trace=c['trace'];raw=c['diagnostic']['observation']
        need(before['outcome']=='read' and before['consumer_query']['status']=='available','missing legitimate pre-read evidence')
        expect(c['writer']['ready'] is True and raw['diagnostic_only'] and raw['integrity']=='ok','initial readiness/diagnostic failed')
        expect(('observations' in c['writer']['config'])==c['explicit_input'],'input availability not actually controlled')
        commits=[t for t in trace if t['sql']=='COMMIT'];updates=[t for t in trace if t['sql']=='UPDATE']
        if c['explicit_input']:
            expect(attempt['response']['outcome']=='commit' and len(commits)==1,'explicit-input positive did not commit/ACK')
            expect(c['recovery_query']['response']['consumer_query']['accepted_content']==attempt['request']['value'],'explicit positive not recovered')
            return dict(status='SUPPORTED',observation='explicit required tuple accepts new content and recovers')
        if phase=='baseline':
            need(attempt['response'] is None and attempt.get('error'),'missing actual no-response observation')
            expect(len(commits)==len(updates)==1 and commits[0]['in_transaction'] is False,'unknown new tuple did not permit actual content COMMIT')
            expect(raw['view']['content']==attempt['request']['value'] and raw['latest']['accepted_content']==before['state']['content'],'cross-record binding not incompatible')
            expect(c['recovered']['ready'] is False and c['recovery_query'] is None,'poisoned next startup did not refuse')
            return dict(status='COUNTEREXAMPLE',observation='valid recovered read did not provide new required tuple; new content nevertheless committed without usable ACK')
        expect(attempt['response']['outcome']=='deny' and not commits and not updates,'unavailable input did not deny before content write')
        expect(attempt['response']['state']==before['state'] and attempt['response']['consumer_query']==before['consumer_query'],'denial changed accepted data')
        expect(raw['view']==before['state'] and c['recovery_query']['response']['consumer_query']==before['consumer_query'],'earlier ACKed pair not retained')
        return dict(status='SUPPORTED',observation='read allowed, new content denied/ROLLBACK before write with tuple unavailable')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))
def main():
    d=json.loads(Path(sys.argv[1]).read_bytes());result={k:check(c,d['phase']) for k,c in d['cases'].items()}
    assert result['explicit']['status']=='SUPPORTED' and result['unavailable']['status']==('COUNTEREXAMPLE' if d['phase']=='baseline' else 'SUPPORTED'),result
    missing=copy.deepcopy(d['cases']['unavailable']);del missing['before']['response']
    incomplete=check(missing,d['phase']);assert incomplete['status']=='INCOMPLETE'
    children=[c[k] if k!='bootstrap' else c[k]['process'] for c in d['cases'].values() for k in ('bootstrap','writer','recovered','diagnostic')]
    children.sort(key=lambda c:c['start_ns']);assert len(children)==len({c['pid'] for c in children})==8
    assert all(c['exit'] in (-9,0,1) for c in children) and all(a['exit_ns']<b['start_ns'] for a,b in zip(children,children[1:]))
    for path,digest in d['source_hashes'].items():assert hashlib.sha256(subprocess.check_output(['git','show',d['execution_sha']+':docs/research/'+path])).hexdigest()==digest
    print(json.dumps(dict(phase=d['phase'],cases=result,incomplete_control=incomplete,owned_children=len(children),maximum_observed_child_concurrency=1,source_hashes_verified=True,
                          qualification='current retained evidence versus new acceptance input, selected profile only; no source truth/nonrollback/power-loss/full C11 proof'),indent=2,sort_keys=True))
if __name__=='__main__':main()
