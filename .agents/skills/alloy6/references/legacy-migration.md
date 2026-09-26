# Migrating legacy Alloy models

The day-course materials and many catalog models predate Alloy 6. Their relational lessons remain useful, but their dynamic models typically use explicit ordered states instead of native temporal semantics.

## Detect the modeling style

### Legacy explicit-state style

Typical signs:

- `open util/ordering[State]` or `open util/ordering[Time]`;
- predicates with explicit pre/post parameters;
- state fields stored on each `State` atom;
- facts connecting each non-final state to its ordered successor;
- an exact `State` scope, often forced by `util/ordering`, that acts as finite trace length.

This style remains expressible after resolving syntax collisions, but label it explicitly. It represents a finite ordered sequence, not an Alloy 6 infinite lasso trace.

### Native Alloy 6 style

Typical signs:

- `var` signatures or fields;
- primed next-state expressions;
- `init`, action, `stutter`, `next`, and `traces` predicates;
- `always`, `eventually`, or other temporal operators;
- an explicit `steps` bound.

Use native style for new behavioral models unless explicit states are themselves domain objects or compatibility is required.

## Compatibility traps

Pre-6 code often names the post-state parameter `s'`. Alloy 6 reserves `'` as the next-state operator, so that identifier is invalid or changes meaning. Rename the parameter to `post` or `nextState` before compiling a legacy model.

Alloy 6 also reserves temporal words including `after`, `always`, `before`, `eventually`, `historically`, `once`, `releases`, `since`, `steps`, `triggered`, `until`, and `var`. Rename legacy identifiers that collide.

Copy ASCII syntax from source files, not typographic punctuation from PDFs. Alloy identifiers cannot use typographic primes or dashes.

## Migration recipe

1. Preserve the old model and its expected command outcomes as a baseline.
2. Separate static configuration from values stored per `State`.
3. Move changing values into `var` fields on a stable owner signature.
4. Rewrite `action[pre, post, ...]` so current fields are unprimed and next fields are primed.
5. Replace ordered-state trace facts with `init` and `always next`; add complete frames and stutter.
6. Rewrite commands with an explicit `steps` horizon and compare witnesses/counterexamples rather than assuming equivalence.

`util/ordering[S]` makes `S` exact and nonempty. Removing it can change satisfiability independently of the temporal rewrite, so control scopes carefully during comparison.

## Day-course modernization

Sessions 1 through 3 remain useful for relations, language basics, and static modeling. Session 4’s `State`/`Time` and `util/ordering` presentation should be taught as legacy, then rewritten with native temporal constructs.

Preserve the course’s effective learning loop:

1. classify domain atoms;
2. relate them;
3. constrain incrementally;
4. run witnesses;
5. inspect and minimize counterexamples;
6. refine and check claims.

Do not copy known defects from the exercises:

- one Session 2 predicate example declares `d` but invokes the predicate with an undeclared `a`;
- a logic solution supplies a binary tuple for a unary `set univ` exercise;
- an exercise solution relies on `univ` being empty, which is not valid for Alloy 6 because built-in integer atoms are in the universe. Use an explicit domain signature instead.
