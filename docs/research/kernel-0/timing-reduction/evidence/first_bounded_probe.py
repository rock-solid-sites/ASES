#!/usr/bin/env python3
"""Bounded one-field outcome sensitivity probe; not a global proof."""
import sys, time
from pathlib import Path
from dataclasses import replace
K=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(K)); sys.path.insert(0,str(K/'direct-rtl')); sys.path.insert(0,str(K/'timing-reduction'))
import kernel0_finite_model as m
import timing_event_model as te
start=time.monotonic(); states_by_profile={}
for p in te.PROFILES:
    states=[m.State(),m.established(p=p),m.established((0,7),p=p)]
    if not p.exclusive: states.append(m.established((0,7),(3,2),p=p))
    s=states[-1]
    for q in (m.Request('set',0,0,1),m.Request('accept',0,value=1)):
        s,out=m.resolve(s,q,p)
        if out=='commit': states.append(s)
    states_by_profile[p.name]=states
print('bounded probe: selected reachable seed states x complete 148-offer catalog; legal one-field perturbations; all three profiles',flush=True)
print('state counts:',{k:len(v) for k,v in states_by_profile.items()},flush=True)
checks=0; mismatches=[]; kind_counts={}
for p in te.PROFILES:
    for si,s in enumerate(states_by_profile[p.name]):
        for q in te.CATALOG:
            ref,refkind=m.resolve(s,q,p)
            touched=te.types(q)['reads']|te.types(q)['writes']
            for field in te.FIELDS:
                if field not in touched: continue
                alt=replace(s,**{field:te._other_value(getattr(s,field))})
                if not m.invariant(alt,p): continue
                _,kind=m.resolve(alt,q,p); checks+=1
                kind_counts[kind]=kind_counts.get(kind,0)+1
                if kind!=refkind and len(mismatches)<8:
                    mismatches.append({'profile':p.name,'seed':si,'offer':q.label(),'changed_field':field,'reference':refkind,'perturbed':kind})
print('legal one-field perturbation checks:',checks,'first mismatches:',mismatches,flush=True)
print('perturbed outcome counts:',kind_counts,flush=True)
print('elapsed_s:',round(time.monotonic()-start,3),flush=True)
