"""Mock-environment assurance for encrypted R2/e2 backup script.

Mock AGE is NOT cryptography; these tests qualify the pipeline's control flow
and failure handling, not real encryption or a provider-side restore.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest

SCRIPT=Path(__file__).with_name("backup_encrypted.sh")
MOCK_AGE="""#!/usr/bin/env python3
import pathlib,sys
a=sys.argv
assert a[1]=='-r' and a[3]=='-o'
raw=pathlib.Path(a[5]).read_bytes()
pathlib.Path(a[4]).write_bytes(b'MOCK-AGE-CIPHERTEXT\\0'+raw[::-1])
"""
MOCK_RCLONE="""#!/usr/bin/env python3
import os,pathlib,sys
args=sys.argv
assert args[1] in ('copyto','cat')
base=pathlib.Path(os.environ['FAKE_REMOTE_ROOT'])
def dest(key):
    assert key.startswith(('r2:','e2:'))
    return base/key.replace(':','/',1)
if args[1]=='copyto':
    src=pathlib.Path(args[2]);target=dest(args[3])
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():sys.exit(3)
    body=src.read_bytes()
    if os.getenv('FAKE_REMOTE_TAMPER')=='1':body=b'tampered'+body
    target.write_bytes(body)
elif args[1]=='cat':
    sys.stdout.buffer.write(dest(args[2]).read_bytes())
"""

class BackupScriptTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.bin=self.root/"bin"
        self.bin.mkdir()
        for name,code in (("age",MOCK_AGE),("rclone",MOCK_RCLONE)):
            path=self.bin/name
            path.write_text(code)
            path.chmod(0o700)
        self.source=self.root/"evidence.tar.gz"
        self.source.write_bytes(b"unit test: archive contents \\x00 no secrets")
        self.output=self.root/"status"
        self.remotes=self.root/"remotes"
        self.env=os.environ.copy()
        for key in ("E2_ENDPOINT","E2_ACCESS_KEY_ID","E2_SECRET_ACCESS_KEY","E2_BUCKET",
                    "FAKE_REMOTE_TAMPER"):
            self.env.pop(key,None)
        self.env.update({
            "PATH":str(self.bin)+os.pathsep+self.env["PATH"],
            "SOURCE_COMMIT":"a"*40,
            "RUN_ID":"1234567",
            "AGE_RECIPIENT":"age1"+"q"*58,
            "R2_ACCOUNT_ID":"fixture-account",
            "R2_ACCESS_KEY_ID":"fixture-r2-id",
            "R2_SECRET_ACCESS_KEY":"fixture-r2-secret",
            "SOURCE_TAR":str(self.source),
            "BACKUP_OUTPUT":str(self.output),
            "FAKE_REMOTE_ROOT":str(self.remotes),
        })

    def run_backup(self):
        return subprocess.run(["bash",str(SCRIPT)],env=self.env,
                              text=True,capture_output=True,timeout=10)

    def test_primary_ciphertext_only_and_verified_readback(self):
        p=self.run_backup()
        self.assertEqual(p.returncode,0,p.stderr)
        status=json.loads((self.output/"attestation.json").read_text())
        self.assertEqual(status["r2"],"CIPHERTEXT_READBACK_VERIFIED")
        self.assertEqual(status["idrive_e2"],"BLOCKED_NOT_CONFIGURED")
        self.assertEqual(status["decrypt_restore"],"NOT_TESTED")
        copies=list(self.remotes.rglob("*"))
        files=[x for x in copies if x.is_file()]
        self.assertEqual(len(files),1)
        ciphertext=files[0].read_bytes()
        self.assertTrue(ciphertext.startswith(b"MOCK-AGE-CIPHERTEXT"))
        self.assertNotEqual(ciphertext,self.source.read_bytes())
        self.assertFalse((self.output/"evidence.tar.gz.age").exists())

    def test_secondary_mirror_independent_destination(self):
        self.env.update({"E2_ENDPOINT":"fixture-e2.example",
                         "E2_ACCESS_KEY_ID":"fixture-e2-id",
                         "E2_SECRET_ACCESS_KEY":"fixture-e2-secret",
                         "E2_BUCKET":"ases-secondary"})
        p=self.run_backup()
        self.assertEqual(p.returncode,0,p.stderr)
        status=json.loads((self.output/"attestation.json").read_text())
        self.assertEqual(status["idrive_e2"],"CIPHERTEXT_READBACK_VERIFIED")
        ciphertexts=[x.read_bytes() for x in self.remotes.rglob("*.age")]
        self.assertEqual(len(ciphertexts),2)
        self.assertEqual(ciphertexts[0],ciphertexts[1])

    def test_tampered_remote_fails_without_success_attestation(self):
        self.env["FAKE_REMOTE_TAMPER"]="1"
        p=self.run_backup()
        self.assertNotEqual(p.returncode,0)
        self.assertFalse((self.output/"attestation.json").exists())

    def test_missing_primary_credential_fails_closed(self):
        self.env.pop("R2_SECRET_ACCESS_KEY")
        p=self.run_backup()
        self.assertNotEqual(p.returncode,0)
        self.assertFalse((self.output/"attestation.json").exists())

    def test_incomplete_secondary_config_fails(self):
        self.env["E2_ENDPOINT"]="fixture-e2.example"
        p=self.run_backup()
        self.assertNotEqual(p.returncode,0)
        self.assertFalse((self.output/"attestation.json").exists())

    def test_invalid_recipient_fails_before_upload(self):
        self.env["AGE_RECIPIENT"]="not-a-valid-age-recipient"
        p=self.run_backup()
        self.assertNotEqual(p.returncode,0)
        self.assertFalse(self.remotes.exists())

    def test_max_size_prevents_unbounded_upload(self):
        with self.source.open("wb") as f:
            f.truncate(50000001)
        p=self.run_backup()
        self.assertNotEqual(p.returncode,0)
        self.assertFalse(self.remotes.exists())

if __name__=="__main__":
    unittest.main()
