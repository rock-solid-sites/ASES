#!/usr/bin/env python3
"""Deterministic generator for the Phase 1 Jev diagnostic case corpus.

Emits `cases.ndjson` (62 synthetic cases, areas A-D) with stable ids, ordered by
id ascending. Pure stdlib, no network, no wall-clock, fixed seeds, so the output
is byte-reproducible.

Routing legality for area D is computed by `harness/routing_policy.py` from
machine-readable signals BEFORE the case is emitted; nothing here leaks routing
metadata into the model-visible `state` or `questions`.

All content is synthetic. No real person, organisation, credential, or
production identifier appears in any state text.
"""
from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routing_policy import (  # noqa: E402
    ROLE_LABEL,
    build_criteria,
    compute_legality,
)

GENERATOR_VERSION = "1.0.0"
SCHEMA_VERSION = "jevp1-case-1.0"
SPLITS = ("train", "dev", "test")
ROLES = ("build", "escalate", "investigate", "redesign", "repair", "review")
VARIANT_KINDS = ("base", "option_reorder", "distractor", "missing_evidence",
                 "noise", "opaque_labels", "irrelevant_change")

# Opaque option keys for the opaque_labels control. Content-free by design.
OPAQUE_KEYS = {
    "build": "opt_k7a1",
    "escalate": "opt_m2b9",
    "investigate": "opt_r4c3",
    "redesign": "opt_t8d5",
    "repair": "opt_w1e6",
    "review": "opt_y5f2",
}

DISTRACTOR_PARAGRAPHS = (
    "Unrelated context: the team also owns two other services that have no "
    "dependency on this change. The on-call rota for the following week was "
    "rearranged for reasons unrelated to the work described here. A quarterly "
    "headcount plan is circulating and is not yet approved.",
    "Additional context that does not bear on the question: the repository has "
    "418 open pull requests, the most recent one was merged eleven days ago, "
    "and the build cache was last cleared in an unrelated maintenance window. "
    "None of these facts describe the item in question.",
    "Background, unrelated to the item in question: the documentation site was "
    "rehosted to a new static generator last quarter, the internal wiki was "
    "archived, and the office move to the second floor completed. None of this "
    "affects the matter being asked about.",
    "Unrelated material: the project uses a two-week iteration cadence, three "
    "teams share the same monorepo, and the office coffee machine was replaced. "
    "The following is a verbatim copy of an unrelated meeting agenda and "
    "contains no information about the item under discussion.",
    "Incidental information, not evidence about the item in question: the "
    "service catalogue contains 92 entries, 14 of which are deprecated, and the "
    "dashboard refresh was completed last sprint. None of this bears on the "
    "question asked.",
)

CASES = []


def _prov(template_id):
    return {
        "template_id": template_id,
        "generator": "harness/gen_cases.py",
        "generator_version": GENERATOR_VERSION,
        "synthetic": True,
        "contains_personal_content": False,
        "contains_secrets": False,
    }


def _ctl(pair_id, variant_kind="base", base_case_id=None, deciding_fact="",
         label_map=None, option_order=None, perturbation_seed=None):
    return {
        "pair_id": pair_id,
        "variant_kind": variant_kind,
        "base_case_id": base_case_id,
        "deciding_fact": deciding_fact,
        "label_map": label_map,
        "option_order": option_order,
        "perturbation_seed": perturbation_seed,
    }


def _gt(answerable, answer, rationale, deciding_fact, abstain_expected=False,
        abstain_acceptable=False, probabilities=None):
    return {
        "answerable": answerable,
        "answer": answer,
        "probabilities": probabilities,
        "rationale": rationale,
        "deciding_fact": deciding_fact,
        "abstain_expected": abstain_expected,
        "abstain_acceptable": abstain_acceptable,
    }


def add(case_id, area, split, difficulty, state, qtype, instructions,
        ground_truth, control, template_id, difficulty_note=None, criteria=None,
        signals=None):
    assert split in SPLITS, f"{case_id}: bad split {split}"
    assert control["variant_kind"] in VARIANT_KINDS, case_id
    if qtype == "noul":
        assert criteria is None, f"{case_id}: noul must not carry criteria"
    if qtype == "choice":
        assert isinstance(criteria, dict), f"{case_id}: choice needs a dict"
    if qtype == "score":
        assert isinstance(criteria, list), f"{case_id}: score needs a list"
    routing = None
    if area == "D":
        assert signals is not None, f"{case_id}: area D needs signals"
        routing = compute_legality(signals)
        assert criteria is not None, f"{case_id}: area D needs choice criteria"
    rec = {
        "schema_version": SCHEMA_VERSION,
        "id": case_id,
        "area": area,
        "split": split,
        "difficulty": difficulty,
        "difficulty_note": difficulty_note,
        "state": state,
        "questions": [{
            "qid": "q",
            "type": qtype,
            "instructions": instructions,
            "criteria": criteria,
        }],
        "ground_truth": ground_truth,
        "control": control,
        "routing": routing,
        "provenance": _prov(template_id),
    }
    CASES.append(rec)
    return rec


# ---------------------------------------------------------------------------
# Noise / distractor transforms (seeded, meaning-preserving)
# ---------------------------------------------------------------------------
def apply_noise(text, seed):
    """Seeded, meaning-preserving surface perturbation.

    Only whitespace, line breaking, sentence-initial capitalisation, and word
    duplication. No token is deleted, reordered, or substituted, so the
    deciding fact and therefore the ground truth are unchanged by construction.
    """
    rng = random.Random(seed)
    words = text.split(" ")
    out = []
    for w in words:
        r = rng.random()
        if r < 0.05:
            w = w + " "          # doubled space
        elif r < 0.09:
            w = w.upper()        # shouting; meaning preserved for these tokens
        out.append(w)
        if rng.random() < 0.04:
            out.append(w)         # duplicated word
    s = " ".join(out)
    if rng.random() < 0.5:
        s = s.replace(". ", ".\n")          # arbitrary line breaks
    if rng.random() < 0.5:
        s = "  " + s                        # leading whitespace
    if rng.random() < 0.5:
        s = s + "   "                       # trailing whitespace
    return s


def apply_distractor(state, seed, template_id, base_id):
    para = DISTRACTOR_PARAGRAPHS[seed % len(DISTRACTOR_PARAGRAPHS)]
    return f"{state}\n\n{para}"


# ===========================================================================
# AREA A - cheap-baseline comparison. 20 cases, ground truth known.
# 16 base + 2 distractor + 1 missing_evidence + 1 noise.
# ===========================================================================

A = [
    # ---- easy (train) ----
    ("a-e01", "train", "easy",
     "The checkout service deployed build 812 to production at 14:02 UTC. The "
     "post-deploy health check returned HTTP 200 for all three probes. No "
     "rollback was recorded in the following 30 minutes.",
     "Did the checkout service deploy succeed?",
     "yes", "The post-deploy health check returned HTTP 200 for all three "
     "probes and no rollback was recorded.",
     "health check returned HTTP 200 for all three probes, no rollback recorded",
     "Deploy outcome stated as an explicit success signal.",
     "T-A-EASY-01", "Deterministic outcome stated outright; no competing signal."),
    ("a-e02", "train", "easy",
     "The test suite ran and 7 of 42 tests failed. The runner exited with "
     "code 1.",
     "Did the test suite pass?",
     "no", "7 of 42 tests failed and the runner exited with code 1.",
     "7 of 42 tests failed, exit code 1",
     "Explicit numeric failure count; matches the P2b preflight anchor pattern.",
     "T-A-EASY-01", "P2b-style anchor: this is the exact reverse anchor used "
     "to confirm noul == P(yes)."),
    ("a-e03", "train", "easy",
     "The schema validation step rejected the migration script. The migration "
     "was aborted before any row was written and the schema version is "
     "unchanged.",
     "Was the migration applied to the database?",
     "no", "The migration was aborted before any row was written, so it was "
     "not applied.",
     "migration aborted before any row was written",
     "Explicitly states the mutation never occurred.",
     "T-A-EASY-01", "Negative question about an action that never happened."),
    ("a-e04", "train", "easy",
     "The release candidate recorded 18 acceptance checks and all 18 are "
     "marked PASS in the acceptance report. The report is signed by two "
     "independent reviewers.",
     "Did the release meet its acceptance criteria?",
     "yes", "All 18 acceptance checks are marked PASS in a signed report.",
     "all 18 acceptance checks marked PASS",
     "Explicit complete-count pass with a corroborating signature.",
     "T-A-EASY-01", "Corroboration present but not required for the answer."),
    ("a-e05", "train", "easy",
     "The build log for run 4411 ends with the line 'BUILD FAILED: exit code "
     "2' and no artefact was published to the registry.",
     "Did the build succeed?",
     "no", "The build log ends with BUILD FAILED and no artefact was "
     "published.",
     "log ends 'BUILD FAILED: exit code 2', no artefact published",
     "Explicit terminal failure line in the log.",
     "T-A-EASY-01", "Log-tail style, the shape CI systems actually produce."),
    ("a-e06", "train", "easy",
     "Commit 5c1a0d2 was pushed to the integration branch. The pipeline "
     "configuration disables continuous integration for that path, so no job "
     "was triggered and no pipeline record exists for the commit.",
     "Did the pipeline run for commit 5c1a0d2?",
     "no", "The pipeline path is disabled, so no job was triggered for the "
     "commit and no pipeline record exists.",
     "CI disabled for that path, no job triggered",
     "A missing artefact explained by a configuration fact, not by silence.",
     "T-A-EASY-01", "Tests the difference between 'no evidence' and 'a known "
     "negative'."),
    ("a-e07", "train", "easy",
     "Incident INC-2291 was declared resolved at 09:41 UTC and the follow-up "
     "page was closed at 10:02 UTC by the incident commander.",
     "Was the incident resolved?",
     "yes", "The incident was declared resolved and the follow-up page was "
     "closed.",
     "declared resolved 09:41, follow-up page closed 10:02",
     "Explicit resolution declaration with a closure timestamp.",
     "T-A-EASY-01", "Process-state success rather than technical success."),

    # ---- medium (train / dev) ----
    ("a-m01", "train", "medium",
     "Three of the five canary nodes were upgraded to release 4.7. The rollout "
     "was paused by the operator at 12:20 UTC and was never resumed. The "
     "remaining two nodes are still running release 4.6.",
     "Are all nodes running release 4.7?",
     "no", "Only three of five nodes were upgraded and the rollout was paused "
     "and never resumed, so two nodes still run 4.6.",
     "3 of 5 nodes upgraded, rollout paused and never resumed",
     "Requires combining a partial count with an explicit 'never resumed'.",
     "T-A-MED-01", "Partial-progress state; naive '3 of 5' keyword matching "
     "could misread progress as completion."),
    ("a-m02", "train", "medium",
     "Migration 0031 ran for 40 minutes against the replica and reported "
     "'completed successfully' with 0 errors. A separate disk incident four "
     "hours later caused an unrelated rollback of migration 0037.",
     "Did migration 0031 complete without error?",
     "yes", "Migration 0031 completed successfully with 0 errors; the later "
     "rollback concerned a different migration.",
     "migration 0031 completed successfully, 0 errors",
     "Requires noticing the later rollback concerns migration 0037, not 0031.",
     "T-A-MED-01", "Entity-disambiguation trap: a nearby true-but-irrelevant "
     "negative fact."),
    ("a-m03", "train", "medium",
     "The linter reported 214 warnings and 0 errors. The continuous "
     "integration gate is configured with --max-warnings unset and "
     "--max-errors 0, so the gate is evaluated on errors only.",
     "Did the lint gate fail?",
     "no", "The gate is evaluated on errors only and there were 0 errors, so "
     "the gate did not fail despite 214 warnings.",
     "0 errors, gate evaluates errors only",
     "Requires applying the stated gate configuration rather than reacting to "
     "the warning count.",
     "T-A-MED-01", "Surface-token trap: 214 warnings looks like failure."),
    ("a-m04", "train", "medium",
     "The service was rolled back to the previous release. Separately, the "
     "manual data fix was applied afterwards and a reconciliation report then "
     "showed 0 missing rows and 0 duplicate rows.",
     "Was the incident fully resolved including data correctness?",
     "yes", "The rollback restored service and the subsequent reconciliation "
     "report showed no missing or duplicate rows, so both availability and "
     "data correctness are satisfied.",
     "reconciliation report: 0 missing rows, 0 duplicate rows",
     "Requires composing the service state with the later data verification.",
     "T-A-MED-01", "Two-part resolution; requires both halves to be true."),
    ("a-m05", "dev", "medium",
     "Design DOC-118 was circulated for review. Reviewer 1 and reviewer 2 both "
     "approved. Reviewer 3 recorded an objection about the retry policy, and "
     "the meeting minutes record that the objection was resolved by adopting "
     "the bounded-retry variant.",
     "Was reviewer 3's objection resolved?",
     "yes", "The minutes record the objection as resolved by adopting the "
     "bounded-retry variant.",
     "meeting minutes record the objection resolved",
     "Requires matching the objection to its resolution rather than to the "
     "number of approvals.",
     "T-A-MED-01", "Multi-party record with a dissent that is subsequently "
     "closed."),
    ("a-m06", "dev", "medium",
     "The message queue drained to zero at 02:14 UTC and has remained at zero "
     "for 6 hours. The producer was scaled to 0 replicas at 02:20 UTC and no "
     "consumer has reported an error since.",
     "What is the current severity of the message-queue backlog?",
     "none", "The backlog has been zero for 6 hours with the producer scaled "
     "to zero and no consumer errors.",
     "backlog zero for 6h, producer scaled to 0, no consumer errors",
     "Requires combining level, trend, and absence of error signal.",
     "T-A-MED-02", "Ordinal scale type; requires mapping evidence to a level."),
    ("a-m07", "dev", "medium",
     "The dependency specifier was pinned to 2.4.0. The resolver output for "
     "run 4412 lists exactly one resolved version for that package: 2.4.0.",
     "Did the build use a version other than the 2.4.0 pin?",
     "no", "The resolver lists exactly one version, 2.4.0, which is the pin.",
     "resolver lists exactly 2.4.0, matching the pin",
     "Requires comparing two stated values rather than reacting to one.",
     "T-A-MED-01", "Value-comparison task; the negative framing invites a "
     "surface-match error."),
    ("a-m08", "dev", "medium",
     "The TLS certificate for the internal endpoint expires in 3 days. An "
     "automated renewal job is configured but has not executed in the last 90 "
     "days; the last run logged 'skipped: lock held'.",
     "Will the certificate remain valid indefinitely?",
     "no", "The certificate expires in 3 days and the renewal job has not run "
     "in 90 days, so it will not remain valid indefinitely.",
     "expires in 3 days, renewal job has not run in 90 days",
     "Requires combining an expiry date with a failed renewal mechanism.",
     "T-A-MED-01", "Future-state question answered from present evidence."),

    # ---- hard (test) ----
    ("a-h01", "test", "hard",
     "Feature flag 'new-checkout' was enabled for 5% of traffic. Orders from "
     "the flagged cohort showed a 3.1% error rate over 24 hours; unflagged "
     "traffic showed 0.4%. The team's stated error budget for this cohort is "
     "0.5%. The flag was disabled the following morning. The cohort was not "
     "re-measured after the flag was disabled.",
     "Did the flagged cohort meet the stated 0.5% error budget?",
     "no", "The flagged cohort's 3.1% error rate exceeds the stated 0.5% "
     "budget, so the budget was not met.",
     "flagged cohort error rate 3.1% vs stated budget 0.5%",
     "Requires a numeric comparison against an explicit threshold, while "
     "ignoring the post-disable silence.",
     "T-A-HARD-01", "Threshold comparison with an unmeasured tail that should "
     "not change the answer."),
    ("a-h02", "test", "hard",
     "The read replica lagged by up to 4 minutes during the migration window. "
     "The application's configured read-staleness tolerance is 5 minutes, and "
     "the observed lag never exceeded that tolerance.",
     "Did the application exceed its configured staleness tolerance?",
     "no", "Observed lag peaked at 4 minutes against a 5-minute tolerance, so "
     "the tolerance was not exceeded.",
     "observed peak lag 4 min vs 5 min configured tolerance",
     "Requires comparing an observed value against a configured limit.",
     "T-A-HARD-01", "Limit comparison where the 'bad' word appears but the "
     "answer is negative."),
    ("a-h03", "test", "hard",
     "Deploy A at 10:00 failed its health check and was rolled back. Deploy B "
     "at 10:40 used a different image tag and passed all checks. No further "
     "deploys were executed that day and the rollback of deploy A was not "
     "undone.",
     "Is the currently running version the version from deploy A?",
     "no", "Deploy A failed and was rolled back; deploy B is running and the "
     "rollback was not undone.",
     "deploy A failed and rolled back, deploy B running, rollback not undone",
     "Requires resolving a two-event timeline to a single current state.",
     "T-A-HARD-01", "Temporal resolution; the earlier event is not the current "
     "state."),
    ("a-h04", "test", "hard",
     "The compliance audit reported 3 policy violations. Two were remediated "
     "the same day and independently re-verified. The third concerns a "
     "service that was decommissioned four months ago and has no live data "
     "path; it is tracked in open ticket OPS-4412.",
     "What is the current residual risk from the unremediated finding?",
     "low", "The only unremediated finding concerns a decommissioned service "
     "with no live data path, so the residual risk is low despite the ticket "
     "being open.",
     "sole unremediated finding is a decommissioned service with no live data "
     "path",
     "Requires weighing the finding's live exposure rather than counting open "
     "tickets.",
     "T-A-HARD-02", "Ordinal scale where the obvious count signal (1 open "
     "ticket) points the wrong way."),
    ("a-h05", "test", "hard",
     "The capacity model predicted 1,200 requests per second at peak. The load "
     "test sustained 1,450 requests per second for 10 minutes with no errors "
     "and no queue growth.",
     "Did the system exceed its predicted peak capacity?",
     "yes", "The system sustained 1,450 rps against a predicted 1,200 rps, so "
     "it exceeded the predicted peak.",
     "sustained 1,450 rps vs predicted 1,200 rps",
     "Requires comparing an observed value against a predicted one.",
     "T-A-HARD-01", "Positive answer requiring a comparison, not a keyword."),

    # ---- controls ----
    # NOTE: exactly one distractor control is kept in area A. A second was
    # generated and then removed to hold the corpus inside the 60+-5 budget;
    # distractor coverage is retained via a-dist1 (answerable) and b-dist1
    # (unanswerable), which is the contrast that actually matters.
    ("a-dist1", "train", "easy",
     "Three of the five canary nodes were upgraded to release 4.7. The rollout "
     "was paused by the operator at 12:20 UTC and was never resumed. The "
     "remaining two nodes are still running release 4.6.\n\n"
     "Unrelated context: the team also owns two other services that have no "
     "dependency on this change. The on-call rota for the following week was "
     "rearranged for reasons unrelated to the work described here. A quarterly "
     "headcount plan is circulating and is not yet approved.",
     "Are all nodes running release 4.7?",
     "no", "Same deciding fact as a-m01: only three of five nodes were "
     "upgraded and the rollout was never resumed. The appended paragraph "
     "carries no evidence about node release versions.",
     "3 of 5 nodes upgraded, rollout paused and never resumed",
     "Control for a-m01. The appended text asserts nothing about the item "
     "under question.",
     "T-A-CTRL-DIST", "Baseline case plus a plausible irrelevant paragraph."),
    ("a-miss1", "test", "hard",
     "Feature flag 'new-checkout' was enabled for 5% of traffic. The flag was "
     "disabled the following morning. The cohort was not re-measured after the "
     "flag was disabled.",
     "Did the flagged cohort meet the stated 0.5% error budget?",
     None, "The evidence needed to answer has been removed: the cohort error "
     "rate and the stated error budget are both absent from the state. No "
     "determination is possible from what remains, so the correct behaviour is "
     "low confidence or abstention.",
     "cohort error rate and stated error budget are both absent",
     "Control for a-h01. Exactly the two clauses carrying the deciding fact "
     "have been deleted.",
     "T-A-CTRL-MISS", "Evidence-removal control. Any confident answer here is "
     "an error."),
    ("a-noise1", "dev", "medium",
     None,  # filled by the noise transform below
     "Did the build use a version other than the 2.4.0 pin?",
     "no", "After surface perturbation the resolver still lists exactly one "
     "version, 2.4.0, matching the pin. The noise transform only alters "
     "whitespace, line breaks, capitalisation, and word duplication, so no "
     "token that carries the deciding fact is removed or replaced.",
     "resolver lists exactly 2.4.0, matching the pin",
     "Control for a-m07. Its base question is reused verbatim so the noise "
     "control is the only difference from its base.",
     "T-A-CTRL-NOISE", "Seeded surface noise; the deciding fact survives "
     "intact."),
]

# The noise control needs a base text distinct from a-m01 so it is not a
# duplicate; it reuses a-m01's family with a reworded question.
A_NOISE_BASE_STATE = (
    "The dependency specifier was pinned to 2.4.0. The resolver output for "
    "run 4412 lists exactly one resolved version for that package: 2.4.0."
)
A_NOISE_SEED = 20260926

# Per-case control spec for the area A controls. Applied after the generic loop
# because the generic loop defaults every case to the `base` control kind.
A_CONTROL_SPEC = {
    "a-dist1": ("a-m01", "distractor", "a-m01"),
    "a-miss1": ("a-h01", "missing_evidence", "a-h01"),
}

for entry in A:
    (cid, split, difficulty, state, question, answer, rationale, deciding,
     note, template_id, diff_note) = entry
    if cid == "a-noise1":
        state = apply_noise(A_NOISE_BASE_STATE, A_NOISE_SEED)
        gt = _gt(True, answer, rationale, deciding)
        ctl = _ctl("a-m07", "noise", "a-m07", deciding,
                   perturbation_seed=A_NOISE_SEED)
        add(cid, "A", split, difficulty, state, "noul", question, gt, ctl,
            template_id, diff_note)
    else:
        gt = _gt(True, answer, rationale, deciding)
        if cid in A_CONTROL_SPEC:
            pair_id, vk, base_id = A_CONTROL_SPEC[cid]
            ctl = _ctl(pair_id, vk, base_id, deciding)
        else:
            ctl = _ctl(cid, "base", None, deciding)
        add(cid, "A", split, difficulty, state, "noul", question, gt, ctl,
            template_id, diff_note)

# a-miss1 needs the unanswerable ground truth, patched here so the table above
# stays readable.
for rec in CASES:
    if rec["id"] == "a-miss1":
        rec["ground_truth"] = _gt(False, None, rec["ground_truth"]["rationale"],
                                  rec["ground_truth"]["deciding_fact"],
                                  abstain_expected=True)

# a-m06 and a-h04 use the ordinal `score` type; rebuild them as such.
SCORE_LOW = ["none", "low", "high"]
for rec in CASES:
    if rec["id"] == "a-m06":
        rec["questions"][0]["type"] = "score"
        rec["questions"][0]["criteria"] = SCORE_LOW
    if rec["id"] == "a-h04":
        rec["questions"][0]["type"] = "score"
        rec["questions"][0]["criteria"] = ["low", "medium", "high"]


# ===========================================================================
# AREA B - abstention / escalation. 14 cases, unanswerable or ambiguous.
# 10 base + 2 distractor + 1 missing_evidence + 1 noise.
# ===========================================================================

B = [
    # ---- conflicting evidence (genuinely ambiguous) ----
    ("b-a01", "train", "hard",
     "Continuous integration reported FAIL on job 'nightly' at 03:12 UTC. The "
     "same job reported PASS at 03:13 UTC. The excerpt does not record why the "
     "two runs disagree, and no rerun has been performed.",
     "Did the nightly job pass?",
     None, "Two runs of the same job disagree and the cause of the "
     "disagreement is not recorded. A determinate yes or no is not derivable, "
     "so the correct behaviour is low confidence or abstention.",
     "two runs of the same job disagree with no recorded cause",
     "Directly comparable to the P2c preflight anchor, which returned a "
     "mid-range noul of 0.59-0.61 rather than a saturated value.",
     "T-B-AMB-01", "Conflicting reports, cause unrecorded."),
    ("b-a02", "dev", "hard",
     "Two engineers independently reviewed the change. One approved it. The "
     "other wrote 'I cannot approve this until the rollback plan exists'. No "
     "rollback plan has since been written and no further review is recorded.",
     "Did the review pass?",
     None, "One reviewer approved and one withheld approval pending a rollback "
     "plan that does not exist. The review is not resolved either way, so the "
     "correct behaviour is low confidence or abstention.",
     "one approval, one conditional non-approval never satisfied",
     "Requires recognising an unsatisfied condition as an open state rather "
     "than a count.",
     "T-B-AMB-01", "Conditional approval that was never satisfied."),
    ("b-a03", "dev", "hard",
     "Customer report CS-8812 says the export completed and the confirmation "
     "email arrived. Internal ticket OPS-4402 says the export was aborted and "
     "no file was produced. The two records reference different export ids.",
     "Did the export complete?",
     None, "The customer record and the internal record disagree and refer to "
     "different export ids, so neither can be preferred on the available "
     "evidence. The correct behaviour is low confidence or abstention.",
     "conflicting records referencing different export ids",
     "Entity mismatch prevents disambiguation; guessing would be unfounded.",
     "T-B-AMB-02", "Conflicting records about different entities."),
    ("b-a04", "test", "hard",
     "The change-control board met on 12 May. The minutes available in the "
     "workspace end mid-sentence at 'the board agreed to defer the decision "
     "until'. No continuation is present.",
     "Did the change-control board approve the change?",
     None, "The minutes are truncated exactly at the decision clause, so the "
     "outcome is not recorded. The correct behaviour is low confidence or "
     "abstention.",
     "minutes truncated at the decision clause",
     "Truncated evidence; absence of a decision is not a rejection.",
     "T-B-AMB-02", "Truncated record at the decisive clause."),
    ("b-a05", "test", "hard",
     "The dataset for evaluation was assembled from two sources. The first "
     "labels 82% of items positive. The second labels 31% positive. No "
     "adjudication was performed and the assembly method is not recorded.",
     "Is the majority label of this dataset positive?",
     None, "The two sources disagree substantially and no adjudication or "
     "assembly method is recorded, so the majority label cannot be established "
     "from the available evidence. The correct behaviour is low confidence or "
     "abstention.",
     "82% vs 31% positive rate across two unadjudicated sources",
     "Both readings are numerically defensible; neither can be preferred.",
     "T-B-AMB-02", "Quantitative disagreement without adjudication."),

    # ---- insufficient evidence (deciding fact simply absent) ----
    ("b-i01", "train", "hard",
     "Service 'cart-checkout' was deployed to production on 2026-09-20. No "
     "logs, metrics, traces, or health-check output are available in the "
     "workspace, and no monitoring record was exported for the period.",
     "Did the cart-checkout deployment succeed?",
     None, "No evidence of any kind about the deployment outcome is present. "
     "This is insufficient evidence rather than evidence of failure, so the "
     "correct behaviour is low confidence or abstention. Directly comparable "
     "to the P2d preflight anchor, which returned noul 0.47.",
     "no logs, metrics, traces, or health-check output available",
     "Matches the P2d preflight anchor class exactly.",
     "T-B-INS-01", "Total evidence absence; confidence should sit near 0.5."),
    ("b-i02", "dev", "hard",
     "Ticket ENG-3310 is open with the single line 'flaky in staging'. No "
     "frequency, no environment list, no reproduction steps, and no owner "
     "comment are recorded.",
     "Is the failure rate for ticket ENG-3310 above the team's 1% threshold?",
     None, "No failure rate is recorded anywhere, so the comparison against "
     "the 1% threshold cannot be made. The correct behaviour is low "
     "confidence or abstention.",
     "no failure rate recorded; the 1% threshold cannot be compared",
     "The threshold is stated but the quantity to compare is absent.",
     "T-B-INS-01", "Threshold stated, measured quantity absent."),
    ("b-i03", "dev", "hard",
     "Two deployments of the same configuration occurred, one to staging and "
     "one to production, in that order. The records do not state whether the "
     "configurations were identical.",
     "Is production running the same configuration that was validated in "
     "staging?",
     None, "The record does not establish that the two configurations were "
     "identical, so the question cannot be answered from the evidence. The "
     "correct behaviour is low confidence or abstention.",
     "identity of the two configurations is not stated",
     "A missing equality relation, not a missing value.",
     "T-B-INS-02", "Unknown relational fact."),
    ("b-i04", "test", "hard",
     "A load test was executed against the staging environment. The workspace "
     "contains the test plan and the tool configuration. The result files are "
     "not present in the workspace and were not exported.",
     "Did the load test meet its stated target throughput?",
     None, "The plan and configuration are present but the results are not, so "
     "no comparison against the target is possible. The correct behaviour is "
     "low confidence or abstention.",
     "result files absent; only plan and configuration present",
     "Process evidence present, outcome evidence absent.",
     "T-B-INS-01", "Inputs present, outputs absent."),
    ("b-i05", "test", "hard",
     "The dependency was upgraded from 3.1.0 to 3.2.0. The advisory database "
     "reachable from this workspace returns an empty result for 3.2.0 and the "
     "query was not retried.",
     "Does version 3.2.0 contain a known security vulnerability?",
     None, "The advisory lookup returned an empty result, which is consistent "
     "with both 'no known vulnerability' and 'lookup failed or incomplete'. "
     "The correct behaviour is low confidence or abstention.",
     "empty advisory result is consistent with lookup failure, not with safety",
     "An empty result from an unreliable instrument is not evidence of "
     "absence.",
     "T-B-INS-02", "Instrument failure masquerading as a clean result."),

    # ---- controls ----
    # NOTE: b-dist1 is the only distractor control kept in area B; a second was
    # generated and removed to hold the corpus inside the 60+-5 budget.
    ("b-dist1", "dev", "hard",
     "Two engineers independently reviewed the change. One approved it. The "
     "other wrote 'I cannot approve this until the rollback plan exists'. No "
     "rollback plan has since been written and no further review is recorded."
     "\n\n"
     "Additional context that does not bear on the question: the repository "
     "has 418 open pull requests, the most recent one was merged eleven days "
     "ago, and the build cache was last cleared in an unrelated maintenance "
     "window. None of these facts describe the item in question.",
     "Did the review pass?",
     None, "Same decisive evidence as b-a02: one approval and one conditional "
     "non-approval that was never satisfied. The appended paragraph contains "
     "no statement about the review outcome, so the case remains unanswerable.",
     "one approval, one conditional non-approval never satisfied",
     "Control for b-a02. A distractor must not resolve an ambiguity.",
     "T-B-CTRL-DIST", "Critical negative control: added irrelevant text must "
     "not manufacture confidence."),
    ("b-miss1", "train", "hard",
     "Continuous integration ran the 'nightly' job. The workspace records that "
     "the job was scheduled. No result, exit code, or log is present for the "
     "run.",
     "Did the nightly job pass?",
     None, "The evidence present in b-a01 has been removed entirely: the "
     "conflicting FAIL and PASS reports are gone and only the fact of "
     "scheduling remains. The case is unanswerable, so the correct behaviour "
     "is low confidence or abstention.",
     "conflicting result records removed; only the scheduled run remains",
     "Control for b-a01. This is the evidence-removal step: conflict becomes "
     "total absence.",
     "T-B-CTRL-MISS", "Evidence removal applied to an ambiguous case."),
    ("b-noise1", "dev", "hard",
     None,  # filled by the noise transform below
     "Is the failure rate for the staging flake above the team's 1% "
     "threshold?",
     None, "After surface perturbation the record still contains only the "
     "phrase 'flaky in staging' with no frequency. The noise transform alters "
     "whitespace, line breaks, capitalisation, and word duplication only, so "
     "no failure rate is introduced and the case remains unanswerable.",
     "no failure rate recorded; the 1% threshold cannot be compared",
     "Control for b-i02. Surface perturbation must not create the appearance "
     "of a measurement.",
     "T-B-CTRL-NOISE", "Seeded noise on an unanswerable case."),
]

B_NOISE_BASE_STATE = (
    "Ticket ENG-3310 is open with the single line 'flaky in staging'. No "
    "frequency, no environment list, no reproduction steps, and no owner "
    "comment are recorded."
)
B_NOISE_SEED = 20260927

B_CONTROL_SPEC = {
    "b-dist1": ("b-a02", "distractor", "b-a02"),
    "b-miss1": ("b-a01", "missing_evidence", "b-a01"),
}

for entry in B:
    (cid, split, difficulty, state, question, answer, rationale, deciding,
     note, template_id, diff_note) = entry
    if cid == "b-noise1":
        state = apply_noise(B_NOISE_BASE_STATE, B_NOISE_SEED)
        gt = _gt(False, None, rationale, deciding, abstain_expected=True)
        ctl = _ctl("b-i02", "noise", "b-i02", deciding,
                   perturbation_seed=B_NOISE_SEED)
    else:
        gt = _gt(False, None, rationale, deciding, abstain_expected=True)
        if cid in B_CONTROL_SPEC:
            pair_id, vk, base_id = B_CONTROL_SPEC[cid]
            ctl = _ctl(pair_id, vk, base_id, deciding)
        else:
            ctl = _ctl(cid, "base", None, deciding)
    add(cid, "B", split, difficulty, state, "noul", question, gt, ctl,
        template_id, diff_note)


# ===========================================================================
# AREA C - contrastive / causal. 16 cases in 6 pairs + 4 irrelevant_change.
# Each pair differs ONLY in the deciding fact and has opposite ground truth.
# Each whole family lives inside one split.
# ===========================================================================

C_PAIRS = [
    # (pair, split, topic, shared_state, q, fact_yes, fact_no)
    ("cp1", "train",
     "The change under review modifies the request validation path. The pull "
     "request is open. The reviewer note states: '{FACT}'.",
     "Is the change ready to merge?",
     "All required reviewers have approved and the continuous integration "
     "gate is green.",
     "The continuous integration gate is red because the new validation test "
     "fails.",
     "CP1", "Validation path. The deciding fact is the reviewer note alone."),
    ("cp2", "train",
     "Customer account AC-77 was updated at 09:14 UTC. The audit subsystem "
     "recorded the following: '{FACT}'.",
     "Is the audit trail for account AC-77 complete?",
     "The audit log records the change, the actor, and the timestamp.",
     "The audit log records the change and the timestamp but the actor field "
     "is empty.",
     "CP2", "Audit completeness. One missing field flips the answer."),
    ("cp3", "dev",
     "Feature flag 'fast-path-v2' is enabled in production. The rollout record "
     "states: '{FACT}'.",
     "Is the fast-path change fully rolled out?",
     "The rollout plan targets 100% and the current traffic share is 100%.",
     "The rollout plan targets 100% and the current traffic share is 12%.",
     "CP3", "Rollout completion. Plan versus actual share."),
    ("cp4", "dev",
     "Build 903 was produced during the nightly window. The archived build "
     "manifest states: '{FACT}'.",
     "Is build 903 reproducible from the recorded commit?",
     "The recorded build manifest lists commit 7a11c2 as the source.",
     "The recorded build manifest lists commit 9f0e44 as the source.",
     "CP4", "Reproducibility. Only the commit id differs across the pair."),
    ("cp5", "test",
     "Migration 0042 was applied to the primary database. The migration log "
     "ends with: '{FACT}'.",
     "Was migration 0042 applied cleanly?",
     "applied cleanly, reporting 0 warnings.",
     "applied with 3 warnings, one of which is a data-truncation warning.",
     "CP5", "Clean application. A truncation warning flips the answer."),
    ("cp6", "test",
     "Service 'ledger-ingest' runs in namespace prod. The monitoring summary "
     "for the last 30 minutes states: '{FACT}'.",
     "Is ledger-ingest healthy?",
     "All readiness probes have returned HTTP 200 continuously for 30 "
     "minutes.",
     "Readiness probes have been failing with connection refused continuously "
     "for 30 minutes.",
     "CP6", "Service health. Directly parallel outcomes."),
]

C_PAIR_RATIONALE = {
    "cp1": ("yes", "The reviewer note states that all required reviewers "
            "approved and the integration gate is green, so the change is "
            "ready to merge.",
            "reviewer note: all required reviewers approved and gate green"),
    "cp2": ("yes", "The audit log records the change, the actor, and the "
            "timestamp, so the trail is complete.",
            "audit log records change, actor, and timestamp"),
    "cp3": ("yes", "The rollout plan targets 100% and the current traffic "
            "share is 100%, so the change is fully rolled out.",
            "traffic share 100% against a 100% target"),
    "cp4": ("yes", "The manifest lists commit 7a11c2, which is the recorded "
            "source commit, so the build is reproducible from it.",
            "manifest lists 7a11c2, the recorded source commit"),
    "cp5": ("yes", "The log ends with 'applied cleanly' reporting 0 warnings, "
            "so the migration was applied cleanly.",
            "log ends 'applied cleanly', 0 warnings"),
    "cp6": ("yes", "All readiness probes returned HTTP 200 continuously for 30 "
            "minutes, so the service is healthy.",
            "readiness probes 200 continuously for 30 minutes"),
}
C_PAIR_RATIONALE_NO = {
    "cp1": ("no", "The reviewer note states the integration gate is red "
            "because a new validation test fails, so the change is not ready "
            "to merge.",
            "reviewer note: gate red, new validation test fails"),
    "cp2": ("no", "The audit log has an empty actor field, so the trail is not "
            "complete.",
            "audit log actor field is empty"),
    "cp3": ("no", "The current traffic share is 12% against a 100% target, so "
            "the change is not fully rolled out.",
            "traffic share 12% against a 100% target"),
    "cp4": ("no", "The manifest lists commit 9f0e44, not the recorded source "
            "commit 7a11c2, so the build is not reproducible from it.",
            "manifest lists 9f0e44, not the recorded source commit"),
    "cp5": ("no", "The log ends with 'applied with 3 warnings' including a "
            "data-truncation warning, so the migration was not applied "
            "cleanly.",
            "log ends 'applied with 3 warnings' incl. data truncation"),
    "cp6": ("no", "Readiness probes have been failing continuously for 30 "
            "minutes, so the service is not healthy.",
            "readiness probes failing continuously for 30 minutes"),
}

C_MAP = {"cp1": ("c-p1a", "c-p1b"), "cp2": ("c-p2a", "c-p2b"),
         "cp3": ("c-p3a", "c-p3b"), "cp4": ("c-p4a", "c-p4b"),
         "cp5": ("c-p5a", "c-p5b"), "cp6": ("c-p6a", "c-p6b")}

for (pair, split, shared, q, fact_yes, fact_no, tid, diff_note) in C_PAIRS:
    ida, idb = C_MAP[pair]
    for cid, fact, table in ((ida, fact_yes, C_PAIR_RATIONALE),
                             (idb, fact_no, C_PAIR_RATIONALE_NO)):
        answer, rationale, deciding = table[pair]
        state = shared.replace("{FACT}", fact)
        gt = _gt(True, answer, rationale, deciding)
        ctl = _ctl(pair, "base", None, deciding)
        add(cid, "C", split, "hard", state, "noul", q, gt, ctl, tid,
            diff_note)

# ---- irrelevant_change controls: same answer, added irrelevant content ----
C_IRRELEVANT = [
    ("c-i1", "dev", "c-p3a",
     "The team also owns two other services, 'basket' and 'promotions', that "
     "share no code path with this flag and were not part of the rollout.",
     "Is the fast-path change fully rolled out?",
     "yes",
     "The rollout plan still targets 100% and the current traffic share is "
     "still 100%. The added sentence describes two other services and asserts "
     "nothing about the flag's traffic share, so the answer is unchanged.",
     "traffic share 100% against a 100% target",
     "T-C-CTRL-IRR",
     "Irrelevant content naming other services; the deciding fact is "
     "untouched."),
    ("c-i2", "dev", "c-p3a",
     "The flag was created on 2026-03-02 by the platform team and its "
     "description field has not been edited since.",
     "Is the fast-path change fully rolled out?",
     "yes",
     "The rollout plan still targets 100% and the current traffic share is "
     "still 100%. The added sentence gives the flag's creation date and owner "
     "and says nothing about the current traffic share, so the answer is "
     "unchanged.",
     "traffic share 100% against a 100% target",
     "T-C-CTRL-IRR",
     "Irrelevant metadata about the same object; tests surface-level rather "
     "than semantic discrimination."),
    ("c-i3", "test", "c-p5a",
     "The migration tooling in use is version 4.2, which supports both the "
     "online and the offline execution modes for this engine.",
     "Was migration 0042 applied cleanly?",
     "yes",
     "The migration log still ends with 'applied cleanly' reporting 0 "
     "warnings. The added sentence describes the tooling version and modes, "
     "which are not the log's own outcome, so the answer is unchanged.",
     "log ends 'applied cleanly', 0 warnings",
     "T-C-CTRL-IRR",
     "Irrelevant tooling context adjacent to a clean-application claim."),
    ("c-i4", "test", "c-p5a",
     "The schema file touched by this migration is 1,842 lines long and three "
     "other migrations in the same directory also modify that file.",
     "Was migration 0042 applied cleanly?",
     "yes",
     "The migration log still ends with 'applied cleanly' reporting 0 "
     "warnings. The added sentence reports file size and neighbouring "
     "migrations, neither of which is the log's own outcome, so the answer is "
     "unchanged.",
     "log ends 'applied cleanly', 0 warnings",
     "T-C-CTRL-IRR",
     "Irrelevant file-level context; a high lexical-overlap decoy that shares "
     "the word 'migration' and the word 'file'."),
]

C_BASE_STATE = {}
for rec in CASES:
    if rec["area"] == "C" and rec["control"]["variant_kind"] == "base":
        C_BASE_STATE[rec["id"]] = rec["state"]

for (cid, split, base_id, extra, q, answer, rationale, deciding, tid,
     diff_note) in C_IRRELEVANT:
    assert base_id in C_BASE_STATE, base_id
    state = C_BASE_STATE[base_id] + " " + extra
    gt = _gt(True, answer, rationale, deciding)
    ctl = _ctl(base_id, "irrelevant_change", base_id, deciding)
    add(cid, "C", split, "hard", state, "noul", q, gt, ctl, tid, diff_note)


# ===========================================================================
# AREA D - workflow routing. 12 cases. 8 base + 2 option_reorder +
# 2 opaque_labels. All six roles are always presented as candidates, so
# every case has exactly five illegal candidates.
# ===========================================================================

D_Q = "Which workflow role should handle this state next?"

D_BASE = [
    ("d-01", "train",
     "Work item ENG-2201 has been agreed and its specification is complete: "
     "scope, acceptance criteria, and interfaces are all written and approved. "
     "No implementation work has started. No defect is known, no failure is "
     "unexplained, and no governing assumption is known to be invalid. The "
     "work is fully within the team's own remit and needs no decision from an "
     "owner.",
     {"work_not_started": True, "specification_complete": True,
      "completed_work_present": False, "independent_check_needed": False,
      "unexplained_failure_present": False, "known_root_cause": False,
      "governing_assumption_invalid": False,
      "authority_boundary_exceeded": False, "owner_decision_required": False},
     "build", "T-D-01",
     "Clean build case. The four non-build roles are each structurally "
     "illegal."),
    ("d-02", "train",
     "Work item ENG-2244 cannot be estimated because its specification rests "
     "on the assumption that the legacy 'orders' table will still exist in two "
     "years. That assumption was shown last week to be false: the table is "
     "being retired within eighteen months. No defect is known, no failure is "
     "unexplained, and the item is within the team's own remit.",
     {"work_not_started": True, "specification_complete": False,
      "completed_work_present": False, "independent_check_needed": False,
      "unexplained_failure_present": False, "known_root_cause": False,
      "governing_assumption_invalid": True,
      "authority_boundary_exceeded": False, "owner_decision_required": False},
     "redesign", "T-D-02",
     "Invalid governing assumption. Note build is also illegal here because "
     "the specification is no longer complete."),
    ("d-03", "dev",
     "In production, the 'search-indexer' service began returning errors at "
     "07:58 UTC. No root cause has been identified, no defect has been "
     "localised, and no hypothesis has been confirmed. The on-call engineer "
     "has recorded that they do not know why it started. No work item "
     "specification is affected and the situation is within the team's remit.",
     {"work_not_started": False, "specification_complete": True,
      "completed_work_present": False, "independent_check_needed": False,
      "unexplained_failure_present": True, "known_root_cause": False,
      "governing_assumption_invalid": False,
      "authority_boundary_exceeded": False, "owner_decision_required": False},
     "investigate", "T-D-03",
     "Unexplained failure with no root cause. repair is structurally illegal "
     "because a root cause is required."),
    ("d-04", "test",
     "The 'search-indexer' failure has been traced: a configuration change at "
     "07:55 UTC set the shard count to zero, which is the confirmed root "
     "cause, and the fix is to restore the previous value. There is nothing "
     "left unexplained. The fix is within the team's own remit.",
     {"work_not_started": False, "specification_complete": True,
      "completed_work_present": False, "independent_check_needed": False,
      "unexplained_failure_present": True, "known_root_cause": True,
      "governing_assumption_invalid": False,
      "authority_boundary_exceeded": False, "owner_decision_required": False},
     "repair", "T-D-04",
     "Known root cause. investigate is structurally illegal because the "
     "explanation already exists."),
    ("d-05", "test",
     "Engineering finding EF-77 concluded that the current 'search-indexer' "
     "design cannot meet the 200 ms p99 target under the forecast data volume, "
     "because its partitioning assumption is invalid. The finding invalidates "
     "a governing assumption in the design. No single defect is localised and "
     "no specific failure is unexplained.",
     {"work_not_started": False, "specification_complete": False,
      "completed_work_present": False, "independent_check_needed": False,
      "unexplained_failure_present": False, "known_root_cause": False,
      "governing_assumption_invalid": True,
      "authority_boundary_exceeded": False, "owner_decision_required": False},
     "redesign", "T-D-05",
     "Invalid design assumption with no localised defect."),
    ("d-06", "dev",
     "Work item ENG-2201 was implemented and merged yesterday. The change is "
     "complete and sitting in the staging environment awaiting an independent "
     "check before release. No defect is known, no failure is unexplained, no "
     "governing assumption is known to be invalid, and no decision from an "
     "owner is required.",
     {"work_not_started": False, "specification_complete": True,
      "completed_work_present": True, "independent_check_needed": True,
      "unexplained_failure_present": False, "known_root_cause": False,
      "governing_assumption_invalid": False,
      "authority_boundary_exceeded": False, "owner_decision_required": False},
     "review", "T-D-06",
     "Completed work awaiting an independent check. build is illegal because "
     "the work is not unstarted."),
    ("d-07", "test",
     "A newly deployed feature behaves incorrectly in production. The cause is "
     "not known. Separately, the behaviour violates a published interface "
     "contract, so any continuation requires a decision by the owning team "
     "about whether the contract or the feature changes. No root cause has "
     "been identified and no defect has been localised.",
     {"work_not_started": False, "specification_complete": True,
      "completed_work_present": False, "independent_check_needed": False,
      "unexplained_failure_present": True, "known_root_cause": False,
      "governing_assumption_invalid": False,
      "authority_boundary_exceeded": False, "owner_decision_required": True},
     "escalate", "T-D-07",
     "Two legal roles (escalate and investigate). escalate has deterministic "
     "priority under the policy; this tests whether that priority is "
     "reproduced rather than whether a single answer is guessed."),
    ("d-08", "test",
     "Work item ENG-2310 has a confirmed root cause: the retry budget was set "
     "to zero in a configuration change. The obvious fix would restore the "
     "previous value, but that value violates a published interface contract "
     "that external consumers depend on. Continuing requires an owner decision "
     "about the contract. The root cause itself is fully understood.",
     {"work_not_started": False, "specification_complete": True,
      "completed_work_present": False, "independent_check_needed": False,
      "unexplained_failure_present": True, "known_root_cause": True,
      "governing_assumption_invalid": False,
      "authority_boundary_exceeded": False, "owner_decision_required": True},
     "escalate", "T-D-08",
     "Two legal roles (escalate and repair). The tempting-but-illegal answer "
     "is investigate, because 'the cause is not fully resolved' superficially "
     "resembles an unexplained failure."),
]

D_STATES = {}
for (cid, split, state, signals, expected, tid, diff_note) in D_BASE:
    D_STATES[cid] = (state, signals, tid, diff_note)
    legality = compute_legality(signals)
    assert legality["expected_role"] == expected, \
        f"{cid}: policy says {legality['expected_role']}, expected {expected}"
    gt = _gt(True, expected,
             f"Under policy {legality['policy_rule_id']}, the legal roles are "
             f"{legality['legal_roles']} and the highest-priority legal role "
             f"is {expected}. The remaining roles are structurally illegal.",
             f"deterministic signal evaluation yields {expected}")
    ctl = _ctl(cid, "base", None, f"signals -> {expected}")
    add(cid, "D", split, "hard", state, "choice", D_Q, gt, ctl, tid,
        diff_note, criteria=build_criteria(ROLES), signals=signals)

# ---- option_reorder control: identical options, different wire order ----
D_REORDER = [("d-r01", "dev", "d-03",
              ["review", "escalate", "build", "repair", "investigate",
               "redesign"]),
             ("d-r02", "dev", "d-06",
              ["repair", "redesign", "review", "build", "escalate",
               "investigate"])]

for (cid, split, base_id, order) in D_REORDER:
    state, signals, tid, diff_note = D_STATES[base_id]
    legality = compute_legality(signals)
    gt = _gt(True, legality["expected_role"],
             f"Identical evidence to {base_id}; only the presentation order of "
             f"the six candidates differs. The legal roles remain "
             f"{legality['legal_roles']} and the expected role remains "
             f"{legality['expected_role']}.",
             f"signals -> {legality['expected_role']}")
    ctl = _ctl(base_id, "option_reorder", base_id,
               f"signals -> {legality['expected_role']}", option_order=list(order))
    add(cid, "D", split, "hard", state, "choice", D_Q, gt, ctl, tid,
        diff_note + " Option presentation order permuted.",
        criteria=build_criteria(order), signals=signals)

# ---- opaque_labels control: keys renamed, labels identical ----
D_OPAQUE = ["d-l01", "d-l02"]
D_OPAQUE_BASE = {"d-l01": "d-04", "d-l02": "d-05"}
OPAQUE_ORDER = ["opt_k7a1", "opt_m2b9", "opt_r4c3", "opt_t8d5", "opt_w1e6",
                "opt_y5f2"]
for cid in D_OPAQUE:
    base_id = D_OPAQUE_BASE[cid]
    state, signals, tid, diff_note = D_STATES[base_id]
    legality = compute_legality(signals)
    label_map = {OPAQUE_KEYS[r]: r for r in ROLES}
    gt = _gt(True, legality["expected_role"],
             f"Identical evidence and identical label text to {base_id}; only "
             f"the option keys are replaced with content-free tokens. Mapped "
             f"back through the stored label_map, the legal roles remain "
             f"{legality['legal_roles']} and the expected role remains "
             f"{legality['expected_role']}.",
             f"signals -> {legality['expected_role']}")
    ctl = _ctl(base_id, "opaque_labels", base_id,
               f"signals -> {legality['expected_role']}",
               label_map=label_map, option_order=list(OPAQUE_ORDER))
    add(cid, "D", "test", "hard", state, "choice", D_Q, gt, ctl, tid,
        diff_note + " Option keys replaced with opaque tokens; label text "
        "unchanged.",
        criteria={OPAQUE_KEYS[r]: ROLE_LABEL[r] for r in ROLES},
        signals=signals)


# ===========================================================================
# Emit
# ===========================================================================
def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "cases.ndjson")
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids)), "duplicate case id"
    CASES.sort(key=lambda c: c["id"])
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for c in CASES:
            f.write(json.dumps(c, ensure_ascii=False,
                               separators=(",", ":")) + "\n")
    by_area = {}
    by_split = {}
    for c in CASES:
        by_area[c["area"]] = by_area.get(c["area"], 0) + 1
        by_split[c["split"]] = by_split.get(c["split"], 0) + 1
    print(f"wrote {out} with {len(CASES)} cases")
    print("by area :", dict(sorted(by_area.items())))
    print("by split:", dict(sorted(by_split.items())))


if __name__ == "__main__":
    main()
