# Phase I F1 targeted run record

Status: PARTIAL; bounded finite evidence only. No unbounded proof claim.

Source SHA-256 after the two narrowly scoped corrections: 265c4eb0e2105452a6aadf562a83b4ee1e343d600350c0c081cacad7d9843c68.

Environment: Python 3.11; VPS worktree only; 1,000,000-KiB virtual-memory cap; 120-second timeout per small check; explicit 10,000-state cap for the context exploration.

Syntax: python3 -m py_compile docs/research/phase-i-f1/phase_i_f1_model.py — PASS.

Before correction, bounded context engine-loss-and-recovery reached the counterexample (stop, activate_image): image became mounted while engine enforcement stayed down, violating C6. The activation effect now sets engine and image together. Rerun: 16 reachable states, 78 committed transitions, 0 invariant violations.

Initial grant witness inspection found every grant denied because WU.latent defaulted to an empty tuple interpreted as no rights. The state default now explicitly carries NET and SINK RW latent ceilings as a trusted initial premise. This premise needs design/plan mapping and is not derived from the finite run.

Witness run: 10 named histories; 7 committed every event. WT-02, WT-03, WT-04, WT-05, WT-06, WT-08, WT-10 committed. WT-01 lacks a grant on the full ancestor path; WT-07 exposes a reversed pending-ack guard; WT-09 has an inconsistent delegation fixture. These are not successful witnesses and remain open.

A previous all-context invocation used timeout 120s and a 1,800,000-KiB virtual-memory cap, then terminated with MemoryError before producing output. It is incomplete and is not counted as a bounded result. The combined all-context driver has no per-context CLI and retains expanded state paths, so further exhaustive runs are paused pending bounded exploration/reporting changes.

Not tested: C1-C13 and A-L complete mapping, capacity/content/sink/derivation/concurrency obligations, intended destructive mutant validity, independent review, implementation refinement, power-loss/host assumptions, and any unbounded theorem.

## Coverage mapping and follow-up checks (2026-10-30)



This is a status mapping to the frozen plan, not a claim that every obligation is implemented.



| Target | Model representation / result | Status / gap |

|---|---|---|

| C1 | guard/effect and serialized event transition | partial; no exact protected-effect ledger or whole commitment |

| C2 | D-1 serialized single holder | assumption only; no cyclic multi-proposal or independent-transition fixture |

| C3 | grants and ancestor chain at use | partial; no resource/capacity allocation or consumption |

| C4 | fixed P/Q/S/C/D parent forest, cycle and removal guards | partial; no authoritative boundary metadata agreement |

| C5 | seal/stop and internal computation flag | partial; no accepted content retention or disposition |

| C6 | fixed generations and stale-origin rejection | partial; no live holder/route overlap oracle |

| C7 | stop/recovery/image activation events | partial; no current storage image or content/coupling equivalence |

| C8 | latent ceilings and sealed move | partial; descendant latent restrictions and final disposition unfinished |

| C9 | not represented | absent: truth/applicability, unknown and scoped judgments |

| C10 | SINK capability name only | absent: sink acceptance, visibility, delivery and failure contracts |

| C11 | partial WU boundary fields | absent: identity/provenance/project and consumer-evidence retention |

| C12 | management revoke/ack and recovery guards | partial; no lost reply, durable publication or irreversible effect |

| C13 | AC pending/request/apply bit | partial; no concrete access-control adapter, partial-apply or open-handle test |



| Work Unit section | Model representation / result | Status / gap |

|---|---|---|

| A — canonical empty bounded object | fixed WU records; WT-01 | partial; no general establishment/removal identity history |

| B — resource/attachment distinction | NET/SINK capability labels | absent: resource allocation distinct from exposure |

| C — execution independent of WU | thinking bits and stop witness WT-05 | partial; no real resource-backed activity or external routes |

| D — intrinsic boundary record | parent/sealed/grants/latent fields | partial; identity, created-by, project, attachment provenance omitted |

| E — currentness and recovery | fixed generation and image booleans | partial; no stale authentic image/currentness discriminator |

| F — restart sequence | recover_start/recover_step/activate_image | partial; events are largely no-ops and no discovery/validation stages |

| G — containment | parent forest, path grant conjunction | partial; no management-vs-containment complete policy or capacity |

| H — revocation/sealing | seal and stop | partial; descendant effect and retained contents absent |

| I — products/export/destruction | remove guard only | absent: content acceptance/export/disposition |

| J — reparenting | move + latent ceiling | partial; coupled whole move/recovery and descendants not covered |

| K — invariants 1–20 | selected K.1/K.7/K.8/K.11/K.12 representations | partial; remaining K obligations need named checks |

| L — current build boundary | no implementation realization | out of scope for this finite model; no prototype/refinement claim |



Retest after repairing the initial latent ceiling, recovery activation, ack guard, delegation guard and WT-01 full ancestor path: syntax PASS; 10/10 named witness sequences committed every event. This counts admission only; WT-05/WT-08 promised negative-use controls are not actually in their sequence and therefore are not counted as full semantic witness acceptance.



ATTACKS/negative mutation run: 11 attack histories, 10 weakened variants; only AT-02 ancestor ceiling and AT-09 complete-domain variants reached a distinct fault. The other 8 variants did not discriminate their intended fault and remain incomplete. Do not count them as controls.



Final mapped status: partial. Coverage table records omissions explicitly. No all-context run or proof claim.

## Additional latent-ceiling mutation and bounded-run update (2026-10-30)



A focused negative use after the WT-08 move initially committed incorrectly: the move retained only explicit latent metadata, not the old ancestors effective grant ceiling; use-time chain evaluation also ignored latent metadata. The move now retains the intersection of all old ancestor grants in the child latent ceiling, and use-time effective grants intersect latent ceilings. Retest: same AT-05 write attempt is denied in the reference; with latent_preserved=False the weakened trace diverges and AT-05 is now a valid discriminator.



Latest attack-report retest: 3/10 variants discriminate their named fault (AT-02, AT-05, AT-09). Seven remain invalid/non-discriminating.



Latest syntax check passed. The containment-and-grants context was run with a 10,000-state cap, 1,000,000-KiB memory cap and 120-second timeout; it raised state-bound-exceeded before completion. This is INCOMPLETE, not a pass. The 16-state recovery-context result was obtained before this latest change and must be rerun. Evidence is recorded here; no output was represented as exhaustive.

## Finite-context cap and retest record (2026-10-30)



The previously non-finite management/AC event loops were given explicit model horizons: management generation counter stops at MAX_GENERATIONS=4; AC epoch stops at MAX_AC_EPOCHS=2. These are bounded-context assumptions, not claims that production has these limits. They make the explored event relation finite for these variables.



| Context / check | Reachable states | Committed transitions | Violations | Status |

|---|---:|---:|---:|---|

| engine-loss-and-recovery | 16 | 78 | 0 | complete for this declared context and 10,000-state cap |

| replacement-and-management | 456 | 2,086 | 0 | complete for this declared context and 10,000-state cap |

| delegation | 120 | 502 | 0 | complete for this declared context and 10,000-state cap |

| containment-and-grants | >10,000 | n/a | n/a | incomplete; explicit state cap exceeded |

| all | >10,000 | n/a | n/a | incomplete; explicit state cap exceeded |



Each small context had a 1,000,000-KiB virtual-memory cap and 120-second timeout. Positive named traces retested: 10/10 commit all events. Mutants: 3/10 discriminate (AT-02, AT-05, AT-09). A direct post-stop use check denies with sealed-by-loss; AT-05 write-after-move denies in the reference. The named witness prose still overstates WT-05/WT-08 because those sequences do not themselves issue the corresponding negative use; the direct checks are separate and bounded.



No results JSON was generated: the model driver only writes at end, while aggregate exploration exceeds the state cap. The Markdown run record contains raw counts/counterexamples and explicit incompleteness. The final all-context profile is finite only under the generation/AC caps and is still not completely explored.

## Source and final bounded retest reference



Current model SHA-256 for the finite-context retests: 83827480e6825650717a719c4d9920d16591803d7017903bdece741dce9ae8aa.



Post-horizon syntax and targeted witness/mutation rerun: py_compile PASS; 10/10 named event sequences commit; 3/10 mutation variants discriminate (AT-02, AT-05, AT-09). Context counts above were collected against this model revision before formatting-only cleanup of the horizon guards; semantics unchanged.



The original aggregate script still has configured limits of 200,000–400,000 states per context and no global time budget; it was not rerun. Reaching an explicit 10,000-state cap is an incomplete result. The three completed contexts are small, separately invoked traversals, not the full plan acceptance.

## Accepted-content continuity milestone (2026-10-30)



Model SHA-256: dd3fe74dbb89e4276c2e5e3f830f71f4fce87e15bbe4eaf5acef724a34a22065.



Scope: one immutable atom x owned by C; one SINK attachment; fixed P->C containment; fixed authority position B at generation 3 and stale A evidence at generation 2. No other content atoms, mutation of bytes, or storage implementation is represented.



Named history (indices correspond to the content-continuity context): grant P/SINK RW; grant C/SINK RW; accept_x(C,B-gen-3); stop (accepting activity/engine holder lost); recover_start; recover_step(P); recover_step(C); activate_image (atomic engine+image activation seals all present Work Units); revoke old management generation 0; acknowledge revocation; attempt use_x(C,B-gen-3) while C is still sealed (denied: sealed); issue fresh management authority; explicitly activate P and C; attempt use_x(C,A-gen-2) (denied: stale-evidence); use_x(C,B-gen-3) (commits). The sole accept_x precedes stop; no content resubmission occurs.



Cold prefix check: accepted_x remains true and all Work Units are sealed after activate_image. Final state: accepted_x=true and one use observation (C,x,RW,B-gen-3). Denials: pre-reactivation sealed use and stale generation-2 use. Current generation-3 use succeeds after fresh management authority and explicit activation.



Bounded run: context content-continuity, state cap 5,000, actual 600 reachable states, 3,090 committed transitions, 0 invariant violations; Python syntax check PASS; 1,000,000-KiB virtual-memory cap and 120-second timeout. The context completed. No aggregate/exhaustive context was run.



Trust assumptions: accepted_x is an immutable durable-store abstraction owned by C; stop and cold recovery preserve its exact identity/value; the recovery image is current and compatible; generation-2 is stale and management reissue establishes current authority; the single serialized holder and guards are trusted. The model does not verify storage durability, bytes/hash equality, rollback resistance, host isolation, or authority service correctness.



Mapping: C1—accept/use are guarded transitions but no external whole-effect refinement; partial. C5—x remains bounded across stop/recovery and computation/execution holder loss; one-atom abstract evidence, not storage proof. C6—stale generation-2 ingress denied after fresh authority; no physical source binding. C7—cold recovery reaches sealed boundary and retained x; current-image/cut equivalence is assumed, not tested. C12—old management revoke acknowledgement precedes fresh authority; no lost reply/publication protocol.



Work Unit A—C remains a bounded object with accepted content; B—SINK is an exposed attachment, resource/attachment distinction not represented; C—stop loses activity while WU/content persists; D—parent/grant/seal fields stand in for boundary record, identity/provenance absent; E—currentness is fixed-generation premise; F—cold image activation is modeled and starts sealed, discovery/validation absent; G—path grants P/C checked; H—old management revoked and sealed recovery explicitly reactivated; I—x remains confined and is used internally, no export/disposal; J—no move in this history; K—partial witnesses for empty/content persistence, path, sealing/currentness, no full K.1–20 proof; L—no runtime/prototype claim.

## Scope-list synchronization



The executable scope list now includes the limited accepted-x continuity fixture. Rerun at model SHA-256 e0db7168b4b0684c1865f8baa3a6605c4d01077f7db0edeec76adbf2e107fa82: content-continuity context 600 states, 3,090 committed transitions, 0 invariant violations; syntax check PASS. This remains a single boolean atom/store abstraction, not byte-level or rollback evidence.

## Capacity-one reservation competition milestone (2026-10-30)



Model SHA-256: 9487921b8c8cbb554435e0b16075e069dedbe6a8d7608845a2d7e293dc25c064.



Fixture definition: P owns exactly one capacity unit. capacity_reserved is either None, C, or sibling S and represents allocation of that one P-owned unit as a child view. It is not a second global unit. capacity_consumed is a separate boolean indicating consumption of the same reservation; the invariant rejects consumption without an allocated owner. Thus allocated global units = 1 iff capacity_reserved is non-None, never parent reservation plus child allocation.



Named history: reserve_capacity(C) commits; competing reserve_capacity(S) is denied with capacity-unit-already-allocated; independent_change commits; consume_capacity(C) commits. Final state: owner C, consumed true, independent_changed true, invariant passes. The context graph reaches reservation winners C and S (and unallocated None), so the competing request order is not hard-coded by the transition system.



Bounded run: capacity-one context, 8 reachable states, 10 committed transitions, zero invariant violations; 10,000-state cap; 1,000,000-KiB virtual-memory cap; 120-second timeout. Syntax check PASS. This is a serialized allocation/consumption fixture only; no numeric quantities, resource interface, simultaneous execution, recovery or host enforcement is tested.



Mapping: C1—reservation and consumption are distinct committed transitions; no concrete effect refinement. C3—one conserved parent unit, exclusive child allocation, and authority-guarded mutation; narrow fixture only. C2—serialized order is assumed, no cycle attack yet.



Work Unit A—P/C/S bounded objects; B—resource allocation is represented as an unexposed reservation, no attachment; C—consumption is a state change, no running activity; D—parent relationship is the fixed fixture, not full boundary metadata; E/F—recovery not included; G—C and S are sibling allocation views under P; H—no revocation/sealing; I—no content/export; J—no move; K—partial capacity conservation invariant; L—no realization claim.



Trusted premises: initial P capacity is exactly one; serialized Kernel serializes competing requests; reservation assignment and consumption state are authoritative; only named C/S compete; independent_change is disjoint and management-authorized. Not tested: concurrency, rollback, storage, physical capacity, or schedulers.

## Three-pending-proposal cycle fixture (2026-10-30)



Model SHA-256: 3b0d71be6fa147b43cc63c45a1566b368f5c25e1e74bca05682ba2e47864daa3.



Cycle fixture: proposal 0 requires proposal 1 before commit; proposal 1 requires proposal 2; proposal 2 requires proposal 0. The named history proposes 0,1,2 before attempting any commit, so all three are pending at once. Commit attempts 0,1,2 are each denied with cyclic-predecessor-uncommitted (C2). A separate independent_change then commits while all three remain pending and uncommitted.



Bounded run: cycle-order context, 16 reachable states, 32 committed transitions, zero invariant violations under 10,000 states, 1,000,000-KiB virtual-memory cap and 120-second timeout. Syntax check PASS. Named history state: pending=(true,true,true), committed=(false,false,false), independent_changed=true; invariant passes.



Mapping: C2—cyclic precedence cannot be satisfied by a first commit; this is a serialized guard-level cycle fixture, not concurrent validation or a general serializability proof. C3—independent management-authorized change is accepted despite the pending conflict. Work Unit A/C—fixed bounded proposal state, no real processes. Work Unit K—one explicit cycle counterexample attempt and independence control; all other K claims remain outside this context.



Assumptions: one serialized Kernel; fixed predecessor relation; proposal registration does not itself commit protected effects; the independent change is disjoint and authorized. Not tested: concurrent holders, order graphs beyond this exact 3-cycle, scheduler fairness, rollback, or external effects.
