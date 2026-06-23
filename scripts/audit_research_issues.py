#!/usr/bin/env python3
"""
audit_research_issues.py — post-create audit for Crosslink `research` issues.

Scans the local Crosslink db (`.crosslink/issues.db`) and flags open
`research`-labeled issues whose description is missing, too short, or
doesn't contain the expected sections (`Rationale`, `Alternatives`).

This is the local-detection companion to the upstream Crosslink feature
request at `research-addenda/Research Addendum 02 - Crosslink
template required_fields feature.md`. When the upstream feature ships,
this script becomes a redundant local mirror; until then, it surfaces
the gap for the Principal or for session-end review.

Motivation: a `research` issue was created on 2026-06-22 with no
description and no record of why Microsoft AutoGen was selected as the
first Track B harness evaluation. The reasoning had to be reconstructed
post-hoc. See `selection-rationale/2026-06-22-microsoft-autogen.md`
for the documented gap.

Usage:
    python3 scripts/audit_research_issues.py
    python3 scripts/audit_research_issues.py --json
    python3 scripts/audit_research_issues.py --min-chars 200

Exit codes:
    0 — script ran successfully. Violations may exist; check output.
    1 — Crosslink db not found, schema mismatch, or other runtime error.

This script is detection, not prevention. It does not block issue
creation; it surfaces the state of existing issues for review. Pair it
with a session-end handoff (e.g., include its output in the next
`crosslink session end --notes ...` call) to make the violations
visible at the natural review boundary.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


DEFAULT_MIN_CHARS = 200
DEFAULT_REQUIRED_SECTIONS = ("Rationale", "Alternatives")
TARGET_LABEL = "research"


def find_crosslink_db() -> Path:
    """Locate `.crosslink/issues.db` by walking up from cwd."""
    cwd = Path.cwd()
    for path in (cwd, *cwd.parents):
        candidate = path / ".crosslink" / "issues.db"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Crosslink db not found in {cwd} or any parent directory. "
        "Run from inside a project that has been initialized with `crosslink init`."
    )


def audit(
    db_path: Path,
    min_chars: int,
    required_sections: tuple[str, ...],
) -> list[dict]:
    """Return a list of violation dicts for open issues with the target label."""
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('issues', 'labels')"
        )
        tables = {row[0] for row in cur.fetchall()}
        if not {"issues", "labels"}.issubset(tables):
            raise RuntimeError(
                f"Crosslink db at {db_path} is missing the 'issues' or 'labels' table. "
                "Schema may have changed; check crosslink version compatibility."
            )
        cur.execute(
            """
            SELECT i.id, i.title, i.description
            FROM issues i
            INNER JOIN labels l ON l.issue_id = i.id
            WHERE l.label = ? AND i.status = 'open'
            ORDER BY i.id
            """,
            (TARGET_LABEL,),
        )
        violations: list[dict] = []
        for issue_id, title, description in cur.fetchall():
            reasons: list[str] = []
            desc = description or ""
            if not desc.strip():
                reasons.append("description is empty")
            else:
                if len(desc) < min_chars:
                    reasons.append(
                        f"description is too short ({len(desc)} < {min_chars} chars)"
                    )
                for section in required_sections:
                    if section.lower() not in desc.lower():
                        reasons.append(f"missing required section: {section}")
            if reasons:
                violations.append(
                    {
                        "id": issue_id,
                        "title": title,
                        "description_chars": len(desc),
                        "reasons": reasons,
                    }
                )
        return violations
    finally:
        conn.close()


def format_text(violations: list[dict], min_chars: int) -> str:
    if not violations:
        return (
            f"PASS: no open `{TARGET_LABEL}` issues with missing rationale "
            f"(min {min_chars} chars, sections {list(DEFAULT_REQUIRED_SECTIONS)}).\n"
        )
    lines = [
        f"VIOLATIONS: {len(violations)} open `{TARGET_LABEL}` issue(s) "
        "with missing or insufficient rationale:",
        "",
    ]
    for v in violations:
        lines.append(f"  #{v['id']} {v['title']}")
        lines.append(f"    description: {v['description_chars']} chars")
        for reason in v["reasons"]:
            lines.append(f"    - {reason}")
        lines.append("")
    lines.append(
        "Recommendation: add `Rationale:` and `Alternatives considered:` sections "
        "to each issue's description, OR create a `selection-rationale/YYYY-MM-DD-*.md` "
        "file and link it in the issue body. The companion template is in the "
        "selection-rationale/ folder."
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Crosslink `research` issues for missing rationale."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (one object: {count, violations}).",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=DEFAULT_MIN_CHARS,
        help=f"Minimum description length (default: {DEFAULT_MIN_CHARS}).",
    )
    parser.add_argument(
        "--required-sections",
        nargs="+",
        default=list(DEFAULT_REQUIRED_SECTIONS),
        help=(
            "Required section names. Each is matched as a case-insensitive substring "
            "of the description. Default: 'Rationale' 'Alternatives'."
        ),
    )
    args = parser.parse_args()

    try:
        db_path = find_crosslink_db()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        violations = audit(db_path, args.min_chars, tuple(args.required_sections))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"count": len(violations), "violations": violations}, indent=2))
    else:
        sys.stdout.write(format_text(violations, args.min_chars))

    return 0


if __name__ == "__main__":
    sys.exit(main())
