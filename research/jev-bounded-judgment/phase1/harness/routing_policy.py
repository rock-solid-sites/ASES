#!/usr/bin/env python3
"""Deterministic Foreman-style workflow-routing legality policy.

Single source of truth for `routing.legal_roles` / `illegal_roles` /
`expected_role`. Imported by BOTH the case generator and the scorer, so the
scorer independently RECOMPUTES legality from the machine-readable `signals`
block and compares it against the stored value. The stored value is therefore
checked, never trusted.

Deliberate separation of concerns: this module is never imported by
`run_jev.py` or `run_baselines.py`. Those build model requests from `state` and
`questions` only, so no model ever sees the legality computation.

Pure, no I/O, no randomness, no wall-clock dependency.
"""
from __future__ import annotations

POLICY_RULE_ID = "foreman-routing-1.0"

ROLES = ("build", "escalate", "investigate", "redesign", "repair", "review")

SIGNALS = (
    "work_not_started",
    "specification_complete",
    "completed_work_present",
    "independent_check_needed",
    "unexplained_failure_present",
    "known_root_cause",
    "governing_assumption_invalid",
    "authority_boundary_exceeded",
    "owner_decision_required",
)

# Human-readable role descriptions, used verbatim as the `choice` labels so the
# label text is identical between base and opaque-label variants.
ROLE_LABEL = {
    "build": "Build new work whose specification is complete",
    "escalate": "Escalate because a decision or authority exceeds local remit",
    "investigate": "Investigate an unexplained failure to find a root cause",
    "redesign": "Redesign because a governing assumption is invalid",
    "repair": "Repair a defect whose root cause is already known",
    "review": "Review completed work that still needs an independent check",
}

# Deterministic tie-break order when several roles are legal: the most
# conservative escalation-first, then corrective, then generative, then review.
# Fixed tuple -> no dependence on dict/set iteration order.
PRIORITY = ("escalate", "investigate", "repair", "redesign", "build", "review")


def compute_legality(signals: dict) -> dict:
    """Return legal_roles / illegal_roles / expected_role from raw signals.

    A role is legal only when its own precondition signal(s) are set. This makes
    the illegal candidates structurally impossible rather than merely unlikely.
    """
    s = {k: bool(signals.get(k, False)) for k in SIGNALS}
    missing = [k for k in signals if k not in SIGNALS]
    if missing:
        raise ValueError(f"unknown routing signal(s): {sorted(missing)}")

    legal = {}

    # repair requires an identified root cause; suspicion is not knowledge.
    legal["repair"] = s["known_root_cause"]
    # investigate requires an unexplained failure AND no known root cause.
    legal["investigate"] = s["unexplained_failure_present"] and not s["known_root_cause"]
    # redesign requires a governing assumption that is known to be invalid.
    legal["redesign"] = s["governing_assumption_invalid"]
    # escalate requires crossing an authority boundary or needing an owner decision.
    legal["escalate"] = s["authority_boundary_exceeded"] or s["owner_decision_required"]
    # review requires completed work that still needs an independent check.
    legal["review"] = s["completed_work_present"] and s["independent_check_needed"]
    # build requires work not started with a complete specification.
    legal["build"] = s["work_not_started"] and s["specification_complete"]

    legal_roles = sorted(r for r, ok in legal.items() if ok)
    illegal_roles = sorted(r for r, ok in legal.items() if not ok)

    # Expected role = highest-priority legal role. Deterministic: PRIORITY is a
    # fixed tuple, and a tie is impossible because the tuple is totally ordered
    # over a fixed role set.
    expected = None
    for r in PRIORITY:
        if r in legal_roles:
            expected = r
            break

    return {
        "policy_rule_id": POLICY_RULE_ID,
        "signals": {k: s[k] for k in SIGNALS},
        "legal_roles": legal_roles,
        "illegal_roles": illegal_roles,
        "expected_role": expected,
    }


def build_criteria(keys):
    """`choice` criteria MUST be a dict: option_key -> option_label."""
    return {k: ROLE_LABEL[k] for k in keys}
