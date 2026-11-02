#!/usr/bin/env python3
"""Passive OpenCode Zen catalog refresh for the ASES resource controller.

No inference calls and no account credentials. Public catalog presence is not
account entitlement. HTTPS host is pinned. Fetch failure keeps the prior cache.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib import request
from urllib.parse import urlparse

URL = "https://opencode.ai/zen/v1/models"
MAX_BYTES = 4 * 1024 * 1024
DEFAULT_TTL = 24 * 60 * 60


def normalize(payload: bytes) -> tuple[dict, list[str], str]:
    if len(payload) > MAX_BYTES:
        raise ValueError("catalog response exceeds 4 MiB")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("catalog response is not an object")
    models = data.get("data", data.get("models"))
    if not isinstance(models, list) or len(models) > 10000:
        raise ValueError("catalog requires a bounded data/models list")
    ids = []
    for model in models:
        if not isinstance(model, dict) or not isinstance(model.get("id"), str):
            raise ValueError("catalog contains model without ID")
        mid = model["id"]
        if not mid or len(mid) > 160 or not all(c.isalnum() or c in "_-.:/" for c in mid):
            raise ValueError("invalid model ID")
        ids.append(mid)
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate model ID")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    return data, sorted(ids), digest


def fetch_catalog(opener=request.urlopen, timeout: float = 12.0) -> bytes:
    req = request.Request(
        URL,
        headers={"User-Agent": "ASES-resource-control/0.1 (passive catalog check)",
                 "Accept": "application/json"},
        method="GET",
    )
    with opener(req, timeout=timeout) as response:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname != "opencode.ai":
            raise ValueError("catalog response redirected to untrusted host")
        if response.status != 200:
            raise ValueError(f"catalog HTTP status {response.status}")
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("oversized provider response")
        return raw


def cached_manifest(cache: Path) -> dict | None:
    path = cache / "latest.json"
    if not path.exists():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("manifest not object")
        return doc
    except (ValueError, OSError):
        return None


def persist(cache: Path, data: dict, ids: list[str], digest: str, fetched_at: int) -> dict:
    """Immutable content-addressed gzip blob, with read-back *before* latest pointer."""
    cache.mkdir(parents=True, exist_ok=True)
    prior = cached_manifest(cache)
    filename = digest + ".json.gz"
    destination = cache / filename
    if not destination.exists():
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as f:
            temp = Path(f.name)
            try:
                with gzip.GzipFile(fileobj=f, mode="wb", mtime=0) as z:
                    z.write(canonical)
                f.flush()
                os.fsync(f.fileno())
            except BaseException:
                temp.unlink(missing_ok=True)
                raise
        os.replace(temp, destination)
    with gzip.open(destination, "rb") as f:
        read_back = f.read(MAX_BYTES + 1)
    if hashlib.sha256(read_back).hexdigest() != digest:
        raise ValueError("catalog cache failed read-back hash verification")
    previous = set(prior.get("model_ids", [])) if prior else set()
    manifest = {
        "provider": "opencode-zen", "source": URL, "sha256": digest,
        "fetched_at": fetched_at, "model_ids": ids,
        "added": sorted(set(ids) - previous),
        "removed": sorted(previous - set(ids)),
        "changed": prior is None or prior.get("sha256") != digest,
        "archive": filename, "source_type": "public_catalog_not_entitlement",
        "verified": "local_sha256_readback_only",
        "controller_synced": False,
    }
    target = cache / "latest.json"
    with tempfile.NamedTemporaryFile(dir=cache, mode="w", encoding="utf-8", delete=False) as f:
        temp = Path(f.name)
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, target)
    return manifest



def read_cached(cache: Path, manifest: dict) -> dict:
    archive = cache / manifest["archive"]
    if archive.name != manifest["archive"]:
        raise ValueError("unsafe archive path")
    with gzip.open(archive, "rb") as stream:
        content = stream.read(MAX_BYTES + 1)
    data, _, digest = normalize(content)
    if digest != manifest["sha256"]:
        raise ValueError("cached catalog hash mismatch")
    return data


def mark_synced(cache: Path, manifest: dict) -> dict:
    manifest = {**manifest, "controller_synced": True}
    with tempfile.NamedTemporaryFile(dir=cache, mode="w", encoding="utf-8",
                                     delete=False) as f:
        temp = Path(f.name)
        json.dump(manifest, f, sort_keys=True, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, cache / "latest.json")
    return manifest


def forward(controller: str, db: str, message: dict) -> dict:
    completed = subprocess.run(
        [controller, db, "request", "-"],
        input=json.dumps(message), capture_output=True, text=True,
        timeout=20, check=False,
    )
    if completed.returncode:
        raise RuntimeError("controller rejected catalog event: " + completed.stderr[:1000])
    return json.loads(completed.stdout)


def check(cache: Path, ttl: int = DEFAULT_TTL, force: bool = False,
          opener=request.urlopen, clock=time.time, controller: str | None = None,
          db: str | None = None) -> dict:
    if (controller is None) != (db is None):
        raise ValueError("controller and DB must be specified together")
    current = cached_manifest(cache)
    timestamp = int(clock())
    if not force and current and timestamp >= current.get("fetched_at", 0) and (
        timestamp - current.get("fetched_at", 0) < ttl
    ):
        try:
            data = read_cached(cache, current)
            if controller is not None and db is not None and not current.get("controller_synced"):
                forward(controller, db, {
                    "op": "import_catalog",
                    "catalog": {"provider": "opencode-zen", "source_url": URL,
                                "retrieved_at": current["fetched_at"], "payload": data},
                })
                current = mark_synced(cache, current)
            return {**current, "refresh": "CACHE_FRESH"}
        except (ValueError, OSError, KeyError):
            # Corrupted cache is never considered a successful catalog observation.
            pass
    try:
        data, ids, digest = normalize(fetch_catalog(opener=opener))
        result = persist(cache, data, ids, digest, timestamp)
        if controller is not None and db is not None:
            forward(controller, db, {
                "op": "import_catalog",
                "catalog": {"provider": "opencode-zen", "source_url": URL,
                            "retrieved_at": timestamp, "payload": data},
            })
            result = mark_synced(cache, result)
        return {**result, "refresh": "SUCCESS"}
    except Exception as exc:
        message = f"{type(exc).__name__}: {str(exc)[:350]}"
        if controller is not None and db is not None:
            try:
                forward(controller, db, {"op": "catalog_failure",
                                         "provider": "opencode-zen",
                                         "description": message})
            except Exception:
                # The original failure is primary; do not fabricate a recorded failure.
                message += "; controller_failure_record_unverified"
        return {"refresh": "FAILED", "error": message,
                "prior_catalog_preserved": current is not None,
                "prior_digest": current.get("sha256") if current else None,
                "availability": "UNKNOWN"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cache", required=True, type=Path)
    p.add_argument("--ttl", type=int, default=DEFAULT_TTL)
    p.add_argument("--force", action="store_true")
    p.add_argument("--controller", default=None)
    p.add_argument("--db", default=None)
    args = p.parse_args()
    if args.ttl < 0:
        p.error("TTL must be nonnegative")
    result = check(args.cache, ttl=args.ttl, force=args.force,
                   controller=args.controller, db=args.db)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["refresh"] != "FAILED" else 2


if __name__ == "__main__":
    sys.exit(main())
