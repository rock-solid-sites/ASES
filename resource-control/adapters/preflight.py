#!/usr/bin/env python3
"""Mechanical session preflight: consume a scoped snapshot, refresh supported
public catalogs via a trusted controller, emit only exceptions to orchestrator.

This cannot authenticate accounts or discover private usage for unsupported
providers. Launch authorization remains a separate durable Rust transaction.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import socket
import sys
from typing import Any

import opencode_zen


def call_gateway(path: Path, request: dict) -> dict:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(8)
        client.connect(str(path))
        client.sendall(json.dumps(request).encode())
        client.shutdown(socket.SHUT_WR)
        out = bytearray()
        while True:
            part = client.recv(65536)
            if not part:
                break
            out.extend(part)
            if len(out) > 5 * 1024 * 1024:
                raise ValueError("gateway response exceeds 5 MiB")
    data = json.loads(out)
    if not data.get("ok"):
        raise RuntimeError("preflight gateway refused: " + str(data.get("error", "unknown")))
    return data["result"]


def classify(snapshot: dict, catalog_states: list[dict], refresh: dict) -> dict:
    exceptions: list[dict] = []
    for b in snapshot.get("balances", []):
        if not b.get("fresh", False):
            exceptions.append({"kind": "STALE_ENTITLEMENT", "meter": b.get("meter_id")})
        elif b.get("available", 0) < 0:
            exceptions.append({"kind": "RESOURCE_DEFICIT", "meter": b.get("meter_id"),
                               "units": -b["available"]})
        if b.get("provider_reported") is None:
            exceptions.append({"kind": "PROVIDER_USAGE_UNOBSERVED", "meter": b.get("meter_id"),
                               "severity": "informational"})
    for catalog in catalog_states:
        if not catalog.get("fresh", False):
            exceptions.append({"kind": "STALE_MODEL_CATALOG", "provider": catalog.get("provider")})
        if catalog.get("last_error"):
            exceptions.append({"kind": "CATALOG_FETCH_FAILURE",
                               "provider": catalog.get("provider"),
                               "detail": catalog["last_error"]})
    if refresh.get("refresh") == "FAILED":
        exceptions.append({"kind": "CATALOG_REFRESH_FAILED", "provider": "opencode-zen",
                           "detail": refresh.get("error")})
    return {"resource_catalog_version": snapshot.get("catalog_version"),
            "balances": snapshot.get("balances", []),
            "catalogs": catalog_states,
            "exceptions": exceptions,
            "authorization": "NOT_GRANTED_BY_PREFLIGHT",
            "launch_requires_revision_bound_reservation": True}


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--socket",required=True,type=Path)
    p.add_argument("--cache",required=True,type=Path)
    p.add_argument("--catalog-ttl",type=int,default=86400)
    p.add_argument("--controller",default=None,
                   help="trusted local controller binary; do not expose to orchestrator UID")
    p.add_argument("--db",default=None)
    args=p.parse_args()
    if args.catalog_ttl<0:
        p.error("catalog TTL cannot be negative")
    if (args.controller is None)!=(args.db is None):
        p.error("controller and DB must be supplied together")
    refresh=opencode_zen.check(
        args.cache,ttl=args.catalog_ttl,controller=args.controller,db=args.db)
    try:
        snapshot=call_gateway(args.socket,{"op":"snapshot"})
        state=call_gateway(args.socket,{"op":"catalog_states","ttl_seconds":args.catalog_ttl})
        result=classify(snapshot,state["catalogs"],refresh)
        result["catalog_refresh"]=refresh.get("refresh")
        if args.controller is None:
            result["exceptions"].append({"kind":"CATALOG_CONTROLLER_SYNC_NOT_VERIFIED",
                                         "detail":"read-only client has no entitlement-update authority"})
        print(json.dumps(result,sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc),
                          "authorization":"NOT_GRANTED"},sort_keys=True))
        return 2


if __name__=="__main__":
    sys.exit(main())
