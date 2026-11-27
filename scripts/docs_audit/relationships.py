"""Observed document relationships, not instruction authority or semantic equivalence."""
from collections import defaultdict
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit

FIELDS = {"depends_on", "consumed_by", "related_documents", "implements",
          "implemented_by", "supersedes", "superseded_by", "adapted_from"}
DOWNSTREAM = {"consumed_by", "implemented_by"}
RETIRED = {"historical", "deprecated", "archived", "superseded"}
DOC = re.compile(r"\.mdx?(?:#[^\s]*)?$", re.I)
LINK = re.compile(r"\]\((<[^>]+>|[^)\n]+)\)")
URL = re.compile(r"https?://(?:github\.com|raw\.githubusercontent\.com)/[^\s<>\)\]\x60]+", re.I)
KEY = re.compile(r"^([\w-]+):\s*(.*)$")
ITEM = re.compile(r"^\s*[-*]\s+(.+?)\s*$")


def scalar(s):
    return s.strip().strip('\"\'')


def observations(text):
    """Conservative block-list metadata and visible lexical references with line evidence."""
    lines = text.splitlines()
    field = None
    end = 0
    if lines and lines[0].strip() == "---" and "---" in lines[1:]:
        end = lines.index("---", 1) + 1
        for n, line in enumerate(lines[1:end-1], 2):
            key = KEY.match(line)
            if key:
                field, value = key.groups()
                if field in FIELDS and value and value != "[]":
                    yield field, scalar(value), n, "metadata", not value.startswith(("[", "{", "|", ">"))
            elif field in FIELDS and (item := ITEM.match(line)):
                yield field, scalar(item.group(1)), n, "metadata", True
            elif line.strip() and not line.lstrip().startswith("#"):
                field = None
    fence = None
    heading = ""
    for n, line in enumerate(lines[end:], end+1):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence:
            continue
        if stripped.startswith("#"):
            heading = stripped.lstrip("# ")
        code = re.findall(r"`([^`\n]+)`", line)
        visible = re.sub(r"`[^`\n]+`", "", line)
        refs = [("markdown_link", x.strip("<>")) for x in LINK.findall(visible)]
        refs += [("github_url", x.rstrip(".,;")) for x in URL.findall(visible)]
        refs += [("literal_path", x) for x in code if not any(c in x for c in "[]()")]
        seen = set()
        for kind, value in refs:
            if DOC.search(value) and value not in seen:
                seen.add(value)
                yield kind, value, n, heading, True


def source_state(root):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    try:
        return {"revision": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain"))}
    except (OSError, subprocess.CalledProcessError):
        return {"revision": "UNVERIFIED", "dirty": None}


def consumer_snapshot(spec):
    repo, sep, folder = spec.partition("=")
    if not sep or not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("consumer root must be OWNER/REPO=PATH")
    root = Path(folder).resolve()
    state = source_state(root)
    if state["revision"] == "UNVERIFIED" or state["dirty"]:
        raise ValueError("consumer root must be a clean Git checkout: " + repo)
    paths = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"]).decode().split("\0")
    texts = {p: (root / p).read_text(encoding="utf-8", errors="replace") for p in paths
             if p.lower().endswith((".md", ".mdx")) and (root / p).is_file()
             and not (root / p).is_symlink()}
    return repo, texts, set(paths), state


def relationship_graph(repo, texts, existing, records, state, extra=()):
    """Reverse observed edges; never imply semantic dependence from a hyperlink."""
    roots = {repo.casefold(): (repo, texts, existing, state)}
    for name, body, paths, info in extra:
        if name.casefold() in roots:
            raise ValueError("duplicate repository: " + name)
        roots[name.casefold()] = (name, body, paths, info)
    primary = {d["path"]: d for d in records}
    aliases = defaultdict(set)
    for key, (name, body, paths, info) in roots.items():
        for p in body:
            aliases[key, PurePosixPath(p).stem.casefold()].add(p)
            title = re.search(r"^title:\s*(.+)$", body[p].split("\n---", 1)[0], re.M)
            if title and body[p].startswith("---\n"):
                aliases[key, scalar(title.group(1)).casefold()].add(p)
    edges, incoming, review = [], defaultdict(list), []
    for key, (name, body, paths, info) in roots.items():
        for path, text in sorted(body.items()):
            for kind, value, line, heading, supported in observations(text):
                target_key, target, ref, result = key, None, None, "unresolved"
                raw = unquote(value.split("#", 1)[0])
                url = urlsplit(raw) if raw.startswith(("https://", "http://")) else None
                if not supported:
                    result = "unsupported_metadata"
                elif url:
                    parts = url.path.strip("/").split("/")
                    if url.hostname == "github.com" and len(parts) >= 5 and parts[2] == "blob":
                        target_key, ref, target = "/".join(parts[:2]).casefold(), parts[3], "/".join(parts[4:])
                    elif url.hostname == "raw.githubusercontent.com" and len(parts) >= 4:
                        target_key, ref, target = "/".join(parts[:2]).casefold(), parts[2], "/".join(parts[3:])
                    if target:
                        result = ("pinned_revision" if re.fullmatch(r"[0-9a-fA-F]{40}", ref)
                                  else "snapshot_path" if ref in {"main", "master"} and target_key in roots and target in roots[target_key][2]
                                  else "unverified_remote")
                else:
                    parts = raw.split("/", 2)
                    qualified = len(parts) == 3 and "/".join(parts[:2]).casefold() in roots
                    if qualified:
                        target_key, raw = "/".join(parts[:2]).casefold(), parts[2]
                    known = roots[target_key][2]
                    relative = posixpath.normpath(posixpath.join(posixpath.dirname(path), raw))
                    options = {raw} if qualified else {relative} if kind == "markdown_link" else {raw, relative}
                    found = options & known
                    if len(found) == 1:
                        target, result = next(iter(found)), "snapshot_path"
                    elif len(found) > 1:
                        result = "ambiguous_path"
                    elif kind in FIELDS and not DOC.search(raw):
                        matches = aliases[target_key, raw.casefold()]
                        if len(matches) == 1:
                            target, result = next(iter(matches)), "unique_alias"
                        elif len(matches) > 1:
                            result = "ambiguous_alias"
                    elif kind == "markdown_link":
                        result = "missing_relative_path"
                target_repo = roots[target_key][0] if target_key in roots else target_key
                edge = {"source_repo": name, "source_path": path, "line": line, "section": heading,
                        "kind": kind, "reference": value, "target_repo": target_repo,
                        "target_path": target, "ref": ref, "resolution": result,
                        "target_scanned": bool(target_key in roots and target in roots[target_key][1])}
                edges.append(edge)
                # A pinned adaptation is a live reconciliation relationship, not an ordinary historical citation.
                # Preserve a removed source path so its deletion still triggers consideration.
                if not target or (result not in {"snapshot_path", "unique_alias"}
                                  and not (kind == "adapted_from" and target_key in roots
                                           and result in {"pinned_revision", "unverified_remote"})):
                    continue
                if kind in DOWNSTREAM:
                    subject, consumer = f"{name}:{path}", f"{target_repo}:{target}"
                elif kind in {"depends_on", "implements", "markdown_link", "github_url", "literal_path", "adapted_from"}:
                    subject, consumer = f"{target_repo}:{target}", f"{name}:{path}"
                else:
                    continue
                if subject != consumer:
                    incoming[subject].append({"consumer": consumer, "edge": len(edges)-1,
                                              "action": "consider_reconciliation" if kind == "adapted_from" else "inspect_reference"})
                if key == repo.casefold() and target_key == key:
                    src, dst = primary.get(path, {}), primary.get(target, {})
                    if src.get("declared_active") and dst.get("status", "").lower().split("(")[0].strip() in RETIRED:
                        review.append({"edge": len(edges)-1, "reason": "current-source reference to retired document; inspect context"})
    return {"scope": [{"repository": n, **s, "scanned_documents": len(t)} for n, t, p, s in roots.values()],
            "edges": edges, "incoming_candidates": dict(sorted(incoming.items())), "review_candidates": review,
            "limits": "Lexical and declared references only; no authority inference, remote ref validation, semantic drift detection, or unseen consumer guarantee. External roots require private handling."}


def changed_source_paths(root, revision):
    """Diff committed source paths, including both names on rename; never mutate checkouts."""
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", revision):
        raise ValueError("changed-since requires a Git commit SHA")
    command = ["git", "-C", str(root)]
    subprocess.check_output(command + ["rev-parse", "--verify", revision + "^{commit}"], stderr=subprocess.DEVNULL)
    return set(subprocess.check_output(command + ["diff", "--no-renames", "--name-only", "-z",
                                                   revision, "HEAD", "--"]).decode().split("\\0")) - {""}


def reconciliation_candidates(graph, repo, paths):
    """A source change flags affected consumers; no file replacements or baseline promotion."""
    out = []
    for path in sorted(paths):
        source = repo + ":" + path
        for item in graph["incoming_candidates"].get(source, []):
            out.append({"source": source, **item, "evidence": graph["edges"][item["edge"]]})
    return out
