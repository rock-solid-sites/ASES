---
title: "Updated Evidence-Based Workflow Gates — Consolidated Overview"
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
  - gates-issues.md

related_documents:
  - evidence-based-gates.md
  - gates-verified-facts.md
  - gates-issues.md

consumed_by:
  - Crosslink implementation

supersedes:
  - evidence-based-gates.md
  - gates-verified-facts.md
  - gates-issues.md

superseded_by:
  - Crosslink implementation issues #13, #22-#27

last_updated: 2026-08-10
---

# Updated Evidence-Based Workflow Gates — Consolidated Overview

**Status:** Synthesis of all work to date (2026-07-13)
**Basis documents:**
- `evidence-based-gates.md` — original DRAFT design
- `gates-verified-facts.md` — source-verified facts (crosslink 0.9.0-beta.1)
- `gates-issues.md` — revised issue list with verdicts
- v2 scoping passes: deepseek-flash + nemotron-verifier (independent, converging)

**Purpose:** A single document capturing everything we currently know about adding
evidence-based workflow gates to Crosslink — what the design intended, what the code
actually does, what is genuinely left to build, and the corrected plan.

---

## 1. Executive summary

The original design proposed building a suite of "evidence-based gates" on top of Crosslink,
premised on the belief that Crosslink currently enforces signatures (`signing_enforcement:
enforced`) over a body of unsigned history, and that most signature/role/trust primitives were
missing. **Both premises are wrong.**

Source verification (crosslink `0.9.0-beta.1`) shows:
- `signing_enforcement` **defaults to `audit`** — there is no pre-existing enforced state to be
  compatible with.
- **7 of the 8 "gaps" in the design's §3.1 table already exist** in code.

The real work is **wiring and activation**, not construction: roughly **~300 LOC** to plumb
enforcement into the local CLI path and **~150 LOC** to call the already-correct event-signature
verifier. The design's monolithic `VerificationService` and `trust/cutover.json` are overengineered
and should be dropped in favour of thin adapters and the existing `bootstrap.status` mechanism.

---

## 2. What Crosslink already does (verified)

| Capability | Status | Evidence |
|---|---|---|
| Hub-commit signature verification | ✅ exists | `signing.rs` `SignatureVerification{Valid,Unsigned,Invalid,NoCommits}`; `verify_content` → `ssh-keygen -Y verify`; `sync/trust.rs:427` `verify_recent_commits` |
| Lock-commit signature verification | ✅ exists (display only) | `sync/trust.rs:458` `verify_locks_signature`; surfaced by `dashboard/reader.rs:362` as `SignatureState` |
| Role-aware agent signing | ✅ exists | `identity.rs:19-25` `AgentRole{Driver,Agent}`; `agent init --role`; agent signs with its own key, driver with its registered key |
| Trust-approver identity | ✅ exists | `commands/trust.rs:85-90` records `approved_by` driver fingerprint; auto-populates `allowed_signers` |
| Bootstrap completion / cutover | ✅ exists | `sync/bootstrap.rs:55-64` `complete_bootstrap` on first `trust approve`; `bootstrap.status` `pending→complete` |
| `allowed_signers` auto-population | ✅ exists | driver/agent keys self-register; comment `crosslink-agent:<id>@host` |
| Canonicalization for signing | ✅ exists (SSH-native) | `signing.rs:683-698` sorted `key=value\n` — **not** JSON |
| Clock-skew tolerance | ✅ exists | `clock_skew.rs:21` `SKEW_THRESHOLD_SECS = 60`, git-timestamp witness |

**Genuinely missing (the three real gaps):**
1. **Enforcement wiring into the local CLI path** (HIGH) — `signing_enforcement` is read only in the
   server layer; `sync`/`kickoff`/`swarm` never consult it.
2. **Runtime event-signature verification** (HIGH) — `verify_event_signature()` (`events.rs:505-522`)
   is correct but has **no non-test caller**.
3. **Role→key binding** (MEDIUM) — encode role in the `allowed_signers` principal rather than adding a
   struct field.

---

## 3. Corrections to the original design

| Original claim | Corrected fact |
|---|---|
| Repos run `enforced` with unsigned history (§1) | Defaults to `audit`; no enforced state exists |
| `trust_model.rs` is a signature primitive (§3.1) | It is *finding-triage* for the agent review pipeline — unrelated to signatures |
| 8 primitives must be built (§3.1) | 7 already exist; only the 3 gaps above are real |
| Need monolithic `VerificationService` (§6) | Thin per-command adapters suffice (~300 LOC) |
| Need `trust/cutover.json` (GATE-1.1) | `bootstrap.status` already provides cutover gating |
| Need per-key `role` field in `allowed_signers` (GATE-2.4) | Use principal encoding `role+agent_id@crosslink` |
| Need RFC 8785/JCS JSON canonicalization (§7 Q3) | Crosslink uses sorted `key=value\n`; JCS not required |
| `crosslink-driver` OS user is the sole driver-key mechanism (GATE-1.5) | Add `--key-dir` fallback so CI works without `useradd` |

---

## 4. Revised issue verdicts (GATE-1.x / GATE-2.x)

Legend: ✅ valid · 🔄 reframe · ❌ descope

**Section 1 — Migration & Compatibility**
- **GATE-1.1** Cutover record — ❌ descope (use `bootstrap.status`)
- **GATE-1.2** Enforcement guard — 🔄 merge into Phase 1; keep loud warning
- **GATE-1.3** Backfill / re-signing — ❌ descope (`integrity sign-backfill` exists)
- **GATE-1.4** Dry-run / warn mode — 🔄 keep as `dry-run` enum variant (Phase 1)
- **GATE-1.5** Driver key retrofit — ✅ simplify with `--key-dir` for CI

**Section 2 — Valid Evidence per Role**
- **GATE-2.1** Evidence per role — 🔄 defer fine-grained roles; `Driver`/`Agent` covers MVP
- **GATE-2.2** Non-repudiation — 🔄 largely exists; wire `verify_event_signature` (Phase 2)
- **GATE-2.3** Orchestrator ≠ evidence — ✅ valid; implicit under simplified roles
- **GATE-2.4** `allowed_signers` role field — 🔄 principal encoding instead of struct field

(Full annotations in `gates-issues.md`.)

---

## 5. Corrected implementation plan

| Phase | Deliverable | Depends on |
|---|---|---|
| **0** | TDD BYPASS tests (~15 scenarios) asserting current `audit` behaviour | — |
| **1** | Plumb `signing_enforcement` into local `sync`/`kickoff`/`swarm`; add `dry-run` variant; respect `bootstrap.status` | Phase 0 |
| **2** | Wire `verify_event_signature()` into sync event-replay + kickoff/swarm completion | Phase 1 |
| **3** | `crosslink trust driver-init [--key-dir]` + `--force` guard + override audit log | Phase 2 |
| **4** | Reconcile `bootstrap.status` vs `cutover.json` (descope the latter) | Phase 3 |
| **5** | `crosslink status --audit-violations` / `--override-audit` reporting | Phase 3 |

**Effort:** ~300 LOC enforcement wiring + ~150 LOC event-sig call sites. Not a new service module.
**Highest-risk item:** plumbing enforcement into the correct (per-command) code path rather than a
monolithic service. **Most dangerous omission in original design:** no CI path for the driver key.

---

## 6. What we still do not know

- **The server-crash root cause** (this session was interrupted by a Hostkey VPS hard-reset while two
  `task` agents ran concurrently). Strong hypothesis: memory exhaustion from opencode context bloat
  (≈870 MB/session) × cloned subagent contexts on an ≈8 GB VPS. **Unconfirmed** — needs the Hostkey
  Serial Console / RAM graph around the 17:46 UTC reset. See `server-crash-postmortem.md`.
- Whether fine-grained `Builder`/`Reviewer`/`Auditor` roles are actually required by a real workflow, or
  whether the `Driver`/`Agent` split is sufficient permanently.
- Exact UX of the `dry-run` report and the audit-violation viewer (deferred details).

---

## 7. Evidence appendix

**Files examined**
- `to-file/evidence-based-gates.md` (design)
- `to-file/gates-issues.md` (revised issues)
- `to-file/gates-verified-facts.md` (source truth)
- `to-file/server-crash-postmortem.md` (incident log)
- crosslink `0.9.0-beta.1` source: `signing.rs`, `events.rs`, `sync/trust.rs`, `sync/bootstrap.rs`,
  `commands/trust.rs`, `identity.rs`, `clock_skew.rs`, `config_registry.rs`, `server/types.rs`,
  `server/handlers/config.rs`, `dashboard/reader.rs`, `trust_model.rs`

**Key citations**
- `signing_enforcement` default `audit`: `config_registry.rs:108-112`
- enforcement only in server layer: `server/types.rs`, `server/handlers/config.rs` (zero refs in
  `commands/sync.rs`, `commands/kickoff/run.rs`, `commands/swarm/*`)
- `verify_event_signature` uncalled: `events.rs:505-522`
- `bootstrap.status` cutover: `sync/bootstrap.rs:55-64`
- canonicalization `key=value\n`: `signing.rs:683-698`
- `AgentRole{Driver,Agent}`: `identity.rs:19-25`

**Process note:** Both v2 scoping agents were run in *separate sessions*. The concurrent launch of both
in one message is the action correlated with the server crash; re-running deepseek-flash alone
succeeded. Recommend serial agent launches going forward.
