#!/usr/bin/env python3
"""Read-only, evidence-based cache review. Never download or delete B2 objects."""
import base64
import datetime as dt
import json
import os
import re
import sys
import tomllib
import unittest
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
VERSION = re.compile(r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\Z")
PATHS = ("package.json", "pyproject.toml", "Cargo.toml", "manifest.json", "VERSION")
MAX_CALLS = 200
MAX_ROWS = 40
STALE_DAYS = 30
MAX_RESPONSE = 1_500_000

class Unknown(Exception):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

class PublicAPI:
    def __init__(self, token):
        self.token = token
        self.calls = 0
        self.opener = urllib.request.build_opener(NoRedirect())
    @lru_cache(maxsize=256)
    def get(self, path):
        if self.calls >= MAX_CALLS:
            raise Unknown("request budget")
        self.calls += 1
        request = urllib.request.Request("https://api.github.com" + path, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self.token,
            "User-Agent": "ASES-CodeGraph-retention",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with self.opener.open(request, timeout=6) as response:
                raw = response.read(MAX_RESPONSE + 1)
                if len(raw) > MAX_RESPONSE:
                    raise Unknown("response too large")
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise Unknown("upstream request failed") from None
        except (OSError, ValueError):
            raise Unknown("upstream unavailable") from None

def stable(value):
    match = VERSION.fullmatch(value) if isinstance(value, str) and len(value) <= 40 else None
    if not match:
        return None
    result = tuple(map(int, match.groups()))
    return result if result != (0, 0, 0) else None

def version_text(value):
    return ".".join(map(str, value))

def parse_version(path, raw):
    try:
        if path == "VERSION":
            return stable(raw.strip())
        if path.endswith(".json"):
            obj = json.loads(raw)
            if path == "package.json" and obj.get("private") is True:
                return None
            return stable(obj.get("version"))
        obj = tomllib.loads(raw)
        if path == "pyproject.toml":
            project = obj.get("project", {})
            if "version" in project.get("dynamic", []):
                return None
            return stable(project.get("version"))
        return stable(obj.get("package", {}).get("version"))
    except (ValueError, TypeError, AttributeError):
        return None

def safe_repo(repo):
    return isinstance(repo, str) and REPO.fullmatch(repo) and not any(p in (".", "..") for p in repo.split("/"))

def public_head(api, repo):
    if not safe_repo(repo):
        raise Unknown("invalid repository")
    data = api.get("/repos/" + repo)
    if not data or data.get("private") is not False:
        raise Unknown("public repository not verified")
    branch = data.get("default_branch")
    if not isinstance(branch, str) or not branch or len(branch) > 255:
        raise Unknown("default branch unknown")
    # Quote a branch as one URL component; never use it as a shell expression.
    head = api.get("/repos/" + repo + "/commits/" + urllib.parse.quote(branch, safe=""))
    sha = head.get("sha") if isinstance(head, dict) else None
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise Unknown("default commit unknown")
    return sha

def declarations(api, repo, sha):
    if not SHA.fullmatch(sha):
        raise Unknown("invalid commit")
    listing = api.get("/repos/" + repo + "/contents?ref=" + sha)
    if not isinstance(listing, list):
        raise Unknown("root listing unavailable")
    values = {}
    for item in listing:
        path = item.get("name")
        if path not in PATHS:
            continue
        # Symlinks/submodules and dynamic or ambiguous declarations are not evidence.
        if item.get("type") != "file" or not isinstance(item.get("size"), int) or not 0 <= item["size"] <= 128_000:
            values[path] = None
            continue
        data = api.get("/repos/" + repo + "/contents/" + path + "?ref=" + sha)
        if not isinstance(data, dict) or data.get("type") != "file" or data.get("encoding") != "base64":
            values[path] = None
            continue
        try:
            raw = base64.b64decode(data["content"]).decode("utf-8")
            values[path] = parse_version(path, raw)
        except (ValueError, TypeError, KeyError):
            values[path] = None
    return values

def compare_versions(old, new):
    # Same root declarations on both snapshots; disagreement or change in the
    # declaration set is not evidence of project-level supersession.
    if not old or old.keys() != new.keys() or None in old.values() or None in new.values():
        return None
    if len(set(old.values())) != 1 or len(set(new.values())) != 1:
        return None
    return next(iter(old.values())), next(iter(new.values())), sorted(old)

def ancestor(api, repo, old, head):
    result = api.get("/repos/" + repo + "/compare/" + old + "..." + head + "?per_page=1")
    if not isinstance(result, dict):
        return False
    return (result.get("status") == "ahead"
            and result.get("base_commit", {}).get("sha") == old
            and result.get("merge_base_commit", {}).get("sha") == old)

def protection(config):
    if not isinstance(config, dict) or set(config) != {"protected"} or not isinstance(config["protected"], list):
        raise ValueError("invalid retention registry")
    protected = {}
    for item in config["protected"]:
        if set(item) != {"repository", "commit", "reason"} or not safe_repo(item["repository"]) or not SHA.fullmatch(item["commit"]):
            raise ValueError("invalid protected index")
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            raise ValueError("missing retention reason")
        protected[(item["repository"], item["commit"])] = True
    return protected

def classify(report, api, current_cli, protected, now):
    if stable(current_cli) is None:
        raise ValueError("unrecognized adopted CLI version")
    rows = report["indexes"]
    cached = {(r["repository"], r["commit"], r["cli"]) for r in rows if r["current_bytes"] > 0}
    heads = {}
    versions = {}
    def get_versions(repo, sha):
        key = repo, sha
        if key not in versions:
            versions[key] = declarations(api, repo, sha)
        return versions[key]
    candidates = protected_count = incomplete = 0
    # Largest keys first; explicit bound reported, not silently treated as safe.
    for i, row in enumerate(rows):
        repo, commit, cli = row["repository"], row["commit"], row["cli"]
        age = max(0, (now - dt.datetime.fromisoformat(row["latest_upload"])).days)
        row.update(upload_age_days=age, flags=[], evidence={}, recommendation="keep", upstream_status="not_checked")
        if (repo, commit) in protected:
            row["recommendation"] = "protected"
            protected_count += 1
            continue
        flags = row["flags"]
        strong = False
        if stable(cli) and stable(cli) < stable(current_cli):
            flags.append("older_adopted_engine")
            row["evidence"]["adopted_cli"] = current_cli
            strong = True
        if row["bytes"] > row["current_bytes"]:
            flags.append("noncurrent_object_versions")
            row["evidence"]["noncurrent_bytes"] = row["bytes"] - row["current_bytes"]
        if age >= STALE_DAYS:
            flags.append("old_upload_not_last_access")
        if i >= MAX_ROWS:
            row["upstream_status"] = "scan_limit"
            incomplete += 1
        else:
            try:
                if repo not in heads:
                    try:
                        heads[repo] = public_head(api, repo)
                    except Unknown:
                        heads[repo] = None
                head = heads[repo]
                if not head:
                    raise Unknown("head unavailable")
                row["evidence"]["upstream_sha"] = head
                if head == commit:
                    row["upstream_status"] = "current_head"
                elif not ancestor(api, repo, commit, head):
                    row["upstream_status"] = "ancestry_unverified"
                    incomplete += 1
                else:
                    pair = compare_versions(get_versions(repo, commit), get_versions(repo, head))
                    if pair is None:
                        row["upstream_status"] = "version_unknown_or_ambiguous"
                        incomplete += 1
                    else:
                        old, new, sources = pair
                        row["evidence"].update(cached_version=version_text(old), upstream_version=version_text(new), version_paths=sources)
                        row["upstream_status"] = "compared"
                        if old < new:
                            flags.append("upstream_version_increased")
                            strong = True
                        elif old == new and (repo, head, current_cli) in cached:
                            flags.append("same_version_newer_head_cached")
                        elif old > new:
                            row["upstream_status"] = "upstream_version_lower"
            except Unknown:
                row["upstream_status"] = "upstream_unavailable_or_budget"
                incomplete += 1
        if flags:
            row["recommendation"] = "delete_candidate" if strong else "review_only"
            candidates += 1
    report.update(candidate_count=candidates, protected_count=protected_count,
                  incomplete_upstream_checks=incomplete, age_threshold_days=STALE_DAYS,
                  adopted_cli=current_cli, api_calls=getattr(api, "calls", 0))
    return report

class Tests(unittest.TestCase):
    def test_versions(self):
        self.assertLess(stable("1.9.0"), stable("1.10.0"))
        for val in ("1.2.0-dev", "1.2", "01.2.3", "0.0.0", "1.2.3+abc", None):
            self.assertIsNone(stable(val))
        self.assertIsNone(parse_version("package.json", '{"private":true,"version":"1.2.3"}'))
        self.assertIsNone(parse_version("pyproject.toml", '[project]\ndynamic=["version"]'))
        self.assertEqual(parse_version("Cargo.toml", '[package]\nversion="1.2.3"'), (1,2,3))
    def test_ambiguous(self):
        self.assertIsNone(compare_versions({"VERSION":(1,2,3)}, {"package.json":(2,0,0)}))
        self.assertIsNone(compare_versions({"VERSION":(1,2,3),"manifest.json":(1,0,0)}, {"VERSION":(2,0,0),"manifest.json":(2,0,0)}))
        self.assertEqual(compare_versions({"VERSION":(1,2,3)}, {"VERSION":(2,0,0)})[:2], ((1,2,3),(2,0,0)))
    def test_flags(self):
        old, head = "a"*40, "b"*40
        class Mock:
            def get(self, path):
                if path.endswith("/repos/a/b"):
                    return {"private":False,"default_branch":"main"}
                if path.endswith("/commits/main"):
                    return {"sha":head}
                if "/compare/" in path:
                    return {"status":"ahead","base_commit":{"sha":old},"merge_base_commit":{"sha":old}}
                if "/contents?ref=" in path:
                    return [{"name":"VERSION","size":5,"type":"file"}]
                if "/contents/VERSION?ref=" in path:
                    return {"type":"file","encoding":"base64","content":base64.b64encode(("1.0.0" if path.endswith(old) else "2.0.0").encode()).decode()}
                raise Unknown()
        def row(sha,cli="1.6.2",size=10,current=10):
            return {"repository":"a/b","commit":sha,"cli":cli,"bytes":size,"current_bytes":current,"latest_upload":"2026-11-26T00:00:00+00:00"}
        now=dt.datetime(2026,11,26,tzinfo=dt.timezone.utc)
        result=classify({"indexes":[row(old),row(head),row(old,"1.5.0",20,10)]}, Mock(),"1.6.2",{},now)
        self.assertEqual(result["candidate_count"],2)
        self.assertIn("upstream_version_increased",result["indexes"][0]["flags"])
        self.assertEqual(result["indexes"][1]["recommendation"],"keep")
        self.assertIn("older_adopted_engine",result["indexes"][2]["flags"])
        self.assertIn("noncurrent_object_versions",result["indexes"][2]["flags"])
        self.assertEqual(classify({"indexes":[row(old)]},Mock(),"1.6.2",{("a/b",old):True},now)["protected_count"],1)
        class Offline:
            def get(self,path): raise Unknown()
        result=classify({"indexes":[row(old)]},Offline(),"1.6.2",{},now+dt.timedelta(days=31))
        self.assertEqual(result["indexes"][0]["recommendation"],"review_only")
        self.assertEqual(result["indexes"][0]["flags"],["old_upload_not_last_access"])
        self.assertEqual(result["incomplete_upstream_checks"],1)
    def test_divergence(self):
        class Divergent:
            def get(self,path): return {"status":"diverged","base_commit":{"sha":"a"*40},"merge_base_commit":{"sha":"c"*40}}
        self.assertFalse(ancestor(Divergent(),"a/b","a"*40,"b"*40))
    def test_registry(self):
        self.assertEqual(protection({"protected":[{"repository":"a/b","commit":"a"*40,"reason":"active research"}]}),{("a/b","a"*40):True})
        with self.assertRaises(ValueError): protection({"protected":[{"repository":"a/b","commit":"a"*40,"reason":""}]})

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        path = Path(sys.argv[1])
        source = Path(".github/scripts/codegraph-public-explore.sh").read_text()
        matches = re.findall(r'^cli_version="([^"]+)"$', source, re.M)
        if len(matches) != 1:
            raise SystemExit("Adopted CLI version not verified")
        token = os.environ["GH_TOKEN"]
        report = json.loads(path.read_text())
        registry = protection(json.loads(Path(".github/codegraph-cache-retention.json").read_text()))
        result = classify(report, PublicAPI(token), matches[0], registry, dt.datetime.now(dt.timezone.utc))
        path.write_text(json.dumps(result, indent=2)+"\n")
        print("Candidates: {}; protected: {}; incomplete upstream checks: {}; API calls: {}".format(
            result["candidate_count"], result["protected_count"], result["incomplete_upstream_checks"], result["api_calls"]))
    else:
        raise SystemExit("Usage: codegraph-cache-candidates.py report.json | --self-test")
