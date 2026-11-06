#!/usr/bin/env bash
# Upload ONLY age ciphertext. The private decryption key must remain outside CI.
set -Eeuo pipefail
umask 077
: "${SOURCE_COMMIT:?}"; : "${RUN_ID:?}"; : "${AGE_RECIPIENT:?}"
: "${R2_ACCOUNT_ID:?}"; : "${R2_ACCESS_KEY_ID:?}"; : "${R2_SECRET_ACCESS_KEY:?}"
: "${SOURCE_TAR:?}"; : "${BACKUP_OUTPUT:?}"
test -s "$SOURCE_TAR"
mkdir -p "$BACKUP_OUTPUT"
RAW_SIZE=$(stat -c %s "$SOURCE_TAR")
test "$RAW_SIZE" -le 50000000
[[ "$AGE_RECIPIENT" =~ ^age1[0-9a-z]+$ ]] || { echo "Require an age PUBLIC recipient"; exit 1; }
CIPHER="$BACKUP_OUTPUT/evidence.tar.gz.age"
age -r "$AGE_RECIPIENT" -o "$CIPHER" "$SOURCE_TAR"
sha256sum "$SOURCE_TAR" > "$BACKUP_OUTPUT/plaintext.sha256"
sha256sum "$CIPHER" > "$BACKUP_OUTPUT/ciphertext.sha256"
RUN_ATTEMPT="${RUN_ATTEMPT:-1}"
[[ "$RUN_ATTEMPT" =~ ^[1-9][0-9]*$ ]] || { echo "Invalid run attempt"; exit 1; }
KEY="ases/phase-i/$RUN_ID/attempt-$RUN_ATTEMPT/$SOURCE_COMMIT/evidence.tar.gz.age"
export RCLONE_CONFIG_R2_TYPE=s3 RCLONE_CONFIG_R2_PROVIDER=Cloudflare
export RCLONE_CONFIG_R2_ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
export RCLONE_CONFIG_R2_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"
export RCLONE_CONFIG_R2_ENV_AUTH=false RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true
verify_remote() {
  local name="$1" object="$2" recovered="$BACKUP_OUTPUT/readback-$1.age"
  rclone copyto "$CIPHER" "$object" --immutable --s3-no-check-bucket
  rclone cat "$object" --s3-no-check-bucket > "$recovered"
  cmp -s "$CIPHER" "$recovered"
  sha256sum "$recovered" > "$BACKUP_OUTPUT/readback-$name.sha256"
  rm "$recovered"
}
verify_remote r2 "r2:ases-assurance-evidence/$KEY"
E2_STATUS=BLOCKED_NOT_CONFIGURED
if [[ -n "${E2_ENDPOINT:-}" || -n "${E2_ACCESS_KEY_ID:-}" || -n "${E2_SECRET_ACCESS_KEY:-}" || -n "${E2_BUCKET:-}" ]]; then
  : "${E2_ENDPOINT:?incomplete mirror}"; : "${E2_ACCESS_KEY_ID:?incomplete mirror}"
  : "${E2_SECRET_ACCESS_KEY:?incomplete mirror}"; : "${E2_BUCKET:?incomplete mirror}"
  export RCLONE_CONFIG_E2_TYPE=s3 RCLONE_CONFIG_E2_PROVIDER=IDrive
  export RCLONE_CONFIG_E2_ENDPOINT="$E2_ENDPOINT"
  export RCLONE_CONFIG_E2_ACCESS_KEY_ID="$E2_ACCESS_KEY_ID"
  export RCLONE_CONFIG_E2_SECRET_ACCESS_KEY="$E2_SECRET_ACCESS_KEY"
  export RCLONE_CONFIG_E2_ENV_AUTH=false RCLONE_CONFIG_E2_NO_CHECK_BUCKET=true
  verify_remote e2 "e2:$E2_BUCKET/$KEY"
  E2_STATUS=CIPHERTEXT_READBACK_VERIFIED
fi
printf '{"run_id":"%s","commit":"%s","r2":"CIPHERTEXT_READBACK_VERIFIED","idrive_e2":"%s","private_key_off_ci":true,"decrypt_restore":"NOT_TESTED"}\n' "$RUN_ID" "$SOURCE_COMMIT" "$E2_STATUS" > "$BACKUP_OUTPUT/attestation.json"
rm "$CIPHER"
echo "Encrypted object uploaded; remote ciphertext readback verified"
