"""Boundary tests for discovery-only agent execution routes.

No account-access, billing or launch-readiness facts are inferred.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent
CATALOG = ROOT / "candidate_inventory_v0.json"


class AgentExecutionDiscoveryCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.providers = cls.catalog["providers"]

    def test_existing_registry_is_discovery_only(self):
        self.assertIn("candidate", self.catalog["purpose"].lower())
        self.assertNotIn("active", self.catalog["purpose"].lower())

    def test_provider_ids_are_unique(self):
        ids = [p["id"] for p in self.providers]
        self.assertEqual(len(ids), len(set(ids)))

    def test_documented_routes_reference_real_products(self):
        for p in self.providers:
            with self.subTest(provider=p["id"]):
                products = set(p["products"])
                for product in (p.get("documented_execution_routes") or {}):
                    self.assertIn(product, products)

    def test_documentation_never_grants_launch_authority(self):
        for p in self.providers:
            for product, route in (p.get("documented_execution_routes") or {}).items():
                with self.subTest(provider=p["id"], product=product):
                    self.assertEqual(route["source_class"], "official_documentation")
                    self.assertTrue(route["source_url"].startswith("https://"))
                    self.assertEqual(route["account_access"], "unverified")
                    self.assertEqual(route["adapter_state"], "not_implemented")
                    self.assertEqual(route["launch_test"], "not_run")
                    self.assertRegex(route["reviewed_on"], r"^20\d{2}-\d{2}-\d{2}$")

    def test_preserve_foundational_provider_inventory(self):
        ids = {p["id"] for p in self.providers}
        for required in ("github", "gitlab", "modal", "e2b", "daytona",
                         "vercel", "cloudflare", "openai", "hostkey"):
            self.assertIn(required, ids)

    def test_inference_candidate_research_is_not_account_evidence(self):
        records = {p["id"]: p for p in self.providers}
        for required in ("groq", "cohere", "z-ai", "cerebras", "sambanova", "ollama"):
            with self.subTest(provider=required):
                record = records[required]
                self.assertEqual(record["status"], "unverified_candidate")
                self.assertIn("inference", record["roles"])
                self.assertNotIn("account_evidence", record)
                self.assertFalse(record.get("documented_execution_routes"))
        self.assertIn("payment method", records["cerebras"]["notes"])
        self.assertIn("conflicting", records["sambanova"]["notes"])
        self.assertIn("pay-per-token", records["ollama"]["notes"])

    def test_no_duplicate_fly_sprite_alias(self):
        ids = {p["id"] for p in self.providers}
        self.assertIn("fly", ids)
        self.assertNotIn("sprites-dev", ids)

    def test_enough_official_launch_routes_to_justify_probe(self):
        sources = [(p["id"], route["source_url"])
                   for p in self.providers
                   for route in (p.get("documented_execution_routes") or {}).values()]
        self.assertGreaterEqual(len(sources), 10)
        self.assertEqual(len(sources), len(set(sources)))


if __name__ == "__main__":
    unittest.main()
