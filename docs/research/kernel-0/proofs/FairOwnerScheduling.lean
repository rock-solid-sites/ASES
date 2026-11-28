import Lean

/-! Transport of scheduler obligations from global runs to local owners. -/

namespace Kernel0.FairOwnerScheduling

def Recurs (fact : Nat → Prop) : Prop :=
  ∀ start, ∃ index, start ≤ index ∧ fact index

def Stabilizes (fact : Nat → Prop) : Prop :=
  ∃ start, ∀ index, start ≤ index → fact index

theorem fairness_transports_if_trigger_and_action_transport
    (localTrigger globalTrigger : Prop) (localTaken globalTaken : Nat → Prop)
    (trigger : localTrigger → globalTrigger)
    (taken : ∀ index, globalTaken index → localTaken index)
    (globalFair : globalTrigger → Recurs globalTaken) :
    localTrigger → Recurs localTaken := by
  intro localEnabled start
  obtain ⟨index, later, fired⟩ := globalFair (trigger localEnabled) start
  exact ⟨index, later, taken index fired⟩

def AEnabled (_ : Nat) : Prop := True
def BEnabled (_ : Nat) : Prop := True
def ATaken (_ : Nat) : Prop := True
def BTaken (_ : Nat) : Prop := False

theorem scheduling_the_union_can_starve_an_owner :
    (Stabilizes (fun index => AEnabled index ∨ BEnabled index) →
      Recurs (fun index => ATaken index ∨ BTaken index)) ∧
    Stabilizes BEnabled ∧ ¬ Recurs BTaken := by
  exact ⟨fun _ start => ⟨start, Nat.le_refl start, Or.inl trivial⟩,
    ⟨0, fun _ _ => trivial⟩,
    fun recurs => match recurs 0 with | ⟨_, _, impossible⟩ => impossible⟩

def sharedOpportunity (index : Nat) : Prop := index % 2 = 0

theorem intermittent_opportunity_is_frequent_but_never_stable :
    Recurs sharedOpportunity ∧ ¬ Stabilizes sharedOpportunity := by
  constructor
  · intro start
    refine ⟨2 * start, by omega, ?_⟩
    unfold sharedOpportunity
    omega
  · rintro ⟨start, stable⟩
    have odd := stable (2 * start + 1) (by omega)
    unfold sharedOpportunity at odd
    omega

theorem continuous_local_enablement_needs_more_than_weak_global_fairness :
    (Stabilizes sharedOpportunity → Recurs BTaken) ∧
    ¬ (Recurs sharedOpportunity → Recurs BTaken) ∧
    ¬ (Stabilizes BEnabled → Recurs BTaken) := by
  have intermittent := intermittent_opportunity_is_frequent_but_never_stable
  have starvation := scheduling_the_union_can_starve_an_owner
  exact ⟨fun stable => (intermittent.2 stable).elim,
    fun fair => starvation.2.2 (fair intermittent.1),
    fun fair => starvation.2.2 (fair starvation.2.1)⟩

#print axioms fairness_transports_if_trigger_and_action_transport
#print axioms scheduling_the_union_can_starve_an_owner
#print axioms intermittent_opportunity_is_frequent_but_never_stable
#print axioms continuous_local_enablement_needs_more_than_weak_global_fairness

end Kernel0.FairOwnerScheduling
