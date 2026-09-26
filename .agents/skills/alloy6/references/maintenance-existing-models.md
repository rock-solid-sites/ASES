# Maintaining large existing models

Use this workflow for a real repository model whose history, vocabulary, dialect,
or downstream tooling is part of the specification. A locally plausible formula
is not enough when the task is to reproduce a documented correction.

## Lock the maintenance contract

Before editing, record:

- the source revision and target revision, issue, standard clause, or paper result;
- the requested target Alloy dialect and Analyzer version;
- the allowed files or paragraphs and the parts that must remain untouched;
- the expected command outcomes already documented by the project;
- whether an accepted patch is available locally. If it is, inspect it; do not
  guess an alternative and call it the historical repair.

Keep syntax migration, semantic repair, and model redesign as separate changes.
If an old model does not parse in Alloy 6, a narrow semantic repair can still be
correct for its historical dialect. Report the parse boundary instead of
mass-migrating unrelated code.

## Map prose to the model's vocabulary

For each noun and condition in the requirement, locate the existing signature,
relation, helper function, and consumer that represents it. Write the mapping
down before composing a replacement formula.

Prefer a canonical helper already defined by the model. For example, if an
access-control model defines `effectiveAccess` for inherited permissions, use
that view rather than rebuilding it from direct grants and reachability merely
because the expansion appears similar. A helper may encode typing, direction,
scope, or historical intent not visible at the edit site.

If an inline alternative is necessary, establish equivalence under the model's
facts with a named assertion and bounded check. Without that evidence, label it
an alternative design rather than the accepted correction.

### Run a definition-first candidate pass

Do this before writing the replacement expression, even when the model is short:

1. Write the required source and target types plus each semantic condition from
   the issue or standard.
2. Search the whole model for field, `fun`, and `pred` declarations whose types
   or bodies mention those endpoints or the primitive relations in the clause.
   Inspect definitions, not only names or nearby code.
3. Record a compact table with candidate name, declared type, definition,
   consumers, covered clauses, and any missing clause.
4. Choose a type-compatible named view that covers the clause before composing
   an expression from its primitives. Reuse of that view elsewhere for the same
   concept is additional provenance evidence.
5. If choosing an inline composite instead, put the candidate rejection and an
   executed equivalence check in the report. If the historical dialect prevents
   that check, do not claim the inline composite reproduces the accepted repair.

Use this scratch shape:

| Requirement clause | Candidate view | Definition/consumers | Decision and evidence |
|---|---|---|---|
| source and target types plus semantic condition | named field/function/predicate | exact body and important uses | reuse, reject with reason, or equivalence command/result |

A plausible primitive formula is not a substitute for this pass. Reading the
whole file without recording candidates is also insufficient: long models make
small helper definitions easy to notice but then ignore during composition.

### Accepted-correction gate

When the request explicitly names an accepted fix, source revision, or merged
patch, historical reproduction and alternative design are different tasks.

- If the accepted diff is available, follow it within the allowed edit region.
- If the diff is unavailable, prefer the existing helper whose definition and
  name directly encode the requirement clause. Do not replace that helper with
  an ad hoc expansion because the expansion appears stronger or clearer.
- Put doubts about the accepted encoding in the report as a separate review
  finding. Do not silently change the requested historical repair.
- If neither history nor model vocabulary determines the edit, state that the
  accepted correction was not established instead of claiming reproduction.

This gate is about provenance, not blind trust: reproduce first when that is
the task, then evaluate the accepted design separately if requested.

## Respect abstraction boundaries

Classify every disputed concept as one of:

- static model structure;
- mutable model state;
- an environment or runtime input;
- an implementation detail outside the model.

Do not convert an unmodeled runtime condition into a timeless fact. Either add
an explicit environment relation and its lifecycle as a deliberate model
extension, or remove the unsupported derived property while preserving the
static distinctions the model still needs. State which option the source issue
or design authority supports.

## Make the smallest auditable patch

1. Localize the affected paragraph and every helper it calls.
2. Write a vocabulary map from each requirement clause to candidate helpers,
   including each helper's definition and consumers. Inspect all uses of the
   changed relation, predicate, or function.
3. When removing a signature, field, helper, or derived property, trace the
   deletion through declarations, constraints, command scopes, capacity
   comments, examples, and reports. Either update each dependent artifact or
   record why retaining it is semantically intentional.
4. Preserve unrelated bytes when the task requests an isolated correction.
5. Compare the resulting diff with the allowed scope and, when available, the
   accepted patch.
6. Run the project's historical baseline in its compatible Analyzer when
   available. Separately run current-version parse or command discovery only if
   that evidence is relevant.
7. Report source-diff evidence, parse evidence, and solver evidence separately.

Before delivery, fail closed: if a type-compatible named helper matches a
requirement clause, do not ship an inline reconstruction unless an equivalence
check was actually executed. List the candidate helper and the evidence for
using or rejecting it in the report.

An exact diff match proves only that the accepted source change was reproduced.
It does not by itself establish satisfiability, assertion validity, or
implementation conformance.

## Interpret Analyzer XML through its consumer

Alloy XML contains raw atom labels and tuples, not necessarily the domain names
shown by an application's converter or report. Keep two layers separate:

1. **Raw witness:** the selected skolem atoms and exact field tuples in the XML.
2. **Domain projection:** renaming, normalization, path traversal, filtering, or
   aggregation performed by the repository's converter, visualizer theme, or
   reporting code.

Start from the command-specific skolems and expand only through relations used by
the failed property. Do not treat every atom in the instance as part of the
counterexample. An empty field relation is different from unrelated atoms of
that field's target signature.

When downstream source is supplied, inspect it before normalizing labels. Cite
both the raw atom and the conversion rule in the report. If it is unavailable,
return raw identifiers and say that application-level normalization was not
established; do not invent friendly names.

From the installed skill directory, use `scripts/alloy_xml_slice.py` for a
deterministic first slice and name only fields used by the failed property:

```sh
python3 scripts/alloy_xml_slice.py counterexample.xml \
  --skolem-prefix '$Property_' \
  --field demoLink --field demoEmpty
```

Depth 0 includes tuples directly touching a selected skolem; increase
`--expand-depth` deliberately. Requested empty fields are retained with zero
tuple counts, while misspelled skolem prefixes or field labels fail nonzero.
The script reports raw identifiers only. Interpret the slice against the failed
assertion and any downstream converter before making a domain claim.

Use the helper only for trusted Analyzer-generated XML. It parses the document
in memory and rejects files larger than 32 MiB unless `--allow-large-file` is
passed after provenance and resource review.
