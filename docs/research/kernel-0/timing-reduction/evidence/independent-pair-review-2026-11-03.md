# Independent paired-state check — 2026-11-03

## First verdict

**Bounded conformance: pass, with a finite-fixture scope.** At pinned source
revision `0d54fa63aecf5d942b68958d37d61cabc41c6527`, the pair scanner compares
distinct legal fixture states under three observation masks. For each request
it compares `(outcome, projected successor)` whenever the projected pre-states
are equal. The narrower `rights` mask has positive mismatch controls; adding
`parents` removes mismatches in the four-state fixture, while a six-state
coupled fixture exposes four mismatches for `rights+parents`. Adding `data`
removes those mismatches in this fixture. This is evidence about the enumerated
states, two requests, two profiles, and listed masks only; it does not establish
general mask sufficiency.

The mask named `rights_parents_data` contains only `rights`, `parents`, and
`data`. It omits `established`, `content`, and `issued`, so its zero-mismatch
result must not be read as an all-fields or global result.

The timing harness deadline path reports JSON with `status: incomplete` and
`reason: deadline`. The separate `parent_projection_probe.py` does not pass at
this pinned revision: it asserts that the current `minimal_style` omits
`parents`, while the repaired implementation includes `parents`. This is a
stale negative-control probe and does not invalidate the pair scanner result.

## Basis and source identity

Worktree `/workspace/ases-kernel-check`, branch
`review/autonomy-20261103-kernel-pairs`, HEAD
`0d54fa63aecf5d942b68958d37d61cabc41c6527`. The checked files are:

| File | SHA-256 |
|---|---|
| `docs/research/kernel-0/timing-reduction/evidence/pair_projection_scan.py` | `917c3eda21a31c72bed15d19c386bae3cc2499a050c39fc729a18ae0b157f3c6` |
| `docs/research/kernel-0/timing-reduction/evidence/parent_projection_probe.py` | `089ddd489bb5a0a26473d94f74d28decba7093cdacd83afbbe79737a3c76929b` |
| `docs/research/kernel-0/timing-reduction/timing_event_model.py` | `c3a66af47758e4a724e80531ae4468a6dfce0f4f1b4179cf208549d7aed1854f` |
| `docs/research/kernel-0/kernel0_finite_model.py` | `c9c429b0400df6e044d30b71befaeb810657430372fb1088f9e62631c8965083` |

The comparison contract used here is the Kernel-0 Abstract Semantics resolved
transition relation: a commit has a whole successor; a denial has no
authoritative effect. The Verification Obligations state that checked models
establish only represented properties and assumptions. These definitions
support checking outcome and visible successor together; they do not imply
that an observation mask can omit an authoritative distinction.

## Commands and results

All Python executions were run with a 1 GiB virtual-memory limit and a
1800-second timeout. The scanner outputs report peak RSS of about 12–15 MiB;
each completed in under 0.003 seconds.

The first attempted wrapper included `/usr/bin/time`, which is absent in this
environment and prevented Python from starting. The distinct failed command
was:

```sh
ulimit -v 1048576; /usr/bin/time -f 'elapsed=%e maxrss_kb=%M exit=%x' timeout 1800s python3 docs/research/kernel-0/timing-reduction/evidence/pair_projection_scan.py --states-per-profile 4 --pair-case-cap 1000
```

The actual bounded reruns were:

```sh
ulimit -v 1048576; timeout 1800s python3 docs/research/kernel-0/timing-reduction/evidence/pair_projection_scan.py --states-per-profile 4 --pair-case-cap 1000
ulimit -v 1048576; timeout 1800s python3 docs/research/kernel-0/timing-reduction/evidence/pair_projection_scan.py --states-per-profile 6 --pair-case-cap 1000
ulimit -v 1048576; timeout 1800s python3 docs/research/kernel-0/timing-reduction/timing_event_model.py --deadline 0 --output /tmp/ases-kernel-deadline-should-not-exist.json
ulimit -v 1048576; timeout 1800s python3 docs/research/kernel-0/timing-reduction/evidence/parent_projection_probe.py
```

The two pair-scanner runs completed with statuses `complete_bounded_fixture`.
The four-state run covered 8 states and 72 pair cases; the six-state run covered
12 states and 180 pair cases. Negative neighboring control: the rights-only
mask found 8 and 26 mismatches, respectively. Positive neighboring controls:
`rights+parents` had zero mismatches for four states, then found four mismatches
in the six-state coupled profile; `rights+parents+data` had zero mismatches in
both runs. The scanner's old perturbation style was `rights` only, while its
repaired style included both `rights` and `parents` in both profiles.

The zero-second deadline invocation exited 1 and emitted:

```json
{"cursor": {"completed_offers": 0, "legal_states": 0, "next_word": 0, "profile": "independent"}, "phase": "correspondence", "reason": "deadline", "status": "incomplete"}
```

The parent-projection probe exited 1 with `AssertionError` at its line 23
assertion that the current style omit `parents`.

## Independent reproduction

This independent enumeration was written and run only in `/tmp`; it calls the
frozen transition oracle but implements its own pair enumeration, projections,
and mismatch comparison. It reproduced the passing and failing neighboring
controls above.

```python
from dataclasses import replace
from itertools import combinations
from pathlib import Path
import sys, json
root=Path('/workspace/ases-kernel-check/docs/research/kernel-0/timing-reduction')
sys.path.insert(0,str(root))
import timing_event_model as t
m=t.model
masks={'rights':('rights',),'rights_parents':('rights','parents'),
       'rights_parents_data':('rights','parents','data')}
requests=(m.Request('restrict',target=0,value=0),
          m.Request('set',evidence=0,target=0,value=1))
def proj(s, fields): return tuple((f,getattr(s,f)) for f in fields)
result={}
for n in (4,6):
  summary={}
  for p in t.PROFILES[:2]:
    root=m.established((0,7),p=p)
    a,ka=m.resolve(root,m.Request('grant',target=3,value=1),p)
    b,kb=m.resolve(root,m.Request('delegate',evidence=0,target=3,value=1),p)
    states=[a,b,replace(a,content=1),replace(b,content=1),
            replace(a,data=(0,1)),replace(b,data=(0,1))][:n]
    assert ka==kb=='commit' and len(set(states))==n
    assert all(m.invariant(s,p) for s in states)
    ps={name:{'cases':0,'same_input':0,'different':0,'examples':[]}
        for name in masks}
    for (i,x),(j,y) in combinations(enumerate(states),2):
      for q in requests:
        ox,kx=m.resolve(x,q,p); oy,ky=m.resolve(y,q,p)
        for name,fields in masks.items():
          c=ps[name]; c['cases']+=1
          if proj(x,fields)!=proj(y,fields): continue
          c['same_input']+=1
          if kx!=ky or proj(ox,fields)!=proj(oy,fields):
            c['different']+=1
            if len(c['examples'])<2:
              c['examples'].append([i,j,q.label(),kx,ky])
    summary[p.name]=ps
  result[str(n)]=summary
assert result['4']['independent']['rights']['different']>0
assert result['4']['independent']['rights_parents']['different']==0
assert result['6']['coupled']['rights_parents']['different']>0
assert result['6']['independent']['rights_parents_data']['different']==0
print(json.dumps(result,sort_keys=True))
```

Its raw JSON output is preserved here:

```json
{"4": {"coupled": {"rights": {"cases": 12, "different": 4, "examples": [[0, 1, "restrict(management, 0, 0, 0)", "commit", "commit"], [0, 3, "restrict(management, 0, 0, 0)", "commit", "commit"]], "same_input": 12}, "rights_parents": {"cases": 12, "different": 0, "examples": [], "same_input": 4}, "rights_parents_data": {"cases": 12, "different": 0, "examples": [], "same_input": 4}}, "independent": {"rights": {"cases": 12, "different": 4, "examples": [[0, 1, "restrict(management, 0, 0, 0)", "commit", "commit"], [0, 3, "restrict(management, 0, 0, 0)", "commit", "commit"]], "same_input": 12}, "rights_parents": {"cases": 12, "different": 0, "examples": [], "same_input": 4}, "rights_parents_data": {"cases": 12, "different": 0, "examples": [], "same_input": 4}}}, "6": {"coupled": {"rights": {"cases": 30, "different": 17, "examples": [[0, 1, "restrict(management, 0, 0, 0)", "commit", "commit"], [0, 3, "restrict(management, 0, 0, 0)", "commit", "commit"]], "same_input": 30}, "rights_parents": {"cases": 30, "different": 4, "examples": [[0, 4, "set(a0, 0, 1, 0)", "commit", "deny"], [1, 5, "set(a0, 0, 1, 0)", "commit", "deny"]], "same_input": 12}, "rights_parents_data": {"cases": 30, "different": 0, "examples": [], "same_input": 4}}, "independent": {"rights": {"cases": 30, "different": 9, "examples": [[0, 1, "restrict(management, 0, 0, 0)", "commit", "commit"], [0, 3, "restrict(management, 0, 0, 0)", "commit", "commit"]], "same_input": 30}, "rights_parents": {"cases": 30, "different": 0, "examples": [], "same_input": 12}, "rights_parents_data": {"cases": 30, "different": 0, "examples": [], "same_input": 4}}}}
```

## Limits

This review checks the comparator and bounded fixture behavior, not the
abstract model's adequacy or the correctness of every transition rule. It
covers only the first two profiles, a hand-built set of four or six states per
profile, `restrict` and `set`, and three masks. The oracle still resolves from
full state; projection is applied to compare visible pre-state and successor.
No global sufficiency claim, exhaustiveness claim, physical timing claim, or
realization conformance result follows. The zero-second deadline probe checks
the early-exit reporting path, not deadline behavior at every later phase.
