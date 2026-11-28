import Lean

/-!
Distinguishing two justified explanations from their observable evidence.
A per-probe product is valid only with the real joint-realizability premise.
-/

namespace Kernel0.DiscriminatingChecks

def NoCommon {Observation : Type} (first second : Observation → Prop) : Prop :=
  ¬ ∃ result, first result ∧ second result

def Product {Index : Type} {View : Index → Type}
    (possibilities : (i : Index) → View i → Prop) (report : (i : Index) → View i) : Prop :=
  ∀ i, possibilities i (report i)

theorem separated_by_one_probe {Index : Type} {View : Index → Type}
    (first second : (i : Index) → View i → Prop)
    (separated : ∃ i, NoCommon (first i) (second i)) :
    NoCommon (Product first) (Product second) := by
  rintro ⟨report, firstFits, secondFits⟩
  obtain ⟨i, cannotFit⟩ := separated
  exact cannotFit ⟨report i, firstFits i, secondFits i⟩

theorem product_separator_is_necessary {Index : Type} {View : Index → Type}
    (first second : (i : Index) → View i → Prop) :
    NoCommon (Product first) (Product second) ↔ ∃ i, NoCommon (first i) (second i) := by
  classical
  constructor
  · intro disjoint
    apply Classical.byContradiction
    intro noSeparator
    have common : ∀ i, ∃ result, first i result ∧ second i result := by
      intro i
      apply Classical.byContradiction
      intro missing
      exact noSeparator ⟨i, missing⟩
    let report (i : Index) : View i := Classical.choose (common i)
    exact disjoint ⟨report, fun i => (Classical.choose_spec (common i)).1,
      fun i => (Classical.choose_spec (common i)).2⟩
  · exact separated_by_one_probe first second

def same (report : Bool → Bool) : Prop := report false = report true

def opposite (report : Bool → Bool) : Prop := report false ≠ report true

def marginal (world : (Bool → Bool) → Prop) (probe observed : Bool) : Prop :=
  ∃ report, world report ∧ report probe = observed

theorem correlation_distinguishes_joint_reports : NoCommon same opposite := by
  rintro ⟨_, equal, unequal⟩
  exact unequal equal

theorem neither_marginal_distinguishes (probe observed : Bool) :
    marginal same probe observed ∧ marginal opposite probe observed := by
  constructor
  · exact ⟨fun _ => observed, rfl, rfl⟩
  · refine ⟨fun i => if i = probe then observed else !observed, ?_, by simp⟩
    unfold opposite
    cases probe <;> cases observed <;> decide

#print axioms separated_by_one_probe
#print axioms product_separator_is_necessary
#print axioms correlation_distinguishes_joint_reports
#print axioms neither_marginal_distinguishes

end Kernel0.DiscriminatingChecks
