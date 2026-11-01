"""Research-only atomic admission for discrete allowance buckets; process-local, not durable."""
from dataclasses import dataclass
from threading import Lock

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

class Ledger:
    def __init__(self, budgets):
        if not isinstance(budgets, dict) or not budgets:
            raise ValueError("budgets required")
        self._lock = Lock()
        self._budgets = {}
        for bucket, budget in budgets.items():
            if not isinstance(bucket, Bucket) or any(not isinstance(v, str) or not v for v in vars(bucket).values()):
                raise ValueError("invalid bucket identity")
            if not isinstance(budget, dict) or type(budget.get("limit")) is not int or type(budget.get("reserve")) is not int or not 0 <= budget["reserve"] <= budget["limit"]:
                raise ValueError("invalid budget")
            self._budgets[bucket] = (budget["limit"], budget["reserve"])
        self._used = {b: 0 for b in budgets}
        self._version = 0
        self._admitted = {}

    def snapshot(self):
        with self._lock:
            return {"version": self._version, "available": {b: limit - reserve - self._used[b] for b, (limit, reserve) in self._budgets.items()}}

    def admit(self, plan_id, expected_version, claims):
        """All-or-nothing reservation; reject stale version, duplicate ID and missing bucket."""
        with self._lock:
            if type(expected_version) is not int or expected_version != self._version:
                return False, "stale snapshot"
            if not isinstance(plan_id, str) or not plan_id or plan_id in self._admitted:
                return False, "invalid or duplicate plan id"
            if not isinstance(claims, (list, tuple)) or not claims:
                return False, "claims required"
            totals = {}
            for claim in claims:
                if not isinstance(claim, Claim) or type(claim.amount) is not int or claim.amount <= 0:
                    return False, "invalid claim"
                if claim.bucket not in self._budgets:
                    return False, "unknown allowance bucket"
                totals[claim.bucket] = totals.get(claim.bucket, 0) + claim.amount
            for bucket, amount in totals.items():
                limit, reserve = self._budgets[bucket]
                if self._used[bucket] + amount > limit - reserve:
                    return False, "insufficient discrete allowance"
            for bucket, amount in totals.items():
                self._used[bucket] += amount
            self._admitted[plan_id] = totals
            self._version += 1
            return True, "admitted"

    def release(self, plan_id, expected_version):
        with self._lock:
            if type(expected_version) is not int or expected_version != self._version:
                return False, "stale snapshot"
            if plan_id not in self._admitted:
                return False, "unknown plan id"
            for bucket, amount in self._admitted.pop(plan_id).items():
                self._used[bucket] -= amount
            self._version += 1
            return True, "released"
