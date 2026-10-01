"""Cheap discriminating witnesses, using the frozen bounded oracle/codecs."""
from dataclasses import asdict, replace
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "direct-rtl"))
from correspondence import model, PROFILES, encode_state, encode_request


def witnesses():
    Q = model.Request
    p = PROFILES[0]
    s = model.State()
    history = []
    for q in (Q("establish"), Q("grant", target=0, value=7),
              Q("replace", target=0, other=1)):
        before = s
        s, outcome = model.resolve(s, q, p)
        assert outcome == "commit"
        history.append(dict(request=asdict(q), before=asdict(before), after=asdict(s)))
    old = Q("set", 0, 0, 1)
    current = Q("set", 1, 0, 1)
    forged = replace(current, authentic=False)
    old_out, old_result = model.resolve(s, old, p)
    forged_out, forged_result = model.resolve(s, forged, p)
    new_out, new_result = model.resolve(s, current, p)
    assert old_result == forged_result == "deny" and old_out == forged_out == s
    assert new_result == "commit" and new_out.data == (1, 0)
    # Erasing the source distinction leaves one observation. Enumerate every
    # deterministic Boolean decision at that observation; neither separates it.
    required = [False, True]
    possible = [[x, x] for x in (False, True)]
    assert required not in possible
    # Remove whole-publication timing: mix changed bits of an allowed pair.
    pair = Q("pair", 1, value=3)
    successor, outcome = model.resolve(s, pair, p)
    torn = replace(s, data=(1, 0))
    assert outcome == "commit" and model.invariant(torn, p)
    assert torn != s and torn != successor
    # Torn ingress can be well-formed, so validity checks cannot detect it.
    pair0 = Q("pair", 1, value=0)
    pair1 = Q("pair", 1, value=1)
    w0, w3, w1 = map(encode_request, (pair0, pair, pair1))
    assert (w0 ^ w1) & ~(w0 ^ w3) == 0
    torn_input_out, torn_input_result = model.resolve(s, pair1, p)
    assert torn_input_result == "commit" and torn_input_out == torn
    return {
        "profile": p.name, "history": history,
        "authority": {"state": asdict(s), "state_word": encode_state(s),
            "old": asdict(old), "forged": asdict(forged), "current": asdict(current),
            "required_outcomes": [old_result, forged_result, new_result],
            "caller_controls_verdict_or_new_lane": {
                "presented_word": encode_request(current), "actual_outcome": new_result,
                "actual_successor": asdict(new_out)},
            "erased_observation_decisions": possible, "required_decisions": required},
        "timing": {"proposal": asdict(pair), "before": asdict(s),
            "whole_successor": asdict(successor), "torn_observation": asdict(torn),
            "torn_satisfies_invariant": True,
            "torn_ingress_endpoints": [w0, w3], "torn_ingress_word": w1,
            "scope": "abstract cut witness; not analog or gate-delay simulation"},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(witnesses(), indent=2, sort_keys=True))
