"""Experimental ASES evidence-contract classifier. No universal proof claims."""
import hashlib
import json
from pathlib import Path

EXECUTION = {"PASS", "FAIL", "ERROR", "INCONCLUSIVE", "BLOCKED", "CANCELLED", "SKIPPED", "NOT_RUN"}
CLAIM = {"SUPPORTED_WITHIN_SCOPE", "CONTRADICTED", "UNRESOLVED", "NOT_TESTABLE_AS_STATED"}
QUALITY = {"QUALIFIED", "PARTIALLY_QUALIFIED", "UNQUALIFIED"}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            h.update(block)
    return h.hexdigest()

def classify(record):
    """Fail closed: no passing claim from absent controls or unqualified checker."""
    execution = record.get("execution", "NOT_RUN")
    if execution not in EXECUTION:
        raise ValueError("unknown execution status")
    files = record.get("artifacts", [])
    artifact_ok = bool(files) and all(
        isinstance(x.get("sha256"), str) and len(x["sha256"]) == 64 and
        isinstance(x.get("size"), int) and x["size"] >= 0 and
        x.get("capture_complete") is True for x in files
    )
    controls = record.get("controls", {})
    qualified = all(controls.get(k) is True for k in
                    ("valid_neighbor_accepted", "invalid_evidence_rejected", "oracle_independent"))
    quality = "QUALIFIED" if artifact_ok and qualified else (
        "PARTIALLY_QUALIFIED" if artifact_ok else "UNQUALIFIED")
    if execution == "FAIL" and record.get("violation_observed") is True:
        claim = "CONTRADICTED"
    elif execution == "PASS" and quality == "QUALIFIED" and record.get("frozen_claim"):
        claim = "SUPPORTED_WITHIN_SCOPE"
    else:
        claim = "UNRESOLVED"
    return {"execution": execution, "claim_evaluation": claim,
            "evidence_quality": quality,
            "archive_complete": record.get("off_provider_archive_verified") is True,
            "acceptance": None}  # acceptance requires an authorized decision

def manifest(root):
    root = Path(root)
    return [{"path": str(p.relative_to(root)), "size": p.stat().st_size,
             "sha256": sha256(p), "capture_complete": True}
            for p in sorted(root.rglob("*")) if p.is_file()]

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    p.add_argument("--execution", choices=sorted(EXECUTION), required=True)
    p.add_argument("--frozen-claim", default="")
    a = p.parse_args()
    artifacts = manifest(a.directory)
    # Replay is not an independent oracle: never manufacture qualified status.
    record = {"schema": "ases.assurance.pilot.v0", "execution": a.execution,
              "frozen_claim": a.frozen_claim, "artifacts": artifacts,
              "controls": {}, "off_provider_archive_verified": False}
    record["assessment"] = classify(record)
    print(json.dumps(record, sort_keys=True, indent=2))
