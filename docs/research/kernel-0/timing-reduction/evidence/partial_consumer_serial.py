#!/usr/bin/env python3
"""Two-operation logical serial witness against a partial-publication mutant."""
import argparse
from collections import deque
from dataclasses import asdict, replace
from itertools import permutations
from pathlib import Path
import json, resource, sys, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import timing_event_model as t
m=t.model
p=t.PROFILES[1]
base=m.established((0,7), p=p)
base=replace(base, data=(0,1))
assert m.invariant(base,p)
requests={'pair':m.Request('pair', evidence=0, value=1),
          'consumer':m.Request('set', evidence=0, target=1, value=1)}
assert all(q in t.CATALOG for q in requests.values())
candidate, pair_kind=m.resolve(base,requests['pair'],p)
assert pair_kind=='commit' and candidate.data==(1,0)


def serial_histories():
    """Independent replay from initial state; no graph/mutation state used."""
    result=[]
    for order in permutations(requests):
        state=base; outcomes={}
        for name in order:
            state, kind=m.resolve(state,requests[name],p)
            outcomes[name]=kind
        result.append({'order':list(order),'outcomes':outcomes,'final':asdict(state)})
    return result


def steps(mode):
    if mode=='control_consumer_first': return ('private_candidate','consumer','pair')
    if mode=='control_pair_first': return ('private_candidate','pair','consumer')
    return ('partial_y','consumer','remaining_x')


def step(mode, node):
    index,state,outcomes=node
    actions=steps(mode)
    if index==len(actions): return None
    action=actions[index]; outs=dict(outcomes)
    if action in requests:
        state,kind=m.resolve(state,requests[action],p)
        outs[action]=kind
    elif action=='private_candidate':
        assert state==base and candidate.data==(1,0)
        # Candidate exists separately; authoritative state remains unchanged.
    elif action=='partial_y':
        assert state==base
        state=replace(state,data=(state.data[0],candidate.data[1]))
        assert state.data==(0,0) and m.invariant(state,p)
    else:
        state=replace(state,data=(candidate.data[0],state.data[1]))
        outs['pair']=pair_kind
    return ((index+1,state,tuple(sorted(outs.items()))),action)


def explore(mode, budget):
    if budget<1: return {'status':'incomplete','states':0,'edges':0,'next':'root'}
    root=(0,base,()); seen={root}; queue=deque([root]); edges=[]; cuts=[]
    while queue:
        node=queue.popleft(); i,s,outcomes=node
        cuts.append({'stage':i,'state':asdict(s),'outcomes':dict(outcomes)})
        edge=step(mode,node)
        if edge is None: continue
        nxt,action=edge
        if nxt not in seen and len(seen)>=budget:
            return {'status':'incomplete','states':len(seen),'edges':len(edges),
                    'cuts_processed':len(cuts),'rejected_action':action,'current_stage':i}
        edges.append({'action':action,'from_stage':i,'to_stage':nxt[0]})
        if nxt not in seen: seen.add(nxt); queue.append(nxt)
    final=cuts[-1]; candidates=serial_histories()
    matches=[x for x in candidates if x['outcomes']==final['outcomes'] and x['final']==final['state']]
    return {'status':'complete','states':len(seen),'edges':len(edges),'cuts':cuts,
            'edge_trace':edges,'observed_operation_outcomes':len(final['outcomes']),
            'serial_witnesses':[x['order'] for x in matches], 'serial_candidates':candidates,
            'final_invariant':m.invariant(s,p)}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--state-cap',type=int,default=1000)
    args=ap.parse_args()
    if not 1<=args.state_cap<=1000: ap.error('state cap must be in 1..1000')
    started=time.monotonic(); used=0; graphs={}
    for mode in ('control_consumer_first','control_pair_first','unsafe_partial_and_blind_write'):
        g=explore(mode,args.state_cap-used); graphs[mode]=g; used+=g['states']
        if g['status']!='complete':
            print(json.dumps({'status':'incomplete','state_cap':args.state_cap,'states_discovered':used,
                              'stopped_graph':mode,'graphs':graphs},sort_keys=True)); return 2
    assert graphs['control_consumer_first']['serial_witnesses']==[['consumer','pair']]
    assert graphs['control_pair_first']['serial_witnesses']==[['pair','consumer']]
    bad=graphs['unsafe_partial_and_blind_write']
    assert not bad['serial_witnesses'] and bad['final_invariant'] is False
    print(json.dumps({'status':'complete_bounded_fixture','state_cap':args.state_cap,
        'states_discovered':used,'edges':sum(g['edges'] for g in graphs.values()),
        'cuts':sum(len(g['cuts']) for g in graphs.values()),
        'operation_outcomes':sum(g['observed_operation_outcomes'] for g in graphs.values()),
        'serial_permutations_per_graph':len(serial_histories()),'graphs':graphs,
        'elapsed_seconds':time.monotonic()-started,
        'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'scope':'partial visibility plus blind remaining publication; not partial visibility alone'},sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
