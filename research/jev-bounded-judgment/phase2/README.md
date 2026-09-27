# Jev bounded-judgment — Phase 2: does deterministic code structure help?

**Issue:** #570 (subissue of #565) · **Status:** design frozen for build
**Started:** 2026-09-27 · **Branch:** `research/jev-phase1-565` (worktree
`.worktrees/jev-phase1`)

## Question

Does deterministic code structure materially improve the **efficiency or
reliability of bounded semantic judgments**?

This is not a re-run of Phase 1. Phase 1's programme verdict is canonical:
no capability niche for Jev over a cheap free general model; real operational
advantages; intrinsic abstention unestablished; **Q4 — does anything survive
outside a template-generated synthetic corpus — is the binding limitation.**
Phase 2 attacks Q4 by replacing synthetic templates with **real code and real
coding decisions**.

## Hypothesis

For the same underlying problem, a deterministically extracted structural
representation changes the cost/accuracy profile of a bounded judgment
relative to raw source.

## Representations (matched pairs over identical code)

| id | representation | content |
|---|---|---|
| **R1** `raw` | relatively raw source | the module's full source text, verbatim |
| **R2** `struct` | deterministic structure | module symbol table; per-function signature, bindings, resolved + unresolved direct callees, decorators, control-flow metrics (`n_stmts`, `n_branches`, `max_nesting`, `has_try`, `has_raise`); module imports; intra-module call-graph edge list |
| **R3** `struct+minimal` | structure + only the source of the functions on the queried call path | **only where it materially tests the hypothesis** |

R2 is produced by Python's **standard library `ast` and `symtable`** — no new
infrastructure, no third-party parser. `tree-sitter`, `ast-grep`, `networkx`
and `ctags` are absent from this host (the `sg` on PATH is shadow-utils
`newgrp`, not ast-grep), so stdlib is both the preference and the only option.

## Corpus: real code, vendored and hashed

Five real Python standard-library modules, vendored into `corpus/` so the
benchmark is reproducible from committed material rather than from a
host-dependent interpreter install. Provenance (upstream path, byte size,
sha256, upstream licence) is recorded per file in `corpus/PROVENANCE.json`.

Chosen for a spread of size and character, so that any input-size effect is
visible rather than an artefact of one file:

| module | bytes | lines | character |
|---|---|---|---|
| `shlex.py` | ~13.5 K | 350 | small, call-rich parsing |
| `json_encoder.py` | ~16 K | 442 | serialisation |
| `textwrap.py` | ~19.8 K | 494 | text algorithm |
| `dataclasses.py` | ~56 K | 1453 | large, decorator-heavy, deep call graph |
| `configparser.py` | ~54.6 K | 1368 | large, sectioned, many classes |

## Ground truth is computed, never asserted

Every ground truth is derived **deterministically from the source AST** by the
same code that builds the representation. No model supplies an answer, and no
model may see an answer before committing to one.

This structurally removes the Phase-1 self-preference confound (L1/A4) rather
than relying on policy to prevent it. Phase 1's known ground-truth defect class
(D2 F1, `c-p4b` — truth not derivable from model-visible text) is the failure
mode this design has to survive, so it gets a mechanical gate rather than a
reviewer's eye.

## Admissibility gate — the core of the design

A case is scored **only** when its ground truth is independently defensible
**and** derivable from the representation the model actually sees. Every case
type therefore ships a **required-evidence predicate**: a mechanical assertion
run against each representation separately.

- predicate satisfied → condition is *derivable*, case is scored there
- predicate not satisfied → that condition is *unanswerable* for that case

An unanswerable condition is **never** scored as a model error, and is reported
separately. Per-condition admissibility is recorded, because differential
admissibility between R1 and R2 is itself a finding: **structure can remove
evidence required to derive an answer.** That is a real risk of preprocessing
and this benchmark is designed to be able to detect it, not to assume it away.

### Leak and evidence-removal checks

Run over every generated representation:

1. **No answer leak.** No representation may contain a field, label, key or
   natural-language string that states the answer to any case in the set, nor
   any ground-truth value, nor a precomputed boolean about a queried
   proposition. Checked by scanning for the queried token set and for any
   field whose name asserts a queried predicate.
2. **No evidence removal.** For each case, the required-evidence predicate must
   hold for every condition under which the case is scored.
3. **Symmetric derivability.** For a case to enter the R1-vs-R2 comparison at
   all, it must be derivable under **both**. Cases derivable under only one
   condition are reported separately as a *derivability* result, not silently
   scored, because a one-sided comparison measures the representation
   difference and nothing else.

## The honesty problem with this benchmark, stated up front

**Structure can turn a judgment into a lookup, and a lookup is not a judgment.**

If R2 answers a question by exposing the queried edge in a field, the task
under R2 may be retrieval rather than bounded judgment. Any accuracy gain is
then evidence that structure *removed the need to judge*, not that structure
improved *judging*.

So every case is classified, per condition, as:

- `lookup` — the queried fact is directly present as a field value
- `judgment` — the fact must be composed or inferred from the representation

and results are reported **split by that classification**. A gain concentrated
in `lookup` cases is reported as such and explicitly does not support a claim
about bounded-judgment quality. This is the single largest interpretation
limit in Phase 2 and it is recorded before any data exists.

## Measurements — smallest sufficient set

| quantity | why it is here |
|---|---|
| correctness (on admissible cells only) | the reliability half of the hypothesis |
| input size (bytes / tokens) | the efficiency half; structure's main claim |
| latency + tail (median, p95, p99) | Jev's verified operational advantage; does structure change it |
| cost | direct `jev-1.13.0` tariff; structure changes input tokens |
| probability behaviour | Phase 1 proved `confidence` is **derived** from the probability vector, so report `probabilities`, `max_prob`, and derived confidence side by side, never as two corroborating signals |
| robustness to irrelevant context | the same question against a source with a large deterministically-appended irrelevant block |

## Arms

- **Subject:** direct TypeSafe `jev-1.13.0` at `https://api.typesafe.ai/v1/systemone`,
  re-confirmed live before the run. Not via the Zen free route, which followup-03
  showed is refused (0/197).
- **Comparator:** a cheap free general model, in a matched representation. A
  Jev-only measurement cannot decide whether structure helps, because "structure
  helps" is a claim about the *interaction* between representation and
  mechanism. Phase 1's central lesson is that a missing comparator made a
  headline question unresolvable for a full phase.

## Models

Only the routes designated in `.crosslink/knowledge/model-discipline.md`:
`opencode/muse-spark-1.3-contributor-free` (`muse-free`) and
`opencode/mimo-v2.6-flash-free` (`mimo`). No autonomous substitution.

The Go route is unavailable on this account, so the paid-escalation clause in
`model-discipline.md` cannot be exercised: if a designated model fails a
capability gate, that is **reported**, not escalated around.

**Producer and verifier are different families.** Harness, corpus, extraction
and scoring are produced by the orchestrator; formal independent verification
uses the family that did not produce the artefact. Same-family checks are
operational only and are labelled as such.

## Gates, in order

1. All generation / extraction / scoring / analysis code **committed before any
   result is relied on**.
2. Case set and extraction logic **frozen** — a recorded sha256 over the frozen
   inputs, asserted at run time.
3. Formal verification reproduces **both** representative source→structure
   transformations **and** the final reported statistics.
4. A **clean-clone reproduction path** is provided and **verified** before
   closeout.

## Out of scope

Historical-session replay. EDASES architecture redesign. Any reconstruction or
re-run of Phase 1.

## Layout

```
phase2/
  README.md               this file
  corpus/                 vendored real source + PROVENANCE.json
  harness/
    extract.py            deterministic structure extraction (stdlib ast)
    gen_cases.py          case enumeration; ground truth computed
    validate_cases.py     admissibility: derivability, leak, evidence-removal
    run_jev.py            direct TypeSafe client
    run_general.py        comparator arm
    score.py              deterministic scorer
  frozen/                 frozen case set + extraction digest
  results/                raw requests/responses, per condition
  tables/                 derived summaries
  findings/               supported / limitations / failures
  verification.md         formal independent verification
```

## Stop condition

Benchmark frozen, executed, independently verified, reproducible from
committed material, and sufficient to state where structural preprocessing
**helps, hurts, or remains unresolved**. Then report supported findings,
limitations, failures, and the smallest justified next experiment.
