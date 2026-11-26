#!/usr/bin/env python3
"""Delete only explicitly approved, unchanged CodeGraph archive versions."""
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
CLI = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+\Z")

def approvals(data, protected):
    if not isinstance(data, list) or not 1 <= len(data) <= 50:
        raise ValueError("expected 1-50 approved snapshots")
    result = {}
    for item in data:
        if not isinstance(item, dict) or set(item) != {"repository", "commit", "cli", "bytes"}:
            raise ValueError("invalid approved entry")
        repo, sha, cli, size = (item[k] for k in ("repository", "commit", "cli", "bytes"))
        if not all(isinstance(s, str) for s in (repo, sha, cli)) or not REPO.fullmatch(repo) or any(p in (".", "..") for p in repo.split("/")) or not SHA.fullmatch(sha) or not CLI.fullmatch(cli) or type(size) is not int or size <= 0:
            raise ValueError("invalid approved identity or size")
        if (repo, sha) in protected:
            raise ValueError("protected snapshot")
        key = f"codegraph/v1/{repo}/{sha}/codegraph-{cli}-linux-x64.tar.gz"
        if key in result:
            raise ValueError("duplicate approval")
        result[key] = size
    return result

def preflight(payload, key, expected):
    if not isinstance(payload, dict) or payload.get("IsTruncated") or any(payload.get(k) for k in ("NextToken", "NextKeyMarker", "NextVersionIdMarker")):
        raise ValueError("incomplete version listing")
    versions = [v for v in payload.get("Versions", []) if v["Key"] == key]
    markers = [v for v in payload.get("DeleteMarkers", []) if v["Key"] == key]
    if not versions and not markers:
        return None
    if markers or len(versions) != 1:
        raise ValueError("object versions changed; reapproval required")
    v = versions[0]
    if v.get("IsLatest") is not True or v.get("Size") != expected or not isinstance(v.get("VersionId"), str) or not v["VersionId"] or v["VersionId"] == "null":
        raise ValueError("object identity changed; reapproval required")
    return v["VersionId"]

def run_approved(entries, list_versions, delete_version):
    # Check the entire batch before issuing any delete.
    selected = [(key, size, preflight(list_versions(key), key, size)) for key, size in entries.items()]
    for key, size, version in selected:
        if version is None:
            print(f"Already absent: {key}")
            continue
        # A newly uploaded version must not be silently included.
        if preflight(list_versions(key), key, size) != version:
            raise ValueError("version changed after preflight")
        delete_version(key, version)
        if preflight(list_versions(key), key, size) is not None:
            raise ValueError("approved object still present; check fresh inventory")
        print(f"Verified absent: {key} ({size} bytes)", flush=True)

def main():
    items = json.loads(os.environ["APPROVED_JSON"])
    config = json.loads(Path(".github/codegraph-cache-retention.json").read_text())
    protected = {(i["repository"], i["commit"]) for i in config["protected"]}
    entries = approvals(items, protected)
    bucket, region, endpoint = (os.environ[k] for k in ("B2_BUCKET", "B2_REGION", "B2_ENDPOINT"))
    if not all((bucket, region, endpoint, os.environ.get("AWS_ACCESS_KEY_ID"), os.environ.get("AWS_SECRET_ACCESS_KEY"))):
        raise ValueError("existing B2 configuration unavailable")
    def aws(action, *args):
        cmd = ["aws", "s3api", action, "--bucket", bucket, "--region", region, "--endpoint-url", endpoint, "--output", "json", *args]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if proc.returncode:
            # Do not print raw credentials or version IDs.
            code = "access denied" if re.search(r"AccessDenied|Unauthorized|Forbidden|403", proc.stderr, re.I) else "request failed"
            raise RuntimeError(f"B2 {action}: {code}")
        return json.loads(proc.stdout or "{}")
    run_approved(entries, lambda k: aws("list-object-versions", "--prefix", k),
                 lambda k, v: aws("delete-object", "--key", k, "--version-id", v))
    print("Approved batch complete; all requested keys absent.")

class Tests(unittest.TestCase):
    def setUp(self):
        self.item = {"repository":"a/b","commit":"a"*40,"cli":"1.6.2","bytes":12}
        self.entries = approvals([self.item], set())
        self.key = next(iter(self.entries))
        self.v = {"Key": self.key, "Size":12, "IsLatest":True, "VersionId":"opaque-1"}
    def test_protected(self):
        with self.assertRaises(ValueError):
            approvals([self.item], {("a/b","a"*40)})
    def test_validation(self):
        for item in ({**self.item,"repository":"../b"}, {**self.item,"commit":"main"}, {**self.item,"bytes":True}):
            with self.assertRaises(ValueError): approvals([item], set())
        with self.assertRaises(ValueError): approvals([self.item,self.item],set())
    def test_preflight(self):
        self.assertEqual(preflight({"Versions":[self.v]}, self.key, 12), "opaque-1")
        self.assertIsNone(preflight({}, self.key, 12))
        for data in ({"IsTruncated":True}, {"Versions":[self.v,self.v]}, {"Versions":[{**self.v,"Size":13}]}, {"DeleteMarkers":[{"Key":self.key}]}):
            with self.assertRaises(ValueError): preflight(data,self.key,12)
    def test_exact_delete_and_idempotence(self):
        state = [self.v, {**self.v,"Key":self.key+".other"}]
        calls = []
        def delete(k,v):
            calls.append((k,v))
            state[:] = [x for x in state if x["Key"] != k or x["VersionId"] != v]
        run_approved(self.entries, lambda k: {"Versions":list(state)}, delete)
        run_approved(self.entries, lambda k: {"Versions":list(state)}, delete)
        self.assertEqual(calls, [(self.key,"opaque-1")])
        self.assertEqual(len(state),1)
    def test_all_preflight_before_delete(self):
        second = {**self.item,"commit":"b"*40}
        entries = approvals([self.item,second],set())
        calls=[]
        with self.assertRaises(ValueError):
            run_approved(entries,lambda k: {"Versions":[self.v]} if k==self.key else {"IsTruncated":True}, lambda k,v: calls.append((k,v)))
        self.assertEqual(calls,[])
    def test_changed_after_preflight(self):
        listings=iter([{"Versions":[self.v]}, {"Versions":[{**self.v,"VersionId":"new"}]}])
        calls=[]
        with self.assertRaises(ValueError):
            run_approved(self.entries,lambda k: next(listings), lambda k,v: calls.append((k,v)))
        self.assertEqual(calls,[])

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 1:
        try:
            main()
        except (ValueError, KeyError, TypeError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
            # RuntimeError messages above are sanitized; input errors are generic.
            print("Cleanup stopped: " + (str(exc) if isinstance(exc,(ValueError,RuntimeError)) and not isinstance(exc,json.JSONDecodeError) else "invalid input or operation failure"), file=sys.stderr)
            sys.exit(1)
    else:
        raise SystemExit("Usage: codegraph-cache-delete.py [--self-test]")
