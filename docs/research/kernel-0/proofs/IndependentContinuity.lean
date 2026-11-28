import Lean

/-!
Encoding lower bounds for independently replaceable consumer positions.
An exact decoder may be distributed across trusted components.
-/

namespace Kernel0.IndependentContinuity

theorem recoverable_information_is_injective
    {Position Representation : Type}
    (encode : (Position → Bool) → Representation)
    (acceptsOld : Representation → Position → Bool)
    (exact : ∀ live position, acceptsOld (encode live) position = live position) :
    ∀ {first second}, encode first = encode second → first = second := by
  intro first second encoded
  funext position
  rw [← exact first position, ← exact second position, encoded]

theorem reachable_profiles_need_different_encodings
    {Position Representation : Type}
    (encode : (Position → Bool) → Representation)
    (reachable : (Position → Bool) → Prop)
    (acceptsOld : Representation → Position → Bool)
    (exact : ∀ live, reachable live →
      ∀ position, acceptsOld (encode live) position = live position) :
    ∀ {first second}, reachable first → reachable second →
      encode first = encode second → first = second := by
  intro first second hasFirst hasSecond encoded
  funext position
  rw [← exact first hasFirst position, ← exact second hasSecond position, encoded]

def replace {Position : Type} [DecidableEq Position]
    (profile : Position → Bool) (position : Position) : Position → Bool :=
  fun other => if other = position then false else profile other

theorem replacement_only_changes_position {Position : Type} [DecidableEq Position]
    (profile : Position → Bool) (position : Position) :
    replace profile position position = false ∧
    ∀ other, other ≠ position → replace profile position other = profile other := by
  constructor
  · simp [replace]
  · intro other different
    simp [replace, different]

theorem independent_replacements_commute {Position : Type} [DecidableEq Position]
    (profile : Position → Bool) (first second : Position) :
    replace (replace profile first) second = replace (replace profile second) first := by
  funext position
  unfold replace
  by_cases firstMatch : position = first <;> by_cases secondMatch : position = second <;>
    simp [firstMatch, secondMatch]

def replaceAll {Position : Type} [DecidableEq Position]
    (positions : List Position) (profile : Position → Bool) : Position → Bool :=
  positions.foldl replace profile

theorem replaceAll_exact {Position : Type} [DecidableEq Position]
    (positions : List Position) (profile : Position → Bool) (query : Position) :
    replaceAll positions profile query = if query ∈ positions then false else profile query := by
  induction positions generalizing profile with
  | nil => simp [replaceAll]
  | cons head tail ih =>
    change replaceAll tail (replace profile head) query =
      if query ∈ head :: tail then false else profile query
    rw [ih]
    by_cases queued : query ∈ tail
    · simp [queued]
    · simp [queued, replace]

theorem shared_uniform_revocation_cannot_express_selective_replacement
    {Position Representation : Type} [DecidableEq Position]
    (first second : Position) (distinct : first ≠ second)
    (acceptsOld : Representation → Position → Bool)
    (uniform : ∀ repr, acceptsOld repr first = acceptsOld repr second) :
    ¬ ∃ repr, ∀ query, acceptsOld repr query = replace (fun _ => true) first query := by
  rintro ⟨repr, exact⟩
  have combined := uniform repr
  rw [exact first, exact second] at combined
  simp [replace, Ne.symm distinct] at combined

#print axioms recoverable_information_is_injective
#print axioms reachable_profiles_need_different_encodings
#print axioms replacement_only_changes_position
#print axioms independent_replacements_commute
#print axioms replaceAll_exact
#print axioms shared_uniform_revocation_cannot_express_selective_replacement

end Kernel0.IndependentContinuity
