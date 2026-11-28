import Lean

/-!
Finite established schedules. Intermediate authority and the attribution
of every reply matter. No concurrent runtime implementation is assumed.
-/

namespace Kernel0.CommutingEffects

abbrev Step (State Request Reply : Type) := State → Request → Reply × State

def run {State Request Reply : Type} (step : Step State Request Reply) :
    List Request → State → State × List (Request × Reply)
  | [], state => (state, [])
  | request :: rest, state =>
    let first := step state request
    let remaining := run step rest first.2
    (remaining.1, (request, first.1) :: remaining.2)

def CommutesAt {State Request Reply : Type}
    (step : Step State Request Reply) (state : State) (first second : Request) : Prop :=
  let a := step state first
  let b := step state second
  let afterA := step a.2 second
  let afterB := step b.2 first
  afterA.2 = afterB.2 ∧ afterA.1 = b.1 ∧ afterB.1 = a.1

def SameResults {State Request Reply : Type}
    (a b : State × List (Request × Reply)) : Prop :=
  a.1 = b.1 ∧ a.2.Perm b.2

theorem adjacent_swap
    {State Request Reply : Type}
    (step : Step State Request Reply) (state : State) (first second : Request)
    (suffix : List Request) (commutes : CommutesAt step state first second) :
    SameResults (run step (first :: second :: suffix) state)
      (run step (second :: first :: suffix) state) := by
  obtain ⟨stateEqual, replyB, replyA⟩ := commutes
  unfold SameResults
  simp only [run]
  rw [stateEqual, replyB, replyA]
  exact ⟨rfl, List.Perm.swap _ _ _⟩

inductive Reorders {Request : Type} (independent : Request → Request → Prop) :
    List Request → List Request → Prop where
  | nil : Reorders independent [] []
  | cons (first : Request) {left right} :
      Reorders independent left right → Reorders independent (first :: left) (first :: right)
  | swap (first second : Request) (suffix : List Request) :
      independent first second →
      Reorders independent (first :: second :: suffix) (second :: first :: suffix)
  | trans {first second third} :
      Reorders independent first second → Reorders independent second third →
      Reorders independent first third

theorem local_diamonds_preserve_results
    {State Request Reply : Type}
    (step : Step State Request Reply) (reachable : State → Prop)
    (independent : Request → Request → Prop)
    (closed : ∀ state request, reachable state → reachable (step state request).2)
    (commutes : ∀ state first second, reachable state → independent first second →
      CommutesAt step state first second)
    {first second : List Request} (order : Reorders independent first second)
    {state : State} (initial : reachable state) :
    SameResults (run step first state) (run step second state) := by
  induction order generalizing state with
  | nil => exact ⟨rfl, List.Perm.nil⟩
  | cons request _ rest =>
    obtain ⟨sameState, sameReplies⟩ := rest (closed state request initial)
    exact ⟨sameState, List.Perm.cons (request, (step state request).1) sameReplies⟩
  | swap first second suffix unrelated =>
    exact adjacent_swap step state first second suffix (commutes state first second initial unrelated)
  | trans _ _ left right =>
    obtain ⟨leftState, leftReplies⟩ := left initial
    obtain ⟨rightState, rightReplies⟩ := right initial
    exact ⟨leftState.trans rightState, leftReplies.trans rightReplies⟩

private def capTwo : Step Nat Nat Bool := fun used _ =>
  if used < 2 then (true, used + 1) else (false, used)

theorem every_pair_commutes_at_empty (first second : Nat) :
    CommutesAt capTwo 0 first second := by
  simp [CommutesAt, capTwo]

theorem three_requests_can_observe_different_acceptance :
    ¬ SameResults (run capTwo [0,1,2] 0) (run capTwo [2,1,0] 0) := by
  intro same
  have original : (0, true) ∈ (run capTwo [0,1,2] 0).2 := by decide
  have changed := same.2.mem_iff.mp original
  have absent : (0, true) ∉ (run capTwo [2,1,0] 0).2 := by decide
  exact absent changed

#print axioms local_diamonds_preserve_results
#print axioms every_pair_commutes_at_empty
#print axioms three_requests_can_observe_different_acceptance

end Kernel0.CommutingEffects
