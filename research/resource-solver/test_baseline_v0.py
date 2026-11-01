"""Regression checks for the committed prototype; run: python -m unittest discover -s research/resource-solver -p 'test_*.py'"""
import copy
import unittest
from heuristic_v0 import schedule
from validator_v1 import validate
F={"scenario":"synthetic-two","stages":[{"id":"a","dependencies":[],"duration_ticks":3,"ram_mib":1024,"cpu_millicores":1000,"slots":1},{"id":"b","dependencies":["a"],"duration_ticks":2,"ram_mib":1024,"cpu_millicores":1000,"slots":1}]}
S={"id":"snapshot-1","environments":{"vps":{"ram_mib":2048,"cpu_millicores":2000,"slots":2,"outages":[]}}}
class Baseline(unittest.TestCase):
 def test_feasible(self):
  p=schedule(F,S);self.assertEqual(validate(F,p,S),[]);self.assertEqual(p["stages"]["b"]["start"],3)
 def test_outage(self):
  s=copy.deepcopy(S);s["environments"]["vps"]["outages"]=[[0,4]]
  self.assertGreaterEqual(schedule(F,s)["stages"]["a"]["start"],4)
 def test_cycle(self):
  f=copy.deepcopy(F);f["stages"][0]["dependencies"]=["b"]
  with self.assertRaisesRegex(ValueError,"cycle"):schedule(f,S)
 def test_oversized(self):
  f=copy.deepcopy(F);f["stages"][0]["ram_mib"]=99999
  with self.assertRaisesRegex(ValueError,"no feasible"):schedule(f,S)
 def test_dependency_violation(self):
  p=schedule(F,S);p["stages"]["b"]["start"]=2
  self.assertTrue(any("dependency" in e for e in validate(F,p,S)))
 def test_forged_demand(self):
  p=schedule(F,S);p["stages"]["a"]["ram_mib"]=1
  self.assertTrue(any("authoritative" in e for e in validate(F,p,S)))
 def test_snapshot_identity(self):
  p=schedule(F,S);p["snapshot_id"]=""
  self.assertTrue(any("snapshot" in e for e in validate(F,p,S)))
if __name__=="__main__":unittest.main()
