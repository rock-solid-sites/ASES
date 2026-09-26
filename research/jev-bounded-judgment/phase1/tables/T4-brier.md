# T4 — Brier score per mechanism

Lower is better; 0.0 is a perfect one-hot on the truth. Answerable cases with a usable prediction only.

| mechanism | Brier (all answerable) | n scored | noul | choice | score | train | dev | test |
|---|---|---|---|---|---|---|---|---|
| prior | 66.7% | 50 | 50.1% | 116.7% | 66.7% | 49.3% | 78.3% | 75.0% |
| rule | 28.2% | 50 | 37.1% | 1.2% | 30.4% | 23.6% | 35.7% | 26.5% |
| lexical | 56.4% | 50 | 40.5% | 102.1% | 66.7% | 36.8% | 67.4% | 67.3% |
| jev | 3.5% | 50 | 4.0% | 2.7% | 0.1% | 2.1% | 6.6% | 2.4% |
| general_model | 0.0% | 50 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

> sum over categories of (p - onehot)^2, un-normalised by category count; answerable cases with a usable prediction only. A general model decoded to a hard label therefore scores 0.0 by construction whenever it is right — that is an encoding floor, not perfect calibration. An ECE / reliability diagram is deliberately NOT reported: these vectors are P(label) under the model's own answer, not frequency forecasts, so binning them against realised frequencies would not be meaningful.

> `general_model` is decoded to a hard one-hot, so its Brier is 0.0 whenever it is right and 1.0 (2-way) / 1.8 (6-way routing) whenever it is not. It is an **encoding floor, not a calibration result**, and it is not comparable to a mechanism that emits a graded distribution.
