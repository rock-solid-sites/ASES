"""Offline discriminating tests: no external network or model-inference calls."""
import gzip
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import opencode_zen as zen


class FakeResponse:
    status = 200

    def __init__(self, payload, url=zen.URL, status=200):
        self.payload = payload
        self.url = url
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def geturl(self):
        return self.url

    def read(self, n=-1):
        return self.payload[:n]


def payload(*models):
    return json.dumps({"object": "list", "data": [{"id": x} for x in models]}).encode()


def fake(data, url=zen.URL, status=200):
    def opener(req, timeout):
        assert req.get_method() == "GET"
        assert "/models" in req.full_url
        assert timeout > 0
        return FakeResponse(data, url, status)
    return opener


class CatalogTests(unittest.TestCase):
    def test_normalization_is_canonical_across_key_order(self):
        a = b'{"data":[{"id":"model-one"}],"object":"list"}'
        b = b'{"object":"list","data":[{"id":"model-one"}]}'
        self.assertEqual(zen.normalize(a)[2], zen.normalize(b)[2])

    def test_invalid_model_list_rejected_with_valid_neighbor(self):
        self.assertEqual(zen.normalize(payload("a", "b"))[1], ["a", "b"])
        for invalid in [b'{}', b'{"data":{}}', b'{"data":[{}]}',
                        b'{"data":[{"id":"a"},{"id":"a"}]}',
                        b'{"data":[{"id":"bad id"}]}']:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    zen.normalize(invalid)

    def test_response_size_guard(self):
        with self.assertRaises(ValueError):
            zen.normalize(b" " * (zen.MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            zen.fetch_catalog(opener=fake(b"x" * (zen.MAX_BYTES + 1)))

    def test_redirect_off_provider_rejected(self):
        with self.assertRaisesRegex(ValueError, "untrusted host"):
            zen.fetch_catalog(opener=fake(payload("x"), "https://attacker.invalid/models"))
        with self.assertRaisesRegex(ValueError, "untrusted host"):
            zen.fetch_catalog(opener=fake(payload("x"), "http://opencode.ai/zen/v1/models"))
        self.assertEqual(zen.fetch_catalog(opener=fake(payload("x"))), payload("x"))

    def test_non_success_status_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTP status"):
            zen.fetch_catalog(opener=fake(payload("x"), status=503))

    def test_immutable_compressed_cache_and_diff(self):
        with TemporaryDirectory() as d:
            cache = Path(d)
            first = zen.check(cache, opener=fake(payload("a", "b")), clock=lambda: 1000)
            self.assertEqual(first["refresh"], "SUCCESS")
            self.assertEqual(first["added"], ["a", "b"])
            self.assertTrue((cache / first["archive"]).exists())
            self.assertEqual(json.loads(gzip.decompress((cache / first["archive"]).read_bytes()))["object"], "list")
            second = zen.check(cache, opener=fake(payload("b", "c")), clock=lambda: 2000, force=True)
            self.assertEqual(second["added"], ["c"])
            self.assertEqual(second["removed"], ["a"])
            self.assertTrue((cache / first["archive"]).exists())
            self.assertNotEqual(first["sha256"], second["sha256"])

    def test_fresh_cache_does_not_call_provider(self):
        with TemporaryDirectory() as d:
            cache = Path(d)
            zen.check(cache, opener=fake(payload("a")), clock=lambda: 1000)
            def should_not_call(*a, **kw):
                raise AssertionError("unnecessary provider call")
            result = zen.check(cache, opener=should_not_call, clock=lambda: 1001)
            self.assertEqual(result["refresh"], "CACHE_FRESH")

    def test_failure_does_not_delete_last_verified_catalog(self):
        with TemporaryDirectory() as d:
            cache = Path(d)
            prior = zen.check(cache, opener=fake(payload("old")), clock=lambda: 1000)
            def failing(*a, **kw):
                raise TimeoutError("provider is down")
            failed = zen.check(cache, opener=failing, clock=lambda: 200000, force=True)
            self.assertEqual(failed["refresh"], "FAILED")
            self.assertTrue(failed["prior_catalog_preserved"])
            self.assertEqual(failed["prior_digest"], prior["sha256"])
            self.assertEqual(zen.cached_manifest(cache)["sha256"], prior["sha256"])

    def test_corrupted_archive_cannot_be_reused_as_verified(self):
        with TemporaryDirectory() as d:
            cache = Path(d)
            prior = zen.check(cache, opener=fake(payload("a")), clock=lambda: 1000)
            (cache / prior["archive"]).write_bytes(b"corrupt")
            result = zen.check(cache, opener=fake(payload("a")), clock=lambda: 2000, force=True)
            self.assertEqual(result["refresh"], "FAILED")
            self.assertIn("error", result)
            self.assertEqual(zen.cached_manifest(cache)["sha256"], prior["sha256"])

    def test_controller_arguments_are_explicit(self):
        with TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "specified together"):
                zen.check(Path(d), controller="/usr/bin/controller")

    def test_cli_success_and_stale_failure_exit_codes(self):
        with TemporaryDirectory() as d:
            result = zen.check(Path(d), opener=fake(payload("model")), clock=lambda: 1000)
            self.assertEqual(result["refresh"], "SUCCESS")
            self.assertEqual(len(result["sha256"]), hashlib.sha256().digest_size * 2)


if __name__ == "__main__":
    unittest.main()
