# T2 — Accuracy per area

Area A cheap-baseline comparison · B abstention/escalation · C contrastive/causal perturbations · D workflow routing.

**Area B is 13/13 unanswerable** — every area-B case has `answerable=false` and `abstain_expected=true`, so `acc answerable-only` is undefined there and the mixed column plus the false-confidence column are the whole of the area-B result.

| mechanism | area | cells | answerable | unanswerable | acc answerable-only | acc mixed | answered unanswerable |
|---|---|---|---|---|---|---|---|
| prior | A | 23 | 22 | 1 | 59.1% | 56.5% | 1/1 |
| prior | B | 13 | 0 | 13 | n/a (all unanswerable) | 0.0% | 13/13 |
| prior | C | 16 | 16 | 0 | 37.5% | 37.5% | 0/0 |
| prior | D | 12 | 12 | 0 | 25.0% | 25.0% | 0/0 |
| rule | A | 23 | 22 | 1 | 72.7% | 69.6% | 1/1 |
| rule | B | 13 | 0 | 13 | n/a (all unanswerable) | 0.0% | 13/13 |
| rule | C | 16 | 16 | 0 | 68.8% | 68.8% | 0/0 |
| rule | D | 12 | 12 | 0 | 100.0% | 100.0% | 0/0 |
| lexical | A | 23 | 22 | 1 | 59.1% | 56.5% | 1/1 |
| lexical | B | 13 | 0 | 13 | n/a (all unanswerable) | 0.0% | 13/13 |
| lexical | C | 16 | 16 | 0 | 75.0% | 75.0% | 0/0 |
| lexical | D | 12 | 12 | 0 | 33.3% | 33.3% | 0/0 |
| jev | A | 23 | 22 | 1 | 100.0% | 95.7% | 1/1 |
| jev | B | 13 | 0 | 13 | n/a (all unanswerable) | 0.0% | 13/13 |
| jev | C | 16 | 16 | 0 | 93.8% | 93.8% | 0/0 |
| jev | D | 12 | 12 | 0 | 100.0% | 100.0% | 0/0 |
| general_model | A | 23 | 22 | 1 | 100.0% | 95.7% | 1/1 |
| general_model | B | 13 | 0 | 13 | n/a (all unanswerable) | 7.7% | 12/13 |
| general_model | C | 16 | 16 | 0 | 100.0% | 100.0% | 0/0 |
| general_model | D | 12 | 12 | 0 | 100.0% | 100.0% | 0/0 |

| mechanism | split | cells | acc answerable-only | acc mixed |
|---|---|---|---|---|
| prior | train | 21 | 55.6% | 47.6% |
| prior | dev | 21 | 33.3% | 23.8% |
| prior | test | 22 | 41.2% | 31.8% |
| rule | train | 21 | 77.8% | 66.7% |
| rule | dev | 21 | 73.3% | 52.4% |
| rule | test | 22 | 82.3% | 63.6% |
| lexical | train | 21 | 66.7% | 57.1% |
| lexical | dev | 21 | 53.3% | 38.1% |
| lexical | test | 22 | 52.9% | 40.9% |
| jev | train | 21 | 100.0% | 85.7% |
| jev | dev | 21 | 93.3% | 66.7% |
| jev | test | 22 | 100.0% | 77.3% |
| general_model | train | 21 | 100.0% | 85.7% |
| general_model | dev | 21 | 100.0% | 76.2% |
| general_model | test | 22 | 100.0% | 77.3% |
