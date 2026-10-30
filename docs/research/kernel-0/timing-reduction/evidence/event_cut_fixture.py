#!/usr/bin/env python3
"""Small logical capture/current-view/whole-successor/order fixture; not timing proof."""
from dataclasses import FrozenInstanceError, asdict
from itertools import permutations
from pathlib import Path
import json, sys
HERE=Path(__file__).resolve().parents[1]
K0=HERE.parent
sys.path.insert(0,str(K0))
import kernel0_finite_model as m
p=m.Profile('independent')
# Capture representation: the finite flight model stores the full immutable Request.
q=m.Request('set', evidence=0, target=0, value=1, other=0)
captured=m.Request(q.kind,q.evidence,q.target,q.value,q.other,q.authentic)
assert captured==q
try:
    captured.target=1
except FrozenInstanceError:
    capture_immutable=True
else:
    raise AssertionError('request capture representation is mutable')
# Current-view event interleavings: current semantics pass, stale-snapshot mutant is detected.
base=m.established((0,7),p=p)
requests=(m.Request('set',0,0,1),m.Request('restrict',target=0,value=0))
good=m.flight_explore('bounded revocation/current-view fixture',base,requests,(0,-1),p,death=False)
bad=m.flight_explore('bounded revocation/stale-view mutant',base,requests,(0,-1),p,weakness='stale_view',death=False)
assert good['counterexample'] is None and bad['counterexample'] is not None
# Whole-successor publication granularity: operation endpoints are the only accepted cuts.
pair=m.Request('pair',evidence=0,value=3)
whole,outcome=m.resolve(base,pair,p)
partial=m.replace(base,data=(1,0))
assert outcome=='commit' and whole.data==(1,1)
accepted_cuts={base,whole}
assert partial not in accepted_cuts and partial not in (base,whole)
# Necessary order for interacting commitments: a completed revocation precedes
# a later write. Only the overlap history can serialize as write then revocation.
ops=((lambda s: True, lambda s: (False,s[1])),
     (lambda s: s[0], lambda s: (s[0],1)))
overlap=m.serial_witness((True,0),ops,(0,1),frozenset())
ordered=m.serial_witness((True,0),ops,(0,1),frozenset({(0,1)}))
assert overlap==[1,0] and ordered is None
explored=good['states']+bad['states']+len(tuple(permutations((0,1))))
assert explored<=1000,(explored,good['states'],bad['states'])
print(json.dumps({'status':'PASS','explored_states':explored,'state_cap':1000,
 'capture':'full immutable Request copied as one Python object (physical torn capture not modeled)',
 'current_view':{'correct_states':good['states'],'mutant_states':bad['states'],'stale_view_counterexample':bad['counterexample']},
 'whole_successor':{'before':asdict(base),'complete':asdict(whole),'intermediate_cut_rejected':asdict(partial)},
 'ordering':{'overlap_witness':overlap,'completed_before_initiated_witness':ordered},
 'model_boundary':'flight_explore makes proposal capture and successor state change atomic; no intermediate capture/publication cut exists in its state encoding'},sort_keys=True))
