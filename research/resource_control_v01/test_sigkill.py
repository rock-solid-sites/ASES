"""Checkpoint-qualified real SIGKILL recovery tests, not synthetic exceptions."""
import os
import select
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from control import Control, MockLauncher, recover_mock


CHILD = '''
import sys,time
from control import Control,MockLauncher
db,provider_db,stage=sys.argv[1:]
control=Control(db)
q=control.quote(claims={"cpu":40},estimate={"minutes":40},account="acct")
control.reserve(job_id="job",attempt_id="attempt",quote=q,account="acct")
if stage=="RESERVED":
    print("RESERVED",flush=True)
    time.sleep(90)
a=control.acknowledge("job",snapshot_digest=q["snapshot_digest"],
                      expires_at=int(time.time())+300)
if stage=="AUTHORIZED":
    print("AUTHORIZED",flush=True)
    time.sleep(90)
control.launch_prepare("job",token=a["token"])
external=MockLauncher(provider_db).launch("attempt")
if stage=="EXTERNAL":
    print("EXTERNAL",flush=True)
    time.sleep(90)
control.launch_confirm("job",external_id=external)
'''


@unittest.skipUnless(os.name=="posix" and hasattr(signal,"SIGKILL"),"SIGKILL requires POSIX")
class CrashRecovery(unittest.TestCase):
    def kill_at_checkpoint(self, stage):
        with tempfile.TemporaryDirectory() as root:
            db=Path(root)/"authority.db"
            provider=Path(root)/"provider.db"
            ctl=Control(db)
            ctl.register_bucket(bucket_id="cpu",account="acct",provider="mock",
                product="codespace",period="p",unit="core-minutes",allowance=100)
            proc=subprocess.Popen([sys.executable,"-u","-c",CHILD,
                                   str(db),str(provider),stage],
                                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                  text=True,cwd=str(Path(__file__).parent))
            try:
                ready,_,_=select.select([proc.stdout],[],[],12)
                self.assertTrue(ready,"checkpoint not reached")
                marker=proc.stdout.readline().strip()
                if marker!=stage:
                    self.fail("unexpected checkpoint: "+repr(marker)+
                              " stderr="+proc.stderr.read()[:1000])
                os.kill(proc.pid,signal.SIGKILL)
                proc.wait(timeout=8)
                self.assertEqual(proc.returncode,-signal.SIGKILL)
                recovered=Control(db)
                state=recovered.status("job")["job"]["state"]
                balance=recovered.snapshot()["buckets"][0]
                self.assertEqual(balance["reserved"],40)
                self.assertEqual(balance["local_consumed"],0)
                self.assertEqual(balance["available"],60)
                self.assertEqual(state,{
                    "RESERVED":"RESERVED","AUTHORIZED":"AUTHORIZED",
                    "EXTERNAL":"LAUNCH_PENDING"}[stage])
                if stage=="EXTERNAL":
                    ext=MockLauncher(provider)
                    self.assertEqual(recover_mock(recovered,ext)[0]["state"],"RUNNING")
                    self.assertEqual(recovered.status("job")["job"]["external_id"],
                                     ext.lookup("attempt"))
                    self.assertEqual(len(recover_mock(recovered,ext)),0)
            finally:
                if proc.poll() is None:
                    proc.kill();proc.wait(timeout=5)
                proc.stdout.close()
                proc.stderr.close()

    def test_kill_after_reservation_durable(self):
        self.kill_at_checkpoint("RESERVED")

    def test_kill_after_ack_durable(self):
        self.kill_at_checkpoint("AUTHORIZED")

    def test_kill_after_external_launch_detected(self):
        self.kill_at_checkpoint("EXTERNAL")


if __name__=="__main__":
    unittest.main()
