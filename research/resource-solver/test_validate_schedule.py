import unittest
from validate_schedule import validate
F = {"stages": [{"id":"a","dependencies":[]},{"id":"b","dependencies":["a"]}]}
P = {"environments":{"vps":{"ram_gib":4,"cpu_cores":2}},"stages":{"a":{"start":0,"end":2,"environment":"vps","ram_gib":3,"cpu_cores":1},"b":{"start":2,"end":4,"environment":"vps","ram_gib":3,"cpu_cores":1}}}
class Tests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(F,P),[])
    def test_dependency(self):
        import copy
        p=copy.deepcopy(P);p["stages"]["b"]["start"]=1
        self.assertTrue(any("dependency" in e for e in validate(F,p)))
    def test_ram(self):
        import copy
        f=copy.deepcopy(F);f["stages"][1]["dependencies"]=[]
        p=copy.deepcopy(P);p["stages"]["b"]["start"]=1
        self.assertTrue(any("ram_gib" in e for e in validate(f,p)))
    def test_frozen(self):
        import copy
        p=copy.deepcopy(P);p["frozen"]={"a":{"end":3}}
        self.assertTrue(any("frozen" in e for e in validate(F,p)))
    def test_missing(self):
        import copy
        p=copy.deepcopy(P);del p["stages"]["a"]
        self.assertTrue(validate(F,p))
if __name__ == "__main__": unittest.main()
