"""Exact reference MILP for synthetic TripN subsets. Optional SciPy dependency.
Run: python research/resource-solver/exact_tripn_subsets.py
HiGHS is a C++ reference solver, NOT a proposed production ASES dependency.
Only status==0 with zero gap constitutes a proven optimum.
"""
import json,pathlib,time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix
ROOT=pathlib.Path(__file__).resolve().parents[2]
F=json.loads((ROOT/"docs/research/fixtures/tripn-synthetic-s0.json").read_text())
STAGES={s["id"]:s for s in F["stages"]}
CASES=[
 ("6",list(STAGES)[:6]),
 ("8",["design_handoff","styling_contract","site_chill_zone","plugin_search","plugin_results","plugin_cart","plugin_confirm_handoff","plugin_iframe"]),
 ("10",["design_handoff","styling_contract","site_chill_zone","plugin_search","plugin_results","plugin_cart","plugin_confirm_handoff","plugin_iframe","plugin_settings","booking_integration_test"])
]
def check(schedule,ids,ram,cpu,slots):
    assert set(schedule)==set(ids)
    for i,(a,b) in schedule.items():
        s=STAGES[i]
        assert b-a==s["duration_ticks"] and a>=0
        assert all(schedule[d][1]<=a for d in s["dependencies"] if d in ids)
    for t in range(max(b for a,b in schedule.values())):
        active=[STAGES[i] for i,(a,b) in schedule.items() if a<=t<b]
        assert sum(s["ram_mib"] for s in active)<=ram
        assert sum(s["cpu_millicores"] for s in active)<=cpu
        assert sum(s["slots"] for s in active)<=slots
def baseline(ids,ram,cpu,slots):
    plan={};pending=set(ids)
    while pending:
        ready=[i for i in pending if all(d in plan for d in STAGES[i]["dependencies"])]
        if not ready:raise ValueError("cycle or non-closed subset")
        i=min(ready,key=lambda k:(-STAGES[k]["duration_ticks"],k));s=STAGES[i]
        t=max((plan[d][1] for d in s["dependencies"]),default=0)
        while True:
            b=t+s["duration_ticks"]
            if all(
                sum(STAGES[k]["ram_mib"] for k,(a,z) in plan.items() if a<=x<z)+s["ram_mib"]<=ram and
                sum(STAGES[k]["cpu_millicores"] for k,(a,z) in plan.items() if a<=x<z)+s["cpu_millicores"]<=cpu and
                sum(STAGES[k]["slots"] for k,(a,z) in plan.items() if a<=x<z)+s["slots"]<=slots
                for x in range(t,b)):break
            t+=1
        plan[i]=(t,b);pending.remove(i)
    check(plan,ids,ram,cpu,slots)
    return max(b for a,b in plan.values())
def exact(ids,ram,cpu,slots,limit=20):
    H=sum(STAGES[i]["duration_ticks"] for i in ids)
    variables=[(i,t) for i in ids for t in range(H-STAGES[i]["duration_ticks"]+1)]
    N=len(variables);rows=[];lower=[];upper=[]
    def add(terms,lo,hi):rows.append(terms);lower.append(lo);upper.append(hi)
    for i in ids:add([(j,1) for j,(k,t) in enumerate(variables) if k==i],1,1)
    for i in ids:
        for d in STAGES[i]["dependencies"]:
            if d in ids:add([(j,t if k==i else -t) for j,(k,t) in enumerate(variables) if k in (i,d)],STAGES[d]["duration_ticks"],np.inf)
    for t in range(H):
        for key,cap in [("ram_mib",ram),("cpu_millicores",cpu),("slots",slots)]:
            add([(j,STAGES[i][key]) for j,(i,a) in enumerate(variables) if a<=t<a+STAGES[i]["duration_ticks"]],-np.inf,cap)
    for i in ids:add([(j,t) for j,(k,t) in enumerate(variables) if k==i]+[(N,-1)],-np.inf,-STAGES[i]["duration_ticks"])
    A=lil_matrix((len(rows),N+1))
    for r,terms in enumerate(rows):
        for j,v in terms:A[r,j]=v
    c=np.zeros(N+1);c[N]=1
    lb=np.zeros(N+1);ub=np.ones(N+1);ub[N]=H
    start=time.perf_counter()
    result=milp(c,integrality=np.ones(N+1),bounds=Bounds(lb,ub),constraints=LinearConstraint(A.tocsr(),lower,upper),options={"time_limit":limit,"mip_rel_gap":0})
    seconds=time.perf_counter()-start
    verified=False
    if result.x is not None:
        schedule={i:(t,t+STAGES[i]["duration_ticks"]) for j,(i,t) in enumerate(variables) if result.x[j]>.5}
        check(schedule,ids,ram,cpu,slots);verified=True
    return {"status":int(result.status),"objective":float(result.fun) if result.fun is not None else None,
            "bound":float(result.mip_dual_bound) if result.mip_dual_bound is not None else None,
            "gap":float(result.mip_gap) if result.mip_gap is not None else None,
            "seconds":round(seconds,3),"verified":verified,"variables":N+1}
if __name__=="__main__":
    for label,ids in CASES:
        for ram,cpu,slots in [(4096,2000,2),(8192,4000,4)]:
            g=baseline(ids,ram,cpu,slots);r=exact(ids,ram,cpu,slots)
            print(json.dumps({"case":label,"capacity":[ram,cpu,slots],"baseline":g,"exact":r}))
