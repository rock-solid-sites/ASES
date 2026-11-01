"""Fail-closed portfolio admission oracle, independent of scheduling algorithms.

Version 1 models account-period credits and task-specific execution modes.
All values are synthetic. This module does not import portfolio_harness_v0.
"""
from collections import defaultdict

def validate(snapshot, placements):
    errors = []
    if not isinstance(snapshot, dict) or not isinstance(placements, dict):
        return ["invalid snapshot or plan"]
    try:
        horizon = snapshot["horizon"]
        tasks_raw = snapshot["tasks"]
        envs = snapshot["environments"]
        accounts = snapshot["accounts"]
        policy = snapshot["policy"]
        if type(horizon) is not int or horizon <= 0 or not isinstance(tasks_raw, list) or not isinstance(envs, dict) or not isinstance(accounts, dict) or not isinstance(policy, dict):
            return ["invalid snapshot structure"]
        tasks = {}
        for task in tasks_raw:
            if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not task["id"] or task["id"] in tasks:
                errors.append("duplicate or invalid task id")
                continue
            tasks[task["id"]] = task
        if errors:
            return sorted(set(errors))
        usage = defaultdict(int)
        timelines = defaultdict(list)
        for tid, placement in placements.items():
            if tid not in tasks:
                errors.append("unknown task: " + str(tid))
                continue
            if not isinstance(placement, dict):
                errors.append(tid + ": malformed placement")
                continue
            task = tasks[tid]
            env_id, start = placement.get("env"), placement.get("start")
            if env_id not in envs or env_id not in task["modes"]:
                errors.append(tid + ": ineligible environment")
                continue
            env = envs[env_id]
            if type(start) is not int or start < 0:
                errors.append(tid + ": invalid start")
                continue
            mode = task.get("mode_overrides", {}).get(env_id, {})
            duration = mode.get("duration", task["duration"])
            cpu = mode.get("cpu", task["cpu"])
            ram = mode.get("ram", task["ram"])
            credits = mode.get("credits", duration if env.get("account") else 0)
            if any(type(x) is not int or x < 0 for x in (duration, cpu, ram, credits)) or duration == 0:
                errors.append(tid + ": invalid demand")
                continue
            end = start + duration
            if end > horizon:
                errors.append(tid + ": outside horizon")
                continue
            if any(type(env.get(k)) is not int or env[k] <= 0 for k in ("cpu", "ram", "slots")):
                errors.append(env_id + ": invalid capacity")
                continue
            if cpu > env["cpu"] or ram > env["ram"]:
                errors.append(tid + ": exceeds environment capacity")
            owner = env.get("account")
            if owner is not None:
                if owner not in accounts or owner not in policy.get(task["project"], []):
                    errors.append(tid + ": unauthorized account")
                else:
                    period = accounts[owner].get("period", horizon)
                    if type(period) is not int or period <= 0:
                        errors.append(owner + ": invalid period")
                    elif start // period != (end - 1) // period:
                        errors.append(tid + ": crosses account reset")
                    else:
                        usage[(owner, start // period)] += credits
            timelines[env_id].append((start, end, cpu, ram, tid))
            for dep in task.get("deps", []):
                if dep not in tasks or dep not in placements or not isinstance(placements[dep], dict):
                    errors.append(tid + ": missing dependency " + str(dep))
                    continue
                dp = placements[dep]
                de = dp.get("env")
                ds = dp.get("start")
                if de not in envs or type(ds) is not int:
                    errors.append(tid + ": invalid dependency")
                    continue
                dt = tasks[dep]
                dd = dt.get("mode_overrides", {}).get(de, {}).get("duration", dt["duration"])
                if type(dd) is not int or ds + dd > start:
                    errors.append(tid + ": dependency not complete")
        for env_id, spans in timelines.items():
            env = envs[env_id]
            for time in sorted({x for a, b, _, _, _ in spans for x in (a, b)})[:-1]:
                active = [(cpu, ram) for a, b, cpu, ram, _ in spans if a <= time < b]
                if len(active) > env["slots"] or sum(x for x, _ in active) > env["cpu"] or sum(y for _, y in active) > env["ram"]:
                    errors.append(env_id + ": capacity exceeded at " + str(time))
        for (owner, period_index), consumed in usage.items():
            acc = accounts[owner]
            limit, reserve = acc.get("credits"), acc.get("reserve", 0)
            if type(limit) is not int or type(reserve) is not int or reserve < 0 or limit < reserve:
                errors.append(owner + ": invalid credit budget")
            elif consumed > limit - reserve:
                errors.append(owner + ": protected credits exceeded in period " + str(period_index))
        return sorted(set(errors))
    except (KeyError, TypeError, ValueError, IndexError, AttributeError, OverflowError) as exc:
        return sorted(set(errors + ["malformed input: " + type(exc).__name__]))
