"""Synthetic 18-stage single-environment reference benchmark. No external dependencies.
Run from repo root: python research/resource-solver/benchmark_tripn_s0.py
Resource assumptions are S-tier, not observed TripN execution metrics.
"""
import json
import pathlib
import time
ROOT=pathlib.Path(__file__).resolve().parents[2]
F=json.loads((ROOT/"docs/research/fixtures/tripn-synthetic-s0.json").read_text())
def run(ram=4096,cpu=2000,slots=2,outage=None):
    stages={s["id"]:s for s in F["stages"]}
    scheduled={}
    pending=set(stages)
    start_clock=time.perf_counter_ns()
    while pending:
        ready=[stages[k] for k in pending if all(d in scheduled for d in stages[k]["dependencies"])]
        if not ready:raise ValueError("cycle")
        s=min(ready,key=lambda x:(-x["duration_ticks"],x["id"]))
        sid=s["id"]
        if s["ram_mib"]>ram or s["cpu_millicores"]>cpu or s["slots"]>slots:raise ValueError("oversized stage")
        t=max((scheduled[d][1] for d in s["dependencies"]),default=0)
        while True:
            end=t+s["duration_ticks"]
            checkpoints=sorted({t,end}|{x for a,b in scheduled.values() for x in (a,b) if t<x<end})
            valid=True
            for x,y in zip(checkpoints,checkpoints[1:]):
                active=[stages[k] for k,(a,b) in scheduled.items() if a<y and x<b]
                if (sum(q["ram_mib"] for q in active)+s["ram_mib"]>ram or
                    sum(q["cpu_millicores"] for q in active)+s["cpu_millicores"]>cpu or
                    sum(q["slots"] for q in active)+s["slots"]>slots):
                    valid=False;break
            if outage and t<outage[1] and outage[0]<end:valid=False
            if valid:break
            t+=1
        scheduled[sid]=(t,end);pending.remove(sid)
    elapsed=(time.perf_counter_ns()-start_clock)/1e6
    # Independent minute-by-minute resource and precedence check.
    makespan=max(b for a,b in scheduled.values())
    for sid,(a,b) in scheduled.items():
        assert b-a==stages[sid]["duration_ticks"]
        assert all(scheduled[d][1]<=a for d in stages[sid]["dependencies"])
    for t in range(makespan):
        active=[stages[k] for k,(a,b) in scheduled.items() if a<=t<b]
        assert sum(s["ram_mib"] for s in active)<=ram
        assert sum(s["cpu_millicores"] for s in active)<=cpu
        assert sum(s["slots"] for s in active)<=slots
        if outage and outage[0]<=t<outage[1]:assert not active
    return {"makespan_minutes":makespan,"scheduler_ms":round(elapsed,3),"validated":True,
            "schedule":{k:{"start":a,"end":b} for k,(a,b) in sorted(scheduled.items())}}
if __name__=="__main__":
    cases={"vps_4g_2cpu":{},"vps_8g_4cpu":{"ram":8192,"cpu":4000,"slots":4},
           "vps_4g_outage":{"outage":(0,15)}}
    print(json.dumps({k:run(**v) for k,v in cases.items()},indent=2))
