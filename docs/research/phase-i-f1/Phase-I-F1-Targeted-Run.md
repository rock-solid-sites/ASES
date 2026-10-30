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
