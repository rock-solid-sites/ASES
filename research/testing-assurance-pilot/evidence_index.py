#!/usr/bin/env python3
"""Portable, research-only CI evidence index; never implies external archival.

A complete local index and verified copy are separate from independent storage.
CI can make the index and test it even when no external archive is configured.
"""
import argparse
import hashlib
import json
import mimetypes
import os
import subprocess
import time
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def build(root, source_rev, plan_sha):
    found = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in ("evidence-manifest.json", "evidence-integrity.json"):
            continue
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        found.append({
            "path": rel, "sha256": sha256(data), "bytes": len(data),
            "content_type": mimetypes.guess_type(rel)[0] or "application/octet-stream"
        })
    return {
        "schema_version": 1,
        "status": "INDEX_CREATED",
        "scope": "Files currently in GitLab CI job results/ directory only",
        "run": {"source_revision": source_rev,
                "pilot_plan_sha256": plan_sha,
                "ci_pipeline_id": os.environ.get("CI_PIPELINE_ID", "UNKNOWN"),
                "ci_job_id": os.environ.get("CI_JOB_ID", "UNKNOWN"),
                "generated_utc_epoch_seconds": int(time.time())},
        "artifacts": found,
        "artifact_count": len(found),
        "total_artifact_bytes": sum(x["bytes"] for x in found),
        "independent_external_archive": "NOT_VERIFIED",
    }


def verify(root, manifest):
    failures = []
    for item in manifest["artifacts"]:
        p = root / item["path"]
        if not p.is_file():
            failures.append({"path": item["path"], "reason": "MISSING"})
        else:
            data = p.read_bytes()
            if len(data) != item["bytes"] or sha256(data) != item["sha256"]:
                failures.append({"path": item["path"], "reason": "HASH_OR_SIZE_MISMATCH"})
    return {
        "execution_integrity": "COMPLETE_LOCALLY" if not failures else "FAILED",
        "failures": failures,
        "independent_external_archive": "NOT_VERIFIED",
        "claim_conclusion": "NO_CLAIM_ABOUT_EXTERNAL_ARCHIVE",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--plan", required=True)
    args = p.parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    plan = Path(args.plan)
    if not plan.is_file():
        raise SystemExit("ERROR: frozen plan missing")
    manifest = build(root, args.source, sha256(plan.read_bytes()))
    path = root / "evidence-manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    status = verify(root, manifest)
    status_path = root / "evidence-integrity.json"
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": status["execution_integrity"],
        "evidence_files": manifest["artifact_count"],
        "bytes": manifest["total_artifact_bytes"],
        "external_archive": status["independent_external_archive"],
        "manifest_sha256": sha256(path.read_bytes())
    }, sort_keys=True))
    # Keep the full machine-readable pilot result and index available to a
    # separate, supervised connector for archival outside GitLab's retention.
    # The proof of external export must be added separately, after receipt.
    for label, filename in (
        ("ASES_P1_FULL_RESULT", root / "pilot/p1.json"),
        ("ASES_P1_EVIDENCE_INDEX", path)
    ):
        if filename.is_file():
            print(label + "=" + json.dumps(json.loads(filename.read_text()),
                                           separators=(",", ":"), sort_keys=True))
    if status["execution_integrity"] != "COMPLETE_LOCALLY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
