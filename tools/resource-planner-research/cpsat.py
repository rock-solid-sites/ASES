"""Research-only CP-SAT comparison. Install ortools independently; not a chosen runtime."""
import sys,json,time
from common import load,report
from ortools.sat.python import cp_model

def solve(m, time_limit=3.0):
    model=cp_model.CpModel();jobs=list(m['stages']);rs=m['resources']
    horizon=sum(max((v['duration'] for v in st['modes']),default=0)+st.get('transferMinutesIfMoved',0) for st in m['stages'].values())+1
    if any(not m['stages'][n]['modes'] for n in jobs):return None,'INFEASIBLE','proven',0
    xs={}; starts={}; ends={}; intervals={rid:[] for rid in rs}; charge={rid:[] for rid in rs}; cost=[]
    for n in jobs:
        st=m['stages'][n]; starts[n]=model.NewIntVar(0,horizon,'start_'+n);ends[n]=model.NewIntVar(0,horizon,'end_'+n)
        bs=[]
        for k,mo in enumerate(st['modes']):
            b=model.NewBoolVar('mode_'+n+'_'+str(k));xs[n,k]=b;bs.append(b)
            iv=model.NewOptionalIntervalVar(starts[n],mo['duration'],ends[n],b,'interval_'+n+'_'+str(k))
            rid=mo['resource'];intervals[rid].append(iv);charge[rid].append(mo['duration']*b);cost.append(mo.get('costCents',0)*b)
        model.AddExactlyOne(bs)
    for rid,iv in intervals.items():
        if iv:model.AddNoOverlap(iv)
        model.Add(sum(charge[rid])<=rs[rid]['quotaMinutes'])
    model.Add(sum(cost)<=m['budgetCents'])
    for n in jobs:
        st=m['stages'][n]
        for pred in st.get('after',[]):
            for a,pmo in enumerate(m['stages'][pred]['modes']):
                for b,cmo in enumerate(st['modes']):
                    lag=st.get('transferMinutesIfMoved',0) if pmo['resource']!=cmo['resource'] else 0
                    model.Add(starts[n]>=ends[pred]+lag).OnlyEnforceIf([xs[pred,a],xs[n,b]])
        for other in st.get('independentFrom',[]):
            for a,mo in enumerate(st['modes']):
                for b,othermode in enumerate(m['stages'][other]['modes']):
                    if mo['resource']==othermode['resource']:
                        model.AddBoolOr([xs[n,a].Not(),xs[other,b].Not()])
    finish=model.NewIntVar(0,horizon,'finish');model.AddMaxEquality(finish,[ends[n] for n in jobs]);model.Minimize(finish)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=time_limit;solver.parameters.num_search_workers=1;solver.parameters.random_seed=1
    status=solver.Solve(model);sg={cp_model.OPTIMAL:'OPTIMAL',cp_model.FEASIBLE:'FEASIBLE_NOT_PROVEN',cp_model.INFEASIBLE:'INFEASIBLE',cp_model.UNKNOWN:'UNKNOWN',cp_model.MODEL_INVALID:'MODEL_INVALID'}[status]
    plans=None
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        plans={}
        for n in jobs:
            idx=next(k for k in range(len(m['stages'][n]['modes'])) if solver.Value(xs[n,k])); plans[n]=(m['stages'][n]['modes'][idx]['resource'],solver.Value(starts[n]),solver.Value(ends[n]),idx)
    return plans,sg,'proven' if sg in ('OPTIMAL','INFEASIBLE') else 'bounded',solver.NumBranches()

if __name__=='__main__':
    m=load(sys.argv[1]);ts=time.perf_counter()
    plans,status,guar,branches=solve(m,float(sys.argv[2]) if len(sys.argv)>2 else 3.0)
    print(json.dumps(report(m,'ortools-cpsat',plans,(time.perf_counter()-ts)*1000,status,guar,{'branches':branches})))
