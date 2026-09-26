# Analysis, evidence, and debugging

Alloy analysis is model finding. A command asks a solver for a satisfying instance of a formula within structural scopes and, for behavioral models, a temporal horizon.

## Read command results correctly

| Command | SAT means | UNSAT means |
|---|---|---|
| `run P` | an instance satisfying `P` was found | no instance was found within the declared bounds |
| `check A` | a counterexample to assertion `A` was found | no counterexample was found within the declared bounds |

An instance or counterexample that is found is valid for the model. Failure to find one is bounded evidence and may change with larger scopes, a longer trace horizon, a different arithmetic bitwidth, or corrected assumptions.

## Commands and expected outcomes

```alloy
run Interesting {
  some disj a, b: Account | a.owner != b.owner
} for 5 but exactly 3 Account expect 1

assert UniqueKeys {
  all disj a, b: Account | a.key != b.key
}

check UniqueKeys for 6 but 4 Account expect 0
```

- Signature scopes are upper bounds unless marked `exactly`.
- The default overall top-level scope is 3, but do not rely on it in a deliverable.
- Singleton extensions consume atoms from a parent’s scope.
- Subset signatures declared with `in` cannot be scoped directly.
- `util/ordering[S]` forces `S` to be nonempty and to use its exact command scope.
- Behavioral commands default to a finite horizon. State the intended `steps` explicitly.

`expect 1` means the command should be satisfiable: a `run` should find an instance or a `check` should find a counterexample. `expect 0` means it should be unsatisfiable: commonly, a check should find no counterexample.

Avoid the syntactic trap:

```alloy
check Safe       // checks the named assertion
check Safe {}    // names a check of the empty formula; it does not invoke Safe
```

## Time bounds

- `for 8 steps` explores lassos with a bounded horizon up to 8 transitions.
- `for 2..8 steps` sets a minimum and maximum horizon.
- `for 1.. steps` requests complete temporal checking and requires a compatible complete solver such as nuXmv.

Complete temporal checking covers all traces of the finite state space induced by signature scopes. It does not remove structural bounds and may be slow or exhaust memory.

## CLI verification

Alloy 6.2.0 includes a dispatcher CLI. Discover the installed version’s commands first:

```sh
java -jar "$ALLOY_JAR" help
java -jar "$ALLOY_JAR" commands path/to/model.als
```

When all model commands include `expect`, this runs them as a fail-closed gate:

```sh
java -jar "$ALLOY_JAR" exec -q -t none -o - path/to/model.als
```

The process exits nonzero when an observed satisfiability result disagrees with `expect`.

The `-c` selector is useful for interactive investigation, but it fails open on a typo: a pattern matching zero commands can exit successfully. First list commands and manually confirm one exact match before selecting it:

```sh
java -jar "$ALLOY_JAR" commands path/to/model.als
java -jar "$ALLOY_JAR" exec -c CommandName -q -t none -o - path/to/model.als
```

Do not use a selected-command invocation as the only CI gate; execute every command with `expect` for fail-closed verification. These forms were verified against Alloy 6.2.0. For another 6.x build, use its `help` output rather than guessing. If no distribution JAR is present, run the commands in the GUI and report that the CLI gate was unavailable.

Do not enable arithmetic overflow prevention merely to make a command pass; it removes overflowing instances and can hide a real modeling error.

## Literate Alloy in Markdown

Alloy 6 can extract models from Markdown. The file must start with YAML frontmatter delimited by `---`, followed by one or more fences whose opener is exactly ````alloy`. A `title:` key is optional. Only Alloy-fenced content is analyzed, so prose and other code fences do not become part of the model.

````markdown
---
title: Optional human-facing title
---

```alloy
module model
sig A {}
run { some A } for exactly 1 A expect 1
```
````

Pass the `.md` path to both CLI stages exactly as an `.als` path:

```sh
java -jar "$ALLOY_JAR" commands path/to/model.md
java -jar "$ALLOY_JAR" exec -q -t none -o - path/to/model.md
```

If the command list is empty, first check the initial frontmatter delimiters and exact lowercase `alloy` fence before debugging the model itself.

## Verification ladder

1. Parse the model and fix all warnings that lack an explicit justification.
2. Run a minimal witness to confirm the base model is satisfiable.
3. Run a meaningful witness with nonempty relations or a real transition.
4. Check each assertion at a small, understandable scope and diagnose every counterexample.
5. Increase one structural scope or the temporal horizon at a time, recording the result.

For liveness, first check a bounded horizon. Use complete temporal checking only after bounded counterexamples are exhausted and only with deliberately small structural scopes.

## Debugging a counterexample

Do not patch the assertion immediately. Determine which of these is true:

- model fault: a multiplicity, fact, transition, frame, or formula is wrong;
- missing assumption: the environment allows something the real domain forbids;
- design fault: the system behavior genuinely violates the requirement;
- property fault: the assertion is stronger, weaker, or differently scoped than the prose.

For a static instance, inspect the smallest relation that makes the formula false. For a trace, identify the static configuration, initial state, events, loop edge, and first failing state. Use the evaluator on smaller subexpressions.

Preserve a useful failure as a regression command with `expect 1` before the repair, then update the expected outcome only when the repair is intentional and evidenced.

## Debugging UNSAT and vacuity

An UNSAT `run` is often a conflict among assumptions. A passing check can be vacuous for the same reason.

- Start with `run {}` at a small scope.
- Require one domain atom, then one relation tuple, then the intended scenario.
- Temporarily move groups of facts into named predicates and add them back incrementally.
- Use the Analyzer’s unsat core where available, then confirm by relaxing the highlighted constraint.
- After every added security or integrity fact, rerun the meaningful witness.

Facts imported by modules also constrain the model. Inspect `open` statements when local formulas appear harmless.

## Visualizer strategy

For temporal instances:

- New Config changes static relations.
- New Init changes the initial state under the same configuration.
- New Trace changes behavior under the same configuration and initial state.
- New Fork preserves the prefix through the focused state and explores a different future.

Use table, tree, or text views when the graph hides higher-arity tuples. Parameterless derived functions can expose useful relations to the visualizer without adding solver state.

## Evidence report template

```text
Analyzer: Alloy 6.x / solver name
Command: check Property for ... but ... steps
Expected: UNSAT (no counterexample)
Observed: UNSAT
Evidence: no counterexample in the declared structural scope and horizon
Not established: larger structures, omitted environment behavior, implementation conformance
```
