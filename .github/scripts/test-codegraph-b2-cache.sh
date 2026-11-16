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
git -C "$root/fixture" init -q
git -C "$root/fixture" -c user.name=Fixture -c user.email=fixture@example.invalid add .
git -C "$root/fixture" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm 'fixture source'

cat > "$root/bin/git" <<'SH'
#!/usr/bin/env bash
if [[ "$1" == clone ]]; then
  exec /usr/bin/git clone -q "$FIXTURE_REPO" "${@: -1}"
fi
exec /usr/bin/git "$@"
SH
cat > "$root/bin/aws" <<'PY'
#!/usr/bin/env python3
import json, os, shutil, sys
args = sys.argv[1:]
operation = args[1]
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
export RUNNER_TEMP="$root/runs"
export PATH="$root/bin:$PATH"
export B2_CACHE_ENABLED=true
export B2_BUCKET=codegraph
export B2_REGION=eu-central-003
export B2_ENDPOINT=https://s3.eu-central-003.backblazeb2.com
export AWS_ACCESS_KEY_ID=fixture-key-id
export AWS_SECRET_ACCESS_KEY=fixture-app-key

run_fixture() {
  bash .github/scripts/codegraph-public-explore.sh fixture/public 'selectRegion callers'
}

run_fixture > "$root/fresh.txt"
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
