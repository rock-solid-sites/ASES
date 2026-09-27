You are doing a BOUNDED, READ-ONLY cross-check of a structural extractor. You
are a builder-role agent. Report what you find; do not fix anything.

Repository (already checked out, do NOT create another worktree):
/home/claude-code/projects/ASES/.worktrees/jev-phase1
Branch: research/jev-phase1-565

Everything you need is under:
research/jev-bounded-judgment/phase2/

## Why this task exists

Phase 2 claims that deterministically extracted structure (from Python's stdlib
`ast`) preserves the facts needed to answer bounded questions about real code.
The entire result rests on `harness/extract.py` being correct. You are checking
that claim INDEPENDENTLY, by reading the raw source yourself and deciding what
the structure SHOULD say, then comparing against what the extractor emitted.

Do not run `harness/extract.py` to get your answer first. Read the SOURCE, form
your own judgement, and only then compare. If you read the extractor's output
first you will merely confirm it.

## Your task

Pick these SIX (module, function) pairs:

  (shlex.py,        shlex.__init__)
  (shlex.py,        split)
  (json_encoder.py, JSONEncoder.iterencode)
  (textwrap.py,     TextWrapper._wrap_chunks)
  (dataclasses.py,  dataclass)
  (configparser.py, RawConfigParser._read)

For EACH pair, do all of this by reading `corpus/<module>.py` directly:

1. State the function's parameter names, in order, as written in the `def`.
2. List the names that are ASSIGNED anywhere inside the function body
   (`x = ...`, `x += ...`, `for x in ...`, `with ... as x`, `except E as x`,
   walrus `:=`). Do NOT include names merely READ from a parameter.
3. Count the maximum CONTROL-FLOW nesting depth inside the body. A new level is
   opened by: if / elif (the `if` only) / else (no new level) / for / while /
   with / try / except handler / nested def / nested class / match. Do not count
   the function itself.
4. State whether the body contains a `try` block, and whether it contains an
   explicit `raise` statement.
5. List the names of functions/constructors CALLED directly in the body. Report
   the dotted form as written (e.g. `collections.deque`, `self.token`,
   `isinstance`). EXCLUDE any call that occurs inside a nested `def` or
   `class` body, and exclude calls inside a lambda's body is NOT excluded
   (lambdas are expressions in the enclosing function).

Then compare your independent reading against the extractor's output. Produce
the extractor's view with:

  cd research/jev-bounded-judgment/phase2
  python3 -c "
import sys; sys.path.insert(0,'harness')
import extract, json
m=extract.load_module('corpus/shlex.py','shlex')
f=m.qualified_functions['shlex.__init__']
print(json.dumps({k:f[k] for k in ('params','assigned_locals','max_nesting','has_try','has_raise')}, indent=1))
print('edges:', [e for e in m.call_edges if e[0]=='shlex.__init__'])
"

## Deliverable

Write ONE file and nothing else:
  research/jev-bounded-judgment/phase2/harness/extractor-crosscheck-mi.md

For each of the six pairs, give a table:

| field | my independent reading | extractor's output | agree? |
|---|---|---|---|

Then a findings section listing:
- every DISAGREEMENT, with the file, the line range you looked at, and which
  reading you believe is correct and WHY
- any case where you are unsure and why
- an overall verdict: does the extractor faithfully preserve the facts it claims
  to, for these six functions?

## Rules

- READ-ONLY. Create only `harness/extractor-crosscheck-mi.md`. Do NOT edit
  extract.py, gen_cases.py, validate_cases.py, score.py, run_jev.py, anything in
  corpus/, frozen/, or results/. Do not run git commit, push or checkout.
- If the extractor is wrong, say so plainly. A cross-check that finds nothing is
  a useless cross-check. Equally, do not manufacture disagreements to look
  rigorous — if it agrees, say it agrees.
- Quote the source lines you relied on. Line-referenced evidence beats
  assertion.
- Judge ONLY the six pairs above. Do not audit the whole extractor.
