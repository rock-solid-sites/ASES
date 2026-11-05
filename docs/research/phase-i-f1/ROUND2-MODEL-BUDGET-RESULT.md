# Original first context completes; its observation diagnostic is false

Executed original child/model at59e112b with only parent wall budget30s (prior5s),
unchanged256MiB child virtual cap and original200000 state bound. Command
`python3 docs/research/phase-i-f1/round2_model_budget.py`.

Actual wall7.21897s, child CPU7.215515s, child-lifetime peak RSS65896KiB (parent's
only child before measurement). Exit0, no timeout/stderr, exact source hashes stable.
Containment-and-grants BFS completes6.3363s:18208 reachable states,192656 committed
transitions,0 invariant violations. Observation phase completes7.1536s:24 observation
groups,24 colliding groups, equivalent=false, five reported admission mismatches for
use C/SINK/W/origin3. Original diagnostic reports only first5 examples, not total number
of mismatching pairs; do not infer count5 is exhaustive.

This resolves the earlier first-context5s run as time-bounded incompleteness, not a
product pass/fail. The whole original driver still has other contexts, semantic checks,
witnesses and attack runs not executed here. Child exit0 means this diagnostic driver
completed, not that the false observation predicate became true. Original main also
records observation diagnostic separately from its final ok gate; source-reviewed only,
no new full driver result. No generic F1 closure or full-model verification inferred.

WHY: identify actual limiting phase before changing verification scope/implementation.
WHAT: unmodified original exploration, phase/progress events, exit/timeout/actual measured
resources and executable/source identities. Certainty: executed finite first-context
result; model is abstract and selected independent of physical SQLite/host evidence.
No native enforcement, power loss or universal proof. Source/command/raw in
round2-model-budget.raw.json, stderr empty. Next smallest discriminator: replay two
named reachable histories sharing the declared diagnostic Obs but differing in required
next-use authorization; identify missing information, not repair equivalence by fiat.
