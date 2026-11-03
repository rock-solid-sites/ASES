#!/usr/bin/env python3
"""Partial-view continuation controls with operation-only and read-aware witnesses."""
import argparse
from collections import deque
from dataclasses import asdict, replace
from itertools import permutations
from pathlib import Path
import json, resource, sys, time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import timing_event_model as t
m=t.model; p=t.PROFILES[1]
base=replace(m.established((0,7),p=p),data=(0,1))
q={'pair':m.Request('pair',evidence=0,value=1), 'consumer':m.Request('set',evidence=0,target=1,value=1)}
assert m.invariant(base,p) and all(x in t.CATALOG for x in q.values())
candidate,kind=m.resolve(base,q['pair'],p)
assert kind=='commit' and candidate.data==(1,0)
partial=replace(base,data=(0,0)); assert m.invariant(partial,p)


def serial_check(outcomes, final, include_read):
    """Replay all allowed completed-op/read orders from the untouched oracle state."""
    events=list(outcomes)
    if include_read: events.append('read')
    histories=[]; checked=0
    for seq in permutations(events):
        if include_read and seq.index('read')>seq.index('consumer'): continue
        checked+=1; state=base; observed={}; read=None
        for name in seq:
            if name=='read': read=state
            else: state,observed[name]=m.resolve(state,q[name],p)
        if observed==outcomes and state==final and (not include_read or read==partial):
            histories.append(list(seq))
    return {'candidate_orders_checked':checked,'witnesses':histories}


def step(mode,node):
    stage,state,packed=node; outcomes=dict(packed)
    if stage==0: return (1,partial,packed),'expose_partial'
    if stage==1:
        state,result=m.resolve(state,q['consumer'],p); outcomes['consumer']=result
        return (2,state,tuple(sorted(outcomes.items()))),'consumer'
    if stage==2:
        if mode=='blind':
            state=replace(state,data=(candidate.data[0],state.data[1])); outcomes['pair']='commit'
        elif mode=='revalidate':
            state,result=m.resolve(state,q['pair'],p); outcomes['pair']=result
        return (3,state,tuple(sorted(outcomes.items()))),mode
    return None


def explore(mode,budget):
    if budget<1: return {'status':'incomplete','states':0,'edges':0,'next':'root'}
    root=(0,base,()); seen={root}; work=deque([root]); cuts=[]; edges=[]
    while work:
        node=work.popleft(); stage,state,packed=node
        cuts.append({'stage':stage,'state':asdict(state),'outcomes':dict(packed)})
        edge=step(mode,node)
        if edge is None: continue
        nxt,action=edge
        if nxt not in seen and len(seen)>=budget:
            return {'status':'incomplete','states':len(seen),'edges':len(edges),'cuts_processed':len(cuts),
                    'current_stage':stage,'rejected_action':action}
        edges.append({'from':stage,'to':nxt[0],'action':action})
        if nxt not in seen: seen.add(nxt); work.append(nxt)
    outcomes=dict(node[2]); final=node[1]
    return {'status':'complete','states':len(seen),'edges':len(edges),'cuts':cuts,'edge_trace':edges,
            'pair_pending':'pair' not in outcomes,'operation_only':serial_check(outcomes,final,False),
            'with_authoritative_read':serial_check(outcomes,final,True),
            'final_invariant':m.invariant(final,p)}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--state-cap',type=int,default=1000); a=ap.parse_args()
    if not 1<=a.state_cap<=1000: ap.error('state cap must be in 1..1000')
    started=time.monotonic(); used=0; graphs={}
    for mode in ('blind','revalidate','withhold'):
        g=explore(mode,a.state_cap-used); graphs[mode]=g; used+=g['states']
        if g['status']!='complete':
            print(json.dumps({'status':'incomplete','state_cap':a.state_cap,'states_discovered':used,
                              'stopped_graph':mode,'graphs':graphs},sort_keys=True)); return 2
    assert not graphs['blind']['operation_only']['witnesses']
    assert graphs['revalidate']['operation_only']['witnesses']==[['consumer','pair']]
    assert graphs['withhold']['operation_only']['witnesses']==[['consumer']]
    assert all(not x['with_authoritative_read']['witnesses'] for x in graphs.values())
    print(json.dumps({'status':'complete_bounded_fixture','state_cap':a.state_cap,'states_discovered':used,
        'edges':sum(g['edges'] for g in graphs.values()),'cuts':sum(len(g['cuts']) for g in graphs.values()),
        'total_serial_orders':sum(g[k]['candidate_orders_checked'] for g in graphs.values() for k in ('operation_only','with_authoritative_read')),
        'graphs':graphs,'elapsed_seconds':time.monotonic()-started,
        'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'scope':'fixed operations and explicit read; no universal protocol claim'},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
