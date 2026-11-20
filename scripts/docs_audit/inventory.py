#!/usr/bin/env python3
"""Read-only ASES-owned documentation inventory; never promotes status or authority.

Runs from any repository checkout. Only file contents and git revision are read;
no remote APIs, provider calls or project-manager writes.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[2]
IGNORED = (
    "fork/", ".crosslink/", ".crosslink.backup-", "docs/historical/",
    "handoff-bundle/", "staging/", "to-file/", "session-handoffs/",
    "evaluation-corpus/", "docs/research/retrospectives/",
)
ROOT_ENTRYPOINTS = {
    "README.md", "ORIENTATION.md", "ARCHITECTURE.md", "AGENTS.md",
    "SESSION-START.md", "docs/SESSION-END.md", "docs/ORCHESTRATOR.md",
}
CURRENT_DIRS = (
    "docs/standards/", "docs/methodology/", "docs/requirements/",
    "docs/architecture/", "skills/current/",
)
HIGH_RISK = {
    "AGENTS.md", "SESSION-START.md", "docs/SESSION-END.md",
    "docs/ORCHESTRATOR.md", "docs/methodology/Agent Model Launch Routes.md",
}
RETIRED_MARKERS = (
    "crosslink session", "crosslink kickoff", "IT3812",
    "be ready to fall back to a paid Go model",
)
FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$")
LINK_RE = re.compile(r"\]\(([^)#]+\.md(?:#[^)]*)?)\)")
VALID_STATUS = {"active", "validated", "draft", "experimental",
                "deprecated", "archived", "historical", "superseded"}


def ignored(path: str) -> bool:
    return path.startswith(IGNORED)


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    data: dict[str, str] = {}
    for line in lines[1:end]:
        m = FIELD_RE.match(line)
        if m and not line.lstrip().startswith("#"):
            data[m.group(1)] = m.group(2).strip("'\"")
    return data


def reference_check(path: str, text: str, existing: set[str]) -> list[str]:
    """Check only explicit relative Markdown links; don't guess symbolic refs."""
    errors: list[str] = []
    for value in LINK_RE.findall(text):
        target = unquote(value.split("#", 1)[0])
        if target.startswith(("http:", "https:", "/", "mailto:")):
            continue
        parts = path.split("/")[:-1]
        for segment in target.split("/"):
            if segment == "..":
                if parts:
                    parts.pop()
                else:
                    errors.append(f"escapes repository: {value}")
            elif segment and segment != ".":
                parts.append(segment)
        full = "/".join(parts)
        if full not in existing:
            errors.append(f"missing relative link: {value}")
    return sorted(set(errors))


def inventory(root: Path = REPO) -> dict:
    docs: list[dict] = []
    existing = {p.relative_to(root).as_posix()
                for p in root.rglob("*") if p.is_file()}
    for path in sorted(existing):
        if not path.lower().endswith((".md", ".mdx")) or ignored(path):
            continue
        text = (root / path).read_text(encoding="utf-8", errors="replace")
        meta = frontmatter(text)
        status = meta.get("status", "")
        status_type = status.lower().split("(", 1)[0].strip()
        candidate = path.startswith(CURRENT_DIRS) or path in ROOT_ENTRYPOINTS
        active = status_type == "active" or path.startswith("skills/current/")
        norm = bool(meta.get("title")) and status_type in {"active", "validated"}
        warning: list[str] = []
        if candidate and not meta and not path.startswith("skills/current/"):
            warning.append("candidate entrypoint has no structured metadata")
        if active and not meta.get("version"):
            warning.append("declared-active entry lacks explicit version")
        if status and status_type not in VALID_STATUS:
            warning.append("nonstandard status metadata: " + status)
        if active and not meta.get("authority") and not path.startswith("skills/current/"):
            warning.append("declared-active entry lacks authority")
        if path in HIGH_RISK and active:
            matches = [m for m in RETIRED_MARKERS if m.lower() in text.lower()]
            if matches:
                warning.append("active entrypoint contains retired route markers: "
                               + ", ".join(matches))
        missing = reference_check(path, text, existing)
        docs.append({
            "path": path, "title": meta.get("title") or Path(path).stem,
            "status": status or ("Current skill" if path.startswith("skills/current/") else "Undeclared"),
            "authority": meta.get("authority") or "UNVERIFIED",
            "version": meta.get("version") or None,
            "program": meta.get("program") or None,
            "layer": meta.get("layer") or None,
            "canonical_repository": meta.get("canonical_repository") or None,
            "declared_active": bool(active),
            "normative_candidate": norm,
            "entrypoint_candidate": candidate,
            "warnings": warning,
            "broken_relative_links": missing,
        })
    duplicates: list[dict] = []
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for doc in docs:
        if doc["declared_active"] and doc["authority"].lower() == "canonical":
            grouped[(doc["program"] or "", doc["title"].casefold())].append(doc["path"])
    for (program, title), paths in sorted(grouped.items()):
        if len(paths) > 1:
            duplicates.append({"program": program, "title": title, "paths": paths})
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                      text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "UNVERIFIED"
    return {
        "schema": "ases-document-inventory-v1",
        "source_revision": sha, "coverage": "repo-owned MD/MDX; listed exclusions",
        "excluded_prefixes": list(IGNORED),
        "counts": {
            "owned_records": len(docs),
            "declared_active": sum(d["declared_active"] for d in docs),
            "entrypoint_candidates": sum(d["entrypoint_candidate"] for d in docs),
            "active_without_version": sum(d["declared_active"] and d["version"] is None
                                          for d in docs),
            "active_with_warnings": sum(d["declared_active"] and bool(d["warnings"])
                                        for d in docs),
            "broken_link_records": sum(bool(d["broken_relative_links"]) for d in docs),
            "duplicate_active_canonical_identities": len(duplicates),
        },
        "duplicate_active_canonical_identities": duplicates,
        "documents": docs,
    }


def markdown_index(data: dict) -> str:
    lines = [
        "# ASES documentation inventory (declared status; not an approval)",
        "",
        "**Generated from the checked-out ASES source tree.** Source revision: "
        f"\`{data['source_revision']}\`. Generated classifications and metadata are "
        "**observations, not freshness or authority verification**. In particular, "
        "a document marked Active can still contain obsolete procedures.",
        "",
        "Use the [canonical documentation standard](standards/Documentation%20Standard.md) "
        "and [task-scoped information method]"
        "(methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) "
        "for ownership and authority. [Current operational skills](../skills/current/README.md) "
        "are a separate selective-dispatch surface. Experimental "
        "[knowledge-index work](../scripts/knowledge_index/README.md) "
        "is not a canonical document registry.",
        "",
        f"Inventory: {data['counts']['owned_records']} in-scope Markdown/MDX files, "
        f"{data['counts']['declared_active']} declared active/current, "
        f"{data['counts']['active_without_version']} of those lack a declared version; "
        f"{data['counts']['active_with_warnings']} have metadata/route warnings. "
        "Diagnostics require review before a document can be certified current.",
        "",
        "## Declared active/current documents",
        "",
        "| Source | Declared authority | Version | Diagnostics |",
        "| --- | --- | --- | --- |",
    ]
    for d in data["documents"]:
        if not d["declared_active"]:
            continue
        rel = ("../" + d["path"]).replace(" ", "%20")
        details = "; ".join(d["warnings"][:2]) or "—"
        lines.append(f"| [{d['title']}]({rel}) | {d['authority']} "
                     f"| {d['version'] or 'unversioned'} | {details} |")
    lines.extend([
        "", "## Coverage and exceptions", "",
        "- Included: repo-owned Markdown/MDX outside the explicitly excluded "
        "vendored, archived and generated surfaces.",
        "- Files that declare Experimental, Draft, Deprecated or Archived remain "
        "discoverable from Git but are **not** automatically current instructions.",
        "- Undeclared, malformed, mirrored or stale records are **not** silently "
        "reclassified. Resolve them through the version/authority audit.",
        "- Version, authority, link and duplicate-identity diagnostics are "
        "read-only findings; no automatic header or version fabrication.",
        "- Retired commands within historical documents are retained as evidence, "
        "not authorized launch instructions.",
        "",
        "For the complete machine-readable inventory and broken-link details, "
        "run \`python scripts/docs_audit/inventory.py --json-out <path> "
        "--index-out <path>\` in the repository, or consult the CI artifact.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--index-out", type=Path)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    data = inventory(args.root)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if args.index_out:
        args.index_out.parent.mkdir(parents=True, exist_ok=True)
        args.index_out.write_text(markdown_index(data), encoding="utf-8")
    if args.summary or not (args.index_out or args.json_out):
        print(json.dumps({
            "revision": data["source_revision"], **data["counts"],
            "high_risk": [
                {"path": d["path"], "warnings": d["warnings"]}
                for d in data["documents"] if d["path"] in HIGH_RISK
            ],
            "duplicate_active_canonical_identities":
                data["duplicate_active_canonical_identities"][:10],
        }, indent=2))


if __name__ == "__main__":
    main()
