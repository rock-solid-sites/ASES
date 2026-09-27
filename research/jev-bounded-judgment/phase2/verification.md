# Phase 2 independent verification

Verifier role: formal independent verifier (did not produce the artefacts).
Worktree: `/home/claude-code/projects/ASES/.worktrees/jev-phase1`, branch
`research/jev-phase1-565`. Phase 2 dir: `research/jev-bounded-judgment/phase2/`.

Method for Step 1: I read `corpus/*.py` first and derived each field by hand
from the brief's definitions, THEN ran `harness/extract.py` via `load_module`
and compared. I had not read `findings/findings.md` or any score output at the
time of the Step 1 comparison.

Two scope notes that apply to the whole table (not disagreements, but
definition mismatches between the brief and the extractor worth recording):

- (a) **Params order.** The brief asks for "`def` order"; the extractor emits
  `params` **sorted alphabetically** (`sorted(set(params))`,
  `extract.py:195`). The SETS agree in all six cases; only the ordering
  differs. Cosmetic.
- (b) **Nested-function scope.** The brief says call edges must EXCLUDE calls
  inside a nested `def`/`class` (extractor does, `extract.py:240-258`), but is
  silent on whether `assigned_locals`, `max_nesting`, `has_try`, `has_raise`
  include nested bodies. The extractor uses `ast.walk(fn)` for all four, i.e.
  it INCLUDES nested bodies (and comprehension loop variables, which are
  `Store` context). Only `JSONEncoder.iterencode` (nested `def floatstr`) and
  `dataclass` (nested `def wrap`) exercise this. I report both readings below.
- (c) **`elif` nesting.** The brief says "`else` adds no level" but does not
  mention `elif`. In `ast`, `elif` is an `If` node inside the parent's `orelse`,
  so the extractor counts each `elif` as +1 depth. Three of my six initial
  hand-computed depths were wrong for exactly this reason; re-inspection
  confirms the extractor follows its own rule (`BRANCH_NODES`,
  `extract.py:31-34`, `_max_nesting`, `extract.py:212-225`) correctly.

## Step 1 — source-to-structure check (six pairs)

Notation: M = my independent hand reading; E = extractor output.
Line numbers are 1-based in the frozen corpus files.

### 1. `shlex.py`, `shlex.__init__` (corpus/shlex.py:21-66)

| field | my reading (M) | extractor (E) | verdict |
|---|---|---|---|
| params (def order) | self, instream, infile, posix, punctuation_chars | sorted: infile, instream, posix, punctuation_chars, self | AGREE as sets; order differs per (a) |
| assigned | M-first-pass: {instream, t}; corrected: {instream, punctuation_chars, t} | {instream, punctuation_chars, t} | AGREE after correction — I first missed `punctuation_chars = ''` at line 55 inside `if not punctuation_chars:` (lines 54-57). E is right. `t` from line 64 (`t = self.wordchars.maketrans(...)`). Attribute stores (`self.x = ...`) correctly excluded by both. |
| max_nesting | M-first-pass: 1; corrected: 2 | 2 | AGREE after correction — I first missed that `elif punctuation_chars is True:` (line 56) is a nested `If` at depth 2 per (c). All other `if`s (lines 23, 25, 29, 35) are depth 1. E is right. |
| has_try | False | False | AGREE (no `try` in lines 21-66) |
| has_raise | False | False | AGREE (no `raise`) |
| calls | M listed: isinstance, StringIO, dict.fromkeys, self.wordchars.maketrans, self.wordchars.translate. E adds: deque | E is a SUPERSET and correct — I missed `deque()` at lines 48, 52, 61 (`self.pushback = deque()` etc.). `import`-bound names correctly produce no edge. | AGREE (E correct, my list incomplete) |

### 2. `shlex.py`, `split` (corpus/shlex.py:305-315)

| field | my reading (M) | extractor (E) | verdict |
|---|---|---|---|
| params (def order) | s, comments, posix | sorted: comments, posix, s | AGREE as sets; order differs per (a) |
| assigned | {lex} (line 311 `lex = shlex(...)`); `import warnings` (line 308) binds no `Name/Store`, excluded by both | {lex} | AGREE |
| max_nesting | 1 (`if s is None:` line 307, `if not comments:` line 313) | 1 | AGREE |
| has_try | False | False | AGREE |
| has_raise | False | False | AGREE |
| calls | warnings.warn, shlex, list | warnings.warn, shlex, list | AGREE exactly |

### 3. `json_encoder.py`, `JSONEncoder.iterencode` (corpus/json_encoder.py:204-257)

| field | my reading (M) | extractor (E) | verdict |
|---|---|---|---|
| params (def order) | self, o, _one_shot | sorted: _one_shot, o, self | AGREE as sets; order differs per (a) |
| assigned | body-only: {markers, _encoder, _iterencode}; incl. nested (b): + {text} | {markers, _encoder, _iterencode, text} | AGREE with the nested-inclusive reading. `text` is assigned inside nested `def floatstr` (lines 226-243, e.g. `text = 'NaN'`). The nested def name `floatstr` itself is correctly absent (a `def` name is not a `Name/Store` node). No disagreement once scope (b) is fixed: E documents walk-semantics. |
| max_nesting | M-first-pass: 2; corrected: 4 | 4 | AGREE after correction — the `if o != o: / elif o == _inf: / elif o == _neginf: / else:` chain (lines 229-237) nests three deep via (c) inside `def floatstr` (depth 1), giving depth 4. I first counted the elif-chain flat. E follows its rule correctly. |
| has_try | False | False | AGREE |
| has_raise | body-only: False; incl. nested: True | True | AGREE with nested-inclusive reading — `raise ValueError(...)` is inside `floatstr` (lines 239-241). Same scope note as assigned. |
| calls (excl. nested) | c_make_encoder, _make_iterencode, _iterencode | c_make_encoder, _make_iterencode, _iterencode | AGREE exactly. `repr(o)` inside `floatstr` correctly excluded. |

### 4. `textwrap.py`, `TextWrapper._wrap_chunks` (corpus/textwrap.py:241-342)

| field | my reading (M) | extractor (E) | verdict |
|---|---|---|---|
| params (def order) | self, chunks | sorted: chunks, self | AGREE as sets; order differs per (a) |
| assigned | {lines, indent, cur_line, cur_len, width, l, prev_line} | same 7 names | AGREE exactly. `l` (line 299 `l = len(chunks[-1])`), `prev_line` (line 334). Subscript `del`s correctly bind nothing. |
| max_nesting | M-first-pass: 5; corrected: 6 | 6 | AGREE after correction — deepest path: `while chunks:` (1, line 273) -> `if cur_line:` (2, line 313) -> `if (self.max_lines is None or ...)` (3, line 314) -> `else: while cur_line:` (4, line 324) -> `else:` (of while, no add) `if lines:` (5, line 333) -> `if (len(prev_line) + ...)` (6, line 335). I first dropped the level-3 `if` wrapping the inner `while`. E is right. |
| has_try | False | False | AGREE |
| has_raise | True (lines 245, 253 `raise ValueError`) | True | AGREE |
| calls | M listed a subset (ValueError, len, chunks.reverse, chunks.pop, self._handle_long_word, sum, map, join-via-`''.join`, lines.append, rstrip, lstrip). E: ValueError, chunks.pop, chunks.reverse, cur_line.append, join, len, lines.append, map, rstrip, self._handle_long_word, self.placeholder.lstrip, strip, sum | AGREE (E correct; my list missed the `.append` calls and `strip`). Dotted-name rendering notes confirmed sensible: `''.join(...)` renders as bare `join` (base is a Constant, `_dotted` returns `""`), `lines[-1].rstrip()` as bare `rstrip` (base is a Subscript). Deterministic consequences of `extract.py:140-148`. | AGREE |

### 5. `dataclasses.py`, `dataclass` (corpus/dataclasses.py:1156-1184)

| field | my reading (M) | extractor (E) | verdict |
|---|---|---|---|
| params (def order) | cls, init, repr, eq, order, unsafe_hash, frozen, match_args, kw_only, slots | same set, sorted | AGREE as sets; order differs per (a). (`cls` positional-only, rest kw-only; extractor flattens all three arg classes, `extract.py:162-168`.) |
| assigned | {} (no `=`/`for`/`with-as`/`except-as`/`:=` at body level; `def wrap` binds no `Name/Store`; `wrap`'s body is a bare `return`) | {} | AGREE exactly |
| max_nesting | 1 (`def wrap` line 1174 at depth 1; `if cls is None:` line 1179 at depth 1) | 1 | AGREE |
| has_try | False | False | AGREE |
| has_raise | False | False | AGREE |
| calls (excl. nested) | wrap (line 1184 `return wrap(cls)`; line 1181 `return wrap` is a read, not a call) | wrap | AGREE exactly. `_process_class(...)` inside `wrap` correctly excluded. |

### 6. `configparser.py`, `RawConfigParser._read` (corpus/configparser.py:998-1118)

| field | my reading (M) | extractor (E) | verdict |
|---|---|---|---|
| params (def order) | self, fp, fpname | sorted: fp, fpname, self | AGREE as sets; order differs per (a) |
| assigned | {elements_added, cursect, sectname, optname, lineno, indent_level, e, line, comment_start, inline_prefixes, next_prefixes, prefix, index, value, first_nonspace, cur_indent_level, mo, vi, optval, p} (20 names) | same 20 names | AGREE exactly, including `p` (dict-comprehension loop var, line ~1017 `{p: -1 for p in ...}` — a `for x` binder, `Store` context) and tuple targets (`for lineno, line`, line 1014; `optname, vi, optval = mo.group(...)`, line ~1093). |
| max_nesting | M-first-pass: 5; corrected: 6 | 6 | AGREE after correction — the option-line `if mo:` (line 1091) sits inside the `else` of the `if mo: (1068) / elif cursect is None: (1086) / else:` chain, so per (c) it is at depth 5 and its contents (`if self._strict ...` line ~1096, `if optval is not None` line ~1101) at depth 6. I first counted the elif-chain flat. E follows its rule correctly. |
| max_nesting | M-first-pass: 5; corrected: 6 | 6 | AGREE (see above) |
| has_try | False | False | AGREE (error accumulation via `e`, no `try`) |
| has_raise | True (`raise DuplicateSectionError` ~1071, `MissingSectionHeaderError` ~1088, `DuplicateOptionError` ~1097, `raise e` ~1117) | True | AGREE |
| calls | M listed a subset. E (26 edges): DuplicateOptionError, DuplicateSectionError, MissingSectionHeaderError, SectionProxy, append, elements_added.add, enumerate, first_nonspace.start, inline_prefixes.items, isspace, line.find, line.strip, line.strip.startswith, min, mo.group, optname.rstrip, optval.strip, self.NONSPACECRE.search, self.SECTCRE.match, self._dict, self._handle_error, self._join_multiline_values, self._optcre.match, self.optionxform, set, strip | AGREE (E correct; my hand list was non-exhaustive — I missed `append`, `elements_added.add`, `optval.strip`, `inline_prefixes.items`, `first_nonspace.start`, `self._join_multiline_values`, `set`, and the `raise`-site exception "calls"). Raise-site calls (`raise X(...)`) are `Call` nodes; counting them as called names is consistent with the brief's "dotted names called directly". Chained `line.strip().startswith(...)` renders as `line.strip.startswith` per `_dotted` recursion — deterministic. | AGREE |

### Step 1 summary

- **6/6 functions: extractor output confirmed correct** against the corpus
  source under the extractor's documented rules. Every first-pass disagreement
  (shlex `punctuation_chars`+`deque`, iterencode depth 4, _wrap_chunks depth 6,
  _read depth 6) resolved **in the extractor's favour** on re-inspection with
  cited lines above. I report this explicitly: the extractor survived
  adversarial re-checking; my initial readings were the faulty ones.
- No manufactured faults. Genuine documentation-grade notes (not defects):
  (a) params are alphabetical, not `def` order; (b) assigned/has_raise/has_try/
  max_nesting include nested-def bodies while call edges exclude them — the
  asymmetry is intentional and documented in code, but the brief's spec text
  only pins the call-edge side; (c) `elif` costs a nesting level while `else`
  costs none, so `max_nesting` penalises elif-chains (this is what drives
  iterencode=4 and _read=6).
- HOW CERTAIN: evidence-based (hand AST-level re-derivation per function, then
  mechanical comparison). WHAT-NOT-TESTED in Step 1: only these six pairs;
  the rest of the corpus, `render_struct` byte output, and frozen digests are
  Step 4 material.

---

## BLOCKER — appended by the ORCHESTRATOR, not by the verifier

**This section is orchestrator-authored and is NOT verifier evidence.** It is
recorded here so the blocker survives on disk in the designated artifact rather
than only in chat. Nothing above or below this line was written by the verifier
family except Step 1.

- **Recorded:** 2026-09-27T21:42Z
- **Blocks:** Step 2 (independent reproduction of the final statistics) and
  Step 3 (adversarial judgement of the material claims)

### Both designated verifiers are rate-limited

From `~/.local/share/opencode/opencode.log`:

```
21:34:20Z  ERROR  providerID=opencode modelID=muse-spark-1.3-contributor-free
                   agent=build error.error="AI_APICallError: Rate limit exceeded.
                   Please try again later."
21:34:20Z  WARN   message=retry provider=opencode attempt=1
                   code="Rate limit exceeded. Please try again later."
                   nextDelay=8740000
21:34:25Z  ERROR  "AI_RetryError: Failed after 3 attempts. Last error:
                   Rate limit exceeded. Please try again later."

21:39:03Z  ERROR  providerID=opencode modelID=mimo-v2.6-flash-free
                   agent=build error.error="AI_APICallError: Rate limit exceeded.
                   Please try again later."
21:39:03Z  WARN   message=retry provider=opencode attempt=1
                   code="Rate limit exceeded. Please try again later."
                   nextDelay=8457000
21:39:07Z  ERROR  "AI_RetryError: Failed after 3 attempts. Last error:
                   Rate limit exceeded. Please try again later."
```

| model | role | limit observed at | nextDelay | clears (approx) |
|---|---|---|---|---|
| `opencode/muse-spark-1.3-contributor-free` | designated verifier, completed Step 1 | 21:34:20Z | 8,740,000 ms ≈ 2.43 h | ~23:59Z |
| `opencode/mimo-v2.6-flash-free` | second designated verifier | 21:39:03Z | 8,457,000 ms ≈ 2.35 h | ~23:58Z |

Both free-tier Zen models exhausted at effectively the same moment, which
indicates an account-level free-tier quota rather than a per-model fault. This
is the third distinct free-model failure mode recorded in this programme, after
`longcat` (no Go entitlement) and MiMo's earlier task-completion failures.

A liveness probe of `muse-spark-1.3-contributor-free` at 21:34Z returned no
text and no error event, consistent with the limit being in force. The MiMo
dispatch produced a 0-byte event stream and no file.

### What was NOT done, and why

- The orchestrator did **not** take the verification verdict itself. The
  orchestrator authored the harness, ran the measurement and wrote
  `harness/crosscheck_stats.py`, so any verdict it produced would be
  same-family and therefore operational only.
- The orchestrator did **not** substitute an undesignated model. Per
  `model-discipline.md`, if an approved model is unreachable the correct action
  is to stop and report, not to shortlist a replacement.

### Free-tier availability probe (reconnaissance only, no dispatch)

| model | state | designated? |
|---|---|---|
| `opencode/nemotron-3-ultra-free` | **ALIVE** | no |
| `opencode/nemotron-3.5-lightning-free` | **ALIVE** | no |
| `opencode/big-pickle` | proven working earlier on 2026-09-27 (64/64 twice, byte-identical across chunkings) | no |
| `opencode/ling-3.0-flash-fin-free` | silent fail on probe; also failed the output contract during setup | no |

Live, undesignated, cross-family models therefore exist. Using one as the formal
verifier is an operator decision, not an orchestrator decision.

### How to discharge the gate

1. **Wait for the limit to clear** (~23:58Z) and re-run
   `VERIFY-BRIEF-2.md` on `opencode/muse-spark-1.3-contributor-free`. It is
   written to append to this file and to skip Step 1. This preserves the
   original verifier family and its already-recorded Step 1.
2. **Or** the operator designates one of the live undesignated models above as
   the verifier, in which case `VERIFY-BRIEF-3.md` is ready to run on it. It
   enforces derive-before-compare, forbids use of `crosscheck_stats.py` as a
   source of truth, and mandates four incremental write checkpoints.

Until one of those happens, Step 2 and Step 3 remain OUTSTANDING and Phase 2
remains partially verified.
