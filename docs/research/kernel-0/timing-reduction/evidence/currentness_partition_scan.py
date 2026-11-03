#!/usr/bin/env python3
"""Exhaust two chains' interleavings and independently search serial witnesses."""
import argparse
from dataclasses import asdict
from itertools import permutations
from pathlib import Path
import json, resource, sys, time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import timing_event_model as t
m=t.model; p=t.PROFILES[0]
initial=m.established((0,7),p=p)
q={'write':m.Request('set',evidence=0,target=0,value=1),
   'revoke':m.Request('restrict',target=0,value=0)}
assert all(v in t.CATALOG for v in q.values())
events=('read','prepare','revoke_prepare','revoke_commit','monitor','write_resolve')
constraints=(('read','prepare'),('prepare','write_resolve'),('revoke_prepare','revoke_commit'),
             ('revoke_commit','monitor'),('monitor','write_resolve'))


def schedules():
    return [order for order in permutations(events) if all(order.index(a)<order.index(b) for a,b in constraints)]


def serial(outcomes,final,monitor):
    witnesses=[]; checked=0
    for order in permutations(('write','revoke','monitor')):
        if order.index('revoke')>order.index('monitor'): continue
        checked+=1; state=initial; seen={}; observed=None
        for event in order:
            if event=='monitor': observed=state
            else: state,seen[event]=m.resolve(state,q[event],p)
        if seen==outcomes and state==final and observed==monitor: witnesses.append(list(order))
    return {'orders_checked':checked,'witnesses':witnesses}


def run_one(mode,order):
    state=initial; snapshot=None; proposed=None; result=None; observed=None; outcomes={}
    cuts=[{'event':'start','state':asdict(state)}]
    for event in order:
        if event=='read': snapshot=state
        elif event=='prepare': proposed,result=m.resolve(snapshot,q['write'],p)
        elif event=='revoke_commit': state,outcomes['revoke']=m.resolve(state,q['revoke'],p)
        elif event=='monitor': observed=state
        elif event=='write_resolve':
            if mode=='current': state,outcomes['write']=m.resolve(state,q['write'],p)
            elif result=='commit':
                state=m.merge_effect(state,snapshot,proposed); outcomes['write']=result
            else: outcomes['write']=result
        cuts.append({'event':event,'state':asdict(state)})
    return {'partition':'read_before_revoke' if order.index('read')<order.index('revoke_commit') else 'read_after_revoke',
            'schedule':list(order),'outcomes':outcomes,'monitor':asdict(observed),'final':asdict(state),
            'serial':serial(outcomes,state,observed),'cuts':cuts}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--state-cap',type=int,default=1000); ap.add_argument('--schedule-cap',type=int,default=20)
    a=ap.parse_args()
    if not 1<=a.state_cap<=1000 or not 1<=a.schedule_cap<=20: ap.error('bounds: states 1..1000, schedules 1..20')
    started=time.monotonic(); orders=schedules(); assert len(orders)==10
    total_states=0; results=[]
    for mode in ('current','stale'):
        for i,order in enumerate(orders):
            if len(results)>=a.schedule_cap or total_states+7>a.state_cap:
                print(json.dumps({'status':'incomplete','states_counted':total_states,'schedules_completed':len(results),
                    'next':{'mode':mode,'partition_index':i,'schedule':order},
                    'reason':'schedule_cap' if len(results)>=a.schedule_cap else 'state_cap'},sort_keys=True)); return 2
            row=run_one(mode,order); row['mode']=mode; results.append(row); total_states+=len(row['cuts'])
    for row in results:
        has=bool(row['serial']['witnesses'])
        assert has == (row['mode']=='current' or row['partition']=='read_after_revoke')
    counts={}
    for row in results:
        k=row['mode']+'/'+row['partition']; c=counts.setdefault(k,{'schedules':0,'witnessed':0,'unwitnessed':0})
        c['schedules']+=1; c['witnessed' if row['serial']['witnesses'] else 'unwitnessed']+=1
    print(json.dumps({'status':'complete_bounded_partition','schedule_cap':a.schedule_cap,'state_cap':a.state_cap,
        'valid_schedules_per_mode':len(orders),'schedule_runs':len(results),'state_cuts_counted':total_states,
        'event_steps':len(results)*len(events),'serial_orders_checked':sum(x['serial']['orders_checked'] for x in results),
        'counts':counts,'results':results,'elapsed_seconds':time.monotonic()-started,
        'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'scope':'two fixed event chains; abstract whole commitment, no torn field reads'},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
