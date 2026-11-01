"""Deterministic generated DAG families for mode-aware scheduling experiments."""
import random
from portfolio_oracle_v1 import validate
from portfolio_harness_v2 import greedy, beam, metric

def scenario(seed, count=8):
    if type(count) is not int or not 2 <= count <= 24:
        raise ValueError("count must be 2..24")
    rng = random.Random(seed)
    d = {"horizon": 18, "accounts": {"shared": {"credits": 18, "reserve": 2, "period": 9}},
         "environments": {
             "local": {"cpu": 4, "ram": 8, "slots": 2, "account": None},
             "cloud": {"cpu": 8, "ram": 24, "slots": 3, "account": "shared"}},
         "policy": {"alpha": ["shared"], "beta": ["shared"], "gamma": ["shared"]}, "tasks": []}
    for i in range(count):
        duration = rng.randint(1, 4)
        cpu = rng.randint(1, 3)
        ram = rng.randint(1, 6)
        deps = [f"task-{j}" for j in range(i) if rng.random() < .09]
        d["tasks"].append({
            "id": f"task-{i}", "project": rng.choice(["alpha", "beta", "gamma"]),
            "duration": duration, "cpu": cpu, "ram": ram, "deadline": rng.randint(4, 18),
            "value": rng.randint(1, 15), "modes": ["local", "cloud"], "deps": deps,
            "mode_overrides": {"cloud": {"duration": max(1, duration - 1),
                                         "cpu": min(8, cpu + 1),
                                         "ram": min(24, ram + 2),
                                         "credits": rng.randint(1, 3)}}})
    return d

def evaluate(seeds=range(20), count=8, width=30):
    records = []
    for seed in seeds:
        d = scenario(seed, count)
        for name, planner in (("greedy", greedy), ("beam", lambda x: beam(x, width))):
            p = planner(d)
            errors = validate(d, p)
            if errors:
                raise AssertionError((seed, name, errors))
            records.append({"seed": seed, "planner": name, "tasks": len(p),
                            "on_time_value": metric(d, p)[0],
                            "credits": -metric(d, p)[2]})
    return records

if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2))
