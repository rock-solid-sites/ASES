"""Seeded portfolio stress, boundary, metamorphic and tiny-instance checks."""
import copy
import itertools
import random
import unittest
from portfolio_harness_v0 import fixture, greedy, beam, score
from portfolio_oracle_v1 import validate

class PortfolioStress(unittest.TestCase):
    def setUp(self):
        self.data = fixture()
        for account in self.data["accounts"].values():
            account["period"] = 7

    def test_shared_account_spend_across_projects(self):
        d = self.data
        d["accounts"]["rss"]["credits"] = 5
        d["accounts"]["rss"]["reserve"] = 1
        p = {"hms-build": {"env": "burst", "start": 0},
             "rss-test": {"env": "burst", "start": 3},
             "hms-test": {"env": "burst", "start": 3}}
        self.assertTrue(any("protected credits" in e for e in validate(d, p)))

    def test_boundary_exact_budget(self):
        d = self.data
        d["accounts"]["rss"]["credits"] = 5
        d["accounts"]["rss"]["reserve"] = 3
        p = {"hms-test": {"env": "burst", "start": 3},
             "hms-build": {"env": "vps", "start": 0}}
        self.assertEqual(validate(d, p), [])

    def test_capacity_endpoints_not_overlapping(self):
        p = {"hms-build": {"env": "vps", "start": 0},
             "ases-bench": {"env": "vps", "start": 3}}
        self.assertEqual(validate(self.data, p), [])

    def test_permutation_invariance(self):
        p = beam(self.data)
        for seed in range(25):
            items = list(p.items())
            random.Random(seed).shuffle(items)
            self.assertEqual(validate(self.data, dict(items)), [])

    def test_monotone_capacity(self):
        p = beam(self.data)
        for seed in range(30):
            d = copy.deepcopy(self.data)
            rng = random.Random(seed)
            for e in d["environments"].values():
                e["cpu"] += rng.randrange(5)
                e["ram"] += rng.randrange(8)
                e["slots"] += rng.randrange(3)
            self.assertEqual(validate(d, p), [])

    def test_monotone_credits(self):
        p = beam(self.data)
        for seed in range(30):
            d = copy.deepcopy(self.data)
            rng = random.Random(seed)
            for a in d["accounts"].values():
                a["credits"] += rng.randrange(10)
            self.assertEqual(validate(d, p), [])

    def test_seeded_planner_scenarios(self):
        for seed in range(40):
            d = copy.deepcopy(self.data)
            rng = random.Random(seed)
            for t in d["tasks"]:
                t["value"] = rng.randint(1, 20)
                t["deadline"] = rng.randint(max(t["duration"], 3), 7)
            for a in d["accounts"].values():
                a["credits"] += rng.randint(0, 5)
            for name, fn in (("greedy", greedy), ("beam", beam)):
                with self.subTest(seed=seed, planner=name):
                    p = fn(d)
                    self.assertEqual(validate(d, p), [])
                    self.assertLessEqual(len(p), len(d["tasks"]))

    def test_seeded_mutation_fuzz(self):
        baseline = beam(self.data)
        for seed in range(100):
            rng = random.Random(seed)
            p = copy.deepcopy(baseline)
            d = copy.deepcopy(self.data)
            tid = rng.choice(list(p))
            kind = rng.randrange(5)
            if kind == 0:
                p[tid]["start"] = -1
            elif kind == 1:
                p[tid]["env"] = "nonexistent"
            elif kind == 2:
                p[tid]["start"] = "invalid"
            elif kind == 3:
                d["tasks"].append(copy.deepcopy(d["tasks"][0]))
            else:
                d["environments"][p[tid]["env"]]["cpu"] = 0
            self.assertTrue(validate(d, p), f"seed={seed},kind={kind}")

    def test_exact_tiny_reference(self):
        d = {"horizon": 3, "accounts": {}, "policy": {"a": []},
             "environments": {"e": {"cpu": 1, "ram": 1, "slots": 1,
                                    "account": None, "startup": 0}},
             "tasks": [
                 {"id": "a", "project": "a", "duration": 2, "cpu": 1,
                  "ram": 1, "deadline": 2, "value": 5, "modes": ["e"], "deps": []},
                 {"id": "b", "project": "a", "duration": 2, "cpu": 1,
                  "ram": 1, "deadline": 3, "value": 4, "modes": ["e"], "deps": []}]}
        valid = []
        for x, y in itertools.product((None, 0, 1), repeat=2):
            p = {k: {"env": "e", "start": v}
                 for k, v in (("a", x), ("b", y)) if v is not None}
            if not validate(d, p):
                valid.append(score(d, p)["value_on_time"])
        self.assertEqual(max(valid), 5)
        self.assertEqual(score(d, beam(d))["value_on_time"], max(valid))

if __name__ == "__main__":
    unittest.main()
