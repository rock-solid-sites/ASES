"""Independent ASES schedule feasibility checker (standard library)."""
def validate(fixture, plan):
    errors = []
    stages = {s["id"]: s for s in fixture["stages"]}
    schedule = plan.get("stages", {})
    environments = plan.get("environments", {})
    if set(stages) != set(schedule):
        errors.append("stage set mismatch")
    for sid, spec in stages.items():
        if sid not in schedule:
            continue
        p = schedule[sid]
        a, b, env = p.get("start"), p.get("end"), p.get("environment")
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or a < 0 or b <= a:
            errors.append(f"{sid}: invalid interval")
            continue
        if env not in environments:
            errors.append(f"{sid}: unknown environment")
        for dep in spec.get("dependencies", []):
            if dep not in stages:
                errors.append(f"{sid}: unknown dependency {dep}")
            elif dep in schedule and schedule[dep].get("end", float("inf")) > a:
                errors.append(f"{sid}: dependency {dep} incomplete")
        for field, value in plan.get("frozen", {}).get(sid, {}).items():
            if p.get(field) != value:
                errors.append(f"{sid}: frozen {field} changed")
        for metric in ("ram_gib", "cpu_cores"):
            if not isinstance(p.get(metric), (int, float)) or p[metric] < 0:
                errors.append(f"{sid}: invalid {metric}")
    for env, capacity in environments.items():
        jobs = [p for p in schedule.values() if p.get("environment") == env and isinstance(p.get("start"), (int, float)) and isinstance(p.get("end"), (int, float))]
        for t in sorted({t for p in jobs for t in (p["start"], p["end"])})[:-1]:
            active = [p for p in jobs if p["start"] <= t < p["end"]]
            for metric in ("ram_gib", "cpu_cores"):
                if all(isinstance(p.get(metric), (int, float)) for p in active) and sum(p[metric] for p in active) > capacity[metric] + 1e-9:
                    errors.append(f"{env}@{t}: {metric} capacity exceeded")
    return errors
