"""Finite codecs and enumeration; no RTL transition implementation in Python."""
from dataclasses import replace
from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kernel0_finite_model as model

BASE = "00086d1722a22b481daa834b1e2b0f1a2d3e2b9e"
SOURCES = ("Kernel-0-Direct-RTL-Experiment.md", "Kernel-0-Abstract-Semantics.md",
           "Kernel-0-Verification-Obligations.md", "Kernel-0-Finite-Model.md",
           "kernel0_finite_model.py", "Kernel-0-Re-Minimization.md")
KINDS = ("establish", "grant", "restrict", "replace", "delegate", "set", "flip",
         "accept", "resume", "pair", "mixed")
PROFILES = (model.Profile("independent"), model.Profile("coupled", coupled=True),
            model.Profile("exclusive", exclusive=True))


def encode_state(s):
    assert s.parents[:3] == (-1, -1, -1)
    if not s.established:
        assert s == model.State()
        return 0
    assert s.content in (0, 1)
    return (1 | s.data[0] << 1 | s.data[1] << 2 | s.content << 3 |
            s.issued << 4 | sum(r << (8 + 3*i) for i, r in enumerate(s.rights)) |
            (s.parents[3]+1) << 20)


def decode_state(word):
    assert 0 <= word < 1 << 22
    if not word & 1:
        assert word == 0, "noncanonical absent state"
        return model.State()
    return model.State(True, ((word >> 1) & 1, (word >> 2) & 1), (word >> 3) & 1,
                       (word >> 4) & 15,
                       tuple((word >> (8+3*i)) & 7 for i in range(4)),
                       (-1, -1, -1, (word >> 20)-1))


def encode_request(q):
    a = 4 if q.evidence == model.MANAGER else q.evidence
    return (KINDS.index(q.kind) | a << 4 | q.target << 7 | q.value << 9 |
            q.other << 12 | int(q.authentic) << 14)


def decode_request(word):
    a = (word >> 4) & 7
    return model.Request(KINDS[word & 15], model.MANAGER if a == 4 else a,
                         (word >> 7) & 3, (word >> 9) & 7, (word >> 12) & 3,
                         bool(word & (1 << 14)))


def valid_states(p):
    """All invariant-satisfying states, INCLUDING unreachable states.

    The only allowed parent entry is child 3 -> {0,1,2}; no hidden history
    is used to narrow the enumeration. Loop bounds exhaust the declared fields.
    """
    yield model.State()
    for rights in product(range(8), repeat=4):
        if sum(bool(r) for r in rights[:3]) > 1:
            continue
        active = sum((1 << i) for i, r in enumerate(rights) if r)
        for issued in range(16):
            if active & ~issued:
                continue
            for parent in range(-1, 3):
                if parent >= 0 and (not rights[3] or rights[3] & ~rights[parent]):
                    continue
                for x, y, content in product(range(2), repeat=3):
                    s = model.State(True, (x, y), content, issued, rights,
                                    (-1, -1, -1, parent))
                    if model.invariant(s, p):
                        yield s


def requests():
    original = tuple(model.catalog())
    assert len(original) == 148
    return original + tuple(replace(q, authentic=False) for q in original)
