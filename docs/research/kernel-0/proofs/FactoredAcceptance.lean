import Lean

/-!
Exact acceptance and required success with independently observable checks.
Coherent and authentic observation acquisition is an independent premise.
-/

namespace Kernel0.FactoredAcceptance

def requiredProjection {Trial Index : Type} {View : Index → Type}
    (observe : (i : Index) → Trial → View i) (required : Trial → Prop)
    (i : Index) (input : View i) : Prop :=
  ∃ trial, required trial ∧ observe i trial = input

def compatible {Trial Index : Type} {View : Index → Type}
    (observe : (i : Index) → Trial → View i) (required : Trial → Prop)
    (trial : Trial) : Prop :=
  ∀ i, requiredProjection observe required i (observe i trial)

theorem each_required_trial_is_compatible {Trial Index : Type} {View : Index → Type}
    (observe : (i : Index) → Trial → View i) {required : Trial → Prop}
    {trial : Trial} (needed : required trial) :
    compatible observe required trial :=
  fun _ => ⟨trial, needed, rfl⟩

theorem every_preserving_factor_accepts_compatible {Trial Index : Type} {View : Index → Type}
    {observe : (i : Index) → Trial → View i} {required : Trial → Prop}
    {check : (i : Index) → View i → Prop}
    (preserves : ∀ trial, required trial → ∀ i, check i (observe i trial))
    {trial : Trial} (possible : compatible observe required trial) :
    ∀ i, check i (observe i trial) := by
  intro i
  obtain ⟨witness, needed, same⟩ := possible i
  rw [← same]
  exact preserves witness needed i

theorem factorization_exists_iff {Trial Index : Type} {View : Index → Type}
    (observe : (i : Index) → Trial → View i) (required candidate legal : Trial → Prop) :
    (∃ check : (i : Index) → View i → Prop,
      (∀ trial, required trial → ∀ i, check i (observe i trial)) ∧
      (∀ trial, candidate trial → (∀ i, check i (observe i trial)) → legal trial)) ↔
    (∀ trial, candidate trial → compatible observe required trial → legal trial) := by
  constructor
  · rintro ⟨check, preserves, safe⟩ trial available joined
    exact safe trial available (every_preserving_factor_accepts_compatible preserves joined)
  · intro safe
    exact ⟨requiredProjection observe required,
      fun _ needed => each_required_trial_is_compatible observe needed, safe⟩

structure Attempt where
  grantedRoute : Bool
  actualRoute : Bool

def routedCorrectly (attempt : Attempt) : Prop :=
  attempt.grantedRoute = attempt.actualRoute

def separateViews (i : Bool) (attempt : Attempt) : Bool :=
  if i then attempt.grantedRoute else attempt.actualRoute

theorem separate_route_checks_admit_mismatch :
    compatible separateViews routedCorrectly ⟨false, true⟩ ∧
      ¬ routedCorrectly ⟨false, true⟩ := by
  constructor
  · intro i
    cases i
    · exact ⟨⟨true, true⟩, rfl, rfl⟩
    · exact ⟨⟨false, false⟩, rfl, rfl⟩
  · change ¬ (false = true)
    decide

def pairedView (_ : Unit) (attempt : Attempt) : Bool × Bool :=
  (attempt.grantedRoute, attempt.actualRoute)

theorem paired_view_is_exact (attempt : Attempt) :
    compatible pairedView routedCorrectly attempt ↔ routedCorrectly attempt := by
  constructor
  · intro joined
    obtain ⟨witness, matching, same⟩ := joined ()
    have first := congrArg Prod.fst same
    have second := congrArg Prod.snd same
    exact first.symm.trans (matching.trans second)
  · exact each_required_trial_is_compatible pairedView

#print axioms each_required_trial_is_compatible
#print axioms every_preserving_factor_accepts_compatible
#print axioms factorization_exists_iff
#print axioms separate_route_checks_admit_mismatch
#print axioms paired_view_is_exact

end Kernel0.FactoredAcceptance
