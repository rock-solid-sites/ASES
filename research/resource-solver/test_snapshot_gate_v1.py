"""Snapshot gate RED/GREEN and concurrency regression tests."""
import copy
import unittest
from concurrent.futures import ThreadPoolExecutor
from snapshot_gate_v1 import AdmissionGate, fingerprint
from allowance_admission_v2 import Bucket, Claim

B=Bucket("rss","github","codespaces","2026-11","core-hours")
def snapshot():
    return {"allowance_period":"2026-11","horizon":5,"accounts":{"rss":{"credits":8,"reserve":0}},
            "policy":{"p":["rss"]},
            "environments":{"cloud":{"account":"rss","cpu":4,"ram":8,"slots":1}},
            "tasks":[{"id":"job","project":"p","duration":2,"cpu":1,"ram":1,
                      "deadline":5,"modes":["cloud"],"deps":[],
                      "mode_overrides":{"cloud":{"credits":3,"allowance":dict(vars(B))}}}]}
PLAN={"job":{"env":"cloud","start":0}}
class GateTests(unittest.TestCase):
    def setUp(self): self.g=AdmissionGate(snapshot(),{B:{"limit":8,"reserve":0}})
    def test_fresh_plan(self):
        self.assertTrue(self.g.admit("x",0,snapshot(),PLAN)[0])
        self.assertEqual(self.g.balances()["available"][B],5)
    def test_stale_policy(self):
        s=snapshot();s["policy"]["p"]=[]
        self.assertTrue(self.g.update_snapshot(0,s)[0])
        self.assertFalse(self.g.admit("x",0,snapshot(),PLAN)[0])
        self.assertEqual(self.g.balances()["available"][B],8)
    def test_current_revoked_policy(self):
        s=snapshot();s["policy"]["p"]=[]
        self.g.update_snapshot(0,s)
        self.assertFalse(self.g.admit("x",1,s,PLAN)[0])
    def test_stale_quota_revision(self):
        self.g.admit("x",0,snapshot(),PLAN)
        self.assertFalse(self.g.admit("y",0,snapshot(),PLAN)[0])
    def test_mutated_snapshot_not_accepted(self):
        s=snapshot();s["tasks"][0]["mode_overrides"]["cloud"]["credits"]=1
        self.assertFalse(self.g.admit("x",0,s,PLAN)[0])
    def test_mutated_plan_no_admission(self):
        p=copy.deepcopy(PLAN);p["job"]["start"]=-1
        self.assertFalse(self.g.admit("x",0,snapshot(),p)[0])
    def test_fingerprint_order_independent(self):
        self.assertEqual(fingerprint(snapshot()),fingerprint(copy.deepcopy(snapshot())))
    def test_update_no_mutation(self):
        s=snapshot();self.g.update_snapshot(0,s);s["policy"]["p"]=[]
        self.assertTrue(self.g.admit("x",1,snapshot(),PLAN)[0])
    def test_duplicate_id_after_release(self):
        self.g.admit("x",0,snapshot(),PLAN);self.g.release("x",1)
        self.assertFalse(self.g.admit("x",2,snapshot(),PLAN)[0])
    def test_atomic_competition(self):
        with ThreadPoolExecutor(max_workers=12) as pool:
            outcomes=list(pool.map(lambda i:self.g.admit(str(i),0,snapshot(),PLAN)[0],range(60)))
        self.assertEqual(sum(outcomes),1)
    def test_bad_snapshot_update_rejected(self):
        s=snapshot();s["tasks"][0]["duration"]=0
        self.assertFalse(self.g.update_snapshot(0,s)[0])
    def test_wrong_bucket_account(self):
        s=snapshot();s["tasks"][0]["mode_overrides"]["cloud"]["allowance"]["account"]="other"
        self.assertFalse(self.g.admit("x",0,s,PLAN)[0])
    def test_repeated_policy_update_cas(self):
        s=snapshot();self.assertTrue(self.g.update_snapshot(0,s)[0])
        self.assertFalse(self.g.update_snapshot(0,s)[0])
    def test_snapshot_isolation_from_constructor_input(self):
        s=snapshot();g=AdmissionGate(s,{B:{"limit":8,"reserve":0}})
        s["policy"]["p"]=[]
        self.assertTrue(g.admit("x",0,snapshot(),PLAN)[0])
    def test_release_preserves_spend(self):
        self.g.admit("x",0,snapshot(),PLAN)
        self.assertTrue(self.g.settle("x",1,[Claim(B,2)])[0])
        self.assertTrue(self.g.release("x",2)[0])
        self.assertEqual(self.g.balances()["spent"][B],2)
        self.assertEqual(self.g.balances()["available"][B],6)
    def test_failed_settlement_no_version_change(self):
        self.g.admit("x",0,snapshot(),PLAN)
        self.assertFalse(self.g.settle("x",1,[Claim(B,4)])[0])
        self.assertEqual(self.g.state()["revision"],1)
    def test_two_different_versions_only_one_admitted(self):
        def run(i):
            if i%2:return self.g.update_snapshot(0,snapshot())[0]
            return self.g.admit("x",0,snapshot(),PLAN)[0]
        with ThreadPoolExecutor(max_workers=16) as pool:
            result=list(pool.map(run,range(40)))
        self.assertEqual(sum(result),1)
    def test_invalid_policy_update_rejected_without_mutation(self):
        s=snapshot();s["tasks"][0]["deps"]=["missing"]
        before=self.g.state()
        self.assertFalse(self.g.update_snapshot(0,s)[0])
        self.assertEqual(before,self.g.state())
    def test_empty_plan_rejected(self):
        self.assertFalse(self.g.admit("x",0,snapshot(),{})[0])
    def test_paid_mode_without_mapping_rejected(self):
        s=snapshot();del s["tasks"][0]["mode_overrides"]["cloud"]["allowance"]
        g=AdmissionGate(s,{B:{"limit":8,"reserve":0}})
        self.assertFalse(g.admit("x",0,s,PLAN)[0])
if __name__=="__main__":unittest.main()

class PeriodIdentityTests(unittest.TestCase):
    def test_wrong_period_not_charged(self):
        s=snapshot();s["allowance_period"]="2026-12"
        g=AdmissionGate(s,{B:{"limit":8,"reserve":0}})
        self.assertFalse(g.admit("x",0,s,PLAN)[0])
    def test_matching_period_admitted(self):
        s=snapshot();s["allowance_period"]="2026-11"
        g=AdmissionGate(s,{B:{"limit":8,"reserve":0}})
        self.assertTrue(g.admit("x",0,s,PLAN)[0])
