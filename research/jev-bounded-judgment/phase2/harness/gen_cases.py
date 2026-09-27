#!/usr/bin/env python3
"""Phase 2 case generation. Ground truth is COMPUTED, never asserted.

Every case's answer is derived from the source AST by `extract.py`. No model
writes, suggests, confirms or ranks a case answer, and no model sees an answer
before committing to one. That structurally removes the Phase-1 self-preference
confound (findings.md L1 / ERRATA.md A4) rather than relying on policy.

Each case type ships a REQUIRED-EVIDENCE PREDICATE: a mechanical assertion
about what a representation must contain for the ground truth to be derivable
from it. The predicate is evaluated per condition, and a condition that fails
its predicate is UNANSWERABLE for that case -- never a model error.

Each case also carries a `classification`:
  lookup    the queried fact is a direct field value in that representation
  judgment  the fact must be composed or intersected from the representation
Results are reported split by classification, because a gain concentrated in
`lookup` cases is evidence that structure removed the need to judge, not that
structure improved judging.

Deterministic: no RNG, no clock, no host paths. Case ids are
`<module>.<type>.<nnn>` and selection is by sorted order.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import extract  # noqa: E402

SUBJECTS = ["shlex", "json_encoder", "textwrap", "dataclasses", "configparser"]
DISTRACTOR = "_distractor_uuid"


# ---------------------------------------------------------------- helpers
def bare(qualname):
    return qualname.split(".")[-1]


def pick_distinct(seq, n, offset=0):
    out, i = [], offset
    while len(out) < n and i < len(seq):
        out.append(seq[i])
        i += 1
    return out


def case_id(module, ctype, i):
    return f"{module}.{ctype}.{i:03d}"


# ------------------------------------------------------- required-evidence
# Each predicate: (facts, case) -> bool. True means the ground truth is
# derivable from the structure rendering. The RAW representation is the
# verbatim source, so its predicate is simply "the referenced entity is present
# in the source at all", which is why raw is checked separately.
# NOTE: all predicates read through `c["params"]`, matching the case schema.
def ev_direct_call(facts, c):
    p = c["params"]
    return (p["caller"] in {e[0] for e in facts.call_edges}
            or p["caller"] in facts.qualified_functions)


def ev_path2(facts, c):
    p = c["params"]
    callees = {b for _, b in facts.call_edges}
    # src and mid must both be inspectable module functions; dst need only be a
    # token present in the edge set, since the question asks whether the chain
    # reaches it, not whether it is itself defined here.
    return (p["src"] in facts.qualified_functions
            and p["mid"] in facts.qualified_functions
            and p["dst"] in callees)


def ev_param_rebound(facts, c):
    p = c["params"]
    f = facts.fn_fact(p["fn"])
    return bool(f) and p["param"] in f["params"]


def ev_unused_import(facts, c):
    p = c["params"]
    return p["mod"] in set(facts.import_keys())


def ev_nesting_conjunction(facts, c):
    p = c["params"]
    return (p["callee"] in {b for _, b in facts.call_edges}
            and p["target"] in facts.qualified_functions)


def ev_string_literal(facts, c):
    # Structure deliberately carries NO string literals, so a literal-presence
    # question is NOT derivable from it. This is the evidence-removal probe.
    return False


def ev_none(facts, c):
    return False


# ------------------------------------------------------------- generators
def gen_direct_call(facts, module):
    """LOOKUP under struct, JUDGMENT under raw. Both polarities."""
    cases, i = [], 0
    edges = sorted({(a, b) for a, b in facts.call_edges
                    if a in facts.qualified_functions})
    # TRUE cases: caller calls callee (bare-name callees only, so the token is
    # unambiguous in both representations).
    trues = [(a, b) for a, b in edges if "." not in b][:3]
    for caller, callee in trues:
        i += 1
        cases.append({
            "case_id": case_id(module, "direct_call", i),
            "type": "noul", "ctype": "direct_call",
            "question": (f"In this module, does `{caller}` directly call "
                         f"`{callee}`?"),
            "ground_truth": "yes",
            "gt_basis": f"call_edges contains [{caller}, {callee}]",
            "evidence_predicate": "ev_direct_call",
            "classification": {"struct": "lookup", "raw": "judgment"},
            "params": {"caller": caller, "callee": callee},
            "raw_evidence": (f"`{caller}` is a function defined in the source, "
                             f"so whether it calls `{callee}` is decidable by "
                             f"reading its body."),
        })
    # FALSE cases: the callee is a real module-level symbol that IS called by
    # some other function, but NOT by this caller. Pairs are enumerated as
    # (caller, callee) over real symbols and then FILTERED to those with no
    # edge -- enumerating existing edges here would label real edges "no".
    by_callee = {}
    for a, b in edges:
        if "." not in b:
            by_callee.setdefault(b, []).append(a)
    callers_all = sorted(facts.qualified_functions)
    falses = []
    for callee, other_callers in sorted(by_callee.items()):
        for caller in callers_all:
            if caller == callee or callee in caller:
                continue
            if (caller, callee) in edges:
                continue                      # edge exists -> truth is "yes"
            falses.append((caller, callee))
    for caller, callee in falses[:2]:
        i += 1
        cases.append({
            "case_id": case_id(module, "direct_call", i),
            "type": "noul", "ctype": "direct_call",
            "question": (f"In this module, does `{caller}` directly call "
                         f"`{callee}`?"),
            "ground_truth": "no",
            "gt_basis": (f"call_edges has no [{caller}, {callee}]; `{callee}` is "
                         f"called by {sorted(by_callee[callee])}, so its "
                         f"absence here is a real negative"),
            "evidence_predicate": "ev_direct_call",
            "classification": {"struct": "lookup", "raw": "judgment"},
            "params": {"caller": caller, "callee": callee},
            "raw_evidence": (f"`{caller}` is a function defined in the source, "
                             f"so its calls are decidable by reading its body."),
        })
    return cases


def gen_path2(facts, module):
    """JUDGMENT under both: requires composing the edge set."""
    cases, i = [], 0
    adj = {}
    for a, b in facts.call_edges:
        adj.setdefault(a, []).append(b)
    for src in sorted(facts.qualified_functions):
        if i >= 2:
            break
        for mid in adj.get(src, []):
            if i >= 2:
                break
            if mid == src or mid not in facts.qualified_functions:
                # the intermediate must itself be a function we can inspect
                continue
            for dst in adj.get(mid, []):
                if dst in (src, mid) or dst == mid:
                    continue
                i += 1
                cases.append({
                    "case_id": case_id(module, "call_path2", i),
                    "type": "noul", "ctype": "call_path2",
                    "question": (f"In this module, is there a function that "
                                 f"`{src}` calls, which in turn calls `{dst}`?"),
                    "ground_truth": "yes",
                    "gt_basis": f"edge [{src},{mid}] and edge [{mid},{dst}]",
                    "evidence_predicate": "ev_path2",
                    "classification": {"struct": "judgment", "raw": "judgment"},
                    "params": {"src": src, "dst": dst, "mid": mid},
                    "raw_evidence": (f"both `{src}` and `{dst}` are defined in "
                                     f"the source, so the chain is decidable."),
                })
                if i >= 2:
                    break
    return cases


def gen_param_rebound(facts, module):
    """JUDGMENT under struct: requires intersecting params with assigned_locals."""
    cases, i = [], 0
    for fn, f in sorted(facts.qualified_functions.items()):
        for p in f["params"]:
            if p.startswith("*"):
                continue
            truth = p in f["assigned_locals"]
            if i >= 2:
                return cases
            i += 1
            cases.append({
                "case_id": case_id(module, "param_rebound", i),
                "type": "noul", "ctype": "param_rebound",
                "question": (f"In `{fn}`, is the parameter `{p}` rebound by an "
                             f"assignment to `{p}` inside the function body?"),
                "ground_truth": "yes" if truth else "no",
                "gt_basis": (f"params contains {p}=True; "
                             f"assigned_locals contains {p}="
                             f"{truth}"),
                "evidence_predicate": "ev_param_rebound",
                "classification": {"struct": "judgment", "raw": "judgment"},
                "params": {"fn": fn, "param": p},
                "raw_evidence": f"`{fn}` is defined in the source with body visible.",
            })
    return cases


def gen_unused_import(facts, module):
    """JUDGMENT under struct: requires intersecting imports with names_loaded."""
    cases, i = [], 0
    unused = set(facts.unused_imports())
    cands = []
    for imp in facts.imports:
        if imp["names"] is None:
            cands.append((imp["module"], imp["module"] in unused))
        else:
            for nm in imp["names"]:
                if nm == "*":
                    continue
                key = f"{imp['module']}.{nm}"
                cands.append((key, key in unused))
    for key, truth in cands:
        if i >= 1:
            break
        i += 1
        cases.append({
            "case_id": case_id(module, "unused_import", i),
            "type": "noul", "ctype": "unused_import",
            "question": (f"Is `{key}` imported in this module but never "
                         f"referenced by name anywhere in the module's code?"),
            "ground_truth": "yes" if truth else "no",
            "gt_basis": f"unused_imports() contains {key} = {truth}",
            "evidence_predicate": "ev_unused_import",
            "classification": {"struct": "judgment", "raw": "judgment"},
            "params": {"mod": key},
            "raw_evidence": "the import statement and all name usages are in the source.",
        })
    return cases


def gen_nesting_conjunction(facts, module):
    """JUDGMENT under both: filter by nesting AND check an edge."""
    cases, i = [], 0
    deep = [f for f, v in sorted(facts.qualified_functions.items())
            if v["max_nesting"] >= 3]
    if not deep:
        return cases
    target = deep[0]
    adj = {}
    for a, b in facts.call_edges:
        adj.setdefault(a, []).append(b)
    callees = [c for c in adj.get(target, []) if "." not in c]
    if not callees:
        return cases
    callee = callees[0]
    thr = facts.fn_fact(target)["max_nesting"] - 1
    truth = facts.fn_fact(target)["max_nesting"] > thr
    cases.append({
        "case_id": case_id(module, "nesting_conjunction", 1),
        "type": "noul", "ctype": "nesting_conjunction",
        "question": (f"Does any function in this module have maximum "
                     f"control-flow nesting deeper than {thr} AND also call "
                     f"`{callee}`?"),
        "ground_truth": "yes" if truth else "no",
        "gt_basis": (f"`{target}` max_nesting="
                     f"{facts.fn_fact(target)['max_nesting']} > {thr} is "
                     f"{facts.fn_fact(target)['max_nesting'] > thr}; it calls "
                     f"{callee} = {facts.has_call_edge(target, callee)}"),
        "evidence_predicate": "ev_nesting_conjunction",
        "classification": {"struct": "judgment", "raw": "judgment"},
        "params": {"target": target, "callee": callee, "threshold": thr},
        "raw_evidence": "the function and its body are present in the source.",
    })
    return cases


def gen_string_literal_probe(facts, module):
    """EVIDENCE-REMOVAL PROBE. Derivable from raw, NOT from structure.

    Structure carries no string literals, so this case is admissible under raw
    and unanswerable under struct. It is the designed test that preprocessing
    can remove evidence required to derive an answer.
    """
    lits = [s for s in facts.string_literals() if 4 <= len(s) <= 40]
    if not lits:
        return []
    fns = sorted(facts.qualified_functions)
    if not fns:
        return []
    fn = fns[0]
    src = facts.source_of(fn)
    hit = next((s for s in lits if s in src), lits[0])
    return [{
        "case_id": case_id(module, "string_literal_probe", 1),
        "type": "noul", "ctype": "string_literal_probe",
        "question": (f"Does the body of `{fn}` contain the string literal "
                     f"{hit!r}?"),
        "ground_truth": "yes" if hit in src else "no",
        "gt_basis": (f"literal substring test against the recorded source of "
                     f"`{fn}` (lines {facts.fn_fact(fn)['lineno']}-"
                     f"{facts.fn_fact(fn)['end_lineno']})"),
        "evidence_predicate": "ev_string_literal",
        "classification": {"struct": "unanswerable", "raw": "judgment"},
        "params": {"fn": fn, "literal": hit},
        "raw_evidence": "the function body is present verbatim in the raw source.",
        "note": ("Structure carries no string literals by design, so this case "
                 "is UNANSWERABLE under struct. It is retained to measure "
                 "evidence removal, not to score a model error."),
    }]


def gen_unanswerable(facts, module):
    """Not derivable from ANY representation. Never a model error."""
    fns = sorted(facts.qualified_functions)
    if not fns:
        return []
    fn = fns[len(fns) // 2]
    return [
        {
            "case_id": case_id(module, "unanswerable_semantic", 1),
            "type": "noul", "ctype": "unanswerable_semantic",
            "question": (f"Is `{fn}` safe to call concurrently from multiple "
                         f"threads?"),
            "ground_truth": None,
            "gt_basis": "NOT DERIVABLE. Thread safety is a semantic property; "
                        "neither the source nor the extracted structure "
                        "establishes it.",
            "evidence_predicate": "ev_none",
            "classification": {"struct": "unanswerable", "raw": "unanswerable"},
            "params": {"fn": fn},
            "raw_evidence": "none; the property is not in the representation.",
            "note": ("Admissible as an unanswerable cell only. Used to compare "
                     "answering/confidence behaviour across representations, "
                     "never to score accuracy."),
        },
        {
            "case_id": case_id(module, "unanswerable_runtime", 1),
            "type": "noul", "ctype": "unanswerable_runtime",
            "question": (f"At runtime, how many times is `{fn}` called per "
                         f"request?"),
            "ground_truth": None,
            "gt_basis": "NOT DERIVABLE. Runtime call frequency is a runtime "
                        "property; no static representation establishes it.",
            "evidence_predicate": "ev_none",
            "classification": {"struct": "unanswerable", "raw": "unanswerable"},
            "params": {"fn": fn},
            "raw_evidence": "none; the property is not in the representation.",
            "note": "Admissible as an unanswerable cell only.",
        },
    ]


GENERATORS = [
    ("direct_call", gen_direct_call),
    ("call_path2", gen_path2),
    ("param_rebound", gen_param_rebound),
    ("unused_import", gen_unused_import),
    ("nesting_conjunction", gen_nesting_conjunction),
    ("string_literal_probe", gen_string_literal_probe),
    ("unanswerable", gen_unanswerable),
]


def build():
    cases = []
    for module in SUBJECTS:
        facts = extract.load_module(
            os.path.join(PHASE2, "corpus", module + ".py"), module)
        for ctype, fn in GENERATORS:
            for c in fn(facts, module):
                c["module"] = module
                c["module_sha256"] = extract.sha256_text(facts.source)
                c["struct_sha256"] = extract.sha256_text(facts.render_struct())
                cases.append(c)
    return cases


def main():
    out = os.path.join(PHASE2, "frozen", "cases.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cases = build()
    text = json.dumps(cases, ensure_ascii=False, indent=1, sort_keys=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")

    from collections import Counter
    print(f"cases: {len(cases)} -> {out}")
    print(f"  sha256: {hashlib.sha256(text.encode()).hexdigest()}")
    print("  by ctype:", dict(Counter(c["ctype"] for c in cases)))
    print("  by ground_truth:", dict(Counter(
        str(c["ground_truth"]) for c in cases)))
    print("  by module:", dict(Counter(c["module"] for c in cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
