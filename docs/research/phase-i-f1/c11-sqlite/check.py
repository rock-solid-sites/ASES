#!/usr/bin/env python3
"""Actual C11 storage coupling, original tuples only in observer, never recovery."""
import copy
import hashlib
import json
from pathlib import Path
import sys

class Incomplete(Exception):pass
class Violation(Exception):pass
def need(v,msg):
    if not v:raise Incomplete(msg)
def expect(v,msg):
    if not v:raise Violation(msg)

def case(value):
    try:
        writer=value['writer'];recovered=value['recovered'];accept=value['accept'];stage=value['stage']
        need('response' in accept,'missing acceptance reply/no-reply observation')
        expect('observations' not in recovered['config'],'original observation tuple supplied to recovery')
        expect(writer['config']['observations']==value['declared_original_observations'],'original acceptance source mismatch')
        expect(all(c['response']['outcome']=='commit' for c in value['bootstrap']['calls']),'bootstrap failed')
        expect(writer['start_ns']<writer['ready_ns']<accept['start_ns']<writer['exit_ns']<recovered['start_ns'],
               'accept/process/recovery precedence')
        if stage:
            gate=value['gate']
            need(gate['pid']==writer['pid'] and gate['stage']==stage and gate['raw_hex']=='47','missing actual inherited gate evidence')
            expect(accept['start_ns']<gate['observed_ns']<writer['exit_ns'] and accept['response'] is None and accept.get('error'),
                   'cut/no-ACK observation wrong')
        else:expect(accept['response']['outcome']=='commit','uninterrupted accepted control failed')
        query=value['recovered_query']['response']['consumer_query']
        raw=value['independent_reader']['observation']
        expect(value['independent_reader']['exit']==0 and raw['pid']==value['independent_reader']['pid'] and raw['integrity']=='ok',
               'fresh independent SQLite read failed')
        expect(raw['query']==query and raw['view']==value['recovered_query']['response']['state'],'fresh query/state disagreement')
        view_bytes=bytes.fromhex(raw['view_utf8_hex'])
        expect(hashlib.sha256(view_bytes).hexdigest()==raw['view_sha256'],'view raw digest mismatch')
        expect(json.loads(view_bytes)==raw['view'],'raw view not represented')
        trace=value['writer_trace'];update=[e for e in trace if e['sql']=='UPDATE'];insert=[e for e in trace if e['sql']=='INSERT'];commits=[e for e in trace if e['sql']=='COMMIT']
        expect(len(update)==1 and update[0]['in_transaction'] is True,'actual protected-content UPDATE missing')
        if stage=='prepared':
            expect(not commits and len(insert)==1 and insert[0]['in_transaction'] is True,'prepared transaction evidence')
            prior=value['bootstrap']['calls'][-1]['response']
            expect(query==prior['consumer_query'] and raw['view']==prior['state'],'pre-COMMIT prior ACKed pair changed')
            expect(raw['observation_utf8_hex'] is not None,'prior accepted observations disappeared')
            return dict(status='SUPPORTED',observation='pre-COMMIT prior ACKed content and observation pair retained')
        expect(commits and commits[0]['in_transaction'] is False and raw['view']['content']==query['accepted_content']==accept['request']['value'],
               'actual locally committed protected content not recovered')
        if value['mode']=='split' and stage=='durable':
            expect(not insert and len(commits)==1,'split gap already wrote observations')
            expect(query['status']=='incompatible_required_observations' and query['required'] is None and raw['observation_utf8_hex'] is not None,
                   'split gap did not expose metadata loss')
            prior=value['bootstrap']['calls'][-1]['response']['consumer_query']
            stored=json.loads(bytes.fromhex(raw['observation_utf8_hex']))
            expect(stored=={'accepted_content':prior['accepted_content'],'required':prior['required']},'split gap does not retain exact prior observations')
            return dict(status='COUNTEREXAMPLE',observation='new content COMMIT survived with incompatible prior evidence; new required observations missing, no ACK')
        expect(query['status']=='available' and query['required']==value['declared_original_observations'],'required accepted observations not retained')
        record=bytes.fromhex(raw['observation_utf8_hex'])
        expect(hashlib.sha256(record).hexdigest()==raw['observation_sha256'],'accepted observation raw digest')
        expect(json.loads(record)=={'accepted_content':accept['request']['value'],'required':value['declared_original_observations']},'raw accepted bundle differs')
        expect(len(insert)==1 and insert[0]['in_transaction'] is True,'accepted observation insert missing')
        if value['mode']=='atomic':expect(insert[0]['end_ns']<commits[0]['start_ns'] and len(commits)==1,'observations not in original transaction')
        else:expect(commits[0]['end_ns']<insert[0]['start_ns']<commits[1]['start_ns'],'separate-commit positive order')
        return dict(status='SUPPORTED',observation='exact accepted observation bytes recovered without original tuple input')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    data=json.loads(Path(sys.argv[1]).read_bytes());results={k:case(v) for k,v in data['cases'].items()}
    assert results['split-gap']['status']=='COUNTEREXAMPLE',results
    assert all(v['status']=='SUPPORTED' for k,v in results.items() if k!='split-gap'),results
    a,b=data['cases']['atomic-A'],data['cases']['atomic-B']
    assert a['independent_reader']['observation']['view_utf8_hex']==b['independent_reader']['observation']['view_utf8_hex']
    assert a['recovered_query']['response']['consumer_query']['required']!=b['recovered_query']['response']['consumer_query']['required']
    missing_accept=copy.deepcopy(a);del missing_accept['accept']['response']
    missing_query=copy.deepcopy(a);del missing_query['recovered_query']['response']['consumer_query']
    incomplete=dict(missing_accept=case(missing_accept),missing_recovered_observations=case(missing_query))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=[c[k] if k!='bootstrap' else c[k]['process'] for c in data['cases'].values() for k in ('bootstrap','writer','recovered','independent_reader')]
    children.sort(key=lambda c:c['start_ns'])
    assert len(children)==len({c['pid'] for c in children})==20
    assert all(c['exit'] in (-9,0) for c in children) and all(a['exit_ns']<b['start_ns'] for a,b in zip(children,children[1:]))
    base=Path(__file__).resolve().parent.parents[1]
    for path,digest in data['source_hashes'].items():assert hashlib.sha256((base/path).read_bytes()).hexdigest()==digest
    print(json.dumps(dict(cases=results,distinct_observation_worlds_same_core_view=True,incomplete_controls=incomplete,
                          owned_children=len(children),maximum_observed_child_concurrency=1,
                          qualification='trusted accepted opaque observations, actual SQLite process loss; no authenticity/schema/minimality/general C11 closure'),indent=2,sort_keys=True))
if __name__=='__main__':main()
