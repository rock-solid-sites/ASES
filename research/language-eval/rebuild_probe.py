#!/usr/bin/env python3
"""Apply type-explicit, semantics-preserving edits to the REAL decision paths.

Runs only in a disposable CI checkout, after compiling/benchmarking unedited
sources. Every edit is checked against its expected exact source text.
Purpose: measure genuinely invalidated compilation, not no-op rebuilds.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

replacements = [
    (
        ROOT / "rust/src/main.rs",
        "current_usage.saturating_sub(c.included).max(0)",
        "current_usage.saturating_sub(c.included).max(0i64)",
    ),
    (
        ROOT / "haskell/Main.hs",
        "then max 0 (currentUsage - included c)",
        "then max (0 :: Integer) (currentUsage - included c)",
    ),
]

for path, old, new in replacements:
    source = path.read_text()
    if source.count(old) != 1:
        raise AssertionError(f"{path}: expected one target, found {source.count(old)}")
    if new in source:
        raise AssertionError(f"{path}: edit already applied")
    path.write_text(source.replace(old, new, 1))
    print(f"source-edited: {path.relative_to(ROOT)}: {old} -> {new}")
