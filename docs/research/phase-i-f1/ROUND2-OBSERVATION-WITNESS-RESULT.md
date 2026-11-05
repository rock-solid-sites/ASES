# Two reachable histories collide in the diagnostic observation

Sourceeb15d8e. Command `python3 docs/research/phase-i-f1/round2_observation_witness.py`.
Original initial history and grant P/SINK/RW then grant C/SINK/RW both retain same
present/sealed/parent fields, management statuses and uses log: exactly the diagnostic
Obs. Both prefixes reachable; all granted events commit/invariants pass. Next identical
use C/SINK/W/origin3 denies initially and commits after grants. Original guard, separately
restated use oracle and actual resolve agree, no underlying authorization defect.

Original observational_equivalence applied to exactly these two Node states reports
one colliding group/equivalent=false and the actual differing use event. Full states/
prefixes/next outputs retained in raw. Adding actual grants distinguishes this pair,
but no sufficiency/minimality or canonical schema assertion follows. No BFS rerun.
This makes the completed first-context diagnostic reproducible without confusing its
false projection predicate with zero invariant violations or diagnostic-driver exit0.
Other full-driver contexts/semantic checks not discharged here. Abstract model only,
no host/physical/power-loss or F1 completion claim. Next: original full-driver phase
checkpointing under one bounded window, so first actual remaining limiting phase is
observed instead of assuming the first context is still the blocker.
