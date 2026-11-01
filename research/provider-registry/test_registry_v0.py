import unittest
from registry_v0 import Registry
T = "2026-11-01T12:00:00Z"

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.r = Registry()
        self.k = self.r.discover("example", "cloud", "official-documentation")

    def configured(self):
        self.r.configure(self.k, "account-1", "operator", T)

    def verified(self):
        self.configured()
        self.r.verify(self.k, 1, {"plan": "basic"}, "provider-account-api", "operator", T)

    def active(self):
        self.verified()
        self.r.transition(self.k, "active", "operator", T)

    def test_discovery_not_schedulable(self):
        self.assertFalse(self.r.eligible(self.k))
        self.assertEqual(self.r.operational, {})

    def test_configured_not_schedulable(self):
        self.configured()
        self.assertFalse(self.r.eligible(self.k))

    def test_verified_not_schedulable(self):
        self.verified()
        self.assertFalse(self.r.eligible(self.k))

    def test_active_schedulable(self):
        self.active()
        self.assertTrue(self.r.eligible(self.k))

    def test_active_without_verification_rejected(self):
        self.configured()
        self.assertRaises(ValueError, self.r.transition, self.k, "active", "operator", T)

    def test_missing_account_evidence_rejected(self):
        self.configured()
        self.assertRaises(ValueError, self.r.verify, self.k, 1, {}, "api", "operator", T)

    def test_wrong_revision_rejected(self):
        self.configured()
        self.assertRaises(ValueError, self.r.verify, self.k, 2, {"plan": "a"}, "api", "operator", T)

    def test_catalog_change_revokes_eligibility(self):
        self.active()
        self.r.change_catalog(self.k, "operator", T)
        self.assertFalse(self.r.eligible(self.k))

    def test_catalog_change_requires_new_verification(self):
        self.active()
        self.r.change_catalog(self.k, "operator", T)
        self.assertRaises(ValueError, self.r.verify, self.k, 1, {"plan": "a"}, "api", "operator", T)
        self.r.verify(self.k, 2, {"plan": "a"}, "api", "operator", T)
        self.r.transition(self.k, "active", "operator", T)
        self.assertTrue(self.r.eligible(self.k))

    def test_degraded_blocks(self):
        self.active()
        self.r.transition(self.k, "degraded", "operator", T)
        self.assertFalse(self.r.eligible(self.k))

    def test_draining_blocks(self):
        self.active()
        self.r.transition(self.k, "draining", "operator", T)
        self.assertFalse(self.r.eligible(self.k))

    def test_retired_blocks(self):
        self.active()
        self.r.transition(self.k, "draining", "operator", T)
        self.r.transition(self.k, "retired", "operator", T)
        self.assertFalse(self.r.eligible(self.k))
        self.assertRaises(ValueError, self.r.transition, self.k, "active", "operator", T)

    def test_unused_candidate_discard(self):
        self.r.discard_candidate(self.k)
        self.assertNotIn(self.k, self.r.candidates)

    def test_configured_candidate_cannot_discard(self):
        self.configured()
        self.assertRaises(ValueError, self.r.discard_candidate, self.k)

    def test_historical_assignment_survives_retirement(self):
        self.active()
        self.r.assign("job-1", self.k)
        self.r.transition(self.k, "draining", "operator", T)
        self.r.transition(self.k, "retired", "operator", T)
        self.assertEqual(self.r.assignments["job-1"], self.k)

    def test_duplicate_assignment_rejected(self):
        self.active()
        self.r.assign("job-1", self.k)
        self.assertRaises(ValueError, self.r.assign, "job-1", self.k)

    def test_assignment_denied_when_degraded(self):
        self.active()
        self.r.transition(self.k, "degraded", "operator", T)
        self.assertRaises(ValueError, self.r.assign, "job-1", self.k)

    def test_invalid_timestamp_rejected(self):
        self.assertRaises(ValueError, self.r.configure, self.k, "account", "actor", "2026-11-01")

    def test_unknown_candidate_rejected(self):
        self.assertRaises(ValueError, self.r.configure, ("missing", "product"), "account", "actor", T)

    def test_duplicate_configure_rejected(self):
        self.configured()
        self.assertRaises(ValueError, self.r.configure, self.k, "account", "actor", T)

    def test_events_preserved(self):
        self.active()
        self.assertEqual([event[1] for event in self.r.events], ["configured", "verified", "active"])

if __name__ == "__main__":
    unittest.main()
