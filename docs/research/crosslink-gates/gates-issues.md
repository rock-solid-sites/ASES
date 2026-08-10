---
title: "Evidence-Based Gates — Implementation Issues (Revised)"
program: EDASES
layer: Research
document_type: Research Record
status: Archived
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard
  - evidence-based-gates.md
  - gates-verified-facts.md

related_documents:
  - evidence-based-gates.md
  - gates-verified-facts.md
  - updated-evidence-based-gates.md

consumed_by:
  - Crosslink implementation

supersedes: []

superseded_by:
  - updated-evidence-based-gates.md
  - Crosslink implementation issues #13, #22-#27

last_updated: 2026-08-10
---

# Evidence-Based Gates — Implementation Issues (Revised)

**Basis:** `evidence-based-gates.md` (DRAFT design) + `gates-verified-facts.md` (source-verified,
crosslink 0.9.0-beta.1) + v2 scoping passes (deepseek-flash, nemotron-verifier — 2026-07-13).

**Key correction up front:** The design's §1 premise (repos run `signing_enforcement: enforced`
with unsigned history) is **false** — the value defaults to `audit`, and ASES runs `audit`. No
pre-existing enforced state exists. The §3.1 gap table overstates gaps: **7 of 8 claimed primitives
already exist in code.** The real work is *wiring/activation*, not construction.

Verdict tags: ✅ valid · 🔄 reframe · ❌ descope.

---

## Section 1 — Migration & Compatibility

- **GATE-1.1 — Cutover record (`trust/cutover.json`)** — ❌ **descope (MVP)**
  - `bootstrap.status` (`sync/bootstrap.rs:18-25`, flips `pending→complete` on first `trust approve`,
    `sync/bootstrap.rs:55-64`) already provides bootstrap-aware enforcement gating. A second
    `cutover.json` duplicates this. Revisit only if explicit grandfather-policy fields are later needed
    (add them to `bootstrap.json`, not a new file).
  - *Original design text (lines 7–11) is superseded.*

- **GATE-1.2 — Enforcement guard (missing-cutover → audit)** — 🔄 **reframe → merge into Phase 1**
  - Underlying need ("don't reject unsigned bootstrap commits") is already handled by `bootstrap.status`.
    Phase 1 enforcement wiring must check `bootstrap.state == "complete"` before rejecting — already built.
  - Keep the **loud stderr + audit warning** requirement; it's cheap and valuable.
  - No longer the single highest-risk item (enforcement *wiring* is). Keep property/fuzz test on the
    bootstrap/timestamp boundary.

- **GATE-1.3 — Backfill / re-signing** — ❌ **descope**
  - `crosslink integrity sign-backfill` already exists (verified). Not a prerequisite for any gate.
  - *Original design text (lines 19–22) is superseded.*

- **GATE-1.4 — Dry-run / warn mode** — 🔄 **reframe → keep as Phase 1 dependency**
  - `signing_enforcement` enum (`config_registry.rs:108`) is `disabled | audit | enforced`. Adding a
    `dry-run` variant is a <10-line change and gives a non-rejecting test mode before flipping to
    `enforced`. Keep `crosslink sync --dry-run-report report.json` as deferrable.

- **GATE-1.5 — Driver key retrofit (`crosslink trust driver-init`)** — ✅ **valid, simplify impl**
  - Design wrongly assumes a dedicated `crosslink-driver` OS user as the sole mechanism. Add
    `crosslink trust driver-init [--key-dir <path>]`; default to OS-user path, `--key-dir` overrides for
    CI (CI cannot `useradd` without root — the original `--user-dir` fallback note is correct and
    required). `key_dir` pattern already exists (`signing.rs:88`). Missing-driver-key guard on `--force`
    / `trust cutover` stays.

---

## Section 2 — Valid Evidence per Role

- **GATE-2.1 — Evidence artifacts per role** — 🔄 **reframe (defer fine-grained roles)**
  - Code has only `AgentRole::{Driver,Agent}` (`identity.rs:19-25`), not Builder/Reviewer/Auditor.
    For MVP: `AgentRole::Agent` signs all agent-produced events; `AgentRole::Driver` signs overrides +
    cutover. Extend `AgentRole` only when a concrete workflow needs per-role distinction.

- **GATE-2.2 — Evidence non-repudiation** — 🔄 **reframe (largely exists)**
  - `sign_event()` (`events.rs:488-498`) and `verify_event_signature()` (`events.rs:505-522`) already
    implement the signed NDJSON envelope. The **single real gap: `verify_event_signature` has no
    non-test caller** — wire it into the sync event-replay path and kickoff/swarm completion checks
    (Phase 2 below).
  - Canonicalization concern is a **red herring**: `canonicalize_event()` (`events.rs:473-480`) feeds
    `signing::canonicalize_for_signing()` → sorted `key=value\n` (`signing.rs:683-698`), NOT JSON
    objects. No RFC 8785/JCS needed for the current mechanism.

- **GATE-2.3 — Orchestrator assertions are not evidence** — ✅ **valid, implicit under simplified roles**
  - If role model stays `Driver`/`Agent`, "orchestrator" is just an `AgentRole::Agent`; the gate checks
    "is the signer the expected agent?" No separate mechanism needed for MVP.

- **GATE-2.4 — `allowed_signers` role field** — 🔄 **reframe → use principal encoding**
  - `AllowedSignerEntry` (`signing.rs:498-508`) has no `role` field, but the parser at `signing.rs:542-604`
    is **hand-parsed** (`splitn(2,' ')`), NOT `ssh-keygen -Y verify` — so a trailing/encoded field is
    safe. **Recommendation: principal encoding `role+agent_id@crosslink`** (e.g. `builder+agent-7@crosslink`)
    rather than a new struct field. Parse `principal.split('+')` for role when needed. Avoids breaking
    `ssh-keygen -Y verify` compatibility and keeps `AllowedSignerEntry` unchanged.

---

## The three genuine gaps (what actually must be built)

1. **Enforcement wiring into the local CLI path** — *HIGH.* `signing_enforcement` is read only in the
   server layer (`server/types.rs`, `server/handlers/config.rs`). `commands/sync.rs`,
   `commands/kickoff/run.rs`, `commands/swarm/*` contain **zero** references to it. Plumb it through and
   make `SignatureVerification::Invalid` (from `sync/trust.rs:429`) a hard failure in `enforced` mode.
   Prefer a thin per-command adapter over a new monolithic `VerificationService`.
2. **Runtime event-signature verification** — *HIGH.* `verify_event_signature()` (`events.rs:505-522`)
   is correct but uncalled. Call it from the sync event-replay path and gate-like consumers.
3. **Role→key binding (principal encoding)** — *MEDIUM.* Encode role in the `allowed_signers` principal
   (`role+agent_id@crosslink`); enforce that only the declared role's key may sign a given artifact type.

*(JSON/RFC 8785 canonicalization: NOT needed — crosslink uses SSH-native `key=value\n`. HSM/TPM: future
upgrade path, not required.)*

---

## Corrected implementation phasing (dependency-ordered)

| Phase | Deliverable | Depends on |
|---|---|---|
| **0** | TDD BYPASS tests (§5.1's ~15 scenarios) asserting current `audit` behaviour (unsigned accepted) | — |
| **1** | Plumb `signing_enforcement` into local `sync`/`kickoff`/`swarm`; add `dry-run` enum variant; respect `bootstrap.status` | Phase 0 |
| **2** | Wire `verify_event_signature()` into sync event-replay + kickoff/swarm completion | Phase 1 |
| **3** | `crosslink trust driver-init [--key-dir]` + `--force` guard + override audit log | Phase 2 |
| **4** | Reconcile `bootstrap.status` vs `cutover.json` (descope the latter; extend `bootstrap.json` only if needed) | Phase 3 |
| **5** | `crosslink status --audit-violations` / `--override-audit` reporting | Phase 3 |

Effort estimate: ~300 LOC enforcement wiring + ~150 LOC event-sig call sites. **Not** a new service module.

---

## Corrections to apply to `evidence-based-gates.md`

- §1: replace the "currently enforced" premise with "defaults to `audit`; no enforced state exists."
- §3.1 gap table: mark 7/8 as already-implemented (cite `gates-verified-facts.md` §2).
- §6: replace the dependency-broken phasing (driver-init before cutover) with the table above.
- §7 Q3 (JSON canonicalization): note crosslink uses sorted `key=value\n`; JCS not required.
- GATE-2.4: adopt principal encoding instead of a struct field.
