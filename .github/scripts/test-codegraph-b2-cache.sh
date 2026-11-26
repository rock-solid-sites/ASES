#!/usr/bin/env bash
set -euo pipefail

root="$(mktemp -d "${RUNNER_TEMP:-/tmp}/codegraph-b2-test.XXXXXX")"
trap 'rm -rf "$root"' EXIT
mkdir -p "$root/bin" "$root/store" "$root/fixture"

cat > "$root/fixture/region.ts" <<'TS'
export function selectRegion(region: string): string {
  return normalize(region);
}
function normalize(region: string): string {
  return region.trim().toLowerCase();
}
TS
git -C "$root/fixture" init -q -b default
git -C "$root/fixture" -c user.name=Fixture -c user.email=fixture@example.invalid add .
git -C "$root/fixture" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm 'fixture source'

cat > "$root/bin/git" <<'SH'
#!/usr/bin/env bash
# Use real local Git transport and ref semantics for the fixture's public URL.
# Optional race injection moves a ref immediately before the fetch.
for arg in "$@"; do
  if [[ "$arg" == fetch && -n "${MOVE_REF_ON_FETCH:-}" ]]; then
    /usr/bin/git -C "$FIXTURE_REPO" update-ref refs/heads/racing "$MOVE_REF_ON_FETCH"
    break
  fi
done
exec /usr/bin/git -c "url.file://$FIXTURE_REPO.insteadOf=https://github.com/fixture/public.git" "$@"
SH
cat > "$root/bin/aws" <<'PY'
#!/usr/bin/env python3
import json, os, shutil, sys
args = sys.argv[1:]
operation = args[1]
with open(os.environ["MOCK_B2_LOG"], "a", encoding="utf-8") as log:
    log.write(operation + "\n")
def value(name):
    return args[args.index(name) + 1]
path = os.path.join(os.environ["MOCK_B2_STORE"], value("--key"))
if operation == "head-object":
    if not os.path.isfile(path):
        print("An error occurred (404) when calling HeadObject: Not Found", file=sys.stderr)
        raise SystemExit(1)
    with open(path + ".meta", encoding="utf-8") as metadata:
        digest = metadata.read().strip()
    print(json.dumps({"Metadata": {"sha256": digest}}))
elif operation == "get-object":
    shutil.copyfile(path, args[-1])
    print("{}")
elif operation == "put-object":
    os.makedirs(os.path.dirname(path), exist_ok=True)
    shutil.copyfile(value("--body"), path)
    with open(path + ".meta", "w", encoding="utf-8") as metadata:
        metadata.write(value("--metadata").split("=", 1)[1] + "\n")
    print("{}")
else:
    raise SystemExit("Unsupported mock S3 operation: " + operation)
PY
chmod +x "$root/bin/git" "$root/bin/aws"

if [[ -z "${CODEGRAPH_BIN:-}" || ! -x "$CODEGRAPH_BIN" ]]; then
  npm_config_cache="$root/npm-cache" npm install --prefix "$root/codegraph" --no-audit --no-fund @colbymchenry/codegraph@1.6.2 >/dev/null
  CODEGRAPH_BIN="$root/codegraph/node_modules/.bin/codegraph"
fi
export CODEGRAPH_BIN
export FIXTURE_REPO="$root/fixture"
export MOCK_B2_STORE="$root/store"
export MOCK_B2_LOG="$root/b2.log"
touch "$MOCK_B2_LOG"
export RUNNER_TEMP="$root/runs"
export PATH="$root/bin:$PATH"
export B2_CACHE_ENABLED=true
export B2_BUCKET=codegraph
export B2_REGION=eu-central-003
export B2_ENDPOINT=https://s3.eu-central-003.backblazeb2.com
export AWS_ACCESS_KEY_ID=fixture-key-id
export AWS_SECRET_ACCESS_KEY=fixture-app-key

run_fixture() {
  bash .github/scripts/codegraph-public-explore.sh fixture/public 'selectRegion callers' "$@"
}

first="$(git -C "$FIXTURE_REPO" rev-parse HEAD)"
run_fixture > "$root/fresh.txt"
grep -Fq '**Requested revision:** `default HEAD`' "$root/fresh.txt"
grep -Fq "**Commit:** `$first`" "$root/fresh.txt"
grep -Fq '**Index:** `fresh`' "$root/fresh.txt"
run_fixture > "$root/restored.txt"
grep -Fq '**Index:** `restored`' "$root/restored.txt"
grep -Fq 'Restored verified CodeGraph index' "$root/restored.txt"
grep -Fq 'normalize' "$root/restored.txt"

object="$(find "$root/store" -type f ! -name '*.meta' | head -1)"
cp "$object" "$root/good.tar.gz"
cp "$object.meta" "$root/good.meta"
printf 'corrupt' >> "$object"
if run_fixture > "$root/corrupt.txt" 2>&1; then
  echo 'Corrupt snapshot was accepted' >&2
  exit 1
fi
grep -Fq 'checksum does not match object metadata' "$root/corrupt.txt"
cp "$root/good.tar.gz" "$object"

tamper_manifest() {
python3 - "$object" "$1" "$2" <<'PY'
import io, json, os, sys, tarfile, tempfile
path, field, replacement_value = sys.argv[1:]
with tarfile.open(path, "r:gz") as source:
    members = [(member, source.extractfile(member).read() if member.isfile() else None) for member in source.getmembers()]
fd, replacement = tempfile.mkstemp(dir=os.path.dirname(path))
os.close(fd)
with tarfile.open(replacement, "w:gz") as target:
    for member, data in members:
        if member.name == ".codegraph-b2-manifest.json":
            manifest = json.loads(data)
            manifest[field] = replacement_value
            data = json.dumps(manifest).encode()
            info = tarfile.TarInfo(member.name)
            info.size = len(data)
            target.addfile(info, io.BytesIO(data))
        elif member.isdir():
            target.addfile(member)
        else:
            target.addfile(member, io.BytesIO(data))
os.replace(replacement, path)
PY
python3 - "$object" "$object.meta" <<'PY'
import hashlib, sys
with open(sys.argv[1], "rb") as archive:
    digest = hashlib.sha256(archive.read()).hexdigest()
with open(sys.argv[2], "w", encoding="utf-8") as metadata:
    metadata.write(digest + "\n")
PY
}
tamper_manifest repository tampered/repository
if run_fixture > "$root/manifest-repository.txt" 2>&1; then
  echo 'Manifest with a mismatched repository identity was accepted' >&2
  exit 1
fi
grep -Fq 'manifest is invalid or does not match' "$root/manifest-repository.txt"
tamper_manifest codegraph_version 0.0.0
if run_fixture > "$root/manifest-version.txt" 2>&1; then
  echo 'Manifest with a mismatched CodeGraph version was accepted' >&2
  exit 1
fi
grep -Fq 'manifest is invalid or does not match' "$root/manifest-version.txt"

cp "$root/good.tar.gz" "$object"
cp "$root/good.meta" "$object.meta"

printf '\nexport const anotherRegion = "eu-central-003";\n' >> "$root/fixture/region.ts"
git -C "$root/fixture" -c user.name=Fixture -c user.email=fixture@example.invalid add .
git -C "$root/fixture" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm 'new fixture commit'
run_fixture > "$root/new-commit.txt"
grep -Fq '**Index:** `fresh`' "$root/new-commit.txt"
grep -Fq 'Stored verified CodeGraph index' "$root/new-commit.txt"

echo 'PASS: first-run upload and verified restore'
echo 'PASS: corrupted archive rejected'
echo 'PASS: mismatched repository and CodeGraph manifest identities rejected'
echo 'PASS: different source commit gets a distinct fresh index'

# Revisions must identify actual fixture commits, not merely produce a cache hit.
second="$(git -C "$FIXTURE_REPO" rev-parse HEAD)"
assert_result() {
  local file="$1" requested="$2" expected="$3" mode="$4"
  grep -Fq "**Requested revision:** \`$requested\`" "$file"
  grep -Fq "**Commit:** \`$expected\`" "$file"
  grep -Fq "**Index:** \`$mode\`" "$file"
}
# A feature branch differs from the actual default branch.
git -C "$FIXTURE_REPO" branch feature "$first"
git -C "$FIXTURE_REPO" tag lightweight "$first"
git -C "$FIXTURE_REPO" -c user.name=Fixture -c user.email=fixture@example.invalid tag -a annotated "$first" -m annotated
run_fixture refs/heads/feature > "$root/branch.txt"
assert_result "$root/branch.txt" refs/heads/feature "$first" restored
run_fixture refs/tags/lightweight > "$root/lightweight.txt"
assert_result "$root/lightweight.txt" refs/tags/lightweight "$first" restored
run_fixture refs/tags/annotated > "$root/annotated.txt"
assert_result "$root/annotated.txt" refs/tags/annotated "$first" restored
run_fixture "$first" > "$root/older-sha.txt"
assert_result "$root/older-sha.txt" "$first" "$first" restored
bash .github/scripts/codegraph-public-explore.sh --issue-title '[codegraph] fixture/public@refs/heads/feature' 'selectRegion callers' > "$root/issue-ref.txt"
assert_result "$root/issue-ref.txt" refs/heads/feature "$first" restored
bash .github/scripts/codegraph-public-explore.sh --issue-title '[codegraph] fixture/public' 'selectRegion callers' > "$root/issue-default.txt"
assert_result "$root/issue-default.txt" 'default HEAD' "$second" restored

# Advance the feature to a distinct third commit while default remains second.
git -C "$FIXTURE_REPO" checkout -q feature
printf '\nexport const featureOnly = "feature";\n' >> "$FIXTURE_REPO/region.ts"
git -C "$FIXTURE_REPO" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qam 'feature advance'
third="$(git -C "$FIXTURE_REPO" rev-parse HEAD)"
git -C "$FIXTURE_REPO" checkout -q default
run_fixture refs/heads/feature > "$root/advanced.txt"
assert_result "$root/advanced.txt" refs/heads/feature "$third" fresh
run_fixture "$first" > "$root/replay.txt"
assert_result "$root/replay.txt" "$first" "$first" restored
[[ "$(find "$root/store" -type f ! -name '*.meta' | wc -l)" -eq 3 ]]
echo 'PASS: branch/tag/SHA selection, same-commit aliases, advancing branch, historical replay, default and issue title compatibility'

reject_without_b2() {
  local before
  before="$(wc -l < "$MOCK_B2_LOG")"
  if "$@" > "$root/rejected.txt" 2>&1; then
    echo 'Invalid or unavailable revision accepted' >&2
    cat "$root/rejected.txt" >&2
    exit 1
  fi
  [[ "$(wc -l < "$MOCK_B2_LOG")" == "$before" ]]
}
blob="$(git -C "$FIXTURE_REPO" rev-parse HEAD:region.ts)"
git -C "$FIXTURE_REPO" tag noncommit "$blob"
for bad in refs/heads/missing refs/tags/missing refs/tags/noncommit "$blob" 0000000000000000000000000000000000000000 feature HEAD 'HEAD~1' '--upload-pack=bad' 'refs/heads/../default' 'refs/heads/default:refs/heads/evil' 'refs/heads/default@{1}' 'refs/heads/default^{}' 'refs/heads/a b' 'refs/heads/a;touch' $'refs/heads/a\nb'; do
  reject_without_b2 run_fixture "$bad"
done
git -C "$FIXTURE_REPO" tag feature "$second"
reject_without_b2 run_fixture feature
reject_without_b2 bash .github/scripts/codegraph-public-explore.sh --issue-title '[codegraph] fixture/public@' 'selectRegion callers'
reject_without_b2 bash .github/scripts/codegraph-public-explore.sh --issue-title '[codegraph] fixture/public@refs/heads/feature@oops' 'selectRegion callers'
reject_without_b2 bash .github/scripts/codegraph-public-explore.sh '../public' 'selectRegion callers'
git -C "$FIXTURE_REPO" branch racing "$first"
export MOVE_REF_ON_FETCH="$second"
reject_without_b2 run_fixture refs/heads/racing
grep -Fq 'Requested ref moved' "$root/rejected.txt"
unset MOVE_REF_ON_FETCH
echo 'PASS: invalid, unavailable, ambiguous, noncommit and moved revisions rejected before cache access'
