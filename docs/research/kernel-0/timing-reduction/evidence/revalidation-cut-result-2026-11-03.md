# Partial visibility under three continuations

Preregistered at `11112a2d8` against `ec2539717`. The coupled-profile fixture and oracle inputs are unchanged. In each graph an authoritative observation sees the same partial `(0,0)` before the consumer commits. Only the pair continuation changes. The independent serial replay enumerates completed operations and, separately, the observed read; it shares the frozen oracle with the graphs and respects the read-before-consumer edge.

| Continuation | Final | Operation-only witness | Witness including partial authoritative read |
| --- | --- | --- | --- |
| Blind remaining bit | `(1,1)`; invariant false | none | none |
| Revalidate whole pair | `(1,0)`; invariant true | consumer → pair | none |
| Pair stays pending | `(0,1)`; invariant true | consumer only | none |

The revalidation and pending variants avoid the stale-write failure in this fixture when judged by outcomes and final state. However, neither serial history can explain the explicit partial read: the coherent pre- or post-pair values are `(0,1)` and `(1,0)`, not `(0,0)`. This is a statement about a declared authoritative read; if the same internal value is unavailable as an observation and does not affect behavior, that read claim does not apply. Omitting the read yields a different, weaker observation interface. No particular revalidation or withholding mechanism is established as necessary, and no global contract is proved.

Complete run: 12 unique graph states/cuts, 9 edges, 12 candidate serial orders across the operation-only and read-aware checks, two completed operation outcomes each for blind and revalidate and one for the pending case. Bounds: 1,000 total graph states, 10 s, 1 GiB; Python 0.00041 s, peak RSS 12,416 KiB, exit 0. A cap-2 run stopped incomplete at stage 1 after two discovered states, one edge and two processed cuts, before the consumer edge. Neither run enumerates arbitrary concurrent histories.

Replay: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/revalidation_cut_scan.py --state-cap 1000'`. Script SHA-256 `ff9c73b6aca8fd494a6d4392391f155b04146ea1e3b1873b6d5814b92273a2eb`; raw output `5f5972774fcc6e603a55ac5989921f36646ba9e91c6057f19f72e8b9cffbda8e`; truncation `6b7966c380342d3fd2ee0ef6960b60206e9f012bd097a88b1ce2bab6c92df112`.
