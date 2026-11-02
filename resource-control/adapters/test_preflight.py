"""Deterministic preflight exception classification; no live provider access."""
import unittest
import preflight


class PreflightTests(unittest.TestCase):
    def test_no_exceptions_with_current_complete_readings(self):
        out=preflight.classify({
            "catalog_version":5,
            "balances":[{"meter_id":"core","fresh":True,"available":30,
                         "provider_reported":10}]
        },[{"provider":"opencode-zen","fresh":True,"last_error":None}],
        {"refresh":"SUCCESS"})
        self.assertEqual(out["exceptions"],[])
        self.assertEqual(out["authorization"],"NOT_GRANTED_BY_PREFLIGHT")
        self.assertTrue(out["launch_requires_revision_bound_reservation"])

    def test_stale_and_overdrawn_resources_flagged_without_fabricated_balance(self):
        out=preflight.classify({
            "catalog_version":7,
            "balances":[
                {"meter_id":"one","fresh":False,"available":10,"provider_reported":None},
                {"meter_id":"two","fresh":True,"available":-8,"provider_reported":100}]
        },[{"provider":"opencode-zen","fresh":False,"last_error":"offline"}],
        {"refresh":"FAILED","error":"timeout"})
        kinds=[x["kind"] for x in out["exceptions"]]
        self.assertEqual(kinds,[
            "STALE_ENTITLEMENT","PROVIDER_USAGE_UNOBSERVED",
            "RESOURCE_DEFICIT","STALE_MODEL_CATALOG",
            "CATALOG_FETCH_FAILURE","CATALOG_REFRESH_FAILED"])
        self.assertEqual(out["resource_catalog_version"],7)
        self.assertEqual(out["exceptions"][2]["units"],8)

    def test_missing_catalog_and_no_balance_are_not_marked_as_healthy_by_fiat(self):
        out=preflight.classify({"catalog_version":None,"balances":[]},[],{"refresh":"FAILED"})
        self.assertEqual(out["authorization"],"NOT_GRANTED_BY_PREFLIGHT")
        self.assertEqual(out["exceptions"][0]["kind"],"CATALOG_REFRESH_FAILED")


if __name__=="__main__":
    unittest.main()
