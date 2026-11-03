# Ancestor state at protected use

**Status: bounded policy fix; no L5 host acceptance claim.** Commit `2e118966b` changes the use-time admission guard to require the requested unit and every ancestor through the root to be active and unsealed. Full-path grants and latent ceilings continue to attenuate the requested effect.

## Frozen-history reachability

The frozen L5 manager in `l5_integrated.py` exposes only `authorize_move` and `authorize_activate`. The latter activates and unseals every Work Unit. There is no manager operation that seals or inactivates an ancestor while leaving D active. The adversarial Q-sealed / D-active current record in `test_ancestor_use_policy.py` is therefore a policy input test, not a state shown reachable through the frozen manager protocol. No such reachability claim is made.

## Bounded checks

Run `python3 -m py_compile l5_integrated.py test_ancestor_use_policy.py` and `python3 test_ancestor_use_policy.py` from this directory.

The pure policy checks pass: compliant active-path use retains read; the existing latent ceiling continues to deny write; a sealed or inactive ancestor blocks use even when D is active and unsealed; an ancestor with no grants removes descendant read/write; and the prior D-only guard admits the sealed-ancestor case as a deliberately weakened mutant.

## Limits

These checks construct current-record values directly and do not exercise a concrete host confinement route. Landlock is unavailable in this environment (`ENOSYS` for syscall 444), so the integrated worker test is not rerun here. The canonical T11 text allows a separately authorized grant exception, but the frozen manager has no grant operation; this patch does not invent one. That exception remains unsupported and untested. No L5/L6/F3 acceptance, manager identity, crash durability, rollback, or production security claim follows.
