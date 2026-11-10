---
title: Local inventory removal and the missing shared lifecycle boundary
program: EDASES
layer: Research
document_type: Investigation
status: Experimental
authority: Derived
last_updated: 2026-11-10
---

# Result and exact limit

Native L6 local removal does not establish global Work Unit removal. A fresh
history disposes and removes L6 x/unit while the asserted matching L5 accepted
reference and bytes survive. A small experimental joint inventory hook blocks
that local removal when the fixed foreign material is included in the native
transaction's scan. Twelve native histories pass the separate raw checker;
three altered-evidence controls reject.

**Genuine native shared-domain removal remains blocked.** L5 has neither a
protected domain-registration/import interface nor accepted-content/child
disposition. Even an initially empty object store still contains native child D
depending on C. The shared-unit port includes D and refuses. The positive empty
control is explicitly a narrower local inventory removal, not a global success.

## Implementation and order

`domain_worker.py` wraps the original L6 Store without changing its transaction,
COMMIT or cleanup code. For removal it takes the same stable L5 management lock
used by the admission prototype, then invokes L6's native BEGIN IMMEDIATE. The
inventory hook runs inside that transaction and includes selected accepted L5
references plus actual object material. Symlinks/unsupported types, missing
referenced bytes and changed root identity refuse; unknown files and even empty
directories block material emptiness. The client cannot supply an omitted root
list: the test supervisor fixes the participating roots in configuration.

Removal scope is explicit:

- `shared-work-unit`, the default, also includes native descendant D. There is
  no safe successful native completion for the occupied/fixed graph because
  the necessary L5 disposition transitions do not exist.
- `local-inventory` applies the joint material check and invokes only the native
  L6 removal. Its success says `native_global_destruction=false`. It does not
  destroy L5's metadata boundary or assert the child lifecycle complete.

The first ten-history run exercised the material guard. Source inspection then
identified the retained empty-child obligation. The final twelve-history run
adds that falsifier and an empty-directory control; it does not rewrite an
initial local success as evidence for a stronger global contract.

## Native observations

| History | Observation |
| --- | --- |
| Original local removal with foreign accepted L5 object | L6 COMMITTED/live=false while L5 reference and bytes remain |
| Same state through joint material guard | DENY, L6 live/dependencies retained; foreign scan observed inside transaction |
| Initially empty material domain, explicit local scope | Native local removal commits; a later creator denies |
| Initially empty material but native D remains, shared scope | DENY; inventory names `foreign-l5-child:D` |
| Creator commits first | Removal denies and dependent remains bounded |
| Remover pauses after scan inside transaction | Concurrent creator gets native SQLite lock failure; removal completes; later creation denies |
| Put process killed after file fsync before catalog COMMIT | Unregistered x survives; removal denies rather than treating absent row as emptiness |
| Disposition process killed after COMMIT before unlink | Removal denies while disposed bytes remain; separate native cleanup allows local empty removal |
| Selected L5 reference with missing bytes | Unresolved inventory, no removal; missing is not disposition |
| Unregistered L5 bytes or empty directory | Material check denies |
| F4 admission holds its guards before append | Joint removal returns busy; authorized effect then appends/publishes |
| Deliberate incomplete local-only removal before later use | The actual append guard refuses at L6 liveness, without treating old acceptance as current permission |

## Required real ownership interface

A real shared boundary must establish, before import publication, which owning
domain owns each accepted reference and its actual retained bytes. That binding
must come from a protected registrar or equivalent native acceptance transition,
not matching hashes or a caller alias. Every later durable creation, including
candidates and child units, must participate. The lifecycle verifier needs a
complete owning domain, not an executor-supplied subset.

An explicit authorized L5 content/child disposition must preserve required F1
source observations and other survivors. F1 source evidence is not transferred
to a different owning domain merely because its bytes were imported. Final
removal must order with imports, creates and protected effects at their declared
acceptance event. Unknown physical debris and unresolved local effects cannot
be silently dropped. If remote-visibility cancellation is additionally desired,
that is a separate contract: an already accepted local F4 effect can legitimately
publish later under the tested use-at-local-append interpretation.

These interfaces are requirements exposed by the native counterexamples, not
implemented authority mechanisms. A new universal graph, global transaction or
Kernel primitive is not established as necessary.

## Reproduction and assumptions

Run `python3 -B docs/research/phase-i-lifecycle-domain/probe.py --out <new-dir>`,
then `python3 -B docs/research/phase-i-lifecycle-domain/check.py <new-dir>/raw.json`.
Final raw frames/bytes, independent verdict and file hashes are in `evidence/`.
Original pins are L6 `0f348fda`, L5 `51b34afa`, F1 `29ec3960`, receipt `9226cd4b`;
the append hook is parent admission implementation `8ddca2fd`.

WHY: negative emptiness claims require a complete current domain, including
children and physical leftovers. WHAT: exact native file/catalog/process
observations and a guarded joint scan at L6's real transaction boundary. HOW
CERTAIN: evidence-based for the finite fixed-root histories. WHAT-NOT-TESTED:
authenticated native shared identity; complete all-writer/descriptor custody;
an L5 disposition implementation; hostile storage writers; physical power loss;
arbitrary overlap; distributed cancellation; or native global destruction.
The root map remains **test-only**. Advisory lock participation is a premise,
and the custody experiment demonstrates why that premise is not confinement.

No original source, frozen policy, parent branch, production service or CI was
changed. Continue to the bounded-launch engine slice after this demonstrated
native-interface blocker.
