"""Regression for overconservative interval-overlap resource accounting."""
import unittest
from heuristic_v0 import schedule
from validator_v1 import validate
class Overlap(unittest.TestCase):
 def test_staggered_jobs_allow_middle_placement(self):
  f={"scenario":"staggered","stages":[
   {"id":"a","dependencies":[],"duration_ticks":2,"ram_mib":2,"cpu_millicores":1,"slots":1},
   {"id":"b","dependencies":["a"],"duration_ticks":2,"ram_mib":2,"cpu_millicores":1,"slots":1},
   {"id":"c","dependencies":[],"duration_ticks":2,"ram_mib":2,"cpu_millicores":1,"slots":1}]}
  snap={"id":"fixed","environments":{"vps":{"ram_mib":4,"cpu_millicores":2,"slots":2,"outages":[]}}}
  p=schedule(f,snap)
  self.assertEqual(validate(f,p,snap),[])
  self.assertEqual(max(v["end"] for v in p["stages"].values()),4)
if __name__=="__main__":unittest.main()
