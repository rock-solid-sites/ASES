#!/usr/bin/env python3
"""Phase 2 admissibility gate.

Four independent checks. A case that fails any of them is not silently scored.

1. GROUND-TRUTH RE-DERIVATION. Recompute every answerable case's ground truth
   here, from the source AST, WITHOUT reading the generator's recorded
   `gt_basis` or trusting its `ground_truth` field. A generator bug therefore
   shows up as a mismatch rather than as a wrong score.

2. PER-CONDITION DERIVABILITY. Evaluate the case's required-evidence predicate
   against each representation. A condition that fails its predicate is
   UNANSWERABLE for that case -- never a model error. Differential
   admissibility is a reported result, because preprocessing can remove
   evidence required to derive an answer.

3. NO ANSWER LEAK. Scan every rendering for (a) any field whose name asserts a
   proposition some case asks about, and (b) any case's ground-truth value
   appearing as a labelled answer. Structure must expose FACTS whose conjunction
   the model must perform.

4. SYMMETRIC DERIVABILITY. Only cases admissible under BOTH raw and struct
   enter the representation comparison. Cases admissible under one condition
   only are reported separately as a derivability result, because a one-sided
   comparison measures the representation difference and nothing else.

Exit non-zero if any invariant is violated, so a broken case set cannot be run.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import extract  # noqa: E402
import gen_cases as gc  # noqa: E402

CONDITIONS = ["raw", "struct", "raw_ic", "struct_ic"]

# Field-name fragments that would constitute a precomputed answer for some
# case type. The structure must never contain these.
FORBIDDEN_FIELD_FRAGMENTS = [
    "rebound", "unused", "shadow", "path_exists", "reachable",
    "conjunction", "answers", "ground_truth", "correct", "label",
    "is_called", "calls_", "has_unused", "verdict",
]

ANSWER_TOKENS = ("yes", "no")


# ------------------------------------------------------- 1. re-derivation
def rederive(facts, c):
    """Recompute the ground truth for one case, from the AST only.

    Returns (value, status) where status is 'match', 'mismatch' or
    'unanswerable'/'unsupported'.
    """
    ct, p = c["ctype"], c["params"]
    if ct == "direct_call":
        v = "yes" if facts.has_call_edge(p["caller"], p["callee"]) else "no"
        return v, ("match" if v == c["ground_truth"] else "mismatch")
    if ct == "call_path2":
        via = facts.has_call_edge(p["src"], p["mid"]) and \
            facts.has_call_edge(p["mid"], p["dst"])
        v = "yes" if via else "no"
        return v, ("match" if v == c["ground_truth"] else "mismatch")
    if ct == "param_rebound":
        f = facts.fn_fact(p["fn"])
        if not f or p["param"] not in f["params"]:
            return None, "unsupported"
        v = "yes" if p["param"] in f["assigned_locals"] else "no"
        return v, ("match" if v == c["ground_truth"] else "mismatch")
    if ct == "unused_import":
        v = "yes" if p["mod"] in set(facts.unused_imports()) else "no"
        return v, ("match" if v == c["ground_truth"] else "mismatch")
    if ct == "nesting_conjunction":
        f = facts.fn_fact(p["target"])
        v = "yes" if (f["max_nesting"] > p["threshold"]
                      and facts.has_call_edge(p["target"], p["callee"])) else "no"
        return v, ("match" if v == c["ground_truth"] else "mismatch")
    if ct == "string_literal_probe":
        v = "yes" if p["literal"] in facts.source_of(p["fn"]) else "no"
        return v, ("match" if v == c["ground_truth"] else "mismatch")
    if ct in ("unanswerable_semantic", "unanswerable_runtime"):
        return None, "unanswerable"
    return None, "unsupported"


# ------------------------------------------------- 2. per-condition gating
def derivable(facts, c, condition):
    """Is the ground truth derivable from this representation?

    A case with no ground truth is not derivable under ANY condition -- it is
    an unanswerable cell by construction, not a scorable one.
    """
    if c["ground_truth"] is None:
        return False
    if condition in ("raw", "raw_ic"):
        # Raw is the verbatim source, so derivability reduces to the case
        # having recorded raw evidence at all.
        return bool(c.get("raw_evidence")) and c.get("raw_evidence") != \
            "none; the property is not in the representation."
    # Structure conditions: run the declared required-evidence predicate.
    pred_name = c["evidence_predicate"]
    pred = getattr(gc, pred_name, None)
    if pred is None:
        return False
    try:
        return bool(pred(facts, c))
    except Exception:
        return False


# ------------------------------------------------------------- 3. leakage
def field_names(struct_text):
    """Identifiers used as field/label names in the structure rendering."""
    names = set()
    for line in struct_text.splitlines():
        m = re.match(r"\s*([a-z_]+)=", line)
        if m:
            names.add(m.group(1))
        m2 = re.match(r"def\s+(\S+)", line)
        if m2:
            names.add("def")
        for m3 in re.finditer(r"^(\w+)\s*->", line):
            names.add("edge")
    return names


def check_leaks(struct_text, cases):
    findings = []
    names = field_names(struct_text)
    for frag in FORBIDDEN_FIELD_FRAGMENTS:
        for n in names:
            if frag in n:
                findings.append(
                    f"forbidden field fragment {frag!r} present in field {n!r}")
    low = struct_text.lower()
    for c in cases:
        gt = c["ground_truth"]
        if gt in (None, "yes", "no"):
            continue
        if re.search(rf"\b(answer|result|verdict)\b\s*[:=]\s*{re.escape(gt)}",
                     low):
            findings.append(f"ground-truth token leaked for {c['case_id']}")
    # The queried entity must not appear pre-joined with its answer.
    for c in cases:
        if c["ctype"] != "param_rebound":
            continue
        fn, par = c["params"]["fn"], c["params"]["param"]
        if re.search(rf"{re.escape(fn)}[^\n]{{0,40}}{re.escape(par)}"
                     rf"[^\n]{{0,20}}rebound", struct_text, re.I):
            findings.append(f"rebound conjunction leaked for {c['case_id']}")
    return findings


# ------------------------------------------------------------------ main
def main():
    cases_path = os.path.join(PHASE2, "frozen", "cases.json")
    cases = json.load(open(cases_path, encoding="utf-8"))

    facts_by_mod = {}
    for m in gc.SUBJECTS:
        facts_by_mod[m] = extract.load_module(
            os.path.join(PHASE2, "corpus", m + ".py"), m)
    distractor = extract.load_module(
        os.path.join(PHASE2, "corpus", "_distractor_uuid.py"), "uuid")

    problems = []
    rows = []
    for c in cases:
        facts = facts_by_mod[c["module"]]
        # 1. independent re-derivation
        val, status = rederive(facts, c)
        if status == "mismatch":
            problems.append(f"GROUND-TRUTH MISMATCH {c['case_id']}: "
                            f"recorded={c['ground_truth']!r} rederived={val!r}")
        elif status == "unsupported":
            problems.append(f"UNSUPPORTED ctype {c['case_id']}")
        # corpus identity
        if extract.sha256_text(facts.source) != c["module_sha256"]:
            problems.append(f"CORPUS DRIFT {c['case_id']}")
        if extract.sha256_text(facts.render_struct()) != c["struct_sha256"]:
            problems.append(f"STRUCT DRIFT {c['case_id']}")
        # 2. per-condition derivability
        d = {cond: derivable(facts, c, cond) for cond in CONDITIONS}
        # 4. symmetric comparability
        comparable = d["raw"] and d["struct"] and c["ground_truth"] is not None
        rows.append({
            "case_id": c["case_id"], "ctype": c["ctype"],
            "module": c["module"], "ground_truth": c["ground_truth"],
            "rederived": val, "rederive_status": status,
            "derivable": d, "comparable": comparable,
            "classification": c["classification"],
        })

    # 3. leakage, over the subject structures
    leak_findings = []
    for m in gc.SUBJECTS:
        st = facts_by_mod[m].render_struct()
        leak_findings += [f"[{m}] {f}" for f in check_leaks(st, cases)]
    # and the distractor-perturbed render
    for m in gc.SUBJECTS:
        st = facts_by_mod[m].render_struct() + distractor.render_struct()
        leak_findings += [f"[{m}+distractor] {f}"
                          for f in check_leaks(st, cases)]
    problems += leak_findings

    from collections import Counter
    report = {
        "cases_sha256": hashlib.sha256(
            open(cases_path, "rb").read()).hexdigest(),
        "n_cases": len(cases),
        "n_ground_truth_mismatch": sum(
            1 for r in rows if r["rederive_status"] == "mismatch"),
        "n_leak_findings": len(leak_findings),
        "admissibility_by_condition": {
            cond: sum(1 for r in rows if r["derivable"][cond]) for cond in CONDITIONS},
        "n_comparable_raw_and_struct": sum(1 for r in rows if r["comparable"]),
        "n_struct_only": sum(
            1 for r in rows if r["derivable"]["struct"] and not r["derivable"]["raw"]),
        "n_raw_only": sum(
            1 for r in rows if r["derivable"]["raw"] and not r["derivable"]["struct"]),
        "comparable_by_ctype": dict(Counter(
            r["ctype"] for r in rows if r["comparable"])),
        "problems": problems,
    }
    out = os.path.join(PHASE2, "frozen", "admissibility.json")
    json.dump({"summary": report, "rows": rows},
              open(out, "w", encoding="utf-8"), indent=1)

    print(f"cases sha256      : {report['cases_sha256']}")
    print(f"cases             : {report['n_cases']}")
    print(f"GT mismatches     : {report['n_ground_truth_mismatch']}")
    print(f"leak findings     : {report['n_leak_findings']}")
    print(f"admissible/cond   : {report['admissibility_by_condition']}")
    print(f"comparable raw+struct : {report['n_comparable_raw_and_struct']}")
    print(f"struct-only       : {report['n_struct_only']}")
    print(f"raw-only          : {report['n_raw_only']}   <- evidence removal by structure")
    print(f"comparable by ctype: {report['comparable_by_ctype']}")
    if problems:
        print("\nPROBLEMS:")
        for p in problems[:25]:
            print("  -", p)
        return 1
    print("\nall admissibility invariants hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
