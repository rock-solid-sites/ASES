import copy,unittest
from validator_v1 import validate
F={'scenario':'test','stages':[{'id':'a','dependencies':[],'ram_mib':1800,'cpu_millicores':1000,'slots':1},{'id':'b','dependencies':[],'ram_mib':1800,'cpu_millicores':1000,'slots':1}]}
S={'id':'trusted-1','environments':{'vps':{'ram_mib':2048,'cpu_millicores':2000,'slots':2,'outages':[]}}}
P={'fixture_id':'test','snapshot_id':'trusted-1','time_tick_seconds':60,'environments':{'vps':{'ram_mib':99999,'cpu_millicores':2000,'slots':2,'outages':[]}},'stages':{'a':{'start':0,'end':2,'environment':'vps','ram_mib':1800,'cpu_millicores':1000,'slots':1},'b':{'start':0,'end':2,'environment':'vps','ram_mib':1800,'cpu_millicores':1000,'slots':1}}}
class Boundary(unittest.TestCase):
 def test_reject_forged_capacity(self):
  self.assertTrue(any('capacity' in x for x in validate(F,P,S)))
 def test_accept_correct_capacity(self):
  p=copy.deepcopy(P);p['stages']['b']['start']=2;p['stages']['b']['end']=4;p['environments']=copy.deepcopy(S['environments'])
  self.assertEqual(validate(F,p,S),[])
 def test_reject_stale_snapshot(self):
  p=copy.deepcopy(P);p['snapshot_id']='old'
  self.assertTrue(any('snapshot' in x for x in validate(F,p,S)))
 def test_reject_forged_outage(self):
  s=copy.deepcopy(S);s['environments']['vps']['outages']=[[0,3]]
  p=copy.deepcopy(P);p['stages']['b']['start']=2;p['stages']['b']['end']=4
  self.assertTrue(any('outage' in x for x in validate(F,p,s)))
if __name__=='__main__':unittest.main()
