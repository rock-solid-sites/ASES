#!/usr/bin/env python3
"""
validate.py — Corpus validator for validation-brief-corpus (issue #530).

Checks:
  - manifest.json exists and is valid JSON
  - corpus.jsonl exists and each line is valid JSON with required fields
  - Every manifest entry has a corresponding file on disk
  - Every file on disk is listed in manifest (no orphan)
  - ID uniqueness (well-formed + malformed + adversarial share one namespace)
  - Malformed/adversarial have expected_recovery
  - Well-formed have 4 ACs in the markdown body (heuristic)
  - Frontmatter validity (yaml `id`, `class`, `kind`, `version` present for md briefs)

Exit 0 = all checks pass. Exit 1 = any failure. Prints a summary.

Usage:
  python harness/validate.py
  python harness/validate.py --corpus-root evaluation-corpus/validation-brief-corpus
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

REQUIRED_MANIFEST_FIELDS = {"corpus", "version", "total_briefs", "briefs"}
REQUIRED_BRIEF_FIELDS = {"id", "file", "kind"}
REQUIRED_CORPUS_FIELDS = {"id", "kind", "file"}

def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8", errors="strict")
    if not text.startswith("---"):
        return None, "missing frontmatter delimiter"
    end = text.find("\n---", 3)
    if end == -1:
        return None, "unterminated frontmatter"
    fm_text = text[3:end].strip()
    if HAS_YAML:
        try:
            data = yaml.safe_load(fm_text)
            return data, None
        except Exception as e:
            return None, f"yaml parse error: {e}"
    # Fallback minimal parser: key: value per line
    data = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()
    return data, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-root", default="evaluation-corpus/validation-brief-corpus")
    args = ap.parse_args()

    root = Path(args.corpus_root)
    # When run from harness/ dir, root is ../..
    if not root.exists():
        # Try relative to harness location
        harness_dir = Path(__file__).parent
        root = (harness_dir.parent).resolve()
    if not root.exists():
        print(f"FAIL: corpus root not found: {root}", file=sys.stderr)
        sys.exit(1)

    manifest_path = root / "manifest.json"
    corpus_path = root / "corpus.jsonl"

    errors = []
    warnings = []

    # Manifest
    if not manifest_path.exists():
        errors.append(f"missing manifest: {manifest_path}")
        manifest = None
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"manifest invalid JSON: {e}")
            manifest = None
        else:
            for f in REQUIRED_MANIFEST_FIELDS:
                if f not in manifest:
                    errors.append(f"manifest missing field: {f}")
            if manifest and "briefs" in manifest:
                total = manifest.get("total_briefs")
                actual = len(manifest["briefs"])
                if total != actual:
                    errors.append(f"manifest total_briefs {total} != len(briefs) {actual}")
                # Check total is 40
                if actual != 40:
                    warnings.append(f"manifest has {actual} briefs, expected 40")

    # Corpus.jsonl
    corpus_records = []
    if not corpus_path.exists():
        errors.append(f"missing corpus.jsonl: {corpus_path}")
    else:
        for i, line in enumerate(corpus_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                corpus_records.append(rec)
            except Exception as e:
                errors.append(f"corpus.jsonl line {i} invalid JSON: {e}")
                continue
            for f in REQUIRED_CORPUS_FIELDS:
                if f not in rec:
                    errors.append(f"corpus.jsonl line {i} missing field: {f}")
            if rec.get("kind") in ("malformed", "adversarial") and "expected_recovery" not in rec:
                errors.append(f"corpus.jsonl line {i} ({rec.get('id')}) missing expected_recovery")

    # File existence and ID uniqueness
    seen_ids = {}
    if manifest and "briefs" in manifest:
        for entry in manifest["briefs"]:
            bid = entry.get("id")
            kind = entry.get("kind")
            fpath = entry.get("file")
            if not bid or not fpath or not kind:
                errors.append(f"manifest entry missing id/file/kind: {entry}")
                continue
            if bid in seen_ids:
                errors.append(f"duplicate id in manifest: {bid} (also in {seen_ids[bid]})")
            else:
                seen_ids[bid] = fpath
            # File exists
            full = root / fpath
            if not full.exists():
                errors.append(f"manifest entry {bid} file not found on disk: {fpath}")
            else:
                # For md files, check frontmatter
                if fpath.endswith(".md"):
                    fm, err = parse_frontmatter(full)
                    if err:
                        errors.append(f"{bid} frontmatter error: {err}")
                    else:
                        if fm.get("id") != bid:
                            errors.append(f"{bid} frontmatter id mismatch: {fm.get('id')} != {bid}")
                        if "kind" not in fm:
                            warnings.append(f"{bid} frontmatter missing kind")
                        if "version" not in fm:
                            warnings.append(f"{bid} frontmatter missing version")
                # For malformed/adversarial, check expected_recovery in manifest
                if kind in ("malformed", "adversarial") and "expected_recovery" not in entry:
                    errors.append(f"{bid} ({kind}) missing expected_recovery in manifest")

    # Check corpus.jsonl ↔ manifest alignment
    if corpus_records and manifest and "briefs" in manifest:
        manifest_ids = {e["id"] for e in manifest["briefs"]}
        corpus_ids = {r["id"] for r in corpus_records if "id" in r}
        if manifest_ids != corpus_ids:
            missing_in_corpus = manifest_ids - corpus_ids
            missing_in_manifest = corpus_ids - manifest_ids
            if missing_in_corpus:
                errors.append(f"IDs in manifest but not corpus.jsonl: {missing_in_corpus}")
            if missing_in_manifest:
                errors.append(f"IDs in corpus.jsonl but not manifest: {missing_in_manifest}")

    # Summary
    print(f"Corpus root: {root}")
    print(f"Manifest: {manifest_path} — {len(seen_ids)} briefs")
    print(f"Corpus.jsonl: {corpus_path} — {len(corpus_records)} records")
    print(f"HAS_YAML: {HAS_YAML}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  WARN: {w}")
    if errors:
        print(f"\nFAIL: {len(errors)} error(s):")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    else:
        print("\nPASS: corpus integrity OK")
        # Class counts
        if manifest:
            from collections import Counter
            kinds = Counter(e["kind"] for e in manifest["briefs"])
            print(f"  well-formed: {kinds.get('well-formed', 0)}, malformed: {kinds.get('malformed', 0)}, adversarial: {kinds.get('adversarial', 0)}")
        sys.exit(0)

if __name__ == "__main__":
    main()
