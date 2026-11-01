"""Portfolio allocation comparison harness. Standard library only; synthetic, not provider entitlements.
Run: python3 research/resource-solver/portfolio_harness_v0.py
"""
import itertools
import json
from collections import defaultdict

def fixture():
    return {
        "horizon": 7,
        "accounts": {
            "rss": {"credits": 10, "reserve": 3, "reset_day": 7},
            "mbd": {"credits": 8, "reserve": 2, "reset_day": 7},
        },
        "environments": {
            "vps": {"cpu": 4, "ram": 8, "slots": 2, "account": None, "startup": 0},
            "burst": {"cpu": 8, "ram": 32, "slots": 3, "account": "rss", "startup": 2},
            "mbd-cloud": {"cpu": 8, "ram": 32, "slots": 2, "account": "mbd", "startup": 2},
        },
        "tasks": [
            {"id": "hms-build", "project": "hms", "duration": 3, "cpu": 3, "ram": 5, "deadline": 3, "value": 10, "modes": ["vps", "burst"], "deps": []},
            {"id": "hms-test", "project": "hms", "duration": 2, "cpu": 5, "ram": 20, "deadline": 5, "value": 9, "modes": ["burst", "mbd-cloud"], "deps": ["hms-build"]},
            {"id": "ases-bench", "project": "ases", "duration": 2, "cpu": 3, "ram": 8, "deadline": 6, "value": 6, "modes": ["vps", "burst", "mbd-cloud"], "deps": []},
            {"id": "rss-test", "project": "rss", "duration": 1, "cpu": 2, "ram": 4, "deadline": 6, "value": 4, "modes": ["vps", "burst"], "deps": []},
            {"id": "mbd-work", "project": "mbd", "duration": 2, "cpu": 4, "ram": 12, "deadline": 7, "value": 8, "modes": ["mbd-cloud"], "deps": []},
        ],
        "policy": {"hms": ["rss"], "ases": ["rss", "mbd"], "rss": ["rss"], "mbd": ["mbd"]},
    }

def validate(data, placements):
    errors = []
    tasks = {t["id"]: t for t in data["tasks"]}
    envs = data["environments"]
    used = defaultdict(int)
    for tid, p in placements.items():
        if tid not in tasks:
            errors.append("unknown task " + tid)
            continue
        t = tasks[tid]
        eid, start = p["env"], p["start"]
        if eid not in envs or eid not in t["modes"]:
            errors.append(tid + ": ineligible environment")
            continue
        e = envs[eid]
        if type(start) is not int or start < 0 or start + t["duration"] > data["horizon"]:
            errors.append(tid + ": invalid interval")
            continue
        owner = e["account"]
        if owner and owner not in data["policy"][t["project"]]:
            errors.append(tid + ": borrowing prohibited")
        if owner:
            used[owner] += t["duration"]
        for dep in t["deps"]:
            if dep not in placements or dep not in tasks or placements[dep]["start"] + tasks[dep]["duration"] > start:
                errors.append(tid + ": dependency")
        for day in range(start, start + t["duration"]):
            active = [tasks[other] for other, op in placements.items()
                      if other in tasks and op.get("env") == eid and type(op.get("start")) is int
                      and op["start"] <= day < op["start"] + tasks[other]["duration"]]
            if sum(x["cpu"] for x in active) > e["cpu"] or sum(x["ram"] for x in active) > e["ram"] or len(active) > e["slots"]:
                errors.append(eid + ": capacity day " + str(day))
    for owner, amount in used.items():
        a = data["accounts"][owner]
        if amount > a["credits"] - a["reserve"]:
            errors.append(owner + ": protected allowance exceeded")
    return sorted(set(errors))

def score(data, plan):
    tasks = {t["id"]: t for t in data["tasks"]}
    completed = sum(tasks[k]["value"] for k, p in plan.items() if p["start"] + tasks[k]["duration"] <= tasks[k]["deadline"])
    late = sum(1 for k, p in plan.items() if p["start"] + tasks[k]["duration"] > tasks[k]["deadline"])
    credit = sum(tasks[k]["duration"] for k, p in plan.items() if data["environments"][p["env"]]["account"])
    instances = {(p["env"], p["start"] // data["horizon"]) for p in plan.values() if data["environments"][p["env"]]["startup"]}
    startup = sum(data["environments"][e]["startup"] for e, _ in instances)
    return {"value_on_time": completed, "late": late, "credit_ticks": credit, "startup_units": startup, "tasks": len(plan)}

def candidates(data, task, plan):
    for eid in task["modes"]:
        for start in range(data["horizon"] - task["duration"] + 1):
            proposal = {**plan, task["id"]: {"env": eid, "start": start}}
            if not validate(data, proposal):
                yield proposal

def greedy(data):
    plan = {}
    pending = {t["id"]: t for t in data["tasks"]}
    while pending:
        ready = [t for t in pending.values() if all(d in plan for d in t["deps"])]
        if not ready:
            raise ValueError("cyclic dependencies")
        task = min(ready, key=lambda t: (t["deadline"], -t["value"], t["id"]))
        choices = list(candidates(data, task, plan))
        if choices:
            plan = min(choices, key=lambda p: (p[task["id"]]["start"] + task["duration"], score(data, p)["credit_ticks"], p[task["id"]]["env"]))
        del pending[task["id"]]
    return plan

def beam(data, width=100):
    """Bounded portfolio lookahead, not an exact solver. May omit tasks."""
    order = []
    pending = {t["id"]: t for t in data["tasks"]}
    while pending:
        ready = sorted((t for t in pending.values() if all(d in order for d in t["deps"])), key=lambda t: (t["deadline"], -t["value"]))
        if not ready:
            raise ValueError("cyclic dependencies")
        t = ready[0]
        order.append(t["id"])
        del pending[t["id"]]
    tasks = {t["id"]: t for t in data["tasks"]}
    states = [{}]
    for tid in order:
        new = []
        for p in states:
            new.append(p)
            if all(d in p for d in tasks[tid]["deps"]):
                new.extend(candidates(data, tasks[tid], p))
        new.sort(key=lambda p: (-score(data, p)["value_on_time"], -score(data, p)["tasks"], score(data, p)["credit_ticks"], score(data, p)["startup_units"], json.dumps(p, sort_keys=True)))
        states = new[:width]
    return states[0]

def run():
    data = fixture()
    results = {}
    for name, plan in (("greedy", greedy(data)), ("beam100", beam(data))):
        errors = validate(data, plan)
        if errors:
            raise AssertionError((name, errors))
        results[name] = {"metrics": score(data, plan), "plan": plan}
    print(json.dumps({"scenario": "synthetic-portfolio-v0", "limitations": "Daily ticks, synthetic quotas; no provider APIs, no inference coupling, no actual execution", "results": results}, indent=2, sort_keys=True))
    return results

if __name__ == "__main__":
    run()
