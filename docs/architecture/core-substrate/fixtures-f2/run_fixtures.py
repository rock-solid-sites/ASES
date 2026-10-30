#!/usr/bin/env python3
"""Replay the machine-checkable F2 fixture tranche using the independent oracle."""
import json
from pathlib import Path
from f2lib import run_scenario, _read_path, build, Result, apply

ROOT = Path(__file__).resolve().parent
catalog = json.loads((ROOT / "fixtures.json").read_text())

class StepResult:
    def __init__(self, value):
        self.denied = value.get("denied")
        self.reason = value.get("reason", "")
        self.engine_denied = value.get("engine_denied")
        self.delete_blocked = value.get("delete_blocked")
        self.takeover_refused = value.get("takeover_refused")
        self.sink = value.get("sink")
        self.flags = value.get("flags", {})
        self.delete_reason = value.get("delete_reason", "")

def _dict_result(value):
    return StepResult(value)

def observed(expect, result, store):
    failures = []
    attrs = {"deny": "denied", "engine_deny": "engine_denied", "delete_blocked": "delete_blocked",
             "takeover_refused": "takeover_refused", "sink": "sink"}
    for key, attr in attrs.items():
        if key in expect and getattr(result, attr) != expect[key]:
            failures.append(f"{key}: expected {expect[key]!r}, got {getattr(result, attr)!r}")
    for key, value in expect.get("flags", {}).items():
        if result.flags.get(key) != value:
            failures.append(f"flag {key}: expected {value!r}, got {result.flags.get(key)!r}")
    for key, value in expect.get("store", {}).items():
        got = _read_path(store, key)
        if got != value:
            failures.append(f"store[{key}]: expected {value!r}, got {got!r}")
    if "reason_contains" in expect and expect["reason_contains"] not in (result.reason or ""):
        failures.append(f"reason {result.reason!r} lacks {expect['reason_contains']!r}")
    if "delete_reason_contains" in expect and expect["delete_reason_contains"] not in (result.delete_reason or ""):
        failures.append(f"delete reason {result.delete_reason!r} lacks {expect['delete_reason_contains']!r}")
    return failures

raw = []
failed = False
for fixture in catalog["fixtures"]:
    if fixture.get("status") == "prepared-only":
        raw.append({"id": fixture["id"], "trace": fixture["trace"], "assumption": fixture["assumption"],
                    "status": "prepared-only", "execution_scope": fixture.get("execution_note"),
                    "expected_observation": fixture["expected_observation"], "mutation": None})
        continue
    world = {"init": fixture["initial_state"]}
    step_observations = []
    if fixture.get("expected_steps"):
        store = build(fixture["initial_state"])
        result = Result()
        for event in fixture["events"]:
            result = Result()
            apply(store, event, result, fixture.get("mechanism", {}))
            step_observations.append(result.as_dict())
        baseline = []
        for index, expected in enumerate(fixture["expected_steps"]):
            baseline.extend([f"step {index}: {failure}" for failure in observed(expected, _dict_result(step_observations[index]), store)])
        baseline.extend(observed(fixture["expected_observation"], result, store))
    else:
        store, result = run_scenario(world, {"events": fixture["events"]}, fixture.get("mechanism"))
        baseline = observed(fixture["expected_observation"], result, store)
    record = {"id": fixture["id"], "trace": fixture["trace"], "assumption": fixture["assumption"],
              "status": "executed" if not baseline else "blocked", "execution_scope": "f2lib abstract replay only",
              "observation": result.as_dict(), "step_observations": step_observations,
              "store": store, "failures": baseline, "mutation": None}
    if fixture.get("mutation"):
        mechanism = dict(fixture.get("mechanism", {})); mechanism.update(fixture["mutation"])
        mutation_steps = []
        if fixture.get("expected_steps"):
            mutated_store = build(fixture["initial_state"])
            mutated_result = Result()
            for event in fixture["events"]:
                mutated_result = Result()
                apply(mutated_store, event, mutated_result, mechanism)
                mutation_steps.append(mutated_result.as_dict())
        else:
            mutated_store, mutated_result = run_scenario(world, {"events": fixture["events"]}, mechanism)
        mutation_failures = observed(fixture["mutation_expected"], mutated_result, mutated_store)
        record["mutation"] = {"mech": fixture["mutation"], "observation": mutated_result.as_dict(),
                              "step_observations": mutation_steps, "store": mutated_store,
                              "status": "discriminating" if not mutation_failures else "invalid",
                              "failures": mutation_failures}
        if mutation_failures:
            record["status"] = "blocked"
    failed |= record["status"] != "executed"
    raw.append(record)

out = {"schema": "f2-run-results-v1", "scope": "abstract reference replay; not host/runtime evidence",
       "executed": sum(item["status"] == "executed" for item in raw),
       "prepared_only": sum(item["status"] == "prepared-only" for item in raw),
       "blocked": sum(item["status"] == "blocked" for item in raw), "cases": raw}
(ROOT / "results.json").write_text(json.dumps(out, indent=2, sort_keys=True, default=lambda value: sorted(value) if isinstance(value, set) else repr(value)) + "\n")
print(json.dumps({"executed": out["executed"], "prepared_only": out["prepared_only"], "blocked": out["blocked"],
                  "mutations": {item["id"]: item["mutation"]["status"] for item in raw if item["mutation"]}}, indent=2))
raise SystemExit(1 if failed else 0)
