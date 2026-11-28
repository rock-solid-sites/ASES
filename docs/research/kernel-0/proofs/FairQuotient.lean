import Lean

/-!
Labelled path lifting for a quotient that preserves the monitor and fairness facts.
The witness is chosen at the actual concrete state, including after every step.
-/

namespace Kernel0.FairQuotient

structure Graph (State Event : Type) where
  step : State → Event → State → Prop

structure Path {State Event : Type} (graph : Graph State Event) where
  stateAt : Nat → State
  event : Nat → Event
  valid : ∀ n, graph.step (stateAt n) (event n) (stateAt (n + 1))

def InfinitelyOften (holds : Nat → Prop) : Prop :=
  ∀ start, ∃ n, start ≤ n ∧ holds n

def EventuallyAlways (holds : Nat → Prop) : Prop :=
  ∃ start, ∀ n, start ≤ n → holds n

theorem weak_fairness_transport (enabled firstEnabled taken firstTaken : Nat → Prop)
    (states : ∀ n, enabled n ↔ firstEnabled n)
    (edges : ∀ n, taken n ↔ firstTaken n) :
    (EventuallyAlways enabled → InfinitelyOften taken) ↔
      (EventuallyAlways firstEnabled → InfinitelyOften firstTaken) := by
  constructor
  · intro fair ⟨start, ongoing⟩ bound
    obtain ⟨n, after, taking⟩ := fair ⟨start, fun m order => (states m).mpr
      (ongoing m order)⟩ bound
    exact ⟨n, after, (edges n).mp taking⟩
  · intro fair ⟨start, ongoing⟩ bound
    obtain ⟨n, after, taking⟩ := fair ⟨start, fun m order => (states m).mp
      (ongoing m order)⟩ bound
    exact ⟨n, after, (edges n).mpr taking⟩

theorem strong_fairness_transport (enabled firstEnabled taken firstTaken : Nat → Prop)
    (states : ∀ n, enabled n ↔ firstEnabled n)
    (edges : ∀ n, taken n ↔ firstTaken n) :
    (InfinitelyOften enabled → InfinitelyOften taken) ↔
      (InfinitelyOften firstEnabled → InfinitelyOften firstTaken) := by
  constructor
  · intro fair frequent bound
    have hasEnabled : InfinitelyOften enabled := by
      intro start
      obtain ⟨n, after, holds⟩ := frequent start
      exact ⟨n, after, (states n).mpr holds⟩
    obtain ⟨n, after, taking⟩ := fair hasEnabled bound
    exact ⟨n, after, (edges n).mp taking⟩
  · intro fair frequent bound
    have hasEnabled : InfinitelyOften firstEnabled := by
      intro start
      obtain ⟨n, after, holds⟩ := frequent start
      exact ⟨n, after, (states n).mp holds⟩
    obtain ⟨n, after, taking⟩ := fair hasEnabled bound
    exact ⟨n, after, (edges n).mpr taking⟩

def project {Concrete Abstract Event : Type} {source : Graph Concrete Event}
    {target : Graph Abstract Event} (view : Concrete → Abstract)
    (preserve : ∀ {before event after}, source.step before event after →
      target.step (view before) event (view after))
    (path : Path source) : Path target where
  stateAt := fun n => view (path.stateAt n)
  event := path.event
  valid := fun n => preserve (path.valid n)

noncomputable def lift {Concrete Abstract Event : Type} {source : Graph Concrete Event}
    {target : Graph Abstract Event} (view : Concrete → Abstract)
    (reflect : ∀ before {event after}, target.step (view before) event after →
      ∃ successor, source.step before event successor ∧ view successor = after)
    (path : Path target) (start : Concrete) (initial : view start = path.stateAt 0) :
    {concrete : Path source //
      concrete.stateAt 0 = start ∧
      (∀ n, view (concrete.stateAt n) = path.stateAt n) ∧
      concrete.event = path.event} := by
  classical
  let advance (n : Nat) (before : {state // view state = path.stateAt n}) :
      {after : Concrete // source.step before.val (path.event n) after ∧
        view after = path.stateAt (n + 1)} := by
    have step := path.valid n
    rw [← before.property] at step
    exact ⟨Classical.choose (reflect before.val step),
      Classical.choose_spec (reflect before.val step)⟩
  let here : (n : Nat) → {state // view state = path.stateAt n} :=
    Nat.rec ⟨start, initial⟩ (fun n before => ⟨(advance n before).val,
      (advance n before).property.2⟩)
  exact ⟨{
    stateAt := fun n => (here n).val
    event := path.event
    valid := fun n => (advance n (here n)).property.1
  }, rfl, fun n => (here n).property, rfl⟩

inductive Stage where
  | staged | selected | answered
  deriving DecidableEq

inductive Visible where
  | pending | done
  deriving DecidableEq

inductive Event where
  | internal | answer
  deriving DecidableEq

def stages : Graph Stage Event where
  step before event after :=
    (before = .staged ∧ event = .internal ∧ after = .selected) ∨
    (before = .selected ∧ event = .answer ∧ after = .answered) ∨
    (before = .answered ∧ event = .internal ∧ after = .answered)

def view : Stage → Visible
  | .staged | .selected => .pending
  | .answered => .done

def unionGraph : Graph Visible Event where
  step before event after :=
    ∃ actual next, view actual = before ∧ view next = after ∧ stages.step actual event next

theorem merged_state_permits_permanent_delay : Nonempty {path : Path unionGraph //
    ∀ n, path.stateAt n = .pending} :=
  ⟨⟨{ stateAt := fun _ => .pending, event := fun _ => .internal, valid := fun _ =>
    ⟨.staged, .selected, rfl, rfl, Or.inl ⟨rfl, rfl, rfl⟩⟩ }, fun _ => rfl⟩⟩

theorem actual_progress_after_at_most_two_steps (path : Path stages) :
    path.stateAt 2 = .answered := by
  have first := path.valid 0
  have second := path.valid 1
  unfold stages at first second
  rcases first with ⟨_, _, after⟩ | ⟨_, _, after⟩ | ⟨_, _, after⟩
  · change path.stateAt 1 = .selected at after
    rw [after] at second
    rcases second with ⟨wrong, _, _⟩ | ⟨_, _, done⟩ | ⟨wrong, _, _⟩
    · contradiction
    · exact done
    · contradiction
  · change path.stateAt 1 = .answered at after
    rw [after] at second
    rcases second with ⟨wrong, _, _⟩ | ⟨wrong, _, _⟩ | ⟨_, _, done⟩
    · contradiction
    · contradiction
    · exact done
  · change path.stateAt 1 = .answered at after
    rw [after] at second
    rcases second with ⟨wrong, _, _⟩ | ⟨wrong, _, _⟩ | ⟨_, _, done⟩
    · contradiction
    · contradiction
    · exact done

#print axioms weak_fairness_transport
#print axioms strong_fairness_transport
#print axioms project
#print axioms lift
#print axioms merged_state_permits_permanent_delay
#print axioms actual_progress_after_at_most_two_steps

end Kernel0.FairQuotient
