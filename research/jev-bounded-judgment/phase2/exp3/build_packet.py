#!/usr/bin/env python3
"""Select and freeze the Experiment 3 fresh packet.

Two jobs, deliberately separated:

1. DETERMINISTIC SELECTION. The quota and the round-robin rule below were fixed
   before any API call and are declared in `exp3/DESIGN.md`. Selection reads
   `polarity` from the pool purely to guarantee balance, so a constant-answer
   model cannot score perfectly and `normal_answer_correct` stays meaningful.

2. INDEPENDENT GROUND-TRUTH RECOMPUTATION. Every selected case's ground truth is
   recomputed here from `extract.py`, and the question text is re-rendered from
   the `gen_cases.py` template. The pool's `polarity` is treated as a hint and is
   cross-checked against the recomputation; disagreement rejects the packet.
   The arms are read from Experiment 1's own frozen packet, so the instruction
   text is byte-identical by construction rather than by retyping.

Checks, all enforced before the packet is written:
  F1 no duplicate or reused case_id
  F2 no underlying selection reuses an Experiment 1 selection
  F3 answerable polarity is balanced
  F4 recomputed ground truth agrees with the pool hint
  F5 question text re-renders identically from the verified template
  F6 both arms are `choice` arms carried byte-identically from Experiment 1
  F7 unanswerable subjects are distinct functions, none reused from Experiment 1
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PHASE2, "harness"))

import extract  # noqa: E402
import represent  # noqa: E402

sys.path.insert(0, os.path.join(PHASE2, "harness"))
import exp3_pool  # noqa: E402

POOL = os.path.join(HERE, "frozen", "pool.json")
OUT = os.path.join(HERE, "frozen", "packet.json")
EXP1_PACKET = os.path.join(PHASE2, "exp1", "frozen", "packet.json")

# (yes_quota, no_quota) per answerable ctype, fixed before execution.
QUOTA = {
    "direct_call": (5, 5),
    "param_rebound": (4, 4),
    "unused_import": (1, 2),
    "nesting_conjunction": (3, 3),
    "string_literal_probe": (3, 3),
    "call_path2": (4, 4),
}


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def recompute_ground_truth(facts, ctype, p):
    """Recompute ground truth from the corpus, ignoring the pool's hint."""
    if ctype == "direct_call":
        return "yes" if facts.has_call_edge(p["caller"], p["callee"]) else "no"
    if ctype == "param_rebound":
        return "yes" if p["param"] in facts.fn_fact(p["fn"])["assigned_locals"] \
            else "no"
    if ctype == "unused_import":
        return "yes" if p["mod"] in set(facts.unused_imports()) else "no"
    if ctype == "string_literal_probe":
        return "yes" if p["literal"] in facts.source_of(p["fn"]) else "no"
    if ctype == "call_path2":
        mid = p.get("mid")
        return "yes" if (mid and facts.has_call_edge(p["src"], mid)
                         and facts.has_call_edge(mid, p["dst"])) else "no"
    if ctype == "nesting_conjunction":
        thr = p["threshold"]
        deep = {f for f, v in facts.qualified_functions.items()
                if v["max_nesting"] > thr}
        return "yes" if any(facts.has_call_edge(f, p["callee"])
                            for f in deep) else "no"
    if ctype.startswith("unanswerable"):
        return None
    raise ValueError(f"unknown ctype {ctype}")


def rerender_question(ctype, p):
    """Re-render the question from the verified gen_cases templates."""
    if ctype == "direct_call":
        return (f"In this module, does `{p['caller']}` directly call "
                f"`{p['callee']}`?")
    if ctype == "param_rebound":
        return (f"In `{p['fn']}`, is the parameter `{p['param']}` rebound by an "
                f"assignment to `{p['param']}` inside the function body?")
    if ctype == "unused_import":
        return (f"Is `{p['mod']}` imported in this module but never referenced "
                f"by name anywhere in the module's code?")
    if ctype == "string_literal_probe":
        return (f"Does the body of `{p['fn']}` contain the string literal "
                f"{p['literal']!r}?")
    if ctype == "call_path2":
        return (f"In this module, is there a function that `{p['src']}` calls, "
                f"which in turn calls `{p['dst']}`?")
    if ctype == "nesting_conjunction":
        return (f"Does any function in this module have maximum control-flow "
                f"nesting deeper than {p['threshold']} AND also call "
                f"`{p['callee']}`?")
    if ctype.startswith("unanswerable"):
        # The unanswerable templates are Experiment 3's own, declared in
        # exp3_pool.UNANSWERABLE_CLASSES. They are re-rendered here so the F5
        # check still guards them against silent reword between pool and packet.
        for cls, tmpl in exp3_pool.UNANSWERABLE_CLASSES:
            if cls == ctype:
                return tmpl.format(fn=p["fn"])
        raise ValueError(f"no template for unanswerable class {ctype}")
    return None


def round_robin(cands, quota):
    """Take `quota` candidates, cycling modules so no single module dominates."""
    by_mod = {}
    for c in cands:
        by_mod.setdefault(c["module"], []).append(c)
    for v in by_mod.values():
        v.sort(key=lambda c: json.dumps(c["params"], sort_keys=True))
    out, mods = [], sorted(by_mod)
    while len(out) < quota:
        progressed = False
        for m in list(mods):
            if by_mod[m] and len(out) < quota:
                out.append(by_mod[m].pop(0))
                progressed = True
            if not by_mod[m]:
                mods.remove(m)
        if not progressed:
            break
    return out


def main():
    pool = json.load(open(POOL, encoding="utf-8"))
    frozen = json.load(open(os.path.join(PHASE2, "frozen", "cases.json"),
                            encoding="utf-8"))
    frozen_ids = {c["case_id"] for c in frozen}
    exp1 = {
        "edges": {(c["params"]["caller"], c["params"]["callee"])
                  for c in frozen if c["ctype"] == "direct_call"},
        "params": {(c["params"]["fn"], c["params"]["param"])
                   for c in frozen if c["ctype"] == "param_rebound"},
        "imports": {c["params"]["mod"] for c in frozen
                    if c["ctype"] == "unused_import"},
        "nests": {(c["params"]["target"], c["params"]["callee"])
                  for c in frozen if c["ctype"] == "nesting_conjunction"},
        "unans_fns": {c["params"]["fn"] for c in frozen
                      if c["ctype"].startswith("unanswerable")},
        "lits": {(c["params"].get("fn"), c["params"].get("literal"))
                 for c in frozen if c["ctype"] == "string_literal_probe"},
        "paths": {(c["params"].get("src"), c["params"].get("mid"),
                   c["params"].get("dst")) for c in frozen
                  if c["ctype"] == "call_path2"},
    }

    problems = []
    selected = []
    n_yes = n_no = 0

    for ctype, (q_yes, q_no) in sorted(QUOTA.items()):
        for polarity, quota in (("yes", q_yes), ("no", q_no)):
            cands = [c for c in pool[ctype] if c["polarity"] == polarity]
            got = round_robin(cands, quota)
            if len(got) < quota:
                problems.append(f"F3: {ctype}/{polarity} wanted {quota}, "
                                f"pool has only {len(cands)}")
            n_yes += sum(1 for _ in got) if polarity == "yes" else 0
            n_no += sum(1 for _ in got) if polarity == "no" else 0
            selected.extend(got)

    unans = list(pool["unanswerable"])
    ufns = [c["params"]["fn"] for c in unans]
    if len(unans) != 10:
        problems.append(f"F7: expected 10 unanswerable candidates, "
                        f"got {len(unans)}")
    if len(set(ufns)) != len(ufns):
        problems.append("F7: an unanswerable function is reused across classes")
    clash = set(ufns) & exp1["unans_fns"]
    if clash:
        problems.append(f"F2: unanswerable subjects reused from Exp 1: {clash}")
    selected.extend(unans)

    # ---- validate every selected row --------------------------------------
    selected.sort(key=lambda c: (c["ctype"], c["module"],
                                 json.dumps(c["params"], sort_keys=True)))
    seen_ids, rows = set(), []
    facts_cache = {}
    for i, c in enumerate(selected):
        m, ctype, p = c["module"], c["ctype"], c["params"]
        if m not in facts_cache:
            facts_cache[m] = extract.load_module(
                os.path.join(PHASE2, "corpus", m + ".py"), m)
        facts = facts_cache[m]
        cid = f"{m}.{ctype}.exp3.{i:03d}"

        if cid in frozen_ids or cid in seen_ids:
            problems.append(f"F1: duplicate or reused case_id {cid}")
        seen_ids.add(cid)

        if ctype == "direct_call" and (p["caller"], p["callee"]) in exp1["edges"]:
            problems.append(f"F2: {cid} reuses an Exp 1 call edge")
        if ctype == "param_rebound" and (p["fn"], p["param"]) in exp1["params"]:
            problems.append(f"F2: {cid} reuses an Exp 1 (fn,param)")
        if ctype == "unused_import" and p["mod"] in exp1["imports"]:
            problems.append(f"F2: {cid} reuses an Exp 1 import token")
        if ctype == "nesting_conjunction" and \
                (p.get("target"), p["callee"]) in exp1["nests"]:
            problems.append(f"F2: {cid} reuses an Exp 1 nesting target")
        if ctype == "string_literal_probe" and (p["fn"], p["literal"]) in exp1["lits"]:
            problems.append(f"F2: {cid} reuses an Exp 1 string-literal probe")
        if ctype == "call_path2" and \
                (p["src"], p.get("mid"), p["dst"]) in exp1["paths"]:
            problems.append(f"F2: {cid} reuses an Exp 1 call path")

        gt = recompute_ground_truth(facts, ctype, p)
        if c.get("unanswerable"):
            if gt is not None:
                problems.append(f"F4: {cid} declared unanswerable but "
                                f"recomputation returned {gt!r}")
        elif gt != c["polarity"]:
            problems.append(f"F4: {cid} pool hint {c['polarity']!r} but "
                            f"independent recomputation says {gt!r}")

        rq = rerender_question(ctype, p)
        if rq != c["question"]:
            problems.append(f"F5: {cid} question does not re-render.\n"
                            f"      pool:     {c['question']!r}\n"
                            f"      template: {rq!r}")

        state, prov = represent.build_state({"module": m}, "raw")
        rows.append({
            "case_id": cid, "ctype": ctype, "module": m,
            "ground_truth": gt,
            "ground_truth_source": ("recomputed independently in build_packet.py "
                                    "from extract.py; the pool polarity is a "
                                    "selection hint only, never an authority"),
            "question": c["question"],
            "condition": "raw", "send": True,
            "score_for_correctness": gt is not None,
            "unanswerable": gt is None,
            "unanswerable_class": ctype if gt is None else None,
            "state_sha256": sha(state),
            "state_bytes": prov["state_bytes"],
            "params": p,
            "pool_polarity_hint": c.get("polarity"),
        })

    if abs(n_yes - n_no) > 2:
        problems.append(f"F3: answerable polarity imbalance {n_yes} yes vs "
                        f"{n_no} no")

    plan = json.load(open(EXP1_PACKET, encoding="utf-8"))["plan"]
    for arm, spec in sorted(plan.items()):
        if spec.get("type") != "choice":
            problems.append(f"F6: arm {arm} is not a choice arm")
        if not spec.get("instructions"):
            problems.append(f"F6: arm {arm} carries no instruction text")
    if set(plan) != {"arm_a_forced", "arm_b_explicit_unknown"}:
        problems.append(f"F6: unexpected arm set {sorted(plan)}")

    if problems:
        print("PACKET REJECTED:")
        for p in sorted(set(problems)):
            print("  -", p)
        return 1

    packet = {
        "experiment": "exp3-preregistered-explicit-unknown-confirmation",
        "subject_model": "jev-1.13.0",
        "endpoint": "https://api.typesafe.ai/v1/systemone",
        "condition": "raw",
        "preregistered_rules": {
            "explicit_unknown": {
                "rule": "p(insufficient_evidence) >= 0.05",
                "source": "operator-specified; fixed before execution; NOT tuned",
            },
            "external_gate": {
                "rule": "act iff p(ground_truth_option) >= 0.86; abstain on an "
                        "unanswerable case iff max(p(yes),p(no)) < 0.86",
                "source": "carried from Experiment 1, where 0.86 was the best "
                          "point on that grid; applied OUT OF SAMPLE here and "
                          "NOT re-tuned",
            },
        },
        "plan": plan,
        "plan_provenance": ("read from exp1/frozen/packet.json so the arm "
                            "instruction text is byte-identical to Experiment 1"),
        "selection_rule": {
            "quota": {k: list(v) for k, v in sorted(QUOTA.items())},
            "method": "round-robin across modules, sorted by params, "
                      "deterministic",
            "fixed": "before any API call",
        },
        "counts": {
            "answerable_yes": n_yes, "answerable_no": n_no,
            "unanswerable": len(unans), "total_cases": len(rows),
            "arms": len(plan),
            "planned_requests": len(rows) * len(plan),
        },
        "freshness": {
            "reused_case_ids": 0, "reused_selections": 0,
            "exp1_unanswerable_subjects": len(exp1["unans_fns"]),
            "exp3_unanswerable_subjects": len(set(ufns)),
        },
        "rows": rows,
    }
    text = json.dumps(packet, ensure_ascii=False, indent=1, sort_keys=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    print(f"packet -> {OUT}")
    print(f"  sha256={hashlib.sha256(text.encode()).hexdigest()}")
    print(f"  answerable yes={n_yes} no={n_no}  unanswerable={len(unans)}")
    print(f"  arms={len(plan)}  planned_requests="
          f"{packet['counts']['planned_requests']}")
    print("  checks F1-F7: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
