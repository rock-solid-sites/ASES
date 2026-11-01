"""Negative and metamorphic tests for the independent portfolio oracle."""
import copy
import random
import unittest
from portfolio_harness_v0 import fixture, greedy, beam
from portfolio_oracle_v1 import validate

class OracleTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()
        for account in self.data["accounts"].values():
            account["period"] = 7
        self.good = {"hms-build": {"env": "vps", "start": 0},
                     "hms-test": {"env": "burst", "start": 3},
                     "mbd-work": {"env": "mbd-cloud", "start": 0}}

    def reject(self, data, plan, expected):
        errors = validate(data, plan)
        self.assertTrue(any(expected in e for e in errors), errors)

    def test_baselines_admitted(self):
        for planner in (greedy, beam):
            self.assertEqual(validate(self.data, planner(self.data)), [])

    def test_duplicate_task_id(self):
        self.data["tasks"].append(copy.deepcopy(self.data["tasks"][0]))
        self.reject(self.data, self.good, "duplicate")

    def test_malformed_inputs_fail_closed(self):
        for plan in (None, [], {"hms-build": None}, {"hms-build": {"env": "vps", "start": "zero"}}, {"unknown": {"env": "vps", "start": 0}}):
            self.assertTrue(validate(self.data, plan))
        self.assertTrue(validate(None, self.good))

    def test_unauthorized_borrow(self):
        self.data["tasks"][2]["modes"] = ["mbd-cloud"]
        self.data["policy"]["ases"] = ["rss"]
        self.reject(self.data, {"ases-bench": {"env": "mbd-cloud", "start": 0}}, "unauthorized")

    def test_shared_account_double_spend(self):
        self.data["accounts"]["rss"]["credits"] = 5
        self.data["accounts"]["rss"]["reserve"] = 3
        self.reject(self.data, self.good, "protected credits")

    def test_reset_boundary(self):
        self.data["accounts"]["mbd"]["period"] = 2
        self.reject(self.data, {"mbd-work": {"env": "mbd-cloud", "start": 1}}, "crosses account reset")

    def test_reset_allows_new_period(self):
        self.data["accounts"]["mbd"]["period"] = 2
        self.assertEqual(validate(self.data, {"mbd-work": {"env": "mbd-cloud", "start": 2}}), [])

    def test_mode_specific_resource_demand(self):
        task = next(t for t in self.data["tasks"] if t["id"] == "hms-build")
        task["mode_overrides"] = {"vps": {"ram": 9}}
        self.reject(self.data, {"hms-build": {"env": "vps", "start": 0}}, "exceeds environment")

    def test_mode_specific_duration(self):
        task = next(t for t in self.data["tasks"] if t["id"] == "hms-build")
        task["mode_overrides"] = {"vps": {"duration": 5}}
        self.reject(self.data, self.good, "dependency not complete")

    def test_capacity_collision(self):
        self.reject(self.data, {"hms-build": {"env": "vps", "start": 0},
                                "rss-test": {"env": "vps", "start": 0}}, "capacity exceeded")

    def test_random_mutation_rejections(self):
        randomizer = random.Random(2718)
        for _ in range(60):
            data = copy.deepcopy(self.data)
            plan = copy.deepcopy(self.good)
            change = randomizer.choice(("negative", "unknown", "overspend", "invalid_mode"))
            if change == "negative":
                plan["hms-build"]["start"] = -randomizer.randint(1, 10)
                expected = "invalid start"
            elif change == "unknown":
                plan["hms-build"]["env"] = "missing"
                expected = "ineligible"
            elif change == "overspend":
                data["accounts"]["rss"]["reserve"] = 10
                expected = "protected credits"
            else:
                plan["hms-test"]["env"] = "vps"
                expected = "ineligible"
            self.reject(data, plan, expected)

if __name__ == "__main__":
    unittest.main()
