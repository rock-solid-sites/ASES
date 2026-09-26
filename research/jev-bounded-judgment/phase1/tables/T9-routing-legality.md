# T9 — Routing legality (area D)

Legality is deterministic and computed from `routing.signals` **before any model sees a case**. `n_recompute_mismatch` is the scorer independently recomputing the stored block and comparing — it must be 0 for every mechanism.

| mechanism | cases | usable | legal | legal rate | illegal picks | picked expected role | recompute mismatch |
|---|---|---|---|---|---|---|---|
| prior | 12 | 12 | 3/12 | 25.0% | 9 | 3/12 | 0 |
| rule | 12 | 12 | 12/12 | 100.0% | 0 | 12/12 | 0 |
| lexical | 12 | 12 | 5/12 | 41.7% | 7 | 4/12 | 0 |
| jev | 12 | 12 | 12/12 | 100.0% | 0 | 12/12 | 0 |
| general_model | 12 | 12 | 12/12 | 100.0% | 0 | 12/12 | 0 |

## T9a — Jev, case by case

| case | expected role | legal roles | predicted role | legal? | correct? | confidence | source |
|---|---|---|---|---|---|---|---|
| d-01 | build | build | build | True | True | 1.0 | reported |
| d-02 | redesign | redesign | redesign | True | True | 1.0 | reported |
| d-03 | investigate | investigate | investigate | True | True | 1.0 | reported |
| d-04 | repair | repair | repair | True | True | 1.0 | reported |
| d-05 | redesign | redesign | redesign | True | True | 1.0 | reported |
| d-06 | review | review | review | True | True | 1.0 | reported |
| d-07 | escalate | escalate, investigate | escalate | True | True | 0.52 | reported |
| d-08 | escalate | escalate, repair | escalate | True | True | 0.99 | reported |
| d-l01 | repair | repair | repair | True | True | 1.0 | reported |
| d-l02 | redesign | redesign | redesign | True | True | 1.0 | reported |
| d-r01 | investigate | investigate | investigate | True | True | 1.0 | reported |
| d-r02 | review | review | review | True | True | 1.0 | reported |

> Legality is recomputed from routing.signals by routing_policy.compute_legality and compared with the stored block; n_recompute_mismatch must be 0. A role is legal only when its own precondition signal is set, so the illegal candidates are structurally impossible — that is what makes area D adversarial rather than descriptive. TAUTOLOGY WARNING: `rule` evaluates that same policy, so its 12/12 is a definition, not a discovery.
