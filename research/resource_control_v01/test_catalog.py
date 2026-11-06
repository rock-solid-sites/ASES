"""Provider catalog invariants: changed data, no inference, failures not removals."""
import json
import tempfile
import unittest
from pathlib import Path
from catalog import CatalogMonitor, normalized_models
from control import Rejected


def response(items, status=200, etag="v1"):
    return lambda url, old_etag, old_modified: (
        status,{"ETag":etag},json.dumps({"models":items}).encode())


def model(id,free=True,unlimited=None,price=0):
    return {"id":id,"free":free,"unlimited_advertised":unlimited,
            "price_micros_per_million":price,"context_tokens":128000}


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.c=CatalogMonitor(Path(self.tmp.name)/"catalog.db")
        self.c.register("zen","https://example.invalid/models",ttl_seconds=1000)

    def test_initial_models_and_free_status(self):
        r=self.c.refresh("zen",fetcher=response([model("freeA"),model("paidB",False,price=15)]),now=100)
        self.assertEqual(r["status"],"CHANGED")
        self.assertEqual(r["diff"]["added"],["freeA","paidB"])
        self.assertFalse(self.c.state("zen",now=101)["stale"])

    def test_changed_limits_prices_and_unlimited_are_detected(self):
        self.c.refresh("zen",fetcher=response([model("a",unlimited=True)]),now=100)
        r=self.c.refresh("zen",fetcher=response([model("a",unlimited=False,price=10)]),now=102)
        self.assertEqual(r["diff"]["changed"],["a"])
        self.assertEqual(r["status"],"CHANGED")

    def test_removed_model_detected_only_after_valid_catalog(self):
        self.c.refresh("zen",fetcher=response([model("a"),model("b")]),now=100)
        result=self.c.refresh("zen",fetcher=response([model("b")]),now=110)
        self.assertEqual(result["diff"]["removed"],["a"])

    def test_failed_fetch_preserves_previous_catalog(self):
        self.c.refresh("zen",fetcher=response([model("a")]),now=100)
        def broken(*args):raise OSError("provider outage")
        self.assertEqual(self.c.refresh("zen",fetcher=broken,now=200)["status"],"FETCH_ERROR")
        state=self.c.state("zen",now=200)
        self.assertIn("a",state["models"])
        self.assertEqual(state["last_error"],"provider outage")
        self.assertEqual(self.c.history("zen")[-1]["kind"],"FETCH_ERROR")

    def test_304_without_previous_is_failure_not_empty(self):
        r=self.c.refresh("zen",fetcher=lambda *args:(304,{},b""),now=100)
        self.assertEqual(r["status"],"FETCH_ERROR")
        self.assertIsNone(self.c.state("zen",now=100)["models"])

    def test_304_uses_cached_model_list(self):
        self.c.refresh("zen",fetcher=response([model("a")]),now=100)
        r=self.c.refresh("zen",fetcher=lambda *args:(304,{},b""),now=200)
        self.assertEqual(r["status"],"NOT_MODIFIED")
        self.assertEqual(len(self.c.state("zen",now=200)["models"]),1)

    def test_stale_ttl_and_recovery(self):
        self.c.refresh("zen",fetcher=response([model("a")]),now=100)
        self.assertTrue(self.c.state("zen",now=1101)["stale"])
        self.c.refresh("zen",fetcher=response([model("a")]),now=1102)
        self.assertFalse(self.c.state("zen",now=1102)["stale"])

    def test_invalid_model_id_retains_old(self):
        self.c.refresh("zen",fetcher=response([model("a")]),now=100)
        invalid=self.c.refresh("zen",fetcher=response([model("bad model")]),now=101)
        self.assertEqual(invalid["status"],"FETCH_ERROR")
        self.assertIn("a",self.c.state("zen",now=101)["models"])

    def test_duplicate_model_id_rejected(self):
        self.assertEqual(self.c.refresh("zen",fetcher=response([model("a"),model("a")]),now=100)["status"],"FETCH_ERROR")

    def test_unknown_free_status_not_assumed_free(self):
        self.c.refresh("zen",fetcher=response([model("a",free=None)]),now=100)
        self.assertIsNone(self.c.state("zen",now=100)["models"]["a"]["free"])

    def test_unlimited_advertised_not_capacity_assurance(self):
        self.c.refresh("zen",fetcher=response([model("a",unlimited=True)]),now=100)
        entry=self.c.state("zen",now=100)["models"]["a"]
        self.assertTrue(entry["unlimited_advertised"])
        self.assertNotIn("remaining_requests",entry)

    def test_non_https_catalog_rejected(self):
        with self.assertRaises(ValueError):
            self.c.register("bad","http://insecure.invalid/models")

    def test_oversized_catalog_fails_without_data_loss(self):
        self.c.refresh("zen",fetcher=response([model("a")]),now=100)
        r=self.c.refresh("zen",fetcher=lambda *args:(200,{},b" "*5_000_001),now=101)
        self.assertEqual(r["status"],"FETCH_ERROR")
        self.assertIn("a",self.c.state("zen",now=102)["models"])

    def test_out_of_order_fetch_does_not_overwrite(self):
        self.c.refresh("zen",fetcher=response([model("a")]),now=300)
        r=self.c.refresh("zen",fetcher=response([model("old")]),now=200)
        self.assertEqual(r["status"],"STALE_FETCH_DISCARDED")
        self.assertIn("a",self.c.state("zen",now=301)["models"])

    def test_vendor_schema_requires_explicit_adapter(self):
        vendor={"data":[{"name":"a"}]}
        result=self.c.refresh("zen",fetcher=lambda *args:(200,{},json.dumps(vendor).encode()),now=100)
        self.assertEqual(result["status"],"FETCH_ERROR")
        def adapt(value):
            return {"models":[{"id":row["name"],"free":None} for row in value["data"]]}
        result=self.c.refresh("zen",fetcher=lambda *args:(200,{},json.dumps(vendor).encode()),
                              adapter=adapt,now=101)
        self.assertEqual(result["status"],"CHANGED")


if __name__=="__main__":
    unittest.main()
