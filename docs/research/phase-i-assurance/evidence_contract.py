"""Experimental ASES evidence contract; metadata attestations are not proof."""
import hashlib
import json
from pathlib import Path
import re

EXECUTION = {"PASS", "FAIL", "ERROR", "INCONCLUSIVE", "BLOCKED", "CANCELLED", "SKIPPED", "NOT_RUN"}
CLAIM = {"SUPPORTED_WITHIN_SCOPE", "CONTRADICTED", "UNRESOLVED", "NOT_TESTABLE_AS_STATED"}
QUALITY = {"QUALIFIED", "PARTIALLY_QUALIFIED", "UNQUALIFIED"}
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def valid_artifact(x):
    if not isinstance(x, dict):
        return False
    path = x.get("path")
    return (isinstance(path, str) and bool(path) and "\\" not in path and
            not path.startswith("/") and not any(p in (".", "..", "") for p in path.split("/")) and
            isinstance(x.get("sha256"), str) and bool(DIGEST.fullmatch(x["sha256"])) and
            type(x.get("size")) is int and x["size"] >= 0 and
            x.get("capture_complete") is True)


def valid_manifest(files):
    return (isinstance(files, list) and bool(files) and
            all(valid_artifact(x) for x in files) and
            len({x["path"] for x in files}) == len(files))


def verify_manifest(root, files):
    """Re-read listed files and detect changed bytes; unlisted files are not covered."""
    root = Path(root).resolve()
    if not root.is_dir() or not valid_manifest(files):
        return False
    for artifact in files:
        path = root / artifact["path"]
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            return False
        if path.stat().st_size != artifact["size"] or sha256(path) != artifact["sha256"]:
            return False
    return True


def classify(record):
    """Fail closed; independent oracle and true provenance remain external requirements."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    execution = record.get("execution", "NOT_RUN")
    if execution not in EXECUTION:
        raise ValueError("unknown execution status")
    files = record.get("artifacts", [])
    artifact_ok = valid_manifest(files) and record.get("artifact_integrity_verified") is True
    controls = record.get("controls", {})
    controls = controls if isinstance(controls, dict) else {}
    qualified = all(controls.get(k) is True for k in
                    ("valid_neighbor_accepted", "invalid_evidence_rejected", "oracle_independent"))
    quality = "QUALIFIED" if artifact_ok and qualified else (
        "PARTIALLY_QUALIFIED" if artifact_ok else "UNQUALIFIED")
    frozen = record.get("frozen_claim")
    if execution == "FAIL" and artifact_ok and record.get("violation_observed") is True:
        claim = "CONTRADICTED"
    elif execution == "PASS" and quality == "QUALIFIED" and isinstance(frozen, str) and frozen.strip():
        claim = "SUPPORTED_WITHIN_SCOPE"
    else:
        claim = "UNRESOLVED"
    # An external archive cannot be verified from user-supplied metadata alone.
    return {"execution": execution, "claim_evaluation": claim,
            "evidence_quality": quality, "archive_complete": False,
            "acceptance": None}


def manifest(root):
    """Hash a scoped directory, excluding caches and refusing symlinks/secret-looking files."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("manifest root is not a directory")
    results = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(x in (".git", "__pycache__", ".pytest_cache") for x in relative.parts) or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError("symlink not allowed in manifest scope")
        if not path.is_file():
            continue
        if path.name.startswith(".env") or path.suffix in (".key", ".pem"):
            raise ValueError("potential secret detected in manifest scope")
        results.append({"path": relative.as_posix(), "size": path.stat().st_size,
                        "sha256": sha256(path), "capture_complete": True})
    return results


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    p.add_argument("--execution", choices=sorted(EXECUTION), required=True)
    p.add_argument("--frozen-claim", default="")
    a = p.parse_args()
    artifacts = manifest(a.directory)
    verified = verify_manifest(a.directory, artifacts)
    record = {"schema": "ases.assurance.pilot.v1", "execution": a.execution,
              "frozen_claim": a.frozen_claim, "artifacts": artifacts,
              "artifact_integrity_verified": verified, "controls": {},
              "off_provider_archive_verified": False}
    record["assessment"] = classify(record)
    print(json.dumps(record, sort_keys=True, indent=2))
