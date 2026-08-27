---
title: Doll Corpus Retrospective — From Beads to Crosslink via Gates 0–10
program: EDASES
layer: Research
document_type: Standard
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - Documentation Standard
  - Concept: Levels of Abstraction
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/ORCHESTRATOR.md

consumed_by:
  - Future ATProto / Beads / Chainlink / VDD corpus extractions
  - ASES methodology development
  - Execution engine research programme

related_documents:
  - .crosslink/knowledge/agent-orchestration-playbook.md
  - docs/research/session-recovery-after-crash.md
  - docs/research/Workflow Topology Design and Reasoning Record.md

supersedes: []

superseded_by: []

last_updated: 2026-08-27
---

# Doll Corpus Retrospective — From Beads to Crosslink via Gates 0–10

## Purpose

This document is the full retrospective of the Doll Corpus extraction — the
Beads → Chainlink → VDD / VDD-IAR → Crosslink run executed through Gates 0–10
— preserved as a **reusable research method**. It records why the pipeline was
built the way it was, what survived contact with the real ATProto AppView,
what failed, and what a future operator should copy verbatim.

It is a Derived synthesis of the actual run. Where numbers are quoted they
are the observed numbers from that run, not projections.

---

## 1. Objective

Extract a bounded, evidence-linked Doll research corpus from the public
ATProto network and land it as Crosslink artefacts, using the same gate
discipline that governs any future domain corpus:

```
Beads  →  Chainlink  →  VDD / VDD-IAR  →  Crosslink
              Gates 0 – 10
```

* **Beads** — raw post collection from the unauthenticated AppView.
* **Chainlink** — lexical and contextual eligibility, thread expansion.
* **VDD / VDD-IAR** — decisions, eras/URIs, facets/evidence, research
  questions, final deliverables.
* **Crosslink** — durable issue / artefact store (Gates as Crosslink issues).

Gates 0–10 are the reusable pipeline template. The Doll run is the first
instantiation.

---

## 2. The Funnel (Observed Numbers)

All counts are from the completed Doll run.

| Stage | Artefact | Count | Notes |
|-------|----------|-------|-------|
| **Scan universe** | ATProto posts scanned | **21,413** | 205 pages via AppView |
| **Collected** | Posts persisted (atomic + cursor) | **19,932** | unauthenticated, streaming |
| **Lexical pass** | Lexically eligible | **2,326** | vocab `d8cca707` |
| — | — before alias strip | 4,392 | inflated by `doll` alias |
| — | `doll` alias hits stripped | **2,585** | single largest FP source |
| **Contextual pass** | Contextually eligible | **509** | 460 high + 49 low anchored |
| **Thread expansion** | Threads | **284** | expanded to 1,251 posts, avg 4.4 / thread |
| **Gate 5** | Decisions | **10** | curated from threads |
| **Gate 6** | Eras / URIs | **5 eras / 29 URIs** | era-bounded URI sets |
| **Gate 7** | Facets / evidence | **16 facets / 72 evidence** | facet → evidence links |
| **Gate 8** | Research questions | **16 RQs (P0 5)** | prioritised |
| **Gates 9–10** | Final deliverables | **4 finals** | terminal artefacts |

Mnemonic for reuse: **21k → 20k → 2.3k → 509 → 284 (1,251) → 10 → 5/29 → 16/72 → 16(5) → 4**.

Lexical vocab identity `d8cca707` is recorded so a future run can assert
byte-identical eligibility.

---

## 3. Pipeline — Gates 0–10 as a Reusable Template

| Gate | Name | Input → Output | Discriminating check |
|------|------|----------------|----------------------|
| 0 | **Probe & Scope** | question → AppView capability + filter behaviour | Filter probe (see §4.9) before any collection |
| 1 | **Collect** | AppView pages → raw posts (atomic writes + cursor) | Resume-from-cursor after kill; RSS < 500 MB |
| 2 | **Lexical eligibility** | raw → lexically eligible | NO LLM; STOP gates; alias strip; word-boundary for len ≤ 3 |
| 3 | **Contextual eligibility** | lexical → contextual | Co-occurrence + thread anchoring (rescues low-specificity) |
| 4 | **Thread expansion** | contextual posts → threads | Thread is the primary unit (not post) |
| 5 | **Decisions** | threads → decisions | Human / LLM curation with evidence links |
| 6 | **Eras / URIs** | decisions + threads → eras + URI sets | Era bounds are explicit |
| 7 | **Facets / Evidence** | eras → facets + evidence | Facet → evidence traceability |
| 8 | **Research Questions** | facets → RQs (prioritised, P0 subset) | P0 = must-answer |
| 9 | **Finals — draft** | RQs → draft deliverables | Linked to RQs |
| 10 | **Finals — release** | drafts → released finals | Gate close requires termination-path verification |

Gates 0–4 are mechanical and must be deterministic. Gates 5–10 are
interpretive and require human judgement — the pipeline makes that boundary
explicit.

### Extraction/lib trio (reuse as a library)

The Doll run factored three modules that should be copied, not reinvented:

* **collector** — AppView paging, atomic writes, cursor persistence.
* **lexicon** — vocab-gated eligibility, alias handling, word-boundary matching.
* **threader** — thread reconstruction and anchoring.

Future corpora should vendor or import this trio and only replace the vocab
and the Gate 5+ curation prompts.

---

## 4. What Worked

### 4.1 Cheap unauthenticated AppView collection with atomic writes + cursor

No auth, no paid tier. Each page was written atomically (write-to-temp then
rename) and the cursor was persisted alongside the data. A killed collector
resumes from the last cursor — no re-scan, no duplicate pages. This is why
the run survived multiple Observer kills and an `earlyoom` SIGTERM and still
landed 19,932 / 21,413 posts.

### 4.2 Lexical-first, NO LLM, with STOP gates

Lexical eligibility (vocab `d8cca707`) ran before any model call. STOP gates
prevented LLM spend on posts that could never qualify. At ~10% lexical
pass-through (2,326 / 19,932) the saving is structural, not marginal.

### 4.3 Alias strip — `doll` removed (2,585 hits)

The initial lexicon matched the alias `doll` as if it were domain vocabulary.
Stripping that alias cut the lexical set from 4,392 to 2,326 (−2,585). The
alias was by far the largest single source of false positives. Rule: domain
aliases that collide with common English must be stripped or demoted before
any count is reported.

### 4.4 Word-boundary fix for len ≤ 3 tokens (IAR / Git / OOM / lock)

Short tokens were initially matched by substring (`IAR` inside `familiar`,
`Git` inside `legitimate`, etc.). Enforcing `\b` word boundaries for tokens
with length ≤ 3 eliminated this class of false positive. Four tokens were
affected: `IAR`, `Git`, `OOM`, `lock`. Cost: one regex flag. Saving: entire
lexical precision floor.

### 4.5 Thread as the primary unit

Post-level eligibility is noisy. Threads (284 threads → 1,251 posts, avg 4.4)
are the unit that carries context. Anchoring, co-occurrence, and all
Gate 5+ artefacts reference threads, not isolated posts.

### 4.6 Streaming with RSS < 500 MB

The collector streamed pages to disk and never held the full 21k corpus in
memory. Resident set stayed below 500 MB for the entire run. This is what
kept the process alive on a memory-constrained host (see §5.4) and what
future runs must preserve — no in-memory accumulation pass.

### 4.7 < 2 min checkpoint + 45 s heartbeat — survived Observer kills

State was checkpointed every < 2 minutes and a 45-second heartbeat was
emitted. Observer incorrectly killed two collectors on pane-hash false
positives — `pp3g-qlIC` (failed) and `pp3g-lGBq` (succeeded) — plus the `b2N7`
harness fell into an `rtk git` loop. All three were recovered from the last
checkpoint because the heartbeat made staleness unambiguous and the checkpoint
interval bounded loss to < 2 minutes of progress.

### 4.8 Strict local `.gitignore` + disk-only derived artefacts

```
raw/
normalized/
state/
corpus/
derived/
__pycache__/
```

Raw, normalized, state, corpus, and derived artefacts were never staged.
Derived artefacts lived on disk only (ignored, not committed). This prevented
accidental 5 GB commits and kept `git status` readable. The one exception was
the over-eager `derived/` ignore that hid `extraction/` — see §5.7.

### 4.9 Model fallback chain — unused but wired

The fallback chain (`muse-spark` → `hy3-free` → Go) was wired through the
harness but never triggered in the Doll run. Its value is as insurance: a
future run that does trigger it will not need a code change mid-flight.

### 4.10 Filter probe — 68/100 gap, `posts_with_replies` fallback, `postsCount` 14,333

Before collection, a probe asserted filter behaviour. The probe revealed:

* a **68/100 gap** between the advertised filter and observed pass-through;
* that `posts_with_replies` was the viable fallback filter;
* that `postsCount 14,333` was the exact-match count for the chosen filter.

Without this probe the run would have collected under the wrong filter for
205 pages before anyone noticed. The probe is now Gate 0 and must run before
any collection in every future corpus.

### 4.11 Co-occurrence + thread anchoring for low-specificity terms

Low-specificity lexical hits (49 of the 509) were not discarded. They were
anchored to their thread: a low-specificity post that co-occurs in a thread
with a high-specificity post inherits eligibility through the thread. This
rescued 49 posts that post-level scoring would have dropped and is the reason
the contextual set is 509 (460 + 49) rather than 460.

---

## 5. What Didn't Work

### 5.1 Filter omission

The initial collector ran without the Gate 0 filter probe. The misconfigured
filter was only caught after a full scan had been evaluated. Cost: one wasted
scan cycle. Fix: Gate 0 is now mandatory and blocks Gate 1.

### 5.2 Alias inflation

As noted in §4.3, `doll` as an alias inflated the lexical set by 2,585
(~59%). The error was silent — counts looked plausible until the alias was
enumerated. Lesson: enumerate and justify every alias in the vocab before
reporting any funnel number.

### 5.3 Substring false positives

Short tokens matched as substrings before the word-boundary fix (§4.4). Any
future vocab that adds a token with length ≤ 3 must be tested against a
substring probe (e.g. `IAR` must not match `familiar`) before it ships.

### 5.4 Observer pane-hash false positives + harness loop

Three incidents in one run:

| Incident | Session | Outcome |
|----------|---------|---------|
| Observer pane-hash collision | `pp3g-qlIC` | killed — **failed** (false positive) |
| Observer pane-hash collision | `pp3g-lGBq` | killed — **succeeded** (also a false positive, but recovery worked) |
| Harness `rtk git` loop | `b2N7` | tight loop on git state polling |

All three were caused by the Observer's pane-hash heuristic treating a busy
collector as stalled. Mitigations: heartbeat (§4.7) disambiguates "busy" from
"stalled"; `rtk ls/read` replaces bare `git` in harness polling; pane-hash
thresholds need retuning (tracked separately).

### 5.5 earlyoom SIGTERM at 05:58 (PID 704, 3.4 / 3.9 GB swap)

At 05:58 the host `earlyoom` sent SIGTERM to PID 704 when swap hit 3.4 GB of
3.9 GB. The collector died mid-page. Recovery succeeded because of atomic
writes + cursor (§4.1) and checkpoint interval (§4.7), but the incident shows
that RSS < 500 MB (§4.6) is not optional — any future change that grows
resident set risks turning a recoverable SIGTERM into an unrecoverable OOM
kill (SIGKILL, no graceful shutdown).

### 5.6 Swarm singleton conflict (Observer Swarm v1.1 active, fell back to sequential kickoffs)

The run attempted a swarm launch while Observer Swarm v1.1 was already active.
The singleton guard rejected the second swarm. The run fell back to sequential
`kickoff`s. Sequential is slower but deterministic and does not contend on the
singleton. Until the singleton is lifted, sequential is the default.

### 5.7 Over-eager `derived/` ignore hiding `extraction/`

The `.gitignore` entry for `derived/` was written as a prefix match that also
ignored `extraction/` (which lived under `derived/extraction/` in an earlier
layout). The extraction code was therefore invisible to `git status` and to
review. Fix: use anchored or strict directory ignores (`/derived/` not
`derived/`) and verify with `git check-ignore -v -- <path>` after any
`.gitignore` change.

---

## 6. Going Forward — Reusable Method

### 6.1 Template Gates 0–10 as the pipeline

Copy the gate table in §3. Replace only the vocab, the Gate 0 probe
assertions, and the Gate 5+ curation prompts. Do not reorder gates; do not
merge Gates 0–4 with Gates 5–10 — the mechanical / interpretive boundary is
load-bearing.

### 6.2 Extraction/lib trio

Vendor the three modules (§3, Extraction/lib trio) as a library. Future
corpora should not reimplement collection, lexicon, or thread logic.

### 6.3 Resilience checklist (copy verbatim)

Every future run must satisfy all six before Gate 1 opens:

- [ ] **< 2 min checkpoint** — state flushed to disk every < 2 minutes.
- [ ] **45 s heartbeat** — liveness file updated every 45 seconds.
- [ ] **Streaming, RSS < 500 MB** — no in-memory accumulation of the raw corpus.
- [ ] **Strict `.gitignore`** — `raw/`, `normalized/`, `state/`, `corpus/`, `derived/`, `__pycache__/` ignored; verified with `git check-ignore -v`.
- [ ] **Model fallback chain wired** — even if unused.
- [ ] **Filter probe (Gate 0) green** — before any collection.
- [ ] **Word-boundary enforcement for len ≤ 3** — tested with substring probes.

### 6.4 Alias rule

Every alias in the vocab must be enumerated and justified. Any alias that
collides with common English (e.g. `doll`, `chain`, `beads`) is stripped or
demoted to co-occurrence-only by default. Report both pre-strip and post-strip
counts.

### 6.5 Filter probe as the first step (Gate 0)

No collection without a passing filter probe. The probe must assert:

* filter name and parameters;
* expected vs. observed pass-through (report the gap, e.g. 68/100);
* fallback filter if the primary is unavailable (`posts_with_replies`);
* exact-match count for the chosen filter (`postsCount`).

### 6.6 Git boundary — local-only by default

All artefacts are local until the operator explicitly approves a push. No
agent pushes. No bare `git` in harness polling — use `rtk ls/read`. Derived
artefacts are disk-only and ignored; only curated gates (decisions, eras,
facets, RQs, finals) are committed.

### 6.7 Archiving — `tar cJf` / `zstd --long`, not 7zip, for 5 GB sessions

Session archives at ~5 GB must use:

```bash
tar cJf archive.tar.xz <dir>        # xz, or
tar -I 'zstd --long' -cf archive.tar.zst <dir>
```

Do not use `7z` / `7zip` — it is not guaranteed to be available on the host
and handles large streaming archives poorly in this environment. `tar` +
`xz`/`zstd` is universally available and streams without holding the full
archive in memory.

---

## 7. Traceability

| Concept | Doll value | Reuse action |
|---------|------------|--------------|
| Vocab identity | `d8cca707` | Assert byte-identical or bump and record new hash |
| Scan universe | 21,413 | Re-probe; do not assume stable |
| Lexical eligibility | 2,326 (4,392 pre-strip) | Re-run alias strip; compare counts |
| Contextual | 509 (460 + 49) | Re-run anchoring; report split |
| Threads | 284 → 1,251 (avg 4.4) | Primary unit for all downstream gates |
| Decisions → Finals | 10 → 4 | Human curation; not mechanical |

---

## 8. Open Questions

* Whether the vocab hash should be content-addressed (hash of vocab file) or
  assigned — `d8cca707` was assigned; content addressing would make drift
  detection mechanical.
* Whether Gate 5 (decisions) can be partially automated without losing
  traceability — current answer is no; keep it human-curated.
* Whether pane-hash thresholds can be tuned to eliminate the false-positive
  class in §5.4 without losing real-stall detection.

---

## 9. References

* Workflow Topology Design and Reasoning Record
  (`docs/research/Workflow Topology Design and Reasoning Record.md`) —
  two principles (reasoning certainty, cheapest-test-first), information
  asymmetry boundary, position-emitting agents, durable store, cheap staleness
  trigger, AUDITOR as one-role/two-phase verifier, reviewer as
  pre-consumption readiness audit.
* ORCHESTRATOR (`docs/ORCHESTRATOR.md`) — operational procedure derived from
  the topology design.
* Agent Orchestration Playbook (`.crosslink/knowledge/agent-orchestration-playbook.md`,
  §5.8) — dispatch-level mechanics.
* Documentation Standard (`docs/standards/Documentation Standard.md`) —
  frontmatter and dependency rules applied by this document.

---

*This retrospective was written from the observed Doll Corpus run. Numbers,
session IDs, and incident timestamps are as recorded during that run.*
