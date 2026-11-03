#!/usr/bin/env python3
"""Bounded interleavings of one two-field publication and one read."""
import argparse, itertools, json, resource, time
PRE=(0,1); POST=(1,0)

def cases():
    for mode in ('whole','split'):
        for pub in ((0,1),(1,0)):
            for read in ((0,1),(1,0)):
                events=(f'p{pub[0]}',f'p{pub[1]}',f'r{read[0]}',f'r{read[1]}')
                for order in itertools.permutations(events):
                    if order.index(events[0])<order.index(events[1]) and order.index(events[2])<order.index(events[3]):
                        yield mode,pub,read,order

def run(mode,pub,read,order):
    visible=list(PRE); captured=[None,None]; trace=[{'event':'start','visible':list(visible)}]
    commit_event=f'p{pub[0] if mode=="whole" else pub[1]}'
    for event in order:
        i=int(event[1])
        if event[0]=='p':
            if mode=='split': visible[i]=POST[i]
            elif event==commit_event: visible[:]=POST
        else: captured[i]=visible[i]
        trace.append({'event':event,'visible':visible.copy(),'captured':captured.copy()})
    # Enumerate abstract state at each cut from immediately before first read
    # through immediately after second read; commit changes the whole state.
    first=order.index(f'r{read[0]}'); last=order.index(f'r{read[1]}')
    commit=order.index(commit_event)
    cuts=[{'after_events':k,'state':list(POST if commit<k else PRE)} for k in range(first,last+2)]
    matches=[cut for cut in cuts if cut['state']==captured]
    return {'mode':mode,'publication_order':pub,'read_order':read,'schedule':order,'commit_event':commit_event,
            'observed':captured,'eligible_cuts':cuts,'coherent':bool(matches),'trace':trace}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--state-cap',type=int,default=250); ap.add_argument('--schedule-cap',type=int,default=48); a=ap.parse_args()
    if not 1<=a.state_cap<=250 or not 1<=a.schedule_cap<=48: ap.error('bounds states 1..250, schedules 1..48')
    start=time.monotonic(); rows=[]; cuts=0
    for index,(mode,pub,read,order) in enumerate(cases()):
        if len(rows)>=a.schedule_cap or cuts+5>a.state_cap:
            print(json.dumps({'status':'incomplete','schedules_completed':len(rows),'state_cuts_counted':cuts,
              'reason':'schedule_cap' if len(rows)>=a.schedule_cap else 'state_cap',
              'next':{'index':index,'mode':mode,'publication_order':pub,'read_order':read,'schedule':order}},sort_keys=True)); return 2
        rows.append(run(mode,pub,read,order)); cuts+=5
    assert len(rows)==48
    assert any(not r['coherent'] for r in rows if r['mode']=='split') and any(r['coherent'] for r in rows if r['mode']=='split')
    counts={}
    for r in rows:
        key=f"{r['mode']}/p{''.join(map(str,r['publication_order']))}/r{''.join(map(str,r['read_order']))}/tuple{''.join(map(str,r['observed']))}/{'coherent' if r['coherent'] else 'incoherent'}"
        counts[key]=counts.get(key,0)+1
    print(json.dumps({'status':'complete_bounded','schedules':len(rows),'state_cuts_counted':cuts,'event_steps':len(rows)*4,
      'counts':counts,'results':rows,'elapsed_seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
