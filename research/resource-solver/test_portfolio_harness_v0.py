"""Regression tests for synthetic portfolio harness; no external dependencies."""
import unittest
from portfolio_harness_v0 import fixture, validate, greedy, beam, score

class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()

    def test_both_planners_feasible(self):
        for planner in (greedy, beam):
            self.assertEqual(validate(self.data, planner(self.data)), [])

    def test_borrowing_permission(self):
        plan = {"hms-build": {"env": "mbd-cloud", "start": 0}}
        self.assertTrue(any("ineligible" in e or "borrowing" in e for e in validate(self.data, plan)))

    def test_protected_allowance(self):
        self.data["accounts"]["rss"]["reserve"] = 10
        plan = {"hms-build": {"env": "burst", "start": 0}}
        self.assertTrue(any("allowance" in e for e in validate(self.data, plan)))

    def test_capacity(self):
        plan = {"hms-build": {"env": "vps", "start": 0},
                "rss-test": {"env": "vps", "start": 0}}
        self.assertTrue(any("capacity" in e for e in validate(self.data, plan)))

    def test_dependency(self):
        plan = {"hms-test": {"env": "burst", "start": 0}}
        self.assertTrue(any("dependency" in e for e in validate(self.data, plan)))

    def test_determinism(self):
        self.assertEqual(beam(self.data), beam(self.data))
        self.assertEqual(greedy(self.data), greedy(self.data))

    def test_metrics(self):
        plan = greedy(self.data)
        self.assertLessEqual(score(self.data, plan)["tasks"], len(self.data["tasks"]))

if __name__ == "__main__":
    unittest.main()
