"""Mutation checks for account/workstream/billing separation."""
import copy
import unittest
from account_attribution_v1 import read, validate, classify_event


def example(data):
    return {
        "workstream_id": "hms",
        "execution_account_id": "github-rss",
        "api_actor_account_id": "github-mbd",
        "repository_owner_account_id": "github-rss",
        "billing_account_id": None,
        "repository": "rock-solid-sites/HMS",
        "product_id": "actions",
        "meter_id": "runner_minutes",
        "billing_period": "2026-11",
        "amount": 3,
        "unit": "minutes",
        "observation_source": "test_fixture_not_actual_usage",
        "observed_at": "2026-11-12T20:00:00Z",
        "correlation_id": "test-hms-001"
    }


class AccountAttributionContract(unittest.TestCase):
    def setUp(self):
        self.data = read()

    def test_registry_validates_without_real_usage(self):
        self.assertTrue(validate(self.data))
        self.assertEqual(self.data["usage_events"], [])

    def test_connected_and_planned_accounts_remain_distinct(self):
        by_id = {x["id"]: x for x in self.data["accounts"]}
        for live in ("github-rss", "github-mbd", "github-tripn"):
            self.assertEqual(by_id[live]["identity_state"], "connector_observed")
        for planned in ("github-ases-planned", "github-hms-planned"):
            self.assertEqual(by_id[planned]["identity_state"], "planned")
            self.assertIsNone(by_id[planned]["public_handle"])

    def test_repo_owner_is_not_workstream(self):
        repos = {x["full_name"]: x for x in self.data["repositories"]}
        self.assertEqual(repos["rock-solid-sites/HMS"]["workstream_id"], "hms")
        self.assertEqual(repos["rock-solid-sites/HMS"]["repository_owner_account_id"], "github-rss")
        self.assertEqual(repos["rock-solid-sites/ASES"]["workstream_id"], "ases")
        self.assertEqual(repos["rock-solid-sites/ASES"]["repository_owner_account_id"], "github-rss")

    def test_unknown_biller_must_not_be_silently_attributed_to_repo_owner(self):
        e = example(self.data)
        self.assertEqual(classify_event(e, self.data), "unallocated")
        self.assertIsNone(e["billing_account_id"])

    def test_billing_is_distinct_explicit_role(self):
        e = example(self.data)
        e["billing_account_id"] = "github-mbd"
        self.assertEqual(classify_event(e, self.data), "account_bound_but_unverified")
        self.assertNotEqual(e["billing_account_id"], e["repository_owner_account_id"])

    def test_planned_account_cannot_be_used_for_execution(self):
        e = example(self.data)
        e["execution_account_id"] = "github-hms-planned"
        with self.assertRaises(AssertionError):
            classify_event(e, self.data)

    def test_planned_account_cannot_be_biller(self):
        e = example(self.data)
        e["billing_account_id"] = "github-hms-planned"
        with self.assertRaises(AssertionError):
            classify_event(e, self.data)

    def test_repository_owner_mismatch_is_not_silent(self):
        e = example(self.data)
        e["repository_owner_account_id"] = "github-mbd"
        with self.assertRaises(AssertionError):
            classify_event(e, self.data)

    def test_missing_account_ref_is_not_valid(self):
        e = example(self.data)
        e["execution_account_id"] = "unknown-account"
        with self.assertRaises(AssertionError):
            classify_event(e, self.data)

    def test_duplicate_account_rejected(self):
        x = copy.deepcopy(self.data)
        x["accounts"].append(copy.deepcopy(x["accounts"][0]))
        with self.assertRaises(AssertionError):
            validate(x)

    def test_invalid_parent_cycle_rejected(self):
        x = copy.deepcopy(self.data)
        next(w for w in x["workstreams"] if w["id"] == "rss")["parent_id"] = "hms"
        with self.assertRaises(AssertionError):
            validate(x)

    def test_secret_value_field_rejected(self):
        x = copy.deepcopy(self.data)
        x["accounts"][0]["api_key"] = "test-secret-never-commit"
        with self.assertRaises(AssertionError):
            validate(x)

    def test_usage_event_requires_all_attribution_fields(self):
        e = example(self.data)
        del e["billing_account_id"]
        with self.assertRaises(AssertionError):
            classify_event(e, self.data)


if __name__ == "__main__":
    unittest.main()
