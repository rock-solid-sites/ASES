# Paired observation discriminator (2026-11-03)

Harness base `0be418c77` (original frontier `9d0ecf1ed`; previous counterexample commit `cbd0e22c1`). The original failing parent observation and old unsafe selector are retained. The repair at `9dc5b34dc` probes the fourth parent and supplies the active profile to `minimal_style`; it remains a one-alternative heuristic, not an algorithm that establishes minimality or sufficiency. Full successor comparisons can retain a field because that field is carried through, not necessarily because the operation depends on it. The frozen semantic oracle and ingress are untouched.

The separate `0be418c77` harness fix checks the deadline within the correspondence, residue, and mixed-offer traversals and skips noncanonical nonzero even state words while retaining the strict decoder. A 0.05 s internal deadline under an external 5 s/1 GiB cap stopped **incomplete** at independent word 25, next offer 63, with 14 legal states encountered and 1,987 offers completed (13 × 148 + 63); see `inner-deadline-probe.log`. The cursor is a diagnostic location, not a tested resume facility. Existing correspondence still compares oracle outputs derived from the same full state and must not be treated as a sufficiency proof.

## Independent paired-state oracle

For each selected mask and fixed request, compare two legal states only when their projected pre-states agree; compare the independently resolved outcome and projected whole successor. Masks are specified in the fixture, not selected by the heuristic. The original selector is reconstructed as an unsafe control; on the parent pair it omits `parents`, while the repaired selector includes it in both profiles. The small 4-state/profile run preceded expansion and completed 72 pair/mask/request checks under 10 s, 1 GiB and 72-case caps; it found 8 mismatches under rights only and none in 8 comparable checks under rights+parents.

The expanded 6-state/profile run completed 180 pair/mask/request checks with a cap of 180, 10 s timeout and 1 GiB address-space cap (12 legal states, two requests, two profiles, three masks). Python elapsed 0.0014 s, peak RSS 12,416 KiB:

| Mask | Equal pre-view comparisons | Mismatches |
| --- | ---: | ---: |
| rights | 60 | 26 |
| rights + parents | 24 | 4 |
| rights + parents + data | 8 | 0 |

The new mismatch is semantic under the frozen coupled-profile invariant: same rights and parent view, data `(0,0)` versus `(0,1)`, and `set x=1` commit versus deny. The data-bearing mask distinguishes those inputs. Its zero mismatches are evidence only for the 8 comparable checks in this fixture and two catalog requests, not a global sufficiency claim. Content and data variants are directly constructed and validated legal, rather than all being separately shown reachable. Exclusive profile, complete catalog, RTL correspondence, torn capture, partial publication and global timing reduction are untested.

The first expanded attempt (`pair_projection_scan_v1.py`, `pair-projection-expanded-v1-failure.log`) incorrectly asserted that rights+parents would remain sufficient; it failed. The revised scan retained this negative observation and added the data-bearing control. The separate 7-case cap run stopped incomplete exactly after 7 with its next pair/request/mask cursor in `pair-projection-truncated.log`. The earlier v1 small run and truncation are preserved with their corresponding script. Existing projection regression passed; the event/cut regression passed with 151 states and its stale-view counterexample, preserving its atomic-capture/publication limits.

Replay from worktree root: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/pair_projection_scan.py --states-per-profile 6 --pair-case-cap 180'`. Script SHA-256 `917c3eda21a31c72bed15d19c386bae3cc2499a050c39fc729a18ae0b157f3c6`; expanded raw log `35b63e01f97af1e7a96f6afe02be6c9d266d6aef1d0b8d5f978a04bceabd193d`; harness `c3a66af47758e4a724e80531ae4468a6dfce0f4f1b4179cf208549d7aed1854f`.
