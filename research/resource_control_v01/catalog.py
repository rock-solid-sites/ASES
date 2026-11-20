"""Passive provider model-catalog monitor, independent of inference and routing.

This process retrieves public/provider-authorized metadata only. It deliberately
never invokes model inference or claims model availability based on a listing.
"""
import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from control import canonical, require_id, Rejected


def normalized_models(body):
    """Require a normalized adapter result; never guess unknown vendor schema."""
    if not isinstance(body,dict) or not isinstance(body.get("models"),list):
        raise ValueError("adapter must return a models list")
    out={}
    for model in body["models"]:
        if not isinstance(model,dict):
            raise ValueError("invalid model")
        name=require_id(model.get("id"),"model id")
        if name in out:raise ValueError("duplicate model id")
        free=model.get("free")
        if free not in (True,False,None):raise ValueError("invalid free flag")
        advertised=model.get("unlimited_advertised")
        if advertised not in (True,False,None):raise ValueError("invalid advertised limit")
        price=model.get("price_micros_per_million")
        if price is not None and (type(price) is not int or price<0):
            raise ValueError("invalid price")
        context=model.get("context_tokens")
        if context is not None and (type(context) is not int or context<=0):
            raise ValueError("invalid context")
        out[name]={"free":free,"unlimited_advertised":advertised,
                   "price_micros_per_million":price,"context_tokens":context}
    return out


def fetch_json(url, etag=None, last_modified=None, *, timeout=5):
    if not isinstance(url,str) or not url.startswith("https://"):
        raise ValueError("catalog URL must be HTTPS")
    headers={"Accept":"application/json"}
    if etag:headers["If-None-Match"]=etag
    if last_modified:headers["If-Modified-Since"]=last_modified
    try:
        with urlopen(Request(url,headers=headers),timeout=timeout) as response:
            data=response.read(5_000_001)
            if len(data)>5_000_000:raise ValueError("catalog too large")
            return response.status,dict(response.headers),data
    except HTTPError as e:
        if e.code==304:return 304,dict(e.headers),b""
        raise


class CatalogMonitor:
    def __init__(self, db):
        self.db=str(db)
        Path(self.db).parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.db)
        try:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS sources(
                    id TEXT PRIMARY KEY,url TEXT NOT NULL,etag TEXT,last_modified TEXT,
                    digest TEXT,content TEXT,checked_at INTEGER,success_at INTEGER,
                    last_error TEXT,ttl_seconds INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,source_id TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,kind TEXT NOT NULL,
                    digest TEXT,error TEXT,diff TEXT);
            """)
            c.commit()
        finally:c.close()

    @contextmanager
    def _tx(self):
        c=sqlite3.connect(self.db,timeout=20,isolation_level=None)
        c.row_factory=sqlite3.Row
        try:
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.commit()
        except Exception:
            if c.in_transaction:c.rollback()
            raise
        finally:c.close()

    def register(self, source_id, url, ttl_seconds=86400):
        require_id(source_id,"source id")
        if not isinstance(url,str) or not url.startswith("https://"):raise ValueError("HTTPS required")
        if type(ttl_seconds) is not int or ttl_seconds<1:raise ValueError("invalid TTL")
        with self._tx() as c:
            if c.execute("SELECT 1 FROM sources WHERE id=?",(source_id,)).fetchone():
                raise Rejected("SOURCE_EXISTS")
            c.execute("INSERT INTO sources(id,url,ttl_seconds) VALUES(?,?,?)",
                      (source_id,url,ttl_seconds))

    def state(self, source_id, now=None):
        stamp=int(time.time()) if now is None else now
        with self._tx() as c:
            row=c.execute("SELECT * FROM sources WHERE id=?",(source_id,)).fetchone()
            if row is None:raise Rejected("UNKNOWN_SOURCE")
            r=dict(row)
            return {"source_id":source_id,"url":r["url"],"etag":r["etag"],
                    "digest":r["digest"],"models":json.loads(r["content"]) if r["content"] else None,
                    "checked_at":r["checked_at"],"success_at":r["success_at"],
                    "stale":r["success_at"] is None or stamp>r["success_at"]+r["ttl_seconds"],
                    "last_error":r["last_error"]}

    def refresh(self, source_id, *, fetcher=fetch_json, adapter=None, now=None):
        stamp=int(time.time()) if now is None else now
        with self._tx() as c:
            row=c.execute("SELECT * FROM sources WHERE id=?",(source_id,)).fetchone()
            if row is None:raise Rejected("UNKNOWN_SOURCE")
            previous=dict(row)
        # Network fetch is outside the SQLite write transaction.
        try:
            status,headers,raw=fetcher(previous["url"],previous["etag"],previous["last_modified"])
            if status not in (200,304):raise ValueError("bad catalog status")
            if status==304:
                if previous["content"] is None:raise ValueError("304 without cached catalog")
                with self._tx() as c:
                    c.execute("UPDATE sources SET checked_at=?,success_at=?,last_error=NULL WHERE id=?",
                              (stamp,stamp,source_id))
                    c.execute("INSERT INTO history(source_id,timestamp,kind,digest) VALUES(?,?,?,?)",
                              (source_id,stamp,"NOT_MODIFIED",previous["digest"]))
                return {"status":"NOT_MODIFIED","models":len(json.loads(previous["content"]))}
            if len(raw)>5_000_000:raise ValueError("catalog too large")
            decoded=json.loads(raw)
            normalized=normalized_models(adapter(decoded) if adapter else decoded)
            serialized=canonical(normalized)
            new_digest=hashlib.sha256(serialized.encode()).hexdigest()
            old=json.loads(previous["content"]) if previous["content"] else {}
            diff={"added":sorted(set(normalized)-set(old)),
                  "removed":sorted(set(old)-set(normalized)),
                  "changed":sorted(k for k in set(old)&set(normalized) if old[k]!=normalized[k])}
            changed=new_digest!=previous["digest"]
            # A delayed older fetch may not overwrite a newer successful snapshot.
            with self._tx() as c:
                current=c.execute("SELECT success_at FROM sources WHERE id=?",(source_id,)).fetchone()
                if current["success_at"] is not None and current["success_at"]>stamp:
                    return {"status":"STALE_FETCH_DISCARDED"}
                c.execute("""UPDATE sources SET checked_at=?,success_at=?,last_error=NULL,
                            etag=?,last_modified=?,content=?,digest=? WHERE id=?""",
                          (stamp,stamp,headers.get("ETag"),headers.get("Last-Modified"),
                           serialized,new_digest,source_id))
                c.execute("""INSERT INTO history(source_id,timestamp,kind,digest,diff)
                             VALUES(?,?,?,?,?)""",
                          (source_id,stamp,"CHANGED" if changed else "UNCHANGED",
                           new_digest,canonical(diff)))
            return {"status":"CHANGED" if changed else "UNCHANGED","diff":diff,
                    "models":len(normalized),"digest":new_digest}
        except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
            # Fail without erasing previously known models, and keep the failure.
            with self._tx() as c:
                c.execute("UPDATE sources SET checked_at=?,last_error=? WHERE id=?",
                          (stamp,str(exc)[:250],source_id))
                c.execute("INSERT INTO history(source_id,timestamp,kind,error) VALUES(?,?,?,?)",
                          (source_id,stamp,"FETCH_ERROR",str(exc)[:250]))
            return {"status":"FETCH_ERROR","error":str(exc)[:250]}

    def history(self, source_id):
        with self._tx() as c:
            return [dict(x) for x in c.execute("SELECT * FROM history WHERE source_id=? ORDER BY id",(source_id,))]
