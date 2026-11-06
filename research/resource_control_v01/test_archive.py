"""Archive-integrity positive and negative controls."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from control import Control, Rejected
from archive import archive, verify, restore


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.c=Control(self.root/"control.db")
        self.c.register_bucket(bucket_id="slot",account="acct",provider="mock",
            product="local",period="p",unit="slots",allowance=1)
        q=self.c.quote(claims={"slot":1},estimate={"kind":"test"},account="acct")
        self.c.reserve(job_id="j",attempt_id="a",quote=q,account="acct")

    def test_archive_and_restore_byte_exact(self):
        result=archive(self.c,"j",self.root/"archives",
                       artifacts={"trace.txt":b"test trace\n"*2000})
        self.assertTrue(result["verified"])
        self.assertTrue(verify(result["archive"],result["manifest"])["verified"])
        restored=restore(result["archive"],result["manifest"],self.root/"restore")
        self.assertIn("trace.txt",restored["files"])
        self.assertEqual((self.root/"restore"/"trace.txt").read_bytes(),b"test trace\n"*2000)
        self.assertLess(Path(result["archive"]).stat().st_size,len(b"test trace\n"*2000))

    def test_archive_detects_bit_corruption(self):
        r=archive(self.c,"j",self.root/"archives")
        p=Path(r["archive"])
        original=p.read_bytes()
        p.write_bytes(original[:-4]+b"FAIL")
        self.assertFalse(verify(r["archive"],r["manifest"])["verified"])
        with self.assertRaises(Rejected):restore(r["archive"],r["manifest"],self.root/"restore")

    def test_missing_manifest_is_not_verified(self):
        r=archive(self.c,"j",self.root/"archives")
        Path(r["manifest"]).unlink()
        self.assertFalse(verify(r["archive"],r["manifest"])["verified"])
        with self.assertRaises(Rejected):archive(self.c,"j",self.root/"archives")

    def test_unknown_job_does_not_claim_archival_success(self):
        with self.assertRaises(Rejected):archive(self.c,"unknown",self.root/"archives")

    def test_path_traversal_and_duplicate_reserved_entry_rejected(self):
        for key in ("../secrets","a/b","session.json","..hidden"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    archive(self.c,"j",self.root/"archives",artifacts={key:b"oops"})

    def test_nonbyte_attachment_rejected(self):
        with self.assertRaises(ValueError):
            archive(self.c,"j",self.root/"archives",artifacts={"log.txt":"not bytes"})

    def test_preserves_incomplete_job_as_it_is(self):
        r=archive(self.c,"j",self.root/"archives")
        record=json.loads((lambda z:z.read("session.json"))(
            __import__("zipfile").ZipFile(r["archive"])))
        self.assertEqual(record["job"]["job"]["state"],"RESERVED")

    def test_rearchive_after_activity_creates_new_snapshot(self):
        old=archive(self.c,"j",self.root/"archives")
        self.c.finalize("j",state="CANCELLED",event_id="e1")
        new=archive(self.c,"j",self.root/"archives")
        self.assertNotEqual(old["archive"],new["archive"])
        self.assertTrue(verify(old["archive"],old["manifest"])["verified"])
        self.assertTrue(verify(new["archive"],new["manifest"])["verified"])

    def test_archive_duplicates_safe(self):
        old=archive(self.c,"j",self.root/"archives")
        new=archive(self.c,"j",self.root/"archives")
        self.assertTrue(new["duplicate"])
        self.assertEqual(old["archive"],new["archive"])


if __name__=="__main__":
    unittest.main()
