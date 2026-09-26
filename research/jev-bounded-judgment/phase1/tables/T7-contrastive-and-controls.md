# T7 — Contrastive pairs and adversarial controls

## T7a — contrastive pairs (six families, each differing only in the deciding fact)

`distinguished` = the two members of the pair got different labels. `both correct` = the mechanism got both. The confidence verdict asks whether the confidence signal ranked the members the way the truth does, and only on pairs where the mechanism got exactly one right: **correct order** = the right member carries the higher confidence; **inverted** = the wrong member does; **tied** = identical confidence, so no ranking is expressed at all; **n/a** = confidence missing, or both / neither correct so there is no ranking to check.

| mechanism | pairs | distinguished | rate | both correct | one correct | neither | conf correct order | conf inverted | conf tied | conf n/a |
|---|---|---|---|---|---|---|---|---|---|---|
| prior | 6 | 0/6 | 0.0% | 0/6 | 6 | 0 | 0 | 0 | 6 | 0 |
| rule | 6 | 1/6 | 16.7% | 1/6 | 5 | 0 | 2 | 0 | 3 | 1 |
| lexical | 6 | 2/6 | 33.3% | 2/6 | 4 | 0 | 2 | 0 | 2 | 2 |
| jev | 6 | 5/6 | 83.3% | 5/6 | 1 | 0 | 1 | 0 | 0 | 5 |
| general_model | 6 | 6/6 | 100.0% | 6/6 | 0 | 0 | 0 | 0 | 0 | 6 |

## T7b — per-control behaviour, each control against its own base

`label stable` = the control did not change the label. `mean/min/max d(conf)` = the shift in the confidence the mechanism reports, control minus base. A control that is *supposed* to be inert (`irrelevant_change`) but moves the confidence is a finding; `missing_evidence` is *supposed* to move it, and a control where it does not is also a finding.

| mechanism | control | n | label stable | rate | correct | answered unanswerable | mean d(conf) | min d(conf) | max d(conf) |
|---|---|---|---|---|---|---|---|---|---|
| prior | irrelevant_change | 4 | 4/4 | 100.0% | 0 | 0 | 0.0 | 0.0 | 0.0 |
| prior | distractor | 2 | 2/2 | 100.0% | 1 | 1 | 0.0 | 0.0 | 0.0 |
| prior | noise | 2 | 2/2 | 100.0% | 1 | 1 | 0.0 | 0.0 | 0.0 |
| prior | opaque_labels | 2 | 2/2 | 100.0% | 1 | 0 | 0.0 | 0.0 | 0.0 |
| prior | option_reorder | 2 | 2/2 | 100.0% | 0 | 0 | 0.0 | 0.0 | 0.0 |
| prior | missing_evidence | 2 | 2/2 | 100.0% | 0 | 2 | 0.0 | 0.0 | 0.0 |
| rule | irrelevant_change | 4 | 4/4 | 100.0% | 4 | 0 | -0.5 | -1.0 | 0.0 |
| rule | distractor | 2 | 1/2 | 50.0% | 1 | 1 | 0.5 | 0.0 | 1.0 |
| rule | noise | 2 | 2/2 | 100.0% | 0 | 1 | 0.0 | 0.0 | 0.0 |
| rule | opaque_labels | 2 | 2/2 | 100.0% | 2 | 0 | 0.0 | 0.0 | 0.0 |
| rule | option_reorder | 2 | 2/2 | 100.0% | 2 | 0 | 0.0 | 0.0 | 0.0 |
| rule | missing_evidence | 2 | 1/2 | 50.0% | 0 | 2 | -0.5 | -1.0 | 0.0 |
| lexical | irrelevant_change | 4 | 4/4 | 100.0% | 4 | 0 | 0.0 | 0.0 | 0.0 |
| lexical | distractor | 2 | 0/2 | 0.0% | 0 | 1 | -0.1767 | -0.3333 | -0.0202 |
| lexical | noise | 2 | 2/2 | 100.0% | 0 | 1 | 0.0 | 0.0 | 0.0 |
| lexical | opaque_labels | 2 | 2/2 | 100.0% | 1 | 0 | 0.0 | 0.0 | 0.0 |
| lexical | option_reorder | 2 | 2/2 | 100.0% | 1 | 0 | 0.0 | 0.0 | 0.0 |
| lexical | missing_evidence | 2 | 2/2 | 100.0% | 0 | 2 | -0.0698 | -0.2286 | 0.0889 |
| jev | irrelevant_change | 4 | 4/4 | 100.0% | 4 | 0 | -0.01 | -0.04 | 0.0 |
| jev | distractor | 2 | 2/2 | 100.0% | 1 | 1 | 0.01 | 0.0 | 0.02 |
| jev | noise | 2 | 2/2 | 100.0% | 1 | 1 | -0.05 | -0.08 | -0.02 |
| jev | opaque_labels | 2 | 2/2 | 100.0% | 2 | 0 | 0.0 | 0.0 | 0.0 |
| jev | option_reorder | 2 | 2/2 | 100.0% | 2 | 0 | 0.0 | 0.0 | 0.0 |
| jev | missing_evidence | 2 | 1/2 | 50.0% | 0 | 2 | -0.07 | -0.52 | 0.38 |
| general_model | irrelevant_change | 4 | 4/4 | 100.0% | 4 | 0 | 0.0 | 0.0 | 0.0 |
| general_model | distractor | 2 | 2/2 | 100.0% | 1 | 1 | 0.0 | 0.0 | 0.0 |
| general_model | noise | 2 | 2/2 | 100.0% | 1 | 1 | 0.0 | 0.0 | 0.0 |
| general_model | opaque_labels | 2 | 2/2 | 100.0% | 2 | 0 | 0.0 | 0.0 | 0.0 |
| general_model | option_reorder | 2 | 2/2 | 100.0% | 2 | 0 | 0.0 | 0.0 | 0.0 |
| general_model | missing_evidence | 2 | 1/2 | 50.0% | 0 | 2 | 0.0 | 0.0 | 0.0 |

## T7c — controls that did not behave

Selected from the data, not written by hand. Two filters: a control that is *supposed* to be inert but moved the confidence by 0.05 or more while holding the label; and **every** `missing_evidence` cell, in either direction.

Grid-wide abstention picture: the corpus contains 70 unanswerable cells (14 unanswerable cases x 5 mechanisms). **69 of them received a label**, and **0 of 320 cells set the `abstained` flag**. The 1 cell(s) that emitted no label did so because the transport failed, not because the mechanism judged the question unanswerable: that is a missing answer, not an abstention. No mechanism in this grid recognised that a deciding fact had been removed. Where the confidence rose after the evidence was removed, the confidence is not tracking evidential support at all.

| mechanism | control | variant | base | pred base | pred variant | d(conf) | what happened |
|---|---|---|---|---|---|---|---|
| prior | missing_evidence | a-miss1 | a-h01 | no | no | 0.0 | evidence removed, confidence flat, still answered |
| prior | missing_evidence | b-miss1 | b-a01 | no | no | 0.0 | evidence removed, confidence flat, still answered |
| rule | irrelevant_change | c-i1 | c-p3a | yes | yes | -1.0 | supposed to be inert: label held, confidence moved |
| rule | irrelevant_change | c-i2 | c-p3a | yes | yes | -1.0 | supposed to be inert: label held, confidence moved |
| rule | missing_evidence | a-miss1 | a-h01 | no | no | 0.0 | evidence removed, confidence flat, still answered |
| rule | missing_evidence | b-miss1 | b-a01 | no | yes | -1.0 | evidence removed, confidence fell, still answered |
| lexical | missing_evidence | a-miss1 | a-h01 | no | no | -0.2286 | evidence removed, confidence fell, still answered |
| lexical | missing_evidence | b-miss1 | b-a01 | yes | yes | 0.0889 | evidence removed, confidence ROSE, still answered |
| jev | noise | b-noise1 | b-i02 | no | no | -0.08 | supposed to be inert: label held, confidence moved |
| jev | missing_evidence | a-miss1 | a-h01 | no | no | -0.52 | evidence removed, confidence fell, still answered |
| jev | missing_evidence | b-miss1 | b-a01 | yes | no | 0.38 | evidence removed, confidence ROSE, still answered |
| general_model | missing_evidence | a-miss1 | a-h01 | no | no | 0.0 | evidence removed, confidence flat, still answered |
| general_model | missing_evidence | b-miss1 | b-a01 | yes | no | 0.0 | evidence removed, confidence flat, still answered |
