# T10 — Empirical test of the documented confidence derivation

Claim under test (`README.md`): `confidence = (n*max(p) - 1) / (n - 1)`. Competing hypothesis: `confidence = max(p)`. The published confidence is demonstrably **not** `max(p)` (preflight P3a: 0.13 vs 0.27), so the distinction is load-bearing for every threshold sweep.

| mechanism | testable cells | label-space sizes | A: mean / max abs error | A within 0.01 | A exact at 2dp | B: mean / max abs error | verdict |
|---|---|---|---|---|---|---|---|
| prior | 0/64 | — | — | — | — | — | NOT TESTABLE — this mechanism reports no confidence field |
| rule | 0/64 | — | — | — | — | — | NOT TESTABLE — this mechanism reports no confidence field |
| lexical | 0/64 | — | — | — | — | — | NOT TESTABLE — this mechanism reports no confidence field |
| jev | 14/64 | {'3': 2, '6': 12} | 0.0005 / max 0.005 | 14/14 | 13/14 | 0.0071 / max 0.08 | A better |
| general_model | 0/64 | — | — | — | — | — | NOT TESTABLE — this mechanism reports no confidence field |

## T10a — stored derived confidence rechecked against a fresh recomputation

| mechanism | rows checked | mismatches |
|---|---|---|
| prior | 64 | 0 |
| rule | 64 | 0 |
| lexical | 64 | 0 |
| jev | 64 | 0 |
| general_model | 63 | 0 |

| question type | cells | with API-reported confidence |
|---|---|---|
| choice | 12 | 12 |
| noul | 50 | 0 |
| score | 2 | 2 |

> Residual = |reported confidence - hypothesis|. Probabilities are published rounded, so a residual of one or two units in the last place is the rounding floor, not a refutation. Hypothesis A is supported where A's mean absolute residual is materially below B's. A CHEAP TEST IS NOT AVAILABLE for noul: the API publishes no confidence there, so the derivation can only be tested on 14 of Jev's 64 cells.
