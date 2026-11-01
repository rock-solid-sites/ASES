"""Discrete account/provider/product/period/unit admission tests."""
import concurrent.futures
import unittest
from allowance_ledger_v1 import Bucket, Claim, Ledger
A = Bucket("rss", "github", "codespaces", "2026-11", "core-hours")
B = Bucket("mbd", "github", "codespaces", "2026-11", "core-hours")
C = Bucket("rss", "modal", "compute", "2026-11", "credits")
D = Bucket("rss", "github", "codespaces", "2026-12", "core-hours")
class AllowanceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger({k: {"limit": 10, "reserve": 2} for k in (A, B, C, D)})
    def test_distinct_accounts(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 8)])[0])
        self.assertEqual(self.ledger.snapshot()["available"][B], 8)
    def test_distinct_provider(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 8)])[0])
        self.assertEqual(self.ledger.snapshot()["available"][C], 8)
    def test_distinct_period(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 8)])[0])
        self.assertEqual(self.ledger.snapshot()["available"][D], 8)
    def test_no_cross_bucket_substitution(self):
        self.assertFalse(self.ledger.admit("p", 0, [Claim(A, 9)])[0])
    def test_exact_limit(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 8)])[0])
    def test_duplicate_claims_aggregate(self):
        self.assertFalse(self.ledger.admit("p", 0, [Claim(A, 5), Claim(A, 4)])[0])
    def test_multi_bucket_atomic_rollback(self):
        self.assertFalse(self.ledger.admit("p", 0, [Claim(A, 5), Claim(B, 9)])[0])
        self.assertEqual(self.ledger.snapshot()["available"][A], 8)
        self.assertEqual(self.ledger.snapshot()["version"], 0)
    def test_stale_version(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 1)])[0])
        self.assertFalse(self.ledger.admit("q", 0, [Claim(A, 1)])[0])
    def test_duplicate_id(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 1)])[0])
        self.assertFalse(self.ledger.admit("p", 1, [Claim(A, 1)])[0])
    def test_release(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 5)])[0])
        self.assertTrue(self.ledger.release("p", 1)[0])
        self.assertEqual(self.ledger.snapshot()["available"][A], 8)
    def test_release_stale(self):
        self.assertTrue(self.ledger.admit("p", 0, [Claim(A, 5)])[0])
        self.assertFalse(self.ledger.release("p", 0)[0])
    def test_invalid_amounts(self):
        for amount in (0, -1, True, 1.5):
            self.assertFalse(self.ledger.admit("p", 0, [Claim(A, amount)])[0])
    def test_unknown_bucket(self):
        self.assertFalse(self.ledger.admit("p", 0, [Claim(Bucket("rss", "github", "codespaces", "2027-01", "core-hours"), 1)])[0])
    def test_concurrent_cas_single_winner(self):
        def attempt(i):
            return self.ledger.admit(f"p{i}", 0, [Claim(A, 8)])[0]
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            outcomes = list(pool.map(attempt, range(100)))
        self.assertEqual(sum(outcomes), 1)
        self.assertEqual(self.ledger.snapshot()["available"][A], 0)
    def test_concurrent_independent_buckets_still_serialized(self):
        def attempt(args):
            i, bucket = args
            while True:
                v = self.ledger.snapshot()["version"]
                ok, why = self.ledger.admit(f"p{i}", v, [Claim(bucket, 1)])
                if ok or why != "stale snapshot":
                    return ok
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            outcomes = list(pool.map(attempt, [(i, A if i % 2 == 0 else B) for i in range(40)]))
        self.assertEqual(sum(outcomes), 16)
    def test_bad_budget(self):
        with self.assertRaises(ValueError):
            Ledger({A: {"limit": 1, "reserve": 2}})
if __name__ == "__main__":
    unittest.main()
