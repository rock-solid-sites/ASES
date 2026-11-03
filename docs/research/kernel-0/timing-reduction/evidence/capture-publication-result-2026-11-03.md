# Capture and publication cuts — bounded result (2026-11-03)

Preregistered at `53af2ce15`, based on `0d54fa63a`; the new standalone graph consumes the unchanged frozen catalog and `resolve`. It is an abstract model deliberately exposing piecemeal cuts, not a modification to or verification of the inherited flight model. The source-choice transitions abstract the availability of bits from two offered endpoint values; they do not model a physical sender, timing, encoding hazard, or framing protocol.

| Graph | Unique states / cuts | Transitions | Violating cuts |
| --- | ---: | ---: | ---: |
| Whole proposal capture | 5 | 4 | 0 |
| Independent-bit capture mutation | 11 | 10 | 2 |
| Whole successor publication | 3 | 2 | 0 |
| Split authoritative publication mutation | 5 | 5 | 2 |

All 24 unique graph states are designated observation cuts. The capture mutation combines the bits of actually offered pair values 0 and 3 into catalog values 1 or 2, each of which commits but was never offered. The control captures only an endpoint and matches that endpoint's oracle result. Publication mutation exposes `(1,0)` or `(0,1)` in the two orders en route to the oracle-designated `(1,1)`; both partial states satisfy the independent-profile state invariant, so legality alone does not establish whole-successor correspondence. The whole-publication control exposes the old state while the candidate is private and the full successor afterward. Oracle successor values are constructed by calling the same frozen oracle that defines the property; this tests sensitivity of the abstraction to these mutations, not independent oracle correctness.

Replay from worktree root: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/capture_publication_cuts.py --state-cap 1000'`. Complete: 24 discovered states, 21 traversed transitions, 24 cuts; Python elapsed 0.00037 s, peak RSS 12,416 KiB, exit 0. A separate `--state-cap 2` run exited 2 with explicit incomplete status, after two states, one completed transition and one observed cut; the rejected next state was `captured, 3`. Counts refer to distinct nodes and edges in these four finite graphs, not paths or all executions. See raw logs for all cuts and truncation cursor.

Fixture SHA-256 `d71fd7d90e74fea39e38ab68f33c4d7ce3df9cff129e3211a6e659100f864e35`; full raw log `ff27ab3782a5e15d0150c20160d462d27c2a642525df2956f48084b8a048373e`; truncation raw log `d8f9ec226bc9aa9385d7dc37e4c66e0db85193df149ca3171be8eeb309a85d13`.

These finite examples do not show how an actual capture/publication boundary is implemented or qualified, do not establish that another consumer cannot observe a private candidate, and do not establish the global candidate timing contract. A useful next discriminator is a bounded interacting request that reads an exposed partial successor: compare the correct hidden-candidate model against a mutant in which the partial view authorizes another catalog request, and require a common serial oracle witness. This would distinguish invalid observation from downstream authorization, without assuming physical implementation.
