# Bounded F1 repair contract — frozen after independent original reproduction

## Diagnosis and derivation

`evidence/original-02` reproduced six cases. Missing-bundle changed-content acceptance
commits an incompatible pair; fresh observations work; reads and unchanged reacceptance
work; invalid input does not poison a valid later acceptance. Reconfigured `restrict`
replaces required observations without a new content/evidence acceptance. `original-01`
is a sandbox Unix-socket EPERM infrastructure failure, not an F1 verdict.

The cause is **the experimental C11 wrapper**: `ObservedStore.write` rewrites evidence
for every state write if a configuration tuple exists, and skips it if absent. The
inherited holder's transaction and finite authorization policy do not promise C11's
additional evidence contract and have no knowledge of that optional configuration.
No SQLite malfunction or new Kernel defect is established.

Frozen comparator at `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`:

- Closure §3: "Consumer-required decision/evidence records are accepted contents, not
  disposable caches"; representation may vary, required observations may not disappear.
- Closure §7 accept: exact proposed/validated meaning, with required bytes/provenance
  retained. C1 requires a whole effect; C9 requires applicable premises; C11 retention;
  C12 recoverable-before-ACK. Recovery is not bootstrap or a fresh evidence oracle.
- C11 PREREG: supervisor supplies truthful opaque observations; no invention from the
  content/PID/rights. Its single current-pair/five-case experiment does not define
  arbitrary consumers, provenance authentication, or a global accepted-content schema.

These support a fail-closed wrapper and explicit evidence acceptance. They do **not**
authorize a timestamp expiry policy or decide semantic truth of opaque strings.

## Isolated variant and smallest supported rules

Reuse the original core, SQLite transaction, gates, query and reader unchanged. Add an
isolated wrapper, not a source overwrite. Its optional trusted configuration input is
`acceptance_bundle = {accepted_content: string, required: four original string fields}`.
The subject must match the proposed native content. An unbound legacy `observations`
configuration is not silently converted into a bound acceptance proposal.

| Operation | Rule |
| --- | --- |
| Read / ordinary recovery | No supplied original observations required; no migration, evidence rewrite, or evidence manufacturing. |
| Changed-content acceptance | Require a structurally valid, explicitly subject-bound new bundle. Missing, mismatched and malformed input denies the entire proposal. |
| Unchanged-content reacceptance without a new bundle | Retain the valid current accepted pair exactly; there is no new evidence assertion to manufacture. |
| Explicit same-content, different opaque bundle | A new guarded evidence acceptance; retain both distinguishable accepted pairs, select the newly accepted one. Identical bytes do not identify the evidence world. |
| Initial `establish`, which creates the core's first finite content | Require the initial trusted bundle for that content; initial empty bootstrap is separate from recovery. |
| Grant/restrict/unrelated operation | Preserve the accepted evidence exactly, regardless of a configured future bundle. |
| Detected incomplete/incompatible existing pair | No mutation may silently repair/discard it. Read can expose incompatibility; missing preparation/schema refuses ordinary startup. |

To honor the operator's **do not discard old observations** constraint without inventing
a disposition rule, retain distinct accepted pairs in one local append-only table.
This is representation, not a general event log or an extra authority primitive. Exact
duplicate pairs occupy one row; all previously accepted opaque worlds/bytes remain
observable. This costs one table and one INSERT per explicit new pair, all in the same
transaction. Removing it would lose old required observations when selecting a new pair.
Capacity/compaction and semantic disposition are not implemented or certified here.

An explicit `--prepare` step creates the variant's table and retains a currently valid
original pair, or prepares an empty trusted initial store. It refuses incompatible
material. Ordinary recovery never creates the table. Preparation has its own transaction
and does not alter the original kernel/observation rows. Original evidence is untouched.

## Commitment and uncertainty

The original `BEGIN IMMEDIATE` encloses current-pair inspection, proposal validation,
core UPDATE, current evidence INSERT/UPDATE and retained-pair INSERT. **The inherited
SQLite COMMIT is the linearization point.** A prepared kill must retain old pair/archive;
a post-COMMIT/pre-ACK kill must retain new pair/archive. SQL failure rolls back all
changes; it must not be relabeled a successful or uncertain commit without evidence.

The trusted supervisor still establishes the bundle's truth and applicability. A stale
bundle for A submitted as evidence for B is detectably mismatched and denied. A past
bundle for the *same immutable subject* is not intrinsically stale under Closure §5;
its semantic freshness cannot be inferred from opaque values. Test and disclose this
boundary; do not invent expiry/nonce authority to claim universal freshness detection.

## Adversarial acceptance, frozen before variant execution

Compare original and repaired paths for the six baseline cases. Add: absent/null/bad
shape/missing field/non-string/mismatched/stale-subject bundles; explicitly accepted
different opaque worlds with equal bytes; duplicate requests and repeated no-bundle
recoveries; invalid then valid work; unrelated writes with a future bundle; actual
prepared/durable SIGKILLs; injected SQL INSERT failure followed by valid fresh-holder
acceptance; explicit preparation of original valid/incompatible stores. The independent
checker reads raw rows/traces and implements these rules without importing the variant.
It must reject altered-evidence controls and a variant mutant that drops admission's
missing-bundle protection. Stop before L5 until this scoped verification succeeds.

WHAT-NOT-TESTED: semantic truth/authentication of trusted input, external freshness,
physical power loss, hostile storage/SQL writers, concurrency beyond original holder
scope, production migration/compaction, general F1 refinement or cross-component repair.
