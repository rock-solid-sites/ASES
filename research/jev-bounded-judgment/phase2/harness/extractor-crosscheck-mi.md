# Extractor cross-check (independent reading vs `harness/extract.py`) — six pairs

Method: I read the six function bodies in `corpus/*.py` first and formed my own
readings of params / assigned names / nesting / try / raise / calls per the
brief's rules. Only then did I run `extract.load_module` to obtain the
extractor's view, and read `extract.py` to adjudicate disagreements. I did not
edit anything except this file.

Line references below are to the corpus files (and to `harness/extract.py` where
implementation explains an output).

---

## 1. `(shlex.py, shlex.__init__)` — corpus/shlex.py:21–66

| field | my independent reading | extractor's output | agree? |
|---|---|---|---|
| params (as written, in order) | `self, instream, infile, posix, punctuation_chars` (line 21–22) | `["infile","instream","posix","punctuation_chars","self"]` | set: yes — **order: NO** |
| assigned names | `instream` (24), `punctuation_chars` (55, 57), `t` (65). The 26 `self.… = …` statements (26–66) target attributes, not names — `self` is `Load` ctx in the AST — so not counted | `["instream","punctuation_chars","t"]` | yes |
| max nesting | 2 — `if not punctuation_chars:` (54) opens 1, `elif punctuation_chars is True:` (56) opens the second | `2` | yes |
| has_try | no `try` anywhere in body | `false` | yes |
| has_raise | no `raise` in body | `false` | yes |
| direct calls (nested-def scope excluded; none present) | `isinstance` (23), `StringIO` (24), `deque` (48, 52, 61), `dict.fromkeys` (65), `self.wordchars.maketrans` (65), `self.wordchars.translate` (66) — 6 distinct | identical 6 edges: `StringIO, deque, dict.fromkeys, isinstance, self.wordchars.maketrans, self.wordchars.translate` | yes |

## 2. `(shlex.py, split)` — corpus/shlex.py:305–315

| field | my independent reading | extractor's output | agree? |
|---|---|---|---|
| params (as written, in order) | `s, comments, posix` (line 305) | `["comments","posix","s"]` | set: yes — **order: NO** |
| assigned names | `lex` (311). `lex.whitespace_split = True` (312) and `lex.commenters = ''` (314) are attribute stores, not name bindings | `["lex"]` | yes |
| max nesting | 1 — `if s is None:` (307), `if not comments:` (313); no elif/nesting below | `1` | yes |
| has_try | no | `false` | yes |
| has_raise | no | `false` | yes |
| direct calls | `shlex` (311), `warnings.warn` (309), `list` (315) | identical: `list, shlex, warnings.warn` | yes |

## 3. `(json_encoder.py, JSONEncoder.iterencode)` — corpus/json_encoder.py:204–257

| field | my independent reading | extractor's output | agree? |
|---|---|---|---|
| params (as written, in order) | `self, o, _one_shot` (line 204) | `["_one_shot","o","self"]` | set: yes — **order: NO** |
| assigned names | `markers` (215, 217), `_encoder` (219, 221), `_iterencode` (248, 253); plus `text` (230, 232, 234) which is assigned inside the nested `def floatstr` (223–243) — the brief says "anywhere inside the function body", with no scope carve-out for assignments, so it counts. (`floatstr` itself is bound by `def`, which is not in the brief's enumerated assignment forms → not counted. Nested-def params `o/allow_nan/_repr/_inf/_neginf` are parameter bindings, not assignments.) | `["_encoder","_iterencode","markers","text"]` | yes |
| max nesting | 4 — `def floatstr` (223) opens 1; `if o != o:` (229) → 2; `elif o == _inf` (231) → 3; `elif o == _neginf` (233) → 4. Depth without entering the nested def would be 1, but the brief lists "nested def" as opening a level | `4` | yes |
| has_try | no `try` (including inside `floatstr`) | `false` | yes |
| has_raise | yes — `raise ValueError(...)` at line 239, inside nested `def floatstr`; the brief's item 4 has no nested-def carve-out (only item 5's call rule does) | `true` | yes |
| direct calls (item 5: exclude nested-def calls) | `c_make_encoder` (248), `_make_iterencode` (253), `_iterencode` (257) | identical: `c_make_encoder, _make_iterencode, _iterencode` (correctly excludes `repr`, `ValueError`, `_repr` from `floatstr`'s body) | yes |

## 4. `(textwrap.py, TextWrapper._wrap_chunks)` — corpus/textwrap.py:241–342

| field | my independent reading | extractor's output | agree? |
|---|---|---|---|
| params (as written, in order) | `self, chunks` (line 241) | `["chunks","self"]` | set: yes — **order: NO** |
| assigned names | `lines` (254), `indent` (259, 261, 278, 280), `cur_line` (273), `cur_len` (274, 296 `+=`, 306, 310 `-=`, 330 `-=`), `width` (283), `l` (291), `prev_line` (334) — 7 distinct. `lines[-1] = …` (337) stores into an element, not a name (AST: base `lines` is `Load`); `del chunks[-1]` (288), `del cur_line[-1]` (311, 331) are not assignments | `["cur_len","cur_line","indent","l","lines","prev_line","width"]` | yes |
| max nesting | 6 — `while chunks:` (269) →1; `if cur_line:` (313) →2; inner `if (self.max_lines is None or…)` (314) →3; its `else:` holds `while cur_line:` (324) →4; that while's `else:` holds `if lines:` (333) →5; `if (len(prev_line)…)` (335) →6; deepest statement `lines[-1] = prev_line + self.placeholder` (337) | `6` | yes |
| has_try | no | `false` | yes |
| has_raise | yes — `raise ValueError(…)` at 256 and 263 | `true` | yes |
| direct calls | 14 distinct as written: `ValueError` (256, 263), `len` (262, 291, 304, 306, 310, 315, 318, 326, 330, 335), `self.placeholder.lstrip` (262, 339), `chunks.reverse` (267), `cur_line.append` (295, 327), `chunks.pop` (295), `self._handle_long_word` (305), `sum`/`map` (306), `cur_line[-1].strip` (309, 325), `chunks[0].strip` (319), `lines.append` (322, 328, 339), `''.join` (322, 328), `lines[-1].rstrip` (334) | 13 edges: `ValueError, chunks.pop, chunks.reverse, cur_line.append, join, len, lines.append, map, rstrip, self._handle_long_word, self.placeholder.lstrip, strip, sum` | **partial — 10/14 identical; 4 names renamed** (see D2) |

## 5. `(dataclasses.py, dataclass)` — corpus/dataclasses.py:1156–1184

| field | my independent reading | extractor's output | agree? |
|---|---|---|---|
| params (as written, in order) | `cls, init, repr, eq, order, unsafe_hash, frozen, match_args, kw_only, slots` (1156–1158). Note `cls` is positional-only and the rest keyword-only (`/`, `*` in the signature) | `["cls","eq","frozen","init","kw_only","match_args","order","repr","slots","unsafe_hash"]` — sorted; `/` and `*` markers dropped | set: yes — **order: NO** (markers also lost) |
| assigned names | none by the brief's forms. `wrap` (1174) is bound by a nested `def`, which the brief's enumerated forms (`x = …`, `+=`, `for`, `with`, `except`, walrus) do not include | `[]` | yes |
| max nesting | 1 — `def wrap` (1174) opens 1; `if cls is None:` (1179) opens 1. `wrap`'s body has no control flow | `1` | yes |
| has_try | no | `false` | yes |
| has_raise | no | `false` | yes |
| direct calls (nested-def excluded) | `wrap` (1184). `_process_class` (1175) is inside nested `def wrap` → excluded per item 5 | `["wrap"]` (correctly excludes `_process_class`) | yes |

## 6. `(configparser.py, RawConfigParser._read)` — corpus/configparser.py:998–1118

| field | my independent reading | extractor's output | agree? |
|---|---|---|---|
| params (as written, in order) | `self, fp, fpname` (line 998) | `["fp","fpname","self"]` | set: yes — **order: NO** |
| assigned names | 20: `elements_added` (1015), `cursect` (1016), `sectname` (1017), `optname` (1018), `lineno` (1019, 1022 for-target), `indent_level` (1020, 1055, 1065), `e` (1021, 1094, 1114), `line` (1022 for-target), `comment_start` (1023, 1034, 1039, 1042), `inline_prefixes` (1025, 1035), `p` (1025 comprehension `for p in …`), `next_prefixes` (1027), `prefix` (1028, 1037 for-targets), `index` (1028 for-target, 1029), `value` (1043), `first_nonspace` (1058), `cur_indent_level` (1059), `mo` (1067, 1090), `vi` (1092), `optval` (1092, 1104). Subscript stores `next_prefixes[prefix]=` (1032), `cursect[optname]=` (1105, 1108) bind no new names | same 20 (sorted; includes `p`) | yes |
| max nesting | 6 — `for lineno, line …` (1022) →1; `if (cursect is not None …)` (1060) →2; its `else:` → `if mo:` (1068) →3; `elif cursect is None:` (1086) →4 (elif opens a level); its `else:` → `if mo:` (1091) →5; `if not optname:` (1093) (also 1096, 1103) →6 | `6` | yes |
| has_try | no `try` statement in the body (raises are emitted bare, errors collected in `e`) | `false` | yes |
| has_raise | yes — `raise DuplicateSectionError(…)` (1072), `raise MissingSectionHeaderError(…)` (1087), `raise DuplicateOptionError(…)` (1098), `raise e` (1118) | `true` | yes |
| direct calls | 26 as written: `set` (1015), `enumerate` (1022), `inline_prefixes.items` (1028), `line.find` (1029), `line[index-1].isspace` (1033), `min` (1034), `line.strip` (1038, inner), `line.strip().startswith` (1038, outer), `line[:comment_start].strip` (1043), `cursect[optname].append` (1052, 1062), `self.NONSPACECRE.search` (1058), `first_nonspace.start` (1059), `self.SECTCRE.match` (1067), `mo.group` (1069, 1092), `DuplicateSectionError` (1072), `elements_added.add` (1075, 1082, 1100), `self._dict` (1079), `SectionProxy` (1081), `MissingSectionHeaderError` (1087), `self._optcre.match` (1090), `self._handle_error` (1094, 1114), `self.optionxform` (1095), `optname.rstrip` (1095), `optval.strip` (1104), `self._join_multiline_values` (1115), `DuplicateOptionError` (1098) | 26 edges; 22 byte-identical, 4 renamed: `isspace` ← `line[index-1].isspace`, `strip` ← `line[:comment_start].strip`, `append` ← `cursect[optname].append`, `line.strip.startswith` ← `line.strip().startswith` | **partial — 22/26 identical; 4 renamed** (see D2) |

---

# Findings

## Disagreements

### D1. Parameter ORDER (and posonly/kwonly markers) is not preserved — all six functions

The extractor's `params` is `sorted(set(params))`
(`extract.py:161–168` collect in def order, `extract.py:195` sorts and
dedupes). Every one of the six functions comes out in a different order than
the `def` writes:

| function | def order (source) | extractor order |
|---|---|---|
| `shlex.__init__` (shlex.py:21–22) | `self, instream, infile, posix, punctuation_chars` | `infile, instream, posix, punctuation_chars, self` |
| `split` (shlex.py:305) | `s, comments, posix` | `comments, posix, s` |
| `JSONEncoder.iterencode` (json_encoder.py:204) | `self, o, _one_shot` | `_one_shot, o, self` |
| `TextWrapper._wrap_chunks` (textwrap.py:241) | `self, chunks` | `chunks, self` |
| `dataclass` (dataclasses.py:1156–1158) | `cls, init, repr, eq, order, unsafe_hash, frozen, match_args, kw_only, slots` | `cls, eq, frozen, init, kw_only, match_args, order, repr, slots, unsafe_hash` |
| `RawConfigParser._read` (configparser.py:998) | `self, fp, fpname` | `fp, fpname, self` |

Which reading is correct: **mine, as the fact "parameter names, in order, as
written in the def"** — the source order is the fact; the extractor's list is
correct only as an unordered set. The sort is deliberate (the module header
claims determinism, `extract.py:17–19`), so this is not an accidental bug — but
the rendered `params=[…]` (`extract.py:420`) looks like an ordered list and is
not one. Two concrete losses beyond order:

* "First parameter of `split`" is `s` in the source; the extractor's list
  starts with `comments`.
* `def dataclass(cls=None, /, *, init=True, …)` — the `/` and `*` markers are
  discarded (`extract.py:162–168` keeps only `*vararg`/`**kwarg` prefixes), so
  "cls is positional-only, the rest are keyword-only" is not recoverable from
  `params`.

Severity: the name SET is preserved 6/6; positional/kind ORDER is preserved 0/6.
Any bounded question that depends on argument position or on posonly/kwonly
kind cannot be answered from this field. (Whether `gen_cases.py` asks such
questions is outside this cross-check's scope.)

### D2. Call-edge callee names lose the receiver when it is not a plain Name/Attribute chain — 8 call sites in 2 functions

`_dotted` (`extract.py:139–148`) returns the bare attribute when the receiver
is a Subscript or Constant (`return f"{base}.{node.attr}" if base else
node.attr`), and flattens an inner Call receiver into the dotted path
(`ast.Call → _dotted(node.func)`). Consequences, all quoted from source:

| source line | callee as written | extractor edge | note |
|---|---|---|---|
| textwrap.py:322, 328 | `''.join(cur_line)` → `''.join` | `join` | receiver (empty-string literal) dropped |
| textwrap.py:309, 325 | `cur_line[-1].strip()` → `cur_line[-1].strip` | `strip` | receiver dropped |
| textwrap.py:319 | `chunks[0].strip()` → `chunks[0].strip` | `strip` | collapses with the two above into ONE edge (dedup at `extract.py:254–256`) |
| textwrap.py:334 | `lines[-1].rstrip()` → `lines[-1].rstrip` | `rstrip` | receiver dropped |
| configparser.py:1033 | `line[index-1].isspace()` → `line[index-1].isspace` | `isspace` | receiver dropped |
| configparser.py:1043 | `line[:comment_start].strip()` → `line[:comment_start].strip` | `strip` | receiver dropped |
| configparser.py:1052, 1062 | `cursect[optname].append(…)` → `cursect[optname].append` | `append` | receiver dropped |
| configparser.py:1038 | `line.strip().startswith(prefix)` → `line.strip().startswith` | `line.strip.startswith` | notation flattening only (inner call correctly also emitted as `line.strip`) |

Which reading is correct: **mine under the brief's rule "report the dotted form
as written."** The extractor's edges are not false about *whether* a call
exists — every call site I found has a corresponding edge and every edge maps
to a real call site (verified: `_read` 26/26 sites, `_wrap_chunks` 14 sites →
13 names because the two `.strip` receivers collapse) — but the callee *name*
is receiver-free for those 8 sites. Concrete harm: `_read -> append` names a
callee that appears nowhere verbatim in the source (`configparser.py:1052` is
`cursect[optname].append`), so a bounded question phrased with the as-written
form will not match the edge (false negative), while a question phrased bare
(`append`) matches a token the source never writes. Within these two functions
the collapse caused no cross-receiver collision of *different* methods (each
bare name maps to exactly one method), so the damage is ambiguity/loss, not a
wrong fact about which method executes.

Functions 1, 2, 3, 5 (`shlex.__init__`, `split`, `iterencode`, `dataclass`)
have 100 % identical call sets — all receivers there are Names/Attributes.

## Cases where I was unsure, and self-corrections

* **My first reading of `_wrap_chunks` nesting was wrong (5); the extractor's 6
  is right.** I initially attached line 323's `else:` to `if cur_line:`
  (line 313). Checking exact indentation: line 313 has 12 spaces, line 314's
  inner `if` has 16, and line 323's `else:` has 16 — so the `else` belongs to
  the inner `if (self.max_lines is None or …)` (314), and `while cur_line:`
  (324, 20 spaces) sits inside that `else`. Corrected path:
  `While@269 → If@313 → If@314 → While@324 → If@333 → If@335` = depth 6, which
  matches the extractor (independently confirmed by instrumenting the same
  walk). No disagreement stands here.
* **elif counting convention (interpretive, not a disagreement).** The brief's
  "a new level is opened by … elif (the `if` only) / else (no new level)" is
  most naturally read as: an `elif` opens a level where it sits (inside the
  parent's orelse), `else` does not. That yields 2 / 4 / 6 for
  `shlex.__init__` / `iterencode` / `_read` — exactly what the extractor
  computes (`extract.py:30–34` includes `ast.If` as a branch node;
  `iter_child_nodes` gives the nested `elif`-If +1). A flat-chain reading
  (all branches equal) would give 1 / 2 / 5 instead, but that reading would
  make the brief's explicit "elif opens a level, else doesn't" clause
  meaningless. I therefore count both as agreeing; I flag it only so the
  convention is on record.
* **Nested-def scope in `iterencode` (interpretive, agreement).** `text`
  (assigned at 230–234), `has_raise=true` (raise at 239), and `max_nesting=4`
  (path through `def floatstr` at 223) all derive from inside a nested
  function. The brief's rules as written endorse including them: assignments
  are "anywhere inside the function body" with no carve-out, "nested def"
  explicitly opens a nesting level, and only item 5 (calls) explicitly
  excludes nested scopes — which both of us honoured (floatstr's `repr`,
  `ValueError`, `_repr` excluded from edges). A stricter scope-based reading
  would give `assigned={markers,_encoder,_iterencode}`, `has_raise=false`,
  `max_nesting=2` — I considered it and rejected it as contrary to the brief's
  wording. Agreement stands under the brief's literal rules.
* **`def`-bound names (`wrap`, `floatstr`).** The brief's enumerated assignment
  forms do not include `def name(...)`, so neither of us lists them as
  assigned. Note for readers: they ARE locals of their enclosing function in
  Python semantics; both readings are internally consistent with the brief,
  and they agree with each other, so no disagreement — just a boundary of what
  `assigned_locals` means.
* **Lambda bodies (latent, no effect here).** `extract.py:249` stops walking at
  `Lambda` for call edges, while the brief says a lambda's body is NOT
  excluded. I verified none of the six bodies contains a lambda (nor any
  `try`/`with`/`match` statement; the `_read` grep hits at 1067/1090 are
  `.match(…)` method calls and 1003 is prose in the docstring), so the two
  rules cannot diverge on these six. Not scored as a disagreement.
* **`del` statements and subscript stores.** The brief lists no `del` form and
  only `x = …`-style name targets; `del chunks[-1]` (288) and
  `lines[-1] = …` (337) therefore count as no new assigned name. The extractor
  agrees (AST: the base of a store-subscript and attribute-store is `Load` ctx,
  verified with `ast.dump` — so `self`/`lines` are not spuriously added).

## Overall verdict

**For these six functions the extractor faithfully preserves the structural
facts it claims, with two systematic gaps that must be treated as "fact not
preserved" wherever a question relies on them.**

* Preserved 6/6: parameter name sets; `assigned_locals`; `max_nesting`;
  `has_try`; `has_raise`; and the existence of every direct call site with
  nested-def calls correctly excluded (item 5) — the call sets are byte-identical
  for 4 of 6 functions.
* Gap 1 (D1): **parameter order and posonly/kwonly markers are discarded for
  all six** (`sorted(set(params))`). Order-sensitive questions
  (e.g. "first parameter of `split`", "is `cls` positional-only in
  `dataclass`") are unanswerable or wrong if read from `params` as if it were
  ordered.
* Gap 2 (D2): **callee names are lossy for subscript/constant receivers — 8
  call sites across `_wrap_chunks` and `_read`** (`''.join`→`join`,
  `cursect[optname].append`→`append`, etc.). Whether a call exists is
  preserved; the as-written callee string is not, so edge matching against
  as-written question phrasings will misalign at those sites.

Nothing in these six shows the extractor inventing a false structural fact:
every `has_try`/`has_raise`/`max_nesting`/assignment claim traces to a quoted
source line, and the one place I initially thought it over-counted
(`_wrap_chunks` = 6) turned out to be my own misreading of Python indentation,
which the extractor got right.
