import Lean

/-!
Grounded authority and the exact incremental recomputation boundary.
Rules have finite premise lists. Policy authentication, attenuation, coherent
snapshots and mediation at the effect decision are outside this model.
-/

namespace Kernel0.GroundedDelegation

structure Rule (Claim : Type) where
  premises : List Claim
  head : Claim

inductive Derived {Claim : Type} (roots : Claim → Prop) (rules : Rule Claim → Prop) :
    Claim → Prop where
  | root {claim} : roots claim → Derived roots rules claim
  | apply (rule : Rule Claim) : rules rule →
      (∀ claim, claim ∈ rule.premises → Derived roots rules claim) →
      Derived roots rules rule.head

theorem derived_is_least
    {Claim : Type} {roots : Claim → Prop} {rules : Rule Claim → Prop}
    {candidate : Claim → Prop}
    (containsRoots : ∀ claim, roots claim → candidate claim)
    (closed : ∀ rule, rules rule →
      (∀ claim, claim ∈ rule.premises → candidate claim) → candidate rule.head)
    {claim : Claim} (proof : Derived roots rules claim) : candidate claim := by
  induction proof with
  | root valid => exact containsRoots _ valid
  | apply rule live _ grounds => exact closed rule live grounds

def changed {Claim : Type} (oldRoots newRoots : Claim → Prop)
    (oldRules newRules : Rule Claim → Prop) (claim : Claim) : Prop :=
  ¬ (oldRoots claim ↔ newRoots claim) ∨
    ∃ rule, rule.head = claim ∧ ¬ (oldRules rule ↔ newRules rule)

inductive Affected {Claim : Type} (mark : Claim → Prop) (rules : Rule Claim → Prop) :
    Claim → Prop where
  | seed {claim} : mark claim → Affected mark rules claim
  | step {claim} (rule : Rule Claim) : rules rule → claim ∈ rule.premises →
      Affected mark rules claim → Affected mark rules rule.head

theorem affected_mono
    {Claim : Type} {mark : Claim → Prop} {small large : Rule Claim → Prop}
    (included : ∀ rule, small rule → large rule)
    {claim : Claim} (proof : Affected mark small claim) : Affected mark large claim := by
  induction proof with
  | seed marked => exact Affected.seed marked
  | step rule live premise _ upstream =>
    exact Affected.step rule (included rule live) premise upstream

theorem affected_union_reduce
    {Claim : Type} {mark : Claim → Prop} {kept other : Rule Claim → Prop}
    (markOmittedHeads : ∀ rule, other rule → ¬ kept rule → mark rule.head)
    {claim : Claim} (proof : Affected mark (fun r => kept r ∨ other r) claim) :
    Affected mark kept claim := by
  classical
  induction proof with
  | seed marked => exact Affected.seed marked
  | step rule live premise _ upstream =>
    by_cases retained : kept rule
    · exact Affected.step rule retained premise upstream
    · exact Affected.seed (markOmittedHeads rule (live.resolve_left retained) retained)

theorem one_graph_suffices
    {Claim : Type} (oldRoots newRoots : Claim → Prop)
    (oldRules newRules : Rule Claim → Prop) (claim : Claim) :
    Affected (changed oldRoots newRoots oldRules newRules) oldRules claim ↔
    Affected (changed oldRoots newRoots oldRules newRules) newRules claim := by
  constructor
  · intro oldProof
    apply affected_union_reduce (other := oldRules) ?_ (affected_mono ?_ oldProof)
    · intro rule previouslyLive nowAbsent
      exact Or.inr ⟨rule, rfl, fun agree => nowAbsent (agree.mp previouslyLive)⟩
    · exact fun _ live => Or.inr live
  · intro newProof
    apply affected_union_reduce (other := newRules) ?_ (affected_mono ?_ newProof)
    · intro rule nowLive previouslyAbsent
      exact Or.inr ⟨rule, rfl, fun agree => previouslyAbsent (agree.mpr nowLive)⟩
    · exact fun _ live => Or.inr live

theorem transfer_outside
    {Claim : Type} {r₀ r₁ : Claim → Prop} {p₀ p₁ : Rule Claim → Prop}
    {affected : Claim → Prop}
    (sameRoot : ∀ claim, ¬ affected claim → r₀ claim → r₁ claim)
    (sameRule : ∀ rule, ¬ affected rule.head → p₀ rule → p₁ rule)
    (closed : ∀ rule claim, p₀ rule → claim ∈ rule.premises →
      affected claim → affected rule.head)
    {claim : Claim} (proof : Derived r₀ p₀ claim) :
    ¬ affected claim → Derived r₁ p₁ claim := by
  induction proof with
  | root live =>
    intro unaffected
    exact Derived.root (sameRoot _ unaffected live)
  | apply rule live _ premises =>
    intro unaffected
    apply Derived.apply rule (sameRule rule unaffected live)
    intro premise occurs
    exact premises premise occurs (fun marked => unaffected (closed rule premise live occurs marked))

theorem outside_agrees
    {Claim : Type} (oldRoots newRoots : Claim → Prop)
    (oldRules newRules : Rule Claim → Prop) {claim : Claim}
    (unaffected :
      ¬ Affected (changed oldRoots newRoots oldRules newRules) newRules claim) :
    Derived oldRoots oldRules claim ↔ Derived newRoots newRules claim := by
  classical
  let mark := changed oldRoots newRoots oldRules newRules
  let region := Affected mark newRules
  have rootsAgree : ∀ v, ¬ region v → (oldRoots v ↔ newRoots v) := by
    intro v outside
    by_cases agree : oldRoots v ↔ newRoots v
    · exact agree
    · exact False.elim (outside (Affected.seed (Or.inl agree)))
  have rulesAgree : ∀ rule, ¬ region rule.head → (oldRules rule ↔ newRules rule) := by
    intro rule outside
    by_cases agree : oldRules rule ↔ newRules rule
    · exact agree
    · exact False.elim (outside (Affected.seed (Or.inr ⟨rule, rfl, agree⟩)))
  constructor
  · intro proof
    refine transfer_outside (affected := region)
      (fun v h => (rootsAgree v h).mp) (fun rule h => (rulesAgree rule h).mp)
      ?_ proof unaffected
    intro rule v live premise inside
    have oldInside := (one_graph_suffices oldRoots newRoots oldRules newRules v).mpr inside
    have oldHead := Affected.step rule live premise oldInside
    exact (one_graph_suffices oldRoots newRoots oldRules newRules rule.head).mp oldHead
  · intro proof
    refine transfer_outside (affected := region)
      (fun v h => (rootsAgree v h).mpr) (fun rule h => (rulesAgree rule h).mpr)
      ?_ proof unaffected
    exact fun rule _ live premise inside => Affected.step rule live premise inside

theorem recompute_on_affected_region
    {Claim : Type} (oldRoots newRoots : Claim → Prop)
    (oldRules newRules : Rule Claim → Prop) (claim : Claim) :
    let region := Affected (changed oldRoots newRoots oldRules newRules) newRules
    let boundary := fun v =>
      (region v ∧ newRoots v) ∨ (¬ region v ∧ Derived oldRoots oldRules v)
    Derived boundary (fun r => region r.head ∧ newRules r) claim ↔
      Derived newRoots newRules claim := by
  classical
  intro region boundary
  constructor
  · intro proof
    induction proof with
    | root h =>
      cases h with
      | inl fresh => exact Derived.root fresh.2
      | inr retained =>
        exact (outside_agrees oldRoots newRoots oldRules newRules retained.1).mp retained.2
    | apply rule live _ premises => exact Derived.apply rule live.2 premises
  · intro proof
    induction proof with
    | @root v live =>
      by_cases inside : region v
      · exact Derived.root (Or.inl ⟨inside, live⟩)
      · exact Derived.root (Or.inr ⟨inside,
          (outside_agrees oldRoots newRoots oldRules newRules inside).mpr (Derived.root live)⟩)
    | apply rule live original premises =>
      by_cases inside : region rule.head
      · exact Derived.apply rule ⟨inside, live⟩ premises
      · exact Derived.root (Or.inr ⟨inside,
          (outside_agrees oldRoots newRoots oldRules newRules inside).mpr
            (Derived.apply rule live original)⟩)

section CycleCounterexample

inductive ExampleClaim where
  | issuer
  | first
  | second
  deriving DecidableEq

open ExampleClaim

private def cycleRules (rule : Rule ExampleClaim) : Prop :=
  rule = ⟨[issuer], first⟩ ∨ rule = ⟨[first], second⟩ ∨ rule = ⟨[second], first⟩

private def circularCache (claim : ExampleClaim) : Prop :=
  claim = first ∨ claim = second

theorem cycle_cache_is_locally_justified (claim : ExampleClaim) :
    circularCache claim ↔ ∃ rule, cycleRules rule ∧ rule.head = claim ∧
      ∀ premise, premise ∈ rule.premises → circularCache premise := by
  constructor
  · intro stored
    rcases stored with same | same
    · subst claim
      exact ⟨⟨[second], first⟩, Or.inr (Or.inr rfl), rfl,
        fun premise member => Or.inr (by simpa using member)⟩
    · subst claim
      exact ⟨⟨[first], second⟩, Or.inr (Or.inl rfl), rfl,
        fun premise member => Or.inl (by simpa using member)⟩
  · rintro ⟨rule, active, selected, _⟩
    rcases active with same | same | same <;> subst rule
    · exact Or.inl selected.symm
    · exact Or.inr selected.symm
    · exact Or.inl selected.symm

theorem cycle_has_no_ground_after_issuer_withdrawal (claim : ExampleClaim) :
    ¬ Derived (fun _ => False) cycleRules claim := by
  intro derivation
  refine derived_is_least (candidate := fun _ => False) (fun _ impossible => impossible)
    ?_ derivation
  intro rule active premises
  rcases active with same | same | same <;> subst rule
  · exact premises issuer (by simp)
  · exact premises first (by simp)
  · exact premises second (by simp)

theorem cycle_was_grounded_before_withdrawal :
    Derived (fun claim => claim = issuer) cycleRules second := by
  have firstGround : Derived (fun claim => claim = issuer) cycleRules first := by
    apply Derived.apply ⟨[issuer], first⟩ (Or.inl rfl)
    intro premise occurs
    exact Derived.root (by simpa using occurs)
  apply Derived.apply ⟨[first], second⟩ (Or.inr (Or.inl rfl))
  intro premise occurs
  have same : premise = first := by simpa using occurs
  simpa [same] using firstGround

end CycleCounterexample

#print axioms derived_is_least
#print axioms one_graph_suffices
#print axioms outside_agrees
#print axioms recompute_on_affected_region

end Kernel0.GroundedDelegation
