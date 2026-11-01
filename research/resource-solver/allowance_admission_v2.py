"""Research-only discrete allowance admission and settlement.

No implicit unit conversions or provider balance assumptions.
A process-local lock is NOT a durable distributed transaction.
"""
from dataclasses import dataclass
from threading import RLock
from collections import defaultdict

@dataclass(frozen=True, order=True)
class Bucket:
    account: str
    provider: str
    product: str
    period: str
    unit: str

@dataclass(frozen=True)
class Claim:
    bucket: Bucket
    amount: int

def plan_claims(snapshot, plan):
    if not isinstance(snapshot, dict) or not isinstance(plan, dict):
        raise ValueError("invalid snapshot or plan")
    tasks = {t["id"]: t for t in snapshot["tasks"]}
    envs = snapshot["environments"]
    claims = defaultdict(int)
    for tid, placement in plan.items():
        if tid not in tasks or not isinstance(placement, dict):
            raise ValueError("unknown task or malformed placement")
        env = placement.get("env")
        task = tasks[tid]
        if env not in envs or env not in task["modes"]:
            raise ValueError("ineligible environment")
        mode = task.get("mode_overrides", {}).get(env, {})
        duration = mode.get("duration", task["duration"])
        amount = mode.get("credits", duration if envs[env].get("account") else 0)
        if type(amount) is not int or amount < 0:
            raise ValueError("invalid charge")
        if amount == 0:
            if mode.get("allowance") is not None:
                raise ValueError("zero-charge mode cannot claim allowance")
            continue
        ident = mode.get("allowance")
        if not isinstance(ident, dict) or set(ident) != set(Bucket.__dataclass_fields__):
            raise ValueError("missing or malformed explicit allowance identity")
        bucket = Bucket(**ident)
        if any(not isinstance(x, str) or not x for x in vars(bucket).values()):
            raise ValueError("invalid allowance identity")
        if envs[env].get("account") != bucket.account:
            raise ValueError("allowance account mismatch")
        claims[bucket] += amount
    return tuple(Claim(k, v) for k, v in sorted(claims.items()))

class Ledger:
    """Atomic single-process ledger with reservation and irreversible settlement."""
    def __init__(self, budgets):
        if not isinstance(budgets, dict) or not budgets:
            raise ValueError("budgets required")
        self._lock = RLock()
        self._budgets = {}
        for bucket, entry in budgets.items():
            if not isinstance(bucket, Bucket) or any(not isinstance(x, str) or not x for x in vars(bucket).values()):
                raise ValueError("invalid bucket")
            if not isinstance(entry, dict) or type(entry.get("limit")) is not int or type(entry.get("reserve")) is not int or not 0 <= entry["reserve"] <= entry["limit"]:
                raise ValueError("invalid budget")
            self._budgets[bucket] = (entry["limit"], entry["reserve"])
        self._reserved = defaultdict(int)
        self._spent = defaultdict(int)
        self._plans = {}
        self._seen_ids = set()
        self._version = 0

    def snapshot(self):
        with self._lock:
            return {"version": self._version,
                    "available": {b: lim-res-self._reserved[b]-self._spent[b] for b, (lim, res) in self._budgets.items()},
                    "reserved": dict(self._reserved), "spent": dict(self._spent)}

    def admit(self, plan_id, expected_version, claims):
        with self._lock:
            if type(expected_version) is not int or expected_version != self._version:
                return False, "stale snapshot"
            if not isinstance(plan_id, str) or not plan_id or plan_id in self._seen_ids:
                return False, "invalid or duplicate plan id"
            if not isinstance(claims, (tuple, list)) or not claims:
                return False, "claims required"
            totals = defaultdict(int)
            for claim in claims:
                if not isinstance(claim, Claim) or type(claim.amount) is not int or claim.amount <= 0:
                    return False, "invalid claim"
                if claim.bucket not in self._budgets:
                    return False, "unknown allowance bucket"
                totals[claim.bucket] += claim.amount
            if any(self._reserved[b] + self._spent[b] + n > self._budgets[b][0] - self._budgets[b][1] for b, n in totals.items()):
                return False, "insufficient discrete allowance"
            for b, n in totals.items():
                self._reserved[b] += n
            self._plans[plan_id] = {"remaining": dict(totals), "settled": defaultdict(int)}
            self._seen_ids.add(plan_id)
            self._version += 1
            return True, "admitted"

    def settle(self, plan_id, expected_version, claims):
        with self._lock:
            if type(expected_version) is not int or expected_version != self._version:
                return False, "stale snapshot"
            if plan_id not in self._plans or not isinstance(claims, (tuple, list)) or not claims:
                return False, "unknown plan or invalid settlement"
            totals = defaultdict(int)
            for c in claims:
                if not isinstance(c, Claim) or type(c.amount) is not int or c.amount <= 0:
                    return False, "invalid claim"
                totals[c.bucket] += c.amount
            p = self._plans[plan_id]
            if any(n > p["remaining"].get(b, 0) for b, n in totals.items()):
                return False, "settlement exceeds reservation"
            for b, n in totals.items():
                self._reserved[b] -= n
                self._spent[b] += n
                p["remaining"][b] -= n
                p["settled"][b] += n
            self._version += 1
            return True, "settled"

    def release(self, plan_id, expected_version):
        with self._lock:
            if type(expected_version) is not int or expected_version != self._version:
                return False, "stale snapshot"
            if plan_id not in self._plans:
                return False, "unknown plan"
            for b, n in self._plans.pop(plan_id)["remaining"].items():
                self._reserved[b] -= n
            self._version += 1
            return True, "released unspent reservation"

def admit_plan(ledger, plan_id, expected_version, snapshot, plan, validator):
    if validator(snapshot, plan):
        return False, "invalid schedule"
    try:
        claims = plan_claims(snapshot, plan)
    except (ValueError, KeyError, TypeError) as exc:
        return False, str(exc)
    if not claims:
        return False, "no chargeable claims (no-op plans require separate admission)"
    return ledger.admit(plan_id, expected_version, claims)
