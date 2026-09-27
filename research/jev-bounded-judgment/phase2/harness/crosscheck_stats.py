#!/usr/bin/env python3
"""Independent reimplementation of the Phase 2 headline statistics.

This is a CROSS-CHECK of `harness/score.py`, not a replacement. It recomputes
the reported numbers from `results/*.ndjson` WITHOUT importing score.py, so a
bug in the scorer's arithmetic or grouping shows up as a mismatch rather than
being reproduced identically by shared code.

It is NOT independent verification. It was written by the orchestrator, which
also wrote the harness. The independent verification of the statistics is
outstanding; see findings/verification-status.md.

Exit non-zero on any mismatch against the reported values.
"""
import json
import math
import os
import statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.dirname(HERE)

# Values as reported in findings/findings.md, independently re-derived here.
REPORTED = {
    "n_admissible": {"raw": 57, "struct": 52, "raw_ic": 57, "struct_ic": 52},
    "accuracy": {"raw": 0.8070, "struct": 0.8846,
                 "raw_ic": 0.7368, "struct_ic": 0.9038},
    "state_bytes_mean": {"raw": 32782, "struct": 17085,
                         "raw_ic": 60363, "struct_ic": 33748},
    "input_tokens_mean": {"raw": 7925, "struct": 5334,
                          "raw_ic": 15945, "struct_ic": 10179},
    "latency_median": {"raw": 337.8, "struct": 324.9,
                       "raw_ic": 386.1, "struct_ic": 344.2},
    "cost_total": {"raw": 0.018973, "struct": 0.011650,
                   "raw_ic": 0.038173, "struct_ic": 0.022230},
    "mcnemar_p": {"raw_vs_struct": 0.6875, "raw_ic_vs_struct_ic": 0.0654,
                  "raw_vs_raw_ic": 0.1250, "struct_vs_struct_ic": 1.0000},
    "noul_at_0_or_1": {"raw": 0, "struct": 0, "raw_ic": 0, "struct_ic": 0},
    "noul_near_half": {"raw": 7, "struct": 3, "raw_ic": 8, "struct_ic": 5},
    "ctype": {
        "nesting_conjunction": {"raw": 0.8, "struct": 0.8,
                                "raw_ic": 0.4, "struct_ic": 0.8},
        "unused_import": {"raw": 0.8, "struct": 0.6,
                          "raw_ic": 0.8, "struct_ic": 0.8},
        "string_literal_probe": {"raw": 0.40, "struct": None,
                                 "raw_ic": 0.40, "struct_ic": None},
    },
    "degradation": {"raw": {"lost": 4, "gained": 0},
                    "struct": {"lost": 1, "gained": 2}},
    "groups": {"judgment_under_both": {"n": 27, "raw": 0.7778,
                                       "struct": 0.8148},
               "lookup_under_struct": {"n": 25, "raw": 0.9200,
                                       "struct": 0.9600}},
    "unanswerable_answered": 40,
    "unanswerable_abstentions": 0,
}

COST_PER_MTOK = 0.042


def exact_mcnemar(a_only, b_only):
    n = a_only + b_only
    if n == 0:
        return 1.0
    k = min(a_only, b_only)
    p = 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(p, 1.0)


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def load_json(p):
    return json.load(open(p, encoding="utf-8"))


def main():
    rows = load(os.path.join(PHASE2, "results", "jev_raw.ndjson"))
    obs = load(os.path.join(PHASE2, "results", "jev_unanswerable_obs.ndjson"))
    cases = {c["case_id"]: c for c in
             load_json(os.path.join(PHASE2, "frozen", "cases.json"))}

    fails, checks = [], 0

    def chk(label, got, want, tol=0.0002):
        nonlocal checks
        checks += 1
        if want is None:
            return
        if got is None or abs(got - want) > tol:
            fails.append(f"{label}: recomputed={got} reported={want}")

    by = defaultdict(list)
    for r in rows:
        by[r["condition"]].append(r)

    # --- per-condition aggregates
    for cond, rs in by.items():
        adm = [r for r in rs if r["admissible"]]
        chk(f"n_admissible[{cond}]", len(adm), REPORTED["n_admissible"][cond])
        correct = [r for r in adm
                   if r["parsed"] and r["parsed"]["label"] == r["ground_truth"]]
        chk(f"accuracy[{cond}]", len(correct) / len(adm),
            REPORTED["accuracy"][cond])
        sb = [r["representation"]["state_bytes"] for r in adm]
        chk(f"state_bytes_mean[{cond}]", statistics.mean(sb),
            REPORTED["state_bytes_mean"][cond], tol=1.0)
        it = [(r.get("usage") or {}).get("input_tokens") for r in adm]
        it = [x for x in it if x]
        chk(f"input_tokens_mean[{cond}]", statistics.mean(it),
            REPORTED["input_tokens_mean"][cond], tol=1.0)
        lat = [r["latency_ms"] for r in adm if r["latency_ms"] is not None]
        chk(f"latency_median[{cond}]", round(statistics.median(lat), 1),
            REPORTED["latency_median"][cond], tol=0.15)
        chk(f"cost_total[{cond}]",
            round(sum(it) / 1e6 * COST_PER_MTOK, 6),
            REPORTED["cost_total"][cond], tol=0.000002)
        nouls = [r["parsed"]["noul"] for r in adm if r["parsed"]]
        chk(f"noul_at_0_or_1[{cond}]",
            sum(1 for v in nouls if v <= 0.0 or v >= 1.0),
            REPORTED["noul_at_0_or_1"][cond])
        chk(f"noul_near_half[{cond}]",
            sum(1 for v in nouls if 0.4 <= v <= 0.6),
            REPORTED["noul_near_half"][cond])

    # --- per-ctype accuracy
    for ct, percond in REPORTED["ctype"].items():
        for cond, want in percond.items():
            if want is None:
                continue
            adm = [r for r in by[cond]
                   if r["ctype"] == ct and r["admissible"]]
            if not adm:
                fails.append(f"ctype[{ct}|{cond}]: no admissible cells")
                continue
            c = sum(1 for r in adm
                    if r["parsed"]["label"] == r["ground_truth"])
            chk(f"ctype[{ct}|{cond}]", round(c / len(adm), 4), want, tol=0.001)

    # --- paired McNemar
    def correct_map(cond):
        return {r["case_id"]: (r["parsed"] is not None
                               and r["parsed"]["label"] == r["ground_truth"])
                for r in by[cond] if r["admissible"] and r["parsed"]}

    pairs = [("raw_vs_struct", "raw", "struct"),
             ("raw_ic_vs_struct_ic", "raw_ic", "struct_ic"),
             ("raw_vs_raw_ic", "raw", "raw_ic"),
             ("struct_vs_struct_ic", "struct", "struct_ic")]
    for name, a, b in pairs:
        A, B = correct_map(a), correct_map(b)
        sh = sorted(set(A) & set(B))
        ao = sum(1 for c in sh if A[c] and not B[c])
        bo = sum(1 for c in sh if B[c] and not A[c])
        chk(f"mcnemar_p[{name}]", round(exact_mcnemar(ao, bo), 4),
            REPORTED["mcnemar_p"][name], tol=0.0005)

    # --- distraction degradation
    for base, want in REPORTED["degradation"].items():
        A, B = correct_map(base), correct_map(base + "_ic")
        sh = sorted(set(A) & set(B))
        lost = sum(1 for c in sh if A[c] and not B[c])
        gained = sum(1 for c in sh if B[c] and not A[c])
        chk(f"degradation[{base}].lost", lost, want["lost"])
        chk(f"degradation[{base}].gained", gained, want["gained"])

    # --- intrinsic case groups, recomputed from the frozen case set
    def group(cid):
        cl = cases[cid]["classification"]
        if cl.get("struct") == "lookup":
            return "lookup_under_struct"
        if cl.get("struct") == "unanswerable" or cl.get("raw") == "unanswerable":
            return "raw_only"
        return "judgment_under_both"

    for g, want in REPORTED["groups"].items():
        a = correct_map("raw")
        b = correct_map("struct")
        ids = [c for c in set(a) & set(b) if group(c) == g]
        chk(f"groups[{g}].n", len(ids), want["n"])
        chk(f"groups[{g}].raw", round(sum(a[c] for c in ids) / len(ids), 4),
            want["raw"], tol=0.001)
        chk(f"groups[{g}].struct", round(sum(b[c] for c in ids) / len(ids), 4),
            want["struct"], tol=0.001)

    # --- no unanswerable cell was ever scored
    bad = [r["case_id"] for r in rows
           if r["ground_truth"] is None and r.get("correct") is True]
    checks += 1
    if bad:
        fails.append(f"unanswerable cells scored correct: {bad[:5]}")
    na_with_answer = [r["case_id"] for r in rows
                      if r["typed_error"] == "not_admissible" and r["parsed"]]
    checks += 1
    if na_with_answer:
        fails.append(f"not_admissible cells carry a parsed answer: "
                     f"{na_with_answer[:5]}")

    # --- unanswerable observation behaviour
    oc = [r for r in obs if r.get("observation_only")]
    answered = sum(1 for r in oc if r["parsed"])
    chk("unanswerable_answered", answered, REPORTED["unanswerable_answered"])
    abst = sum(1 for r in oc if r["parsed"]
               and r["parsed"].get("label") is None)
    chk("unanswerable_abstentions", abst, REPORTED["unanswerable_abstentions"])
    for cond in ("raw", "struct", "raw_ic", "struct_ic"):
        for ct, want_decided in (("unanswerable_runtime", 0),
                                 ("unanswerable_semantic", None)):
            v = [r["parsed"]["noul"] for r in oc
                 if r["condition"] == cond and r["ctype"] == ct and r["parsed"]]
            dec = sum(1 for x in v if abs(x - 0.5) > 0.2)
            if want_decided is not None:
                chk(f"decided[{cond}|{ct}]", dec, want_decided)

    print(f"checks run      : {checks}")
    print(f"mismatches      : {len(fails)}")
    for f in fails:
        print("  MISMATCH", f)
    if fails:
        print("\nCROSS-CHECK FAILED")
        return 1
    print("\nCROSS-CHECK OK: every reported statistic re-derived independently "
          "of harness/score.py")
    print("NOTE: this is an orchestrator-side cross-check, NOT independent "
          "verification. See findings/verification-status.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
