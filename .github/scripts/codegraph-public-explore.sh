#!/usr/bin/env bash
set -euo pipefail

# Public issue titles and manual dispatch share the same validated source selector.
if [[ "${1:-}" == "--issue-title" ]]; then
  [[ $# -eq 3 && "$2" == '[codegraph] '* ]] || { echo 'Invalid CodeGraph issue title' >&2; exit 1; }
  request="${2#\[codegraph\] }"
  question="$3"
  repo="${request%%@*}"
  revision=""
  if [[ "$request" == *@* ]]; then
    revision="${request#*@}"
    [[ -n "$revision" ]] || { echo 'Empty revision suffix' >&2; exit 1; }
  fi
else
  [[ $# -ge 2 && $# -le 3 ]] || { echo 'Usage: owner/repository question [revision]' >&2; exit 1; }
  repo="$1"
  question="$2"
  revision="${3:-}"
fi
cli_version="1.6.2"
cache_enabled="${B2_CACHE_ENABLED:-false}"

if [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ || "${repo%%/*}" == . || "${repo%%/*}" == .. || "${repo#*/}" == . || "${repo#*/}" == .. ]]; then
  echo 'Invalid repository: use owner/repository' >&2
  exit 1
fi
if [[ -z "${question//[[:space:]]/}" || ${#question} -gt 2000 ]]; then
  echo 'Question must contain 1-2000 characters' >&2
  exit 1
fi

# Only full object IDs or explicit branch/tag refs, never revision expressions or refspecs.
if [[ -n "$revision" ]]; then
  if [[ "$revision" =~ ^[0-9a-fA-F]{40}$ ]]; then
    revision_kind=sha
  elif [[ ${#revision} -le 255 && "$revision" =~ ^refs/(heads|tags)/[A-Za-z0-9._/-]+$ ]] && git check-ref-format "$revision"; then
    revision_kind=ref
  else
    echo 'Invalid revision: use refs/heads/..., refs/tags/... or a full 40-hex commit SHA' >&2
    exit 1
  fi
fi
export GIT_TERMINAL_PROMPT=0

if [[ "$cache_enabled" == 'true' ]]; then
  for name in B2_BUCKET B2_REGION B2_ENDPOINT AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY; do
    if [[ -z "${!name:-}" ]]; then
      echo "Required GitHub environment setting is missing: $name" >&2
      exit 1
    fi
  done
fi

export CODEGRAPH_NO_DAEMON=1
export CODEGRAPH_NO_WATCH=1
export CODEGRAPH_TELEMETRY=0

temp_root="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/codegraph-public-explore-${RANDOM}-${RANDOM}"
source_dir="$temp_root/source"
archive="$temp_root/index.tar.gz"
manifest="$temp_root/manifest.json"
engine="${CODEGRAPH_BIN:-$temp_root/codegraph/node_modules/.bin/codegraph}"
mkdir -p "$source_dir" "$(dirname "$engine")"
trap 'rm -rf "$temp_root"' EXIT

# No checkout credentials or credential helper: the target must be public.
public_git() {
  git -c credential.helper= -c http.https://github.com/.extraheader= "$@"
}
url="https://github.com/${repo}.git"
if [[ -z "$revision" ]]; then
  public_git clone --quiet --depth 1 --no-tags "$url" "$source_dir"
  commit="$(git -C "$source_dir" rev-parse --verify HEAD^{commit})"
else
  git -C "$source_dir" init --quiet
  git -C "$source_dir" remote add origin "$url"
  fetch_revision="$revision"
  if [[ "$revision_kind" == sha ]]; then
    expected_object="${revision,,}"
    fetch_revision="$expected_object"
  else
    # Record the exact advertised object before fetch; reject a ref that moves.
    advertised="$(public_git ls-remote --exit-code "$url" "$revision" "$revision^{}")" || {
      echo 'Requested revision unavailable' >&2
      exit 1
    }
    expected_object="$(awk -v ref="$revision" '$2 == ref {print $1}' <<<"$advertised")"
    [[ "$expected_object" =~ ^[0-9a-f]{40}$ ]] || { echo 'Requested ref is missing or ambiguous' >&2; exit 1; }
  fi
  public_git -C "$source_dir" fetch --quiet --depth 1 --no-tags origin "$fetch_revision" || {
    echo 'Requested revision unavailable; no fallback to HEAD' >&2
    exit 1
  }
  actual_object="$(git -C "$source_dir" rev-parse --verify FETCH_HEAD)"
  [[ "$actual_object" == "$expected_object" ]] || { echo 'Requested ref moved during resolution; refusing a different snapshot' >&2; exit 1; }
  commit="$(git -C "$source_dir" rev-parse --verify 'FETCH_HEAD^{commit}')" || {
    echo 'Requested revision is not a commit' >&2
    exit 1
  }
  if [[ "$revision_kind" == sha && "$commit" != "$expected_object" ]]; then
    echo 'Requested SHA does not identify a commit' >&2
    exit 1
  fi
  git -C "$source_dir" checkout --quiet --detach "$commit"
fi
if [[ ! "$commit" =~ ^[0-9a-f]{40}$ || "$(git -C "$source_dir" rev-parse --verify HEAD)" != "$commit" ]]; then
  echo 'Checkout returned an invalid or mismatched commit SHA' >&2
  exit 1
fi

if [[ ! -x "$engine" ]]; then
  npm install --prefix "$temp_root/codegraph" --no-audit --no-fund "@colbymchenry/codegraph@$cli_version"
fi
if [[ "$("$engine" --version)" != "$cli_version" ]]; then
  echo "Unexpected CodeGraph CLI version; expected $cli_version" >&2
  exit 1
fi

cache_key="codegraph/v1/${repo}/${commit}/codegraph-${cli_version}-linux-x64"
archive_key="${cache_key}.tar.gz"
cache_hit=false

if [[ "$cache_enabled" == 'true' ]]; then
  aws_args=(--endpoint-url "$B2_ENDPOINT" --region "$B2_REGION")
  check_object() {
    local key="$1" error_file="$2"
    if aws s3api head-object --bucket "$B2_BUCKET" --key "$key" "${aws_args[@]}" >/dev/null 2>"$error_file"; then
      return 0
    fi
    if grep -Eqi '404|Not Found|NoSuchKey' "$error_file"; then
      return 1
    fi
    cat "$error_file" >&2
    echo "Unable to check Backblaze object: $key" >&2
    return 2
  }

  status=0
  check_object "$archive_key" "$temp_root/archive-head.err" && cache_object_exists=true || status=$?
  if [[ "$status" -gt 1 ]]; then exit 1; fi
  if [[ "$status" -eq 0 ]]; then
    cache_object_exists=true
  else
    cache_object_exists=false
  fi

  if [[ "$cache_object_exists" == true ]]; then
    head_json="$(aws s3api head-object --bucket "$B2_BUCKET" --key "$archive_key" "${aws_args[@]}")"
    expected_archive_hash="$(jq -er '.Metadata.sha256 | select(test("^[0-9a-f]{64}$"))' <<<"$head_json")" || {
      echo 'Backblaze cache object is missing valid SHA-256 metadata' >&2
      exit 1
    }
    aws s3api get-object --bucket "$B2_BUCKET" --key "$archive_key" "${aws_args[@]}" "$archive" >/dev/null
    archive_hash="$(sha256sum "$archive" | cut -d ' ' -f 1)"
    if [[ "$archive_hash" != "$expected_archive_hash" ]]; then
      echo 'Backblaze snapshot checksum does not match object metadata' >&2
      exit 1
    fi
    tar -tzf "$archive" > "$temp_root/archive-files.txt"
    python3 - "$temp_root/archive-files.txt" <<'PY'
from pathlib import PurePosixPath
import sys
for line in open(sys.argv[1], encoding="utf-8"):
    path = PurePosixPath(line.rstrip("\n"))
    if path.is_absolute() or ".." in path.parts or path.parts[0] not in {".codegraph", ".codegraph-b2-manifest.json"}:
        raise SystemExit("Backblaze archive contains an unsafe path")
PY
    python3 - "$archive" <<'PY'
import sys, tarfile
with tarfile.open(sys.argv[1], "r:gz") as archive:
    for member in archive.getmembers():
        if not (member.isfile() or member.isdir()):
            raise SystemExit("Backblaze archive contains a link or special file")
        if member.name.startswith(".codegraph-b2-manifest.json/"):
            raise SystemExit("Backblaze archive manifest must be a regular file")
PY
    tar -xzf "$archive" --no-same-owner --no-same-permissions -C "$source_dir"
    mv "$source_dir/.codegraph-b2-manifest.json" "$manifest"
    jq -e --arg repo "$repo" --arg commit "$commit" --arg version "$cli_version" \
      '.manifest_version == 1 and .repository == $repo and .commit == $commit and .codegraph_version == $version and .platform == "linux-x64" and (.extraction_version | type == "number") and (.database_sha256 | test("^[0-9a-f]{64}$"))' \
      "$manifest" >/dev/null || {
        echo 'Backblaze cache manifest is invalid or does not match this source and CodeGraph version' >&2
        exit 1
      }

    status_json="$("$engine" status --json "$source_dir")"
    jq -e --arg version "$cli_version" --arg extraction "$(jq -r '.extraction_version' "$manifest")" \
      '.initialized == true and .index.state == "complete" and .index.reindexRecommended == false and .index.builtWithVersion == $version and (.index.builtWithExtractionVersion | tostring) == $extraction' \
      <<<"$status_json" >/dev/null || {
        echo 'Restored CodeGraph index is incomplete or incompatible; refusing to query it' >&2
        exit 1
      }
    database_hash="$(sha256sum "$source_dir/.codegraph/codegraph.db" | cut -d ' ' -f 1)"
    if [[ "$database_hash" != "$(jq -r '.database_sha256' "$manifest")" ]]; then
      echo 'Restored CodeGraph database checksum does not match its manifest' >&2
      exit 1
    fi
    cache_hit=true
    echo "Restored verified CodeGraph index for $repo at $commit"
  fi
fi

if [[ "$cache_hit" != true ]]; then
  echo "Building CodeGraph index for $repo at $commit"
  "$engine" init --yes "$source_dir" > "$temp_root/codegraph-index.log" 2>&1 || {
    tail -n 60 "$temp_root/codegraph-index.log" >&2
    exit 1
  }
  status_json="$("$engine" status --json "$source_dir")"
  jq -e --arg version "$cli_version" \
    '.initialized == true and .index.state == "complete" and .index.reindexRecommended == false and .index.builtWithVersion == $version and (.index.builtWithExtractionVersion | type == "number")' \
    <<<"$status_json" >/dev/null || {
      echo 'Fresh CodeGraph index is incomplete or incompatible' >&2
      exit 1
    }
fi

python3 - "$source_dir/.codegraph/codegraph.db" <<'PY'
import sqlite3, sys
with sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True) as db:
    result = db.execute("PRAGMA quick_check").fetchone()[0]
    if result != "ok":
        raise SystemExit(f"SQLite quick_check failed: {result}")
PY

printf '**Repository:** `%s`  \n**Requested revision:** `%s`  \n**Commit:** `%s`  \n**CodeGraph:** `%s`  \n**Index:** `%s`\n\n' \
  "$repo" "${revision:-default HEAD}" "$commit" "$cli_version" "$([[ "$cache_hit" == true ]] && echo restored || echo fresh)" > "$temp_root/codegraph-answer.md"
(cd "$source_dir" && "$engine" explore "$question") >> "$temp_root/codegraph-answer.md"

if [[ "$cache_enabled" == 'true' && "$cache_hit" != true ]]; then
  database_hash="$(sha256sum "$source_dir/.codegraph/codegraph.db" | cut -d ' ' -f 1)"
  extraction_version="$(jq -r '.index.builtWithExtractionVersion' <<<"$status_json")"
  cat > "$manifest" <<EOF
{
  "manifest_version": 1,
  "repository": "$repo",
  "commit": "$commit",
  "codegraph_version": "$cli_version",
  "extraction_version": $extraction_version,
  "platform": "linux-x64",
  "database_sha256": "$database_hash",
  "file_count": $(jq -r '.fileCount' <<<"$status_json"),
  "node_count": $(jq -r '.nodeCount' <<<"$status_json"),
  "edge_count": $(jq -r '.edgeCount' <<<"$status_json")
}
EOF
  cp "$manifest" "$source_dir/.codegraph-b2-manifest.json"
  tar -czf "$archive" -C "$source_dir" .codegraph .codegraph-b2-manifest.json
  archive_hash="$(sha256sum "$archive" | cut -d ' ' -f 1)"
  aws s3api put-object --bucket "$B2_BUCKET" --key "$archive_key" --body "$archive" \
    --metadata "sha256=$archive_hash" "${aws_args[@]}" >/dev/null
  echo "Stored verified CodeGraph index ($archive_hash; $(wc -c < "$archive" | tr -d ' ') compressed bytes)"
fi

echo '--- Resource evidence ---'
du -sh "$source_dir/.codegraph"
wc -c "$temp_root/codegraph-answer.md"
head -c 40000 "$temp_root/codegraph-answer.md"
