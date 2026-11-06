"""Deterministic generated invariant checks over resource accounting histories."""
import random
import tempfile
import time
import unittest
from pathlib import Path
from control import Control, Rejected


class GeneratedHistories(unittest.TestCase):
    def test_80_seeded_multi_job_histories_preserve_accounting(self):
        with tempfile.TemporaryDirectory() as temp:
            for seed in range(80):
                with self.subTest(seed=seed):
                    randomizer=random.Random(seed)
                    db=Path(temp)/(str(seed)+".db")
                    ctl=Control(db)
                    ctl.register_bucket(bucket_id="cpu",account="acct",provider="mock",
                        product="env",period="p",unit="core-minutes",allowance=250)
                    ctl.register_bucket(bucket_id="slot",account="acct",provider="mock",
                        product="env",period="p",unit="slots",allowance=2,kind="CONCURRENT")
                    consumed=0
                    for i in range(6):
                        n=randomizer.randrange(1,25)
                        q=ctl.quote(claims={"cpu":n,"slot":1},
                                    estimate={"minutes":n},account="acct")
                        self.assertTrue(q["eligible"])
                        ctl.reserve(job_id="j"+str(i),attempt_id="a"+str(i),
                                    quote=q,account="acct")
                        view={b["id"]:b for b in ctl.snapshot()["buckets"]}
                        self.assertEqual(view["slot"]["available"],1)
                        self.assertEqual(view["cpu"]["reserved"],n)
                        self.assertEqual(view["cpu"]["available"]+view["cpu"]["reserved"]+
                                         view["cpu"]["local_consumed"],250)
                        if randomizer.randrange(3)==0:
                            ctl.finalize("j"+str(i),state="CANCELLED",event_id="done"+str(i))
                        else:
                            q_used=randomizer.randrange(0,n+1)
                            # The synthetic job was admitted and observed; it need not call a real provider.
                            token=ctl.acknowledge("j"+str(i),
                                snapshot_digest=q["snapshot_digest"],
                                expires_at=int(time.time())+3000)["token"]
                            ctl.launch_prepare("j"+str(i),token=token)
                            ctl.launch_confirm("j"+str(i),external_id="mock"+str(i))
                            ctl.observe("j"+str(i),event_id="use"+str(i),
                                        bucket_id="cpu",cumulative=q_used)
                            ctl.finalize("j"+str(i),state="COMPLETED",
                                         event_id="done"+str(i),stop_evidence="mock shutdown")
                            consumed+=q_used
                        view={b["id"]:b for b in ctl.snapshot()["buckets"]}
                        self.assertEqual(view["cpu"]["local_consumed"],consumed)
                        self.assertEqual(view["cpu"]["reserved"],0)
                        self.assertEqual(view["cpu"]["available"],250-consumed)
                        self.assertEqual(view["slot"]["reserved"],0)
                        self.assertEqual(view["slot"]["available"],2)

    def test_50_randomized_provider_overlap_reconciliation(self):
        with tempfile.TemporaryDirectory() as temp:
            for seed in range(50):
                with self.subTest(seed=seed):
                    rnd=random.Random(seed+1000)
                    local=rnd.randint(0,80)
                    provider=rnd.randint(0,80)
                    overlap=rnd.randint(0,min(local,provider))
                    ctl=Control(Path(temp)/(str(seed)+".db"))
                    ctl.register_bucket(bucket_id="cpu",account="a",provider="p",
                        product="x",period="m",unit="tokens",allowance=250)
                    if local:
                        quote=ctl.quote(claims={"cpu":local},estimate={},account="a")
                        ctl.reserve(job_id="j",attempt_id="attempt",quote=quote,account="a")
                        ack=ctl.acknowledge("j",snapshot_digest=quote["snapshot_digest"],
                                            expires_at=int(time.time())+3000)
                        ctl.launch_prepare("j",token=ack["token"])
                        ctl.launch_confirm("j",external_id="mock")
                        ctl.observe("j",event_id="usage",bucket_id="cpu",cumulative=local)
                        ctl.finalize("j",state="COMPLETED",event_id="done",stop_evidence="stop")
                    ctl.provider_report(report_id="report",bucket_id="cpu",cumulative=provider,
                        observed_at=int(time.time())+1,covered_local=overlap,
                        coverage_evidence="synthetic matched receipts" if overlap else None)
                    b=ctl.snapshot()["buckets"][0]
                    self.assertEqual(b["available"],250-(local+provider-overlap))
                    self.assertEqual(b["reserved"],0)


if __name__=="__main__":
    unittest.main()
