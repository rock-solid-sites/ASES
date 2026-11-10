# Refuse unsupported selected-state interpretation

Frozen 2026-11-10. Base composed/admission `0e724a6c`. Comparator: Closure
C7/C9 and Verification T09: an unknown recovery interpretation cannot be called
current supported authority merely because its fields happen to be parseable.

Source inspection found that the admission port validates F1 root/profile/schema
but invokes L5 `graph_valid` without requiring the selected L5 schema supported
by this pinned experiment. That graph predicate checks topology and rights, not
schema meaning. A request presenting the actual hash of an unsupported selected
record can therefore avoid stale-hash rejection and still reach the same guard.

Use an explicit malformed/unknown-recovery-image control: keep actual accepted
bytes, observations, path rights and live L6 unchanged, but replace the selected
record's schema with a future integer, a string, a boolean, or omit it. Present
the updated actual generation hash. This is **not** an authorized native policy
migration or a new defect claim against the original L5 profile. It is a
discriminator for this adapter's unsupported-interpretation refusal obligation.

Record the current adapter's real HTTP behavior before changing it. The smallest
repair is a strict integer schema==1 check before current path admission. Retain
native append/publication and all existing guards. Valid schema 1 must still
admit; unsupported representations must leave the journal unchanged. A boolean
is not an integer schema even though Python equality considers True==1.

Run before/after native processes, exact generation/record readback and journal
comparisons. The independent checker derives schema type/value and expected
outcome from captured bytes, not the admission predicate. Altered controls must
reject. No general schema migration, source authentication, arbitrary corruption
repair or policy redefinition is added. Original branches/specifications stay
unchanged; this is another isolated disposable adapter experiment.
