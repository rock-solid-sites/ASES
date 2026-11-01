"""Mode-aware portfolio planner regression tests."""
import copy
import unittest
from portfolio_harness_v2 import greedy, beam, order_tasks
from portfolio_oracle_v1 import validate

def sample():
    return {"horizon": 8, "accounts": {"a": {"credits": 5, "reserve": 1, "period": 4}},
        "environments": {"local": {"cpu": 2, "ram": 4, "slots": 1, "account": None},
                         "cloud": {"cpu": 8, "ram": 16, "slots": 2, "account": "a"}},
        "policy": {"p": ["a"]},
        "tasks": [{"id": "build", "project": "p", "duration": 4, "cpu": 2, "ram": 4,
                   "deadline": 5, "value": 7, "modes": ["local", "cloud"], "deps": [],
                   "mode_overrides": {"cloud": {"duration": 2, "cpu": 4, "ram": 8, "credits": 3}}},
                  {"id": "test", "project": "p", "duration": 2, "cpu": 2, "ram": 4,
                   "deadline": 8, "value": 5, "modes": ["local"], "deps": ["build"]}]}

class V2Tests(unittest.TestCase):
    def test_mode_aware(self):
        d = sample()
        for f in (greedy, beam):
            p = f(d)
            self.assertEqual(validate(d, p), [])
            self.assertEqual(len(p), 2)
    def test_period_reset(self):
        self.assertTrue(any("crosses account reset" in e for e in validate(sample(), {"build": {"env": "cloud", "start": 3}})))
    def test_mode_resource_collision(self):
        d = sample()
        d["tasks"][1]["modes"] = ["local", "cloud"]
        p = {"build": {"env": "cloud", "start": 0}, "test": {"env": "cloud", "start": 0}}
        self.assertTrue(validate(d, p))
    def test_dependency_cycle(self):
        d = sample()
        d["tasks"][0]["deps"] = ["test"]
        with self.assertRaises(ValueError):
            order_tasks(d)
    def test_no_mutation(self):
        d = sample()
        before = copy.deepcopy(d)
        greedy(d)
        beam(d)
        self.assertEqual(d, before)
    def test_determinism(self):
        d = sample()
        self.assertEqual(beam(d), beam(d))
    def test_invalid_width(self):
        with self.assertRaises(ValueError):
            beam(sample(), 0)
    def test_invalid_snapshot(self):
        d = sample()
        d["tasks"][0]["duration"] = 0
        for f in (greedy, beam):
            with self.assertRaises(ValueError):
                f(d)
    def test_account_period_boundary(self):
        self.assertEqual(validate(sample(), {"build": {"env": "cloud", "start": 4}}), [])
    def test_mode_credit_limit(self):
        d = sample()
        d["accounts"]["a"]["credits"] = 3
        self.assertTrue(any("protected credits" in e for e in validate(d, {"build": {"env": "cloud", "start": 0}})))

if __name__ == "__main__":
    unittest.main()
