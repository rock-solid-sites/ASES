#!/usr/bin/env python3
"""
session-union.py — read-only union viewer for the split OpenCode session stores.

Store-split context (see #419): On 2026-08-08/09 the ``opencode`` binary on this
machine was flipped to a durable fork build (``1.18.13-pp3g-fork``) that persists
sessions to ``opencode-fork-pp3g.db``, while the operator's interactive TUI was
later upgraded to OpenCode 2 (``0.0.0-beta-17963``, ``opencode2``) which reads
only the main ``opencode.db``.  The main DB was migrated on 2026-08-23 to a
45-migration schema with BOTH a legacy ``session`` table (frozen ~2026-08-09) and
a newer ``session_v2`` table (one live row at migration time); the fork DB
remains on the older 38-migration schema with only ``session``.  All three
stores share the same ASES project id (``b826eb8e...``) so foreign keys align.
This tool never opens the live databases — it snapshot-copies each ``.db`` plus
``-wal``/``-shm`` sidecars into a scratch directory and queries the snapshots,
then unions the listings, dedupes on session id (keeping the richest record),
and presents a single timeline sorted by ``time_updated`` descending.

Usage:
    python3 scripts/session-union.py                          # human table, main+fork
    python3 scripts/session-union.py --project ASES           # filter by directory substring
    python3 scripts/session-union.py --since 2026-08-01 --until 2026-08-23
    python3 scripts/session-union.py --json                   # machine-readable JSON
    python3 scripts/session-union.py --include-local          # also union opencode-local.db
    python3 scripts/session-union.py --snap-dir /tmp/my-snap  # custom scratch dir
    python3 scripts/session-union.py --help

Columns (human and JSON):
    id          — session primary key (e.g. ses_...)
    directory   — session working directory (project/directory)
    project     — project worktree from the ``project`` table (if resolvable)
    title       — session title (may be empty for older rows)
    created     — time_created as ISO-8601 UTC
    updated     — time_updated as ISO-8601 UTC
    source      — which snapshot table produced the row
                  (main:session, main:session_v2, fork:session, local:session)

Deduping: rows are keyed by ``id``; when the same id appears in multiple
sources (notably ``session`` vs ``session_v2`` in the main DB after the
45-migration projection), the richest record is kept: greatest
``time_updated`` wins, then longest non-empty ``title``, then
``session_v2`` is preferred as the canonical v2 projection.

Snapshot safety: every invocation copies
``~/.local/share/opencode/{opencode.db,opencode-fork-pp3g.db}`` (+ ``-wal``
and ``-shm`` sidecars when present) into ``--snap-dir`` (default
``/tmp/opencode/session-union-snap/``) BEFORE opening any SQLite handle.
The optional third store ``opencode-local.db`` is only copied when
``--include-local`` is given (default off).  No file outside the scratch
directory is ever written.

Exit codes:
    0 — success (even if zero sessions matched the filters)
    1 — no snapshot could be read (missing stores, permission error, etc.)
    2 — invalid arguments (bad date format, etc.)

Dependencies: stdlib only (sqlite3, argparse, json, shutil, pathlib, datetime).
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_SNAP_DIR = Path("/tmp/opencode/session-union-snap")
DEFAULT_STORE_DIR = Path.home() / ".local" / "share" / "opencode"

# (source_label, filename) for the mandatory stores.  The optional local
# store is appended only when --include-local is set.
MANDATORY_STORES: list[tuple[str, str]] = [
    ("main", "opencode.db"),
    ("fork", "opencode-fork-pp3g.db"),
]
OPTIONAL_LOCAL: tuple[str, str] = ("local", "opencode-local.db")


# ---------------------------------------------------------------------------
# Snapshot helpers
# ---------------------------------------------------------------------------

def snapshot_copy(store_dir: Path, snap_dir: Path, stores: list[tuple[str, str]]) -> dict[str, Path]:
    """Copy each store's .db + -wal + -shm sidecars into snap_dir.

    Returns mapping label -> snapshot .db path for stores that had a
    readable .db file.  Missing stores are silently skipped (caller decides
    whether that is fatal).  Sidecars are copied only if present.
    """
    snap_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Path] = {}
    for label, filename in stores:
        src = store_dir / filename
        if not src.exists():
            print(f"note: {label} store not found at {src} — skipping", file=sys.stderr)
            continue
        dst = snap_dir / filename
        try:
            shutil.copy2(src, dst)
        except OSError as exc:
            print(f"warning: failed to copy {src} -> {dst}: {exc}", file=sys.stderr)
            continue
        for suffix in ("-wal", "-shm"):
            sidecar_src = Path(str(src) + suffix)
            if sidecar_src.exists():
                sidecar_dst = Path(str(dst) + suffix)
                try:
                    shutil.copy2(sidecar_src, sidecar_dst)
                except OSError as exc:
                    print(f"warning: failed to copy sidecar {sidecar_src}: {exc}", file=sys.stderr)
        result[label] = dst
    return result


# ---------------------------------------------------------------------------
# Schema inspection & reading
# ---------------------------------------------------------------------------

def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    )
    return cur.fetchone() is not None


def _load_project_map(conn: sqlite3.Connection) -> dict[str, str]:
    """Return {project_id: worktree} from the project table if present."""
    if not _table_exists(conn, "project"):
        return {}
    try:
        rows = conn.execute("SELECT id, worktree FROM project").fetchall()
        return {r[0]: r[1] for r in rows}
    except sqlite3.Error:
        return {}


def _read_session_table(
    conn: sqlite3.Connection, table: str, source_label: str, project_map: dict[str, str]
) -> list[dict]:
    """Read all rows from *table* and return normalized session dicts."""
    # Use explicit column list so missing columns (e.g. title nullable vs not)
    # don't break the query; SELECT * is fine since we normalize by name.
    try:
        cur = conn.execute(f'SELECT * FROM "{table}"')
    except sqlite3.Error as exc:
        print(f"warning: cannot read {source_label}:{table}: {exc}", file=sys.stderr)
        return []
    col_names = [d[0] for d in cur.description] if cur.description else []
    col_idx = {name: i for i, name in enumerate(col_names)}
    rows: list[dict] = []
    for raw in cur.fetchall():
        def col(name: str, default=None):
            idx = col_idx.get(name)
            if idx is None:
                return default
            return raw[idx]

        sid = col("id")
        if not sid:
            continue
        directory = col("directory") or ""
        project_id = col("project_id") or ""
        project_worktree = project_map.get(project_id, "")
        title = col("title") or ""
        # title in session_v2 is nullable; normalize None -> ""
        if title is None:
            title = ""
        time_created = col("time_created")
        time_updated = col("time_updated")
        # Normalize to int ms epoch; skip rows with no timestamps
        try:
            tc = int(time_created) if time_created is not None else 0
            tu = int(time_updated) if time_updated is not None else tc
        except (ValueError, TypeError):
            tc = 0
            tu = 0
        rows.append(
            {
                "id": str(sid),
                "directory": str(directory),
                "project": str(project_worktree),
                "project_id": str(project_id),
                "title": str(title),
                "time_created": tc,
                "time_updated": tu,
                "source": f"{source_label}:{table}",
            }
        )
    return rows


def read_snapshot(db_path: Path, label: str) -> list[dict]:
    """Open *db_path* read-only and return all session rows.

    Inspects sqlite_master at runtime: reads ``session`` always when present
    and additionally ``session_v2`` when present (main DB after the
    45-migration).  Does not hardcode table existence.
    """
    # Use URI with immutable flag to avoid WAL journal creation; the snapshot
    # already contains wal/shm sidecars so the reader sees a consistent view.
    uri = f"file:{db_path}?immutable=1"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        print(f"warning: cannot open {label} snapshot {db_path}: {exc}", file=sys.stderr)
        return []
    try:
        project_map = _load_project_map(conn)
        tables: list[str] = []
        if _table_exists(conn, "session"):
            tables.append("session")
        if _table_exists(conn, "session_v2"):
            tables.append("session_v2")
        if not tables:
            print(f"warning: {label} snapshot has no session table", file=sys.stderr)
            return []
        all_rows: list[dict] = []
        for t in tables:
            all_rows.extend(_read_session_table(conn, t, label, project_map))
        return all_rows
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Dedup / filter / sort helpers
# ---------------------------------------------------------------------------

def _richness_key(row: dict) -> tuple[int, int, int]:
    """Sort key for dedup: higher is richer.

    Primary: time_updated (ms).  Secondary: title length.  Tertiary:
    session_v2 is preferred (canonical v2 projection) so it wins ties
    when a legacy session row and its v2 projection are otherwise equal.
    """
    is_v2 = 1 if row["source"].endswith("session_v2") else 0
    return (int(row["time_updated"]), len(row["title"]), is_v2)


def dedupe(rows: list[dict]) -> list[dict]:
    """Deduplicate on session id, keeping the richest record per id."""
    best: dict[str, dict] = {}
    for r in rows:
        sid = r["id"]
        if sid not in best or _richness_key(r) > _richness_key(best[sid]):
            best[sid] = r
    return list(best.values())


def parse_date_to_ms(value: str) -> int:
    """Parse YYYY-MM-DD or ISO-8601 datetime string to ms epoch (UTC).

    Accepts:
      2026-08-09
      2026-08-09T02:38:00
      2026-08-09T02:38:00Z
      2026-08-09 02:38:00
    Bare dates are interpreted as 00:00:00 UTC.  Raises ValueError on failure.
    """
    raw = value.strip()
    # Normalize trailing Z to +00:00 for fromisoformat
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    # Try ISO parse first
    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError:
        # Fall back to date-only
        try:
            dt = datetime.datetime.strptime(raw, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"cannot parse date '{value}': expected YYYY-MM-DD or ISO-8601 (e.g. 2026-08-09 or 2026-08-09T02:38:00Z)"
            )
    # Ensure timezone-aware in UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        dt = dt.astimezone(datetime.timezone.utc)
    return int(dt.timestamp() * 1000)


def ms_to_iso(ms: int) -> str:
    """Convert ms epoch to ISO-8601 UTC string."""
    if not ms:
        return ""
    dt = datetime.datetime.fromtimestamp(ms / 1000, tz=datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_human(rows: list[dict]) -> str:
    if not rows:
        return "No sessions matched.\n"
    # Compute column widths (cap title at 50, directory at 60 for display)
    id_w = max(len("session id"), max(len(r["id"]) for r in rows))
    # Keep full directory in data but truncate display
    dir_display: list[str] = []
    for r in rows:
        d = r["directory"] or r["project"] or ""
        if len(d) > 60:
            d = "..." + d[-57:]
        dir_display.append(d)
    dir_w = max(len("project/directory"), max(len(d) for d in dir_display))
    title_display: list[str] = []
    for r in rows:
        t = r["title"] or ""
        if len(t) > 50:
            t = t[:47] + "..."
        title_display.append(t)
    title_w = max(len("title"), max(len(t) for t in title_display))
    src_w = max(len("source"), max(len(r["source"]) for r in rows))

    header = (
        f"{'session id':<{id_w}}  "
        f"{'project/directory':<{dir_w}}  "
        f"{'title':<{title_w}}  "
        f"{'created':<20}  "
        f"{'updated':<20}  "
        f"{'source':<{src_w}}"
    )
    sep = "-" * len(header)
    lines = [header, sep]
    for r, d, t in zip(rows, dir_display, title_display):
        created = ms_to_iso(r["time_created"])
        updated = ms_to_iso(r["time_updated"])
        lines.append(
            f"{r['id']:<{id_w}}  "
            f"{d:<{dir_w}}  "
            f"{t:<{title_w}}  "
            f"{created:<20}  "
            f"{updated:<20}  "
            f"{r['source']:<{src_w}}"
        )
    # Summary line
    lines.append("")
    lines.append(f"{len(rows)} session(s) total (deduped, sorted by updated desc).")
    return "\n".join(lines) + "\n"


def format_json(rows: list[dict]) -> str:
    # Emit ISO timestamps alongside raw ms for machine consumers
    enriched: list[dict] = []
    for r in rows:
        enriched.append(
            {
                "id": r["id"],
                "directory": r["directory"],
                "project": r["project"],
                "project_id": r["project_id"],
                "title": r["title"],
                "time_created": r["time_created"],
                "time_created_iso": ms_to_iso(r["time_created"]),
                "time_updated": r["time_updated"],
                "time_updated_iso": ms_to_iso(r["time_updated"]),
                "source": r["source"],
            }
        )
    return json.dumps(enriched, indent=2) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Union viewer for the split OpenCode session stores (see module docstring and #419).",
        epilog="Snapshot safety: live stores are copied to --snap-dir before querying; no writes outside the scratch dir.",
    )
    p.add_argument(
        "--snap-dir",
        type=Path,
        default=DEFAULT_SNAP_DIR,
        help=f"scratch directory for snapshot copies (default: {DEFAULT_SNAP_DIR})",
    )
    p.add_argument(
        "--store-dir",
        type=Path,
        default=DEFAULT_STORE_DIR,
        help=f"source directory containing opencode.db etc. (default: {DEFAULT_STORE_DIR})",
    )
    p.add_argument(
        "--include-local",
        action="store_true",
        help="also union the optional third store opencode-local.db (default: off)",
    )
    p.add_argument(
        "--project",
        dest="project_filter",
        default=None,
        help="filter: case-insensitive substring match against directory/project (e.g. ASES)",
    )
    p.add_argument(
        "--since",
        default=None,
        help="filter: only sessions with time_updated >= date (YYYY-MM-DD or ISO-8601, UTC)",
    )
    p.add_argument(
        "--until",
        default=None,
        help="filter: only sessions with time_updated <= date (YYYY-MM-DD or ISO-8601, UTC)",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="output JSON array instead of human-readable table",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Parse date filters early so we fail fast with exit 2
    since_ms: int | None = None
    until_ms: int | None = None
    if args.since is not None:
        try:
            since_ms = parse_date_to_ms(args.since)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
    if args.until is not None:
        try:
            until_ms = parse_date_to_ms(args.until)
        except ValueError as exc:
            parser.error(str(exc))
            return 2
    # Bare YYYY-MM-DD for --until should be inclusive to end-of-day
    if args.until is not None and len(args.until.strip()) == 10:
        # since_ms is start-of-day; make until end-of-day inclusive
        assert until_ms is not None
        until_ms += 24 * 60 * 60 * 1000 - 1

    # Determine which stores to snapshot
    stores = list(MANDATORY_STORES)
    if args.include_local:
        stores.append(OPTIONAL_LOCAL)

    snap_dir: Path = args.snap_dir
    store_dir: Path = args.store_dir

    snapshots = snapshot_copy(store_dir, snap_dir, stores)

    if not snapshots:
        print("error: no snapshot could be created (all stores missing or unreadable)", file=sys.stderr)
        return 1

    # Read and union
    all_rows: list[dict] = []
    for label, db_path in snapshots.items():
        rows = read_snapshot(db_path, label)
        all_rows.extend(rows)

    if not all_rows:
        # Distinguish "stores existed but empty" from "nothing at all"
        print("warning: no sessions found in any snapshot", file=sys.stderr)

    # Dedupe on id keeping richest
    deduped = dedupe(all_rows)

    # Apply filters
    filtered = deduped
    if args.project_filter is not None:
        needle = args.project_filter.lower()
        filtered = [
            r
            for r in filtered
            if needle in (r["directory"] or "").lower()
            or needle in (r["project"] or "").lower()
        ]
    if since_ms is not None:
        filtered = [r for r in filtered if int(r["time_updated"]) >= since_ms]
    if until_ms is not None:
        filtered = [r for r in filtered if int(r["time_updated"]) <= until_ms]

    # Sort by updated desc
    filtered.sort(key=lambda r: int(r["time_updated"]), reverse=True)

    # Emit
    if args.as_json:
        sys.stdout.write(format_json(filtered))
    else:
        sys.stdout.write(format_human(filtered))

    return 0


if __name__ == "__main__":
    sys.exit(main())
