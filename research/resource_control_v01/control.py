"""Experimental deterministic resource-control service (not production deployment).

All resource quantities are nonnegative *integers* in provider-defined units.
SQLite transactions are the single-writer authority for one shared database.
No external credentials or real provider launch are accepted by this module.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def require_id(value, field="id"):
    if not isinstance(value, str) or not value or len(value) > 180 or any(c.isspace() for c in value):
        raise ValueError("invalid " + field)
    return value


def integer(value, field, minimum=0):
    if type(value) is not int or value < minimum or value > 2**62:
        raise ValueError("invalid " + field)
    return value


class Rejected(Exception):
    """A safe, expected refusal with a stable machine-readable reason."""

    def __init__(self, code, detail=""):
        self.code = code
        super().__init__(code + (": " + detail if detail else ""))


class Control:
    """One SQLite-backed authority. Callers must use the same database path."""

    def __init__(self, db):
        self.db = str(db)
        Path(self.db).parent.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(self.db)
        try:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA synchronous=FULL")
            c.executescript("""
                CREATE TABLE IF NOT EXISTS buckets (
                    id TEXT PRIMARY KEY, account TEXT NOT NULL, provider TEXT NOT NULL,
                    product TEXT NOT NULL, period TEXT NOT NULL, unit TEXT NOT NULL,
                    kind TEXT NOT NULL DEFAULT 'CONSUMABLE' CHECK(kind IN ('CONSUMABLE','CONCURRENT')),
                    allowance INTEGER NOT NULL CHECK (allowance>=0),
                    reserved INTEGER NOT NULL DEFAULT 0 CHECK (reserved>=0),
                    locally_consumed INTEGER NOT NULL DEFAULT 0 CHECK (locally_consumed>=0),
                    provider_consumed INTEGER, provider_observed_at INTEGER,
                    provider_covered_local INTEGER NOT NULL DEFAULT 0,
                    price_micros INTEGER, overage TEXT NOT NULL DEFAULT 'BLOCK',
                    refreshed_at INTEGER NOT NULL, ttl_seconds INTEGER NOT NULL,
                    frozen INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(account,provider,product,period,unit));
                CREATE TABLE IF NOT EXISTS quotes (
                    id TEXT PRIMARY KEY, account TEXT NOT NULL, payload TEXT NOT NULL,
                    issued_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, snapshot TEXT NOT NULL, estimate TEXT NOT NULL,
                    attempt_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL,
                    acknowledged TEXT, auth_token_hash TEXT, auth_expires INTEGER,
                    reservation_expires INTEGER NOT NULL,
                    external_id TEXT, reason TEXT, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS claims (
                    job_id TEXT NOT NULL REFERENCES jobs(id), bucket_id TEXT NOT NULL REFERENCES buckets(id),
                    quantity INTEGER NOT NULL CHECK(quantity>=0),
                    observed INTEGER NOT NULL DEFAULT 0 CHECK(observed>=0),
                    corrected INTEGER,
                    PRIMARY KEY(job_id,bucket_id));
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
                    job_id TEXT, kind TEXT NOT NULL, observed_at TEXT NOT NULL,
                    source TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS provider_reports (
                    id TEXT PRIMARY KEY, bucket_id TEXT NOT NULL, observed_at INTEGER NOT NULL,
                    consumed INTEGER NOT NULL CHECK(consumed>=0), source TEXT NOT NULL,
                    covered_local INTEGER NOT NULL DEFAULT 0, coverage_evidence TEXT);
                CREATE TABLE IF NOT EXISTS corrections (
                    id TEXT PRIMARY KEY, job_id TEXT, bucket_id TEXT, quantity INTEGER,
                    reason TEXT NOT NULL, evidence TEXT NOT NULL, actor TEXT NOT NULL,
                    recorded_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS usage_adjustments (
                    id TEXT PRIMARY KEY,job_id TEXT NOT NULL,bucket_id TEXT NOT NULL,
                    previous INTEGER NOT NULL,new_quantity INTEGER NOT NULL,
                    reason TEXT NOT NULL,evidence TEXT NOT NULL,actor TEXT NOT NULL,
                    recorded_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS policies (
                    id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL);
                INSERT OR IGNORE INTO policies(id,revision) VALUES(1,0);
            """)
            c.commit()
        finally:
            c.close()

    @contextmanager
    def _tx(self):
        c = sqlite3.connect(self.db, timeout=20, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("PRAGMA busy_timeout=20000")
        c.execute("PRAGMA synchronous=FULL")
        try:
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.execute("COMMIT")
        except Exception:
            if c.in_transaction:
                c.execute("ROLLBACK")
            raise
        finally:
            c.close()

    @staticmethod
    def _event(c, kind, source, payload, job_id=None, event_id=None):
        e = event_id or str(uuid.uuid4())
        c.execute("INSERT INTO events(event_id,job_id,kind,observed_at,source,payload) VALUES(?,?,?,?,?,?)",
                  (e, job_id, kind, utc_now(), source, canonical(payload)))
        return e

    @staticmethod
    def _revision(c):
        return c.execute("SELECT revision FROM policies WHERE id=1").fetchone()[0]

    @staticmethod
    def _bump(c):
        c.execute("UPDATE policies SET revision=revision+1 WHERE id=1")

    @staticmethod
    def _capacity(b):
        if b["kind"]=="CONCURRENT":
            return b["allowance"]-b["reserved"]
        p = b["provider_consumed"]
        # Unknown overlap is treated conservatively. A verified covered amount
        # removes ONLY the known duplicate between local and provider records.
        spent = b["locally_consumed"] if p is None else (
            p+b["locally_consumed"]-b["provider_covered_local"])
        return b["allowance"] - spent - b["reserved"]

    @staticmethod
    def _fresh(b, now):
        return b["ttl_seconds"] > 0 and b["refreshed_at"] + b["ttl_seconds"] >= now

    def register_bucket(self, *, bucket_id, account, provider, product, period, unit,
                        allowance, price_micros=0, overage="BLOCK", ttl_seconds=3600,
                        observed_at=None, kind="CONSUMABLE"):
        ids = [bucket_id, account, provider, product, period, unit]
        for label, value in zip(("bucket_id","account","provider","product","period","unit"), ids):
            require_id(value, label)
        integer(allowance, "allowance")
        integer(ttl_seconds, "ttl_seconds", 1)
        if price_micros is not None:
            integer(price_micros, "price_micros")
        if overage not in ("BLOCK", "ALLOW_EXPLICIT"):
            raise ValueError("invalid overage")
        if kind not in ("CONSUMABLE","CONCURRENT"):
            raise ValueError("invalid bucket kind")
        stamp = integer(observed_at if observed_at is not None else int(time.time()), "observed_at")
        with self._tx() as c:
            if c.execute("SELECT 1 FROM buckets WHERE id=?", (bucket_id,)).fetchone():
                raise Rejected("DUPLICATE_BUCKET")
            c.execute("""INSERT INTO buckets(id,account,provider,product,period,unit,
                allowance,price_micros,overage,refreshed_at,ttl_seconds,kind)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (bucket_id,account,provider,product,period,unit,allowance,
                 price_micros,overage,stamp,ttl_seconds,kind))
            self._bump(c)
            self._event(c,"BUCKET_REGISTERED","registry",{"bucket_id":bucket_id})

    def refresh_bucket(self, *, bucket_id, allowance, price_micros,
                       observed_at, ttl_seconds, evidence, source="provider"):
        """Update provider entitlement facts, preserving reservations and prior event."""
        require_id(bucket_id,"bucket_id")
        integer(allowance,"allowance");integer(observed_at,"observed_at")
        integer(ttl_seconds,"ttl_seconds",1)
        if price_micros is not None:integer(price_micros,"price_micros")
        if not isinstance(evidence,str) or not evidence.strip():
            raise Rejected("MISSING_PROVIDER_EVIDENCE")
        require_id(source,"source")
        with self._tx() as c:
            b=c.execute("SELECT * FROM buckets WHERE id=?",(bucket_id,)).fetchone()
            if b is None:raise Rejected("UNKNOWN_BUCKET")
            if observed_at<=b["refreshed_at"]:
                raise Rejected("STALE_PROVIDER_FACT")
            c.execute("""UPDATE buckets SET allowance=?,price_micros=?,refreshed_at=?,
                         ttl_seconds=? WHERE id=?""",
                      (allowance,price_micros,observed_at,ttl_seconds,bucket_id))
            current=c.execute("SELECT * FROM buckets WHERE id=?",(bucket_id,)).fetchone()
            if self._capacity(current)<0:
                c.execute("UPDATE buckets SET frozen=1 WHERE id=?",(bucket_id,))
            self._event(c,"BUCKET_REFRESHED",source,
                        {"bucket_id":bucket_id,"allowance":allowance,
                         "price_micros":price_micros,"observed_at":observed_at,
                         "evidence":evidence})
            self._bump(c)
            return {"bucket_id":bucket_id,"available":self._capacity(current),
                    "frozen":self._capacity(current)<0 or bool(b["frozen"])}

    def snapshot(self, account=None, *, now=None):
        stamp = int(time.time()) if now is None else integer(now, "now")
        with self._tx() as c:
            q = "SELECT * FROM buckets" + (" WHERE account=?" if account is not None else "")
            rows = c.execute(q, (require_id(account, "account"),) if account else ()).fetchall()
            records = []
            for b in rows:
                records.append({
                    "id":b["id"],"account":b["account"],"provider":b["provider"],
                    "kind":b["kind"],"product":b["product"],"period":b["period"],"unit":b["unit"],
                    "allowance":b["allowance"],"available":self._capacity(b),
                    "reserved":b["reserved"],"local_consumed":b["locally_consumed"],
                    "provider_consumed":b["provider_consumed"],
                    "provider_covered_local":b["provider_covered_local"],
                    "price_micros":b["price_micros"],"overage":b["overage"],
                    "frozen":bool(b["frozen"]),"fresh":self._fresh(b,stamp),
                    "observed_at":b["refreshed_at"],"ttl_seconds":b["ttl_seconds"]})
            return {"revision":self._revision(c), "buckets":sorted(records,key=lambda x:x["id"])}

    @staticmethod
    def _normalize_claims(claims):
        if not isinstance(claims, dict):
            raise ValueError("claims must be mapping")
        return {require_id(k,"bucket"):integer(v,"claim",1) for k,v in claims.items()}

    def quote(self, *, claims, estimate, account, now=None):
        require_id(account, "account")
        normalized = self._normalize_claims(claims)
        if not isinstance(estimate, dict):
            raise ValueError("estimate must be object")
        canonical(estimate)
        view = self.snapshot(account, now=now)
        indexed = {b["id"]:b for b in view["buckets"]}
        issues = []
        for bid,n in normalized.items():
            b = indexed.get(bid)
            if b is None: issues.append([bid,"UNKNOWN_OR_CROSS_ACCOUNT"])
            elif b["frozen"]: issues.append([bid,"FROZEN"])
            elif not b["fresh"]: issues.append([bid,"STALE"])
            elif b["price_micros"] is None: issues.append([bid,"UNKNOWN_PRICE"])
            elif n > b["available"]: issues.append([bid,"INSUFFICIENT"])
        result={"quote_id":uuid.uuid4().hex,"revision":view["revision"],
                "snapshot_digest":digest(view),"claims":normalized,"estimate":estimate,
                "issues":issues,"eligible":not issues}
        with self._tx() as c:
            c.execute("INSERT INTO quotes(id,account,payload,issued_at) VALUES(?,?,?,?)",
                      (result["quote_id"],account,canonical(result),utc_now()))
            self._event(c,"QUOTED","controller",
                        {"quote_id":result["quote_id"],"account":account,
                         "revision":view["revision"],"eligible":result["eligible"],
                         "claims":normalized})
        return result

    def reserve(self, *, job_id, attempt_id, quote, account, now=None, reservation_ttl=3600):
        require_id(job_id,"job_id");require_id(attempt_id,"attempt_id");require_id(account,"account")
        if not isinstance(quote,dict) or not quote.get("eligible") or quote.get("issues"):
            raise Rejected("INVALID_QUOTE")
        claims = self._normalize_claims(quote.get("claims"))
        if not claims:
            raise Rejected("NO_RESOURCE_CLAIMS")
        stamp = int(time.time()) if now is None else integer(now,"now")
        integer(reservation_ttl,"reservation_ttl",1)
        with self._tx() as c:
            if c.execute("SELECT 1 FROM jobs WHERE id=? OR attempt_id=?", (job_id,attempt_id)).fetchone():
                raise Rejected("DUPLICATE_JOB_OR_ATTEMPT")
            original=c.execute("SELECT account,payload FROM quotes WHERE id=?",(quote.get("quote_id"),)).fetchone()
            if original is None or original["account"]!=account or original["payload"]!=canonical(quote):
                raise Rejected("QUOTE_MISMATCH")
            if quote.get("revision") != self._revision(c):
                raise Rejected("STALE_REVISION")
            rows = {b["id"]:b for b in c.execute("SELECT * FROM buckets WHERE account=?", (account,))}
            # This digest binds the complete account-scoped view, not a self-asserted subset.
            view = {"revision":self._revision(c),"buckets":sorted([{
                "id":b["id"],"account":b["account"],"provider":b["provider"],
                "kind":b["kind"],"product":b["product"],"period":b["period"],"unit":b["unit"],
                "allowance":b["allowance"],"available":self._capacity(b),
                "reserved":b["reserved"],"local_consumed":b["locally_consumed"],
                "provider_consumed":b["provider_consumed"],
                "provider_covered_local":b["provider_covered_local"],"price_micros":b["price_micros"],
                "overage":b["overage"],"frozen":bool(b["frozen"]),
                "fresh":self._fresh(b,stamp),"observed_at":b["refreshed_at"],
                "ttl_seconds":b["ttl_seconds"]} for b in rows.values()],key=lambda x:x["id"])}
            if quote.get("snapshot_digest") != digest(view):
                raise Rejected("STALE_SNAPSHOT")
            for bid,n in claims.items():
                b=rows.get(bid)
                if b is None: raise Rejected("WRONG_ACCOUNT_OR_BUCKET")
                if b["frozen"] or not self._fresh(b,stamp) or b["price_micros"] is None:
                    raise Rejected("INELIGIBLE_BUCKET")
                if n>self._capacity(b):raise Rejected("CAPACITY_EXHAUSTED")
            for bid,n in claims.items():
                c.execute("UPDATE buckets SET reserved=reserved+? WHERE id=?", (n,bid))
            c.execute("""INSERT INTO jobs(id,snapshot,estimate,attempt_id,state,reservation_expires,created_at)
                    VALUES(?,?,?,?,?,?,?)""",(job_id,quote["snapshot_digest"],
                    canonical(quote["estimate"]),attempt_id,"RESERVED",stamp+reservation_ttl,utc_now()))
            for bid,n in claims.items():
                c.execute("INSERT INTO claims(job_id,bucket_id,quantity) VALUES(?,?,?)",(job_id,bid,n))
            self._event(c,"RESERVED","controller",{"claims":claims,"account":account},job_id)
            self._bump(c)
            return {"job_id":job_id,"attempt_id":attempt_id,"state":"RESERVED"}

    def acknowledge(self, job_id, *, snapshot_digest, expires_at):
        require_id(job_id)
        integer(expires_at,"expires_at",1)
        token = uuid.uuid4().hex + uuid.uuid4().hex
        with self._tx() as c:
            j=c.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"]!="RESERVED":raise Rejected("INVALID_STATE")
            if j["snapshot"] != snapshot_digest:raise Rejected("WRONG_SNAPSHOT")
            if expires_at <= int(time.time()): raise Rejected("EXPIRED")
            c.execute("""UPDATE jobs SET state='AUTHORIZED',acknowledged=?,auth_token_hash=?,auth_expires=?
                         WHERE id=?""",(snapshot_digest,hashlib.sha256(token.encode()).hexdigest(),expires_at,job_id))
            self._event(c,"AUTHORIZED","controller",{"expires_at":expires_at},job_id)
            return {"job_id":job_id,"token":token,"expires_at":expires_at}

    def launch_prepare(self, job_id, *, token, now=None):
        stamp=int(time.time()) if now is None else integer(now,"now")
        with self._tx() as c:
            j=c.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"] != "AUTHORIZED":raise Rejected("INVALID_STATE")
            if not isinstance(token,str) or hashlib.sha256(token.encode()).hexdigest()!=j["auth_token_hash"]:
                raise Rejected("UNAUTHORIZED")
            if stamp >= j["auth_expires"]:raise Rejected("EXPIRED")
            c.execute("UPDATE jobs SET state='LAUNCH_PENDING' WHERE id=?",(job_id,))
            self._event(c,"LAUNCH_PENDING","controller",{"attempt_id":j["attempt_id"]},job_id)
            return {"job_id":job_id,"attempt_id":j["attempt_id"],"state":"LAUNCH_PENDING"}

    def launch_confirm(self, job_id, *, external_id):
        require_id(external_id,"external_id")
        with self._tx() as c:
            j=c.execute("SELECT state,external_id FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"]=="RUNNING" and j["external_id"]==external_id:
                return {"job_id":job_id,"state":"RUNNING"}
            if j["state"]!="LAUNCH_PENDING":raise Rejected("INVALID_STATE")
            c.execute("UPDATE jobs SET state='RUNNING',external_id=? WHERE id=?",(external_id,job_id))
            self._event(c,"RUNNING","launcher",{"external_id":external_id},job_id)
            return {"job_id":job_id,"state":"RUNNING"}

    def observe(self, job_id, *, event_id, bucket_id, cumulative, source="local"):
        require_id(event_id,"event_id");require_id(bucket_id,"bucket_id")
        integer(cumulative,"cumulative")
        if source not in ("local","launcher","provider"):
            raise ValueError("invalid source")
        with self._tx() as c:
            existing=c.execute("SELECT job_id,kind,payload FROM events WHERE event_id=?",(event_id,)).fetchone()
            if existing is not None:
                expected={"bucket_id":bucket_id,"cumulative":cumulative}
                if existing["job_id"]!=job_id or existing["kind"]!="USAGE_OBSERVED" or existing["payload"]!=canonical(expected):
                    raise Rejected("EVENT_ID_COLLISION")
                return {"duplicate":True}
            j=c.execute("SELECT state FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"] not in ("RUNNING","LAUNCH_PENDING","INTERRUPTED"):
                raise Rejected("INVALID_STATE")
            claim=c.execute("SELECT observed FROM claims WHERE job_id=? AND bucket_id=?",(job_id,bucket_id)).fetchone()
            if claim is None:raise Rejected("UNKNOWN_CLAIM")
            if cumulative < claim["observed"]:raise Rejected("NONMONOTONIC_LOCAL_OBSERVATION")
            kind=c.execute("SELECT kind FROM buckets WHERE id=?",(bucket_id,)).fetchone()["kind"]
            if kind!="CONSUMABLE":
                raise Rejected("CONCURRENT_CAPACITY_IS_NOT_CONSUMABLE")
            c.execute("UPDATE claims SET observed=? WHERE job_id=? AND bucket_id=?",(cumulative,job_id,bucket_id))
            self._event(c,"USAGE_OBSERVED",source,{"bucket_id":bucket_id,"cumulative":cumulative},job_id,event_id)
            return {"duplicate":False,"observed":cumulative}

    def record_activity(self, job_id, *, event_id, kind, start_ms, end_ms, source="launcher"):
        """Measure an interval; not necessarily productive or billable."""
        require_id(event_id, "event_id")
        if kind not in ("AGENT_ACTIVE","ENVIRONMENT_RUNNING","PROVISIONING",
                        "PROVIDER_BLOCKED","IDLE","TEARDOWN"):
            raise ValueError("invalid activity kind")
        integer(start_ms,"start_ms");integer(end_ms,"end_ms")
        if end_ms < start_ms:raise ValueError("negative interval")
        with self._tx() as c:
            payload={"kind":kind,"start_ms":start_ms,"end_ms":end_ms}
            prior=c.execute("SELECT job_id,kind,payload FROM events WHERE event_id=?",(event_id,)).fetchone()
            if prior is not None:
                if prior["job_id"] != job_id or prior["kind"]!="ACTIVITY" or prior["payload"]!=canonical(payload):
                    raise Rejected("EVENT_ID_COLLISION")
                return {"duplicate":True}
            if not c.execute("SELECT 1 FROM jobs WHERE id=?",(job_id,)).fetchone():
                raise Rejected("UNKNOWN_JOB")
            self._event(c,"ACTIVITY",source,payload,job_id,event_id)
            return {"duplicate":False}

    def interrupt(self, job_id, *, event_id):
        """Loss of visibility retains reservations until authoritative termination."""
        require_id(event_id,"event_id")
        with self._tx() as c:
            existing=c.execute("SELECT job_id,kind,payload FROM events WHERE event_id=?",(event_id,)).fetchone()
            if existing is not None:
                if existing["job_id"]!=job_id or existing["kind"]!="INTERRUPTED":
                    raise Rejected("EVENT_ID_COLLISION")
                return {"duplicate":True}
            j=c.execute("SELECT state FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"] not in ("RUNNING","LAUNCH_PENDING"):raise Rejected("INVALID_STATE")
            c.execute("UPDATE jobs SET state='INTERRUPTED' WHERE id=?",(job_id,))
            self._event(c,"INTERRUPTED","controller",{},job_id,event_id)
            return {"duplicate":False}

    def finalize(self, job_id, *, state, event_id, stop_evidence=None):
        require_id(event_id,"event_id")
        if state not in ("COMPLETED","FAILED","CANCELLED"):
            raise ValueError("invalid terminal state")
        with self._tx() as c:
            existing=c.execute("SELECT job_id,kind,payload FROM events WHERE event_id=?",(event_id,)).fetchone()
            if existing is not None:
                data=json.loads(existing["payload"])
                if existing["job_id"]!=job_id or existing["kind"]!="FINALIZED" or data.get("state")!=state:
                    raise Rejected("EVENT_ID_COLLISION")
                return {"duplicate":True}
            j=c.execute("SELECT state FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"] not in ("RUNNING","INTERRUPTED","AUTHORIZED","RESERVED"):
                raise Rejected("INVALID_STATE")
            if j["state"] in ("RUNNING","INTERRUPTED") and (not isinstance(stop_evidence,str) or not stop_evidence.strip()):
                raise Rejected("MISSING_STOP_EVIDENCE")
            if j["state"] in ("RESERVED","AUTHORIZED") and state!="CANCELLED":
                raise Rejected("NEVER_LAUNCHED")
            claims=c.execute("SELECT * FROM claims WHERE job_id=?",(job_id,)).fetchall()
            overruns=[]
            for claim in claims:
                bid=claim["bucket_id"];reserved=claim["quantity"];used=claim["observed"]
                kind=c.execute("SELECT kind FROM buckets WHERE id=?",(bid,)).fetchone()["kind"]
                if kind=="CONCURRENT":
                    c.execute("UPDATE buckets SET reserved=reserved-? WHERE id=?",(reserved,bid))
                    continue
                c.execute("""UPDATE buckets SET reserved=reserved-?,locally_consumed=locally_consumed+?
                             WHERE id=?""",(reserved,used,bid))
                if used>reserved:
                    overruns.append({"bucket_id":bid,"overrun":used-reserved})
                    c.execute("UPDATE buckets SET frozen=1 WHERE id=?",(bid,))
            c.execute("UPDATE jobs SET state=? WHERE id=?",(state,job_id))
            self._event(c,"FINALIZED","controller",{"state":state,"overruns":overruns,"stop_evidence":stop_evidence},job_id,event_id)
            self._bump(c)
            return {"duplicate":False,"state":state,"overruns":overruns}

    def provider_report(self, *, report_id, bucket_id, cumulative, observed_at,
                        source="provider", covered_local=0, coverage_evidence=None):
        require_id(report_id,"report_id");require_id(bucket_id,"bucket_id")
        integer(cumulative,"cumulative");integer(observed_at,"observed_at")
        integer(covered_local,"covered_local")
        if covered_local>0 and (not isinstance(coverage_evidence,str) or not coverage_evidence.strip()):
            raise Rejected("MISSING_COVERAGE_EVIDENCE")
        if covered_local>cumulative:raise Rejected("INVALID_COVERAGE")
        with self._tx() as c:
            existing=c.execute("SELECT * FROM provider_reports WHERE id=?",(report_id,)).fetchone()
            if existing is not None:
                if (existing["bucket_id"]!=bucket_id or existing["observed_at"]!=observed_at
                    or existing["consumed"]!=cumulative or existing["covered_local"]!=covered_local
                    or existing["coverage_evidence"]!=coverage_evidence):
                    raise Rejected("REPORT_ID_COLLISION")
                return {"duplicate":True}
            b=c.execute("SELECT * FROM buckets WHERE id=?",(bucket_id,)).fetchone()
            if b is None:raise Rejected("UNKNOWN_BUCKET")
            if b["kind"]!="CONSUMABLE":raise Rejected("CONCURRENT_BUCKET_HAS_NO_USAGE_METER")
            if covered_local>b["locally_consumed"]:raise Rejected("INVALID_COVERAGE")
            c.execute("""INSERT INTO provider_reports(id,bucket_id,observed_at,consumed,source,covered_local,coverage_evidence)
                         VALUES(?,?,?,?,?,?,?)""",(report_id,bucket_id,observed_at,cumulative,source,covered_local,coverage_evidence))
            applied=b["provider_observed_at"] is None or observed_at>b["provider_observed_at"]
            if applied:
                c.execute("""UPDATE buckets SET provider_consumed=?,provider_observed_at=?,
                             provider_covered_local=? WHERE id=?""",(cumulative,observed_at,covered_local,bucket_id))
                self._bump(c)
            self._event(c,"PROVIDER_REPORTED",source,
                        {"bucket_id":bucket_id,"cumulative":cumulative,"applied":applied,
                         "covered_local":covered_local,"coverage_evidence":coverage_evidence})
            return {"duplicate":False,"applied":applied}

    def manual_correction(self, *, correction_id, job_id, bucket_id, quantity, reason, evidence, actor):
        # Only observational attribution. It cannot increase budgets or override frozen state.
        require_id(correction_id,"correction_id")
        for k,v in (("job_id",job_id),("bucket_id",bucket_id),("actor",actor)):
            require_id(v,k)
        if not isinstance(reason,str) or len(reason.strip())<5 or not isinstance(evidence,str) or not evidence.strip():
            raise ValueError("reason and evidence required")
        integer(quantity,"quantity")
        with self._tx() as c:
            if c.execute("SELECT 1 FROM corrections WHERE id=?",(correction_id,)).fetchone():
                return {"duplicate":True}
            if not c.execute("SELECT 1 FROM claims WHERE job_id=? AND bucket_id=?",(job_id,bucket_id)).fetchone():
                raise Rejected("UNKNOWN_CLAIM")
            c.execute("""INSERT INTO corrections(id,job_id,bucket_id,quantity,reason,evidence,actor,recorded_at)
                         VALUES(?,?,?,?,?,?,?,?)""",(correction_id,job_id,bucket_id,quantity,reason,evidence,actor,utc_now()))
            self._event(c,"CORRECTION_RECORDED","manual",{"id":correction_id,"quantity":quantity,
                        "bucket_id":bucket_id,"reason":reason,"evidence":evidence,"actor":actor},job_id)
            return {"duplicate":False}

    def adjust_usage(self, *, adjustment_id, job_id, bucket_id, new_quantity,
                     reason, evidence, actor):
        """Authorized append-only amendment of a terminal job's accounting.

        Original 'observed' remains untouched. Actual provider reports remain separate.
        Caller must authenticate the privileged actor at the API boundary.
        """
        require_id(adjustment_id,"adjustment_id")
        require_id(job_id,"job_id");require_id(bucket_id,"bucket_id")
        require_id(actor,"actor");integer(new_quantity,"new_quantity")
        if not isinstance(reason,str) or len(reason.strip())<5 or not isinstance(evidence,str) or not evidence.strip():
            raise ValueError("evidence and reason required")
        with self._tx() as c:
            old=c.execute("SELECT * FROM usage_adjustments WHERE id=?",(adjustment_id,)).fetchone()
            if old is not None:
                if (old["job_id"]!=job_id or old["bucket_id"]!=bucket_id or
                    old["new_quantity"]!=new_quantity or old["reason"]!=reason or
                    old["evidence"]!=evidence or old["actor"]!=actor):
                    raise Rejected("ADJUSTMENT_ID_COLLISION")
                return {"duplicate":True}
            j=c.execute("SELECT state FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"] not in ("COMPLETED","FAILED","CANCELLED"):
                raise Rejected("JOB_NOT_FINALIZED")
            claim=c.execute("SELECT * FROM claims WHERE job_id=? AND bucket_id=?",(job_id,bucket_id)).fetchone()
            if claim is None:raise Rejected("UNKNOWN_CLAIM")
            bucket=c.execute("SELECT * FROM buckets WHERE id=?",(bucket_id,)).fetchone()
            if bucket["kind"]!="CONSUMABLE":raise Rejected("NONCONSUMABLE_ADJUSTMENT")
            prior=claim["corrected"] if claim["corrected"] is not None else claim["observed"]
            delta=new_quantity-prior
            resulting=bucket["locally_consumed"]+delta
            if resulting<bucket["provider_covered_local"]:
                raise Rejected("PROVIDER_COVERAGE_CONFLICT")
            if resulting<0:raise Rejected("NEGATIVE_ACCOUNT_USAGE")
            c.execute("UPDATE claims SET corrected=? WHERE job_id=? AND bucket_id=?",
                      (new_quantity,job_id,bucket_id))
            c.execute("UPDATE buckets SET locally_consumed=locally_consumed+? WHERE id=?",
                      (delta,bucket_id))
            if new_quantity>claim["quantity"]:
                c.execute("UPDATE buckets SET frozen=1 WHERE id=?",(bucket_id,))
            c.execute("""INSERT INTO usage_adjustments(id,job_id,bucket_id,previous,
                        new_quantity,reason,evidence,actor,recorded_at)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                      (adjustment_id,job_id,bucket_id,prior,new_quantity,reason,evidence,actor,utc_now()))
            self._event(c,"USAGE_ADJUSTED","manual",
                        {"adjustment_id":adjustment_id,"bucket_id":bucket_id,
                         "previous":prior,"new_quantity":new_quantity,"reason":reason,
                         "evidence":evidence,"actor":actor},job_id)
            self._bump(c)
            return {"duplicate":False,"delta":delta,"previous":prior,"new_quantity":new_quantity}

    def status(self, job_id):
        with self._tx() as c:
            j=c.execute("SELECT id,attempt_id,state,external_id,reason FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            claims=c.execute("SELECT bucket_id,quantity,observed,corrected FROM claims WHERE job_id=? ORDER BY bucket_id",(job_id,)).fetchall()
            return {"job":dict(j),"claims":[dict(x) for x in claims]}

    def events(self, job_id=None):
        with self._tx() as c:
            rows=c.execute("SELECT * FROM events WHERE job_id=? ORDER BY seq",(job_id,)).fetchall() if job_id else c.execute("SELECT * FROM events ORDER BY seq").fetchall()
            return [dict(r) for r in rows]

    def unresolved_launches(self):
        with self._tx() as c:
            return [dict(r) for r in c.execute("SELECT id,attempt_id,state FROM jobs WHERE state='LAUNCH_PENDING'")]

    def reconcile_bucket(self, bucket_id, *, now=None):
        view={b["id"]:b for b in self.snapshot(now=now)["buckets"]}
        if bucket_id not in view:raise Rejected("UNKNOWN_BUCKET")
        b=view[bucket_id]
        return {"bucket_id":bucket_id,"local_consumed":b["local_consumed"],
                "provider_consumed":b["provider_consumed"],
                "difference":None if b["provider_consumed"] is None else b["provider_consumed"]-b["provider_covered_local"],
                "overlap_unverified":b["provider_consumed"] is not None and b["provider_covered_local"]==0,
                "unattributed_possible":b["provider_consumed"] is not None and b["provider_consumed"]>b["provider_covered_local"],
                "available":b["available"],"frozen":b["frozen"],"fresh":b["fresh"]}


class MockLauncher:
    """Deterministic provider emulator with its own durable database.

    A repeated attempt ID returns the same external job ID. No paid/cloud calls.
    """

    def __init__(self, path):
        self.path=str(path)
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path)
        try:
            c.execute("CREATE TABLE IF NOT EXISTS launches(attempt_id TEXT PRIMARY KEY, external_id TEXT NOT NULL)")
            c.commit()
        finally:c.close()

    def launch(self, attempt_id):
        require_id(attempt_id,"attempt_id")
        c=sqlite3.connect(self.path,timeout=20,isolation_level=None)
        try:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT external_id FROM launches WHERE attempt_id=?",(attempt_id,)).fetchone()
            ext=row[0] if row else "mock-"+uuid.uuid5(uuid.NAMESPACE_URL,attempt_id).hex
            if row is None:c.execute("INSERT INTO launches VALUES(?,?)",(attempt_id,ext))
            c.commit()
            return ext
        finally:c.close()

    def lookup(self, attempt_id):
        c=sqlite3.connect(self.path)
        try:
            row=c.execute("SELECT external_id FROM launches WHERE attempt_id=?",(attempt_id,)).fetchone()
            return row[0] if row else None
        finally:c.close()


def run_mock(control, launcher, job_id, token, *, now=None, crash_after_external=False):
    """At-least-once adapter invocation with idempotent external operation ID."""
    prep=control.launch_prepare(job_id,token=token,now=now)
    ext=launcher.launch(prep["attempt_id"])
    if crash_after_external:
        raise RuntimeError("synthetic crash after external launch")
    control.launch_confirm(job_id,external_id=ext)
    return ext


def recover_mock(control, launcher):
    """Query provider by attempt, never blindly create another external job."""
    results=[]
    for j in control.unresolved_launches():
        ext=launcher.lookup(j["attempt_id"])
        if ext is None:
            results.append({"job_id":j["id"],"state":"UNKNOWN_EXTERNAL_LAUNCH"})
        else:
            control.launch_confirm(j["id"],external_id=ext)
            results.append({"job_id":j["id"],"state":"RUNNING","external_id":ext})
    return results
