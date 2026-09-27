# Independent reading vs extractor: `shlex.split`

Target: `corpus/shlex.py`, function `split` (lines 305–315).
Bounded task: one function only. Reading done from source first, extractor run after.

| field | my reading (from source) | extractor's view | agree? |
|---|---|---|---|
| params, in `def` order | `s`, `comments`, `posix` | `comments`, `posix`, `s` | set agrees; **order does not** — extractor emits `sorted(set(params))` (`harness/extract.py:195`), so def order is lost |
| names assigned in body | `lex` only | `lex` | yes |
| body contains `try` | no | `false` | yes |

## Source lines relied on

- **`corpus/shlex.py:305`** — `def split(s, comments=False, posix=True):` → params in def order `s`, `comments`, `posix`.
- **`corpus/shlex.py:307–310`** — `if s is None:` / `import warnings` / `warnings.warn(...)`. `warnings` is bound by an `import` statement, which is none of the listed assignment forms (`x = `, `x += `, `for x`, `with ... as x`, `except E as x`, `:=`), so it is not counted as an assigned name. `s`, `comments`, `posix` are only read here (and at 311/313), never rebound.
- **`corpus/shlex.py:311`** — `lex = shlex(s, posix=posix)` → the only plain name assignment: `lex`.
- **`corpus/shlex.py:312`** — `lex.whitespace_split = True` → attribute store on an existing object; binds no new name.
- **`corpus/shlex.py:314`** — `lex.commenters = ''` → attribute store; binds no new name.
- **`corpus/shlex.py:315`** — `return list(lex)` → end of body. No `try`/`except`/`finally` anywhere in 305–315, and no `for`, `with`, `except`, or `:=` binding any name.

## Verdict

The extractor agrees with my independent reading on the substance — assigned name `lex` and `has_try = false` match exactly, and the parameter name set `{s, comments, posix}` matches — with the single caveat that `params` is returned alphabetically sorted rather than in `def` order, so that field agrees as a set but not as an ordered list.
