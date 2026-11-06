---
title: Independent Phase I Native Integration Investigation
program: EDASES
layer: Research
document_type: Investigation
status: Experimental
authority: Derived
last_updated: 2026-11-06
---

# Result

**The pinned implementations cannot yet support the proposed common Work Unit execution
without additional trusted integration semantics and enforcement.** A small executable
composition of their real transitions is feasible. A full native protected Work Unit
integration is not established: the L5 experiment starts from a synthetic accepted-object
fixture, L6 owns a different lifecycle/domain, and F4 has a different authority contract.
No invariant was weakened, component replaced, or canonical policy changed.

The authorized fallback is therefore an adversarial review of the model-to-implementation
obligations, backed by a **partial native-component harness**. This does not prove that
every possible trusted composition is impossible. A bridge with an explicit effect,
identity, ownership and ordering contract could change the result; none is implemented
or verified by the pinned services.

The most direct continuation counterexample is in F1's wrapper: after an accepted pair
and a cold restart without original observations, a new acceptance returns COMMIT while
leaving the old incompatible evidence binding. The main composition counterexample is
L5 denial of D-write followed by F4 acceptance/publication of the same causal envelope.
Matching bytes and receipt hashes do not establish shared authority.

WHY: the real guards do not enforce the proposed cross-component relationships. WHAT:
18 completed native-process cases, exact persistent state, independent row readback and
separately derived observation rules. HOW CERTAIN: executed counterexamples within the
declared adapter interpretation; no universal or clean-room proof. WHAT-NOT-TESTED:
native F3 acceptance/confinement, hostile routes, physical power loss, witness nonrollback,
production deployment, or globally complete Work Unit state.

## Evidence and scope

Sources are frozen in [PLAN.md](PLAN.md): F1 `29ec3960…`, L5 `51b34afa…`, L6 `0f348fda…`,
F4 `26db6db3…`, receipt extension `9226cd4b…`. Base assurance is `7a264832…`.
The five full SHAs, executed dependency bytes and hashes are preserved in
[source-index.json](evidence/sources/source-index.json). No original checker or model
supplies the new observer's acceptance assertions. One old checker function is imported
solely as the instrument under adversarial test.

The architectural comparator is **Phase-I-Closure §7 C1–C13**, especially exact effect,
common order, full-path restrictions, compatible recovery, complete disposition,
retained observations and outcome uncertainty. **Phase-I-Verification F4** requires one
explanation of the whole history. Both were read at the pinned F1 commit. Kernel-0's
Evidence Packet and abstract-semantics assumptions distinguish authority from caller
identity, historical evidence from current permission, and local commitment from ACK.
The testing/debugging ontology at `f8c700af…` was consulted as a proposal, not policy.

The test adapter consumes the actually F1-accepted content and bundle. It initializes
the existing L5 fixture with those bytes and metadata, submits the bytes through L6's
real put transaction, and sends the full envelope through F4's real HTTP sink. Its
explicit alias file maps `work`/C/D, inventory name `x`, and sink C/p. **That file is a
test-only authority assumption**, not a mapping authenticated by the services. F1's two
finite strings, L5's fixed P/C/Q/D graph, and L6's flat file domain are unmodified.

The original L5 fixture uses the same test-only initialization principle. Its original
manager, commit, cold selection, permission checks and actual D-effect file are executed
unchanged. Native L4 bootstrap requires Landlock; this executor returned ENOSYS (38).
No confinement bypass was substituted. L6 and the F4 witness are also explicitly trusted
experimental services; the witness has no durable store or publisher authentication.

## Smallest observed counterexamples

Exact extracted witnesses and parent raw hashes are in
[counterexamples.json](evidence/analysis/counterexamples.json). These are shortest useful
suffixes from the preserved reachable prefixes, not globally proven minima.

1. **Recovered acceptance without a bundle.** Start from `(one, observations-for-one)`;
   restart with no `observations`; `accept(zero)` returns `outcome=commit`. Independent
   SQLite read shows content zero and stored binding one. The query says
   `incompatible_required_observations`. Supplied fresh observations give a paired
   COMMIT in the neighboring run. The original five C11 cases did not test continued
   acceptance after recovery; their bounded result is not retroactively falsified.
2. **Descendant denial, downstream effect.** Original sealed move P→Q retains read
   ceilings for C/D; original activation succeeds; D-write returns DENY. `/submit` with
   the same accepted bytes, opaque evidence and causal ID returns 201, and the witness
   publishes the exact journal hash. The native sink sees flat C/p version 1, not D's
   current authority. A source-authorized neighboring path also succeeds. This falsifies
   the proposed use-current composition, not F4's narrower flat-token contract.
3. **Local removal is not global removal.** Dispose and remove L6's local x/unit. L5's
   accepted object and active descendant remain. F4 accepts another same-envelope
   effect. The local L6 all-writer/enclosing-root premise is satisfied; identifying that
   local unit with the whole L5 Work Unit is the unsupported step.
4. **Stale L5 manager reports a move that did not occur.** A passes comparison and writes
   moved record2, then stops at the existing after-record gate. B activates old C-under-P,
   overwriting record2. A resumes and returns COMMITTED for move to Q. Cold state is
   active C-under-P. Its receipt hash even matches those wrong selected bytes. This is
   outside the original single-holder premise and demonstrates why it must be enforced.
5. **Non-accept evidence replacement.** A holder configured with a different future
   observation bundle reads the original accepted tuple correctly, then `restrict`
   rewrites that tuple despite unchanged accepted content. Same-bundle control preserves
   it. This exposes a missing configuration/evidence-lifetime contract, not provenance
   falsity established by the experiment. Supervisor truth was already an explicit premise.

Lost receipt and retry produced **two durable effects with the same request ID**, the
first with a 503 response and actual remote publication. This is permitted by the weak
profile; Phase-I-Closure §4 expressly disclaims automatic safe retry/exactly-once. It is
evidence against silently adding a stronger integration promise, not a new F4 defect.

## Claim disposition

| Claim and tested scope | Disposition | Evidence / remaining qualification |
| --- | --- | --- |
| F1 supplied pair survives selected before/after-COMMIT process kills | Supported within scope | Prepared retains old pair; durable retains new pair without reply. No physical power-loss result. |
| General continued acceptance always commits content with required observations | Contradicted for pinned wrapper | Cold no-bundle accept commits incompatible pair; fresh-bundle neighbor succeeds. This extends beyond original five-case evidence. |
| Accepted tuple immutable across arbitrary reconfigured non-accept holders | Contradicted | `restrict` replaces tuple. Allowed configuration lifetime/source semantics remain unresolved. |
| L5 move retains C/D attenuation under its single-holder contract | Supported within examined scope | Original whole move and activation deny D-write; no new concurrent or native-confinement assurance. |
| Same L5 manager safe under overlapping holders | Contradicted | COMMITTED move receipt with active C still under P. Original experiment excludes this configuration. |
| L6 local locked inventory excludes cooperative creator/remover phantom | Supported within scope | Guarded removal wins/creator denies; creator-first wins/removal denies. Detached mutation strands x and is correctly identified as invalid. |
| L6 local emptiness establishes all shared-identity Work Unit dependents disposed | Contradicted under proposed alias | L5 accepted object remains outside the local inventory. No native shared domain exists. |
| F4 local commit/publication/receipt distinction | Supported within selected scope | Success receipts bind exact bytes; real lost reply differs from rejection; rejection blocks later append and cold readiness. |
| F4 publication certifies source descendant authority or shared lifecycle | Contradicted under use-current composition | Source-denied and locally removed cases both publish. A receipt authenticates neither missing proposition. |
| Exactly-once retry under current F4 API | Not promised; contradicted if added | Same-ID retry after actual receipt loss duplicates effect. |
| Prior F4 checker accepts valid neighboring durable histories | Contradicted outside original selected traces | Correct rejection consumes volatile seq4; native journal 1,2,3,5 is rejected as noncontiguous. |
| Full F1/F3/F4 refinement, native isolation, nonrollback witness | Unresolved / not tested | Mapping and falsifiers provided; no whole-system simulation, source-binding proof or hostile-host evidence. |

## Instrument qualification and reproducibility

[native.py](native.py) executes component code as processes with real SQLite, files,
Unix sockets and loopback HTTP. [observe.py](observe.py) independently checks exact bytes,
opaque-world binding, path authority, aliases, local durable order and publication
responses. Eight altered-evidence controls are rejected. Valid neighbors include source
write authorization, fresh acceptance evidence, both safe inventory orderings, and a
correct denial between durable events. There is no cross-family or clean-room review.

[TRANSITIONS.md](TRANSITIONS.md) records the proposed map and the models' missing native
transitions. In particular, synthetic composition `append_event` does not check descendant
ceiling, and its object bit conflates unrelated persistent domains. More state exploration
does not establish the missing relation. The original source-specific projections remain
bounded evidence, not authoritative specifications.

`attempt-01` preserves a harness HTTP-name-shadowing error, not an implementation result.
`attempt-02` completed 16 cases with 77 managed children, peak two; `recovery-01` completed
two additional cases with six managed children, peak one. All were reaped; managed-child
stderr is empty. Bootstrap and read-only reader subprocesses are additional short-lived
processes recorded through their outputs/commands, not included in that count. Native
campaign runtime was approximately 5.89s plus 0.81s; no CPU/memory/cost measurement is
claimed. Runtime: Python 3.12.14, SQLite 3.53.1, Linux 6.18.57; executable hashes are in raw.
The final reproduction script re-executed those same 18 cases once after the harness's
bootstrap-evidence correction, preserving its separate capture as `reproduction-01`.
That repetition verifies reproducibility of the script; it is not additional independent
oracle evidence. The `stale-token`/sequence-gap cases use pre-grant version 0; actual
overlapping authorized stale writers are tested in L5, not claimed from those F4 cases.

Run [reproduce.sh](reproduce.sh) for a new capture. The committed captures can be checked
offline with the observer. The existing evidence-contract/capture verifier's 34 tests
passed; a separate complete-file-set SHA256 readback covers this evidence directory.
The classifier deliberately remains partially qualified/unresolved because oracle
independence is not independently established. Checksums establish captured-byte integrity,
not truthful source authority or research correctness. Evidence is committed to this
branch; off-provider archive/decryption/restore remains **not tested**.

## Prioritized remaining obligations

1. **Bind new acceptance to an available, validated evidence bundle.** Refuse continued
   acceptance without its required observations; define whether configuration may mutate
   old accepted tuples. Do not fix this by manufacturing evidence from the content hash.
2. **Define and enforce the common effect/authority interface.** Choose the declared
   use-current or exact-obligation contract. A D-origin use must be ordered with the
   relevant L5 authority and L6 lifecycle at F4 acceptance. A detached adapter check is
   insufficient; it becomes part of the TCB and needs commit-point fencing/exclusion.
3. **Establish one complete dependency/lifecycle domain.** The smallest architectural
   change is an authoritative identity/domain binding used by admission and removal,
   with all imported/candidate/accepted material accounted for. It need not be one
   database, but a copied label cannot synchronize two independent unit lifecycles.
4. **Enforce L5 writer exclusion or atomic current-state publication.** Include compare,
   record naming and selector update in that exclusion. Hash matching is not enough.
5. **Specify allowed cross-store committed prefixes and outcome queries.** F1 commitment,
   L5 import, L6 registration and F4 publication are different commits. Refuse a whole
   atomic-transfer promise until those prefixes and recovery are supported. Select any
   stronger deduplication contract explicitly; the baseline permits duplicates.
6. **Rebuild the refinement domain from those interfaces.** Include missing-evidence
   acceptance, non-accept evidence writes, overlapping managers, valid sequence gaps,
   lost-ACK readback and multiple physical domains. Qualify against independent native
   witnesses and clean-room review before treating a safe abstract run as conformance.
7. **Then test stronger premises.** Native confinement/source authenticity, stable-root
   and inode custody, persistent independent witness/currentness, true power loss and
   external archive restore remain separate obligations. No provisioning was attempted.

These are scoped implementation/proof recommendations. They do not add Kernel
primitives, mandate a database/language, or authorize an ASES-wide policy change.
