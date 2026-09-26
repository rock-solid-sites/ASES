# T5 — Coverage vs error at the four fixed thresholds

Thresholds 0.70 / 0.80 / 0.90 / 0.95 are fixed by `README.md`, not tuned on this data. An **act** = a cell whose confidence reaches the threshold. An **error** among the acted cells = a wrong label on an answerable case, or any label at all on an unanswerable case.

`pool` = cells with a usable label AND a confidence; `excluded` = cells that can never be acted on (no label, or no confidence at all).

## T5a — what each mechanism's confidence actually is

| mechanism | what the confidence is |
|---|---|
| prior | derived from the measured TRAIN-split label distribution |
| rule | ASSUMED constant injected by the rule engine (0.75/0.55/0.90), not a measurement; area D re-derives it from the routing policy |
| lexical | derived from an arbitrary-scale token-overlap softmax; the scale is not calibrated, only monotone in overlap |
| jev | MIXED: API-reported for choice/score (14 cells), locally derived from noul for noul (50 cells) — see the caveat block above |
| general_model | IDENTICALLY 1.0 by construction (hard one-hot decode); threshold coverage is an encoding artefact, not a measurement |

## T5b — the curve

| mechanism | threshold | pool | excluded | acted | coverage | errors | error rate of acted | of which false-confidence | of which wrong label |
|---|---|---|---|---|---|---|---|---|---|
| prior | 0.70 | 64 | 0 | 0 | 0.0% | 0 | n/a | 0 | 0 |
| prior | 0.80 | 64 | 0 | 0 | 0.0% | 0 | n/a | 0 | 0 |
| prior | 0.90 | 64 | 0 | 0 | 0.0% | 0 | n/a | 0 | 0 |
| prior | 0.95 | 64 | 0 | 0 | 0.0% | 0 | n/a | 0 | 0 |
| rule | 0.70 | 64 | 0 | 37 | 57.8% | 8 | 21.6% | 5 | 3 |
| rule | 0.80 | 64 | 0 | 37 | 57.8% | 8 | 21.6% | 5 | 3 |
| rule | 0.90 | 64 | 0 | 25 | 39.1% | 8 | 32.0% | 5 | 3 |
| rule | 0.95 | 64 | 0 | 25 | 39.1% | 8 | 32.0% | 5 | 3 |
| lexical | 0.70 | 64 | 0 | 7 | 10.9% | 5 | 71.4% | 0 | 5 |
| lexical | 0.80 | 64 | 0 | 5 | 7.8% | 3 | 60.0% | 0 | 3 |
| lexical | 0.90 | 64 | 0 | 5 | 7.8% | 3 | 60.0% | 0 | 3 |
| lexical | 0.95 | 64 | 0 | 5 | 7.8% | 3 | 60.0% | 0 | 3 |
| jev | 0.70 | 64 | 0 | 48 | 75.0% | 4 | 8.3% | 4 | 0 |
| jev | 0.80 | 64 | 0 | 45 | 70.3% | 3 | 6.7% | 3 | 0 |
| jev | 0.90 | 64 | 0 | 38 | 59.4% | 0 | 0.0% | 0 | 0 |
| jev | 0.95 | 64 | 0 | 25 | 39.1% | 0 | 0.0% | 0 | 0 |
| general_model | 0.70 | 63 | 1 | 63 | 98.4% | 13 | 20.6% | 13 | 0 |
| general_model | 0.80 | 63 | 1 | 63 | 98.4% | 13 | 20.6% | 13 | 0 |
| general_model | 0.90 | 63 | 1 | 63 | 98.4% | 13 | 20.6% | 13 | 0 |
| general_model | 0.95 | 63 | 1 | 63 | 98.4% | 13 | 20.6% | 13 | 0 |

## T5c — Jev coverage under each confidence convention

This is the sensitivity that governs the whole escalation story. Jev publishes **no confidence field for `noul` questions**, and 50 of the 64 cases are `noul`.

| convention | pool | thr 0.70 | thr 0.80 | thr 0.90 | thr 0.95 |
|---|---|---|---|---|---|
| reported | 14 | 20.3% / 0 err | 20.3% / 0 err | 20.3% / 0 err | 20.3% / 0 err |
| derived | 50 | 54.7% / 4 err | 50.0% / 3 err | 39.1% / 0 err | 18.8% / 0 err |

| question type | cells | with API-reported confidence |
|---|---|---|
| choice | 12 | 12 |
| noul | 50 | 0 |
| score | 2 | 2 |

> A high coverage at 0 errors under 'derived' is evidence that the DERIVED quantity separates answerable from unanswerable cases — not evidence that Jev can support escalation, because Jev emitted a confident label on every unanswerable case it was given.

> The mixed headcount of `general_model` is 63 not 64: one cell (`b-i03`) is a `empty_content` transport failure and has no label. Its coverage is flat across all four thresholds because its hard one-hot decode always yields a derived confidence of exactly 1.0.
