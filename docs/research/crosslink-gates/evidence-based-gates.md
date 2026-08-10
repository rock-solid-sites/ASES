---
title: "Evidence-Based Workflow Gates in Crosslink — Design Document"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Experimental
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - gates-verified-facts.md
  - gates-issues.md
  - updated-evidence-based-gates.md
  - server-crash-postmortem.md

consumed_by:
  - Crosslink implementation

supersedes: []

superseded_by:
  - updated-evidence-based-gates.md
  - Crosslink implementation issues #13, #22-#27

last_updated: 2026-08-10
---

# Design Document: Evidence-Based Workflow Gates in Crosslink

**Status**: DRAFT — for review before implementation scoping  
**Affected repos**: All repos using shared `crosslink` binary (cross-repo blast radius: HIGH)  
**Author**: Orchestrator (TripN monorepo)  
**Date**: 2026-07-12

---

## Changelog (This Revision)

- **§1.2 / §4.1 / §5.1-5.2 / §7 Q5**: Resolved Gap 1 — Retrofit path for driver key on existing repos. Added `crosslink trust driver-init`, missing-driver-key enforcement guard symmetric with missing-cutover, BYPASS-014.
- **§3.2 / §4.1 / §5.1-5.2 / §7 Q5**: Resolved Gap 2 — Driver key storage mechanism **committed to dedicated OS user account** (`crosslink-driver`) as the sole mechanism for this deployment. HSM/TPM documented as a future upgrade path (§7 Q5, §1.5). Removed "agents lack filesystem access" assumption. Updated BYPASS-013 to reflect verified mechanism.
- **§5.1 / §5.2**: Added BYPASS-014 (driver key missing → --force denied) and updated BYPASS-013.
- **§1.1 / §4.1 / §5.1-5.2**: Resolved Gap 3 — `crosslink trust cutover` now requires driver key signature (same mechanism as `--force`). Added BYPASS-015 (cutover without driver key → denied). Added `DriverInitiateCutover` gate to §4.1 matrix.
- **§7 Q5**: Confirmed no HSM/TPM on this server (verified against TOOLING.md §14 and `server/fortified-server-architecture.md`). Committed to dedicated OS user mechanism.
- **§7 Q6**: Confirmed new OS user (`crosslink-driver`) does not conflict with server security posture (firewall/Tailscale/aaPanel). Documented rationale.

---

## 1. Migration and Compatibility — Mandatory First

### Problem
Repos currently running `signing_enforcement: "enforced"` (including this TripN repo) have **unsigned history** on `crosslink/hub` and `crosslink/knowledge` branches. The moment any gate starts reading `signing_enforcement` and enforcing it, sync/swarm/kickoff will reject all prior commits — breaking the repo immediately.

### Solution: Grandfathering with Explicit Cutover + Enforcement Guard

**Core principle**: Enforcement applies **only to commits created after a recorded cutover timestamp**. Pre-cutover commits are accepted with a warning (audit mode) or silently (enforced mode), never rejected.

**Guard rule (mandatory, not advisory)**: When `signing_enforcement == "enforced"` **and** `trust/cutover.json` does not exist, gates **must not** enforce. Instead they:
1. Emit a **loud, unmissable warning** (stderr + audit log) on every gate invocation
2. Operate in **effective audit mode** for that invocation (violations logged, nothing rejected)
3. Block hard enforcement until `crosslink trust cutover` is run and cutover record exists

This is an **active state check** at every gate — not operator discipline, not a migration recommendation.

**Additional guard rule (driver key retrofit)**: When `--force` is invoked but `trust/keys/driver.pub` does not exist (repo initialized before this design), `--force` is **unconditionally denied** — same pattern as missing cutover. Driver must run `crosslink trust driver-init` first.

#### 1.1 Cutover Record
- Add a new file on `crosslink/hub`: `trust/cutover.json`
- Schema:
```json
{
  "cutover_timestamp": "2026-07-12T19:00:00Z",
  "cutover_commit": "abc123def456...",
  "enforcement_mode_at_cutover": "enforced",
  "grandfather_policy": "warn" | "silent"
}
```
- Written by driver via `crosslink trust cutover --mode enforced --grandfather warn`
  - **Driver key check**: `trust cutover` requires the driver to sign the cutover request with the driver Ed25519 key (stored in dedicated OS user account — see §7 Q5). Without a valid driver signature, the cutover command is denied (BYPASS-015).
- Immutable once written (append-only; new cutover entries allowed but never removed)

#### 1.2 Verification Logic
For any commit being verified:
```
if no cutover.json exists AND config.enforcement == "enforced":
    return ENFORCEMENT_BLOCKED_MISSING_CUTOVER  // drops to audit with warning
elif commit.timestamp < cutover_timestamp:
    return ACCEPT_GRANDFATHERED  // with warning in audit mode
else:
    return VERIFY_SIGNATURE_NORMALLY
```

#### 1.3 Backfill/Re-signing Process (Optional, Driver-Initiated)
- `crosslink integrity sign-backfill --since <commit> --as <agent-id>` — creates signed attestation entries for historical commits
- Does **not** rewrite git history (preserves SHA integrity)
- Attestations stored as signed `CommentEntry` on hub with `kind: "attestation"` linking to original commit
- Allows repos to clean up audit warnings without force-pushing

#### 1.4 Dry-Run / Warn Mode Before Hard Enforcement
- New config value: `signing_enforcement: "disabled" | "audit" | "enforced" | "dry-run"`
- `"dry-run"`: All verification logic runs, violations logged verbosely, **no commits rejected**, exits 0
- Recommended migration path for **new adopters**: `disabled` → `audit` → `dry-run` (2 weeks) → `enforced`
- `dry-run` mode produces machine-parseable JSON report: `crosslink sync --dry-run-report report.json`

**This repo's migration path justification**: Direct cutover from `enforced` + unsigned history → `crosslink trust cutover` is safe because **no verification was previously running** — nothing was being rejected, so there is no latent rejection that a staged rollout would surface. The first enforcement attempt is the cutover itself; if it fails, the guard in §1.2 prevents silent history rejection. Other repos with partial/working verification should follow the staged path.

#### 1.5 Driver Key Retrofit for Existing Repos
- New command: `crosslink trust driver-init` — generates Ed25519 driver key pair, stores private key in the **dedicated `crosslink-driver` OS user's home directory** (`~crosslink-driver/.crosslink/keys/driver`), writes public key to `trust/keys/driver.pub` on hub
- **Why a dedicated OS user**: This server has no HSM or TPM (confirmed against TOOLING.md §14 infrastructure inventory and `server/fortified-server-architecture.md`). A separate OS user provides the strongest available isolation: filesystem permissions (`0700` on `~crosslink-driver/.crosslink/`) deny the `claude-code` user (and all agent processes) any access to the private key. This is the chosen mechanism for this deployment.
- **Future upgrade path**: HSM/TPM hardware could replace the OS-user mechanism, providing hardware-bound key protection. The `driver-init` command's interface (key generation + pubkey registration) is designed to accept a `--hsm` flag in the future without changing the rest of the trust model.
- Required for **any repo initialized before this design** (no `trust/keys/driver.pub` exists)
- Without driver key present, `--force` is denied at every gate (see §4.1 matrix)
- Without driver key present, `crosslink trust cutover` is also denied (see §4.1 matrix, BYPASS-015)
- One-time setup; idempotent (re-running validates existing key)
- **Server security posture compatibility**: Verified against `server/fortified-server-architecture.md`. The `crosslink-driver` user is a local-only account with no login shell, no sudo, no Tailscale access, and no services bound. It does not create new attack surface — the existing firewall (aaPanel, ports 80/443 public, all else Tailscale-only) covers it. Adding a user is a standard Linux operation that does not interact with aaPanel, Tailscale, or the firewall rule set.

---

## 2. Valid Evidence per Role

Evidence must be **cryptographically bound to the agent identity** that produced it — not merely asserted by the Orchestrator.

### 2.1 Evidence Types

| Role | Evidence Artifact | Verification Method |
|------|-------------------|---------------------|
| **Builder** | Signed `TaskCompleted` event + signed commit(s) on feature branch | 1. Commit signed by agent's SSH key (in `allowed_signers` with `role: "builder"`)<br>2. `TaskCompleted` event signed by same key, contains `issue_id`, `branch`, `commit_sha`<br>3. Branch merged to main via PR (driver merge) |
| **Reviewer** | Signed `ReviewCompleted` event + signed review comment on issue | 1. `ReviewCompleted` event signed by reviewer agent key (`role: "reviewer"`)<br>2. Contains `issue_id`, `verdict` (PASS/CHANGES_REQUESTED), `findings_hash`<br>3. Review comment posted to issue via `crosslink issue comment` (signed entry on hub) |
| **Auditor** | Signed `AuditCompleted` event + signed audit comment on issue | 1. `AuditCompleted` event signed by auditor agent key (`role: "auditor"`)<br>2. Contains `issue_id`, `verdict` (PASS/CONDITIONAL_PASS/FAIL), `findings_hash`<br>2. Audit comment posted to issue (signed entry on hub) |

### 2.2 Evidence Non-Repudiation
- All evidence events are **NDJSON entries** in agent's `events.log` (append-only, on hub branch)
- Each entry: `{ type, timestamp, agent_id, payload, signature, signer_fingerprint }`
- `signature` = Ed25519 detached signature of canonicalized `payload`
- `signer_fingerprint` = SHA256 of agent's public key (matches `allowed_signers` entry)
- Driver can verify any evidence offline: `crosslink verify evidence <event-file>`

### 2.3 Orchestrator Assertions Are Not Evidence
- Orchestrator comments on issues (`kind: "decision"`, `kind: "plan"`) are **not** evidence of Reviewer/Auditor completion
- Gates **must not** accept Orchestrator identity as proof of specialist work
- Violation = gate bypass (see §5)

---

## 3. Single Verification API

### 3.1 Current Gap Analysis (Known Integration Points)

| File | Current State | Gap |
|------|---------------|-----|
| `src/sync/trust.rs` | `verify_locks_signature()` checks commit signatures only | No per-entry verification; no role-aware checks |
| `src/commands/swarm/lifecycle.rs` | Swarm phase transitions check lock ownership | No signature verification on phase completion events |
| `src/commands/swarm/review.rs` | Review gate checks for review comments | Accepts any comment; no author identity verification |
| `src/commands/kickoff/run.rs` | Kickoff completion checks for `TaskCompleted` event | No signature verification on event |
| `src/trust_model.rs` | Defines `TrustLevel`, `SignatureVerification` | Not used by any gate; only by `trust check` CLI |

### 3.2 Proposed API: `VerificationService`

```rust
// src/verification/service.rs
pub struct VerificationService {
    keyring: Keyring,           // loads trust/allowed_signers (with role field)
    cutover: Option<Cutover>,   // loads trust/cutover.json
    config: EnforcementConfig,  // disabled | audit | dry-run | enforced
    driver_key: Option<PublicKey>, // driver-only key for --force auth (hardware-bound)
}

impl VerificationService {
    /// Verify a single commit on hub/knowledge branch
    pub fn verify_commit(&self, commit: &Commit) -> VerificationResult;

    /// Verify a single NDJSON event entry (comment, lock, completion, etc.)
    pub fn verify_event(&self, event: &EventEntry) -> VerificationResult;

    /// Verify role-specific completion evidence — checks signer role matches expected_role
    pub fn verify_builder_completion(&self, issue_id: u64, branch: &str) -> RoleVerification;
    pub fn verify_reviewer_completion(&self, issue_id: u64) -> RoleVerification;
    pub fn verify_auditor_completion(&self, issue_id: u64) -> RoleVerification;

    /// Composite gate check — used by all workflow transitions
    pub fn check_gate(&self, gate: GateType, context: GateContext) -> GateResult;

    /// Emergency override — requires driver key signature, produces immutable audit entry
    pub fn emergency_override(&self, gate: GateType, driver_sig: &Signature) -> OverrideResult;
}

pub enum AgentRole { Builder, Reviewer, Auditor, Orchestrator, Driver }

pub enum GateType {
    SyncAcceptCommit,
    SwarmPhaseTransition { from: Phase, to: Phase },
    SwarmReviewGate,
    SwarmCheckpoint,
    KickoffCompletion,
    TrustApprove,
    DriverInitiateCutover,
}

pub struct GateContext {
    pub commit: Option<Commit>,
    pub event: Option<EventEntry>,
    pub issue_id: Option<u64>,
    pub expected_role: Option<AgentRole>, // Builder | Reviewer | Auditor
    pub agent_id: Option<String>,         // expected agent identity
}

pub enum GateResult {
    Allow,
    AllowWithWarning(String),   // audit/dry-run: violation logged but allowed
    Deny(String),               // enforced: hard block with reason
    EnforcementBlockedMissingCutover, // enforced config but no cutover.json
    EnforcementBlockedMissingDriverKey, // --force invoked but no driver key
}
```

### 3.3 Integration Points (Replace Ad-Hoc Checks)

| Gate | Calls | Replaces |
|------|-------|----------|
| `sync` commit acceptance | `verify_commit()` + `check_gate(SyncAcceptCommit, ...)` | `verify_locks_signature()` in `trust.rs` |
| Swarm phase transition | `check_gate(SwarmPhaseTransition, ...)` | Manual lock check in `lifecycle.rs` |
| Swarm review gate | `verify_reviewer_completion()` + `check_gate(SwarmReviewGate, ...)` | Comment existence check in `review.rs` |
| Swarm checkpoint | `check_gate(SwarmCheckpoint, ...)` | No verification currently |
| Kickoff completion | `verify_builder_completion()` + `check_gate(KickoffCompletion, ...)` | Event existence check in `run.rs` |
| `trust approve` | `check_gate(TrustApprove, ...)` | Manual keyring update |
| `trust cutover` | `check_gate(DriverInitiateCutover, ...)` | No verification currently (new gate) |

---

## 4. Workflow Transitions and Enforcement Modes

### 4.1 Gate Behavior Matrix

| Gate | `disabled` | `audit` | `dry-run` | `enforced` (cutover exists) | `enforced` (NO cutover) | `enforced` (NO driver key) |
|------|------------|---------|-----------|----------------------------|-------------------------|---------------------------|
| **Sync accept commit** | Accept all | Accept all, warn on unsigned/untrusted | Accept all, verbose JSON report on violations | Reject unsigned/untrusted; accept grandfathered | **Drop to audit + loud warning; do not reject** | N/A (no --force here) |
| **Swarm phase transition** | Allow | Allow, warn if prior phase evidence invalid | Allow, report missing/invalid evidence | Block if prior phase evidence missing/invalid | **Drop to audit + loud warning** | N/A |
| **Swarm review gate** | Allow | Allow, warn if reviewer evidence invalid/missing | Allow, report reviewer evidence status | Block unless valid `ReviewCompleted` from trusted Reviewer | **Drop to audit + loud warning** | N/A |
| **Swarm checkpoint** | Allow | Allow, warn if checkpoint evidence invalid | Allow, report checkpoint evidence status | Block unless valid checkpoint evidence from expected role | **Drop to audit + loud warning** | N/A |
| **Kickoff completion** | Allow | Allow, warn if builder evidence invalid | Allow, report builder evidence status | Block unless valid `TaskCompleted` from trusted Builder | **Drop to audit + loud warning** | N/A |
| **Trust approve** | Allow | Allow, warn if key already trusted/revoked | Allow, report key status | Block if key not in `trust/keys/` or already trusted | **Drop to audit + loud warning** | N/A |
| **Emergency override (--force)** | N/A | N/A | N/A | **Requires driver key; produces override audit entry** | **Deny: missing cutover** | **Deny: missing driver key** |
| **Driver initiate cutover (trust cutover)** | N/A | N/A | N/A | **Requires driver key; produces immutable cutover record** | N/A (no cutover = no enforcement) | **Deny: missing driver key** |

**Loud warning** = stderr line `WARNING: signing_enforcement=enforced but trust/cutover.json missing — enforcement suspended, operating in audit mode. Run 'crosslink trust cutover' to enable.` + structured audit log entry.

**Driver key missing warning** = stderr line `ERROR: --force requires driver key; trust/keys/driver.pub not found. Run 'crosslink trust driver-init' to initialize.` + structured audit log entry.

### 4.2 Audit Mode Semantics (Transitional Mode)
- **Purpose**: Repos migrate through `audit` to observe violations before hard enforcement
- **Behavior**: Every gate runs full verification; violations produce structured log entries:
  ```json
  {
    "gate": "SwarmReviewGate",
    "issue_id": 295,
    "expected_role": "Reviewer",
    "actual_signer": "orchestrator-4Adb",
    "violation": "Reviewer completion claimed by non-Reviewer identity",
    "severity": "HIGH",
    "timestamp": "2026-07-12T19:15:00Z"
  }
  ```
- Log destination: `~/.crosslink/audit-violations.log` (rotating, machine-parseable)
- `crosslink sync` / `crosslink swarm` exit 0 always in audit mode
- `crosslink status --audit-violations` shows summary

### 4.3 Enforced Mode Semantics
- **Behavior**: Gates return `Deny(reason)` on any verification failure
- **Error messages** must be actionable:
  - "Commit abc123 not signed by trusted key (expected: reviewer-agent-7, got: orchestrator-4Adb)"
  - "Review gate requires valid ReviewCompleted event from trusted Reviewer; none found for issue #295"
  - "Kickoff completion rejected: TaskCompleted event signature invalid (key not in allowed_signers)"
- **No silent failures**: Every denial includes the specific evidence that was missing/invalid

### 4.4 Cross-Repo Blast Radius Flags

| Area | Blast Radius | Mitigation |
|------|--------------|------------|
| `signing_enforcement` config default change | HIGH — all repos | Default remains `audit`; `enforced` opt-in only |
| `VerificationService` API | HIGH — all gates | Single internal module; gates call via trait, not direct |
| `trust/cutover.json` format | MEDIUM — repos with existing hub | Optional file; absent = enforcement blocked (safe default) |
| Event schema changes | MEDIUM — repos with event consumers | New fields optional; old parsers ignore unknown fields |
| CLI output changes | LOW | Machine-readable flags (`--json`) unchanged |

---

## 5. Regression Test Suite Requirements

### 5.1 Bypass Scenarios to Assert (Not "Add Tests" — Define Exact Scenarios)

| Scenario ID | Description | Expected Behavior in `enforced` |
|-------------|-------------|----------------------------------|
| **BYPASS-001** | Orchestrator fabricates a comment on issue #N claiming "Review complete — PASS" using its own identity | Gate denies: comment author ≠ trusted Reviewer agent |
| **BYPASS-002** | Orchestrator creates fake `ReviewCompleted` event in its own events.log, signs with Orchestrator key | Gate denies: event signer ≠ Reviewer role key in `allowed_signers` |
| **BYPASS-003** | Replay old valid `ReviewCompleted` event from issue #100 onto issue #200 | Gate denies: event payload `issue_id` mismatch |
| **BYPASS-004** | Unsigned commit pushed to `crosslink/hub` (no `-S` flag) | Gate denies: commit lacks signature |
| **BYPASS-005** | Commit signed by key NOT in `trust/allowed_signers` (unapproved agent) | Gate denies: signer untrusted |
| **BYPASS-006** | Commit signed by revoked key (key moved to `.revoked`) | Gate denies: signer revoked |
| **BYPASS-007** | Swarm phase transition from `Implementation` → `Review` without valid `TaskCompleted` from Builder | Gate denies: missing builder evidence |
| **BYPASS-008** | Kickoff agent writes `TaskCompleted` but never pushes code; branch empty | Gate denies: commit SHA in event doesn't exist on branch |
| **BYPASS-009** | `crosslink sync` accepts commit from pre-cutover era without grandfathering check | Gate denies if cutover exists and commit is post-cutover unsigned |
| **BYPASS-010** | Driver runs `crosslink trust approve` for agent whose key not in `trust/keys/` | Gate denies: key file missing |
| **BYPASS-011** | Key legitimately registered and trusted in `allowed_signers`, but with `role: "builder"`; agent uses it to produce `ReviewCompleted` event | Gate denies: signer role (`builder`) ≠ expected role (`reviewer`) |
| **BYPASS-012** | Agent identity (Orchestrator/Builder/Reviewer/Auditor) attempts `crosslink sync --force` without driver key | Gate denies: `--force` requires driver Ed25519 key distinct from all agent roles |
| **BYPASS-013** | Legitimate driver uses `--force` with valid driver key signature | Gate allows override **and** produces immutable audit trail entry in `~/.crosslink/override-audit.log` (hardware-bound, append-only, signed by driver key) with driver fingerprint, timestamp, gate type, reason |
| **BYPASS-014** | `--force` invoked when `trust/keys/driver.pub` does not exist (repo predates driver key) | Gate denies: missing driver key; driver must run `crosslink trust driver-init` first |
| **BYPASS-015** | `crosslink trust cutover` invoked without driver key signature | Gate denies: cutover requires driver key (same mechanism as BYPASS-012/014). Without cutover record, `signing_enforcement == "enforced"` drops to audit mode (enforcement suspended). |

### 5.2 Test Structure
```rust
// tests/verification_gates.rs
mod bypass_scenarios {
    use crate::verification::VerificationService;
    use crate::test_helpers::{setup_repo_with_cutover, make_commit, make_event, sign_with_key, driver_key};

    #[test] fn bypass_001_orchestrator_fakes_review_comment() { ... }
    #[test] fn bypass_002_orchestrator_fakes_review_event() { ... }
    #[test] fn bypass_003_replay_old_review_event() { ... }
    #[test] fn bypass_004_unsigned_commit_rejected() { ... }
    #[test] fn bypass_005_untrusted_key_rejected() { ... }
    #[test] fn bypass_006_revoked_key_rejected() { ... }
    #[test] fn bypass_007_swarm_phase_without_builder_evidence() { ... }
    #[test] fn bypass_008_kickoff_completion_empty_branch() { ... }
    #[test] fn bypass_009_sync_enforces_cutover() { ... }
    #[test] fn bypass_010_trust_approve_missing_key() { ... }
    #[test] fn bypass_011_wrong_role_key_rejected() { ... }
    #[test] fn bypass_012_force_without_driver_key_rejected() { ... }
    #[test] fn bypass_013_force_with_driver_key_logs_immutable() { ... }
    #[test] fn bypass_014_force_without_driver_key_denied() { ... }
    #[test] fn bypass_015_cutover_without_driver_key_denied() { ... }
}
```

### 5.3 CI Enforcement
- All bypass tests **must pass** in `enforced` mode
- Test suite runs in `crosslink` CI on every PR
- `cargo test verification_gates` added to CI matrix
- Failure = PR blocked (no merge without gate integrity proven)

---

## 6. Implementation Phasing (Not Part of Design — For Scoping)

| Phase | Deliverable | Gates Covered |
|-------|-------------|---------------|
| 1 | `VerificationService` core + `trust/cutover.json` + dry-run mode + enforcement guard (missing cutover → audit) | Sync commit acceptance |
| 2 | Role evidence verification (`verify_builder/reviewer/auditor_completion`) + `allowed_signers` role field | Kickoff completion, Swarm review gate |
| 3 | Swarm phase transitions + checkpoints | Swarm lifecycle |
| 4 | `trust approve` gate + audit violation logging + driver key retrofit (`driver-init`) + emergency override + override audit trail | Trust management |
| 5 | Full regression test suite (BYPASS-001 through BYPASS-014) | All gates |

---

## 7. Resolved Questions (Previously Open)

1. **Cutover granularity**: **Single global cutover** for `crosslink/hub` and `crosslink/knowledge` — simpler, matches current single `signing_enforcement` config.
2. **Agent role binding**: **Extend `allowed_signers`** with `role` field per key (format: `key type key fingerprint role agent-id`). Least resistance — `trust_model.rs` already parses `allowed_signers`; adding field preserves git-native format compatibility.
3. **Event payload canonicalization**: **Deterministic JSON** — `serde_json::to_vec(&payload)` with `Serializer::new(Vec::new())` and `sort_keys(true)`. Document exact algorithm in `VERIFICATION.md`.
4. **Clock skew**: Cutover uses **git commit timestamp** as witness. Forged timestamps detectable via `crosslink integrity` clock-skew check (already exists, uses commit graph as witness). No additional mechanism needed.
5. **Driver emergency override**: **Yes, but cryptographically gated with a driver-only Ed25519 key**.
   - `--force` and `crosslink trust cutover` both require a **driver-only Ed25519 key** stored in the **dedicated `crosslink-driver` OS user's home directory** (`~crosslink-driver/.crosslink/keys/driver`, permissions `0700`). The `claude-code` user (and all agent processes) has no access to this directory.
   - **Chosen mechanism**: Dedicated OS user account. This server has no HSM or TPM (verified against TOOLING.md §14 and `server/fortified-server-architecture.md`). A separate OS user provides the strongest available software isolation. HSM/TPM is documented as a future upgrade path.
   - **Mechanism**: `crosslink trust driver-init` generates key and stores it under the `crosslink-driver` user; public key written to `trust/keys/driver.pub` on hub. Private key operations (signing override/cutover requests) require running as the `crosslink-driver` user (e.g., `sudo -u crosslink-driver crosslink trust cutover ...`).
   - Every `--force` and `trust cutover` invocation:
     - Requires valid driver signature on the request payload (signed with the driver key)
     - Produces **immutable** entry in `~crosslink-driver/.crosslink/override-audit.log` (append-only, signed by driver key, includes gate, reason, timestamp, driver fingerprint)
     - Cannot be suppressed or deleted by any agent identity (file owned by `crosslink-driver` user; agents run as `claude-code` and lack write access)
     - `crosslink status --override-audit` shows all overrides; no agent can invoke `--force` or `trust cutover` without driver key (BYPASS-012, BYPASS-015).
   - **BYPASS-013 updated**: "Legitimate driver uses `--force` with valid driver key signature **from driver OS user account**" — gate allows override and produces audit entry as above.
6. **Server security posture compatibility**: Creating the `crosslink-driver` user (local-only, no login shell, no sudo, no Tailscale access, no services bound) does not conflict with the existing security posture. Verified against `server/fortified-server-architecture.md` §"Firewall Configuration" and §"Authentication & Access Workflows". The aaPanel-managed firewall (ports 80/443 public, all else Tailscale-only) is unaffected. A new local user adds no network attack surface.

---

**Next step**: Review this design. On approval, scope implementation phases and delegate to Builder via `crosslink kickoff`.
