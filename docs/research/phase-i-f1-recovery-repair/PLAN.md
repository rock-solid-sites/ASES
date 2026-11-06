# F1 recovery repair — preregistered investigation

Experimental execution-engine work, based on PR #10 commit
`9077d672c186eaf4cc94585be9fccbd554920e30`. Work only on
`research/phase-i-f1-recovery-repair-20261106`; existing branches and original sources
remain unchanged. This is a bounded Python research variant, not production promotion.

## Phase 1, frozen before execution

Execute original C11 `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a` through a newly written
process/socket harness. Do not import the prior harness or checkers. Preserve SQLite
raw rows, exact requests/replies, source hashes, SQL traces and process outcomes.

Comparator: the same commit's Phase-I-Closure §3 (required accepted evidence is not a
cache), §7 acceptance/recovery and C1/C7/C9/C11/C12; original C11 PREREG and its explicit
trusted-supervisor/finite-current-holder scope. Prior interpretations are hypotheses.

Discriminators, each starting from a genuine accepted `(A, observations A)`:

| Case | Discrimination |
| --- | --- |
| Cold changed-content accept without observations | Paired denial versus COMMIT with incompatible old observations |
| Cold changed-content accept with observations B | Useful explicit acceptance must remain possible |
| Cold reads without observations | Recovery must not need an oracle replay or rewrite |
| Cold unchanged-content reacceptance | Existing sufficient observations may suffice; do not assume new evidence necessary |
| Invalid accept then valid accept with supplied B | Rejection must not poison later valid work |
| Reconfigured non-accept write | Configuration alone must not silently replace accepted evidence |

After these observations, freeze the smallest supported repair contract and exact
linearization point before implementing it. Preserve all original evidence. Stop if
required evidence-lifetime semantics cannot be derived; do not invent a new authority
rule, global lifecycle or Kernel primitive.

## Remaining authorized work

Repair and independently check missing/malformed/mismatched/stale-subject bundles,
same-byte opaque worlds, repeats, transaction failure, and actual pre/post-COMMIT kills.
Use invalid evidence controls and an implementation mutant; separate program behavior
from instrument errors and environmental assumptions. No physical power-loss claim.

Only after local F1 adversarial verification succeeds, freeze an L5 writer-exclusion
hypothesis and contract, then compare exclusive-writer protection with current-state
CAS/generation fencing. Any L5 candidate stays in an isolated experimental variant.
No native hostile-process confinement, cross-component repair, main merge or backup work.
