# F3 lifecycle L5 policy conformance review

## Bounded outcome

**Conforms to the fixed claim within the source-level, serialized local profile represented by L5.** No counterexample was found for (1) preserving effective restrictions when sealed `C` moves from `P` to more permissive `Q`, (2) making a later grant affect only its named unit, (3) retaining each ancestor's restrictions in the effective permission calculation, and (4) checking that the manager's supplied state equals the selected published record before management operations. This is a bounded policy/source result, not host-confinement evidence or F3/F5 acceptance.

## First independent assessment (recorded before examining probe output)

The implementation appears aligned with Work Unit design §§G–J and Phase I T11 for its fixed `P/Q/C/D` fixture. A move calculates current effective rights for `C` and `D` before changing `C.parent`, writes those rights as each unit's latent ceiling, and publishes one moved state. Permission calculation walks from the target through every parent and intersects both grants and any latent ceilings. The later grant mutates only the target's ceiling after checking that the target already has the local grant and that its parent currently permits the capability. `enabled` additionally requires current ingress and every ancestor to be active and unsealed. The management path compares caller state with the selected `CURRENT` record before dispatching a management operation.

The main unrepresented condition is serialization: currentness comparison and publication are separate filesystem operations. The policy tests declare a single serialized holder and no concurrency claim. Manager identity and authority are represented by the literal principal `initial-manager` and a source-embedded test credential, so they do not establish real identity, secret protection, or independent authority. Source structure and test fixtures are fixed to four unit IDs and the two permissions `read`/`write`.

## Comparator and evidence

The fixed comparator was read from [Work Unit Component Design](../../docs/architecture/EDASES%20Work%20Unit%20Component%20Design.md), §§G–J, and [Phase I Verification](../../docs/architecture/core-substrate/Phase-I-Verification.md), T11. G requires no inherited authority and effective restrictions along the full containment chain; H requires sealing/revocation not to weaken descendant containment; I requires disposition of dependent contents; J requires a whole authorized move without accidental widening, with later reactivation/grants separately authorized. T11's discriminator is local `read/write` under P's read ceiling, movement under Q that allows both, then successful read and denied write unless separately granted, including D.

Source review:

- `l5_integrated.py:31–53` validates the fixed graph and intersects grants and latent ceilings for each unit up its ancestor chain.
- `l5_integrated.py:54–61` requires current ingress and an active, unsealed full path.
- `l5_integrated.py:85–104` checks published-state equality and performs the sealed move while preserving pre-move effective rights for C and D.
- `l5_integrated.py:105–121` restricts grant requests to C or D/write, checks local and parent authority, and changes only the requested unit's ceiling.
- `l5_integrated.py:122–130` activates only a current inactive sealed state in a separate commit.
- Source controls in `test_post_move_grant.py`, `test_ancestor_use_policy.py`, and `test_management_conformance.py` cover positive use, denial, an ancestor-sealing mutant, a descendant-widening mutant, stale state, and declared manager serialization.

## Probe outcome

All three source checks passed in a disposable `/tmp` copy of the relevant L5 source and its imported L1 module. The post-move/grant check exercised 11 denial cases, the positive sequence, and a deliberate mutant that lets C's grant widen D; the mutant produced D write permission and was detected. The ancestor check confirmed a sealed/inactive ancestor blocks D and that ancestor grant removal removes descendant permissions. The management check confirmed fresh management commits through the handler, stale caller state and wrong principal/credential do not mutate published bytes, and a C-under-P positive activation works.

The comparison sequence observed D as read-only after move, still read-only after granting C, and read/write only after separately granting D. Old ingress remained unable to use either permission. No disallowed prior RESULT, REVIEW, OBSTRUCTION, checkpoint, or builder log was read.

## Exact commands and raw process results

The source was copied to a temporary tree (the first attempt omitted the imported `l1.py` and failed at import before executing a check; the corrected copy included that source). The successful commands ran from `/tmp/f3-policy-source.cmW2ct/lifecycle/l5` under Python 3.12.14 on Linux x86_64:

```text
python3 -B test_post_move_grant.py
exit: 0
stdout: raw/test-post-move.stdout
stderr: raw/test-post-move.stderr (empty)

python3 -B test_ancestor_use_policy.py
exit: 0
stdout: raw/test-ancestor.stdout
stderr: raw/test-ancestor.stderr (empty)

python3 -B test_management_conformance.py
exit: 0
stdout: raw/test-management.stdout
stderr: raw/test-management.stderr (empty)
```

The raw stdout/stderr bytes are preserved under this report directory. Their SHA-256 hashes are:

| Stream | SHA-256 |
| --- | --- |
| post-move stdout | `82fe1f134d9500a293bb597b59eecfe84bf0d6c5e9c9d2031f8f57a995424732` |
| post-move stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| ancestor stdout | `4ed71aa30b2e02be6b8b1fbca09ab1c03094ac1f67fadbea8338eace64f3ee11` |
| ancestor stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| management stdout | `6b46dd62c818a85c378cfe9d2c4807265123ad366ca6f3e4b2529ff221310116` |
| management stderr | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Pinned source hashes

Review commit: `81ce1c2c6b5b7fe606efcfcfb0e35e6605d2d891`.

| File | SHA-256 |
| --- | --- |
| `docs/architecture/EDASES Work Unit Component Design.md` | `8f0fdd147122fd9d70ff308110b3a37dfd80627876c19cfa9d64657cc982f9ea` |
| `docs/architecture/core-substrate/Phase-I-Verification.md` | `f8dbf16606ad58072ec51dfc3306dfd6f55220aa3cb6952c9137790f86cbd13d` |
| `research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py` | `7216dbb401afa01c01ef5f72a5c45555d5525678799aa30164a7eafce4076fd8` |
| `research/phase-i-protected-work-unit-f3/lifecycle/l5/test_post_move_grant.py` | `fdb7d5569fb1a528771aa2da2898a85f4a7a93250ff366baea41559fad3b223e` |
| `research/phase-i-protected-work-unit-f3/lifecycle/l5/test_ancestor_use_policy.py` | `3b8ee7b4cd1302395382a72023dd162baafb3babc2a503d330ae3bc69d913589` |
| `research/phase-i-protected-work-unit-f3/lifecycle/l5/test_management_conformance.py` | `b8db19dacd218e73c1a888a6a5ca7a4ee7567f840e485055e92998db993b57f1` |
| `research/phase-i-protected-work-unit-f3/lifecycle/l1/l1.py` (temporary-copy import) | `000359c5f40a6d560940c356f3e4b08d8ce88e88e45cdf8ba7af9e8afe8d46f2` |

## Trusted inputs and limits

The claim depends on a correct and trusted `CURRENT` selector and selected record, integrity of the local protected store, the source's `initial-manager`/test-credential authorization predicate, and a single serialized manager/commit holder. The commit profile is same-filesystem `os.replace`; it does not establish fsync durability, crash recovery, rollback resistance, or race freedom with multiple writers. The tested graph is exactly P, Q, C, and D; the permission vocabulary is exactly read/write; the local-use path is the modeled socket mediator. Existing ancestor-policy tests include directly published malformed states and label them as unreachable through the frozen manager operations.

Landlock was unavailable for this task, so there was no host confinement, retained-handle, alias, descriptor-passing, process, network, or direct-write test. No physical manager identity or credential security was tested. This review makes no same-family qualification beyond the bounded source controls, no cross-family claim, and no F5 claim.

## Next smallest useful discriminator

The next discriminator is two concurrent manager attempts released after both have passed the current-record comparison but before either publishes. If the declared serialized single-holder profile is an enforced precondition, document the enforcement point and keep this result bounded to that profile; otherwise, demonstrate mutual exclusion or make compare-and-commit atomic so a stale concurrent grant/move cannot overwrite the newer published state.
