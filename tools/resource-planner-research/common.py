"""Research-only scheduling model shared by independent solver experiments.
No credentials, provider network calls, state mutations, or resource launches.
"""
from __future__ import annotations
import json
from pathlib import Path

class ModelError(ValueError): pass


def load(path):
    obj = json.loads(Path(path).read_text())
    if type(obj) is not dict or obj.get('version') != 1: raise ModelError('version')
    if type(obj.get('domain')) is not str or not obj['domain']: raise ModelError('domain')
    rs = obj.get('resources'); ss = obj.get('stages')
    if type(rs) is not list or type(ss) is not list or not rs or not ss: raise ModelError('resources/stages')
    ids=set(); resources={}
    for r in rs:
        if type(r) is not dict or type(r.get('id')) is not str or not r['id'] or r['id'] in ids:raise ModelError('resource id')
        ids.add(r['id'])
        if type(r.get('account')) is not str or type(r.get('domain')) is not str:raise ModelError('account/domain')
        if r.get('availability') not in ('verified','retired','candidate'):raise ModelError('availability')
        if type(r.get('ramGiB')) not in (int,) or r['ramGiB'] <1:raise ModelError('ram')
        if type(r.get('quotaMinutes')) not in (int,) or r['quotaMinutes'] < 0:raise ModelError('quota')
        resources[r['id']]=r
    jobs={}; names=set()
    for st in ss:
        if type(st) is not dict or type(st.get('id')) is not str or not st['id'] or st['id'] in names:raise ModelError('stage id')
        names.add(st['id']); modes=st.get('modes'); after=st.get('after',[])
        if type(modes) is not list or not modes or type(after) is not list or any(type(x) is not str for x in after):raise ModelError('modes/after')
        if type(st.get('minRamGiB',1)) is not int or st.get('minRamGiB',1)<1:raise ModelError('minRam')
        if type(st.get('transferMinutesIfMoved',0)) is not int or st.get('transferMinutesIfMoved',0)<0:raise ModelError('transfer')
        indep=st.get('independentFrom',[])
        if type(indep) is not list or any(type(x) is not str for x in indep):raise ModelError('independence')
        eligible=[]
        for mode in modes:
            if type(mode) is not dict or type(mode.get('resource')) is not str:raise ModelError('mode resource')
            if type(mode.get('duration')) is not int or mode['duration'] <1:raise ModelError('duration')
            if type(mode.get('costCents',0)) is not int or mode.get('costCents',0)<0:raise ModelError('price')
            r=resources.get(mode['resource'])
            if r and r['domain']==obj['domain'] and r['availability']=='verified' and r['ramGiB']>=st.get('minRamGiB',1):eligible.append(mode)
        jobs[st['id']]={**st,'modes':eligible}
    for st in ss:
        if any(p not in jobs or p == st['id'] for p in st.get('after',[])) or any(p not in jobs or p==st['id'] for p in st.get('independentFrom',[])):raise ModelError('unknown reference')
    seen=set(); in_stack=set()
    def visit(x):
        if x in in_stack:raise ModelError('dependency cycle')
        if x in seen:return
        in_stack.add(x)
        for p in jobs[x].get('after',[]):visit(p)
        in_stack.remove(x);seen.add(x)
    for x in jobs:visit(x)
    budget=obj.get('budgetCents',10**9)
    if type(budget) is not int or budget<0: raise ModelError('budget')
    return {'name':obj.get('name',Path(path).stem), 'domain':obj['domain'], 'resources':resources, 'stages':jobs, 'budgetCents':budget}


def check_plan(m, plans):
    """Independent verifier; never trusts solver's feasibility assertion."""
    jobs=m['stages']; resources=m['resources']
    if set(plans)!=set(jobs):return False,'missing stage'
    chosen={};total=0
    for name,(rid,start,end,mode_index) in plans.items():
        st=jobs[name]
        if type(start) is not int or type(end) is not int or start<0:return False,'invalid time'
        if type(mode_index) is not int or mode_index<0 or mode_index>=len(st['modes']):return False,'invalid mode'
        mo=st['modes'][mode_index]
        if rid!=mo['resource'] or end !=start+mo['duration']:return False,'invalid mode duration'
        total+=mo.get('costCents',0);chosen[name]=mo
    if total>m['budgetCents']:return False,'budget'
    for name,(rid,start,end,k) in plans.items():
        st=jobs[name]
        for pred in st.get('after',[]):
            pr,pstart,pend,pk=plans[pred]
            lag=st.get('transferMinutesIfMoved',0) if rid!=pr else 0
            if start<pend+lag:return False,'precedence transfer'
        for other in st.get('independentFrom',[]):
            if rid==plans[other][0]:return False,'independence'
        for other,(orid,os,oe,_) in plans.items():
            if other!=name and rid==orid and start<oe and os<end:return False,'overlap'
    for rid,r in resources.items():
        spent=sum(jobs[name]['modes'][plans[name][3]]['duration'] for name in plans if plans[name][0]==rid)
        if spent>r['quotaMinutes']:return False,'quota'
    return True,'ok'


def report(m, backend, plans, elapsed_ms, status, guarantee, extra=None):
    ans={'fixture':m['name'], 'backend':backend,'status':status,'guarantee':guarantee,'wallMs':round(elapsed_ms,3)}
    if plans is not None:
        feasible,reason=check_plan(m,plans)
        if not feasible:raise AssertionError(f'INDEPENDENT VERIFIER REJECTED {backend}: {reason}')
        ans['makespan']=max(v[2] for v in plans.values())
        ans['costCents']=sum(m['stages'][id]['modes'][v[3]].get('costCents',0) for id,v in plans.items())
        ans['placements']={id:{'resource':v[0],'start':v[1],'end':v[2],'modeIndex':v[3]} for id,v in plans.items()}
    if extra:ans.update(extra)
    return ans
