---
title: Phase I F1 — Finite Transition Model Design
program: EDASES
layer: Research
document_type: Research Finding
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 8
baseline_commit: 4e800957a673c8bd07eeea3c3c909349cdae76ac
plan_commit: 5c03a425fd5627c3764806292b8c5cb653498f4f
depends_on:
  - Phase I Core Substrate Verification Work (F1)
  - EDASES Phase I Core Substrate Closure (C1–C13, §7)
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - EDASES Work Unit Component Design (A–L)
  - Phase I Revocation Verification and Q1 Reduction (Part A AC, Part B D1/D2/D3)
related_documents:
  - EDASES Boundary-Composed Authority
  - Work-Unit-0 Foundational Reduction
implements: []
implemented_by:
  - docs/research/phase-i-f1/phase_i_f1_model.py
supersedes: []
superseded_by: []
last_updated: 2026-10-29
---

# Phase I F1 — finite transition model: design, mapping, observation relation

This note fixes the design of the executable model in
`phase_i_f1_model.py` **before** results are discussed. Results live in
[Phase-I-F1-Results.md](./Phase-I-F1-Results.md); raw evidence in
`Phase-I-F1-Results.json`.

Scope is exactly plan §2: a finite transition model, readable mapping of every
state variable and event to C1–C13, Work Unit K.1–20 and Kernel-0 V1–V6, the
trusted/failure premises, positive witnesses, and the abstraction/observation
definition. Nothing here is promoted into ontology: model variables are named as
model variables and each mapping line says which clause it is *a representation
of* and what it deliberately does **not** represent.

## 1. What the model is and is not

It is a **consumer instantiation** of the Kernel-0 `(σ, q, G, E, I)` contract for
the frozen Work Unit policy C1–C13, with the failure profile of closure §1.1
(executor loss, attachment loss, engine loss under D1+D2, loss during commitment,
missing/obsolete storage, lost sink reply) and the AC policy-ordering obligation.

It is not: a realization, a refinement proof, an unbounded induction, a
concurrency protocol, a scheduler, a storage format, or a claim about any host.
It is also not a second policy: when the frozen text is silent the model either
leaves the behaviour unconstrained and says so, or denies and says so.

## 2. Modelling decisions (each is a *choice*, labelled)

| # | Decision | Why it is safe / how it is disclosed |
| --- | --- | --- |
| D-1 | **Serialized Kernel.** One logical commitment boundary; every guarded event evaluates one coherent view and commits atomically. | Closure §1 says a single serialized holder is a sufficient comparator. This is why C2 (acyclic order) can be discharged as V3: a serialized holder composes into a total order. The model does **not** test concurrent-holder ordering. |
| D-2 | **Finite static boundary set** `{P,Q,S,C,D}`. Containment is a partial function `parent: W ⇀ W`. | Enough to distinguish two possible parents, a descendant, a sibling, several containment roots, empty sealed units. No dynamic creation of Work Unit identities (so "fresh identity" is a modelling premise, see T-2). |
| D-3 | **Grants are pairs `(capability, mode)`** with `capability ∈ {NET, SINK}`, `mode ∈ {READ, WRITE, BOTH}`. Effective use requires *local grant* ∧ *every ancestor grant* (intersection of modes). | Exactly the "effective(child) ⊆ effective(parent)" rule of Work Unit G.11. Local grants vary independently of ancestor ceilings. `NET` is the mediated read/write attachment; `SINK` is the external-effect attachment with the three contracts of closure §4. |
| D-4 | **Sealing = D1+D2**: an affected Work Unit admits no new capability use and no new protected outward effect. Internal CPU-only computation that was already running is a separate variable (`Computing`) and is untouched. D3 is **not** modelled (see §9). | Q1 disposition: baseline sealing does not stop computation. The design keeps a positive control history showing computation continuing while admission is disabled. |
| D-5 | **Management is an explicit grant `MGMT`**, separate from containment, provenance (`created_by`), and project. Initial management of each root is a declared trusted initial-state premise. | C3/K.12: containment is not management; created-by/project never confer it. The model never derives `MGMT` from `parent` or from a project field. |
| D-6 | **Latent structure** = one per-Work-Unit ceiling `latent: (cap, → mode)` applied to descendants and later activation. Reparenting computes it explicitly. | Closure §7 "for moves": latent retained restrictions survive relocation; a child whose write was blocked only by the old parent must not gain write under a permissive destination. The model keeps the latent value visible in the state so a reviewer can check it. |
| D-7 | **Content atoms x and y**, plus one durable *unaccepted candidate* `z`. Accepted content is immutable. `z` is confined and unaccepted; only an accept event turns it into x/y. | C5/C11, H14, T06/T23, K.16. There is no shadow copy of a disposed atom. |
| D-8 | **Capacity one**, conserved across a transfer. A parent allocation is **one** reserved unit; a child allocation is a *view* of the parent's reservation, not a second unit. Consumption requires a current allocation. | Plan §2 third bullet: allocation versus consumption are stated explicitly in the model (`alloc_owner`, `consumed`), and the invariant `alloc_owner → parent reservation` plus `consumed → alloc_owner` prevents double counting. |
| D-9 | **Replacement/authority representations**: in-flight requests carry `Evidence = (kind, generation)`, where generation is a foreign key into the revocation ledger. Validity = *issued now* ∧ *not revoked* ∧ *origin matches the current position for its kind*. | C6/T02/T03/T20. A retained old generation cannot resurrect: generations are never re-issued inside the state; the **weakened** policies expose the difference. |
| D-10 | **AC/C13**: the accepted-effects ledger enforces *per-use* current authority (policy `P-USE`), so a revoke whose ack precedes a later use excludes that use. AC policy changes are modelled as an event that must be ordered before they take effect (a pending AC change blocks substitution until committed) and that must be inside the trust boundary to count as exclusion-change; a partially applied AC change fails closed. | Closure §2 rule 7 and Phase-I-Revocation Part A. Whether a real host's policy change actually invalidates open handles is **not** modelled — only its ordering contract (see §9). |
| D-11 | **Sink contracts** are parameterized: `SINK-DECISION` (authority checked at commit; later acceptance by an old producer allowed), `SINK-USE` (authority checked at acceptance too). The model refuses `EXACTLY-ONCE` under either; duplicates/at-most-once are recorded, not assumed. | Closure §4 and T18/T19. This makes the same question askable under both contracts instead of silently choosing one. |
| D-12 | **Recovery** is explicit: `RECOVERY_PREPARE → RECOVERY_COMMIT → (RECOVERY_ACK | RECOVERY_LOSS) ×2`. Recovery material must be a *current* storage image, declared in the event. Storage material is either `CURRENT` or explicit `OUTSIDE_PROFILE`. | C7, T08/T09/T10. Recovery of an outside-profile image is counted as **unsupported**, not as a successful covered recovery. |
| D-13 | **Uncertainty** is a state bit (`ReplyState ∈ {definite, lost_reply}`) plus `GhostPossible` on sink use. A blind retry of an irreversible effect is denied by policy thereafter; an immutable read stays allowed. | C12/T17/T19. |

## 3. State variables and what they are

`S` is one frozen dataclass, serialized canonically (sorted, tuple-normalized)
so that state identity and hashing are stable across runs.

- **Containment / boundary records** per Work Unit: `present`, `parent`,
  `sealed`, `internal` (D-8 reservation), `created_by`, `project`,
  `attached_agent`; plus `route` (whether a live route handle exists).
  Baseline D1 includes `route: granted → excluded` at the sealing event.
- **Authority**: `grants[w]` (local pairs), `mgmt[w]` (management pairs with
  scope, D-9 generation), `latent[w]` (D-6 accepted ceiling), `revoked_gens`,
  `issued_gens`.
- **Content**: `content[w] = {atom: present}` for accepted atoms, `z[w]`
  (unaccepted durable candidate), `project_of[w]` record (metadata only).
- **Reservation** (D-8): `reserved_to` (one unit, per family), `consumed`.
- **Engine / access control**: `engine_up`, `ac_pending` (C13), `ac_policy`
  (inside/outside trust boundary).
- **Effect traces** (oracle side): `effects` (accepted ledgers), `applied[w]`
  (per-X observer bits), `ghost` (committed history kept *out* of σ; see *
  ordinary vs. ghost* below).
- **Uncertainty** (D-13): `reply_state`, `ghost_possible`.

## 4. Events (the `q` alphabet)

Every event is a *proposal* `q`, resolved by `resolve(σ, q)` into commit or deny.
Event names are model names; the mapping column in §6 gives the clause each is
a representation of.

| Group | Model name | Semantic content |
| --- | --- | --- |
| establishment | `establish(w)` | created empty, no parent, no grants, sealed/inactive (K.1) |
| containment | `attach_child(w, p)`, `detach_child(w)`, `move_child(w, p')`, `remove(w)` | forest changes; `move_child` is the whole transition of J; `remove` requires complete current disposition (C4/C8) |
| grants | `grant/widen(mgmt)` (add local grant), `narrow/revoke` (remove local grant), `seal(w)`, `unseal-activate(w)` | `grant` intersects with latent; `revoke` is a whole restriction with concrete route exclusion (D1) |
| management | `mgmt_grant(w, scope, origin)`, `mgmt_revoke(w, gen)`, `mgmt_revoke_ack(w, gen)` | C13 ordering: a use ordered after the ack cannot use the earlier permission |
| use | `use(w, NET, READ/WRITE)` | mediated protected use requiring local+ancestor grant, condensation of net capability |
| replacement | `revoke(w, kind, gen)` → `revoke_ack` → `reissue(w, kind)` | guarded replacement of a position; old generation revoked, new generation issued; no resurrection |
| engine | `engine_stop`, `recover_prepare`, `recover_commit`, `recover_ack`, `recover_loss` | failure profile; D1/D2 on stop; duplicate route removal on committed recovery |

## 5. Abstraction / observation relation

The observation relation `Obs(σ)` is the set of things the model asserts a
consumer may see, and the equivalence used to claim "observationally equivalent
recovery":

1. **Protected observations.**
   - `CapUse(w, cap, mode, X)` — an *accepted* use (whether the use is
     permitted; not the caller's expectations).
   - `SinkAccept(w, kind, X)` — a *committed sink effect*; the caller's
     awareness of it is a separate bit (`ReplyState`).
   - `Boundary(w)` — physical facts: present, parent, sealed, well-founded.
   - `Mgmt(w, scope)` — current management.
   - `GhostPossible` — whether the caller/source cannot rule out a lost reply.

2. **Non-observations** (interior edits, executor bytes, caches, derived views,
   transient attachments) are excluded by construction and by test: `x` accepted
   only after restart is not a witness; interior edits to metadata are rejected
   or leave `Boundary` unchanged; `derive` is a pure function of retained
   accepted state.

3. **Recovery equivalence.** For two recovered images `σ1, σ2` that the recovery
   procedure maps to the same `Obs`, the future `Obs` streams must be identical
   for every event suffix. The model checks this on a bounded suffix set
   (committed history vs. re-derived; recovered vs. non-interrupted).

   Within this slice the check is performed on **deadlock-freedom and
   post-conflict continuation** (the same `Obs` rules must admit the same future
   keep/split decisions), not on the pending content/derivation backlog in §6.

## 6. Backlog beyond this slice (explicitly not implemented)

The following plan §2 items are **not** in this slice and must not be read into
the results. They are queued for a second model revision:

1. Content acceptance, unaccepted durable candidate z, content retention under
   loss (T06, T23, C5, C11).
2. Capacity/reservation competition between C and S (T04 first half, C3).
3. Three concurrent proposals with a cyclic required order plus the independent
   control (T04 second half, C2).
4. Selected sink with dropped and surviving in-flight messages (T18, T19, C10,
   C12); the reply/uncertainty distinction.
5. Derived results, recomputation, scope-limited judgments and phantom/negative
   facts (T14–T16, T21, C9).
6. Interrupted disposition of dependents, and coupled move/recovery races
   (T12, T13).
7. Observational-equivalence checking of recomputed versus retained derivations.

## 7. Scope boundary of this note

No capacity arithmetic, sink contract, content or derivation claim is made here
until the corresponding item in §6 is implemented; see the results record for the
exact set of checks that were run.
