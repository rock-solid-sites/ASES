# L6 local versus joint lifecycle domain — bounded experiment

Frozen 2026-11-10. Parent admission implementation `8ddca2fd`; original L6
`0f348fda050e67f3d9081a7fc22078eddc547a61`, L5 `51b34afa`, #11 `1970abe2`.
Comparator: Closure C1/C2/C5/C8/C9/C11, H13/H14 and Verification T12/T13/T15/T23
at `29ec3960`. No policy or original implementation is modified.

## Deciding question

Can L6's empty local catalog justify disposing the asserted shared L5/L6 Work
Unit? Fresh #10 replay says no: L6 removes x/unit, L5 retains the accepted
object and current descendant, and original F4 accepts another effect.
The smallest next step is a **test-only complete-domain adapter**, not a new
universal object identity. Its supervisor explicitly declares two participating
roots and the stable #11 L5 management lock. A current L6 removal may proceed
only when the selected L5 accepted references and actual L5 object subtree are
empty as well as the native L6 catalog/files. Missing referenced material is
inconsistency, not disposition. Unknown physical material also blocks removal.

## Reuse and linearization

Wrap original L6 Store, retaining its real BEGIN IMMEDIATE, inventory scan,
COMMIT and physical directory cleanup. Acquire the stable L5 writer guard
before invoking native removal. Add the fixed L5 inventory to the native scan
while its L6 transaction holds. All participating writers must use these guards;
this is the same L5→L6 order as the append-admission slice after its F1 lock.
Thus effect append and final local removal have a common order under this
cooperative finite profile. This is not confinement of an unguarded writer.

This Python module is a disposable integration experiment reusing the existing
Python workers. A rewrite would change the measured transaction boundaries.
Validate runtime inputs, retain exact frames/files, and make no production claim.
State is PRIMARY: local live/dependencies/disposed/files are distinct from L5
accepted references/objects and F4's local/published effect. No automatic bulk
disposition, implicit deletion, or irreversible cross-store transaction is added.

## Identity, ownership and what remains missing

The fixed root mapping is issued by the test supervisor, is marked test-only,
and is checked by device/inode. The client cannot omit roots or choose a smaller
dependency list. It does not prove genuine native shared identity or complete
custody. F1 source observations retain their source-domain meaning; an import
does not transfer their ownership or authorize deleting them.

Native L5 has no accepted-content disposition or lifecycle-domain registration
interface. Therefore an occupied L5 domain cannot successfully finish native
global removal in this experiment. Do not add a fixture deletion and call it
authorized disposition. An initially empty L5 fixture is a non-vacuity control,
not a demonstrated disposed formerly occupied L5 unit. Even there, native L6
removal does not destroy L5's metadata boundary. Result claims must say exactly
"local removal under a joint emptiness guard", never native global destruction.

A real implementation needs a protected registrar that binds imported subject,
retained bytes and owning domain before publication; admits every durable
creation; orders effect admission and disposition; and can demonstrate no omitted
root/descriptor/material. It needs a separately authorized L5 disposition step
that preserves required observations and survivors. Uncertain local F4 commits
remain accepted obligations; no remote cancellation promise follows from removal.

## Required native discriminators

1. Local-only removal succeeds with L5 survivor; joint guard denies unchanged.
2. Initially empty joint domain permits native local removal; creation afterward
   denies. Creator-first leaves a dependent and removal denies.
3. Removal scan paused inside transaction excludes a cooperative creator; after
   removal the creator cannot commit. No stale detached scan is used.
4. Kill a put after fsync before catalog commit; unknown material remains and
   final removal denies. Kill disposition after COMMIT before unlink; cleanup
   is separate, removal refuses until the material is removed.
5. Missing selected referenced L5 object and unknown L5 object both block.
6. An in-flight admitted F4 effect holds guards; lifecycle removal cannot enter.
   Removal before a later effect causes admission refusal. Post-local-commit
   remote visibility is not claimed cancelled.

Keep raw processes, bytes, SQL/gates and independently derived outcome checks.
Finish on these results or an exact blocker, then continue to engine Priority 5.

## Source-driven correction before final capture

The first ten-history run established the material guard only. Further native
source inspection exposed another necessary distinction: even with no accepted
objects, the fixed L5 graph still contains child D depending on C. Empty material
does not mean no child Work Units. L5 has no child disposition/removal transition.
The final port therefore distinguishes `shared-work-unit` (default; includes D
as a durable dependent and refuses) from `local-inventory` (explicitly narrower;
native L6 removal under the joint material guard). The initially empty positive
control uses only the latter. Add an empty-material/nonempty-child falsifier and
an unknown empty-directory control. This correction preserves C8 completeness;
it does not silently turn local removal into global destruction.
