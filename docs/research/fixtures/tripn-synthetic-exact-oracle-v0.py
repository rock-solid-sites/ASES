#!/usr/bin/env python3
"""Exact small-instance scheduling oracle. All durations and RAM are synthetic."""
import itertools
JOBS=[("landing",16,1.5),("og",9,1.5),("pink_bubble",6,1.2),("chill_zone",8,1.2),("seaside",7,1.2)]
def solve(workers,ram):
    best=None
    for a in itertools.product(range(workers),repeat=len(JOBS)):
        if set(a)!=set(range(workers)): continue
        loads=[sum(JOBS[i][1] for i,w in enumerate(a) if w==j) for j in range(workers)]
        peaks=[max(JOBS[i][2] for i,w in enumerate(a) if w==j) for j in range(workers)]
        peak=1+sum(peaks)
        if peak>ram:continue
        cand=(max(loads),peak,a,loads)
        if best is None or cand[:3]<best[:3]:best=cand
    return None if best is None else {"makespan_seconds":best[0],"peak_ram_gib":best[1],"assignment":{JOBS[i][0]:best[2][i] for i in range(len(JOBS))},"worker_load_seconds":best[3]}
if __name__=="__main__":
    import json
    print(json.dumps({f"{ram}GiB_{w}workers":solve(w,ram) for ram in (3,4,8) for w in (1,2,3)},indent=2))
