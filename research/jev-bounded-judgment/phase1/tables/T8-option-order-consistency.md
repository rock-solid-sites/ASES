# T8 — Option-order and opaque-label robustness, plus position bias

## T8a — does renaming or reordering the options change the answer?

`opaque_labels` renames the option keys to content-free tokens (the label *text* is unchanged); `option_reorder` presents the same options in a different order.

| mechanism | controls | label stable | rate | base and variant both correct |
|---|---|---|---|---|
| prior | 4 | 4/4 | 100.0% | 1/4 |
| rule | 4 | 4/4 | 100.0% | 4/4 |
| lexical | 4 | 4/4 | 100.0% | 2/4 |
| jev | 4 | 4/4 | 100.0% | 4/4 |
| general_model | 4 | 4/4 | 100.0% | 4/4 |

## T8b — option-position bias (area D, 6 options, uniform = 16.7%)

A mechanism that always picked the same slot would put every cell in one histogram bucket. `chi2` is the descriptive distance from the expected-position histogram; **no p-value is reported** (n=12).

| mechanism | answered | options | uniform share | predicted position histogram | expected position histogram | pred == expected position | chi2 | df |
|---|---|---|---|---|---|---|---|---|
| prior | 12 | 6 | 16.7% | {'1': 1, '3': 10, '5': 1} | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | 3/12 | 22.8333 | 5 |
| rule | 12 | 6 | 16.7% | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | 12/12 | 0.0 | 5 |
| lexical | 12 | 6 | 16.7% | {'2': 3, '3': 4, '4': 3, '5': 2} | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | 4/12 | 4.8333 | 5 |
| jev | 12 | 6 | 16.7% | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | 12/12 | 0.0 | 5 |
| general_model | 12 | 6 | 16.7% | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | {'0': 1, '1': 2, '2': 2, '3': 3, '4': 3, '5': 1} | 12/12 | 0.0 | 5 |

> n_options is 6 for every area-D case, so uniform is 1/6 = 0.1667. A mechanism that always answered the same position would score far above uniform on the chi2. `rule` and `general_model` matching the expected position 12/12 is a strong result for them; for `rule` it is also partly tautological (see the honesty note).
