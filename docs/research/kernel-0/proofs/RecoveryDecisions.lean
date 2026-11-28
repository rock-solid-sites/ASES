import Lean

/-!
The greatest stable region for repeated must-answer recovery.
Belief construction and correspondence to a native transition relation are
premises at the interface. Nothing in this file assigns a storage layout.
-/

namespace Kernel0.RecoveryDecisions

structure Interface (Belief Input Action : Type) where
  admissible : Belief → Input → Prop
  permitted : Belief → Input → Action → Prop
  next : Belief → Input → Action → Belief → Prop

variable {Belief Input Action : Type}

def step (model : Interface Belief Input Action)
    (region : Belief → Prop) (belief : Belief) : Prop :=
  ∀ input, model.admissible belief input →
    ∃ action, model.permitted belief input action ∧
      ∀ future, model.next belief input action future → region future

theorem step_mono (model : Interface Belief Input Action)
    {smaller larger : Belief → Prop}
    (included : ∀ belief, smaller belief → larger belief)
    {belief : Belief} (nextInSmaller : step model smaller belief) :
    step model larger belief := by
  intro input admissible
  obtain ⟨action, permitted, remaining⟩ := nextInSmaller input admissible
  exact ⟨action, permitted, fun future follows => included future (remaining future follows)⟩

def viable (model : Interface Belief Input Action) (belief : Belief) : Prop :=
  ∃ region : Belief → Prop, region belief ∧
    ∀ current, region current → step model region current

theorem every_viable_view_can_step (model : Interface Belief Input Action)
    {belief : Belief} (initial : viable model belief) : step model (viable model) belief := by
  obtain ⟨region, grounded, closed⟩ := initial
  exact step_mono model (fun next member => ⟨region, member, closed⟩) (closed belief grounded)

theorem viable_fixed_point (model : Interface Belief Input Action) (belief : Belief) :
    viable model belief ↔ step model (viable model) belief := by
  constructor
  · exact every_viable_view_can_step model
  · intro allowed
    refine ⟨step model (viable model), allowed, ?_⟩
    intro current nextAllowed
    exact step_mono model (fun _ => every_viable_view_can_step model) nextAllowed

def survives (model : Interface Belief Input Action) : Nat → Belief → Prop
  | 0 => fun _ => True
  | n + 1 => step model (survives model n)

theorem viability_implies_each_finite_horizon (model : Interface Belief Input Action)
    (n : Nat) {belief : Belief} (initial : viable model belief) : survives model n belief := by
  induction n generalizing belief with
  | zero => trivial
  | succ n prior =>
    exact step_mono model (fun _ member => prior member) (every_viable_view_can_step model initial)

theorem finite_horizons_decrease (model : Interface Belief Input Action)
    (n : Nat) (belief : Belief) :
    survives model (n + 1) belief → survives model n belief := by
  induction n generalizing belief with
  | zero => intro _; trivial
  | succ n previous =>
    intro next
    exact step_mono model previous next

theorem stabilized_horizon_is_exact (model : Interface Belief Input Action) (n : Nat)
    (stable : ∀ belief, survives model n belief → survives model (n + 1) belief)
    (belief : Belief) : viable model belief ↔ survives model n belief := by
  constructor
  · exact viability_implies_each_finite_horizon model n
  · exact fun stays => ⟨survives model n, stays, stable⟩

theorem policy_uses_only_belief_and_input (model : Interface Belief Input Action) :
    ∃ choose : Belief → Input → Option Action,
      ∀ belief input, viable model belief → model.admissible belief input →
      ∃ action, choose belief input = some action ∧ model.permitted belief input action ∧
        ∀ future, model.next belief input action future → viable model future := by
  classical
  let ready : ∀ belief input, viable model belief ∧ model.admissible belief input →
      ∃ action, model.permitted belief input action ∧
        ∀ future, model.next belief input action future → viable model future :=
    fun _ input h => every_viable_view_can_step model h.1 input h.2
  let choose : Belief → Input → Option Action := fun belief input =>
    if h : viable model belief ∧ model.admissible belief input
    then some (Classical.choose (ready belief input h)) else none
  refine ⟨choose, ?_⟩
  intro belief input survives admissible
  have h := And.intro survives admissible
  exact ⟨Classical.choose (ready belief input h),
    by simp only [choose, dif_pos h], Classical.choose_spec (ready belief input h)⟩

section ReleaseCounterexample

inductive RecoveryView where
  | initial | evidenceLost | oldAccepted | oldAbsent | finished
  deriving DecidableEq

inductive RecoveryInput where
  | finishRecovery | readOldOutcome
  deriving DecidableEq

inductive RecoveryAction where
  | disposeEvidence | carryEvidence | reportAccepted | reportAbsent
  deriving DecidableEq

open RecoveryView RecoveryInput RecoveryAction

private def recovery : Interface RecoveryView RecoveryInput RecoveryAction where
  admissible view input :=
    (view = initial ∧ input = finishRecovery) ∨ (view ≠ initial ∧ view ≠ finished ∧ input = readOldOutcome)
  permitted view input action :=
    (view = initial ∧ input = finishRecovery ∧ (action = disposeEvidence ∨ action = carryEvidence)) ∨
    (view = oldAccepted ∧ input = readOldOutcome ∧ action = reportAccepted) ∨
    (view = oldAbsent ∧ input = readOldOutcome ∧ action = reportAbsent)
  next view input action later :=
    (view = initial ∧ input = finishRecovery ∧ action = disposeEvidence ∧ later = evidenceLost) ∨
    (view = initial ∧ input = finishRecovery ∧ action = carryEvidence ∧
      (later = oldAccepted ∨ later = oldAbsent)) ∨
    (view = oldAccepted ∧ input = readOldOutcome ∧ action = reportAccepted ∧ later = finished) ∨
    (view = oldAbsent ∧ input = readOldOutcome ∧ action = reportAbsent ∧ later = finished)

theorem disposal_is_immediately_permitted : recovery.permitted initial finishRecovery disposeEvidence := by
  simp [recovery]

theorem loss_breaks_next_required_answer : ¬ survives recovery 1 evidenceLost := by
  intro canAnswer
  have inputValid : recovery.admissible evidenceLost readOldOutcome := by
    simp [recovery]
  obtain ⟨action, legal, _⟩ := canAnswer readOldOutcome inputValid
  simp [recovery] at legal

theorem disposal_cannot_preserve_viability :
    ¬ ∀ future, recovery.next initial finishRecovery disposeEvidence future → viable recovery future := by
  intro allRemain
  have nextLost : recovery.next initial finishRecovery disposeEvidence evidenceLost := by
    simp [recovery]
  exact loss_breaks_next_required_answer
    (viability_implies_each_finite_horizon recovery 1 (allRemain evidenceLost nextLost))

theorem preserving_evidence_keeps_recovery_viable : viable recovery initial := by
  refine ⟨fun view => view ≠ evidenceLost, by decide, ?_⟩
  intro belief preserved input admissible
  cases belief <;> cases input <;> simp [recovery] at preserved admissible
  · refine ⟨carryEvidence, by simp [recovery], ?_⟩
    intro future next
    simp [recovery] at next
    cases next <;> simp_all
  · refine ⟨reportAccepted, by simp [recovery], ?_⟩
    intro future next
    simp [recovery] at next
    simp [next]
  · refine ⟨reportAbsent, by simp [recovery], ?_⟩
    intro future next
    simp [recovery] at next
    simp [next]

end ReleaseCounterexample

#print axioms viable_fixed_point
#print axioms stabilized_horizon_is_exact
#print axioms policy_uses_only_belief_and_input
#print axioms disposal_cannot_preserve_viability
#print axioms preserving_evidence_keeps_recovery_viable

end Kernel0.RecoveryDecisions
