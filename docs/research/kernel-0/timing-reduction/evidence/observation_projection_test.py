#!/usr/bin/env python3
"""Tiny deterministic check that hidden state fields are removed by projection."""
from dataclasses import replace
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE.parent))
sys.path.insert(0,str(HERE.parent/'direct-rtl'))
sys.path.insert(0,str(HERE))
import kernel0_finite_model as model
import timing_event_model as timing
s=model.established()
without_issued=frozenset(timing.ALL_FIELDS-{'issued'})
changed_hidden=replace(s,issued=1)
assert s != changed_hidden
assert timing.project(s,without_issued)==timing.project(changed_hidden,without_issued)
with_issued=frozenset(timing.ALL_FIELDS)
assert timing.project(s,with_issued)!=timing.project(changed_hidden,with_issued)
visible_data=frozenset(timing.ALL_FIELDS-{'issued'})
changed_visible=replace(s,data=(1,0))
assert timing.project(s,visible_data)!=timing.project(changed_visible,visible_data)
assert timing.project(s,frozenset())==()
print('PASS hidden issued collapses when omitted; visible issued/data remain distinct; empty projection is empty')
