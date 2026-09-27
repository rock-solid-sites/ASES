#!/usr/bin/env python3
"""Build the model-visible state for each (case, condition) pair.

Conditions:
  raw        the module source, verbatim
  struct     the extracted structure
  raw_ic     raw source + the vendored irrelevant module appended
  struct_ic  structure + the distractor's structure appended

The irrelevant-context conditions append REAL unrelated code, not filler
comments, so they perturb both representations in kind: the raw state gains
27 KB of source and the structure gains 49 distractor symbols and their call
edges. The distractor was chosen for ZERO symbol overlap with the five subject
modules, so no question can become ambiguous.

R3 (structure + minimal source) is deliberately NOT built yet. The design makes
it conditional on materially testing the hypothesis, and that decision is
deferred until the R1/R2 result is in hand, so it is not built speculatively.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import extract  # noqa: E402
import gen_cases as gc  # noqa: E402

_CACHE = {}


def facts_for(module):
    if module not in _CACHE:
        _CACHE[module] = extract.load_module(
            os.path.join(PHASE2, "corpus", module + ".py"), module)
    return _CACHE[module]


def distractor():
    if "distractor" not in _CACHE:
        _CACHE["distractor"] = extract.load_module(
            os.path.join(PHASE2, "corpus", "_distractor_uuid.py"), "uuid")
    return _CACHE["distractor"]


def build_state(case, condition):
    """Return (state_text, provenance_dict) for one case under one condition."""
    f = facts_for(case["module"])
    d = distractor()

    if condition == "raw":
        text, kind = f.source, "raw_source_verbatim"
    elif condition == "struct":
        text, kind = f.render_struct(), "deterministic_structure"
    elif condition == "raw_ic":
        text = (f.source + "\n\n# ===== IRRELEVANT CONTEXT (distractor, "
                "not the subject of any question) =====\n" + d.source)
        kind = "raw_source_plus_distractor"
    elif condition == "struct_ic":
        text = (f.render_struct()
                + "\n# ===== IRRELEVANT CONTEXT (distractor) =====\n"
                + d.render_struct())
        kind = "structure_plus_distractor_structure"
    else:
        raise ValueError(f"unknown condition {condition!r}")

    prov = {
        "condition": condition,
        "kind": kind,
        "state_bytes": len(text.encode("utf-8")),
        "module": case["module"],
        "module_sha256": extract.sha256_text(f.source),
        "struct_sha256": extract.sha256_text(f.render_struct()),
        "distractor_sha256": (extract.sha256_text(d.source)
                              if condition.endswith("_ic") else None),
        "extractor": "phase2/harness/extract.py (stdlib ast + symtable)",
    }
    return text, prov


CONDITIONS = ["raw", "struct", "raw_ic", "struct_ic"]


def all_pairs(cases):
    for c in cases:
        for cond in CONDITIONS:
            yield c, cond
