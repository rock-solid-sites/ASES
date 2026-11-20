#!/usr/bin/env python3
"""Fail-closed OpenCode model-route preflight; never invokes a model itself."""
import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import sys

FREE_EVIDENCE_TTL = timedelta(days=7)
NAME_PATTERN = re.compile(r"^(opencode-go|opencode)/[a-z0-9][a-z0-9._-]*$")
FORBIDDEN_KEY_NAMES = frozenset((
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY",
    "PGS2_API_KEY", "PHOENIX_GROVE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY",
    "GEMINI_API_KEY", "XAI_API_KEY",
))


class RouteDenied(ValueError):
    pass


def _unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise RouteDenied("duplicate JSON key")
        obj[key] = value
    return obj


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          object_pairs_hook=_unique_pairs)
    except (OSError, UnicodeError, json.JSONDecodeError) as err:
        raise RouteDenied("missing or invalid configuration") from err


def _utc(text):
    if not isinstance(text, str):
        raise RouteDenied("missing time-stamped free-pricing evidence")
    try:
        result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as err:
        raise RouteDenied("invalid evidence timestamp") from err
    if result.tzinfo is None:
        raise RouteDenied("timestamp must include timezone")
    return result.astimezone(timezone.utc)


def check(model, allowlist, proof, available_keys, now=None, environment=None):
    """Return the exact trusted route or raise RouteDenied. No network or subprocess."""
    env = environment if environment is not None else {}
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise RouteDenied("test clock must have timezone")
    now = now.astimezone(timezone.utc)
    if not isinstance(model, str) or model.strip() != model or not NAME_PATTERN.fullmatch(model):
        raise RouteDenied("exact provider/model ID required; no defaults or variants")
    provider = model.split("/", 1)[0]
    lower = model.lower()
    if re.search(r"(?:^|[-/_.])(?:grok|x-?ai)(?:$|[-/_.])", lower):
        raise RouteDenied("forbidden model family")
    if not isinstance(allowlist, dict) or allowlist.get("schema") != "ases-model-route-allowlist-v1":
        raise RouteDenied("invalid allowlist schema")
    routes = allowlist.get("routes")
    if not isinstance(routes, list) or not routes:
        raise RouteDenied("missing allowlist entries")
    known = {}
    for route in routes:
        if not isinstance(route, dict) or set(route) != {"model", "billing", "evidence"}:
            raise RouteDenied("invalid allowlist entry")
        name, billing = route["model"], route["billing"]
        if not isinstance(name, str) or NAME_PATTERN.fullmatch(name) is None:
            raise RouteDenied("malformed allowlisted route")
        if name in known:
            raise RouteDenied("duplicate allowlisted model")
        if (name.startswith("opencode-go/") and billing != "go_subscription") or (
                name.startswith("opencode/") and billing != "zen_zero_price"):
            raise RouteDenied("provider and billing route mismatch")
        if not isinstance(route["evidence"], str) or not route["evidence"].startswith("https://"):
            raise RouteDenied("missing evidence URI")
        known[name] = route
    if model not in known:
        raise RouteDenied("model is not an explicitly approved route")
    if not isinstance(proof, dict) or proof.get("schema") != "ases-billing-proof-v1":
        raise RouteDenied("missing or invalid billing control evidence")
    if not isinstance(available_keys, (set, frozenset)):
        raise RouteDenied("credential presence must come from trusted runner")
    if any(env.get(name) for name in FORBIDDEN_KEY_NAMES):
        raise RouteDenied("unapproved paid-provider credential is available in execution environment")
    if provider == "opencode-go":
        account = proof.get("go")
        if not isinstance(account, dict) or account.get("subscription_active") is not True:
            raise RouteDenied("Go subscription entitlement not verified")
        if account.get("extra_usage_disabled") is not True:
            raise RouteDenied("Go pay-as-you-go overage must be verified disabled")
        if "OPENCODE_GO_API_KEY" not in available_keys:
            raise RouteDenied("Go credential not present in trusted launcher")
    else:
        zen = proof.get("zen_zero_price")
        if not isinstance(zen, list):
            raise RouteDenied("no independently verified zero-cost Zen evidence")
        matches = [row for row in zen if isinstance(row, dict) and row.get("model") == model]
        if len(matches) != 1:
            raise RouteDenied("no unique zero-cost evidence for this exact Zen model")
        row = matches[0]
        if type(row.get("input_usd_per_million")) not in (float, int) or (
                type(row.get("output_usd_per_million")) not in (float, int)):
            raise RouteDenied("missing numerical free-pricing evidence")
        if row["input_usd_per_million"] != 0 or row["output_usd_per_million"] != 0:
            raise RouteDenied("model is not zero-price on both meters")
        verified = _utc(row.get("verified_utc"))
        if verified > now or now - verified > FREE_EVIDENCE_TTL:
            raise RouteDenied("free-pricing verification stale or in the future")
        if "OPENCODE_API_KEY" not in available_keys:
            raise RouteDenied("Zen credential not present in trusted launcher")
    return {"model": model, "provider": provider, "billing": known[model]["billing"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Reject unauthorized OpenCode routes before launch")
    parser.add_argument("--model", required=True)
    parser.add_argument("--allowlist", type=Path, default=Path(__file__).with_name("allowlist.json"))
    parser.add_argument("--billing-proof", type=Path, required=True,
                        help="Runner-owned private attestation; do not generate from agent input")
    args = parser.parse_args(argv)
    try:
        route = check(args.model, _read_json(args.allowlist),
                      _read_json(args.billing_proof),
                      {name for name in ("OPENCODE_GO_API_KEY", "OPENCODE_API_KEY")
                       if os.environ.get(name)},
                      environment=os.environ)
    except RouteDenied as err:
        print("MODEL_ROUTE_DENIED: " + str(err), file=sys.stderr)
        return 78
    print("MODEL_ROUTE_APPROVED: " + route["model"] + " [" + route["billing"] + "]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
