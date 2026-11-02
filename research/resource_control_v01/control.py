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
        with self._tx() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS buckets (
                    id TEXT PRIMARY KEY, account TEXT NOT NULL, provider TEXT NOT NULL,
                    product TEXT NOT NULL, period TEXT NOT NULL, unit TEXT NOT NULL,
                    allowance INTEGER NOT NULL CHECK (allowance>=0),
                    reserved INTEGER NOT NULL DEFAULT 0 CHECK (reserved>=0),
                    locally_consumed INTEGER NOT NULL DEFAULT 0 CHECK (locally_consumed>=0),
                    provider_consumed INTEGER, provider_observed_at INTEGER,
                    price_micros INTEGER, overage TEXT NOT NULL DEFAULT 'BLOCK',
                    refreshed_at INTEGER NOT NULL, ttl_seconds INTEGER NOT NULL,
                    frozen INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(account,provider,product,period,unit));
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, snapshot TEXT NOT NULL, estimate TEXT NOT NULL,
                    attempt_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL,
                    acknowledged TEXT, auth_token_hash TEXT, auth_expires INTEGER,
                    external_id TEXT, reason TEXT, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS claims (
                    job_id TEXT NOT NULL REFERENCES jobs(id), bucket_id TEXT NOT NULL REFERENCES buckets(id),
                    quantity INTEGER NOT NULL CHECK(quantity>=0),
                    observed INTEGER NOT NULL DEFAULT 0 CHECK(observed>=0),
                    PRIMARY KEY(job_id,bucket_id));
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
                    job_id TEXT, kind TEXT NOT NULL, observed_at TEXT NOT NULL,
                    source TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS provider_reports (
                    id TEXT PRIMARY KEY, bucket_id TEXT NOT NULL, observed_at INTEGER NOT NULL,
                    consumed INTEGER NOT NULL CHECK(consumed>=0), source TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS corrections (
                    id TEXT PRIMARY KEY, job_id TEXT, bucket_id TEXT, quantity INTEGER,
                    reason TEXT NOT NULL, evidence TEXT NOT NULL, actor TEXT NOT NULL,
                    recorded_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS policies (
                    id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL);
                INSERT OR IGNORE INTO policies(id,revision) VALUES(1,0);
            """)

    @contextmanager
    def _tx(self):
        c = sqlite3.connect(self.db, timeout=20, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("PRAGMA busy_timeout=20000")
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
        p = b["provider_consumed"]
        spent = max(b["locally_consumed"], p if p is not None else 0)
        return b["allowance"] - spent - b["reserved"]

    @staticmethod
    def _fresh(b, now):
        return b["ttl_seconds"] > 0 and b["refreshed_at"] + b["ttl_seconds"] >= now

    def register_bucket(self, *, bucket_id, account, provider, product, period, unit,
                        allowance, price_micros=0, overage="BLOCK", ttl_seconds=3600,
                        observed_at=None):
        ids = [bucket_id, account, provider, product, period, unit]
        for label, value in zip(("bucket_id","account","provider","product","period","unit"), ids):
            require_id(value, label)
        integer(allowance, "allowance")
        integer(ttl_seconds, "ttl_seconds", 1)
        if price_micros is not None:
            integer(price_micros, "price_micros")
        if overage not in ("BLOCK", "ALLOW_EXPLICIT"):
            raise ValueError("invalid overage")
        stamp = integer(observed_at if observed_at is not None else int(time.time()), "observed_at")
        with self._tx() as c:
            if c.execute("SELECT 1 FROM buckets WHERE id=?", (bucket_id,)).fetchone():
                raise Rejected("DUPLICATE_BUCKET")
            c.execute("""INSERT INTO buckets(id,account,provider,product,period,unit,
                allowance,price_micros,overage,refreshed_at,ttl_seconds)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (bucket_id,account,provider,product,period,unit,allowance,
                 price_micros,overage,stamp,ttl_seconds))
            self._bump(c)
            self._event(c,"BUCKET_REGISTERED","registry",{"bucket_id":bucket_id})

    def snapshot(self, account=None, *, now=None):
        stamp = int(time.time()) if now is None else integer(now, "now")
        with self._tx() as c:
            q = "SELECT * FROM buckets" + (" WHERE account=?" if account is not None else "")
            rows = c.execute(q, (require_id(account, "account"),) if account else ()).fetchall()
            records = []
            for b in rows:
                records.append({
                    "id":b["id"],"account":b["account"],"provider":b["provider"],
                    "product":b["product"],"period":b["period"],"unit":b["unit"],
                    "allowance":b["allowance"],"available":self._capacity(b),
                    "reserved":b["reserved"],"local_consumed":b["locally_consumed"],
                    "provider_consumed":b["provider_consumed"],
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
        return {"revision":view["revision"],"snapshot_digest":digest(view),
                "claims":normalized,"estimate":estimate,"issues":issues,
                "eligible":not issues}

    def reserve(self, *, job_id, attempt_id, quote, account, now=None):
        require_id(job_id,"job_id");require_id(attempt_id,"attempt_id");require_id(account,"account")
        if not isinstance(quote,dict) or not quote.get("eligible") or quote.get("issues"):
            raise Rejected("INVALID_QUOTE")
        claims = self._normalize_claims(quote.get("claims"))
        stamp = int(time.time()) if now is None else integer(now,"now")
        with self._tx() as c:
            if c.execute("SELECT 1 FROM jobs WHERE id=? OR attempt_id=?", (job_id,attempt_id)).fetchone():
                raise Rejected("DUPLICATE_JOB_OR_ATTEMPT")
            if quote.get("revision") != self._revision(c):
                raise Rejected("STALE_REVISION")
            rows = {b["id"]:b for b in c.execute("SELECT * FROM buckets WHERE account=?", (account,))}
            # This digest binds the complete account-scoped view, not a self-asserted subset.
            view = {"revision":self._revision(c),"buckets":sorted([{
                "id":b["id"],"account":b["account"],"provider":b["provider"],
                "product":b["product"],"period":b["period"],"unit":b["unit"],
                "allowance":b["allowance"],"available":self._capacity(b),
                "reserved":b["reserved"],"local_consumed":b["locally_consumed"],
                "provider_consumed":b["provider_consumed"],"price_micros":b["price_micros"],
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
            c.execute("""INSERT INTO jobs(id,snapshot,estimate,attempt_id,state,created_at)
                    VALUES(?,?,?,?,?,?)""",(job_id,quote["snapshot_digest"],
                    canonical(quote["estimate"]),attempt_id,"RESERVED",utc_now()))
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
            if c.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone():
                return {"duplicate":True}
            j=c.execute("SELECT state FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"] not in ("RUNNING","LAUNCH_PENDING","INTERRUPTED"):
                raise Rejected("INVALID_STATE")
            claim=c.execute("SELECT observed FROM claims WHERE job_id=? AND bucket_id=?",(job_id,bucket_id)).fetchone()
            if claim is None:raise Rejected("UNKNOWN_CLAIM")
            if cumulative < claim["observed"]:raise Rejected("NONMONOTONIC_LOCAL_OBSERVATION")
            c.execute("UPDATE claims SET observed=? WHERE job_id=? AND bucket_id=?",(cumulative,job_id,bucket_id))
            self._event(c,"USAGE_OBSERVED",source,{"bucket_id":bucket_id,"cumulative":cumulative},job_id,event_id)
            return {"duplicate":False,"observed":cumulative}

    def finalize(self, job_id, *, state, event_id):
        require_id(event_id,"event_id")
        if state not in ("COMPLETED","FAILED","CANCELLED","INTERRUPTED"):
            raise ValueError("invalid terminal state")
        with self._tx() as c:
            if c.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone():
                return {"duplicate":True}
            j=c.execute("SELECT state FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            if j["state"] not in ("RUNNING","LAUNCH_PENDING","INTERRUPTED","AUTHORIZED","RESERVED"):
                raise Rejected("INVALID_STATE")
            claims=c.execute("SELECT * FROM claims WHERE job_id=?",(job_id,)).fetchall()
            overruns=[]
            for claim in claims:
                bid=claim["bucket_id"];reserved=claim["quantity"];used=claim["observed"]
                c.execute("""UPDATE buckets SET reserved=reserved-?,locally_consumed=locally_consumed+?
                             WHERE id=?""",(reserved,used,bid))
                if used>reserved:
                    overruns.append({"bucket_id":bid,"overrun":used-reserved})
                    c.execute("UPDATE buckets SET frozen=1 WHERE id=?",(bid,))
            c.execute("UPDATE jobs SET state=? WHERE id=?",(state,job_id))
            self._event(c,"FINALIZED","controller",{"state":state,"overruns":overruns},job_id,event_id)
            self._bump(c)
            return {"duplicate":False,"state":state,"overruns":overruns}

    def provider_report(self, *, report_id, bucket_id, cumulative, observed_at, source="provider"):
        require_id(report_id,"report_id");require_id(bucket_id,"bucket_id")
        integer(cumulative,"cumulative");integer(observed_at,"observed_at")
        with self._tx() as c:
            if c.execute("SELECT 1 FROM provider_reports WHERE id=?",(report_id,)).fetchone():
                return {"duplicate":True}
            b=c.execute("SELECT * FROM buckets WHERE id=?",(bucket_id,)).fetchone()
            if b is None:raise Rejected("UNKNOWN_BUCKET")
            c.execute("""INSERT INTO provider_reports(id,bucket_id,observed_at,consumed,source)
                         VALUES(?,?,?,?,?)""",(report_id,bucket_id,observed_at,cumulative,source))
            applied=b["provider_observed_at"] is None or observed_at>b["provider_observed_at"]
            if applied:
                c.execute("""UPDATE buckets SET provider_consumed=?,provider_observed_at=?,
                             refreshed_at=? WHERE id=?""",(cumulative,observed_at,observed_at,bucket_id))
                self._bump(c)
            self._event(c,"PROVIDER_REPORTED",source,
                        {"bucket_id":bucket_id,"cumulative":cumulative,"applied":applied})
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

    def status(self, job_id):
        with self._tx() as c:
            j=c.execute("SELECT id,attempt_id,state,external_id,reason FROM jobs WHERE id=?",(job_id,)).fetchone()
            if j is None:raise Rejected("UNKNOWN_JOB")
            claims=c.execute("SELECT bucket_id,quantity,observed FROM claims WHERE job_id=? ORDER BY bucket_id",(job_id,)).fetchall()
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
                "difference":None if b["provider_consumed"] is None else b["provider_consumed"]-b["local_consumed"],
                "unattributed_possible":b["provider_consumed"] is not None and b["provider_consumed"]>b["local_consumed"],
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
