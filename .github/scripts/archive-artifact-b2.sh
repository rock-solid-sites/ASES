#!/usr/bin/env bash
# Upload one already-created evidence file and verify exact bytes by restoring it.
# Call only from a trusted job using the dedicated rss-github-artifacts environment.
set -euo pipefail
[[ $# = 2 ]] || { echo 'usage: bash archive-artifact-b2.sh FILE OBJECT_KEY' >&2; exit 2; }
file="$1"
key="$2"
[[ -f "$file" && -s "$file" && "$key" =~ ^[A-Za-z0-9_./-]+$ && "$key" != /* && "$key" != *..* ]] || exit 2
: "${AWS_ACCESS_KEY_ID:?}" "${AWS_SECRET_ACCESS_KEY:?}" "${B2_BUCKET:?}" "${B2_REGION:?}" "${B2_ENDPOINT:?}"
[[ "$B2_BUCKET" = rss-github-artifacts && "$B2_ENDPOINT" =~ ^https://s3[.][a-z0-9-]+[.]backblazeb2[.]com/?$ ]] || exit 2
export AWS_PAGER='' AWS_MAX_ATTEMPTS=1
args=(--endpoint-url "$B2_ENDPOINT" --region "$B2_REGION" --no-cli-pager --cli-connect-timeout 15 --cli-read-timeout 60)
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
digest="$(sha256sum "$file" | cut -d' ' -f1)"
aws s3api put-object --bucket "$B2_BUCKET" --key "$key" --body "$file" --metadata "sha256=$digest" "${args[@]}" > "$work/put.json"
aws s3api get-object --bucket "$B2_BUCKET" --key "$key" "${args[@]}" "$work/restored" > "$work/get.json"
cmp "$file" "$work/restored"
[[ "$(sha256sum "$work/restored" | cut -d' ' -f1)" = "$digest" ]]
printf 'B2_ARCHIVE_VERIFIED bucket=%s key=%s bytes=%s sha256=%s\n' "$B2_BUCKET" "$key" "$(wc -c < "$file")" "$digest"
