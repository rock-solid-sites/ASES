#!/usr/bin/env python3
"""Compute the FRESH case pool for Experiment 3, deterministically.

Experiment 1 drew on all 67 frozen cases, and on 25 call edges, 10 (fn,param)
pairs, 5 import tokens, 5 nesting targets and 5 unanswerable subjects. A fresh
case is one whose underlying SELECTION was not used before, not merely one with
a new id.

Question wording and ground-truth semantics are copied verbatim from
`gen_cases.py` so the fresh cases are judged exactly as the frozen 67 were. A
later build of this pool emitted only TRUE-polarity candidates for `direct_call`
and `nesting_conjunction`; a constant-`yes` model would then score 100% and
`normal_answer_correct` would be meaningless. Both polarities are therefore
enumerated here for every answerable ctype, and `build_packet.py` requires a
balanced mix before it will emit a packet.

This module computes CANDIDATES only. Ground truth is recomputed independently
in `build_packet.py` from `extract.py`; the `polarity` field here is a selection
hint, never an authority.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PHASE2, "harness"))

import extract  # noqa: E402
import gen_cases as gc  # noqa: E402

OUT = os.path.join(PHASE2, "exp3", "frozen", "pool.json")

UNANSWERABLE_CLASSES = [
    ("unanswerable_semantic",
     "Is `{fn}` safe to call concurrently from multiple threads?"),
    ("unanswerable_runtime",
     "At runtime, how many times is `{fn}` called per request?"),
    ("unanswerable_version",
     "Which exact version of the library this module imports must be present "
     "for `{fn}` to behave as written?"),
    ("unanswerable_intent",
     "Why was `{fn}` written — what problem was it introduced to solve?"),
]


def module_facts(module):
    return extract.load_module(
        os.path.join(PHASE2, "corpus", module + ".py"), module)


def build_pool():
    frozen = json.load(open(os.path.join(PHASE2, "frozen", "cases.json"),
                            encoding="utf-8"))
    used_ids, used_edges, used_params, used_imports = set(), set(), set(), set()
    used_nests, used_unans_fns = set(), set()
    for c in frozen:
        p, ct = c["params"], c["ctype"]
        if ct == "direct_call":
            used_edges.add((p["caller"], p["callee"]))
        elif ct == "param_rebound":
            used_params.add((p["fn"], p["param"]))
        elif ct == "unused_import":
            used_imports.add(p["mod"])
        elif ct == "nesting_conjunction":
            used_nests.add((p["target"], p["callee"]))
        elif ct.startswith("unanswerable"):
            used_unans_fns.add(p["fn"])

    pool = {"direct_call": [], "param_rebound": [], "unused_import": [],
            "nesting_conjunction": [], "string_literal_probe": [],
            "call_path2": [], "unanswerable": []}
    unans_n = 0

    for module in gc.SUBJECTS:
        facts = module_facts(module)
        qf = facts.qualified_functions
        edges = sorted({(a, b) for a, b in facts.call_edges if a in qf})
        adj = {}
        for a, b in edges:
            adj.setdefault(a, []).append(b)
        callers_all = sorted(qf)

        # ---- direct_call: BOTH polarities, per gen_cases.gen_direct_call ----
        for caller, callee in edges:
            if "." in callee or (caller, callee) in used_edges:
                continue
            pool["direct_call"].append({
                "module": module, "ctype": "direct_call", "polarity": "yes",
                "question": (f"In this module, does `{caller}` directly call "
                             f"`{callee}`?"),
                "params": {"caller": caller, "callee": callee}})
        by_callee = {}
        for a, b in edges:
            if "." not in b:
                by_callee.setdefault(b, []).append(a)
        for callee, others in sorted(by_callee.items()):
            for caller in callers_all:
                if caller == callee or callee in caller:
                    continue
                if (caller, callee) in edges or (caller, callee) in used_edges:
                    continue
                pool["direct_call"].append({
                    "module": module, "ctype": "direct_call", "polarity": "no",
                    "question": (f"In this module, does `{caller}` directly call "
                                 f"`{callee}`?"),
                    "params": {"caller": caller, "callee": callee,
                               "called_elsewhere_by": sorted(others)}})
                break        # one FALSE per callee keeps negatives diverse

        # ---- param_rebound: both polarities already present in the pool ----
        for fn, f in sorted(qf.items()):
            for prm in f["params"]:
                if prm.startswith("*") or (fn, prm) in used_params:
                    continue
                truth = prm in f["assigned_locals"]
                pool["param_rebound"].append({
                    "module": module, "ctype": "param_rebound",
                    "polarity": "yes" if truth else "no",
                    "question": (f"In `{fn}`, is the parameter `{prm}` rebound "
                                 f"by an assignment to `{prm}` inside the "
                                 f"function body?"),
                    "params": {"fn": fn, "param": prm}})

        # ---- unused_import: both polarities ----
        unused = set(facts.unused_imports())
        cands = []
        for imp in facts.imports:
            if imp["names"] is None:
                cands.append((imp["module"], imp["module"] in unused))
            else:
                for nm in imp["names"]:
                    if nm == "*":
                        continue
                    cands.append((f"{imp['module']}.{nm}",
                                  f"{imp['module']}.{nm}" in unused))
        for key, truth in cands:
            if key in used_imports:
                continue
            pool["unused_import"].append({
                "module": module, "ctype": "unused_import",
                "polarity": "yes" if truth else "no",
                "question": (f"Is `{key}` imported in this module but never "
                             f"referenced by name anywhere in the module's "
                             f"code?"),
                "params": {"mod": key}})

        # ---- nesting_conjunction: TRUE and a defensible module-wide FALSE ----
        # The question is a module-level existential, so a FALSE claim is only
        # defensible when NO sufficiently deep function calls the callee.
        deep = sorted((f, v["max_nesting"]) for f, v in qf.items()
                      if v["max_nesting"] >= 3)
        if deep:
            thr = min(m for _, m in deep) - 1
            deep_fns = {f for f, m in deep if m > thr}
            deep_callees = {c for f in deep_fns
                            for c in adj.get(f, []) if "." not in c}
            for target, m in deep:
                for callee in adj.get(target, []):
                    if "." in callee:
                        continue
                    if (target, callee) in used_nests:
                        continue
                    pool["nesting_conjunction"].append({
                        "module": module, "ctype": "nesting_conjunction",
                        "polarity": "yes", "threshold": thr,
                        "question": (f"Does any function in this module have "
                                     f"maximum control-flow nesting deeper "
                                     f"than {thr} AND also call `{callee}`?"),
                        "params": {"target": target, "callee": callee,
                                   "threshold": thr}})
            all_bare = {c for f, _ in deep for c in adj.get(f, [])
                        if "." not in c} | {
                b for b in {x[1] for x in edges} if "." not in b}
            for callee in sorted(all_bare - deep_callees):
                pool["nesting_conjunction"].append({
                    "module": module, "ctype": "nesting_conjunction",
                    "polarity": "no", "threshold": thr,
                    "question": (f"Does any function in this module have "
                                 f"maximum control-flow nesting deeper than "
                                 f"{thr} AND also call `{callee}`?"),
                    "params": {"target": None, "callee": callee,
                               "threshold": thr,
                               "neg_basis": (f"no function with max_nesting > "
                                             f"{thr} calls `{callee}`")}})

        # ---- string_literal_probe: TRUE and FALSE ----
        lits = [s for s in facts.string_literals() if 4 <= len(s) <= 40]
        fns = sorted(qf)
        if lits and fns:
            fn = fns[-1]              # fns[0] was used by Experiment 1
            src = facts.source_of(fn)
            for lit in lits:
                if (fn, lit) in {(c["params"].get("fn"), c["params"].get("literal"))
                                 for c in frozen
                                 if c["ctype"] == "string_literal_probe"}:
                    continue
                hit = lit in src
                pool["string_literal_probe"].append({
                    "module": module, "ctype": "string_literal_probe",
                    "polarity": "yes" if hit else "no",
                    "question": (f"Does the body of `{fn}` contain the string "
                                 f"literal {lit!r}?"),
                    "params": {"fn": fn, "literal": lit}})
                if hit:
                    break

        # ---- call_path2: TRUE, and a defensible existential FALSE ----
        for src in sorted(qf):
            for dst in sorted(qf):
                if dst == src:
                    continue
                mids = [m for m in adj.get(src, [])
                        if m in qf and m != src and dst in adj.get(m, [])]
                pair_used = any(c["params"].get("mid") == m and
                                c["params"].get("dst") == dst and
                                c["params"].get("src") == src
                                for c in frozen if c["ctype"] == "call_path2")
                if pair_used:
                    continue
                if mids:
                    pool["call_path2"].append({
                        "module": module, "ctype": "call_path2",
                        "polarity": "yes",
                        "question": (f"In this module, is there a function "
                                     f"that `{src}` calls, which in turn calls "
                                     f"`{dst}`?"),
                        "params": {"src": src, "mid": mids[0], "dst": dst}})
                else:
                    # FALSE is only defensible when src and dst are themselves
                    # inspectable module functions, so their absence of a 2-hop
                    # chain is a real negative rather than an artefact of the
                    # callee being external.
                    if any("." not in d for d in adj.get(src, [])):
                        pool["call_path2"].append({
                            "module": module, "ctype": "call_path2",
                            "polarity": "no",
                            "question": (f"In this module, is there a function "
                                         f"that `{src}` calls, which in turn "
                                         f"calls `{dst}`?"),
                            "params": {"src": src, "mid": None, "dst": dst,
                                       "neg_basis": "no 2-hop chain exists"}})

        # ---- unanswerable: functions never used as unanswerable subjects ----
        # TWO DIFFERENT functions per module and the class rotates GLOBALLY, so
        # Experiment 1's five-subject coupling is broken and all four classes
        # appear. The two classes for a module never share a function.
        fresh_fns = [f for f in sorted(qf)
                     if f not in used_unans_fns and not f.endswith(".__init__")]
        for fn in fresh_fns[:2]:
            cls, tmpl = UNANSWERABLE_CLASSES[
                unans_n % len(UNANSWERABLE_CLASSES)]
            unans_n += 1
            pool["unanswerable"].append({
                "module": module, "ctype": cls, "polarity": None,
                "unanswerable": True,
                "question": tmpl.format(fn=fn),
                "params": {"fn": fn, "unans_class": cls}})

    return pool, {
        "used_case_ids": len(used_ids), "used_call_edges": len(used_edges),
        "used_fn_param": len(used_params), "used_import_tokens": len(used_imports),
        "used_nesting_targets": len(used_nests),
        "used_unanswerable_subjects": len(used_unans_fns)}


def main():
    pool, excl = build_pool()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pool, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"fresh pool -> {OUT}")
    print(f"  excluded by Exp 1: {excl}")
    print(f"  {'ctype':22s} {'yes':>5s} {'no':>5s} {'unans':>6s}")
    for k, v in sorted(pool.items()):
        y = sum(1 for c in v if c["polarity"] == "yes")
        n = sum(1 for c in v if c["polarity"] == "no")
        u = sum(1 for c in v if c.get("unanswerable"))
        print(f"  {k:22s} {y:5d} {n:5d} {u:6d}")
    uf = {c["params"]["fn"] for c in pool["unanswerable"]}
    per = {}
    for c in pool["unanswerable"]:
        per.setdefault(c["module"], []).append(c["ctype"])
    print(f"  unanswerable subjects: {len(uf)} distinct functions "
          f"(Exp 1 used {excl['used_unanswerable_subjects']})")
    for m, c in sorted(per.items()):
        print(f"    {m:16s} {c}")
    bad = [k for k, v in pool.items()
           if k != "unanswerable"
           and not any(c["polarity"] == "yes" for c in v)
           or (k != "unanswerable" and v and not any(
               c["polarity"] == "no" for c in v))]
    if bad:
        print(f"  WARNING single-polarity ctypes: {bad}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
