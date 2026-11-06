"""Real age encryption/restore, using synthetic data and an in-process fake S3 transport.

The ephemeral decryption identity never leaves this job. This verifies actual age
cryptography and backup-script compatibility, NOT authentication to R2/e2.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from test_backup_pipeline import MOCK_RCLONE

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "backup_encrypted.sh"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class AgeRestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        stub = self.bin / "rclone"
        stub.write_text(MOCK_RCLONE)
        stub.chmod(0o700)
        self.identity = self.root / "offline-ephemeral-identity.txt"
        subprocess.run(["age-keygen", "-o", str(self.identity)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.recipient = subprocess.check_output(["age-keygen", "-y", str(self.identity)], text=True).strip()
        self.second_identity = self.root / "wrong-identity.txt"
        subprocess.run(["age-keygen", "-o", str(self.second_identity)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.payload = b"ASES synthetic evidence\x00\x01\xff and a small journal\n"
        self.inner = self.root / "phase-i-evidence.tar.gz"
        with tarfile.open(self.inner, "w:gz") as archive:
            entry = tarfile.TarInfo("research/raw-evidence.bin")
            entry.size = len(self.payload)
            archive.addfile(entry, io.BytesIO(self.payload))
        # Encrypt the entire exported envelope, including failure/qualification metadata.
        self.collection = b'{"collection":"INCOMPLETE","source_artifacts":1,"expected_artifacts":22}'
        self.manifest = b'{"complete_verification":false,"verified_manifests":0}'
        self.source = self.root / "complete-evidence-export.tar.gz"
        with tarfile.open(self.source, "w:gz") as archive:
            for name, raw in (
                ("phase-i-evidence.tar.gz", self.inner.read_bytes()),
                ("collection-status.json", self.collection),
                ("manifest-status.json", self.manifest),
            ):
                entry = tarfile.TarInfo(name)
                entry.size = len(raw)
                archive.addfile(entry, io.BytesIO(raw))
        self.before_hash = sha(self.source.read_bytes())
        self.status = self.root / "backup-status"
        self.remote = self.root / "fake-s3"
        self.env = os.environ.copy()
        for key in ("E2_ENDPOINT", "E2_ACCESS_KEY_ID", "E2_SECRET_ACCESS_KEY", "E2_BUCKET",
                    "FAKE_REMOTE_TAMPER"):
            self.env.pop(key, None)
        self.env.update({
            "PATH": str(self.bin) + os.pathsep + self.env["PATH"],
            "SOURCE_COMMIT": "a" * 40,
            "RUN_ID": "24681012",
            "RUN_ATTEMPT": "1",
            "AGE_RECIPIENT": self.recipient,
            "R2_ACCOUNT_ID": "synthetic-account",
            "R2_ACCESS_KEY_ID": "synthetic-r2-access",
            "R2_SECRET_ACCESS_KEY": "synthetic-r2-secret",
            "SOURCE_TAR": str(self.source),
            "BACKUP_OUTPUT": str(self.status),
            "FAKE_REMOTE_ROOT": str(self.remote),
        })

    def run_backup(self):
        return subprocess.run(["bash", str(SCRIPT)], env=self.env,
                              capture_output=True, text=True, timeout=15)

    def restore(self, cipher, identity):
        restored = self.root / ("restored-" + identity.stem + "-" + sha(str(cipher).encode())[:12] + ".tar.gz")
        attempt = subprocess.run(["age", "-d", "-i", str(identity),
                                  "-o", str(restored), str(cipher)],
                                 capture_output=True, text=True, timeout=15)
        return attempt, restored

    def test_actual_crypto_restore_and_wrong_identity(self):
        p = self.run_backup()
        self.assertEqual(p.returncode, 0, p.stderr)
        files = list(self.remote.rglob("*.age"))
        self.assertEqual(len(files), 1)
        ciphertext = files[0].read_bytes()
        self.assertTrue(ciphertext.startswith(b"age-encryption.org/v1\n"))
        self.assertNotEqual(ciphertext, self.source.read_bytes())
        self.assertNotIn(self.payload, ciphertext)
        status = json.loads((self.status / "attestation.json").read_text())
        self.assertEqual(status["r2"], "CIPHERTEXT_READBACK_VERIFIED")
        ok, restored = self.restore(files[0], self.identity)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(sha(restored.read_bytes()), self.before_hash)
        with tarfile.open(restored, "r:gz") as tar:
            self.assertEqual(tar.extractfile("collection-status.json").read(), self.collection)
            self.assertEqual(tar.extractfile("manifest-status.json").read(), self.manifest)
            inner = tar.extractfile("phase-i-evidence.tar.gz").read()
            self.assertEqual(sha(inner), sha(self.inner.read_bytes()))
            with tarfile.open(fileobj=io.BytesIO(inner), mode="r:gz") as nested:
                self.assertEqual(nested.extractfile("research/raw-evidence.bin").read(), self.payload)
        bad, _ = self.restore(files[0], self.second_identity)
        self.assertNotEqual(bad.returncode, 0, "wrong private identity decrypted a real age ciphertext")

    def test_same_attempt_refuses_mutation_but_new_attempt_preserves_both(self):
        first = self.run_backup()
        self.assertEqual(first.returncode, 0, first.stderr)
        same = self.run_backup()
        self.assertNotEqual(same.returncode, 0, "same immutable object key was silently overwritten")
        self.env["RUN_ATTEMPT"] = "2"
        again = self.run_backup()
        self.assertEqual(again.returncode, 0, again.stderr)
        copies = list(self.remote.rglob("*.age"))
        self.assertEqual(len(copies), 2)
        self.assertEqual({p.parent.parent.name for p in copies}, {"attempt-1", "attempt-2"})
        for cipher in copies:
            result, recovered = self.restore(cipher, self.identity)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(sha(recovered.read_bytes()), self.before_hash)

    def test_real_ciphertext_rejects_tampering(self):
        self.assertEqual(self.run_backup().returncode, 0)
        file = next(self.remote.rglob("*.age"))
        mutated = self.root / "tampered.age"
        raw = bytearray(file.read_bytes())
        raw[-1] ^= 1
        mutated.write_bytes(raw)
        bad, _ = self.restore(mutated, self.identity)
        self.assertNotEqual(bad.returncode, 0, "mutated authenticated ciphertext was accepted")

    def test_two_independent_destinations_restore_identically(self):
        self.env.update({"E2_ENDPOINT": "synthetic-e2-endpoint",
                         "E2_BUCKET": "synthetic-e2-bucket",
                         "E2_ACCESS_KEY_ID": "synthetic-e2-access",
                         "E2_SECRET_ACCESS_KEY": "synthetic-e2-secret"})
        p = self.run_backup()
        self.assertEqual(p.returncode, 0, p.stderr)
        copies = list(self.remote.rglob("*.age"))
        self.assertEqual(len(copies), 2)
        self.assertEqual(sha(copies[0].read_bytes()), sha(copies[1].read_bytes()))
        for cipher in copies:
            ok, restored = self.restore(cipher, self.identity)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertEqual(sha(restored.read_bytes()), self.before_hash)
        self.assertEqual(json.loads((self.status / "attestation.json").read_text())
                         ["idrive_e2"], "CIPHERTEXT_READBACK_VERIFIED")

if __name__ == "__main__":
    unittest.main()
