"""Fail-closed snapshot preflight regression cases."""
import copy
import unittest
from portfolio_harness_v0 import fixture
from portfolio_oracle_v1 import validate

class SnapshotPreflightTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()

    def reject(self, mutation, expected):
        data = copy.deepcopy(self.data)
        mutation(data)
        errors = validate(data, {})
        self.assertTrue(any(expected in e for e in errors), errors)

    def test_invalid_unused_account(self):
        self.reject(lambda d: d["accounts"]["mbd"].update(credits=-1), "invalid account budget")

    def test_unused_account_reserve_exceeds_credits(self):
        self.reject(lambda d: d["accounts"]["mbd"].update(reserve=999), "invalid account budget")

    def test_invalid_unused_environment(self):
        self.reject(lambda d: d["environments"]["mbd-cloud"].update(cpu=0), "invalid environment capacity")

    def test_unknown_environment_owner(self):
        self.reject(lambda d: d["environments"]["mbd-cloud"].update(account="missing"), "unknown account owner")

    def test_invalid_unused_task(self):
        self.reject(lambda d: d["tasks"][0].update(duration=0), "invalid task definition")

    def test_unknown_task_dependency(self):
        self.reject(lambda d: d["tasks"][0].update(deps=["missing"]), "invalid task definition")

    def test_invalid_mode(self):
        self.reject(lambda d: d["tasks"][0].update(modes=["missing"]), "invalid task definition")

    def test_boolean_demand_rejected(self):
        self.reject(lambda d: d["tasks"][0].update(cpu=True), "invalid task definition")

    def test_invalid_period_on_unused_account(self):
        self.reject(lambda d: d["accounts"]["mbd"].update(period=0), "invalid account budget")

if __name__ == "__main__":
    unittest.main()
