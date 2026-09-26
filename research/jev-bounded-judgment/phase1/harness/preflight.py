#!/usr/bin/env python3
"""Canonical preflight evidence recorder. Writes /tmp/opencode/preflight_evidence.json.

Stdlib only. Records status, client-side latency, and the exact raw body for
every preflight probe. Never prints or stores the API key.
"""
import json
import os
import time
import urllib.error
import urllib.request

KEY = os.environ.get("OPENCODE_GO_API_KEY", "")
JEV_URL = "https://opencode.ai/zen/v1/systemone"
GO_CHAT_URL = "https://opencode.ai/zen/go/v1/chat/completions"
ZEN_CHAT_URL = "https://opencode.ai/zen/v1/chat/completions"
UA = "curl/8.5.0"
SESSION = "jev-phase1-preflight-20260926"

CHOICE_CR = ["build", "review", "investigate", "repair", "redesign", "escalate"]


def post(url, body, extra=None):
    h = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
         "User-Agent": UA}
    if extra:
        h.update(extra)
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 method="POST", headers=h)
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return {"http_status": r.status,
                    "latency_ms": round((time.monotonic() - t0) * 1000.0, 1),
                    "raw": r.read().decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        return {"http_status": e.code,
                "latency_ms": round((time.monotonic() - t0) * 1000.0, 1),
                "raw": e.read().decode("utf-8", "replace"),
                "typed_error": f"http_{e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"http_status": None,
                "latency_ms": round((time.monotonic() - t0) * 1000.0, 1),
                "raw": "",
                "typed_error": f"{type(e).__name__}"}


def jev(state, instructions):
    return post(JEV_URL, {"model": "jev-1.13-free", "state": state,
                          "questions": {"q": {"type": "noul",
                                              "instructions": instructions}}})


ev = {}

# --- P1: key presence (value never recorded) --------------------------------
ev["P1_key_present"] = {"present": bool(KEY), "length": len(KEY),
                        "env_var": "OPENCODE_GO_API_KEY",
                        "value_recorded": False}

# --- P2: Jev anchors. noul == P(yes)? ---------------------------------------
ev["P2a_noul_pass_anchor"] = jev(
    "The test suite ran and all 42 tests passed. Exit code 0.",
    "Did the test suite pass?")
ev["P2b_noul_fail_anchor"] = jev(
    "The test suite ran and 7 of 42 tests failed. Exit code 1.",
    "Did the test suite pass?")
ev["P2c_noul_ambiguous_anchor"] = jev(
    "CI reported FAIL on job 'nightly' at 03:12 UTC, but the job also reported "
    "PASS at 03:13 UTC. The cause of the conflicting reports is not recorded in "
    "the log excerpt.",
    "Did the CI job pass?")
ev["P2d_noul_missing_evidence_anchor"] = jev(
    "A migration was deployed to staging on 2026-09-20. No logs, metrics, or "
    "monitoring output are available in the workspace.",
    "Did the migration succeed?")
ev["P2e_noul_pass_anchor_repeat"] = jev(
    "The test suite ran and all 42 tests passed. Exit code 0.",
    "Did the test suite pass?")

# --- P3: question-type schema discrimination --------------------------------
CH = {c: c for c in CHOICE_CR}
ev["P3a_choice_criteria_as_dict"] = post(JEV_URL, {
    "model": "jev-1.13-free",
    "state": "The repo is at commit abc123, the build is green, unit tests "
             "pass, and the acceptance criteria for the release are not yet "
             "written.",
    "questions": {"q": {"type": "choice", "instructions": "Which workflow role "
                        "should handle this state next?", "criteria": CH}}})
ev["P3b_choice_criteria_as_list"] = post(JEV_URL, {
    "model": "jev-1.13-free", "state": "x",
    "questions": {"q": {"type": "choice", "instructions": "q",
                        "criteria": CHOICE_CR}}})
ev["P3c_score_criteria_as_list"] = post(JEV_URL, {
    "model": "jev-1.13-free",
    "state": "Three reviewers rated the draft; two said the evidence is strong, "
             "one said it is weak.",
    "questions": {"q": {"type": "score", "instructions": "How strong is the "
                        "evidence?", "criteria": ["weak", "moderate", "strong"]}}})
ev["P3d_score_criteria_as_dict"] = post(JEV_URL, {
    "model": "jev-1.13-free", "state": "x",
    "questions": {"q": {"type": "score", "instructions": "q",
                        "criteria": {"weak": "weak", "moderate": "moderate",
                                     "strong": "strong"}}}})
ev["P3e_choice_three_options"] = post(JEV_URL, {
    "model": "jev-1.13-free",
    "state": "The repo is at commit abc123, the build is green, unit tests "
             "pass, and the acceptance criteria for the release are not yet "
             "written.",
    "questions": {"q": {"type": "choice", "instructions": "Which workflow role "
                        "should handle this state next?",
                        "criteria": {"build": "Build new work not yet started",
                                     "repair": "Repair a known defect",
                                     "escalate": "Escalate beyond local "
                                                 "authority"}}}})

# --- P4: cheap general model baseline ---------------------------------------
GM = {"model": "space-bunny-free",
      "messages": [{"role": "user", "content":
                    "Reply with exactly one word: YES or NO.\n"
                    "State: The test suite ran and all 42 tests passed. "
                    "Exit code 0.\nQuestion: Did the test suite pass?"}],
      "temperature": 0, "max_tokens": 8}
ev["P4a_go_chat_completions"] = post(GO_CHAT_URL, GM,
                                      extra={"x-opencode-session": SESSION})
ev["P4b_zen_chat_completions_same_key"] = post(ZEN_CHAT_URL, GM,
                                                extra={"x-opencode-session":
                                                       SESSION})
ev["P4c_zen_chat_completions_jev_model"] = post(ZEN_CHAT_URL, {
    "model": "jev-1.13-free",
    "messages": [{"role": "user", "content": "hi"}], "max_tokens": 8},
    extra={"x-opencode-session": SESSION})

# --- P5: default-User-Agent behaviour (Cloudflare signature block) ----------
ev["P5_default_ua_1010"] = {
    "note": "urllib default User-Agent 'Python-urllib/3.10' is blocked by "
            "Cloudflare with 'error code: 1010' on both endpoints.",
    "observed_http_status": 403, "observed_raw": "error code: 1010\n",
    "mitigation": "set User-Agent header explicitly"}


def main():
    out = os.environ.get("OUT", "/tmp/opencode/preflight_evidence.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"wrote {out}")
    for k in sorted(ev):
        v = ev[k]
        if isinstance(v, dict) and "http_status" in v:
            print(f"  {k:34s} status={v['http_status']} "
                  f"latency_ms={v['latency_ms']} err={v.get('typed_error','-')}")
        else:
            print(f"  {k:34s} {json.dumps(v)[:80]}")


if __name__ == "__main__":
    main()
