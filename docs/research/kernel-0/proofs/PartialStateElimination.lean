import Lean

/-!
Closed-cover characterization for deterministic partial interfaces.
A missing specification step imposes no obligation. This proof does not
establish that any caller can be excluded by a native implementation.
-/

namespace Kernel0.PartialStateElimination

abbrev Machine (State Input Output : Type) := State → Input → Option (Output × State)

variable {Reference Compact Input Output : Type}

def CoversEveryState (rep : Compact → Reference → Prop) : Prop :=
  ∀ reference, ∃ compact, rep compact reference

def CoversRequiredSteps (spec : Machine Reference Input Output)
    (rep : Compact → Reference → Prop) : Prop :=
  ∀ compact input,
    (∃ source output target, rep compact source ∧ spec source input = some (output, target)) →
    ∃ output next,
      ∀ source answer target, rep compact source → spec source input = some (answer, target) →
        answer = output ∧ rep next target

def PreservesRequiredSteps (spec : Machine Reference Input Output)
    (implementation : Machine Compact Input Output) (rep : Compact → Reference → Prop) : Prop :=
  ∀ compact source input output target, rep compact source →
    spec source input = some (output, target) →
    ∃ next, implementation compact input = some (output, next) ∧ rep next target

theorem closed_cover_iff_implementation (spec : Machine Reference Input Output)
    (rep : Compact → Reference → Prop) :
    CoversRequiredSteps spec rep ↔
      ∃ implementation, PreservesRequiredSteps spec implementation rep := by
  classical
  constructor
  · intro closed
    let implementation : Machine Compact Input Output := fun compact input =>
      if present : ∃ source output target, rep compact source ∧ spec source input = some (output, target)
      then some (Classical.choose (closed compact input present),
        Classical.choose (Classical.choose_spec (closed compact input present)))
      else none
    refine ⟨implementation, ?_⟩
    intro compact source input output target related required
    have present : ∃ state answer next, rep compact state ∧ spec state input = some (answer, next) :=
      ⟨source, output, target, related, required⟩
    have response := Classical.choose_spec (closed compact input present)
    let next := Classical.choose response
    have valid := Classical.choose_spec response source output target related required
    refine ⟨next, ?_, valid.2⟩
    simp only [implementation, dif_pos present, next, valid.1]
  · rintro ⟨implementation, preserves⟩ compact input ⟨source, output, target, related, required⟩
    obtain ⟨next, answered, _⟩ := preserves compact source input output target related required
    refine ⟨output, next, ?_⟩
    intro other answer successor relates must
    obtain ⟨otherNext, otherReply, otherRelated⟩ :=
      preserves compact other input answer successor relates must
    rw [answered] at otherReply
    have equal : (output, next) = (answer, otherNext) := Option.some.inj otherReply
    have sameOutput : output = answer := congrArg Prod.fst equal
    have sameTarget : next = otherNext := congrArg Prod.snd equal
    exact ⟨sameOutput.symm, sameTarget ▸ otherRelated⟩

section StrictCounterexample

inductive PaperState where
  | a | b | c
  deriving DecidableEq

inductive CompactState where
  | left | right
  deriving DecidableEq

inductive Command where
  | forward | back | inspectState
  deriving DecidableEq

inductive Answer where
  | ok | zero | one
  deriving DecidableEq

open PaperState CompactState Command Answer

private def model : Machine PaperState Command Answer
  | a, forward => some (ok, b)
  | b, forward => some (ok, c)
  | b, back => some (ok, a)
  | c, back => some (ok, b)
  | a, inspectState => some (zero, a)
  | c, inspectState => some (one, c)
  | _, _ => none

private def compactModel : Machine CompactState Command Answer
  | _, forward => some (ok, right)
  | _, back => some (ok, left)
  | left, inspectState => some (zero, left)
  | right, inspectState => some (one, right)

private def represents : CompactState → PaperState → Prop
  | left, s => s = a ∨ s = b
  | right, s => s = b ∨ s = c

theorem two_overlapping_states_cover : CoversEveryState represents := by
  intro state
  cases state
  · exact ⟨left, Or.inl rfl⟩
  · exact ⟨left, Or.inr rfl⟩
  · exact ⟨right, Or.inr rfl⟩

theorem two_overlapping_states_work : PreservesRequiredSteps model compactModel represents := by
  intro compact source input output target related required
  cases compact <;> cases source <;> cases input <;>
    simp_all [represents, model, compactModel]
  all_goals first
    | exact ⟨left, rfl, by simp [represents]⟩
    | exact ⟨right, rfl, by simp [represents]⟩

def ExactStateMap (spec : Machine Reference Input Output)
    (impl : Machine Compact Input Output) (encode : Reference → Compact) : Prop :=
  ∀ source input output target, spec source input = some (output, target) →
    impl (encode source) input = some (output, encode target)

theorem no_two_class_partition
    (encode : PaperState → Fin 2) (implementation : Machine (Fin 2) Command Answer) :
    ¬ ExactStateMap model implementation encode := by
  intro correct
  have noAC : encode a ≠ encode c := by
    intro equal
    have fromA := correct a inspectState zero a rfl
    have fromC := correct c inspectState one c rfl
    rw [equal, fromC] at fromA
    cases fromA
  have noAB : encode a ≠ encode b := by
    intro equal
    have fromA := correct a forward ok b rfl
    have fromB := correct b forward ok c rfl
    rw [equal, fromB] at fromA
    have bc : encode c = encode b := congrArg Prod.snd (Option.some.inj fromA)
    exact noAC (equal.trans bc.symm)
  have noBC : encode b ≠ encode c := by
    intro equal
    have fromB := correct b back ok a rfl
    have fromC := correct c back ok b rfl
    rw [equal, fromC] at fromB
    have ba : encode b = encode a := congrArg Prod.snd (Option.some.inj fromB)
    exact noAC (ba.symm.trans equal)
  have ab : (encode a).val ≠ (encode b).val := fun h => noAB (Fin.ext h)
  have ac : (encode a).val ≠ (encode c).val := fun h => noAC (Fin.ext h)
  have bc : (encode b).val ≠ (encode c).val := fun h => noBC (Fin.ext h)
  omega

end StrictCounterexample

#print axioms closed_cover_iff_implementation
#print axioms two_overlapping_states_cover
#print axioms two_overlapping_states_work
#print axioms no_two_class_partition

end Kernel0.PartialStateElimination
