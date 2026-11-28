import Lean

/-!
One-sided observations that hold at the effect time.
This logic does not produce authentication, clocks, or effect-side atomicity.
-/

namespace Kernel0.MonotoneEvidence

def Included {Atom : Type} (first second : Atom → Prop) : Prop :=
  ∀ atom, first atom → second atom

def MonotoneGuard {Atom : Type} (guard : (Atom → Prop) → Prop) : Prop :=
  ∀ {first second}, Included first second → guard first → guard second

def Compatible {Atom : Type} (lower upper actual : Atom → Prop) : Prop :=
  Included lower actual ∧ Included actual upper

theorem lower_bound_exact_for_allows
    {Atom : Type} (guard : (Atom → Prop) → Prop) (monotone : MonotoneGuard guard)
    {lower upper : Atom → Prop} (consistent : Included lower upper) :
    (∀ actual, Compatible lower upper actual → guard actual) ↔ guard lower := by
  constructor
  · intro universal
    exact universal lower ⟨fun _ fact => fact, consistent⟩
  · intro atLower actual bounds
    exact monotone bounds.1 atLower

theorem upper_bound_exact_for_denials
    {Atom : Type} (guard : (Atom → Prop) → Prop) (monotone : MonotoneGuard guard)
    {lower upper : Atom → Prop} (consistent : Included lower upper) :
    (∀ actual, Compatible lower upper actual → ¬ guard actual) ↔ ¬ guard upper := by
  constructor
  · intro universal
    exact universal upper ⟨consistent, fun _ fact => fact⟩
  · intro atUpper actual bounds atActual
    exact atUpper (monotone bounds.2 atActual)

def RecognizesSupport {Atom : Type} (family : (Atom → Prop) → Prop)
    (guard : (Atom → Prop) → Prop) : Prop :=
  ∀ actual, guard actual ↔ ∃ support, family support ∧ Included support actual

theorem positive_certificate_contains_support
    {Atom : Type} {guards : (Atom → Prop) → Prop} {family : (Atom → Prop) → Prop}
    (recognized : RecognizesSupport family guards)
    (lower upper : Atom → Prop) (consistent : Included lower upper)
    (anyPermit : ∀ actual, Compatible lower upper actual → guards actual) :
    ∃ support, family support ∧ Included support lower :=
  (recognized lower).mp (anyPermit lower ⟨fun _ membership => membership, consistent⟩)

theorem negative_certificate_intersects_every_support
    {Atom : Type} {guards : (Atom → Prop) → Prop} {family : (Atom → Prop) → Prop}
    (recognized : RecognizesSupport family guards)
    (lower upper : Atom → Prop) (consistent : Included lower upper) :
    (∀ actual, Compatible lower upper actual → ¬ guards actual) ↔
      ∀ support, family support → ∃ atom, support atom ∧ ¬ upper atom := by
  classical
  constructor
  · intro anyDenial support listed
    by_cases someAbsent : ∃ atom, support atom ∧ ¬ upper atom
    · exact someAbsent
    · have included : Included support upper := by
        intro atom supportMember
        by_cases inUpper : upper atom
        · exact inUpper
        · exact False.elim (someAbsent ⟨atom, supportMember, inUpper⟩)
      exact False.elim (anyDenial upper ⟨consistent, fun _ fact => fact⟩
        ((recognized upper).mpr ⟨support, listed, included⟩))
  · intro eachBlocked actual bounds accepted
    obtain ⟨support, listed, included⟩ := (recognized actual).mp accepted
    obtain ⟨atom, inSupport, absent⟩ := eachBlocked support listed
    exact absent (bounds.2 atom (included atom inSupport))

#print axioms lower_bound_exact_for_allows
#print axioms upper_bound_exact_for_denials
#print axioms positive_certificate_contains_support
#print axioms negative_certificate_intersects_every_support

end Kernel0.MonotoneEvidence
