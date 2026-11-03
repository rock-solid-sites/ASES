# Revalidation versus withheld completion — preregistration

Source `ec2539717`, same coupled-profile initial `(0,1)`, `pair(1)` candidate `(1,0)`, consumer `set(y,1)`, and exposed partial `(0,0)`. The consumer resolves on the partial state and commits, restoring `(0,1)`. Compare three deliberately abstract continuation rules: blind remaining x write; re-evaluate the entire pair with the oracle on the then-current state; and leave the pair pending without publication or a completion outcome. Revalidation and withholding are experimental alternatives, not claims that a specific mechanism is necessary or sufficient.

| Continuation | Predicted consumer / pair outcome | Predicted final | Expected operation-only witness | Expected witness including observed partial `(0,0)` |
| --- | --- | --- | --- | --- |
| blind | commit / commit | `(1,1)` | none | none |
| revalidate | commit / commit | `(1,0)` | consumer before pair | none |
| withhold | commit / pending | `(0,1)` | consumer-only prefix | none |

A serial witness must preserve real-time constraints: the partial observation occurs before the consumer resolves; the pending pair may linearize before the observation, between observation and consumer, after consumer, or remain pending (only for the withheld variant). Model the explicit partial observation as an authoritative read, requiring equality with the complete oracle state at its linearized cut. Then independently enumerate all allowed orderings of the observation and completed operations respecting that constraint, replay each operation with the frozen oracle, and match observed outcomes, final state and, when requested, observed read. For operation-only matching omit the read but preserve all operation outcomes and final state. This separates a hidden internal read from a reported authoritative cut. A pending pair can be omitted; do not count it as committed.

Limit 1,000 total logical graph states, 10 s wall, 1 GiB virtual memory; report distinct states, graph edges, cuts, witness candidates, exact incomplete cursor under a deliberate small cap, and raw evidence. No exhaustive claim beyond the fixed finite scenarios; no physical realization, universal timing reduction, or particular mechanism follows. The existing paired-mask result remains only a sampled comparison.
