"""Validate account and promotional-offer inventories with only Python stdlib.
These are static snapshot checks, not live balance/API verification.
Run: python -m unittest discover -s research/provider-registry -p 'test_inventory_v1.py'
"""
import copy
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).parent

def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))

def validate_known(doc):
    assert doc["schema_version"] == 1 and doc["kind"] == "known_accounts"
    ids = set()
    for r in doc["records"]:
        assert r["id"] not in ids
        ids.add(r["id"])
        assert r["account_evidence"]["status"] in ("user_confirmed", "tool_observed", "user_reported")
        if r["usage"]["status"] == "unknown":
            assert r["usage"]["observed_at"] is None
            for m in r["usage"]["meters"]:
                assert m["granted"] is None and m["consumed"] is None and m["remaining"] is None
        for c in r["claims"]:
            assert type(c["value"]) in (int, float) and c["value"] >= 0
            assert c["scope"] in ("account_reported", "provider_advertised", "historical_advertisement", "historical_estimate", "historical_user_report")
            if c["scope"] != "account_reported":
                assert c["verified_for_current_account"] is False
    return True

def validate_offers(doc):
    assert doc["schema_version"] == 1 and doc["kind"] == "potential_offers"
    ids = set()
    for r in doc["records"]:
        assert r["id"] not in ids
        ids.add(r["id"])
        assert r["redemption_status"] in ("not_redeemed", "not_applicable")
        assert r["eligibility_status"] == "not_assessed"
        assert r["offer_current_status"] == "not_rechecked"
        c = r["credit"]
        assert c["awarded_usd"] is None and c["consumed_usd"] is None and c["remaining_usd"] is None
        for f in ("advertised_usd", "conditional_max_usd"):
            assert c[f] is None or type(c[f]) in (int, float) and c[f] >= 0
        if c["conditional_max_usd"] is not None:
            assert c["advertised_usd"] is not None and c["conditional_max_usd"] >= c["advertised_usd"]
        if r["discount_percent"] is not None:
            assert 0 < r["discount_percent"] < 100
        scenario = r["compute_equivalent_scenario"]
        if scenario is not None:
            assert scenario["includes_provider_price_verification"] is False
            if "nominal_hours_min" in scenario:
                assert scenario["nominal_hours_min"] <= scenario["nominal_hours_max"]
    return True

class InventoryContract(unittest.TestCase):
    def setUp(self):
        self.known = read("known_accounts_v1.json")
        self.offers = read("potential_offers_v1.json")

    def test_snapshots_validate(self):
        self.assertTrue(validate_known(self.known))
        self.assertTrue(validate_offers(self.offers))

    def test_source_row_preservation(self):
        self.assertEqual(len(self.known["records"]), 29)
        self.assertEqual(len(self.offers["records"]), 26)

    def test_new_operator_accounts_and_quota_claims(self):
        accounts = {r["id"]: r for r in self.known["records"]}
        northflank = accounts["northflank"]
        self.assertEqual(northflank["account_evidence"]["status"], "user_confirmed")
        self.assertIsNone(northflank["account_evidence"]["last_live_verified_at"])
        self.assertEqual(northflank["usage"]["status"], "unknown")

        openrouter = accounts["openrouter"]
        monthly = [c for c in openrouter["claims"] if c["metric"] == "operator_reported_monthly_credit"]
        self.assertEqual(len(monthly), 1)
        self.assertEqual(monthly[0]["value"], 5)
        self.assertEqual(monthly[0]["period"], "monthly")
        self.assertEqual(monthly[0]["scope"], "account_reported")
        self.assertIsNone(monthly[0]["verified_for_current_account"])
        self.assertTrue(all(m["remaining"] is None for m in openrouter["usage"]["meters"]))

        nvidia = accounts["nvidia"]
        self.assertEqual(nvidia["account_evidence"]["status"], "user_confirmed")
        self.assertIn("NIM API key", nvidia["account_evidence"]["notes"])
        self.assertEqual(nvidia["usage"]["status"], "unknown")

    def test_paid_opencode_go_is_distinct_from_free_cli_route(self):
        accounts = {r["id"]: r for r in self.known["records"]}
        opencode = accounts["opencode"]
        self.assertEqual(opencode["account_evidence"]["status"], "user_confirmed")
        active_go = [c for c in opencode["claims"] if c["metric"] == "opencode_go_paid_subscription"]
        self.assertEqual(len(active_go), 1)
        self.assertIs(active_go[0]["value"], True)
        self.assertIsNone(active_go[0]["verified_for_current_account"])
        self.assertEqual(opencode["usage"]["status"], "unknown")
        self.assertIn("free variants are CLI-only", opencode["offering_summary"])

    def test_no_account_usage_mistaken_for_zero(self):
        for record in self.known["records"]:
            self.assertEqual(record["usage"]["status"], "unknown")
            for meter in record["usage"]["meters"]:
                self.assertIsNone(meter["consumed"])
                self.assertIsNone(meter["remaining"])

    def test_no_promotional_credit_assumed_awarded(self):
        for record in self.offers["records"]:
            self.assertIsNone(record["credit"]["awarded_usd"])
            self.assertIsNone(record["credit"]["remaining_usd"])

    def test_distinct_actual_vs_potential(self):
        known_ids = {r["id"] for r in self.known["records"]}
        self.assertIn("github", known_ids)
        self.assertIn("modal", known_ids)
        self.assertIn("aws-activate-hms", {r["id"] for r in self.offers["records"]})

    def test_reject_unknown_usage_claimed_zero(self):
        altered = copy.deepcopy(self.known)
        altered["records"][0]["usage"]["meters"][0]["remaining"] = 0
        with self.assertRaises(AssertionError):
            validate_known(altered)

    def test_reject_promotional_award_without_evidence(self):
        altered = copy.deepcopy(self.offers)
        altered["records"][0]["credit"]["awarded_usd"] = 100
        with self.assertRaises(AssertionError):
            validate_offers(altered)

    def test_reject_duplicate_record(self):
        altered = copy.deepcopy(self.known)
        altered["records"].append(copy.deepcopy(altered["records"][0]))
        with self.assertRaises(AssertionError):
            validate_known(altered)

    def test_reject_bad_scenario_quote_claim(self):
        altered = copy.deepcopy(self.offers)
        first = next(x for x in altered["records"] if x["compute_equivalent_scenario"] is not None)
        first["compute_equivalent_scenario"]["includes_provider_price_verification"] = True
        with self.assertRaises(AssertionError):
            validate_offers(altered)

if __name__ == "__main__":
    unittest.main()
