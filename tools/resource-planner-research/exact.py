"""Research-only small-graph exact enumerator: topological serial schedule generation.
For this deliberately narrow fixture model, it enumerates every eligible mode and every
ready task order, placing a chosen task at earliest feasible time on its resource.
No release dates, machine calendars, complex setup or preemptions in this proof-of-concept.
"""
import sys,json,time
from common import load,report

class LimitExceeded(Exception): pass

def solve(m, node_cap=1000000):
    jobs=m['stages'];res=m['resources'];best=None;best_makespan=10**10; explored=0
    if any(not x['modes'] for x in jobs.values()):return None,0,'INFEASIBLE'
    # a resource can execute one stage at a time; order is actively enumerated.
    def rec(done,plans,cost,usage):
        nonlocal best,best_makespan,explored
        explored+=1
        if explored>node_cap:raise LimitExceeded()
        if len(done)==len(jobs):
            finish=max(v[2] for v in plans.values())
            if finish < best_makespan or (finish==best_makespan and (best is None or cost<sum(jobs[k]['modes'][v[3]].get('costCents',0) for k,v in best.items()))):
                best_makespan=finish;best=plans.copy()
            return
        ready=[n for n,st in jobs.items() if n not in done and all(d in done for d in st.get('after',[]))]
        for n in ready:
            st=jobs[n]
            for idx,mode in enumerate(st['modes']):
                rid=mode['resource'];duration=mode['duration'];extra=mode.get('costCents',0)
                if cost+extra>m['budgetCents'] or usage.get(rid,0)+duration>res[rid]['quotaMinutes']:continue
                if any(plans.get(o,(None,))[0]==rid for o in st.get('independentFrom',[])):continue
                if any(rid == plans[other][0] and n in jobs[other].get('independentFrom',[]) for other in done):continue
                earliest=0
                for pred in st.get('after',[]):
                    pr,_,end,_=plans[pred]
                    earliest=max(earliest,end+(st.get('transferMinutesIfMoved',0) if pr!=rid else 0))
                # schedule at earliest non-overlapping gap, not solely at end of resource.
                intervals=sorted((s,e) for other,(r,s,e,_) in plans.items() if r==rid)
                start=earliest
                for s,e in intervals:
                    if start+duration<=s:break
                    if start<e:start=e
                if start+duration>=best_makespan:continue
                newp=plans.copy();newp[n]=(rid,start,start+duration,idx)
                newu=usage.copy();newu[rid]=newu.get(rid,0)+duration
                rec(done|{n},newp,cost+extra,newu)
    try:rec(set(),{},0,{})
    except LimitExceeded:return best,explored,'FEASIBLE_NOT_PROVEN' if best else 'UNKNOWN'
    return best,explored,'OPTIMAL' if best else 'INFEASIBLE'

if __name__=='__main__':
    m=load(sys.argv[1]);t=time.perf_counter()
    p,n,stat=solve(m,int(sys.argv[2]) if len(sys.argv)>2 else 1000000)
    print(json.dumps(report(m,'exact-enumerator',p,(time.perf_counter()-t)*1000,stat,'proven' if stat in ('OPTIMAL','INFEASIBLE') else 'bounded',{'nodes':n})))
