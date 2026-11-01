"""Single-process atomic snapshot/policy and allowance admission prototype.

Research only: no durability, provider reconciliation, or multi-process CAS.
"""
import copy
import hashlib
import json
from threading import RLock
from allowance_admission_v2 import Ledger, plan_claims
from portfolio_oracle_v1 import validate

def fingerprint(snapshot):
    encoded = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

class AdmissionGate:
    def __init__(self, snapshot, budgets):
        if validate(snapshot, {}):
            raise ValueError("invalid initial snapshot")
        self._lock = RLock()
        self._snapshot = copy.deepcopy(snapshot)
        self._digest = fingerprint(self._snapshot)
        self._ledger = Ledger(budgets)
        self._revision = 0

    def balances(self):
        with self._lock:
            return self._ledger.snapshot()

    def state(self):
        with self._lock:
            return {"revision": self._revision, "snapshot_digest": self._digest,
                    "ledger_version": self._ledger.snapshot()["version"]}

    def update_snapshot(self, expected_revision, snapshot):
        with self._lock:
            if type(expected_revision) is not int or expected_revision != self._revision:
                return False, "stale snapshot revision"
            if validate(snapshot, {}):
                return False, "invalid snapshot"
            try:
                copied = copy.deepcopy(snapshot)
                digest = fingerprint(copied)
            except (TypeError, ValueError, OverflowError):
                return False, "noncanonical snapshot"
            self._snapshot, self._digest = copied, digest
            self._revision += 1
            return True, "updated"

    def admit(self, plan_id, expected_revision, snapshot, plan):
        with self._lock:
            if type(expected_revision) is not int or expected_revision != self._revision:
                return False, "stale snapshot revision"
            try:
                if fingerprint(snapshot) != self._digest:
                    return False, "snapshot digest mismatch"
                if validate(self._snapshot, plan):
                    return False, "invalid schedule or policy"
                claims = plan_claims(self._snapshot, plan)
            except (TypeError, ValueError, KeyError, AttributeError, OverflowError):
                return False, "invalid plan or claim mapping"
            if not claims:
                return False, "no chargeable claims"
            version = self._ledger.snapshot()["version"]
            ok, reason = self._ledger.admit(plan_id, version, claims)
            if ok:
                self._revision += 1
            return ok, reason

    def settle(self, plan_id, expected_revision, claims):
        with self._lock:
            if type(expected_revision) is not int or expected_revision != self._revision:
                return False, "stale snapshot revision"
            version = self._ledger.snapshot()["version"]
            ok, reason = self._ledger.settle(plan_id, version, claims)
            if ok:
                self._revision += 1
            return ok, reason

    def release(self, plan_id, expected_revision):
        with self._lock:
            if type(expected_revision) is not int or expected_revision != self._revision:
                return False, "stale snapshot revision"
            version = self._ledger.snapshot()["version"]
            ok, reason = self._ledger.release(plan_id, version)
            if ok:
                self._revision += 1
            return ok, reason
