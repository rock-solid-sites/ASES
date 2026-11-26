#!/usr/bin/env python3
"""Summarize completed B2 object versions; never download, transfer or delete."""
import datetime as dt
import json
import re
import sys
import unittest
from collections import defaultdict

PREFIX = "codegraph/v1/"
LIMIT = 5_000_000_000
KEY = re.compile(r"codegraph/v1/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/([0-9a-f]{40})/codegraph-([0-9]+\.[0-9]+\.[0-9]+)-linux-x64\.tar\.gz\Z")

def inventory(payload):
    if not isinstance(payload, dict) or payload.get("IsTruncated") or any(
        payload.get(k) for k in ("NextToken", "NextKeyMarker", "NextVersionIdMarker")
    ):
        raise ValueError("incomplete or invalid listing")
    versions = payload.get("Versions", [])
    markers = payload.get("DeleteMarkers", [])
    if not isinstance(versions, list) or not isinstance(markers, list):
        raise ValueError("invalid versions or markers")
    groups = defaultdict(lambda: {"bytes": 0, "current_bytes": 0, "versions": 0, "latest_upload": "", "earliest_upload": ""})
    total = current = unknown = 0
    for v in versions:
        key, size, latest = v["Key"], v["Size"], v["IsLatest"]
        if not isinstance(key, str) or not key.startswith(PREFIX):
            raise ValueError("object outside expected prefix")
        if type(size) is not int or size < 0 or type(latest) is not bool:
            raise ValueError("invalid version size or latest flag")
        total += size
        if latest:
            current += size
        match = KEY.fullmatch(key)
        if not match:
            unknown += size
            continue
        # Only normalized, known public-cache identifiers are exported, not version IDs.
        repo, commit, cli = match.groups()
        if any(part in (".", "..") for part in repo.split("/")):
            unknown += size
            continue
        stamp = dt.datetime.fromisoformat(v["LastModified"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("missing timestamp offset")
        stamp = stamp.astimezone(dt.timezone.utc).isoformat()
        g = groups[(repo, commit, cli)]
        g["bytes"] += size
        g["current_bytes"] += size if latest else 0
        g["versions"] += 1
        g["latest_upload"] = max(g["latest_upload"], stamp)
        g["earliest_upload"] = min(g["earliest_upload"] or stamp, stamp)
    for marker in markers:
        if not isinstance(marker.get("Key"), str) or not marker["Key"].startswith(PREFIX):
            raise ValueError("delete marker outside expected prefix")
    rows = [
        {"repository": r, "commit": c, "cli": v, **data}
        for (r, c, v), data in sorted(groups.items())
    ]
    rows.sort(key=lambda r: (-r["bytes"], r["repository"], r["commit"], r["cli"]))
    return {
        "prefix": PREFIX, "threshold_bytes": LIMIT, "total_bytes": total,
        "current_bytes": current, "noncurrent_bytes": total-current,
        "unknown_layout_bytes": unknown, "versions": len(versions),
        "delete_markers": len(markers), "recognized_indexes": len(rows),
        "review_required": total >= LIMIT, "indexes": rows,
    }

class TestInventory(unittest.TestCase):
    def version(self, size, latest=True, key=None):
        return {"Key": key or PREFIX+"owner/repo/"+"a"*40+"/codegraph-1.6.2-linux-x64.tar.gz",
                "Size": size, "IsLatest": latest, "LastModified": "2026-11-26T00:00:00Z",
                "VersionId": "never-export"}
    def test_empty(self):
        self.assertFalse(inventory({})["review_required"])
    def test_threshold_and_versions(self):
        result = inventory({"Versions": [self.version(LIMIT-1), self.version(1, False)]})
        self.assertTrue(result["review_required"])
        self.assertEqual(result["noncurrent_bytes"], 1)
        self.assertEqual(result["indexes"][0]["versions"], 2)
        self.assertEqual(result["indexes"][0]["earliest_upload"], "2026-11-26T00:00:00+00:00")
        self.assertNotIn("never-export", json.dumps(result))
        self.assertFalse(inventory({"Versions": [self.version(LIMIT-1)]})["review_required"])
    def test_unknown_layout(self):
        result = inventory({"Versions": [self.version(10, key=PREFIX+"unknown")]})
        self.assertEqual(result["unknown_layout_bytes"], 10)
        self.assertEqual(result["indexes"], [])
    def test_incomplete(self):
        for value in ({"IsTruncated": True}, {"NextToken": "x"}, {"NextKeyMarker": "x"}):
            with self.assertRaises(ValueError):
                inventory(value)
    def test_wrong_prefix(self):
        with self.assertRaises(ValueError):
            inventory({"Versions":[self.version(1, key="other/private")]})

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 3:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                result = inventory(json.load(f))
            with open(sys.argv[2], "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
                f.write("\n")
            print("Inventory: {} bytes; {} current; {} noncurrent; {} versions; review_required={}".format(
                result["total_bytes"], result["current_bytes"], result["noncurrent_bytes"],
                result["versions"], result["review_required"]))
        except (ValueError, TypeError, KeyError, OSError):
            raise SystemExit("Invalid/incomplete cache inventory; no decision made")
    else:
        raise SystemExit("Usage: codegraph-cache-inventory.py input.json report.json | --self-test")
