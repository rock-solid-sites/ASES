"""Independent feasibility gate, prototype only; no solver dependency."""
def validate(fixture,plan):
    errors=[]
    stages={s["id"]:s for s in fixture["stages"]}
    if len(stages)!=len(fixture["stages"]):errors.append("duplicate stage id")
    jobs=plan.get("stages",{});envs=plan.get("environments",{})
    if set(jobs)!=set(stages):errors.append("stage set mismatch")
    if plan.get("fixture_id")!=fixture.get("scenario"):errors.append("fixture identity mismatch")
    if not plan.get("snapshot_id"):errors.append("missing snapshot identity")
    if type(plan.get("time_tick_seconds")) is not int or plan["time_tick_seconds"]<=0:errors.append("invalid time tick")
    for sid,s in stages.items():
        if sid not in jobs:continue
        p=jobs[sid]
        if not isinstance(p,dict):errors.append(f"{sid}: invalid record");continue
        a,b,e=p.get("start"),p.get("end"),p.get("environment")
        if type(a) is not int or type(b) is not int or a<0 or b<=a:errors.append(f"{sid}: invalid interval");continue
        if e not in envs:errors.append(f"{sid}: unknown environment");continue
        if e not in s.get("allowed_environments",list(envs)):errors.append(f"{sid}: environment ineligible")
        for d in s.get("dependencies",[]):
            if d not in stages:errors.append(f"{sid}: unknown dependency {d}")
            elif d not in jobs or jobs[d].get("end",float("inf"))>a:errors.append(f"{sid}: dependency {d} incomplete")
        if s.get("duration_ticks") is not None and b-a!=s["duration_ticks"]:errors.append(f"{sid}: duration mismatch")
        for k in ("ram_mib","cpu_millicores","slots"):
            if type(p.get(k)) is not int or p[k]<(1 if k=="slots" else 0):errors.append(f"{sid}: invalid {k}")
            if s.get(k) is not None and p.get(k)!=s[k]:errors.append(f"{sid}: {k} differs from authoritative workload")
        if not set(s.get("required_capabilities",[]))<=set(envs[e].get("capabilities",[])):errors.append(f"{sid}: missing capability")
        if s.get("data_class") is not None and s["data_class"] not in envs[e].get("allowed_data_classes",[]):errors.append(f"{sid}: data boundary violated")
        for k,v in plan.get("frozen",{}).get(sid,{}).items():
            if p.get(k)!=v:errors.append(f"{sid}: frozen {k} changed")
    for eid,cap in envs.items():
        active_jobs=[p for p in jobs.values() if isinstance(p,dict) and p.get("environment")==eid and type(p.get("start")) is int and type(p.get("end")) is int]
        for t in sorted({v for p in active_jobs for v in (p["start"],p["end"])})[:-1]:
            active=[p for p in active_jobs if p["start"]<=t<p["end"]]
            for k in ("ram_mib","cpu_millicores","slots"):
                if type(cap.get(k)) is not int or cap[k]<0:errors.append(f"{eid}: invalid {k} capacity")
                elif all(type(p.get(k)) is int for p in active) and sum(p[k] for p in active)>cap[k]:errors.append(f"{eid}@{t}: {k} capacity exceeded")
        for x,y in cap.get("outages",[]):
            if any(p["start"]<y and x<p["end"] for p in active_jobs):errors.append(f"{eid}: scheduled during outage")
    return sorted(set(errors))
