# Native temporal modeling in Alloy 6

Use native Alloy 6 temporal constructs for new behavioral models. Instances are infinite traces represented by finite lassos: a finite prefix whose last state loops to a previous state or itself.

## Static and mutable relations

Signatures and fields are static unless marked `var`.

```alloy
sig User {}
sig Token {}

one sig Service {
  var active: set User,
  var issued: User -> set Token
}
```

- `Service.active` is its value in the current state.
- `Service.active'` is its value in the next state.
- Prime applies to expressions, but keep primed expressions simple and parenthesized when needed.
- If a top-level signature is mutable, `univ` and `iden` also change over time. Its scope bounds all distinct atoms that can appear across the trace, not the population of each state.

Quantification is evaluated in the state where its formula is evaluated. A quantifier over a mutable signature in a top-level formula outside the scope of any temporal operator ranges over initial-state membership; under `after`, `eventually`, or another temporal operator it ranges over the state selected by that operator.

## Mutable top-level creation and deletion

For `var sig File {}`, atoms newly present in the next state are selected from `File' - File`, not from current `File`:

```alloy
pred createOneFile {
  some f: File' - File | File' = File + f
}
```

The equality is the frame condition: it preserves every current file and adds exactly the chosen atom. Quantifying `some f: File` cannot choose a newly created atom because `File` is the current population. Structural scope bounds every distinct `File` atom that may appear anywhere in the trace.

Atoms cannot migrate between disjoint top-level sibling signatures. When an entity changes role, prefer a static carrier signature plus mutable subset signatures:

```alloy
sig File {}
var sig Uploaded in File {}
var sig Trashed in Uploaded {}
```

## Canonical organization

Keep trace constraints reusable so scenarios, assertions, and induction checks can include them explicitly.

```alloy
pred init {
  no Service.active
  no Service.issued
}

pred activate[u: User, t: Token] {
  u not in Service.active                 // guard
  Service.active' = Service.active + u   // effect
  Service.issued' = Service.issued + u->t
}

pred stutter {
  Service.active' = Service.active
  Service.issued' = Service.issued
}

pred next {
  (some u: User, t: Token | activate[u, t]) or stutter
}

pred traces {
  init
  always next
}
```

An action is an ordinary predicate, not an implicit event object. Its body should make three categories obvious:

1. guard: when it may occur;
2. effect: what changes;
3. frame: what must remain equal in the next state.

Inventory every `var` signature and field. In every action, update or frame every item. If a mutable relation is not mentioned, Alloy may assign it any next-state value.

## Facts and invariants

A standalone non-temporal fact is interpreted at the initial state of a behavioral instance. A genuine domain assumption that must constrain every state needs an explicit temporal operator. Do not use such a fact to assume the property you intend to check.

```alloy
pred issuedOnlyToActiveUsers {
  Service.issued.Token in Service.active
}
```

Signature facts and declaration constraints apply in every state. Even so, prefer a named `always` predicate for important behavioral invariants because its scope is easier to see and reuse in assertions.

Do not put the desired safety claim in a fact before checking it. Let the assertion test whether `init` and `next` preserve it.

```alloy
assert IssuedOnlyToActiveUsers {
  traces implies always issuedOnlyToActiveUsers
}
```

## Temporal operators

| Formula | Meaning from the current state |
|---|---|
| `after P` | `P` in the next state |
| `eventually P` | `P` now or at some future state |
| `always P` | `P` now and in every future state |
| `P until Q` | `Q` eventually occurs; `P` holds before it |
| `P releases Q` | `Q` holds until `P`, or forever if `P` never occurs |
| `before P` | `P` in the previous state; false initially |
| `once P` | `P` now or in a past state |
| `historically P` | `P` now and in every past state |
| `P since Q` | `Q` occurred and `P` has held since |
| `P triggered Q` | past-time dual of `releases` |
| `P ; Q` | `P and after Q` |

Unary temporal operators bind tightly. Write `always (P or Q)`, not `always P or Q`, unless the latter grouping is intentional. The sequence operator `;` has very low precedence and is useful for scenario traces.

Past operators at state 0 are usually useless unless nested under a future operator. For example, a historical precondition is often shaped as `always (action implies historically condition)`.

`until` requires its right side to happen. Use `releases` when the right side is allowed to remain true forever.

## Cross-state binding trap

A `let` binding is substitution, not a frozen snapshot. Moving a formula under `after` also moves evaluation of an expression substituted through a `let`:

```alloy
// Does not preserve the current value as a snapshot.
let old = Service.active | after (Service.active = old)

// Compares the next value with the current value.
Service.active' = Service.active
```

Use prime for adjacent-state expression comparisons. Future and past temporal operators apply to formulas, so do not write `before Service.active` or treat `after expression` as a relational value.

## Stuttering and progress

Alloy traces are infinite. A stutter action lets the modeled subsystem remain unchanged while the surrounding world advances and lets deadlocked states extend into an infinite trace.

Include stutter when idle behavior is valid. Then ensure scenario runs require a real event, because a stutter-only trace may otherwise satisfy the model.

Stutter can falsify liveness: `eventually P` may fail because the model can idle forever. Add fairness only when the domain genuinely supplies progress. Keep it named and local to the liveness assertion:

```alloy
pred activateEnabled {
  some Token
  some User - Service.active
}

pred activateOccurs {
  some u: User, t: Token | activate[u, t]
}

pred weakFairnessForActivate {
  always ((always activateEnabled) implies eventually activateOccurs)
}

run FairActivationTrace {
  traces
  weakFairnessForActivate
  some User
  some Token
  eventually activateOccurs
} for 4 but 8 steps expect 1

assert EventuallyActivated {
  traces and weakFairnessForActivate and some User and some Token
    implies eventually some Service.active
}

check EventuallyActivated for 4 but 8 steps expect 0
```

Do not invent fairness merely to remove an inconvenient counterexample.

## Safety, liveness, and induction

- Safety says that a bad state never occurs: typically `always not Bad`.
- Liveness says that a good event eventually occurs: typically `eventually Good`.
- Fairness describes justified scheduling/progress assumptions needed by some liveness properties.

For expensive invariant checks, initiation and preservation can be checked separately. First refactor `init` and `next` out of global facts into predicates; otherwise global trace facts pre-filter the candidate states and can make preservation pass without establishing inductiveness.

```alloy
assert InitInvariant {
  init implies invariantPredicate
}

assert PreserveInvariant {
  invariantPredicate and next implies after invariantPredicate
}
```

Use a 1-step scope for initiation and 2-step scope for preservation. A true reachable-state invariant may still fail preservation because the induction check also considers unreachable states. Strengthen the inductive invariant rather than dismissing the counterexample.

## Scenario traces

Require concrete behavior in `run` commands:

```alloy
run LoginThenIssue {
  traces
  some u: User, t: Token | activate[u, t]
  eventually some Service.issued
} for 4 but 6 steps expect 1
```

For an exact sequence, `p; q; r` abbreviates nested `after` formulas. Remember that action predicates may overlap unless their guards or an explicit exclusivity constraint prevent it.

An exact prefix does not constrain the infinite tail. Add `; always stutter` only when the scenario intends no later changes. Leave the tail open when the purpose is to explore legal continuations.

When the domain requires exactly one event per transition, enforce both event-kind and parameter-binding exclusivity. For the running example:

```alloy
pred nextExclusive {
  (one u: User, t: Token | activate[u, t]) or stutter
  not (stutter and activateOccurs)
}
```

For larger models, derived event views are easier to visualize and audit than many pairwise exclusions. Preserve action parameters as well as the event kind:

```alloy
enum EventKind { ActivateEvent, IdleEvent }

fun activateBindings: User -> Token {
  { u: User, t: Token | activate[u, t] }
}

fun eventKinds: set EventKind {
  { e: EventKind |
    (e = ActivateEvent and some activateBindings) or
    (e = IdleEvent and stutter)
  }
}
```

Checking only `one eventKinds` can miss two simultaneous parameter bindings of the same action kind. When one concrete event per transition is required, also require `lone activateBindings` (and the corresponding relation for every parameterized action), then run a witness that exercises each event kind.
