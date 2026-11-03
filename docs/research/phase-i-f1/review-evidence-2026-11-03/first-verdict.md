# First verdict — source-only, before reading run outputs

Time: 2026-11-03T20:08:50Z
Target: 89db5e03380b9420d0e54c0e11e459fd079b3329
Baseline: 651a740be (new F1 scripts only)

## Verdict

The SQLite capacity competitor is an actual two-subprocess SQLite experiment in source, and its design appears capable of discriminating the selected claim: the reference reads capacity after `BEGIN IMMEDIATE` and inserts reservation plus effect in one commit; the detached mutant observes emptiness before that lock and then commits without revalidating. Source predicts one admitted protected-effect row in the reference and two in the mutant. This is a bounded concrete SQLite realization, not a general SQLite or C11 proof. I have not yet run it or observed the resulting DB/ACK/lifecycles.

The stale-disposition and active-capacity-reassignment controls are model-only at source level. They call the inherited Python F1 resolver for abstract authority transitions, while local Python wrappers store dependent-object/active-use state in ordinary sets/variables and manually reassign capacity state. They do not exercise SQLite or OS process races. Their controls appear to separate stale cached eligibility from current recheck, with positive removal/reassignment/use effects, but any conclusion depends on the resolver and wrapper model's premise that these selected wrapper effects represent the protected acceptance boundary. I have not yet run or independently challenged them.

Scope: this is an initial source-based verdict, not a conformance qualification. It does not establish the fixed claim for every ingress, all external effects, or arbitrary implementations. The selected premise still needs examination: is the chosen actual SQLite transaction the acceptance boundary, and do the two accepted rows materially represent the required protected effect? The next discriminator is running only the source scripts from a disposable `/tmp` copy, independently observing committed store rows before ACK, child exits, and then constructing one direct SQLite bridge counterexample (a writer/change between observation and lock) if needed.

## Source provenance

- `sqlite_capacity_competition.py`: SHA-256 `34e60b2c6a291fb1f2ec3cfdf2d9512fca931970cb7e78cab3d518fef42402df`
- `active_capacity_reassignment.py`: SHA-256 `cd2a4b57ea5454d85fce553990854c6c8a76f9d6858491b3d5c6ed1e489278ba`
- `stale_disposition_recovery.py`: SHA-256 `871b2f03f7ff2b470070523abac9d60250adaa3c7eb5cd5385bf3bf59dee4560`
