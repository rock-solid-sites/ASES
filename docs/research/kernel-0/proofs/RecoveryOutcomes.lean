import Lean

/-!
One-shot recovery with side information and set-valued permitted outcomes.
The decoder may be partial on code/probe pairs that no history can produce.
The encoder's trust and persistence are assumptions outside this model.
-/

namespace Kernel0.RecoveryOutcomes

variable {History Probe Outcome Code Item : Type}

def WitnessesView (feasible : History → Probe → Prop) (encode : History → Code)
    (code : Code) (probe : Probe) : Prop :=
  ∃ history, feasible history probe ∧ encode history = code

def RespondsToView (feasible : History → Probe → Prop)
    (allowed : History → Probe → Outcome → Prop) (encode : History → Code)
    (code : Code) (probe : Probe) (outcome : Outcome) : Prop :=
  ∀ history, feasible history probe → encode history = code → allowed history probe outcome

def LegalDecoder (feasible : History → Probe → Prop)
    (allowed : History → Probe → Outcome → Prop) (encode : History → Code)
    (decode : Code → Probe → Option Outcome) : Prop :=
  ∀ history probe, feasible history probe →
    ∃ outcome, decode (encode history) probe = some outcome ∧ allowed history probe outcome

theorem decoder_exists_iff_common_outcomes
    (feasible : History → Probe → Prop)
    (allowed : History → Probe → Outcome → Prop) (encode : History → Code) :
    (∃ decode, LegalDecoder feasible allowed encode decode) ↔
      ∀ code probe, WitnessesView feasible encode code probe →
        ∃ outcome, RespondsToView feasible allowed encode code probe outcome := by
  classical
  constructor
  · rintro ⟨decode, correct⟩ code probe ⟨witness, feasibleWitness, codeWitness⟩
    obtain ⟨outcome, observed, _⟩ := correct witness probe feasibleWitness
    rw [codeWitness] at observed
    refine ⟨outcome, ?_⟩
    intro other feasibleOther codeOther
    obtain ⟨alternative, sameObservation, correctAlternative⟩ :=
      correct other probe feasibleOther
    rw [codeOther, observed] at sameObservation
    cases sameObservation
    exact correctAlternative
  · intro shared
    let decode : Code → Probe → Option Outcome := fun code probe =>
      if possible : WitnessesView feasible encode code probe
      then some (Classical.choose (shared code probe possible))
      else none
    refine ⟨decode, ?_⟩
    intro history probe possible
    have reachable : WitnessesView feasible encode (encode history) probe :=
      ⟨history, possible, rfl⟩
    refine ⟨Classical.choose (shared (encode history) probe reachable), ?_, ?_⟩
    · simp only [decode, dif_pos reachable]
    · exact Classical.choose_spec (shared (encode history) probe reachable) history possible rfl

def KeptSetAllowed (mandatory optionalCeiling : History → Item → Prop)
    (history : History) (chosen : Item → Prop) : Prop :=
  (∀ item, mandatory history item → chosen item) ∧
  (∀ item, chosen item → optionalCeiling history item)

theorem keep_intervals_agree_iff_pairwise_bounds
    (view : History → Prop) (mandatory optionalCeiling : History → Item → Prop) :
    (∃ chosen, ∀ history, view history → KeptSetAllowed mandatory optionalCeiling history chosen) ↔
      ∀ first second, view first → view second →
        ∀ item, mandatory first item → optionalCeiling second item := by
  constructor
  · rintro ⟨chosen, common⟩ first second seesFirst seesSecond item required
    exact (common second seesSecond).2 item ((common first seesFirst).1 item required)
  · intro compatible
    let chosen : Item → Prop := fun item => ∃ history, view history ∧ mandatory history item
    refine ⟨chosen, ?_⟩
    intro history observed
    constructor
    · intro item required
      exact ⟨history, observed, required⟩
    · rintro item ⟨first, seesFirst, required⟩
      exact compatible first history seesFirst observed item required

theorem exclusion_allows_proper_subfamily (view : History → Prop)
    (missing : ∃ history, ¬ view history) :
    ∃ outcome, ∀ history, view history → outcome ≠ history := by
  obtain ⟨outcome, excluded⟩ := missing
  refine ⟨outcome, ?_⟩
  intro history observed equal
  exact excluded (equal ▸ observed)

theorem exclusion_forbids_whole_family :
    ¬ ∃ outcome : History, ∀ history : History, outcome ≠ history := by
  rintro ⟨outcome, permits⟩
  exact permits outcome rfl

theorem three_histories_pairwise_compatible :
    ∀ first second : Fin 3, ∃ outcome : Fin 3, outcome ≠ first ∧ outcome ≠ second := by
  intro first second
  have cover (n : Fin 3) : n = 0 ∨ n = 1 ∨ n = 2 := by omega
  rcases cover first with h | h | h <;> subst first <;>
    rcases cover second with h | h | h <;> subst second
  all_goals first
    | exact ⟨0, by decide, by decide⟩
    | exact ⟨1, by decide, by decide⟩
    | exact ⟨2, by decide, by decide⟩

#print axioms decoder_exists_iff_common_outcomes
#print axioms keep_intervals_agree_iff_pairwise_bounds
#print axioms exclusion_allows_proper_subfamily
#print axioms exclusion_forbids_whole_family
#print axioms three_histories_pairwise_compatible

end Kernel0.RecoveryOutcomes
