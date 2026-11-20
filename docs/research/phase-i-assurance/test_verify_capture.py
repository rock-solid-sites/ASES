"""Adversarial independent evidence-set verification tests."""
import json
from pathlib import Path
import tempfile
import unittest
from verify_capture import CaptureMismatch, sha, verify


class CaptureVerifierTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.file=self.root/"trace.json"
        self.file.write_bytes(b'{"event":"ok"}')
        self.write_manifest()

    def write_manifest(self, entries=None):
        entries=entries if entries is not None else [
            {"path":"trace.json","size":self.file.stat().st_size,
             "sha256":sha(self.file),"capture_complete":True}]
        (self.root/"manifest.json").write_text(json.dumps({"artifacts":entries}))

    def test_valid_manifest(self):
        self.assertTrue(verify(self.root)["manifest_file_set_exact"])

    def test_tampered_bytes(self):
        self.file.write_bytes(b'{"event":"no"}')
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_unlisted_file(self):
        (self.root/"unexpected.log").write_text("unexpected")
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_missing_listed_file(self):
        self.file.unlink()
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_false_self_hash(self):
        self.write_manifest([{"path":"manifest.json","size":0,"sha256":"0"*64,
                              "capture_complete":True}])
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_duplicate_entries(self):
        row=json.loads((self.root/"manifest.json").read_text())["artifacts"][0]
        self.write_manifest([row,row])
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_invalid_digest(self):
        row=json.loads((self.root/"manifest.json").read_text())["artifacts"][0]
        self.write_manifest([{**row,"sha256":"z"*64}])
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_traversal(self):
        row=json.loads((self.root/"manifest.json").read_text())["artifacts"][0]
        self.write_manifest([{**row,"path":"../secret"}])
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_boolean_size(self):
        row=json.loads((self.root/"manifest.json").read_text())["artifacts"][0]
        self.write_manifest([{**row,"size":True}])
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_symlink(self):
        (self.root/"link").symlink_to(self.file)
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_false_capture_complete(self):
        row=json.loads((self.root/"manifest.json").read_text())["artifacts"][0]
        self.write_manifest([{**row,"capture_complete":False}])
        with self.assertRaises(CaptureMismatch):verify(self.root)

    def test_manifest_self_reference_created_before_hash(self):
        # Redirection to a manifest inside the hashed root must not make a green verification.
        row=json.loads((self.root/"manifest.json").read_text())["artifacts"][0]
        self.write_manifest([row,{"path":"manifest.json","size":0,
                                  "sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                                  "capture_complete":True}])
        with self.assertRaises(CaptureMismatch):verify(self.root)


if __name__=="__main__":
    unittest.main()
