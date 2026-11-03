# Three omitted-field outcome counterexamples

Preregistered at `c6076f260`. The rights+parents+data pre-state projection is insufficient to determine the outcome in each of nine reachable paired cases: three fixed offers in each of independent, coupled and exclusive profiles. All input pairs have identical projected pre-state but the first request commits and the second denies.

| Pair | Reachable histories and request | Fields differing |
| --- | --- | --- |
| Establishment | Empty versus established; request establish | `established` and `content` together |
| Content | Grant a0=7, optionally accept content 1; request resume with value 0 | `content` only |
| Issued history | Established versus grant-and-restrict a0; request grant a0=1 | `issued` only |

Augmenting the baseline mask by the named field distinguishes each pair. The content and issued cases are single-field interventions in the frozen state representation. The establishment case is deliberately weaker: the only legal absent state has content -1, while the established state has content 0, so adding either content or establishment separates that pair. It does not establish independent necessity of the `established` field given content. The histories, legal-state checks, catalog offers, full states, outputs and projected successors are recorded. These witnesses disprove sufficiency for this declared mask and interface; they do not prove a globally minimal mask or necessity for all requests.

All 9 cases/18 input states and 18 target resolutions completed in 0.0012 s Python time, peak RSS 12,416 KiB, under 10 s/1 GiB. Case cap 2 exits 2 with the exact next cursor. Construction uses committed catalog histories and shares the frozen Python oracle with the checks; no RTL, torn-read, or timing claim follows. SHA-256 script `98cda2838ac1fc2abb6a7be7989790992e8dec435dcb972735ec82010a9b1c17`; complete log `abc901e472c847651276f267fe6fdf81031b76feb833b62e1cb9037e796c8981`; truncation `e1fc3dc4cccab30a973666aa1770d747e8c3356fdaa0b9923e9dc9ad94058d4d`.

Next: distinguish whether a functional dependency in legal states makes the explicit establishment field redundant given content for these outcomes; test the invariant relation itself with bounded complete raw words or by direct definition, and do not generalize from these pairs alone.
