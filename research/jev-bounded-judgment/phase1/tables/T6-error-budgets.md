# T6 — Coverage reachable under 1% / 5% / 10% error budgets

A budget of B% over 64 cells allows `floor(B*n)` errors. **At n=64 a 1% budget is 0.64 errors, so the floor is 0 — a 1% budget means ZERO errors.** That discreteness is not a detail; it is the whole reason the 1% row is so stark.

| mechanism | budget | max errors (exact) | max errors (floor) | discrete | achievable at a tested threshold | threshold | coverage | errors |
|---|---|---|---|---|---|---|---|---|
| prior | 1% | 0.64 | 0 | yes | yes | 0.95 | 0.0% | 0 |
| prior | 5% | 3.2 | 3 | yes | yes | 0.95 | 0.0% | 0 |
| prior | 10% | 6.4 | 6 | yes | yes | 0.95 | 0.0% | 0 |
| rule | 1% | 0.64 | 0 | yes | **no** | — | — | min 8 |
| rule | 5% | 3.2 | 3 | yes | **no** | — | — | min 8 |
| rule | 10% | 6.4 | 6 | yes | **no** | — | — | min 8 |
| lexical | 1% | 0.64 | 0 | yes | **no** | — | — | min 3 |
| lexical | 5% | 3.2 | 3 | yes | yes | 0.95 | 7.8% | 3 |
| lexical | 10% | 6.4 | 6 | yes | yes | 0.70 | 10.9% | 5 |
| jev | 1% | 0.64 | 0 | yes | yes | 0.90 | 59.4% | 0 |
| jev | 5% | 3.2 | 3 | yes | yes | 0.80 | 70.3% | 3 |
| jev | 10% | 6.4 | 6 | yes | yes | 0.70 | 75.0% | 4 |
| general_model | 1% | 0.64 | 0 | yes | **no** | — | — | min 13 |
| general_model | 5% | 3.2 | 3 | yes | **no** | — | — | min 13 |
| general_model | 10% | 6.4 | 6 | yes | **no** | — | — | min 13 |

> Only the four thresholds of T5 are searched. A mechanism could in principle sit between them, so *not achievable here* means *not achievable at 0.70/0.80/0.90/0.95* and is not a proof that no threshold works.

> `general_model` is not achievable at any budget because its confidence carries no information: a hard one-hot decode gives 1.0 on every cell, so every threshold selects the same 63 cells and the same 13 errors. Read this as *the general model emitted no usable confidence*, not as *the general model is inaccurate* — on answerable cases it was the most accurate mechanism in the grid (T1).
