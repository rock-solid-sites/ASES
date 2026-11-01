"""Mode-aware portfolio planner v2. Synthetic research only; independent admission."""
import json
from portfolio_oracle_v1 import validate

def demand(task, env, owner):
    mode = task.get("mode_overrides", {}).get(env, {})
    duration = mode.get("duration", task["duration"])
    return duration, mode.get("credits", duration if owner else 0)

def metric(snapshot, plan):
    tasks = {t["id"]: t for t in snapshot["tasks"]}
    envs = snapshot["environments"]
    value = credits = 0
    for tid, p in plan.items():
        t = tasks[tid]
        duration, cost = demand(t, p["env"], envs[p["env"]].get("account"))
        if p["start"] + duration <= t["deadline"]:
            value += t.get("value", 0)
        credits += cost
    return value, len(plan), -credits

def order_tasks(snapshot):
    tasks = {t["id"]: t for t in snapshot["tasks"]}
    pending, ordered = set(tasks), []
    while pending:
        ready = [tasks[tid] for tid in pending if set(tasks[tid].get("deps", [])) <= set(ordered)]
        if not ready:
            raise ValueError("dependency cycle")
        t = min(ready, key=lambda t: (t["deadline"], -t.get("value", 0), t["id"]))
        ordered.append(t["id"])
        pending.remove(t["id"])
    return ordered

def options(snapshot, task, plan):
    for eid in sorted(task["modes"]):
        env = snapshot["environments"][eid]
        duration, _ = demand(task, eid, env.get("account"))
        for start in range(snapshot["horizon"] - duration + 1):
            p = {**plan, task["id"]: {"env": eid, "start": start}}
            if not validate(snapshot, p):
                yield p

def greedy(snapshot):
    if validate(snapshot, {}):
        raise ValueError("invalid snapshot")
    plan = {}
    for tid in order_tasks(snapshot):
        t = next(x for x in snapshot["tasks"] if x["id"] == tid)
        choices = list(options(snapshot, t, plan))
        if choices:
            plan = min(choices, key=lambda p: (p[tid]["start"] + demand(t, p[tid]["env"], snapshot["environments"][p[tid]["env"]].get("account"))[0], -metric(snapshot, p)[0], -metric(snapshot, p)[2], p[tid]["env"]))
    return plan

def beam(snapshot, width=100):
    if type(width) is not int or width < 1 or validate(snapshot, {}):
        raise ValueError("invalid snapshot or beam width")
    states = [{}]
    tasks = {t["id"]: t for t in snapshot["tasks"]}
    for tid in order_tasks(snapshot):
        proposals = []
        for p in states:
            proposals.append(p)
            if set(tasks[tid].get("deps", [])) <= set(p):
                proposals.extend(options(snapshot, tasks[tid], p))
        proposals.sort(key=lambda p: (*(-v for v in metric(snapshot, p)), json.dumps(p, sort_keys=True)))
        states = proposals[:width]
    return states[0]
