# Stored-local predicate failure differs from tested protected widening

Sourcee5dc3b9. Command `python3 docs/research/phase-i-f1/round2_latent_diagnostic.py`.
Original first-context prefix grant P/SINK/R, grant C/SINK/RW, seal C, move C to Q
commits. C local latent R; D local latent RW but effective latent_chain(D)=R. Original
semantic helper C8 predicate reports false. All original model invariants still hold.

Continue actual Q grant/activation, descendant RW grant/write, read grant/use, D seal/
relocation back to P, D activation, explicit P widening and another D RW grant/write.
Reference denies both writes and admits both reads, including after D's later move and
ancestor grant widening. Original guard, separately restated use oracle and actual
resolve agree. latent_preserved=False mutation permits both writes under same schedule;
unrestricted P/C/D write positive commits. The weak checkpoint's local/effective
ceilings are both RW. Raw states/prefixes/helper/guard/oracle/results retained.

WHY: full-driver helper lacked witness detail; false representation predicate must not
be silently called a demonstrated protected-effect failure, nor silently ignored.
WHAT: small original reachable trace plus descendant later-relocation extension,
positive/negative/weak controls, exact executable/source identity. Certainty: executed
finite histories, no broad BFS rerun/independent review yet. Old AT-05 self-move is prior
evidence; this extension targets descendant and subsequent relocation/grant.

Interpretation: in this selected trace, stored local latent may exceed its effective
ancestor intersection while all tested reference uses remain restricted. The helper is
a stronger representation predicate than these tested effect observations establish.
This does not prove canonical policy permits every such stored state or universal C8
preservation, nor justify changing the checker to pass. No policy/model repair or
minimal schema proposal. Keep formal representation acceptance question open pending
governing interpretation/independent check; do not ask routine permission to keep safe
research moving. No physical/native/power-loss or generic F1/PhaseI closure.

Next: bounded independent source/requirement check of exactly this distinction. Separately,
C11 recovered read-only configuration has no original acceptance tuple; test new content
admission with unavailable required evidence rather than assuming startup type checks
cover that legitimate recovery mode. Do not spend further model budget doubling the
incomplete broad-context search solely to produce counts.
