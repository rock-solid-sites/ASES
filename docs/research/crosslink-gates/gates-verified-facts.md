---
title: "Evidence-Based Gates — Verified Facts (Source Synthesis)"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard
  - evidence-based-gates.md

related_documents:
  - evidence-based-gates.md
  - gates-issues.md
  - updated-evidence-based-gates.md

consumed_by:
  - Crosslink implementation

supersedes: []

superseded_by:
  - updated-evidence-based-gates.md
  - Crosslink implementation issues #13, #22-#27

last_updated: 2026-08-10
---

# Evidence-Based Gates — Verified Facts (Source Synthesis)

**Purpose:** Replace open questions and speculation in `evidence-based-gates.md`
(DRAFT) and `gates-issues.md` with concrete, code-verified facts about Crosslink
`0.9.0-beta.1`. Facts below were established by reading the actual source, not by
inferring from the design doc.

**Source:** `/home/claude-code/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/crosslink-0.9.0-beta.1/`
(binary: `crosslink 0.9.0-beta.1` at `/home/claude-code/.cargo/bin/crosslink`).
**Date verified:** 2026-07-13.

---

## 1. Corrections to the design's premises

- **Design §1 premise is false.** The design opens with the assumption that
  signature enforcement is currently **active/enforced**. Reality: the config key
  `signing_enforcement` (`"n"` in `config_registry.rs`) takes `disabled | audit |
  enforced` and **defaults to `audit`**. This repo (ASES) runs **`audit`**, not
  `enforced`. There is therefore no pre-existing "enforced" state to be
  *compatible* with. The migration risk (GATE-1.x) is overstated: the real danger
  is new strict defaults blocking legitimate unsigned bootstrap commits.
- **Design §3.1 mislabels `trust_model.rs`.** `src/trust_model.rs` implements
  *finding-triage* (`TrustConfig`, `IgnoreRules`, `BoundaryConfig`) for the agent
  review pipeline — it has **nothing to do with signature verification**. It must
  not be cited as a signature-verification primitive.
- **Design assumes a "canonical JSON envelope."** Crosslink does **not**
  canonicalize JSON. `signing.rs` produces a canonical form as **sorted
  `key=value\n` pairs** fed to `ssh-keygen -Y verify` (SSH-native), plus git
  commit signing (`git -S`) and detached entry signing. Any gate requiring
  RFC 8785 / JCS JSON normalization is a **new** requirement, not existing.

---

## 2. Verified status of the §3.1 gap table (T-1 … T-8)

| Design item | Claimed missing | Actually in code | Evidence |
|---|---|---|---|
| T-1 Hub commit signature verification | missing | **exists** | `signing.rs` `SignatureVerification{Valid,Unsigned,Invalid,NoCommits}`, `verify_content` → `ssh-keygen -Y verify`; `sync/trust.rs:427` `verify_recent_commits` |
| T-2 Lock-commit signature verification | missing | **exists (display only)** | `sync/trust.rs` `verify_locks_signature`; called by `dashboard/reader.rs:362` → `SignatureState` (reporting, **not** an enforcement gate in `sync`) |
| T-3 Role-aware signing for agents | missing | **exists** | `identity.rs` `AgentRole{Driver,Agent}`; `agent init --role driver\|agent` (#718); `agent.rs` signs with its own key, driver with its registered key |
| T-4 Trust approver identity | missing | **exists** | `commands/trust.rs::approve` records `approved_by` driver fingerprint via `resolve_driver_fingerprint`; principal stored; auto-populates `allowed_signers` |
| T-5 Bootstrap completion / cutover | missing | **exists** | `sync/bootstrap.rs::complete_bootstrap` called on **first** `trust approve`; `bootstrap.status` (`pending` → `complete`) |
| T-6 `allowed_signers` auto-population | missing | **exists** | driver/agent public keys self-register into `trust/allowed_signers`; comment field already used (`crosslink-agent:<id>@host`) |
| T-7 Canonical JSON serialization | missing | **does NOT exist**; SSH-native sorted `key=value\n` only | `signing.rs` canonicalization; nothing JSON/JCS |
| T-8 Clock-skew tolerance | missing | **exists** | `clock_skew.rs`, `SKEW_THRESHOLD_SECS = 60`; detects `|event_ts − commit_ts| > 60` using git commit timestamps as independent witness |

**Conclusion:** 7 of 8 "gaps" are already implemented. The design should be
rewritten as "activate/wire existing primitives" rather than "build from scratch."

---

## 3. Genuine remaining gaps (where new work is required)

1. **Enforcement wiring into the local CLI path.** `signing_enforcement` is
   **only** read/validated in the *server* layer (`server/types.rs`,
   `server/handlers/config.rs`). A grep of `sync/mod.rs`, `commands/sync.rs`,
   `commands/kickoff.rs`, `commands/swarm/*.rs` found **zero** references to
   `signing_enforcement`, `SignatureVerification::Invalid`, `verify_locks*`, or
   `verify_recent*`. For ASES's local (non-server) workflow there is effectively
   **no signature enforcement gate today**. Moving to `enforced` requires plumbing
   the check into the local command paths so an `Invalid` result fails the op.
2. **Runtime event-signature verification.** `events.rs` has `EventEnvelope`
   `{agent_id, agent_seq, timestamp, event, signed_by, signature}` plus
   `sign_event` / `verify_event_signature`, but `verify_event_signature` has **no
   non-test caller**. Event audit signatures are produced but never verified at
   runtime — a real gap if gates depend on tamper-evident audit trails.
3. **JSON canonicalization (if required).** If any gate compares/gates on a
   canonical JSON body, that serialization layer does not exist and must be added
   (RFC 8785 / JCS), separate from the SSH-native canonicalization already used.

---

## 4. Reconciliation with `gates-issues.md`

- **GATE-1.x (Migration / Compatibility):** The "existing enforced state" framing
  is wrong — there is no enforced state. Reframe as: *activating enforcement in the
  local CLI path without breaking unsigned bootstrap commits*. The
  `bootstrap.status` + first-`trust approve` cutover already handles the
  bootstrap-pending risk the design worried about (GAP-3.1-1); keep it, don't
  reinvent.
- **GATE-2.x (Valid Evidence per Role):** Role distinction already exists
  (`AgentRole`, `agent init --role`). What is missing is *enforcing* that only the
  declared role's key may sign a given artifact type, and *verifying* the
  `EventEnvelope` signature. The role→key binding is already materialized in
  `allowed_signers` comments (`crosslink-agent:<id>@host`) and `.crosslink/agent.json`.
- **BYPASS tests (reviewer consensus):** Keep — they must assert the current
  `audit` behaviour (no failure on unsigned) so the enforcement-wiring change is
  provably the thing that flips behaviour.
- **Descope from design:** `integrity sign-backfill` already exists; HSM/KMS and a
  `dry-run --report` are not prerequisites for the core gates and should be
  deferred.

---

## 5. Note on reviewer provenance

Subagent reviews (deepseek-flash, nemotron-verifier, gemini-pro-reviewer) on the
*scope-implementation* question correctly flagged the **dependency-broken §6
phasing** (driver-init before cutover) and recommended a Phase-0 foundation plus
TDD BYPASS tests. Those process recommendations stand. Their *factual* claims
about missing primitives are superseded by the source findings in §2 above: most
primitives exist; the work is wiring + activation, not construction.

---

## 6. Citations (file:line)

- `src/signing.rs` — `AllowedSigners`, `SignatureVerification`, `verify_content`, canonicalization
- `src/events.rs` — `EventEnvelope`, `verify_event_signature` (no callers)
- `src/sync/trust.rs:427` — `verify_recent_commits` / `verify_locks_signature` shared impl
- `src/sync/bootstrap.rs:55` — `complete_bootstrap` (called by `trust approve`)
- `src/commands/trust.rs:42,102` — `approve`, `resolve_driver_fingerprint`, `complete_bootstrap`
- `src/identity.rs:21` — `AgentRole{Driver,Agent}`
- `src/clock_skew.rs` — `SKEW_THRESHOLD_SECS = 60`, git-timestamp witness
- `src/server/types.rs`, `src/server/handlers/config.rs` — `signing_enforcement` read (server only)
- `src/commands/config_registry.rs` — `("n","enforced"|"disabled"|"audit")`, default `audit`
- `src/dashboard/reader.rs:362` — `verify_locks_signature` → `SignatureState` (display only)
