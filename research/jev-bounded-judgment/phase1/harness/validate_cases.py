#!/usr/bin/env python3
"""Deterministic structural validator for cases.ndjson.

Structural only. Performs no network I/O, no model calls, and no scoring. It
checks the MUST constraints declared in schema.md so that a malformed corpus
fails loudly before any budget is spent on the raw run.

Exit code 0 = all checks PASS, 1 = at least one FAIL.

Usage:
    python3 harness/validate_cases.py [path/to/cases.ndjson]
    python3 harness/validate_cases.py --check-reproducible
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from routing_policy import ROLES, compute_legality  # noqa: E402

AREAS = ("A", "B", "C", "D")
SPLITS = ("train", "dev", "test")
DIFFICULTIES = ("easy", "medium", "hard")
VARIANT_KINDS = ("base", "distractor", "irrelevant_change", "missing_evidence",
                 "noise", "opaque_labels", "option_reorder")
QTYPES = ("noul", "choice", "score")
NUL_LABELS = ("no", "yes")

CASE_REQUIRED = ("schema_version", "id", "area", "split", "difficulty",
                 "difficulty_note", "state", "questions", "ground_truth",
                 "control", "routing", "provenance")
GT_REQUIRED = ("answerable", "answer", "probabilities", "rationale",
               "deciding_fact", "abstain_expected", "abstain_acceptable")
CTL_REQUIRED = ("pair_id", "variant_kind", "base_case_id", "deciding_fact",
                "label_map", "option_order", "perturbation_seed")
PROV_REQUIRED = ("template_id", "generator", "generator_version", "synthetic",
                 "contains_personal_content", "contains_secrets")

# Cheap, deliberately narrow leak scan. Not a substitute for human review.
SECRET_PATTERNS = ("sk-", "bearer ", "api_key", "apikey", "password",
                   "secret", "-----begin", "authorization:")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    return bool(ok)


def label_set(case):
    """Real-world label set for a case, after mapping opaque keys back."""
    q = case["questions"][0]
    lm = case["control"].get("label_map") or None
    if q["type"] == "noul":
        return set(NUL_LABELS)
    if q["type"] == "choice":
        keys = set(q["criteria"].keys())
        if lm:
            return {lm[k] for k in keys}
        return keys
    return set(q["criteria"])


def load(path):
    cases = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"FATAL: {path}:{ln} invalid JSON: {e}")
    return cases


def validate(cases):
    # --- C1 count ---------------------------------------------------------
    n = len(cases)
    check("C1_count_within_60_plus_minus_5", 55 <= n <= 65, f"n={n}")
    by_area = {a: sum(1 for c in cases if c["area"] == a) for a in AREAS}
    check("C1_every_area_present", all(v > 0 for v in by_area.values()),
          str(by_area))
    by_split = {s: sum(1 for c in cases if c["split"] == s) for s in SPLITS}
    check("C1_every_split_present", all(v > 0 for v in by_split.values()),
          str(by_split))

    # --- C2 required fields ----------------------------------------------
    missing = []
    for c in cases:
        for k in CASE_REQUIRED:
            if k not in c:
                missing.append(f"{c.get('id','?')}.{k}")
        for k in GT_REQUIRED:
            if k not in c.get("ground_truth", {}):
                missing.append(f"{c.get('id','?')}.ground_truth.{k}")
        for k in CTL_REQUIRED:
            if k not in c.get("control", {}):
                missing.append(f"{c.get('id','?')}.control.{k}")
        for k in PROV_REQUIRED:
            if k not in c.get("provenance", {}):
                missing.append(f"{c.get('id','?')}.provenance.{k}")
    check("C2_all_required_fields_present", not missing,
          f"{len(missing)} missing: {missing[:6]}")

    # --- C3 identity / ordering -----------------------------------------
    ids = [c["id"] for c in cases]
    check("C3_ids_unique", len(ids) == len(set(ids)),
          f"{len(ids) - len(set(ids))} dupes")
    check("C3_ids_sorted_ascending", ids == sorted(ids))
    check("C3_schema_version_uniform",
          {c["schema_version"] for c in cases} == {"jevp1-case-1.0"})

    # --- C4 enums --------------------------------------------------------
    bad = []
    for c in cases:
        if c["area"] not in AREAS:
            bad.append(f"{c['id']}:area={c['area']}")
        if c["split"] not in SPLITS:
            bad.append(f"{c['id']}:split={c['split']}")
        if c["difficulty"] not in DIFFICULTIES:
            bad.append(f"{c['id']}:difficulty={c['difficulty']}")
        if c["control"]["variant_kind"] not in VARIANT_KINDS:
            bad.append(f"{c['id']}:variant_kind={c['control']['variant_kind']}")
        for q in c["questions"]:
            if q["type"] not in QTYPES:
                bad.append(f"{c['id']}:qtype={q['type']}")
    check("C4_enum_values_valid", not bad, f"{bad[:6]}")

    # --- C5 question shape vs criteria container -------------------------
    bad = []
    for c in cases:
        qs = c["questions"]
        if not qs:
            bad.append(f"{c['id']}:no questions")
            continue
        qids = [q["qid"] for q in qs]
        if len(qids) != len(set(qids)):
            bad.append(f"{c['id']}:duplicate qid")
        q = qs[0]
        if not isinstance(q.get("instructions"), str) or not q["instructions"].strip():
            bad.append(f"{c['id']}:empty instructions")
        cr = q.get("criteria")
        if q["type"] == "noul" and cr is not None:
            bad.append(f"{c['id']}:noul must have criteria=null")
        if q["type"] == "choice" and not isinstance(cr, dict):
            bad.append(f"{c['id']}:choice criteria must be a dict")
        if q["type"] == "score" and not isinstance(cr, list):
            bad.append(f"{c['id']}:score criteria must be a list")
    check("C5_criteria_container_matches_type", not bad, f"{bad[:6]}")

    # --- C6 ground-truth coherence ---------------------------------------
    bad = []
    for c in cases:
        gt = c["ground_truth"]
        labels = label_set(c)
        if not isinstance(gt["answerable"], bool):
            bad.append(f"{c['id']}:answerable not bool")
        if not isinstance(gt["abstain_expected"], bool):
            bad.append(f"{c['id']}:abstain_expected not bool")
        if gt["answerable"]:
            if gt["answer"] is None:
                bad.append(f"{c['id']}:answerable but answer=null")
            elif gt["answer"] not in labels:
                bad.append(f"{c['id']}:answer {gt['answer']!r} not in {labels}")
            if gt["answer"] is not None and c["questions"][0]["type"] == "score":
                if gt["answer"] not in c["questions"][0]["criteria"]:
                    bad.append(f"{c['id']}:score answer not in criteria")
        else:
            if gt["answer"] is not None:
                bad.append(f"{c['id']}:unanswerable but answer!=null")
            if not gt["abstain_expected"]:
                bad.append(f"{c['id']}:unanswerable but abstain_expected=false")
        if not (gt["rationale"] or "").strip():
            bad.append(f"{c['id']}:empty rationale")
        if not (gt["deciding_fact"] or "").strip():
            bad.append(f"{c['id']}:empty deciding_fact")
        if not (c["control"]["deciding_fact"] or "").strip():
            bad.append(f"{c['id']}:empty control.deciding_fact")
    check("C6_ground_truth_coherent", not bad, f"{bad[:6]}")

    # --- C7 provenance / no-leak flags ------------------------------------
    bad = [c["id"] for c in cases
           if not c["provenance"]["synthetic"]
           or c["provenance"]["contains_personal_content"]
           or c["provenance"]["contains_secrets"]
           or not c["provenance"]["template_id"]]
    check("C7_provenance_flags_clean", not bad, f"{bad[:6]}")

    leaks = []
    for c in cases:
        blob = c["state"] + " " + c["questions"][0]["instructions"]
        low = blob.lower()
        for p in SECRET_PATTERNS:
            if p in low:
                leaks.append(f"{c['id']}:{p}")
    check("C7_no_secret_like_tokens_in_visible_text", not leaks, f"{leaks[:6]}")

    # --- C8 control family integrity -------------------------------------
    by_id = {c["id"]: c for c in cases}
    bad = []
    for c in cases:
        ctl = c["control"]
        bcid = ctl["base_case_id"]
        vk = ctl["variant_kind"]
        if vk == "base":
            if bcid is not None:
                bad.append(f"{c['id']}:base with base_case_id={bcid}")
            if not (ctl["pair_id"] or "").strip():
                bad.append(f"{c['id']}:base with empty pair_id")
            # pair_id may be the case's own id (singleton family) or a shared
            # family id (a contrastive pair). The family shape itself is
            # checked in C9, so only emptiness is a structural failure here.
        else:
            if bcid is None:
                bad.append(f"{c['id']}:variant without base_case_id")
            elif bcid not in by_id:
                bad.append(f"{c['id']}:base_case_id {bcid} does not exist")
            else:
                base = by_id[bcid]
                if base["split"] != c["split"]:
                    bad.append(f"{c['id']}:family spans splits "
                               f"({c['split']} vs {base['split']})")
                if base["control"]["variant_kind"] != "base":
                    bad.append(f"{c['id']}:base_case_id {bcid} is itself a "
                               f"variant")
    check("C8_control_family_integrity", not bad, f"{bad[:8]}")

    # --- C9 contrastive pairs: opposite answers, same everything else ----
    fams = {}
    for c in cases:
        if c["area"] == "C" and c["control"]["variant_kind"] == "base":
            fams.setdefault(c["control"]["pair_id"], []).append(c)
    bad = []
    for pid, members in fams.items():
        if len(members) != 2:
            bad.append(f"{pid}: {len(members)} members, expected 2")
            continue
        m1, m2 = members
        if m1["split"] != m2["split"]:
            bad.append(f"{pid}: members in different splits")
        a1, a2 = m1["ground_truth"]["answer"], m2["ground_truth"]["answer"]
        if a1 == a2:
            bad.append(f"{pid}: both members have answer {a1!r}")
        if m1["questions"][0]["instructions"] != m2["questions"][0]["instructions"]:
            bad.append(f"{pid}: members ask different questions")
        if m1["difficulty"] != m2["difficulty"]:
            bad.append(f"{pid}: members have different difficulty")
        # The ONLY textual difference must be the deciding fact: same sentence
        # count, same length within a sane band, and both states of identical
        # length after the fact substitution is removed.
        if m1["state"].count(".") != m2["state"].count("."):
            bad.append(f"{pid}: sentence counts differ")
        s1, s2 = m1["state"], m2["state"]
        if abs(len(s1) - len(s2)) > 120:
            bad.append(f"{pid}: state length delta {abs(len(s1)-len(s2))} > 120")
    n_pairs = len(fams)
    check("C9_contrastive_pairs_wellformed", not bad,
          f"pairs={n_pairs} {bad[:8]}")
    check("C9_at_least_4_contrastive_pairs", n_pairs >= 4, f"pairs={n_pairs}")

    # --- C10 per-kind control invariants ----------------------------------
    bad = []
    counts = {k: 0 for k in VARIANT_KINDS}
    for c in cases:
        ctl = c["control"]
        vk = ctl["variant_kind"]
        counts[vk] += 1
        if vk == "base":
            continue
        base = by_id[ctl["base_case_id"]]
        bq, cq = base["questions"][0], c["questions"][0]
        if vk in ("option_reorder", "opaque_labels"):
            if c["state"] != base["state"]:
                bad.append(f"{c['id']}:state must be identical to base")
            if c["ground_truth"]["answer"] != base["ground_truth"]["answer"]:
                bad.append(f"{c['id']}:answer changed vs base")
            bkeys = set(bq["criteria"].keys())
            if vk == "option_reorder":
                if set(cq["criteria"].keys()) != bkeys:
                    bad.append(f"{c['id']}:reorder changed the key set")
                elif list(cq["criteria"].keys()) == list(bq["criteria"].keys()):
                    bad.append(f"{c['id']}:reorder did not change the order")
                if not ctl["option_order"]:
                    bad.append(f"{c['id']}:reorder without option_order")
            else:  # opaque_labels
                lm = ctl["label_map"]
                if not lm:
                    bad.append(f"{c['id']}:opaque without label_map")
                    continue
                if set(lm.keys()) != set(cq["criteria"].keys()):
                    bad.append(f"{c['id']}:label_map keys != criteria keys")
                if {lm[k] for k in lm} != bkeys:
                    bad.append(f"{c['id']}:label_map values != base key set")
                if len(set(lm.values())) != len(lm):
                    bad.append(f"{c['id']}:label_map is not injective")
                for ok_, nk in lm.items():
                    if cq["criteria"][ok_] != bq["criteria"][nk]:
                        bad.append(f"{c['id']}:label text changed for {nk}")
        elif vk == "distractor":
            if not c["state"].startswith(base["state"]):
                bad.append(f"{c['id']}:state does not extend base state")
            elif c["state"] == base["state"]:
                bad.append(f"{c['id']}:distractor added nothing")
            if c["ground_truth"]["answer"] != base["ground_truth"]["answer"]:
                bad.append(f"{c['id']}:answer changed vs base")
        elif vk == "missing_evidence":
            if c["ground_truth"]["answerable"]:
                bad.append(f"{c['id']}:missing_evidence but answerable")
            if c["ground_truth"]["answer"] is not None:
                bad.append(f"{c['id']}:missing_evidence but answer!=null")
            if not c["ground_truth"]["abstain_expected"]:
                bad.append(f"{c['id']}:missing_evidence but not abstain")
            # Evidence must actually have been removed, not merely relabelled.
            if len(c["state"]) >= len(base["state"]):
                bad.append(f"{c['id']}:missing_evidence state did not shrink "
                           f"({len(c['state'])} >= {len(base['state'])})")
            if c["state"] == base["state"]:
                bad.append(f"{c['id']}:missing_evidence removed nothing")
        elif vk == "noise":
            if c["state"] == base["state"]:
                bad.append(f"{c['id']}:noise changed nothing")
            if c["ground_truth"]["answer"] != base["ground_truth"]["answer"]:
                bad.append(f"{c['id']}:answer changed vs base")
            if ctl["perturbation_seed"] is None:
                bad.append(f"{c['id']}:noise without perturbation_seed")
            if c["ground_truth"]["answerable"] != \
                    base["ground_truth"]["answerable"]:
                bad.append(f"{c['id']}:answerability changed vs base")
        elif vk == "irrelevant_change":
            if base["area"] != "C":
                bad.append(f"{c['id']}:irrelevant_change base not in area C")
            if not c["state"].startswith(base["state"]):
                bad.append(f"{c['id']}:state does not extend base state")
            if c["ground_truth"]["answer"] != base["ground_truth"]["answer"]:
                bad.append(f"{c['id']}:answer must equal base answer")
    check("C10_control_kind_invariants", not bad, f"{bad[:8]}")

    # --- C11 control coverage: all seven kinds represented ---------------
    missing_kinds = [k for k, v in counts.items() if v == 0]
    check("C11_all_seven_variant_kinds_present", not missing_kinds,
          f"counts={ {k: v for k, v in sorted(counts.items())} }")
    for k in ("option_reorder", "opaque_labels", "distractor",
              "missing_evidence", "noise", "irrelevant_change"):
        check(f"C11_kind_{k}_has_at_least_one", counts[k] >= 1,
              f"count={counts[k]}")

    # --- C12 routing legality recomputation ------------------------------
    bad = []
    multi_legal = 0
    for c in cases:
        r = c.get("routing")
        if c["area"] == "D":
            if r is None:
                bad.append(f"{c['id']}:area D without routing block")
                continue
            recomputed = compute_legality(r["signals"])
            for k in ("policy_rule_id", "legal_roles", "illegal_roles",
                      "expected_role"):
                if recomputed[k] != r[k]:
                    bad.append(f"{c['id']}:{k} stored {r[k]!r} != recomputed "
                               f"{recomputed[k]!r}")
            if sorted(r["legal_roles"] + r["illegal_roles"]) != sorted(ROLES):
                bad.append(f"{c['id']}:legal+illegal != all six roles")
            if not r["illegal_roles"]:
                bad.append(f"{c['id']}:no illegal candidate")
            if len(r["legal_roles"]) > 1:
                multi_legal += 1
            # All six roles must be offered as candidates on every routing
            # case, and the label text must be the canonical role text.
            from routing_policy import ROLE_LABEL
            vals = set(c["questions"][0]["criteria"].values())
            if vals != set(ROLE_LABEL.values()):
                bad.append(f"{c['id']}:criteria labels are not the canonical "
                           f"role set")
            lm = c["control"].get("label_map")
            if not lm and set(c["questions"][0]["criteria"].keys()) != set(ROLES):
                bad.append(f"{c['id']}:unmapped criteria keys != six roles")
            if lm and set(lm.values()) != set(ROLES):
                bad.append(f"{c['id']}:label_map does not cover six roles")
            if c["ground_truth"]["answer"] != r["expected_role"]:
                bad.append(f"{c['id']}:answer != expected_role")
        elif r is not None:
            bad.append(f"{c['id']}:routing block outside area D")
    check("C12_routing_legality_recomputes", not bad, f"{bad[:8]}")
    check("C12_at_least_two_multi_legal_routing_cases", multi_legal >= 2,
          f"multi_legal={multi_legal}")

    # --- C13 train split supports a measured prior ------------------------
    tr = [c for c in cases if c["split"] == "train" and
          c["questions"][0]["type"] == "noul" and
          c["ground_truth"]["answerable"]]
    labs = [c["ground_truth"]["answer"] for c in tr]
    check("C13_train_split_supports_majority_prior", len(labs) >= 6 and labs,
          f"n={len(labs)} yes={labs.count('yes')} no={labs.count('no')}")

    # --- C14 abstain / answerable coverage -------------------------------
    unans = [c for c in cases if not c["ground_truth"]["answerable"]]
    abst = [c for c in cases if c["ground_truth"]["abstain_expected"]]
    check("C14_unanswerable_cases_present", len(unans) >= 10, f"n={len(unans)}")
    check("C14_unanswerable_per_area",
          all(any(c["area"] == a and not c["ground_truth"]["answerable"]
                  for c in cases) for a in ("A", "B")),
          "areas A and B each carry unanswerable cases")
    check("C14_abstain_expected_subset_of_unanswerable",
          set(c["id"] for c in abst) == set(c["id"] for c in unans),
          f"abstain={len(abst)} unanswerable={len(unans)}")

    return by_area, by_split, counts


def check_reproducible(cases_path):
    """Regenerate the corpus and compare sha256.

    The on-disk corpus is backed up and restored unconditionally, so this check
    can never destroy the corpus it is verifying even if the generator is
    non-deterministic.
    """
    target = os.path.join(ROOT, "cases.ndjson")
    before = sha256(cases_path)
    with open(target, "rb") as f:
        backup = f.read()
    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, "gen_cases.py")],
                           cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            return False, f"generator failed: {p.stderr.strip()[:200]}"
        after = sha256(target)
    finally:
        with open(target, "wb") as f:
            f.write(backup)
    restored = sha256(target) == before
    return (before == after) and restored, \
        f"on-disk={before[:16]} regenerated={after[:16]} restored={restored}"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0] if args else os.path.join(ROOT, "cases.ndjson")
    repro = "--check-reproducible" in sys.argv

    cases = load(path)
    by_area, by_split, counts = validate(cases)

    if repro:
        ok, detail = check_reproducible(path)
        check("C15_generator_reproducible", ok, detail)

    width = max(len(n) for n, _, _ in RESULTS)
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    print("=" * (width + 20))
    print(f"validate_cases.py  {path}")
    print(f"cases={len(cases)}  sha256={sha256(path)[:32]}")
    print(f"by_area={by_area}  by_split={by_split}")
    print(f"variant_kinds={counts}")
    print("=" * (width + 20))
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
    print("=" * (width + 20))
    print(f"{npass}/{len(RESULTS)} checks passed")
    failed = [n for n, ok, _ in RESULTS if not ok]
    if failed:
        print("FAILED CHECKS: " + ", ".join(failed))
        return 1
    print("VALIDATOR RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
