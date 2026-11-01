"""Independent exhaustive tiny-instance reference for portfolio optimization."""
import itertools
import random
import unittest
from portfolio_harness_v2 import beam, greedy, metric
from portfolio_oracle_v1 import validate

def scenario(seed):
    r=random.Random(seed)
    tasks=[]
    for i in range(3):
        tasks.append({"id":str(i),"project":"p","duration":r.randint(1,2),"cpu":1,"ram":1,
                      "deadline":r.randint(1,4),"value":r.randint(1,8),
                      "modes":["local","cloud"],
                      "deps":[str(i-1)] if i and r.random()<.5 else [],
                      "mode_overrides":{"cloud":{"duration":1,"credits":1}}})
    return {"horizon":4,"accounts":{"a":{"credits":1,"reserve":0,"period":4}},
            "policy":{"p":["a"]},
            "environments":{"local":{"cpu":1,"ram":1,"slots":1,"account":None},
                            "cloud":{"cpu":2,"ram":2,"slots":2,"account":"a"}},
            "tasks":tasks}

def exhaustive(d):
    options=[]
    for t in d["tasks"]:
        p=[None]
        for eid in t["modes"]:
            duration=t.get("mode_overrides",{}).get(eid,{}).get("duration",t["duration"])
            p.extend({"env":eid,"start":s} for s in range(d["horizon"]-duration+1))
        options.append(p)
    best=0
    for combo in itertools.product(*options):
        p={t["id"]:v for t,v in zip(d["tasks"],combo) if v is not None}
        if not validate(d,p):
            best=max(best,metric(d,p)[0])
    return best

class ExactReference(unittest.TestCase):
    def test_50_generated_instances(self):
        gaps=[]
        for seed in range(50):
            d=scenario(seed)
            optimum=exhaustive(d)
            for planner in (greedy,lambda x:beam(x,30)):
                plan=planner(d)
                self.assertEqual(validate(d,plan),[],f"seed={seed}")
                value=metric(d,plan)[0]
                self.assertLessEqual(value,optimum,f"seed={seed}")
                gaps.append((seed,planner.__name__,optimum-value))
        self.assertEqual(len(gaps),100)
        # Do not require heuristic optimality: this test measures gaps.
        print("exact comparison:",len(gaps),"planner runs;",
              sum(g>0 for _,_,g in gaps),"suboptimal; max gap",
              max(g for _,_,g in gaps))

if __name__=="__main__":unittest.main()
