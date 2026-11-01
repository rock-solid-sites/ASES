"""Deterministic, nonoptimal earliest-fit baseline. Requires authoritative estimates."""
from validator_v1 import validate
def schedule(fixture,snapshot):
    stages={s["id"]:s for s in fixture["stages"]}
    if len(stages)!=len(fixture["stages"]):raise ValueError("duplicate stage")
    for s in stages.values():
        if type(s.get("duration_ticks")) is not int or s["duration_ticks"]<=0:raise ValueError("missing duration")
        if any(type(s.get(k)) is not int or s[k]<0 for k in ("ram_mib","cpu_millicores")):raise ValueError("missing demand")
        if any(d not in stages for d in s.get("dependencies",[])):raise ValueError("unknown dependency")
    envs=snapshot["environments"]
    plan={"fixture_id":fixture["scenario"],"snapshot_id":snapshot["id"],"time_tick_seconds":60,"environments":envs,"stages":{}}
    pending=set(stages)
    while pending:
        ready=sorted((sid for sid in pending if set(stages[sid].get("dependencies",[]))<=set(plan["stages"])),key=lambda sid:(-stages[sid]["duration_ticks"],sid))
        if not ready:raise ValueError("dependency cycle")
        sid=ready[0];s=stages[sid];earliest=max((plan["stages"][d]["end"] for d in s.get("dependencies",[])),default=0)
        demand={k:s.get(k,1 if k=="slots" else 0) for k in ("ram_mib","cpu_millicores","slots")}
        candidates=[]
        for eid,e in sorted(envs.items()):
            if eid not in s.get("allowed_environments",list(envs)):continue
            if not set(s.get("required_capabilities",[]))<=set(e.get("capabilities",[])):continue
            if s.get("data_class") is not None and s["data_class"] not in e.get("allowed_data_classes",[]):continue
            if any(demand[k]>e[k] for k in demand):continue
            t=earliest
            while t<100000:
                end=t+s["duration_ticks"]
                overlaps=[p for p in plan["stages"].values() if p["environment"]==eid and p["start"]<end and t<p["end"]]
                blockers=[p["end"] for p in overlaps if any(sum(q[k] for q in overlaps)+demand[k]>e[k] for k in demand)]
                outages=[b for a,b in e.get("outages",[]) if t<b and a<end]
                if not blockers and not outages:break
                t=max(t+1,min(blockers+outages))
            if t<100000:candidates.append((t+s["duration_ticks"],t,eid))
        if not candidates:raise ValueError(f"{sid}: no feasible environment")
        end,start,eid=min(candidates)
        plan["stages"][sid]={"start":start,"end":end,"environment":eid,**demand}
        pending.remove(sid)
    errors=validate(fixture,plan)
    if errors:raise ValueError(f"validator rejected: {errors}")
    return plan
