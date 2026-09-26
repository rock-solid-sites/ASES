# Relational modeling in Alloy 6

Use this reference to translate a domain into atoms, relations, constraints, witnesses, and claims.

## Mental model

Everything is a relation:

- a signature is a unary relation (a set of atoms);
- an atom behaves as a singleton unary relation;
- a field is a relation whose first column is its declaring signature;
- `none` is the empty relation, not a null value;
- a scalar is represented by a relation constrained to contain exactly one tuple.

Read `a.r` as relational join/navigation, not as mutable object-field access. If `r: A -> B`, then `a.r` is the set of `B` atoms related to `a`. Joining outside a relation’s domain yields `none`; it does not throw an error.

`in` means subset. It acts like membership only when the left expression is known to be a singleton.

## Signatures and multiplicities

```alloy
abstract sig Principal {}
sig Person extends Principal {}
one sig Service extends Principal {}

sig Team {
  lead: one Person,
  deputy: lone Person,
  members: some Person,
  observers: set Principal
}

sig OnCall in Person {}
```

- `extends` creates disjoint subtypes. If the parent is `abstract`, its atoms must belong to an extension.
- `in` creates a subset signature; subset signatures can overlap and cannot receive an independent command scope.
- Signature multiplicities constrain atom counts: `one`, `lone`, and `some`.
- In a simple unary bound such as `lead: Person`, omission defaults to `one`. In an arrow bound such as `assignments: User -> Role`, omitted arrow multiplicities are `set`, so the relation is unconstrained in cardinality. Write multiplicities explicitly in either form.

Use arrow multiplicities when constraints apply to multiple columns, but prefer ordinary quantification when it is easier to audit.

## Four meanings of `disj`

`disj` is overloaded by where it appears. Read the declaration before assuming it only means distinct quantified atoms.

```alloy
all disj a, b: Account | a.key != b.key

sig Worker {
  primary: disj one Lock,
  disj left, right: lone Lock
}

fact NoRepeatedExpressions {
  disj[Worker.primary, Worker.left, Worker.right]
}
```

- `all disj a, b: Account` requires the quantified variables to denote distinct atoms.
- `primary: disj one Lock` makes the field injective across different `Worker` atoms: their `primary` values cannot overlap.
- `disj left, right: lone Lock` makes those fields disjoint for each declaring `Worker`; it does not make either field injective across workers.
- `disj[e1, e2, ...]` is true when the expression values are pairwise disjoint.

Declaration-level `disj` can be concise, but use an explicit fact when readers need to see which owner or field dimension is being constrained.

## Core relational operators

| Syntax | Meaning | Typical use |
|---|---|---|
| `a.b` | join | navigate a relation |
| `A -> B` | Cartesian product | build a relation or type |
| `r + s` | union | add tuples |
| `r - s` | difference | remove tuples |
| `r & s` | intersection | find shared tuples |
| `r ++ s` | relational override | replace mappings for keys in `s` |
| `A <: r` | domain restriction | keep tuples starting in `A` |
| `r :> B` | range restriction | keep tuples ending in `B` |
| `~r` | transpose | reverse a binary relation |
| `^r` | transitive closure | one-or-more reachability |
| `*r` | reflexive-transitive closure | zero-or-more reachability |
| `#e` | cardinality | count tuples |
| `iden` | identity relation | relate each atom to itself |
| `univ` | current universe | all atoms in the state |

Closure applies only to binary relations. Parenthesize mixed operators when the intended grouping is not visually obvious.

## Reusable patterns

### No self-edge

```alloy
no iden & edge
```

### Acyclic relation

```alloy
no n: Node | n in n.^edge
```

### Reachability from roots

```alloy
Node in Root.*edge
```

### Unique key

```alloy
sig Key {}

sig Account {
  key: one Key
}

all disj x, y: Account | x.key != y.key
```

This pattern relies on every account having exactly one key. With `lone` or `set` keys, inequality compares whole sets and does not express ordinary key uniqueness.

### Total function and injectivity

```alloy
sig Account {
  owner: one User
}

fact AtMostOneAccountPerOwner {
  all disj a, b: Account | a.owner != b.owner
}
```

`owner: one User` makes ownership total and functional from account to user. The additional fact makes the relation injective in the reverse direction: a user owns at most one account. Prefer a declaration over a separate fact only when it expresses the rule exactly.

## Facts, predicates, functions, and assertions

- A `fact` restricts every analyzed instance. Use it only for a true modeling assumption.
- A `pred` packages a formula and is ideal for scenarios, actions, and reusable constraints.
- A `fun` returns an expression/relation. Use it for derived views rather than redundant stored fields.
- An `assert` states a consequence you expect the facts and behavior to imply. A `check` asks the Analyzer to find a counterexample.
- A `run` asks the Analyzer to find a satisfying instance of a predicate or formula.

The declaration constraints on predicate/function parameters are included when that paragraph is run directly, but do not supply semantic preconditions when it is invoked elsewhere. Put real preconditions in the body.

## Modeling discipline

### Classify before constraining

Identify atoms and relations first. Add constraints one at a time and enumerate instances. A strong fact can make the intended example impossible and can make every later assertion appear valid through inconsistency.

### Prefer definitions over duplicate state

If a relation is derivable, expose it with a function:

```alloy
fun writableBy[d: Document]: set Principal {
  d.owner + d.editors
}
```

Storing both source and derived relations creates a consistency obligation and enlarges the search space.

### Choose message identity deliberately

Represent a simple in-flight message as a tuple when sender, receiver, and payload completely characterize it:

```alloy
one sig Network {
  var pending: Node -> Node -> Payload
}
```

This avoids adding identity atoms merely to carry fields. Use a `Message` signature instead when two otherwise identical messages must coexist, or when a message has its own provenance, retry count, acknowledgement, ordering, or lifecycle. State the trade-off; neither representation is universally faster or immune to scope mistakes.

### Guard branches that require witnesses

Do not combine an empty-set implication with an unconditional existential from that same set:

```alloy
// Unsatisfiable when candidates is empty.
(no candidates implies fallback) and (some x: candidates | choose[x])

// The witness is required only in the nonempty branch.
no candidates implies fallback else some x: candidates | choose[x]
```

When the branches produce expressions rather than formulas, use `condition => thenExpr else elseExpr`; when they are formulas, an explicit guarded disjunction can be easier to audit.

### Keep module names and visibility intentional

Use `module path/name` when a model is imported by other files, and keep the module name aligned with its source path. `private` limits a declaration to its module. Do not use reserved words such as `seq` or Alloy 6 temporal operators as identifiers; rename legacy collisions rather than relying on parser recovery.

### Make the universe explicit

Do not use `univ = none` to request an empty domain. Alloy includes built-in atoms such as integers. Introduce a domain signature, such as `sig Atom {}`, and constrain that signature instead.

### Use integers only when arithmetic matters

Alloy integers use a finite bitwidth; the default 4-bit range is `-8` through `7`. Evaluator arithmetic wraps, while Analyzer behavior depends on the configured overflow option. Scope on `Int` selects bitwidth, not a maximum population. Record the bitwidth and overflow setting, and never change overflow handling merely to suppress a counterexample. Prefer uninterpreted atoms or an ordering when only identity or order matters.

### Treat type warnings as evidence

An arity, disjointness, or irrelevance warning often means a join can never match or part of a formula can never affect the result. Fix the model or explicitly justify the expression; do not routinely suppress warnings.
