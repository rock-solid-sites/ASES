#!/usr/bin/env python3
"""Required older evidence distinguishability, separate from atomic latest pairing."""
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
def one(case):
    try:
        accept=case['accept'];writer=case['writer'];gate=case['gate'];recovered=case['recovered']
        need(accept['response'] is None and accept.get('error'),'missing no-ACK observation')
        need(gate['stage']=='durable' and gate['raw_hex']=='47' and gate['pid']==writer['pid'],'inherited durable gate not observed')
        expect(accept['start_ns']<gate['observed_ns']<writer['exit_ns']<recovered['start_ns'],'call/gate/death/recovery order')
        expect('observations' not in recovered['config'],'original observations passed to recovery')
        old=case['required_earlier'];new=case['required_later']
        expect(old['consumer_evidence']!=new['consumer_evidence'],'older evidence did not vary independently')
        expect(all(old[k]==new[k] for k in ('identity_genesis','created_by','project')),'selected stable identity fields changed')
        before=case['bootstrap']['calls'][-1]['response']
        expect(before['consumer_query']['required']==old and before['outcome']=='commit','earlier tuple was not actually ACKed')
        query=case['recovered_query']['response']['consumer_query'];records=query['retained_records']
        raw=case['independent_reader']['observation']
        expect(case['independent_reader']['exit']==0 and raw['integrity']=='ok' and raw['query']==query,'fresh independent read disagreement')
        expect(raw['view']==case['recovered_query']['response']['state'],'fresh protected view mismatch')
        expect(query['status']=='available' and query['required']==new and query['accepted_content']==accept['request']['value'],
               'latest tuple/content coupling failed')
        expect(json.loads(bytes.fromhex(raw['view_utf8_hex']))==raw['view'],'raw protected-view mismatch')
        latest=json.loads(bytes.fromhex(raw['observation_utf8_hex']))
        expect(latest==dict(accepted_content=query['accepted_content'],required=new),'raw latest record mismatch')
        expect(len({r['accepted_content'] for r in records})==len(records),'retained record identity ambiguous')
        by={r['accepted_content']:r['required'] for r in records}
        expect(by.get(query['accepted_content'])==new,'later required evidence unavailable')
        trace=case['writer_trace'];commits=[s for s in trace if s['sql']=='COMMIT'];inserts=[s for s in trace if s['sql']=='INSERT']
        expect(len(commits)==1 and commits[0]['in_transaction'] is False,'actual single COMMIT not observed')
        expect(all(s['in_transaction'] is True and s['end_ns']<commits[0]['start_ns'] for s in inserts),'observation write outside content transaction')
        if case['profile']=='archive':
            expect(len(inserts)==2,'archive and latest records not both written in content transaction')
            expect([json.loads(bytes.fromhex(raw)) for raw in query['archive_rows_raw_hex']]==records,'raw archived rows not recovered')
            expect(len(records)==2 and by.get(before['state']['content'])==old,'earlier accepted required observations lost')
            return dict(status='SUPPORTED',observation='both older and later evidence retained with selected stable identity fields')
        expect(len(inserts)==1 and query['archive_rows_raw_hex']==[],'latest-only control unexpectedly archived')
        expect(len(records)==1 and before['state']['content'] not in by,'latest-only control did not discriminate')
        return dict(status='COUNTEREXAMPLE',observation='atomic latest tuple correct, earlier independently required evidence unavailable')
    except Incomplete as e:return dict(status='INCOMPLETE',reason=str(e))
    except Violation as e:return dict(status='VIOLATION',reason=str(e))
    except (KeyError,TypeError,ValueError,IndexError) as e:return dict(status='INCOMPLETE',reason=str(e))

def main():
    data=json.loads(Path(sys.argv[1]).read_bytes());results={k:one(v) for k,v in data['cases'].items()}
    assert all(v['status']==('SUPPORTED' if k.startswith('archive') else 'COUNTEREXAMPLE') for k,v in results.items()),results
    a,b=data['cases']['latest-A'],data['cases']['latest-B']
    assert a['required_earlier']!=b['required_earlier'] and a['required_later']==b['required_later']
    assert a['independent_reader']['observation']['query']==b['independent_reader']['observation']['query']
    assert a['independent_reader']['observation']['view_utf8_hex']==b['independent_reader']['observation']['view_utf8_hex']
    assert a['independent_reader']['observation']['observation_utf8_hex']==b['independent_reader']['observation']['observation_utf8_hex']
    assert data['cases']['archive-A']['independent_reader']['observation']['query']!=data['cases']['archive-B']['independent_reader']['observation']['query']
    example=data['cases']['archive-A'];no_records=copy.deepcopy(example);del no_records['recovered_query']['response']['consumer_query']['retained_records']
    no_ack=copy.deepcopy(example);del no_ack['accept']['response']
    incomplete=dict(missing_record_observation=one(no_records),missing_reply_observation=one(no_ack))
    assert all(v['status']=='INCOMPLETE' for v in incomplete.values()),incomplete
    children=[c[k] if k!='bootstrap' else c[k]['process'] for c in data['cases'].values() for k in ('bootstrap','writer','recovered','independent_reader')]
    children.sort(key=lambda c:c['start_ns'])
    assert len(children)==len({c['pid'] for c in children})==16
    assert all(c['exit'] in (-9,0) for c in children) and all(a['exit_ns']<b['start_ns'] for a,b in zip(children,children[1:]))
    base=Path(__file__).resolve().parent.parents[1]
    for path,digest in data['source_hashes'].items():assert hashlib.sha256((base/path).read_bytes()).hexdigest()==digest
    print(json.dumps(dict(cases=results,latest_histories_collapse_in_logical_consumer_view=True,archive_histories_distinguished=True,
                          incomplete_controls=incomplete,owned_children=len(children),maximum_observed_child_concurrency=1,
                          qualification='selected trusted required-history profile, no all-physical-byte indistinguishability or authenticity/minimal schema/full C11 proof'),indent=2,sort_keys=True))
if __name__=='__main__':main()
