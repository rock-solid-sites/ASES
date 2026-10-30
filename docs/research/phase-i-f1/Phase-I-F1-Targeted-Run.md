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
