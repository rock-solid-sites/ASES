# Broad all-context exploration is the remaining observed full-driver bottleneck

Original driver/source35d705c, same40s/1GiB virtual bound as Nov3 independent review;
only transparent phase wrappers/progress added. Actual wall40.0162s/child CPU40.0095s,
child-lifetime peak RSS620016KiB; parent timeout/SIGKILL/reap exit-9, stderr empty,
no original end report. Full result remains timed_out_inconclusive, not pass or fail.

Original BFS returns, before the broad `all` context:

| Context | Reached states | Invariant violations |
|---|---:|---:|
| containment-and-grants |18208|0|
| engine-loss-and-recovery |24|0|
| replacement-and-management |684|0|
| delegation |120|0|

Actual commits/denials/check outputs in raw/check JSON. At39.0001s `all` still explores
227533 seen/158039 queued/872333 commits, below declared400000 state cap; no completion.
Other later contexts/witnesses/attacks and final driver acceptance are unexecuted here.
Model/function outputs returned unchanged, telemetry overhead unquantified. No inference
that more time must finish or bound must be sufficient; no repeated budget doubling.

All four completed contexts ran original semantic/observation diagnostics. Some global
semantic-helper predicates are false, including D1 positive controls absent from a
context; Nov3 review ALREADY warned about context applicability. Not a new finding or
reason to silently ignore every false predicate. Containment also reports false
“accepted latent ceiling is within the whole containment chain” without a witness in
its detail field; source distinguishes stored local latent from derived ancestor
intersection. Investigate a small actual reachable trace before classifying that result
as product widening versus a stronger representation predicate. Do not turn zero
invariant violations or child-driver completion into semantic/full-model acceptance.

WHY: previous driver only emits final report, making timeout location unknown. WHAT:
actual original main/function calls, phase entry/returns, periodic graph counts, known
helper failures and exact exit/resources/source/executable hashes. Certainty: observed
finite completed contexts and incomplete broad prefix, not universal F1/PhaseI proof,
physical host enforcement or power loss. Raw stdout/stderr retained; missing end report
is explicit missing evidence, not absence of every potential violation. Next smallest
C8 discriminator: local stored ceiling versus effective path ceiling, descendant
regrant/use and relocation, with weaker latent-preservation mutation and read positive.
