# L5 writer exclusion — frozen after F1 local verification, before L5 variant changes

Gate satisfied: `evidence/analysis/repaired.json` checks 24 F1 histories; five altered
evidence controls reject, and the independently checked live implementation mutant
reproduces the bad pair. This is bounded local evidence, not a full F1 proof.

## Failure hypothesis and comparator

Original L5 `51b34aface9340b7e6821b8c40dc62ca38da15e2` compares in-memory state against
CURRENT before publishing. Commit chooses the next record name from CURRENT. Two
managers can pass the same comparison, write the same record2 name, and publish a
receipt whose hash denotes the other manager's meaning. A's after-record gate permits
B to activate old C-under-P before A selects record2 and ACKs its alleged move to Q.

Closure C1/C2 require exact whole-effect fidelity and one coherent order; §1.1/H2
requires exclusion before replacement activation. Original single-holder tests expressly
exclude concurrent managers. Test the premise, do not redefine its assurance scope.

## Isolated candidates (original policy/commit code unchanged)

1. **Exclusive writer.** Same-root stable advisory `flock(LOCK_EX|LOCK_NB)` acquired
   before the manager exposes READY; held through validation, file publication and
   reply for that process lifetime. All management launchers must participate. Busy
   contenders refuse unchanged. Actual process death releases its open descriptor;
   test successful fresh admission after SIGKILL/reap at original publication gates.
2. **Generation reservation.** Before an original manager call, atomically reserve
   the currently selected generation using an O_CREAT|O_EXCL claim. Only that winner
   may publish its successor. Keep successful claims permanently so delayed writers
   cannot reuse an old generation. A normal denial may release its own unused claim
   while CURRENT is unchanged. An uncertain/crashed reservation is never automatically
   cleared. This is a real atomic *reservation fence*, not POSIX compare-and-replace
   of CURRENT. It must prevent same-generation record-name collisions and stale ACKs.
   Crash before selector advance may block progress; record that availability cost.

The native CURRENT helper has no conditional replacement primitive. A detached
read/recheck followed by os.replace is **not atomic CAS**. Do not label it as one.
A genuine direct CAS alternative must atomically couple expected-current validation,
immutable unique prepared bytes and selector publication at one defined point, including
crash handling. That is a remaining specification/proof option, not an assumed syscall.

## Fixed discriminators and expected distinctions

- Reproduce original after-record overlap: both calls return COMMITTED but cold parent
  is P; the receipt's matching hash must not hide wrong move meaning.
- At the same gate, an exclusive contender must refuse before READY. A generation
  contender may start read-only but must deny its mutation while the old generation is
  reserved. Resume the owner and cold-select parent Q with retained C/D restrictions.
- Uninterrupted move then separately authorized activation must succeed for both
  candidates. Denial-only candidates fail this neighbor.
- Kill the owner after record preparation but before CURRENT. Exclusive fresh admission
  should succeed from the old whole state after actual reap. Generation reservation
  should conservatively refuse rather than guess its stale owner dead; no silent reset.
- Kill after CURRENT publication: cold state must retain whole moved C/D; the next
  generation should admit a fresh authorized activation.
- Deliberately use the original unguarded manager as a competing writer. Both guards
  must be reported insufficient against that bypass. Neither is hostile confinement.

Preserve processes, exact selected/unselected bytes, lock/claim files, replies, gates,
cold state and source hashes. Select the smallest justified candidate for the disclosed
cooperative stable-root premise, or leave unresolved. Do not change F3/F4 global identity,
Kernel semantics, native confinement, source authentication or production implementations.
