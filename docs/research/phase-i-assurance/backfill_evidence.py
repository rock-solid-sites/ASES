#!/usr/bin/env python3
"""Bounded read-only historical GitHub Actions evidence backfill.

Uses the gh CLI only to download listed, already-created artifacts. Records
partial coverage honestly. Never extracts a source artifact's contents as code
and never executes downloaded files.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def collect_files(root):
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlink in downloaded evidence: " + str(path))
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if any(p in ("", ".", "..") for p in relative.split("/")):
            raise ValueError("unsafe downloaded evidence path")
        raw = path.read_bytes()
        files[relative] = {"size": len(raw), "sha256": digest(raw)}
    return files


def download(repo, run_id, dest):
    dest.mkdir(parents=True, exist_ok=True)
    try:
        done = subprocess.run(
            ["gh", "run", "download", str(run_id), "--repo", repo,
             "--dir", str(dest)],
            check=False, capture_output=True, text=True, timeout=240,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return "DOWNLOAD_FAILED", str(error)[:300]
    if done.returncode:
        return "DOWNLOAD_FAILED", (done.stderr or done.stdout)[-300:]
    return "DOWNLOADED", None


def write_archive(destination, manifest, source):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination, "w:gz") as archive:
        def add(name, raw):
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(raw), 0o600, 0
            archive.addfile(info, io.BytesIO(raw))
        add("backfill-manifest.json", json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n")
        for relative in sorted(manifest["files"]):
            add("artifacts/" + relative, (source / relative).read_bytes())


def verify_archive(destination):
    with tarfile.open(destination, "r:gz") as archive:
        members = archive.getmembers()
        if not members or members[0].name != "backfill-manifest.json":
            raise ValueError("backfill manifest missing")
        if any(not m.isfile() or m.name.startswith("/") or ".." in m.name.split("/")
               for m in members):
            raise ValueError("unsafe archive member")
        if len({m.name for m in members}) != len(members):
            raise ValueError("duplicate archive member")
        manifest = json.load(archive.extractfile(members[0]))
        expected = {"artifacts/" + k: v for k, v in manifest["files"].items()}
        if set(expected) != {m.name for m in members[1:]}:
            raise ValueError("backfill archive file set changed")
        for m in members[1:]:
            blob = archive.extractfile(m).read()
            v = expected[m.name]
            if len(blob) != v["size"] or digest(blob) != v["sha256"]:
                raise ValueError("backfill file hash mismatch: " + m.name)
        return manifest


def backfill(inventory, workspace, archive, repository, fetch):
    spec = json.loads(Path(inventory).read_text())
    run_specs = spec["runs"]
    if not isinstance(run_specs, list) or not run_specs or len(run_specs) > 20:
        raise ValueError("unexpected number of frozen runs")
    if len({r["run_id"] for r in run_specs}) != len(run_specs):
        raise ValueError("duplicate run identifier")
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    statuses = []
    for item in run_specs:
        run_id = item["run_id"]
        expected = item["artifacts"]
        root = workspace / str(run_id)
        state, error = download(repository, run_id, root) if fetch else ("CACHED_FIXTURE", None)
        if not root.is_dir():
            root.mkdir(parents=True)
        found = len([p for p in root.iterdir() if p.is_dir() and not p.is_symlink()])
        statuses.append({"run_id": run_id, "expected_artifacts": expected,
                         "observed_artifacts": found, "download_status": state,
                         "complete": found == expected and error is None,
                         "download_error": error})
    files = collect_files(workspace)
    if not files:
        raise ValueError("no historical evidence downloaded; refuse empty backfill")
    complete = all(x["complete"] for x in statuses)
    report = {"schema": "ases.assurance.backfill.export.v1",
              "scope": "selected, frozen GitHub Actions runs only",
              "source_collection_complete": complete,
              "verified_local_member_bytes": True,
              "off_provider_archive_verified": False,
              "encrypted": False,
              "runs": statuses, "files": files}
    write_archive(Path(archive), report, workspace)
    if verify_archive(archive) != report:
        raise ValueError("backfill manifest changed after clean archive readback")
    return {"selected_runs": len(statuses),
            "expected_artifacts": sum(x["expected_artifacts"] for x in statuses),
            "observed_artifacts": sum(x["observed_artifacts"] for x in statuses),
            "source_collection_complete": complete,
            "archived_files": len(files),
            "sha256": digest(Path(archive).read_bytes()),
            "roundtrip_sha256_verified": True,
            "off_provider_archive_verified": False}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", required=True)
    p.add_argument("--workspace", required=True)
    p.add_argument("--archive", required=True)
    p.add_argument("--repository", default="rock-solid-sites/ASES")
    p.add_argument("--fetch", action="store_true")
    a = p.parse_args()
    print(json.dumps(backfill(a.inventory, a.workspace, a.archive, a.repository, a.fetch),
                     sort_keys=True, indent=2))
