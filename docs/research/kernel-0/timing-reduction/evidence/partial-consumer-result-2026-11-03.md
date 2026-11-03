# Partial-successor consumption and serial witness (2026-11-03)

Preregistration `63e36679e`, source `873aab539`; unchanged finite catalog and oracle. Three small logical traces in the coupled profile use an initial legal state `(x,y)=(0,1)`, whole proposal `pair(1)` and consumer `set(y,1)`. The two control traces explicitly construct a private candidate while leaving the authoritative state unchanged, then resolve the operations atomically in the two possible orders. The serial checker independently replays both whole-oracle orders from the initial state and matches both operation outcomes and the entire final state. It uses the same frozen semantic oracle, so independence refers to replay construction, not a second implementation of the semantics.

| Trace | Pair outcome | Consumer outcome | Final data | Serial witness |
| --- | --- | --- | --- | --- |
| Consumer, then pair | commit | commit | `(1,0)` | consumer → pair |
| Pair, then consumer | commit | deny | `(1,0)` | pair → consumer |
| Exposed partial, consumer, blind remaining write | commit | commit | `(1,1)` | none |

In the unsafe trace, the candidate first clears y, exposing legal `(0,0)`; the consumer commits and restores `(0,1)`; the remaining x bit is written blindly, producing `(1,1)`, which violates the coupled invariant. Neither oracle order yields that final state: both produce `(1,0)`, and one also denies the consumer. The model deliberately combines partial visibility with a stale, unvalidated remaining write. It demonstrates that combination's failure, not that observing partial state alone necessarily causes the same failure. The example has two operations and three mutant steps; no claim of mathematical minimality is made.

The bounded run completed 12 states/cuts, 9 edges, 6 operation outcomes, and two serial permutations per completed trace under a 1,000-state, 10 s, 1 GiB ceiling. Python reported 0.00038 s and 12,416 KiB peak RSS; exit 0. A separate cap-2 control exited 2 incomplete after two discovered states, one edge and two processed cuts, before the `consumer` edge. The counts cover only these three prescribed traces, not all interleavings. No physical behavior, implementation mechanism, global serializability, or general timing reduction is established.

Replay: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/partial_consumer_serial.py --state-cap 1000'`. Script SHA-256 `6c128975770818f03da452e276ed3b08418c4da2901167b2d4107d74dc46a0ee`; raw complete output `4289f5f7c00f31d51821b8303a830b41c619aec5204f87d0c68176b1e563ec91`; truncation `47d75a81e459382e6510745008ad41620d811eba188e48ba991ecb8e1a51cba2`.

Historical `parent_projection_probe.py` was separately replayed successfully from a temporary `cbd0e22c1` archive; raw output is `parent-projection-historical-replay.log`. The source-version note documents why its old assertion is expected to fail against the repaired harness.

Next discriminator: hold the same partial visibility constant while replacing the blind completion with revalidation or withholding completion, then compare outcome and final state to both serial oracle orders. This separates the contribution of partial consumption from the stale write; it is not a proposal of a particular physical mechanism.
