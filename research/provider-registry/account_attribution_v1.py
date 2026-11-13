"""Account-attribution structural validation; never grants launch authority."""
from datetime import datetime
import json
import pathlib
import re

CATALOG = pathlib.Path(__file__).with_name("account_attribution_v1.json")
ID = re.compile(r"^[a-z][a-z0-9-]*$")


def read():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def validate(data):
    assert data["schema_version"] == 1
    assert data["kind"] == "provider_account_attribution"
    scopes = {w["id"]: w for w in data["workstreams"]}
    accounts = {a["id"]: a for a in data["accounts"]}
    assert len(scopes) == len(data["workstreams"])
    assert len(accounts) == len(data["accounts"])
    assert all(ID.fullmatch(i) for i in list(scopes) + list(accounts))

    for ident, scope in scopes.items():
        assert scope["parent_id"] is None or scope["parent_id"] in scopes
        seen = {ident}
        parent = scope["parent_id"]
        while parent is not None:
            assert parent not in seen, "workstream hierarchy cycle"
            seen.add(parent)
            parent = scopes[parent]["parent_id"]

    for a in accounts.values():
        assert a["workstream_id"] in scopes
        assert a["entitlement_state"] == "unknown"
        assert a["billing_state"] == "unknown"
        assert a["identity_state"] in ("connector_observed", "planned")
        if a["identity_state"] == "planned":
            assert a["public_handle"] is None
        else:
            assert isinstance(a["public_handle"], str) and a["public_handle"]
            assert a["evidence"]

    repos = set()
    for r in data["repositories"]:
        assert r["full_name"] not in repos
        repos.add(r["full_name"])
        assert r["workstream_id"] in scopes
        owner = accounts[r["repository_owner_account_id"]]
        assert owner["provider_id"] == "github"
        assert owner["identity_state"] == "connector_observed"
        assert r["full_name"].split("/", 1)[0].lower() == owner["public_handle"].lower()

    required = set(data["event_attribution_contract"]["required"])
    assert {
        "workstream_id", "execution_account_id", "api_actor_account_id",
        "repository_owner_account_id", "billing_account_id", "product_id",
        "meter_id", "billing_period", "amount", "unit", "observation_source",
        "observed_at", "correlation_id"
    } <= required

    def scan(value):
        if isinstance(value, dict):
            for key, child in value.items():
                assert not re.search(r"(secret|password|token|api_key|credential_value)", key, re.I), "credentials must stay private"
                scan(child)
        elif isinstance(value, list):
            for child in value:
                scan(child)
    scan(data)
    assert isinstance(data["usage_events"], list)
    for event in data["usage_events"]:
        classify_event(event, data)
    return True


def classify_event(event, data):
    """Capture allocation completeness; it is NOT scheduling admission."""
    required = set(data["event_attribution_contract"]["required"])
    assert required <= event.keys()
    scopes = {s["id"] for s in data["workstreams"]}
    accounts = {a["id"]: a for a in data["accounts"]}
    repos = {r["full_name"]: r for r in data["repositories"]}
    assert event["workstream_id"] in scopes
    assert isinstance(event["amount"], (int, float)) and not isinstance(event["amount"], bool)
    assert event["amount"] >= 0
    assert isinstance(event["correlation_id"], str) and event["correlation_id"]
    assert isinstance(event["observation_source"], str) and event["observation_source"]
    assert isinstance(event["meter_id"], str) and event["meter_id"]
    assert isinstance(event["unit"], str) and event["unit"]
    assert isinstance(event["product_id"], str) and event["product_id"]
    assert isinstance(event["billing_period"], str) and event["billing_period"]
    timestamp = datetime.fromisoformat(event["observed_at"].replace("Z", "+00:00"))
    assert timestamp.utcoffset() is not None

    for role in ("execution_account_id", "api_actor_account_id", "repository_owner_account_id"):
        value = event[role]
        assert value is None or value in accounts
        if value is not None:
            assert accounts[value]["identity_state"] == "connector_observed", "planned account used as active"
    assert event["execution_account_id"] is not None
    repo = event.get("repository")
    if repo is not None and repo in repos:
        assert event["repository_owner_account_id"] == repos[repo]["repository_owner_account_id"]
        assert event["workstream_id"] == repos[repo]["workstream_id"]

    biller = event["billing_account_id"]
    if biller is None:
        return "unallocated"
    assert biller in accounts and accounts[biller]["identity_state"] == "connector_observed"
    return "account_bound_but_unverified"


if __name__ == "__main__":
    validate(read())
    print("account attribution structure valid; no launch permission implied")
