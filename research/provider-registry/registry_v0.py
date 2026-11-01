"""Provider registry lifecycle v0. In-memory research prototype; not an admission engine."""
from datetime import datetime

TRANSITIONS = {
    "configured": {"verified", "retired"},
    "verified": {"active", "configured", "retired"},
    "active": {"degraded", "draining"},
    "degraded": {"active", "draining"},
    "draining": {"retired", "active"},
    "retired": set(),
}

def timestamp(value):
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if d.tzinfo is None or d.utcoffset() is None:
            raise ValueError()
    except (ValueError, AttributeError):
        raise ValueError("timezone-aware timestamp required")
    return d

class Registry:
    def __init__(self):
        self.candidates = {}
        self.operational = {}
        self.events = []
        self.assignments = {}

    def discover(self, provider, product, evidence):
        if not all(isinstance(x, str) and x for x in (provider, product, evidence)):
            raise ValueError("identity and source required")
        key = (provider, product)
        self.candidates[key] = {"evidence": evidence}
        return key

    def configure(self, key, account, actor, at):
        timestamp(at)
        if key not in self.candidates or key in self.operational or not account or not actor:
            raise ValueError("candidate, account and actor required")
        self.operational[key] = {"account": account, "state": "configured", "revision": 1,
                                 "verified_revision": None, "entitlement": None}
        self.events.append((key, "configured", actor, at))

    def verify(self, key, revision, entitlement, evidence, actor, at):
        timestamp(at)
        row = self.operational[key]
        if (row["state"] != "configured" or revision != row["revision"]
            or not isinstance(entitlement, dict) or not entitlement or not evidence or not actor):
            raise ValueError("current revision and account evidence required")
        row["entitlement"] = {"data": entitlement, "evidence": evidence, "observed_at": at}
        row["verified_revision"] = revision
        self.transition(key, "verified", actor, at)

    def transition(self, key, target, actor, at):
        timestamp(at)
        row = self.operational[key]
        if target not in TRANSITIONS[row["state"]] or not actor:
            raise ValueError("invalid transition")
        if target == "active" and (row["verified_revision"] != row["revision"]
                                   or not row["entitlement"]):
            raise ValueError("verification required")
        row["state"] = target
        self.events.append((key, target, actor, at))

    def change_catalog(self, key, actor, at):
        timestamp(at)
        row = self.operational[key]
        if row["state"] == "retired" or not actor:
            raise ValueError("invalid catalog change")
        row["revision"] += 1
        if row["state"] in ("active", "verified"):
            row["state"] = "configured"
        elif row["state"] == "degraded":
            row["state"] = "draining"
        self.events.append((key, "catalog_changed", actor, at))

    def eligible(self, key):
        row = self.operational.get(key)
        return bool(row and row["state"] == "active" and
                    row["verified_revision"] == row["revision"] and row["entitlement"])

    def assign(self, assignment_id, key):
        if not self.eligible(key) or assignment_id in self.assignments:
            raise ValueError("ineligible or duplicate assignment")
        self.assignments[assignment_id] = key

    def discard_candidate(self, key):
        if key in self.operational or key in self.assignments.values():
            raise ValueError("referenced candidate")
        self.candidates.pop(key, None)
