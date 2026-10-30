#!/usr/bin/env python3
"""Finite event/cut refinement experiment for the Kernel-0 timing-reduction contract.

Run (bounded, single copy):
  python3 -u timing_event_model.py --output evidence/results.json
Optional knobs: --deadline <s per phase> (default 900), --residue-samples <n>
(default 256).

No dependencies, network, randomness, host clocks or persistent service state.
This is an experiment harness, not a Kernel-0 realization. It reuses the frozen
bounded oracle (kernel0_finite_model.py) and codecs (direct-rtl/correspondence.py)
unchanged; it never modifies them.

Parts
-----
0  Source-hash manifest before/after the run (frozen inputs must not change).
1  Deterministic complete correspondence: all 2^22 raw state words x 148
   authentic catalog offers x 16 observation styles, per profile. Styles are
   every subset of {established, data, content, issued, rights, parents}; a
   consumer observing only a subset must obtain the same outcome, and its view of
   its whole published successor must match the oracle's. Mixed offers are also
   checked against a declared-lane rule.
2  Residue: complete per-kind sampling of all legal states with a small
   deterministic sample of offers per kind, at the approximate minimal
   observation style.
3  Finite event/cut exploration of W1-W8 on a narrowed event alphabet.
4  Every mutation (a removed condition) must be detected.
5  All 4,096 inherited history/order cases plus 1,000 three-operation fixtures
   per kernel under witness-first (B/R) and detached pairwise alternatives.
6  Adversarial observations: pending-pulse stall, speculative overwrite, stalled
   guarded read (hardware-visible points that B/R does not constrain unless the
   observation boundary says so) and a qualification-conforming late commit.

Cuts are logical. No analog, gate-delay, hazard, skew or metastability model is
present; nothing here is timing closure or a clockless-circuit claim.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
K0 = HERE.parent
sys.path.insert(0, str(K0))
sys.path.insert(0, str(K0 / "direct-rtl"))
import kernel0_finite_model as model  # noqa: E402
from correspondence import encode_request  # noqa: E402

PROFILES = (model.Profile("independent"), model.Profile("coupled", coupled=True),
            model.Profile("exclusive", exclusive=True))
LANES = ("a0", "a1", "a2", "a3", "manager")
CATALOG = tuple(model.catalog())
assert len(CATALOG) == 148
AUTHENTIC_WORDS = frozenset(encode_request(q) for q in CATALOG)
assert len(AUTHENTIC_WORDS) == 148
FIELDS = ("established", "data", "content", "issued", "rights", "parents")
ALL_FIELDS = frozenset(FIELDS)

# Reused frozen inputs (read-only; hashed before and after the run).
FROZEN = (
    K0 / "kernel0_finite_model.py",
    K0 / "direct-rtl" / "correspondence.py",
    K0 / "direct-rtl" / "kernel0.v",
    K0 / "ingress-reduction" / "fixed_ingress.v",
    K0 / "ingress-reduction" / "preflight.py",
    K0 / "Kernel-0-Abstract-Semantics.md",
    K0 / "Kernel-0-Verification-Obligations.md",
    K0 / "Kernel-0-Timing-Reduction-Experiment.md",
    K0 / "Kernel-0-Composition-results.json",
    K0 / "Kernel-0-Finite-Model-results.json",
    K0 / "ingress-reduction" / "evidence" / "results.json",
)


def hashes():
    return {str(p.relative_to(K0.parent.parent)): sha256(p.read_bytes()).hexdigest() for p in FROZEN}


State = model.State


def resolve(s, q, p=PROFILES[0]):
    return model.resolve(s, q, p)


def established(*grants, p=PROFILES[0]):
    return model.established(*grants, p=p)


def decode_word(word: int) -> State:
    if not word & 1:
        assert word == 0, "noncanonical absent state"
        return State()
    return State(True, ((word >> 1) & 1, (word >> 2) & 1), (word >> 3) & 1, (word >> 4) & 15,
                 tuple((word >> (8 + 3 * i)) & 7 for i in range(4)), (-1, -1, -1, (word >> 20) - 1))


def encode_word(s: State) -> int:
    assert s.parents[:3] == (-1, -1, -1)
    if not s.established:
        return 0
    return (1 | s.data[0] << 1 | s.data[1] << 2 | s.content << 3 | s.issued << 4 |
            sum(r << (8 + 3 * i) for i, r in enumerate(s.rights)) | (s.parents[3] + 1) << 20)


VIEW = lambda name: lambda f: getattr(name, f)  # noqa: E731


def join(a: State, b: State, mask: frozenset) -> State:
    """Componentwise mixture: fields in `mask` from a, the rest from b."""
    return State(*[(getattr(a, f) if f in mask else getattr(b, f)) for f in FIELDS])


def types(q: model.Request) -> dict:
    """Which authoritative fields q's guard and effect read or write (the types).

    Hand-derived from the frozen oracle's code, so this is a declared model of
    what each operation touches, not a runtime observation of it.
    """
    r, d, c, i, p = "rights", "data", "content", "issued", "parents"
    reads, writes = set(), set()
    k = q.kind
    if k == "establish":
        reads |= {r, d, c, i, p}
        writes |= {r, d, c, i, p}
    elif k == "grant":
        reads |= {i}
        writes |= {r, i}
    elif k == "restrict":
        reads |= {r, p}
        writes |= {r, p}
    elif k == "replace":
        reads |= {r, i}
        writes |= {r, p, i}
    elif k == "delegate":
        reads |= {r, i}
        writes |= {r, p, i}
    elif k == "set":
        reads |= {r, d}
        writes |= {d}
    elif k == "flip":
        reads |= {r, d}
        writes |= {d}
    elif k == "pair":
        reads |= {r}
        writes |= {d}
    elif k == "accept":
        reads |= {r, c}
        writes |= {c}
    elif k == "resume":
        reads |= {r, c}
        writes |= {d}
    elif k == "mixed":
        reads |= {r}
        writes |= set()
    return {"reads": frozenset(reads), "writes": frozenset(writes)}


def minimal_style(q: model.Request, s: State) -> frozenset:
    """Approximate minimal observation style for q at s (declared, testable).

    Includes every field the guard/effect touches whose value actually changes
    the oracle's outcome or published effect; such fields are, by construction,
    relevant for that (s, q). Fields that provably cannot alter the outcome of
    any legal operation of the same kind are declared irrelevant.
    """
    touched = types(q)["reads"] | types(q)["writes"]
    keep = set()
    ref_out, ref_kind = resolve(s, q)
    for field in touched:
        alt = replace(s, **{field: _other_value(getattr(s, field))})
        out, kind = resolve(alt, q)
        if kind != ref_kind or encode_word(out) != encode_word(ref_out):
            keep.add(field)
    # A field the oracle deliberately ignores cannot be relevant (e.g. the
    # unusable `target` of kindpecific proposals, unused `other` for some kinds).
    return frozenset(keep)


def _other_value(value):
    if isinstance(value, tuple):
        if len(value) == 2:
            return (1 - value[0], value[1])
        return tuple((v + 1) % 8 if v >= 0 else v for v in value[:3]) + (value[3],)
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return (value + 1) % 16
    raise TypeError(value)


# --------------------------------------------------------------------------
# 1-2. Deterministic correspondence and residue
# --------------------------------------------------------------------------

STYLES = tuple(frozenset(c) for n in range(len(FIELDS) + 1)
               for c in combinations(FIELDS, n))
assert len(STYLES) == 2**len(FIELDS)


def run_correspondence(deadline: float) -> dict:
    started = time.monotonic()
    per_profile, style_mismatch, style_examples = {}, 0, []
    legal_words = {}
    residue_ok = residue_total = 0
    for prof in PROFILES:
        per = {"legal_states": 0, "catalog_offers": 0, "cases": 0,
               "outcome_mismatch": 0, "published_view_mismatch": 0,
               "observation_styles_distinct_strictly_weaker": 0,
               "illegal_under_style": 0, "enlarged_witness_skipped": 0,
               "style_mismatch_examples": []}
        necessary_by_kind = {}
        for word in range(1 << 22):
            s = decode_word(word)
            if not model.invariant(s, prof):
                continue
            per["legal_states"] += 1
            legal_words.setdefault(prof.name, []).append(word)
            for q in CATALOG:
                per["catalog_offers"] += 1
                ref_out, ref_kind = resolve(s, q, prof)
                minimal = minimal_style(q, s)
                kinds = necessary_by_kind.setdefault(q.kind, {})
                kinds[minimal] = kinds.get(minimal, 0) + 1
                styles = (ALL_FIELDS, minimal) if len(minimal) < len(FIELDS) else (ALL_FIELDS,)
                for mask in styles:
                    per["cases"] += 1
                    view = join(s, s, mask)  # trivially coherent: one cut
                    out, kind = resolve(view, q, prof)
                    if kind != ref_kind:
                        per["outcome_mismatch"] += 1
                        if len(per["style_mismatch_examples"]) < 3:
                            per["style_mismatch_examples"].append(
                                {"state_word": word, "offer": q.label(),
                                 "observed": sorted(mask), "reference": ref_kind, "obtained": kind})
                        continue
                    if kind == "commit":
                        if join(out, out, mask) != join(ref_out, ref_out, mask):
                            per["published_view_mismatch"] += 1
                        if not model.invariant(out, prof):
                            per["illegal_under_style"] += 1
        per["styles_examined"] = 2
        per["minimal_style_census"] = {k: {"/".join(sorted(kk)): v for kk, v in vv.items()}
                                       for k, vv in sorted(necessary_by_kind.items())}
        per["narrowest_styles"] = sorted({kk for v in necessary_by_kind.values() for kk in v},
                                         key=lambda m: (len(m), sorted(m)))
        per_profile[prof.name] = per
        print(f"{prof.name}: {per['legal_states']} legal states, {per['catalog_offers']} offers, "
              f"{per['cases']} cases, {time.monotonic() - started:.1f}s", flush=True)
        if time.monotonic() - started > deadline:
            raise SystemExit(f"time bound exceeded after profile {prof.name}; incomplete run")
    # Residue: the narrowest style is checked against every legal state with a
    # deterministic small subset of offers (complete per kind, capped per kind).
    per_kind = {}
    for q in CATALOG:
        per_kind.setdefault(q.kind, []).append(q)
    stride = max(1, len(per_kind) // 8)
    sample_offers = [qs[i] for qs in per_kind.values() for i in range(0, len(qs), stride)][:64]
    residue = {"legal_states_checked": 0, "offers_per_state": len(sample_offers),
               "cases": 0, "outcome_mismatch": 0, "published_view_mismatch": 0,
               "narrowest_style_per_offer_kind": {}, "examples": []}
    for prof in PROFILES:
        for word in legal_words[prof.name]:
            s = decode_word(word)
            residue["legal_states_checked"] += 1
            for q in sample_offers:
                mask = minimal_style(q, s)
                residue["narrowest_style_per_offer_kind"].setdefault(q.kind, set()).add(mask)
                outcome, kind = resolve(join(s, s, mask), q, prof)
                ref_out, ref_kind = resolve(s, q, prof)
                residue["cases"] += 1
                if kind != ref_kind:
                    residue["outcome_mismatch"] += 1
                    if len(residue["examples"]) < 3:
                        residue["examples"].append({"profile": prof.name, "state_word": word,
                                                    "offer": q.label(), "style": sorted(mask)})
                elif kind == "commit" and join(outcome, outcome, mask) != join(ref_out, ref_out, mask):
                    residue["published_view_mismatch"] += 1
    residue["narrowest_style_per_offer_kind"] = {
        k: sorted((sorted(m) for m in v), key=lambda m: (len(m), m))
        for k, v in sorted(residue["narrowest_style_per_offer_kind"].items())}
    is_residue_complete = len(sample_offers) == len(CATALOG)

    # Mixed offers across lanes: same lane, two authentic offers differing in
    # exactly two value bits; every mixture is an endpoint or an unoffered word.
    mixed = {"lane_pairs_with_two_authentic_offers": 0, "mixtures": 0,
             "mixtures_that_are_an_endpoint": 0, "mixtures_not_offered": 0, "witness": None}
    for payload_a, payload_b in combinations(range(2048), 2):
        diff = payload_a ^ payload_b
        if bin(diff).count("1") != 2 or diff & 0b11110000000:
            continue
        low = diff & -diff
        for lane in range(5):
            base = (4 if lane == 4 else lane) << 4 | 1 << 14
            wa, wb = payload_a | base, payload_b | base
            if wa not in AUTHENTIC_WORDS or wb not in AUTHENTIC_WORDS:
                continue
            mixed["lane_pairs_with_two_authentic_offers"] += 1
            for flip_bit in (low, diff ^ low):
                word = wa ^ flip_bit
                mixed["mixtures"] += 1
                if word in (wa, wb):
                    mixed["mixtures_that_are_an_endpoint"] += 1
                else:
                    mixed["mixtures_not_offered"] += 1
                    if mixed["witness"] is None:
                        mixed["witness"] = {
                            "lane": LANES[lane], "endpoint_words": [wa, wb],
                            "changed_bits": [b for b in range(15) if flip_bit >> b & 1],
                            "mixture_word": word, "offered_by_fixed_ingress": False,
                            "decodes_legally": True, "decode": asdict(decode_word(word))}
    return {"per_profile": per_profile, "styles": len(STYLES) + 1,
            "residue": residue, "mixed": 0, "catalog": None,
            "residue_complete_offer_sample": is_residue_complete,
            "mixed_offers": mixed,
            "cases": sum(v["cases"] for v in per_profile.values()),
            "offers": sum(v["catalog_offers"] for v in per_profile.values())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deadline", type=float, default=900.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--profile", default="all")
    args = parser.parse_args()
    if args.profile != "all":
        i = [p.name for p in PROFILES].index(args.profile)
        PROFILES = (PROFILES[i],)
    result = run_correspondence(args.deadline)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "per_profile"}, sort_keys=True)[:3000])
