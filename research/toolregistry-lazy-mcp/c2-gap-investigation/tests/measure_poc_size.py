#!/usr/bin/env python
"""Measure the PoC size of intercept_poc.py with a stated, reproducible rule.

Stated rule (as quoted in report.md §5.3): count lines that are
non-blank / non-comment / non-docstring, after removing the shebang line.

The count is tokenize-based so that string literals, nested strings and
multi-line docstrings are classified by the tokenizer rather than by
line-content heuristics:

* ``shebang``: physical line 1 when it starts with ``#!`` (always excluded).
* ``blank``:   lines whose stripped content is empty.
* ``comment``: physical lines that are wholly inside a COMMENT token
  (including single-line comments; the shebang line itself is classified
  separately and always excluded).
* ``docstring``: physical lines that are wholly inside a STRING token that
  opens a module/class/function docstring (the first STRING token in a
  suite, detected by checking the token's preceding non-whitespace token).
* ``code``: everything else — the strict code line count.

The mechanism-proper figure excludes the module's import lines and the
SCHEMA_VALIDATION_MARKER constant assignment from the strict code count.

Output: writes ``logs/measure-poc-size.log`` (in the same HARNESS-style
line format used by the phase logs) and prints a compact summary to stdout.

Run:  /tmp/toolregistry-venv/bin/python tests/measure_poc_size.py
"""

from __future__ import annotations

import io
import sys
import tokenize
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent.parent
TARGET = HERE / "intercept_poc.py"
LOG_FILE = HERE / "logs" / "measure-poc-size.log"


def hlog(msg: str) -> None:
    print(f"HARNESS|{msg}", flush=True)


def classify_lines(src: str) -> dict[int, str]:
    """Return {1-based line_no: kind} for each physical line of src.

    kind is one of: shebang, blank, comment, docstring, code.
    """
    kinds: dict[int, str] = {}
    lines = src.splitlines()
    total = len(lines)
    for idx in range(1, total + 1):
        kinds[idx] = "blank" if not lines[idx - 1].strip() else "code"

    # Shebang: line 1, only if it starts with #!
    if lines and lines[0].startswith("#!"):
        kinds[1] = "shebang"

    comment_lines: set[int] = set()
    docstring_lines: set[int] = set()

    # Walk tokens.  To decide docstring-ness we need the previous
    # non-whitespace token (the first STRING token of a suite follows
    # NEWLINE/INDENT or the module start).
    prev_tok: Any = None
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        ttype, _tstr, (srow, _scol), (_erow, _ecol), _line = tok
        if ttype == tokenize.COMMENT:
            # Single-line comment token always occupies exactly one row;
            # mark it comment (shebang was already classified).
            comment_lines.add(srow)
        elif ttype == tokenize.STRING:
            # A STRING token that is the first token of a suite (after
            # NEWLINE/INDENT or at module start) is a docstring.
            if prev_tok is None or prev_tok.type in (
                tokenize.NEWLINE,
                tokenize.NL,
                tokenize.INDENT,
            ):
                for ln in range(srow, _erow + 1):
                    docstring_lines.add(ln)
        prev_tok = tok

    for idx in range(1, total + 1):
        if kinds[idx] == "shebang":
            continue
        if idx in docstring_lines:
            kinds[idx] = "docstring"
        elif idx in comment_lines:
            kinds[idx] = "comment"
        elif kinds[idx] == "code" and not lines[idx - 1].strip():
            kinds[idx] = "blank"
    return kinds


def count_kind(kinds: dict[int, str], kind: str) -> int:
    return sum(1 for k in kinds.values() if k == kind)


def code_range(kinds: dict[int, str], start: int, end: int) -> int:
    """Count strict code lines in the inclusive physical line range."""
    return sum(1 for ln in range(start, end + 1) if kinds.get(ln) == "code")


def main() -> None:
    if not TARGET.exists():
        hlog(f"MEASURE_ERROR target_missing={TARGET}")
        sys.exit(1)
    src = TARGET.read_text(encoding="utf-8")
    kinds = classify_lines(src)

    total = len(src.splitlines())
    strict_code = count_kind(kinds, "code")
    blanks = count_kind(kinds, "blank")
    comments = count_kind(kinds, "comment")
    docstrings = count_kind(kinds, "docstring")
    shebang = count_kind(kinds, "shebang")

    # Mechanism-proper: strict code minus the module's import lines and the
    # SCHEMA_VALIDATION_MARKER constant assignment.
    imports = code_range(kinds, 44, 51)  # `from __future__` + stdlib + 3 toolregistry imports
    constant = code_range(kinds, 55, 55)  # SCHEMA_VALIDATION_MARKER
    mechanism_proper = strict_code - imports - constant

    # Per-component counts (same strict-code rule).
    classifier = code_range(kinds, 58, 62)          # _is_schema_validation_error
    class_body = code_range(kinds, 65, 103)         # SchemaAwareConnectionManager
    override = code_range(kinds, 79, 103)           # _call_persistent override
    register_async = code_range(kinds, 106, 133)    # _register_async
    register_sync = code_range(kinds, 136, 147)     # register_with_connection

    sum_components = classifier + class_body + register_async + register_sync

    lines = [
        f"MEASURE file={TARGET.name} rule=non-blank/non-comment/non-docstring post-shebang",
        f"MEASURE total={total} shebang={shebang} blank={blanks} comment={comments} "
        f"docstring={docstrings} strict_code={strict_code}",
        f"MEASURE mechanism_proper={mechanism_proper} imports={imports} constant={constant}",
        f"MEASURE component=_is_schema_validation_error lines={classifier}",
        f"MEASURE component=SchemaAwareConnectionManager_class_body lines={class_body}",
        f"MEASURE component=_call_persistent_override lines={override}",
        f"MEASURE component=_register_async lines={register_async}",
        f"MEASURE component=register_with_connection lines={register_sync}",
        f"MEASURE sum_components={sum_components} matches_mechanism_proper={sum_components == mechanism_proper}",
        f"MEASURE table_check=total={total} strict_code={strict_code} mechanism_proper={mechanism_proper}",
    ]
    LOG_FILE.parent.mkdir(exist_ok=True)
    LOG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for ln in lines:
        hlog(ln)
    hlog(f"MEASURE_DONE log={LOG_FILE.name}")

    ok = (
        total == 147
        and strict_code == 64
        and mechanism_proper == 57
        and classifier == 5
        and class_body == 20
        and override == 16
        and register_async == 22
        and register_sync == 10
        and sum_components == mechanism_proper
    )
    hlog(f"MEASURE_RESULT pass={ok}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
