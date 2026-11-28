import Lean

/-!
Cardinality obligations for recovering an already certified cut. This file
models counts. It assumes that the underlying placement may attain those
counts and that fault domains, identities, and certificates are bound correctly.
-/

namespace Kernel0.QuorumThresholds

def CrashThresholds (population failures write read : Nat) : Prop :=
  0 < write ∧ 0 < read ∧ write + failures ≤ population ∧
    read + failures ≤ population ∧ population < write + read

def ByzantineThresholds (population failures write read : Nat) : Prop :=
  0 < write ∧ 0 < read ∧ write + failures ≤ population ∧
    read + failures ≤ population ∧ population + failures < write + read

theorem crash_availability_iff (population failures : Nat) :
    (∃ write read, CrashThresholds population failures write read) ↔
      2 * failures + 1 ≤ population := by
  constructor
  · rintro ⟨write, read, lawful⟩
    unfold CrashThresholds at lawful
    omega
  · intro enough
    refine ⟨population - failures, population - failures, ?_⟩
    unfold CrashThresholds
    omega

theorem byzantine_availability_iff (population failures : Nat) :
    (∃ write read, ByzantineThresholds population failures write read) ↔
      3 * failures + 1 ≤ population := by
  constructor
  · rintro ⟨write, read, lawful⟩
    unfold ByzantineThresholds at lawful
    omega
  · intro enough
    refine ⟨population - failures, population - failures, ?_⟩
    unfold ByzantineThresholds
    omega

/--
Feasibility of an overlap given old-only, new-only, and common pools.
The private counts and the three common parts (old only, new only, both)
fully describe the relevant placement.
-/
def FeasibleOverlap (onlyOld onlyNew shared write read overlap : Nat) : Prop :=
  ∃ oldPrivate newPrivate oldShared newShared,
    oldPrivate ≤ onlyOld ∧ newPrivate ≤ onlyNew ∧
    oldPrivate + oldShared = write ∧ newPrivate + newShared = read ∧
    overlap ≤ oldShared ∧ overlap ≤ newShared ∧ oldShared + newShared ≤ shared + overlap

theorem cross_membership_overlap_lower_bound
    (onlyOld onlyNew shared write read overlap : Nat)
    (attainable : FeasibleOverlap onlyOld onlyNew shared write read overlap) :
    write + read - (onlyOld + onlyNew + shared) ≤ overlap := by
  obtain ⟨oldPrivate, newPrivate, oldShared, newShared, constraints⟩ := attainable
  omega

theorem cross_membership_overlap_is_attained
    (onlyOld onlyNew shared write read : Nat)
    (writeFits : write ≤ onlyOld + shared) (readFits : read ≤ onlyNew + shared) :
    FeasibleOverlap onlyOld onlyNew shared write read
      (write + read - (onlyOld + onlyNew + shared)) := by
  let oldShared := write - onlyOld
  let newShared := read - onlyNew
  refine ⟨write - oldShared, read - newShared, oldShared, newShared, ?_⟩
  dsimp [oldShared, newShared]
  omega

theorem enough_for_validation_can_fail_agreement :
    ∃ population failures threshold : Nat,
      failures < threshold ∧ threshold + failures ≤ population ∧
      2 * threshold ≤ population + failures :=
  ⟨4, 1, 2, by decide⟩

#print axioms crash_availability_iff
#print axioms byzantine_availability_iff
#print axioms cross_membership_overlap_lower_bound
#print axioms cross_membership_overlap_is_attained

end Kernel0.QuorumThresholds
