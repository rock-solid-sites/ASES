import Lean

/-!
Modular safety with current and predecessor premises kept distinct.
A restore must be one of the checked transitions of the actual global history.
-/

namespace Kernel0.GroundedAssurance

inductive Reachable {State : Type} (initial : State → Prop)
    (step : State → State → Prop) : State → Prop where
  | origin {state} : initial state → Reachable initial step state
  | advance {before after} : Reachable initial step before → step before after →
      Reachable initial step after

theorem grounded_at_transition {Index State : Type}
    (property : Index → State → Prop) {before after : State} (rank : Index → Nat)
    (previous : ∀ i, property i before)
    (establish : ∀ i, (∀ j, property j before) →
      (∀ j, rank j < rank i → property j after) → property i after) :
    ∀ i, property i after := by
  have atLevel : ∀ level, ∀ i, rank i = level → property i after := by
    intro level
    induction level using Nat.strongRecOn with
    | ind level smaller =>
      intro i atHere
      apply establish i previous
      intro j below
      apply smaller (rank j) (atHere ▸ below) j rfl
  exact fun i => atLevel (rank i) i rfl

theorem guarantees_hold_at_every_reachable_cut {Index State : Type}
    (property : Index → State → Prop) (initial : State → Prop)
    (step : State → State → Prop) (rank : State → State → Index → Nat)
    (start : ∀ {state}, initial state → ∀ i, property i state)
    (localProof : ∀ {before after}, step before after → ∀ i,
      (∀ j, property j before) →
      (∀ j, rank before after j < rank before after i → property j after) →
      property i after) {state : State} (reached : Reachable initial step state) :
    ∀ i, property i state := by
  induction reached with
  | origin isInitial => exact start isInitial
  | @advance before after _ went prior =>
    exact grounded_at_transition property (rank before after) prior (localProof went)

def alwaysFalse (_ : Bool) : Prop := False

theorem mutual_current_implications_do_not_establish_either :
    (∀ i, alwaysFalse (!i) → alwaysFalse i) ∧ ¬ (∀ i, alwaysFalse i) := by
  exact ⟨fun _ unjustified => unjustified, fun claimed => claimed false⟩

def coherent (cut : Bool × Bool) : Prop := cut.1 = cut.2

def restoreFirst (prior present : Bool × Bool) : Bool × Bool :=
  (prior.1, present.2)

theorem mix_of_two_coherent_cuts_may_be_incoherent :
    coherent (false, false) ∧ coherent (true, true) ∧
    ¬ coherent (restoreFirst (false, false) (true, true)) := by
  exact ⟨rfl, rfl, Bool.noConfusion⟩

#print axioms grounded_at_transition
#print axioms guarantees_hold_at_every_reachable_cut
#print axioms mutual_current_implications_do_not_establish_either
#print axioms mix_of_two_coherent_cuts_may_be_incoherent

end Kernel0.GroundedAssurance
