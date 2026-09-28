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

---

## Step 2 — independent reproduction of the reported statistics

Method: I read `findings/findings.md` ONLY to know what to check, then derived
every number below with my own throwaway `python3 -c` computations straight
from `results/jev_raw.ndjson` (268 rows = 218 admissible + 50
`not_admissible`), `results/jev_unanswerable_obs.ndjson` (268 rows, same 67
cases x 4 conditions), `frozen/cases.json` (67 cases), and `harness/score.py`
(read as a spec for the group rule, which I re-implemented independently). I
did NOT use `harness/crosscheck_stats.py` and did not copy `metrics.json`
values except as comparison targets. McNemar p-values are my own exact
two-sided binomial (`2 * P(Bin(n,0.5) <= min(b,c))`, capped at 1), not a normal
approximation. All 9 sub-checks below are derived, not trusted.

### 2.1 Per-condition table (doc §1)

My values (admissible-only means; p95 by linear interpolation):

| condition | n_adm | accuracy | state bytes | input tokens | median ms | p95 ms | cost USD |
|---|---|---|---|---|---|---|---|
| `raw` | 57 | 0.8070 (46/57) | 32781.9 | 7925.3 (tot 451743) | 337.80 | 426.65 | 0.018973 |
| `raw_ic` | 57 | 0.7368 (42/57) | 60362.9 | 15945.1 (tot 908872) | 386.11 | 451.89 | 0.038173 |
| `struct` | 52 | 0.8846 (46/52) | 17084.6 | 5334.4 (tot 277388) | 324.88 | 381.41 | 0.011650 |
| `struct_ic` | 52 | 0.9038 (47/52) | 33747.6 | 10178.6 (tot 529287) | 344.18 | 407.11 | 0.022230 |

Against the document: every cell matches to the printed precision (state
32782/60363/17085/33748; tokens 7925/15945/5334/10179; medians
337.8/386.1/324.9/344.2; p95 426.6/451.9/381.4/407.1; costs
0.018973/0.038173/0.011650/0.022230). **CONFIRMED.**

### 2.2 Paired McNemar comparisons (doc §0) — exact p-values

| comparison | n | only-first | only-second | my exact p | claimed p |
|---|---|---|---|---|---|
| raw vs struct | 52 | 2 | 4 | **0.6875** | 0.6875 |
| raw_ic vs struct_ic | 52 | 2 | 9 | **0.0654** | 0.0654 |
| raw vs raw_ic | 57 | 4 | 0 | **0.1250** | 0.1250 |
| struct vs struct_ic | 52 | 1 | 2 | **1.0000** | 1.0000 |

All four match exactly. Central claim verified: **none reaches p<0.05**
(the closest is raw_ic vs struct_ic at 0.0654). **CONFIRMED.**

### 2.3 Accuracy by case type per condition (doc §4 table)

My derivation (correct/admissible):

- `nesting_conjunction`: raw 4/5=0.8, raw_ic 2/5=0.4, struct 4/5=0.8,
  struct_ic 4/5=0.8. Claimed 0.8/0.4/0.8/0.8. **CONFIRMED.**
- `unused_import`: raw 4/5=0.8, raw_ic 4/5=0.8, struct 3/5=0.6,
  struct_ic 4/5=0.8. Claimed 0.8/0.8/0.6/0.8. **CONFIRMED.**
- `string_literal_probe`: raw 2/5=0.40, raw_ic 2/5=0.40, struct 0/0
  (no admissible cells — unanswerable by construction), struct_ic 0/0.
  Claimed 0.40 raw, unanswerable struct. **CONFIRMED.**
- Rest (checked, not all printed in doc): `direct_call`
  23/25, 22/25, 24/25, 25/25 (0.92/0.88/0.96/1.0); `param_rebound`
  8/10, 7/10, 10/10, 10/10 (0.8/0.7/1.0/1.0); `call_path2` 5/7, 5/7, 5/7,
  4/7 (0.714/0.714/0.714/0.571). Consistent with doc §4/§5.3.
  **CONFIRMED.**

### 2.4 Distraction degradation counts (doc §4)

From my §2.2 pairings: raw vs raw_ic gives 4-0 (p=0.1250); struct vs
struct_ic gives 1-2 (p=1.0000). Claimed raw loses 4/gains 0, struct loses
1/gains 2. **CONFIRMED.**

### 2.5 Group split rule (doc §3, `score.py:case_group`)

I re-implemented the rule from the code comments (struct==lookup ->
`lookup_under_struct`; raw or struct unanswerable -> `raw_only`; else
`judgment_under_both`) and applied it to `frozen/cases.json` (67 cases):
`lookup_under_struct` n=25, `judgment_under_both` n=27, `raw_only` n=15.
25+27+15=67: **no case dropped or double-counted. CONFIRMED.**

Paired raw vs struct within groups (my derivation): lookup group n=25,
raw 23/25=0.92, struct 24/25=0.96 (only_raw=1, only_struct=2, both=22);
judgment group n=27, raw 21/27=0.7778, struct 22/27=0.8148 (only_raw=1,
only_struct=2, both=20, neither=4); raw_only n=0 shared (correct — no
struct-admissible cells to pair). Gains +4.0pp and +3.7pp follow
arithmetically. All-comparable: n=52, 44/52=0.8462 vs 46/52=0.8846,
2 vs 4. **CONFIRMED.**

### 2.6 Probability (noul) behaviour (doc §6)

My derivation over admissible+parsed cells per condition:

| condition | mean | min | max | exactly 0/1 | in [0.4,0.6] |
|---|---|---|---|---|---|
| raw | 0.4509 | 0.01 | 0.99 | 0 | 7 |
| raw_ic | 0.4323 | 0.02 | 0.98 | 0 | 8 |
| struct | 0.5075 | 0.02 | 0.98 | 0 | 3 |
| struct_ic | 0.5146 | 0.03 | 0.98 | 0 | 5 |

Claimed means/min/max/0-counts/near-half counts (7/8/3/5) all match.
**CONFIRMED.**

### 2.7 Unanswerable behaviour (doc §7)

40 rows with `ground_truth is None` in BOTH raw and obs files (5 runtime +
5 semantic per condition x 4). All 40 have `parsed` present in the obs file:
**40/40 answered, 0 abstentions. CONFIRMED.** Decidedness (|noul-0.5|>0.2),
my derivation: `unanswerable_runtime` 0/5 decided in every condition
(means 0.502/0.426/0.426/0.432 — within the claimed 0.426–0.502 range);
`unanswerable_semantic` decided 3,2,3,3 of 5 across raw/raw_ic/struct/
struct_ic (means 0.322/0.348/0.400/0.388 — within 0.322–0.400). Claimed
"0/5 in every condition" and "2–3 of 5 in every condition".
**CONFIRMED.**

### 2.8 No unanswerable cell was scored

`results/jev/scored.ndjson` (268 rows): 0 rows with `ground_truth is None`
have `correct is not None`. `jev_raw.ndjson`: 0 rows with
`typed_error == "not_admissible"` have `parsed` non-null. **CONFIRMED.**

### 2.9 Cost arithmetic

451743 raw input tokens x $0.042/1M = $0.01897321 → $0.018973 ✓;
277388 struct tokens → $0.01165030 → $0.011650 ✓. Totals ratio
451743/277388 = 1.6286 → **1.63x ✓ arithmetically.** Tariff and
input-token inputs check out. **CONFIRMED with the qualification in §3.1:**
1.63x is the ratio of column TOTALS over different denominators (57 vs 52
cells). On the 52-case paired comparable set — the only set the document
itself (§1) calls interpretable — my derivation gives mean-token ratio
7941.7/5334.4 = 1.4888, i.e. **1.49x**, necessarily equal to the token
ratio since cost is linear in input tokens. State-bytes and token MEAN
ratios (1.92x/1.49x) are denominator-robust (paired recomputation:
1.9228/1.4888 — same to printed precision). The cost figure is the only
headline ratio that moves under pairing.

### Step 2 summary

All nine sub-checks reproduce: per-condition table, all four exact McNemar
p-values, the 6x4 accuracy table spot claims, distraction counts, group
split with no drops/double-counts and following gains, noul behaviour,
unanswerable 40/40 + class-dependent decidedness, no-scoring-of-unscorable,
and cost arithmetic. The single qualification is the 1.63x-vs-1.49x cost
denominator point above, which is Step 3 material, not a numerical error.
HOW CERTAIN: proven (machine re-derivation from raw rows; every claimed
digit checked). WHAT-NOT-TESTED: tier-2 live re-run (needs network +
credential; explicitly out of scope for this offline verification).

---

## Step 2 — independent reproduction of the final statistics
(appended 2026-09-28 by the verifier; Step 1 above untouched)

Method: read `findings/findings.md` ONLY for the list of claims to check, then
derived every number from raw evidence with my own commands:
`results/jev_raw.ndjson` (268 cells: 218 admissible + 50 inadmissible),
`results/jev_unanswerable_obs.ndjson` (same 268 cells; the 40
`ground_truth is None` cells carry `observation_only=true` and answered
`parsed` payloads there), `results/jev/metrics.json`,
`results/jev/scored.ndjson`, `frozen/cases.json`,
`frozen/admissibility.json`. I did NOT use `harness/crosscheck_stats.py` as a
source of truth and did not copy `metrics.json` values as findings — every
value below was recomputed (own percentile, own binomial, own group rule
re-implemented from the frozen case schema). McNemar p-values are exact
two-sided binomial (`2 * P(Bin(n,0.5) <= min(b,c))`, capped at 1.0), not normal
approximations.

### 2.1 Per-condition table (§1) — CONFIRMED cell-for-cell

My derivation vs the document's claim:

| condition | n_adm (mine/claimed) | accuracy (mine/claimed) | state bytes mean | input tokens mean | median ms | p95 ms | cost USD |
|---|---|---|---|---|---|---|---|
| `raw` | 57 / 57 | 46/57 = 0.8070 / 0.8070 | 32781.9 → 32782 / 32782 | 7925.3 → 7925 / 7925 | 337.80 / 337.8 | 426.65 → 426.6 / 426.6 | 0.01897321 → 0.018973 / 0.018973 |
| `raw_ic` | 57 / 57 | 42/57 = 0.7368 / 0.7368 | 60362.9 → 60363 / 60363 | 15945.1 → 15945 / 15945 | 386.11 / 386.1 | 451.89 → 451.9 / 451.9 | 0.03817262 → 0.038173 / 0.038173 |
| `struct` | 52 / 52 | 46/52 = 0.8846 / 0.8846 | 17084.6 → 17085 / 17085 | 5334.4 → 5334 / 5334 | 324.88 → 324.9 / 324.9 | 381.41 → 381.4 / 381.4 | 0.01165030 → 0.011650 / 0.011650 |
| `struct_ic` | 52 / 52 | 47/52 = 0.9038 / 0.9038 | 33747.6 → 33748 / 33748 | 10178.6 → 10179 / 10179 | 344.18 / 344.2 | 407.11 / 407.1 | 0.02223005 → 0.022230 / 0.022230 |

Raw file row counts independently confirm the structure: 67 cases × 4
conditions = 268 cells; admissible 57+57+52+52 = 218; inadmissible
10+10+15+15 = 50 (40 unanswerable-under-all + 10 string-probe-under-struct).
`typed_errors` in raw data = `{'not_admissible': 50}` only — **0 transport
errors, 0 parse errors**, as claimed. Verdict: **§1 table CONFIRMED exactly.**

### 2.2 Paired comparisons with exact McNemar p-values (§0) — CONFIRMED

My independent pairing (admissible + parsed on both sides, shared case_ids):

| comparison | n (mine/claimed) | only-first (mine/claimed) | only-second (mine/claimed) | exact p (mine/claimed) |
|---|---|---|---|---|
| raw vs struct | 52 / 52 | 2 / 2 | 4 / 4 | 0.6875 / 0.6875 |
| raw_ic vs struct_ic | 52 / 52 | 2 / 2 | 9 / 9 | 0.065429… → 0.0654 / 0.0654 |
| raw vs raw_ic | 57 / 57 | 4 / 4 | 0 / 0 | 0.1250 / 0.1250 |
| struct vs struct_ic | 52 / 52 | 1 / 1 | 2 / 2 | 1.0000 / 1.0000 |

Central claim "NONE reach p<0.05": **CONFIRMED.** The closest
(raw_ic vs struct_ic, p≈0.065) is above 0.05 and I recomputed it, not copied
it. Verdict: **§0 table CONFIRMED exactly.**

### 2.3 Accuracy by case type per condition (§4 table) — CONFIRMED

My derivation (admissible cells only; string_probe under struct has 5 cells
present but 0 admissible):

| ctype | raw | struct | raw_ic | struct_ic |
|---|---|---|---|---|
| `nesting_conjunction` | 4/5 = 0.8 ✓ | 4/5 = 0.8 ✓ | 2/5 = **0.4** ✓ | 4/5 = 0.8 ✓ |
| `param_rebound` | 8/10 = 0.8 ✓ | 10/10 = 1.0 ✓ | 7/10 = 0.7 ✓ | 10/10 = 1.0 ✓ |
| `direct_call` | 23/25 = 0.92 ✓ | 24/25 = 0.96 ✓ | 22/25 = 0.88 ✓ | 25/25 = 1.0 ✓ |
| `call_path2` | 5/7 = 0.714 ✓ | 5/7 = 0.714 ✓ | 5/7 = 0.714 ✓ | 4/7 = **0.571** ✓ |
| `unused_import` | 4/5 = 0.8 ✓ | 3/5 = 0.6 ✓ | 4/5 = 0.8 ✓ | 4/5 = 0.8 ✓ |
| `string_literal_probe` | 2/5 = **0.40** ✓ | **unanswerable** (0/5 adm) ✓ | 2/5 = 0.40 (re-derived) | **unanswerable** (0/5 adm) ✓ |

All three specifically challenged cells verified:
`nesting_conjunction` = 0.8/0.8/0.4/0.8 ✓, `unused_import` = 0.8/0.6/0.8/0.8 ✓,
`string_literal_probe` = 0.40 raw and 0-admissible under struct ✓.
Verdict: **CONFIRMED.**

### 2.4 Distraction degradation counts (§4) — CONFIRMED

My pairing clean→+irrelevant on shared admissible+parsed cases:
raw→raw_ic n=57, lost **4**, gained **0** (p=0.1250 per §2.2) ✓;
struct→struct_ic n=52, lost **1**, gained **2** (p=1.0) ✓.
Gap arithmetic re-derived: clean gap (4−2)/52 = 3.85pp → **+3.8pp** ✓;
+irrelevant gap (9−2)/52 = 13.46pp → **+13.5pp** ✓. Verdict: **CONFIRMED.**

### 2.5 Group split rule `case_group` (§3) — CONFIRMED

I re-implemented the rule from the frozen case schema (struct==lookup →
`lookup_under_struct`; raw or struct unanswerable → `raw_only`; else
`judgment_under_both`) without calling `score.py`. Frozen set partitions as
27 / 25 / 15 = 67: **no case dropped, none double-counted** (27+25+15=67) ✓.
Paired raw vs struct within groups: `judgment_under_both` n=27,
raw 21/27=0.7778, struct 22/27=0.8148, only-raw 1, only-struct 2, both 20,
neither 4 ✓; `lookup_under_struct` n=25, raw 23/25=0.92, struct 24/25=0.96,
only-raw 1, only-struct 2, both 22, neither 0 ✓; `raw_only` contributes 0
shared paired cases ✓. Gains: +4.0pp (0.96−0.92) and +3.7pp (0.8148−0.7778) —
**both follow arithmetically** ✓. Verdict: **CONFIRMED, including the
"same size in both groups" reading.**

### 2.6 Probability behaviour per condition (§6) — CONFIRMED

My derivation over admissible+parsed cells:

| condition | mean (mine/claimed) | min | max | exactly 0/1 (mine/claimed) | noul in [0.4,0.6] (mine/claimed) |
|---|---|---|---|---|---|
| `raw` | 0.4509 / 0.4509 | 0.01 | 0.99 | 0 / 0 | 7 / 7 |
| `struct` | 0.5075 / 0.5075 | 0.02 | 0.98 | 0 / 0 | 3 / 3 |
| `raw_ic` | 0.4323 / 0.4323 | 0.02 | 0.98 | 0 / 0 | 8 / 8 |
| `struct_ic` | 0.5146 / 0.5146 | 0.03 | 0.98 | 0 / 0 | 5 / 5 |

Verdict: **CONFIRMED exactly.**

### 2.7 Unanswerable behaviour (§7) — CONFIRMED, with one sourcing note

Sourcing note (not a discrepancy): in `results/jev_raw.ndjson` the 40
`ground_truth is None` cells have `parsed: null` / `typed_error:
"not_admissible"` — they were not answered there. The answered behaviour data
lives in `results/jev_unanswerable_obs.ndjson`, where the same 40 cells carry
`observation_only: true` and full `parsed` payloads (same `request_sha256` as
the raw file, so the same requests). All checks below are against the obs file,
which is clearly the document's source:

- 40 unanswerable cells, **40/40 parsed present, 0 abstentions** ✓
- `unanswerable_runtime`: decided (|noul−0.5|>0.2) **0/5 in all four
  conditions** ✓; means raw 0.502, struct 0.426, raw_ic 0.426, struct_ic 0.432
  → range 0.426–0.502 ✓
- `unanswerable_semantic`: decided 3/5 (raw), 3/5 (struct), 2/5 (raw_ic), 3/5
  (struct_ic) → **2–3 of 5 in every condition** ✓; means 0.322, 0.400, 0.348,
  0.388 → range 0.322–0.400 ✓

Verdict: **CONFIRMED.** The document's §7 numbers are accurate against the obs
file; a future reader should be told explicitly which file the behaviour data
comes from (it currently takes cross-checking both files to see this).

### 2.8 No unanswerable cell scored — CONFIRMED

In `results/jev/scored.ndjson` (268 rows): 0 rows with `ground_truth is None`
and `correct is not None` ✓; 0 rows with `typed_error == "not_admissible"` and
`parsed` present ✓. Same two checks against `results/jev_raw.ndjson`: 0 and 0
✓. Verdict: **CONFIRMED.**

### 2.9 Cost arithmetic (§1 tariff + §2 ratios) — CONFIRMED

My computation: tariff $0.042/1M input, output free, applied to recorded
`usage.input_tokens` reproduces every cost cell to the precision shown
(raw $0.01897321→0.018973; raw_ic $0.03817262→0.038173;
struct $0.01165030→0.011650; struct_ic $0.02223005→0.022230) ✓; tariff record
in `metrics.json` (`usd_per_1M_input: 0.042, output: free`, sourced to
followup-04 TypeSafe docs 2026-09-26) matches the document ✓. Ratios
re-derived: state 32781.9/17084.6 = **1.9188× → 1.92×** ✓; tokens
7925.3/5334.4 = **1.4857× → 1.49×** ✓; cost 0.01897321/0.01165030 =
**1.6286× → 1.63×** ✓. Verdict: **CONFIRMED.**

### Step 2 summary

All nine checks CONFIRMED against raw evidence with exact agreement (up to
stated rounding): per-condition table, four exact McNemar p-values with the
none-significant central claim, the 6×4 type table including all three
challenged rows, distraction counts and both gap figures, the group split with
no drop/double and both gain figures, the noul table, unanswerable behaviour,
the no-scoring-of-unanswerable integrity property, and the cost arithmetic with
all three ratios. One documentation note (not a defect): §7's behaviour data
comes from `jev_unanswerable_obs.ndjson`, which takes both-files comparison to
discover.
HOW CERTAIN: proven (machine re-derivation from the committed raw rows for
every number; the only hand arithmetic is the two gap divisions, shown above).
WHAT-NOT-TESTED in Step 2: whether the raw rows themselves faithfully record
the live endpoint (no re-run without a credential); repeat stability of any
cell; anything outside the nine items.

---

## Step 3 — adversarial judgement

Argued from the Step 2 evidence, not preference. Each item carries WHY (reasoning) / WHAT (basis) / HOW CERTAIN (guess | evidence-based | proven) / WHAT-NOT-TESTED.

### 3.1 Is "efficiency, not accuracy" the right headline, or an under-claim?

Right headline, and refusing the accuracy claim at n=52 is justified. WHY: the four paired p-values (0.6875/0.0654/0.1250/1.0000, independently re-derived in Step 2) leave no room for an accuracy headline — the closest (raw_ic vs struct_ic, 0.0654) still fails at α=0.05, and with four comparisons no multiplicity correction would help. Presenting "structure helps accuracy" would require either a larger n or a pre-registered single comparison, neither of which exists. WHAT: Step 2.2 table + doc §0/§8. HOW CERTAIN: proven (exact arithmetic). WHAT-NOT-TESTED: whether a larger n would flip the result — that is the proposed next experiment, not this verdict.

One genuine qualification (documentation-grade, not a numerical error): the "1.63× cheaper" headline ratio is the ratio of cost-column TOTALS over different denominators (57 raw vs 52 struct cells). On the 52-case paired comparable set — the only set the document itself (§1) calls interpretable — cost ratio = token ratio = 1.4888 → 1.49x (my derivation, Step 2.9), because cost is linear in input tokens. The state-bytes (1.92x) and token (1.49x) MEAN ratios are denominator-robust (paired recomputation 1.9228/1.4888, identical to printed precision). So the efficiency direction is exact and the size/token figures are paired-stable, but the cost figure as headlined violates the document's own "only paired comparisons are interpretable" rule. A reader comparing "1.63× cheaper" against the paired accuracy gap (+3.8pp) is mixing a totals ratio with a paired gap. The fix is one sentence (report paired cost 1.49x alongside); nothing about the efficiency conclusion changes. HOW CERTAIN: proven. This is the sharpest thing in this verification and it is still minor.

### 3.2 Is the no-lookup-concentration reading sound? Non-result vs dressed finding?

The document's call — NON-RESULT — is the right call, and it is stated honestly. WHY: with 2 and 4 discordant cells total, the group comparison (lookup +4.0pp on n=25, judgment +3.7pp on n=27) has no discriminating power between "helps judgment", "helps lookup", and "nothing happened" — the document says exactly this ("consistent with all three"). A dressed finding would have claimed the equal gains as positive evidence; instead §3.1 labels it "the strongest argument for a larger n", i.e. evidence of an open question, not an answer. WHAT: Step 2.5 (1-vs-2 discordants per group). HOW CERTAIN: evidence-based. WHAT-NOT-TESTED: the true group-specific effects (needs the ~300-case enlargement).

### 3.3 Is the robustness signal (raw 4-0 vs struct 1-2, p=0.125) oversold?

No — it is labelled "suggestive... not a supported result" twice (§4, §8 table: "suggestive"). WHY: p=0.125 is reported, not hidden; n=5-per-type is flagged; the gap-widening figures (+3.8pp → +13.5pp) are descriptive of the sample, and I verified the arithmetic follows from the paired counts. An oversell would suppress the p-value or upgrade "suggestive" to "helps"; neither happens. If anything the document underplays by burying that raw_ic vs struct_ic (p=0.0654) is the nearest-to-significant result in the whole phase. WHAT: Steps 2.2/2.4 + doc §4/§8. HOW CERTAIN: evidence-based. WHAT-NOT-TESTED: whether the nesting_conjunction mechanism story (brittle composition over long raw surface) replicates — it is one 5-case row.

### 3.4 Evidence-removal (string_literal_probe): "structure HURTING" or scoping decision?

Fairly characterised as structure hurting *as a replacement*, with the scope made explicit. WHY: the probe fired by design (5/5 struct cells inadmissible, verified Step 2.3), and the document's actual sentence is "structure does not make the model better or worse; it makes the question unaskable" plus "a correctness hazard, not a speedup" — conditioned on silent dropping ("A preprocessing layer that SILENTLY drops the evidence"). That conditioning is the scoping decision made visible: pair structure with its evidence, never replace. Calling it "hurting" without that conditioning would be unfair; with it, it is the measured consequence of the replacement pattern. WHAT: Step 2.3 + doc §5.1. HOW CERTAIN: evidence-based. WHAT-NOT-TESTED: whether keeping literals in the structure (the proposed design decision) preserves the efficiency win — correctly deferred to the next experiment, not claimed here.

### 3.5 `unused_import` 0.6 vs 0.8: cost or noise at n=5?

Correctly called "a flag for enlargement, not a claim" (doc §5.2). WHY: a 1-cell swing at n=5 moves the row by 0.20 — the 0.6-vs-0.8 gap IS one cell (3/5 vs 4/5, verified Step 2.3). The document reports the direction, attributes a mechanism ("more compact representation made the composition harder"), and explicitly withholds claim status. That is the most that n=5 permits, and it is what was done. WHAT: Step 2.3. HOW CERTAIN: proven (counts) for the numbers; guess for the mechanism attribution (one candidate among several — e.g. import-list/name-loaded intersection across two rendered sections). WHAT-NOT-TESTED: which mechanism; persistence across modules.

### 3.6 Anything overstated, understated, or beyond-sample? Anything missing from §9?

Overstated: only the §3.1 cost-ratio framing (minor, above). Understated, if anything: (a) the scorer-bug catch (§10 — the condition-relative split silently dropped all 25 converted cases; finding and fixing this pre-report is a load-bearing honesty result that the document gives one paragraph); (b) the gate catching 10 wrong ground truths pre-run (same — this is the admissibility machinery earning its keep twice, and it strengthens trust in the 218 scored cells). Beyond-sample: I find none — every general sentence I checked is hedged to the sample ("at this sample size", "n=5, so...", "one language", "one distractor"). Missing from §9: two small items — (i) no repeat measurement is listed (it IS listed: item 9, "Single run per cell, no repeats" — so not missing); (ii) the `classification: null` stored on all `_ic` rows in jev_raw.ndjson (only raw/struct rows carry the condition-relative label) is an undocumented row-shape quirk a re-analyst must discover; harmless since grouping is intrinsic from frozen/cases.json, but worth one line. Also §9 could state the paired-cost figure (1.49x) per its own §1 rule. HOW CERTAIN: evidence-based (full read of §§0–11 against Step 2). WHAT-NOT-TESTED: external validity beyond this corpus/mechanism — correctly listed as limitations 2/4, not re-tested here.

### 3.7 Are the limitations honest?

Yes. Each of the seven named constraints (one mechanism; whole-module only; 5 modules one language; one distractor with zero overlap; no repeats; template-generated questions over real code; tariff-dependent cost) is accurate against the artefacts I inspected (67-case composition in MANIFEST; distractor_sha256 present only on _ic rows with zero-overlap claim in MANIFEST; single latency per cell; tariff string in metrics.json matching doc). The document goes further than most by listing its own caught bugs (§10) as results. No limitation I found is absent except the two documentation-grade notes in §3.6. HOW CERTAIN: evidence-based. WHAT-NOT-TESTED: whether the limitations interact (e.g. template questions × single mechanism) — second-order, fairly out of scope.

### 3.8 Is the smallest-next-experiment actually smallest, and does it avoid unopened questions?

Yes, with one sequencing judgement I endorse. WHY: the three items map 1:1 onto the three directionally-positive-but-underpowered openings (accuracy gap → ~300 cases with the SAME pre-registered McNemar read; single-mechanism → one second mechanism with the transport control named; evidence-removal → settle the literals design decision BEFORE scaling so the wrong thing isn't measured at scale). The deliberately-NOT list (no R3, no session replay, no architecture) refuses exactly the budget sinks this phase did not open. The "fix literals first, then scale" ordering is the cheapest-test-first instinct applied correctly: scaling before the representation decision would measure the wrong artefact. WHAT: doc §11 against §§0–8. HOW CERTAIN: evidence-based (design judgement, not arithmetic). WHAT-NOT-TESTED: the power calculation behind "~300" (a 3.8pp gap detectable at n≈300 by McNemar exact — I did not independently recompute the power curve; taking the number as stated).

## Step 4 — integrity and reproduction

- **Unmodified from `ef4dc698`:** `git diff ef4dc698 --stat` over `results/jev_raw.ndjson`, `results/jev_unanswerable_obs.ndjson`, `results/jev/`, `frozen/`, `corpus/`, `harness/score.py`, `harness/run_jev.py`, `harness/extract.py` is EMPTY (exit 0) — the measured artefacts and scoring/running code are byte-identical to the measured-run commit. The only diffs vs ef4dc698 in phase2/ are post-measurement additions disclosed by their own commits/log lines: `harness/crosscheck_stats.py` + `harness/mimo-mini-check.md`, `results/verify-*.jsonl/.err`, `results/autoretry.log` modifications, and this `verification.md`. Post-`reproduce.sh` `git status` over frozen/results/jev/harness/corpus: clean (the Tier-1 regen rewrote frozen files byte-identically). So: the measurement inputs/outputs are intact; the "only new file" phrasing in the brief is outdated (verification tooling accreted afterwards), but every accretion is additive, committed or log-visible, and none touches the evidence chain.
- **Frozen digests:** corpus (6 files), `extract/gen_cases/represent/validate_cases.py`, `frozen/cases.json`, `frozen/admissibility.json` — 12/14 MATCH `frozen/MANIFEST.md`. Two MISMATCH, both explained and non-load-bearing: `harness/run_jev.py` and `harness/score.py` were fixed AFTER the manifest was frozen (manifest commit 1dd546b1 "before any measured run"; fixes landed in ef4dc698): run_jev gained `--send-unanswerable` (the observation-only send that produced the 40 obs cells), score gained the intrinsic `case_group` (the fix doc §10 discloses — the old condition-relative split silently dropped all 25 converted cases). The manifest's "asserted at run time" language cannot have covered these two rows as printed; but the run-time assertions that matter are per-case module/struct digests (validate_cases.py:185-187, recorded inside cases.json), which DO match, and metrics.json carries the NEW `paired_by_case_group` key, proving the report was produced by the fixed scorer. Net: a manifest-documentation wart (two stale rows), not a measurement integrity failure. The manifest should gain one line noting the two post-freeze script fixes with their commit.
- **Re-run:** `bash reproduce.sh` (Tier 1, offline) prints `REPRODUCTION OK (tier 1)`: cases.json digest OK, admissibility.json digest OK, metrics.json re-score byte-identical (sha256 2ce8ac4e…). Tier 2 skipped (no `--live`; needs network + credential). REPORTED AS REQUIRED.
- **Credential scan:** grepped phase2/ for key-value patterns (`sk-`, bearer, `api[_-]?key=...` with values, 64-hex holders). Only hits: sha256 digests (expected), the credential-source LABEL `secrets/typesafe.env#TYPESAFE_API_KEY` (a pointer, not a value — present in every result row by design), and NAME mentions in reproduce.sh/run_jev.py/briefs (paths, not values). The verify-*.jsonl transcripts embed prior tool I/O but no secret values. NO CREDENTIAL VALUES IN phase2/. (Values live in `~/.local/share/opencode/auth.json` and `~/.secrets/typesafe.env`, neither in the repo.)
- **One-question-per-request / no scenario concatenation:** every one of the 268 raw rows has `request.questions` with exactly one key (`q`, type noul) — verified `{1}` distinct count. State composition: all 67 clean-condition states contain no `uuid` text; all 134 `_ic` states contain it (distractor appended, `distractor_sha256` set, clean `module_sha256` unchanged). Representation `kind` values confirm single-module states (`raw_source_verbatim` / `deterministic_structure` / `raw_source_plus_distractor` / `structure_plus_distractor_structure`). The harness never concatenated two scenarios into one state. CONFIRMED.

## Overall verdict

**PASS WITH FINDINGS** — every load-bearing number reproduces exactly (6/6 extractor pairs, 9/9 statistics groups, all four exact McNemar p-values, 40/40 unanswerable behaviour, byte-identical Tier-1 reproduction), and the document's restrained readings (non-result on lookup, suggestive-only on robustness, flag-only on unused_import) are the right calls at this n; the single most important qualification is that the headlined "1.63× cheaper" cost ratio mixes denominators (57 vs 52 cells) and the paired-comparable figure per the document's own §1 rule is 1.49× — direction exact, magnitude slightly overstated as framed — plus two documentation-grade notes (two stale MANIFEST rows for the post-freeze script fixes; `_ic`-row `classification:null` quirk and obs-file sourcing worth one line each).

## Limitations of this verification

- No Tier-2 live re-run: whether the committed raw rows faithfully record the live `jev-1.13.0` endpoint was not re-tested (needs network + TYPESAFE_API_KEY; explicitly out of scope offline).
- No repeat-stability measurement: cell-level nondeterminism is unquantified here as in the document (Phase 1 followup-04's 16/16 is cited, not re-run).
- Step 1 covered only the six designated (module, function) pairs; the rest of the corpus and `render_struct` byte output were checked via digest (validate_cases), not by hand.
- The "~300 cases" power claim in the proposed next experiment was not independently recomputed.
- A second verifier appended a concurrent Step 2 variant to this file; both variants agree on all numbers (independent convergence), and nothing below depends on which variant is read — but the file now carries two Step 2s, which a reader should not mistake for disagreement.

---

## Step 3 — adversarial judgement (appended 2026-09-28 by the verifier)

I argue each point from the re-derived numbers in Step 2, not from preference.
Format per point: WHY / WHAT / HOW CERTAIN / WHAT-NOT-TESTED.

### 3.1 "Efficiency, not accuracy" headline — the right headline, and refusal to claim accuracy is statistically forced, not modesty

WHY: at n=52 with 6 total discordant cells (raw vs struct), no honest reading
can reach significance: even a 4-0 shutout on this base gives exact p=0.125
(re-derived in §2.2 for raw→raw_ic). The most generous legal aggregation — a
sign test on "structure at-or-above in all 4 comparisons" under the global
null — gives p=1/16=0.0625, still above 0.05. Presenting the +3.8pp direction
as "structure helping" would therefore be claiming what the design cannot
support, repeating exactly the Phase 1 lesson the document cites. WHAT: the
headline is correct and the refusal is justified at n=52 — it is not an
under-claim, it is the only claim the arithmetic permits. HOW CERTAIN:
evidence-based (recomputed p-values plus the sign-test bound above).
WHAT-NOT-TESTED: whether a larger n would convert the direction (that is §11's
job, and it is framed as a real negative if it does not survive).

### 3.2 No-lookup-concentration reading — "NON-RESULT" is the right call, and calling it anything more would be dressing

WHY: the entire group comparison rests on 1-vs-2 and 1-vs-2 discordant splits
(§2.5). The "same size gains" (+4.0pp vs +3.7pp) are each a single net cell
flipping. Any of "helps judgment", "helps lookup", "nothing happened" predicts
these counts about equally well — I checked: moving ONE cell in either group
erases or doubles the effect. WHAT: the document's downgrade of its own
designed analysis to a non-result is honest; a finding label here would be a
non-result dressed as one. HOW CERTAIN: evidence-based (counts too small for
any discrimination, shown by the one-cell sensitivity). WHAT-NOT-TESTED:
discrimination at larger n (proposed in §11.1).

### 3.3 Robustness signal (raw 4-0 vs struct 1-2, p=0.125) — NOT oversold

WHY: the document had every incentive to promote its most interesting pattern
(the gap widening +3.8pp → +13.5pp, which I verified arithmetically) and instead
labels it "suggestive sign pattern, not a supported result", keeps p=0.125
visible, and flags n=5 per type. I probed the mechanism claim one level deeper
than the document: the nesting_conjunction 0.8→0.4 collapse is exactly two
cells flipping (json_encoder and textwrap, both yes→no against ground truth
yes; dataclasses was already wrong in both). Two flips carrying a headline
sub-claim is fragile — and the document says so itself ("n=5 per case type ...
suggestive"). WHAT: appropriately hedged; not oversold. HOW CERTAIN:
evidence-based (cell-level flip inspection + the document's own hedges).
WHAT-NOT-TESTED: whether the two flips replicate (no repeats exist).

### 3.4 Evidence-removal finding (string_literal_probe) — correctly characterised as structure HURTING, and the "scoping decision" reframe fails

WHY: the adversarial reframe would be "structure never promised literals, so
unanswerability is scope, not harm". It fails on the document's own terms: the
hazard exists precisely when a preprocessing layer is deployed as a replacement
— silent evidence-dropping is then a correctness hazard regardless of intent,
and the probe measured it (5/5 inadmissible under struct by the gate,
re-derived in §2.3) rather than hypothesising it. The document also volunteers
the defence's best fact (raw itself only 0.40, so the question is hard even
with evidence) instead of hiding it. WHAT: "structure HURTS here" is the fair
characterisation; the scoping reframe is considered and defeated in-text.
HOW CERTAIN: evidence-based. WHAT-NOT-TESTED: whether keeping literals in the
representation (§11.3's design decision) preserves the efficiency gains.

### 3.5 `unused_import` worse under structure (0.6 vs 0.8) — correctly called a cost-flag, not noise-dismissed and not claimed

WHY: at n=5 the entire gap is ONE cell (4/5 vs 3/5). Calling it "structure
harms composition" would be noise-as-claim; calling it "noise, ignore" would
be claim-asymmetry (counting 4-0/1-2 patterns as suggestive while dismissing
this one). The document threads it exactly right: "not an extraction defect"
(checked: both sides of the intersection are emitted), "a flag for
enlargement, not a claim". WHAT: the handling is even-handed and consistent
with §§3–4 hedging. HOW CERTAIN: evidence-based (one-cell margin arithmetic).
WHAT-NOT-TESTED: replication at larger n per type.

### 3.6 Overstatement / understatement / beyond-sample sweep

- Overstated: nothing I can defend. Every accuracy-adjacent statement carries
  its p-value or an explicit "unresolved"/"non-result"/"suggestive" label (§8
  table verified against §§0–7: each row matches the section evidence).
- Understated: arguably the efficiency floor argument (§2
  "1.92× is a floor, not a ceiling") — it is presented as WHAT-NOT-TESTED
  context, but it is the load-bearing EDASES consequence (whole-module
  rendering of 88 functions/260 edges for one-function questions; I confirm
  the configparser scale claim is at least plausible given state bytes 32782
  mean raw vs single-question scope — though I did NOT independently count 88
  functions/260 edges, see limitations). This is emphasis, not error.
- Beyond-sample: the EDASES consequence in §7 ("a gate needs an explicit
  derivability check") generalises from 10 unanswerable cases on one mechanism
  to a design prescription. It is flagged as a consequence, and Phase 1
  agreement is cited — but strictly it inherits the one-mechanism limit (§9.2).
  Acceptable as a recommendation, not as a result; the document's own §9.2
  covers it.
- Missing from §9: two small items. (a) The endpoint is not frozen — a future
  live re-run measures endpoint drift, not reproduction failure (reproduce.sh
  says this; §9 does not list it). (b) §7's behaviour data comes from
  `jev_unanswerable_obs.ndjson`, a second run whose latency column differs from
  the raw file for identical requests (same request_sha256, e.g.
  shlex.direct_call.001 raw 335.04ms vs 380.6ms) — the document never names the
  file, and per-cell latency/parsed comparisons across the two files are not
  discussed. Neither affects any number; both are documentation gaps. HOW
  CERTAIN: evidence-based (text-vs-evidence comparison). WHAT-NOT-TESTED: the
  88-functions/260-edges scale figures (not recounted).

### 3.7 Limitations honesty (§9, nine items) — honest, each independently checkable from my derivations

1. n=52 underpowered — confirmed (§2.2). 2. one mechanism — confirmed:
   model_id is jev-1.13.0 in 268/268 cells, mechanism jev_direct throughout,
   single endpoint. 3. whole-module only — confirmed by representation kinds
   (raw_source_verbatim / deterministic_structure, full-module state bytes).
   4. one language, vendored stdlib — 5 subject modules, all Python (module
   counter re-derived: shlex 46, dataclasses 46, configparser 46, json_encoder
   42, textwrap 38 admissible cells). 5. five per type — confirmed in §2.3
   table. 6. one distractor — confirmed: exactly one non-null
   distractor_sha256 across 134/134 ic cells. 7. template-generated questions —
   confirmed by inspection (uniform "In this module, does X directly call Y?"
   phrasing, all 268 questions type noul with single key "q"). 8. tariff —
   confirmed (§2.9). 9. single run, no repeats — confirmed: 0 duplicate
   (case_id, condition) pairs in 268 rows. WHAT: no limitation is missing that
   the evidence supports, beyond the two documentation gaps in §3.6.
HOW CERTAIN: proven for the checkable items (machine counts). WHAT-NOT-TESTED:
whether template phrasing itself biases the mechanism (untestable from inside
this data).

### 3.8 Smallest next experiment (§11) — actually the smallest, and it refuses the tempting spends

WHY: each prong answers a question THIS phase opened and nothing else —
(1) n≈300 keeps the pre-registered McNemar read (a 3.8pp gap becomes
detectable; non-survival is a "real negative", i.e. falsifiable);
(2) a second mechanism answers generalisability, with the followup-05
transport control made mandatory rather than optional; (3) the literals design
decision must precede scaling, else the scale-up "measures the wrong thing".
The deliberately-NOT list (no R3, no session replay, no architecture) maps
exactly onto spends this phase gave no reason for. One adversarial probe: is
(3) really prior to (1)? Yes — if literals are restored, the efficiency ratios
(§2) shift and the string-probe class changes meaning, so scaling first would
measure a representation already slated for redesign. WHAT: smallest and
correctly ordered; no budget spent on unopened questions. HOW CERTAIN:
evidence-based (design-logic check against Steps 2–3 findings; I did not
cost the experiment). WHAT-NOT-TESTED: actual budget/tariff feasibility of the
second mechanism route.
---

## Step 2 — independent re-derivation of every reported statistic

Method: fresh analysis in this session with Python stdlib only (`json`,
`math`, `statistics`, `collections`). I did NOT import or run
`harness/score.py` for these numbers (I read it afterwards to check the
`case_group` rule against my own reimplementation). Sources:
`results/jev_raw.ndjson` (268 rows = 67 cases x 4 conditions),
`results/jev_unanswerable_obs.ndjson` (268 rows),
`results/jev/metrics.json`, `results/jev/scored.ndjson`,
`frozen/cases.json`, `frozen/admissibility.json`.
McNemar p-values computed as the exact two-sided binomial
(2 x one-sided tail via `math.comb`); I also checked the
sum-of-probabilities-<=-observed exact variant and it gives identical values
to 4dp on all four comparisons (0.6875, 0.0654, 0.1250, 1.0000), so the
p-values are variant-robust. Tariff used: $0.042/1M input tokens, output free.

### 2.1 Per-condition table (findings §1) — ALL MATCH

| condition | n_adm (mine/doc) | accuracy | state bytes mean | input tokens mean | median ms | p95 ms | cost USD |
|---|---|---|---|---|---|---|---|
| raw | 57/57 | 0.8070/0.8070 | 32781.9/32782 | 7925.3/7925 | 337.80/337.8 | 426.65/426.6 | 0.018973/0.018973 |
| raw_ic | 57/57 | 0.7368/0.7368 | 60362.9/60363 | 15945.1/15945 | 386.11/386.1 | 451.89/451.9 | 0.038173/0.038173 |
| struct | 52/52 | 0.8846/0.8846 | 17084.6/17085 | 5334.4/5334 | 324.88/324.9 | 381.41/381.4 | 0.011650/0.011650 |
| struct_ic | 52/52 | 0.9038/0.9038 | 33747.6/33748 | 10178.6/10179 | 344.18/344.2 | 407.11/407.1 | 0.022230/0.022230 |

218 scored cells = 57+57+52+52. Every admissible sent cell has HTTP 200 and a
parsed response (0 parse failures); the only `typed_error` value anywhere is
`not_admissible` (50 cells: 40 unanswerable-under-all + 10
string-literal-under-struct). `results/jev/metrics.json` by_condition matches
my derivation field-for-field (spot-checked acc/n/cost/state/tokens).

### 2.2 The four paired comparisons (findings §0) — ALL MATCH, none significant

| comparison | n | only-first (mine/doc) | only-second | exact McNemar p (mine/doc) | p<0.05? |
|---|---|---|---|---|---|
| raw vs struct | 52 | 2/2 | 4/4 | 0.6875/0.6875 | no |
| raw_ic vs struct_ic | 52 | 2/2 | 9/9 | 0.0654/0.0654 | no |
| raw vs raw_ic | 57 | 4/4 | 0/0 | 0.1250/0.1250 | no |
| struct vs struct_ic | 52 | 1/1 | 2/2 | 1.0000/1.0000 | no |

Pairing is on case_ids admissible AND parsed in both conditions (52/52/57/52).
Accuracies on the shared sets recomputed: raw 0.8462 vs struct 0.8846 (gap
+3.8pp ✓); raw_ic-on-shared-52 0.7692 vs struct_ic 0.9038 (gap +13.5pp ✓).

### 2.3 Accuracy by case type per condition (findings §4 table + §5.1) — ALL MATCH

| ctype | raw | struct | raw_ic | struct_ic |
|---|---|---|---|---|
| nesting_conjunction (n=5) | 4/5=0.800 ✓ | 4/5=0.800 ✓ | 2/5=0.400 ✓ | 4/5=0.800 ✓ |
| param_rebound (n=10) | 8/10=0.800 ✓ | 10/10=1.000 ✓ | 7/10=0.700 ✓ | 10/10=1.000 ✓ |
| direct_call (n=25) | 23/25=0.920 ✓ | 24/25=0.960 ✓ | 22/25=0.880 ✓ | 25/25=1.000 ✓ |
| call_path2 (n=7) | 5/7=0.714 ✓ | 5/7=0.714 ✓ | 5/7=0.714 ✓ | 4/7=0.571 ✓ |
| unused_import (n=5) | 4/5=0.800 ✓ | 3/5=0.600 ✓ | 4/5=0.800 ✓ | 4/5=0.800 ✓ |
| string_literal_probe (n=5) | 2/5=0.400 ✓ (§5.1) | 0 adm (unanswerable) ✓ | 2/5=0.400 | 0 adm (unanswerable) ✓ |

MISMATCH (wording, small but real): findings §5.2 says "Raw 0.8, struct 0.6
under both clean and distractor conditions." The numbers show struct is 0.6
clean but **0.8 under distraction** (4/5). Raw holds 0.8 under both; struct
does not hold 0.6 under both. Carried to Step 3 as finding F2.

### 2.4 Degradation under distraction (findings §4) — MATCH, with case IDs

- raw -> raw_ic: lost 4, gained 0 ✓. Lost:
  `json_encoder.direct_call.003`, `json_encoder.nesting_conjunction.001`,
  `json_encoder.param_rebound.002`, `textwrap.nesting_conjunction.001`.
- struct -> struct_ic: lost 1, gained 2 ✓. Lost:
  `configparser.call_path2.001`. Gained: `configparser.unused_import.001`,
  `dataclasses.direct_call.001` (these two gains are exactly the struct_ic
  recoveries visible in §2.3: unused_import 3/5->4/5, direct_call 24/25->25/25).

### 2.5 Lookup-vs-judgment split (findings §3) — MATCH; grouping rule verified

Reimplemented `case_group` from `frozen/cases.json` classifications
independently (struct==lookup -> lookup_under_struct; either side
unanswerable -> raw_only; else judgment_under_both). Group sizes over the 67
cases: 25 / 15 / 27 — matches the frozen classification Counter
(25 judgment/lookup, 10债+5 unanswerable-involving, 27 judgment/judgment).
On the 52 shared paired cases: `judgment_under_both` n=27, raw 0.7778,
struct 0.8148 (+3.7pp ✓), only-raw 1, only-struct 2, both 20;
`lookup_under_struct` n=25, raw 0.9200, struct 0.9600 (+4.0pp ✓), only-raw 1,
only-struct 2, both 22; `raw_only` contributes 0 shared cells.
27+25+0 = 52: no case dropped, none double-counted (pairing keys on unique
case_id). `score.py:case_group` (lines 47-67) implements the same rule, and
`score.py:main` (lines 155-161) correctly groups from the FROZEN intrinsic
classification, not the condition-relative row value — the §10 scorer-bug fix
is present in the current code. `metrics.json/paired_by_case_group` matches:
(27, 1, 2) and (25, 1, 2). Total discordant cells in raw-vs-struct: 6 ✓.

(typographical: the grouping Counter line in my working notes contained a
stray non-ASCII token; the counts 25/15/27 are as stated.)

### 2.6 Probability behaviour (findings §6) — ALL MATCH

| condition | mean noul | min | max | exactly 0/1 | near 0.5 |
|---|---|---|---|---|---|
| raw | 0.4509 ✓ | 0.01 ✓ | 0.99 ✓ | 0 ✓ | 7 ✓ |
| struct | 0.5075 ✓ | 0.02 ✓ | 0.98 ✓ | 0 ✓ | 3 ✓ |
| raw_ic | 0.4323 ✓ | 0.02 ✓ | 0.98 ✓ | 0 ✓ | 8 ✓ |
| struct_ic | 0.5146 ✓ | 0.03 ✓ | 0.98 ✓ | 0 ✓ | 5 ✓ |

(`noul_at_0_or_1` uses v<=0.0 or v>=1.0, same as scorer.)

### 2.7 Unanswerable behaviour (findings §7) — ALL MATCH

- 40 unanswerable cells (10 cases x 4), all answered with HTTP 200 in
  `jev_unanswerable_obs.ndjson`: 40/40, 0 abstentions ✓.
- `unanswerable_runtime`: per-condition means 0.502/0.426/0.426/0.432
  (range 0.426–0.502 ✓); decided (|noul-0.5|>0.2): 0/5 in every condition ✓.
- `unanswerable_semantic`: means 0.322/0.348/0.400/0.388 (range 0.322–0.400
  ✓); decided: 3/2/3/3 of 5 ✓ ("2–3 of 5 in every condition").

### 2.8 No unanswerable cell scored — CONFIRMED

`results/jev/scored.ndjson` (268 rows): all 40 rows with `ground_truth is
None` have `correct is None` (0 violations). In the main run the 50
inadmissible cells were never sent (`typed_error: not_admissible`, parsed
null). The 40 observation-run answers exist only in
`jev_unanswerable_obs.ndjson`, which was never scored.

### 2.9 Efficiency ratios and the cost column — ARITHMETIC MATCHES, DENOMINATOR PROBLEM

- Table ratios: 32782/17085 = 1.9188 -> **1.92x** ✓;
  7925/5334 = 1.4858 -> **1.49x** ✓; 0.018973/0.011650 = 1.6286 -> **1.63x** ✓.
- Recomputed on the SHARED 52 cases: state 32850.4/17084.6 = **1.9228**
  (-> 1.92x, same rounding); tokens 7941.7/5334.4 = **1.4888** (-> 1.49x,
  same rounding); cost ratio on shared 52 = **1.4888** — necessarily identical
  to the token ratio, because cost is a linear function of input tokens.
- The 1.63x is the ratio of condition TOTAL costs over DIFFERENT denominators
  (57 raw cells vs 52 struct cells). Exact decomposition:
  1.4888 (per-case token saving) x 57/52 (1.0962, the admissibility gap) =
  1.6320. So "1.63x cheaper" bundles the efficiency gain with the fact that 5
  fewer cases were answerable under structure.
- Findings §2 says these are "exact counts over the same 52 comparable
  cases". That sentence is TRUE for the rounded state/token ratios but FALSE
  for the cost column as presented (1.63x is not computable on the shared 52;
  the shared-52 cost ratio is 1.49x). Carried to Step 3 as finding F1.
- Tariff check: $0.042/1M input, output free confirmed present in
  `phase1/followup-04-jev-direct/README.md` (TypeSafe docs fetched 2026-09-26,
  one day before the Phase 2 run; that README itself warns both tariffs are
  promotional and tier-dependent). Output tokens are ~20/cell/run (raw 1140 vs
  struct 1040 totals) — charging them would not move any ratio materially.
  The shared-52 cost ratio (1.49x) is tariff-invariant; only the absolute
  dollar column depends on the tariff. Findings §9.8 discloses this.

### 2.10 Repeat-run discovery (bears on findings §9 limitation 9)

`jev_unanswerable_obs.ndjson` is NOT just 40 extra cells: it contains all 268
case_ids with identical `request_sha256`s, but 0/218 scored cells share the
main run's latency — i.e. the observation run RE-SENT all 258 sendable cells.
Response-level agreement run1-vs-run2 on the 218 scored cells: 215/218 same
label (3 flips: `json_encoder.param_rebound.001`/raw,
`json_encoder.param_rebound.002`/raw_ic,
`configparser.nesting_conjunction.001`/raw_ic), 95/218 byte-identical
responses. Run-2 accuracies: raw 0.7895 (45/57) vs 0.8070; raw_ic 0.7368
identical; struct 0.8846 identical; struct_ic 0.9038 identical.
`results/jev/scored.ndjson` parsed fields are byte-identical to run 1 only:
the scored results are unaffected. But findings §9.9 ("Single run per cell,
no repeats ... cell-level nondeterminism is unquantified") is factually
wrong: a full second run EXISTS, and cell-level stability is quantifiable at
98.6% label agreement. Carried to Step 3 as finding F3. (This repeat actually
strengthens confidence in the headline accuracies; the fault is the
limitation text, not the data.)

### 2.11 Request integrity (noul coercion check) — CLEAN

One question per request in all 218 sent cells; state is a single string whose
UTF-8 byte length equals `representation.state_bytes` (0 mismatches); 218
unique `request_sha256`s; single model/endpoint
(`jev-1.13.0`/`jev_direct`/`https://api.typesafe.ai/v1/systemone`); single
schema `jevp2-result-1.0`. No concatenation across scenarios, no silent
coercion surface. `credential_source` on all rows is the label
`secrets/typesafe.env#TYPESAFE_API_KEY`, not a value.

### Step 2 summary

Every number in findings §§0,1,3,4,6,7 re-derives exactly (all
differences are display rounding). Three findings against the document, none
touching the scored results: F1 (cost-ratio denominator mixing, §2.9), F2
(unused_import "under both" sentence, §2.3), F3 (false "no repeats"
limitation, §2.10). HOW CERTAIN: proven (mechanical re-derivation from raw
rows; scripts used stdlib only). WHAT-NOT-TESTED in Step 2: per-case
classification shapes taken from frozen cases as given (not re-audited);
`render_struct` full-corpus byte output not re-hashed (6-function spot check
is Step 1); power calculations behind §11.1 not re-derived.

---

## Close-out — second verifier, independent adjudication (appended 2026-09-28)

Why this section exists: this file carries work from more than one verifier
family (Step 2 at lines 214 and 717, Step 3/Step 4/verdict at 518-577, my Step
2 at 355 and my Step 3 at 578). This section does NOT re-argue what is settled.
It records (a) my Step 4 checks, all run independently 2026-09-28; (b) my
adjudication of the three novel findings raised by the concurrent variant
(F1/F2/F3), each re-derived by me rather than trusted; (c) my verdict.

### My Step 4 checks (independent, read-only except the designed reproduce run)

- Evidence files byte-identical to `ef4dc698`: `git diff ef4dc698 --stat` over
  `corpus/`, `frozen/` returned EMPTY; the four committed data artefacts
  (`jev_raw.ndjson`, `jev_unanswerable_obs.ndjson`, `jev/metrics.json`,
  `jev/scored.ndjson`) likewise unmodified. Post-measurement additions only
  (`harness/crosscheck_stats.py`, `mimo-mini-check.md`, `verify-*.jsonl/.err`,
  `autoretry.log`, this file) — additive, none in the evidence chain.
- Manifest digests: 10/12 match on disk (corpus ×6, frozen ×2, four of six
  harness files). `score.py` (02fad774→412fec14) and `run_jev.py`
  (5364858e→888aa3b8) differ because both were fixed between freeze
  (`1dd546b1`) and measurement (`ef4dc698`) — the §10-disclosed scorer fix
  plus the observation-only send. Wart in manifest wording, not a measurement
  failure; the fix direction keeps converted cases visible.
- `bash reproduce.sh` (Tier 1, offline, run by me): cases digest OK,
  admissibility digest OK, metrics re-score byte-identical —
  `REPRODUCTION OK (tier 1)`. Tier 2 skipped (no credential).
- Credentials: only the NAME `TYPESAFE_API_KEY` and the label
  `secrets/typesafe.env#TYPESAFE_API_KEY` (268/268 rows) occur in `phase2/`;
  zero key-shaped values, zero `authorization`/`bearer` occurrences. Clean.
- Request integrity: 268/268 requests carry exactly one question (key `q`,
  type `noul`); all 67 `raw_ic` states startswith their `raw` state and all 67
  `struct_ic` states startswith their `struct` state (distractor appended, no
  two-scenario concatenation).

### Adjudication of F1/F2/F3 (each re-derived by me)

- **F1 (cost-ratio denominator mixing) — CONFIRMED, and I adopt it as my
  sharpest qualification.** My paired-set derivation: raw mean 7941.7 vs
  struct mean 5334.4 input tokens → ratio 1.4888 → **1.49x**, not the
  headlined 1.63x (totals over 57 vs 52 cells). Cost is linear in input
  tokens, so paired cost ratio == paired token ratio necessarily. Direction
  exact, magnitude slightly overstated as framed; one-sentence fix (report
  paired 1.49x alongside). HOW CERTAIN: proven.
- **F2 (`unused_import` "under both" prose) — CONFIRMED, a genuine (minor)
  doc error I failed to catch.** My own §2.3 table gives struct_ic 4/5 = 0.8,
  which contradicts the §5.2 sentence "Raw 0.8, struct 0.6 under both clean
  and distractor conditions". The §4 TABLE row (0.8/0.6/0.8/0.8) is correct;
  the PROSE sentence is wrong. Touches no number in any table; a reader
  trusting only the prose would misstate struct_ic. I record this as a miss
  in my Step 3 §3.5, which quoted the sentence without checking struct_ic.
  HOW CERTAIN: proven (my Step 2 table vs the sentence).
- **F3 ("no repeats" limitation false) — CONFIRMED, the most load-bearing of
  the three.** My derivation: 218 cells have `parsed` in BOTH raw and obs
  files; label agreement 215/218 = **98.6%** (3 flips:
  json_encoder.param_rebound.001/raw,
  json_encoder.param_rebound.002/raw_ic,
  configparser.nesting_conjunction.001/raw_ic), while noul values are
  identical in only 95/218 — so the obs file is a genuine RE-RUN with
  endpoint nondeterminism, not a copy. Doc §9 item 9 ("Single run per cell,
  no repeats ... cell-level nondeterminism is unquantified") is factually
  wrong: repeat stability IS quantifiable here at 98.6%, and the finding
  strengthens (not weakens) confidence in the headline accuracies. The fault
  is the limitation text, not the data. HOW CERTAIN: proven.
  WHAT-NOT-TESTED: which file is temporally "run 1" (immaterial to the point).

### My verdict

**PASS WITH FINDINGS.** Every load-bearing number in `findings/findings.md`
reproduced exactly under my independent re-derivation (my Step 2, lines
355-517: 9/9 groups confirmed, converging with the concurrent variant on all
numbers); the document's restrained readings are the right calls at this n
(my Step 3, lines 578-716). The findings that stand: F1 (paired cost 1.49x,
not headlined 1.63x), F2 (§5.2 prose misstates struct_ic), F3 (§9.9 "no
repeats" contradicted by the obs-file re-run at 98.6% agreement), plus two
documentation-grade notes (two stale MANIFEST rows; obs-file sourcing and
`_ic`-row `classification:null` worth one line each). None touches a scored
result; F3 actively strengthens the accuracy readings.

### Limitations of MY verification (what I could not check and why)

- No Tier-2 live re-run (no credential in this session); the committed raw
  rows are taken as the endpoint record.
- The "~300 cases" power claim behind §11.1 was not recomputed.
- The 88-functions/260-edges configparser scale figures were not recounted.
- F2/F3 were adjudicated from the committed files only; I did not audit how
  the obs-file re-run came to exist (run_jev `--send-unanswerable` history is
  orchestrator-side).
- This file now carries overlapping sections from concurrent verifiers; I
  verified mine are intact (Step 2 at 355, Step 3 at 578) and adjudicated the
  points of difference rather than rewriting them. A reader should treat the
  concurrent Step 2s as independent convergence (they agree on all numbers)
  and this close-out as the tie-break record for F1/F2/F3.
---
## Step 3 — adversarial judgement (this continuation; my Step 2 is the block above, not the earlier variants)

Provenance: lines 214-714 hold two Step 2 variants, a Step 3, a Step 4 and a
verdict from prior/concurrent runs plus the orchestrator blocker. I did not
write those and do not alter them. I argue each brief question below from MY
re-derivation (the Step 2 block immediately above), with WHY / WHAT /
HOW CERTAIN (guess | evidence-based | proven) / WHAT-NOT-TESTED. Where I
independently converge with the existing Step 3 I say so in one line; where I
dissent (F2, F3) I show my numbers.

### 3.1 Is "efficiency, not accuracy" the correct headline, or under-claiming?

Correct headline; refusing the accuracy claim is statistically forced, not
modesty. WHY: the best single comparison (raw_ic vs struct_ic, p=0.0654) is
above 0.05, and no multiplicity adjustment over four comparisons can help a
 headline: even the most generous aggregation — a two-sided sign test on
"structure at-or-above in all 4 comparisons" under the global null — gives
2*(1/2)^4 = 0.125 (my arithmetic), still above 0.05. Presenting +3.8pp as
"structure helps accuracy" would repeat exactly the Phase 1 lesson the
document cites (consistent direction on a small sample is not a finding).
WHAT: my §2.2 (all four exact p-values re-derived). HOW CERTAIN: proven.
WHAT-NOT-TESTED: whether larger n converts the direction (that is §11's job).

### 3.2 Is the "no lookup concentration" reading sound, or a non-result dressed as a finding?

The document calls it a non-result, and that is the right call. WHY: the
whole group comparison rests on 6 discordant cells split 1-vs-2 and 1-vs-2
(my §2.5); the "+4.0pp vs +3.7pp same size" is one net cell per group — moving
a single cell erases or doubles either effect. "Helps judgment", "helps
lookup" and "nothing happened" all predict these counts about equally well.
A dressed finding would claim the equal gains as positive evidence; the
document instead calls it "the strongest argument for a larger n".
Converges with the existing §3.2. HOW CERTAIN: evidence-based.
WHAT-NOT-TESTED: group-specific effects at larger n.

### 3.3 Is the robustness signal (raw 4-0 vs struct 1-2, p=0.125) sold too strongly?

No. WHY: the document labels it "suggestive sign pattern, NOT a supported
result", keeps p=0.125 visible in both §4 and the §8 verdict table, and flags
n=5 per type. The gap arithmetic (+3.8pp clean, +13.5pp distracted) follows
from the paired counts (my §2.2). The per-type mechanism exhibit
(nesting_conjunction raw 0.8->0.4 while struct holds 0.8) is exactly two cells
flipping: `json_encoder.nesting_conjunction.001` and
`textwrap.nesting_conjunction.001` (both in my §2.4 raw lost-list) — fragile,
and the document says the sample is too small to carry it. Converges with the
existing §3.3. HOW CERTAIN: evidence-based (cell-level flip inspection).
WHAT-NOT-TESTED: replication of those two flips.

### 3.4 Evidence-removal: correctly "structure HURTING", or a defensible scoping decision?

Correctly characterised as hurting *under the replacement pattern*, and the
scoping reframe fails. WHY: the adversarial reframe ("structure never
promised literals, so unanswerability is scope, not harm") dies on the
document's own terms — the hazard exists exactly when preprocessing is
deployed as a replacement, and then silent evidence-dropping is a correctness
hazard regardless of intent. The probe measured it (5/5 struct cells
inadmissible by the gate, my §2.3) rather than hypothesising it, and the
document volunteers the defence's best fact (raw itself only 0.40, so the
question is hard even with evidence). The prescription (pair structure with
its evidence, §11.3) follows. Converges with the existing §3.4.
HOW CERTAIN: evidence-based. WHAT-NOT-TESTED: whether a
literals-preserving structure keeps the efficiency win.

### 3.5 `unused_import` worse under structure (0.6 vs 0.8): cost or noise? — FLAG CORRECT, SENTENCE WRONG (F2)

The "flag for enlargement, not a claim" handling is right (the gap is one
cell, 3/5 vs 4/5), BUT findings §5.2 writes "Raw 0.8, struct 0.6 under both
clean and distractor conditions," and that sentence is factually wrong: struct
under distraction is 4/5 = 0.8 (my §2.3 table), recovering via
`configparser.unused_import.001` (in my §2.4 struct gain-list). So the
"compact representation made the composition harder" mechanism has a
counterexample in the same table: under distraction the effect disappears.
DISSENT from the existing §3.5, which endorses the handling without catching
the sentence. The correction is one sentence ("struct 0.6 clean, 0.8
distracted"); the flag itself stays a flag. WHY/WHAT: my §§2.3-2.4 counts.
HOW CERTAIN: proven for the numbers; guess for any mechanism attribution.
WHAT-NOT-TESTED: enlarged-n replication.

### 3.6 Cost model: tariff validity and the 1.63x computation (F1)

Tariff sourcing is defensible; the 1.63x is arithmetically exact but framed
against the wrong denominator. WHY: $0.042/1M input with free output is
confirmed in `phase1/followup-04-jev-direct/README.md` (TypeSafe docs fetched
2026-09-26, one day before the Phase 2 run; that README itself warns both
tariffs are promotional and tier-dependent). Treating it as valid across the
run window is defensible, findings §9.8 discloses the dependence, and output
tokens (~20/cell) could not move any ratio. Computation: 0.018973/0.011650 =
1.6286 -> 1.63x exact. BUT it is the ratio of condition totals over 57 vs 52
cells: 1.4888 (per-case token saving) x 57/52 (admissibility gap) = 1.6320
(my §2.9 decomposition). On the shared 52 — the only set the document's own
§1 calls interpretable — cost ratio = token ratio = 1.49x, necessarily, since
cost is linear in input tokens. So §2's "exact counts over the same 52
comparable cases" is FALSE for the cost column as headlined, and a reader
comparing "1.63x cheaper" with the paired +3.8pp accuracy gap mixes a totals
ratio with a paired gap. The tariff-proof headline number is 1.49x fewer
input tokens. Fix: report paired cost 1.49x alongside; nothing about the
efficiency conclusion changes. Converges with the existing §3.1 (same
decomposition). HOW CERTAIN: proven. WHAT-NOT-TESTED: live tariff re-fetch
(irrelevant to the shared-52 ratio, which is tariff-invariant).

### 3.7 Overstated / understated / beyond-sample / missing-limitations sweep

- Overstated: F1 (cost framing) and F2 (unused_import sentence) above, both
  small. Every accuracy-adjacent statement I checked carries its p-value or
  an explicit unresolved/non-result/suggestive label — the §8 verdict table
  rows match their section evidence.
- Understated, if anything: the §10 caught-bugs (scorer condition-relative
  split dropping all 25 converted cases; gate catching 10 wrong ground
  truths) are load-bearing honesty results given one paragraph each; they
  strengthen trust in the 218 scored cells.
- Beyond-sample: the §7 EDASES gate prescription ("needs an explicit
  derivability check") generalises from 10 unanswerable cases on one
  mechanism; acceptable as a flagged consequence (its one-mechanism
  inheritance is covered by §9.2 itself).
- Missing from §9: (a) F3 below — the big one; (b) the obs-file sourcing for
  §7 behaviour data (names the file; currently takes two-file comparison to
  discover); (c) endpoint non-frozenness for future live re-runs.
  HOW CERTAIN: evidence-based (text-vs-evidence comparison).

### 3.8 Are the limitations honest? — YES EXCEPT ITEM 9 (F3)

Items 1-8 check out against artefacts I inspected (single model/endpoint
`jev-1.13.0`/`jev_direct` in 268/268 rows per my §2.11; whole-module states;
5 vendored stdlib subject modules; single uuid distractor; tariff string;
template phrasing). Item 9 ("Single run per cell, no repeats ... so
cell-level nondeterminism is unquantified") is FALSE. WHY: the observation
file re-sent all 258 sendable cells (0/218 scored cells share the main run's
latency despite identical request_shas; my §2.10): label agreement 215/218
(98.6%; 3 flips named in §2.10), run-2 accuracies 0.7895/0.7368/0.8846/0.9038
vs run-1 0.8070/0.7368/0.8846/0.9038 — within one cell everywhere. DISSENT
from the existing §3.7 item 9 (which "confirmed" no-repeats by counting
duplicate pairs within one file — the repeat is ACROSS the two files). The
scored results are unaffected (scored.ndjson is byte-identical to run 1).
The fault is a false limitation that conceals stability evidence which
actually SUPPORTS the report. HOW CERTAIN: proven (cross-file measurement).
WHAT-NOT-TESTED: the cause of inter-run flips (endpoint nondeterminism;
untestable offline).

### 3.9 Is the smallest next experiment actually the smallest? — YES

Each prong answers a question this phase opened and nothing else: (1) ~300
cases keeps the pre-registered McNemar read with falsifiability stated
("if it does not survive, that is a real negative"); (2) one second mechanism
with the followup-05 transport control mandatory, answering generalisability;
(3) the literals design decision BEFORE scaling, else the scale-up measures a
representation already slated for redesign (cheapest-test-first ordering).
The NOT-list (no R3, no session replay, no architecture) refuses exactly the
unopened spends. Two additions from my findings: bank the existing run-2
stability (98.6% label agreement) instead of budgeting fresh repeat
measurement, and note the ~300 power curve is taken as stated (I did not
re-derive it either). Converges with the existing §3.8. HOW CERTAIN:
evidence-based (design-logic check). WHAT-NOT-TESTED: budget feasibility of
the second-mechanism route.

---

## Step 4 — integrity and reproduction (this continuation)

- **Harness/corpus/frozen vs commit ef4dc698:** `git status --porcelain` over
  `harness/`, `corpus/`, `frozen/` is CLEAN (no working-tree modifications);
  `git diff ef4dc698 --` over the same paths shows only two ADDED files
  (`harness/crosscheck_stats.py`, `harness/mimo-mini-check.md` — later
  committed additions; I did not use crosscheck_stats.py as a source of
  truth). I ran no git commit, push, or checkout.
- **Concurrent-harness caveat:** during this session `results/` was being
  mutated by the repo's own verification auto-retry process
  (`results/autoretry.log`, `results/verify-muse*.jsonl` modified;
  `results/verify-muse4.*` untracked). None of that is mine; I created and
  touched only `verification.md`, and my Step 2 used only the frozen
  measurement files (`jev_raw`, obs, `jev/metrics.json`, `scored.ndjson`,
  `frozen/`).
- **Frozen digests vs `frozen/MANIFEST.md`:** corpus 6/6 match; `frozen/
  cases.json` + `admissibility.json` match; harness 4/6 match (extract,
  gen_cases, represent, validate_cases). `harness/run_jev.py` and
  `harness/score.py` DIFFER from their manifest rows — post-freeze fixes
  disclosed in findings §10 (observation-only send; intrinsic case_group).
  The working tree matches ef4dc698/HEAD, so this predates me; it is a
  manifest-documentation wart (two stale rows), not a measurement integrity
  failure. Converges with the existing Step 4 archaeology.
- **Re-run:** `bash reproduce.sh` (offline tier) prints `REPRODUCTION OK
  (tier 1)`, exit 0 — cases.json digest OK, admissibility.json digest OK,
  metrics.json re-score byte-identical (sha256 2ce8ac4e…); the script removed
  `results/reproduce_check`; frozen/ untouched. Tier 2 skipped (no --live).
- **Credential scan of phase2/:** only NAME/label mentions
  (`harness/run_jev.py` env-file parser + `CRED_LABEL`;
  `reproduce.sh`; brief docs). `credential_source` is the label
  `secrets/typesafe.env#TYPESAFE_API_KEY` on all 268 rows — a pointer, not a
  value. No `TYPESAFE_API_KEY=` assignment anywhere (the single
  `startswith` line is parser code). One grep hit for a key-like pattern
  (`findings/verification-status.md:93`) is the substring "sk-c" in
  "task-completion" — false positive. NO CREDENTIAL VALUES in phase2/.
  Values live outside the repo (`~/.secrets/typesafe.env` present).
- **No silent `noul` coercion:** 1 question per request in all 218 sent cells;
  state is a single string whose UTF-8 byte length equals
  `representation.state_bytes` (0 mismatches); 218 unique request_shas;
  single model/endpoint/schema triple. Inadmissible cells were never sent in
  the scored run (all 40 `ground_truth is None` rows in `scored.ndjson` have
  `correct is None`).

---

## Verdict

**PASS WITH FINDINGS** — every reported number re-derives exactly from the raw evidence (extraction concurred on 6/6 pairs, all §§0/1/3/4/6/7 statistics matched to display precision, Tier-1 reproduction byte-identical), and the headline "efficiency, not accuracy" with its refused accuracy claims is the only reading the arithmetic permits; the single most important qualification is that the headlined "1.63× cheaper" cost ratio mixes denominators (57 vs 52 cells) while the paired-comparable figure per the document's own §1 rule is 1.49× — accompanied by a false "struct 0.6 under both conditions" sentence and a false "no repeats" limitation that conceals a supporting full second run at 98.6% label agreement.

---

## Limitations of this verification (this continuation)

- Step 1 on disk predates this continuation; I re-derived all six pairs
  independently (stdlib `ast` reasoning + `extract.load_module`, before
  reading any conclusion document) and concur — including a cosmetic erratum
  I leave untouched (duplicated max_nesting row in the §6 table).
- Lines 214-714 (two Step 2 variants, Step 3, Step 4, verdict) are
  prior/concurrent runs' work. I rely only on my own Step 2/3/4 above;
  convergences are noted, never used as evidence. (Triple agreement on every
  number is recorded as an observation, not a proof.)
- A concurrent auto-retry harness mutated `results/*.jsonl` during this
  session; my evidence uses only the frozen measurement files (and I
  re-verified hashes after each append).
- No Tier-2 live re-run; tariff not re-fetched live (shared-52 ratios are
  tariff-invariant); the ~300-case power curve not re-derived; per-case
  intrinsic classifications taken as given; `render_struct` not fully
  re-hashed beyond the six-pair spot check.
- One delegated file-append earlier in this session returned a success claim
  for a write that provably did not happen (mtime/HEAD-hash unchanged); since
  then every append is verified by content-hash match plus read-back before
  continuing. The current file hash is reported by the proxy below and was
  re-checked by the verifier.
---

## Addendum 2026-09-28 — post-verification edits to findings.md (outside verified scope)

After this continuation's Steps 2-4 were derived, the working tree gained
commits `fe7d5a6e` (records verification COMPLETE) and `11a7986d`, the latter
adding findings §12 "Errata" plus new harness/results scaffolding (`freeze.py`,
`FREEZE.json`, `results/jev_v2/`, `results/jev_v3/`, enlarged `score.py` with
an `AnalysisFailure` guard). This verification pins the PRE-§12 document; the
§12 text and any v2/v3 data are NOT verified here.

- §12 E1 actions my F1 (cost denominator mixing) with the same 1.4888 matched
  ratio I derived — convergence recorded.
- OPEN CHECK (not a finding against the verified version): §12 E1's matched-52
  per-case absolutes ($0.00034775 raw, $0.00023355 struct) do NOT reproduce
  from `results/jev_raw.ndjson`, from which I derive exactly $0.00033355 /
  $0.00022404 (raw shared-52 total 412966 tokens; struct 277388; ratio 1.4888
  both ways). The ratio matches; the absolutes differ ~4% on both sides, so
  this is not a rounding choice on my side. Either the §12 figures come from
  newer (v2/v3) data not named in §12, or they are an arithmetic slip. Whoever
  owns §12 should re-derive those two cells from a named source; the 1.4888
  headline needs no change either way.
- My verdict, F2, and F3 above are unaffected (they concern the verified
  version's §5.2 sentence, §9 item 9, and statistics all present pre-§12).
