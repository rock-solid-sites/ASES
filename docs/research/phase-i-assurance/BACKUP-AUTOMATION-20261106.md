# ASES evidence preservation: automatic private backups (pilot)

Status 2026-11-06: **R2 bucket created and private, workflow backup step installed but BLOCKED until credentials and recipient are configured.** This is experimental branch-only infrastructure and does not create a global ASES policy.

## Architecture and separation

- **Source**: immutable per-run GitHub Actions export artifact with raw probe stdout/stderr, hashes, model traces, failure controls, and exact replay manifests. On every experimental CI run, the `evidence-export` job collects the original source artifacts; a clean restored checksum check is required.
- **Encryption boundary**: CI receives only the **age public recipient**. It encrypts `phase-i-evidence.tar.gz` locally before transfer. GitHub never receives the private age identity; neither R2 nor IDrive e2 receives plaintext. Retain and independently back up the private identity under user control, with a cold-machine restore test.
- **Primary destination**: R2 private, Standard-class bucket `ases-assurance-evidence` (created in western Europe on 2026-11-06). No custom/public r2.dev domains enabled. Keys are restricted to this bucket; the existing `projektor-rss-files` bucket is untouched.
- **Secondary destination**: IDrive e2, existing free allowance, using a dedicated bucket and *different* S3 credentials. Optional in initial workflow; until set, report `BLOCKED_NOT_CONFIGURED`, not redundant storage success.
- **Tertiary/bulk archive**: user's IDrive Personal 10 TB is an endpoint for its own Linux/desktop backup client, **not** an S3 bucket or a drop-in for IDrive e2. Prefer an encrypted archive copied to a VPS staging directory and included in the IDrive Personal backup set; enable versioning and independent cold restore. Separately consider Backblaze B2 and/or Google Drive as additional failure-domain copies after permissions and real costs are verified. Avoid mirroring every short-lived artifact to every destination by default without a retention/expense policy.
- **Upload**: `backup_encrypted.sh` runs only when the export succeeds AND R2 S3 credentials, account ID, and age recipient are supplied. Upload `evidence.tar.gz.age` to an immutable run/commit path. Download ciphertext from each configured remote and verify byte-for-byte equality; no plaintext is uploaded by this script.
- **Attestation states**: `BLOCKED_NOT_CONFIGURED`, `BLOCKED_EXPORT_FAILED`, `CIPHERTEXT_READBACK_VERIFIED`, `DECRYPT_RESTORE_NOT_TESTED`. GitHub job success with blocked preflight does **not** mean a backup occurred. Provider readback proves ciphertext preservation at that moment, **not** user key recovery, permanence, independent custody, or archive completeness outside the exported run.
- **Cost guard**: per-run source tar limited to 50 MB pending accounting. R2's published Standard free tier is **10 GB-month across the account**, 1 million Class A and 10 million Class B operations monthly; check combined storage usage and billing. IDrive e2 free 10GB is a separate quota. Keep immutable runs, do not silently prune evidence; introduce measured long-term tiering only after real off-provider retention verification.

## One-time configuration (user action required)

1. Generate an `age` identity **offline/on a user-controlled device**. Store its private identity in two distinct secure places; provide only the public `age1...` recipient to GitHub as repository variable `ASES_BACKUP_AGE_RECIPIENT`. **Never** place the private age identity in GitHub Actions, the repository, ChatGPT, Cloudflare, or IDrive e2.
2. In Cloudflare R2, create a dedicated **Object Read & Write** S3 API token scoped **only** to bucket `ases-assurance-evidence`; keep secret and access key in GitHub Actions secrets `ASES_R2_ACCESS_KEY_ID` and `ASES_R2_SECRET_ACCESS_KEY`. Store non-secret account ID in GitHub Actions variable `ASES_R2_ACCOUNT_ID`. Do not use a global account token; do not expose R2 publicly.
3. For IDrive e2 secondary mirror, create its own private bucket and limited access key. Store `ASES_E2_ACCESS_KEY_ID`, `ASES_E2_SECRET_ACCESS_KEY` as secrets, and `ASES_E2_ENDPOINT`, `ASES_E2_BUCKET` as variables. If no secondary credentials are configured, R2 alone may be verified but redundancy remains missing; partial/inconsistent configuration fails.
4. Re-run `Phase I independent replay (experimental)` using `workflow_dispatch` or a new isolated assurance commit. Inspect `Encrypted off-provider backup` job and its JSON attestation. **Do not call backups operational until a real encrypted upload + remote bytewise readback are verified.**
5. From a second independently controlled machine, download a selected ciphertext backup, decrypt using only the offline age identity, verify the tar digest and each embedded SHA256SUMS; record a restore receipt. Then repeat with a known older run to prove historical retention. Confirm both the remote key and offline recipient recovery.
6. Provision IDrive Personal 10 TB Linux/Windows agent separately, enable private encryption in that backup account, include the encrypted evidence staging area, and test restore to a different device. Client ownership and sharing must be arranged with distinct encrypted vaults where necessary.

## Unclosed checks

- Current `encrypted-offprovider-backup` has **not** been proven against live R2/e2 credentials.
- CI has no private decryption key by design, therefore cannot claim genuine decrypt-and-restore verification.
- Existing artifacts created before this backup job remain only in GitHub/one-off exported conversation file until separately ingested. Backfill them explicitly.
- Require periodic independent inventory (source run IDs vs R2/e2 listing) and missing-object alerts, restore tests, cost metrics, and retention governance. Measure service outages and runner scheduling delays; never treat scheduled cadence as guaranteed.
- This backup workflow concerns the experimental assurance artifacts only. Extend later to GitHub mirrors + issues/PR/Actions, Cloudflare D1/Workers data, VPS state/logs, and confidential project files with separate scopes and least privilege.
