# Independent Clean-Room Verification Report — F3 L5 Integration

**Review target:** commit `b49e1f66ddd91e501794f6c9381e1e96c19b096c` (`research/f3-l5-lifecycle-integration-20261031`)
**Packet root:** `/tmp/ases-f3-l5-review-packets-20261031/mimo`
**Verdict:** **PASS** (bounded, profile-limited — not full F3/F5 closure)

---

## 0. Provenance, eligibility, and method

**My route:** `opencode/mimo-v2.6-flash-free` (distinct approved route).
**Eligibility basis:** `IMPLEMENTATION-LAUNCH-PROVENANCE.txt:3–4` records that implementation was directly authored by GPT-6 Luna; the only attempted external implementation invocation (Codex CLI v0.157.1, model `glm-5.3-flash`, provider `pgs2`) returned HTTP 402 *before* any implementation output. No successful delegated implementation output exists. My review route is therefore independent of the implementation model, and no implementation authorship is inferred from the failed Codex call. No peer-review verdict was available to or consumed by me.

**Governing sources.** Per instruction, the originally supplied `5c03a425…` is treated as unrelated and was not sought. I read the packet's `spec/Phase-I-Verification.md` (**T11** at `spec/Phase-I-Verification.md:129`) and `spec/Phase-I-Closure.md` (**§7** at `spec/Phase-I-Closure.md:536–615`). Packet file digests: `Phase-I-Verification.md` = `f8dbf16606ad…`, `Phase-I-Closure.md` = `c30a1d89f2c8…`. **Limit:** the packet contains no `.git`, so I could not independently confirm these files are the ones at `511a5272…` (T11) / `8277b7f3…` (§7), nor confirm the target commit hash; I verified content identity of the sections only. Target-source identity is anchored instead by the raw evidence digest binding (below).

**Discipline.** No file was modified. Exactly one run command was executed, as authorized:

```
python3 research/phase-i-protected-work-unit-f3/lifecycle/l5/verify_l5_integrated.py
```

(from workspace root; one earlier invocation with a doubled relative path failed with ENOENT and executed nothing). No other agent was spawned. No path outside this workspace was read.

**T11 (verbatim obligation, `spec/Phase-I-Verification.md:129`):** C has local read/write, P restricts to read; move sealed C under Q allowing both; after activation read succeeds and write still fails *unless a separate authorized grant explicitly changes it*; include D.
**§7 (key clauses, `spec/Phase-I-Closure.md:560–561, 566–572, 589`):** sealed move validates both contexts, avoids cycles/dangling, retains contents and descendant protection, preserves or narrows latent authority; move cannot grant new rights; activation is a separate current authorized event recomputing full-path constraints; C8 forbids silent latent widening including descendants and later activation.

---

## 1. Verifier's observed output (exit 0)

```
PASS raw source digest matches the executed integration source
PASS positive retained independent L4 run evidence
PASS positive retains both exact accepted L4 contents
PASS safe retained independent L4 run evidence
PASS safe retains both exact accepted L4 contents
PASS weakened retained independent L4 run evidence
PASS weakened retains both exact accepted L4 contents
PASS post-move read is exact x from retained and hash-verified L4 accepted storage
PASS accepted x identity/provenance is retained from L4
PASS C and dependent D moved together under Q, D remains child/dependent of C
PASS full transitive path preserves read-only effective ceiling for D
PASS move and activation are distinct authorized whole records
PASS unauthorized management request is denied with no state mutation
PASS safe move permits verified read, denies write, and creates no effect
PASS positive control commits concrete write effect
PASS weakened restriction mutation admits same post-move write
PASS accepted object bytes/hash remain unchanged in all cases
PASS cycle, dangling parent, and unknown permission structures are rejected
PASS every runtime case reports a valid final graph and the bounded status
```

I independently confirmed the digest binding at `verify_l5_integrated.py:10`: `l5_integrated.py` sha256 = `daf24f8fce53810a3961fb72062c49165798b1580ccc88734d941fed41d21156` equals `source_sha256` in `l5-integrated-raw.json`; the three embedded L4 evidence files are byte-equal to their per-case copies and each `l4_raw_sha256` matches; all L4 content hex↔sha256 pairs recompute; baseline discriminator evidence is bound to `l5_write.py` (`source_sha256` `21477179…`).

---

## 2. How the implementation actually behaves (verified by reading, not just by the run)

- **Permission evaluation is genuinely transitive and recomputed per request.** `permissions()` (`l5_integrated.py:46–53`) intersects the ancestor chain's `grants` with any `latent_ceiling` along the path; the mediator calls it fresh from the on-disk current record for every worker request (`:138–140`). Effective rights are never cached in the worker.
- **Move captures and freezes old authority.** `manager_roundtrip` `authorize_move` (`:82–91`) requires manager credential, `graph_valid`, `current_ingress is None`, and *all* units active==False and sealed==True; then sets `C.parent='Q'` and writes `latent_ceiling = prior full-path permissions` for both C and D (`:86–87`), re-validates the resulting graph, and commits one atomic record. Q is permissive (`['read','write']`, `:69`), so post-move D effective rights = `{read}` purely from the retained ceiling (`:132` asserted).
- **Activation is a separate commit.** `authorize_activate` (`:92–98`) requires C already under Q, none active, ingress clear; sets ingress `W-L5`, activates P/Q/C/D, unseals, commits a distinct record. Verifier confirms distinct record names (`verify_l5_integrated.py:21`).
- **Manager authorization does gate transitions — and the gate is non-vacuously exercised.** An unauthorized request (`authorized_by:'intruder'`, wrong credential, `:104–107`) is received, denied, and the pre/post state JSON is byte-identical; asserted at `verify_l5_integrated.py:22`. Within the declared single-trusted-mediator profile this is a real gate, not a rubber stamp.
- **Accepted-object integrity/currentness.** Every served read goes through `verified_content()` (`:23–30`): relative `objects/`-anchored path, no `..`, resolved inside the protected store, sha256 **and** size re-checked against current-record metadata. The served bytes are compared to the retained L4 accepted x (`verify_l5_integrated.py:17–18, 26`).
- **Structure validation is real.** `graph_valid()` (`:31–45`) enforces the exact unit set {P,C,Q,D}, parent references, cycle-freedom, right vocabulary ⊆ {read,write}, and the P/Q root + C∈{P,Q} + D→C + `depends_on==['C']` shape. Adversarial controls (`:152–155`) confirm cycle, dangling parent, and unknown permission rejection (`verify_l5_integrated.py:27`).
- **The weakened-mutant discriminator is a genuine discriminator.** Dropping both latent ceilings to `['read','write']` after a correct move (`:114–116`) flips the same post-move write from DENY (safe) to COMMITTED with a concrete effect (`verify_l5_integrated.py:23 vs :25`). This defeats the vacuity objection: the safe case's write denial is caused by the retained ceiling, not by an inert write path or a universally-denying mediator.
- **Dependent D travels and inherits.** D's parent stays `C`, `depends_on` preserved, D's ceiling set in the same move event (`included:['C','D']` in the committed event, checked at `verify_l5_integrated.py:19–20`).

---

## 3. Findings by severity

### Blocking
None.

### Major

**M1 — T11's "unless a separate authorized grant explicitly changes it" is unimplemented; the only widening path is labelled a mutation, not a grant.**
The safe case proves the negative half. There is no `authorize_grant_change` / latent-ceiling-raising operation anywhere in `l5_integrated.py`; the *only* way ceilings widen post-move is the in-test mutant at `:114–116`, which mutates `latent_ceiling` in-process and commits via the ordinary `commit()` with event `unsafe_mutant_drop_latent_restrictions`. So the authorized-grant half of T11 has **no tested implementation**. `commit()` (`:54–59`) accepts any well-formed state with no guard on who may widen ceilings, so an authorized widening path is representable but not realized or gated. Disposition: missing profile evidence / unimplemented clause — not a proven safety defect (the mediator is trusted), but T11 is only half-discharged.

**M2 — The raw evidence is single-source and self-reported; record digests are not independently re-derivable.**
`run_case` deletes its whole L4-derived fixture at `:150` before returning, so the `record_sha256` values asserted in `mediator_checks`, `move`, and `activation` can never be recomputed from surviving bytes. The verifier (`verify_l5_integrated.py:7–28`) re-parses the generator's own JSON and checks internal consistency, but does not re-derive `permissions()`, does not re-hash any retained record file, and does not re-execute the implementation. The only *independently retained* raw facts are the L4 evidence copies (`l5-integrated-l4-*.json`) and their content digests. `verify_l5_write.py:17` (the older standalone witness) did bind checks to `record_sha256 == activation_record_sha256` and to worker/authority pid distinctness (`:20`); `verify_l5_integrated.py` does neither. Adequate as bounded evidence, weak as independent verification.

### Minor

**m1 — Positive-control activation bypasses the management socket path.** In the no-move branch (`:118–128`) state is activated directly in-process and committed as `separately-authorized_positive_control_activation`, with no `manager_roundtrip`, no credential check, and `activation_event` is `None` in the positive case (confirmed in raw). The verifier never checks the positive case's management path at all — only that a write effect occurred (`verify_l5_integrated.py:24`). The positive baseline therefore does not demonstrate *authorized* activation; it demonstrates that writes are possible when rights exist.

**m2 — Verifier under-binds the safe-case mediator checks.** `verify_l5_integrated.py:23` does not require both safe `mediator_checks` entries to carry `parent_C=='Q'`, `current_ingress=='W-L5'`, the activation `record_sha256`, or a common `worker_pid`. I confirmed from the raw data that they do (`6cabac88…` == activation sha, parent Q, pid 290685), so this is a verifier-completeness gap, not a defect in the run.

**m3 — `included_in_move` is vacuously true when `move` is false.** `:149` encodes `not move or …`, so the positive case reports `included_in_move: True` despite no move occurring. Misleading field; verifier only reads the safe case.

**m4 — D's own accepted content is never read back.** D is seeded with `[y]` (`:71`), but no case ever verifies D's `accepted_contents` integrity, retention, or usability after move/activation. §7's "retain bounded contents and descendant protection" is only partially evidenced (graph linkage + effective rights only).

**m5 — Activation guard does not require sealedness.** `authorize_activate` (`:93`) requires all units inactive and ingress clear, but unlike `authorize_move` (`:83`, which requires `sealed` for all) it does not require `sealed`. An unsealed-but-inactive state could be activated. Not adversarially tested.

**m6 — Latent ceilings are mutable by any ordinary commit.** The mutant path (`:114–116`) shows there is no structural obstacle to widening ceilings other than mediator discipline. This is within the declared trusted-mediator profile (disclosed at `:162`) but means the preservation guarantee is entirely mediator-conferred, not substrate-enforced.

**m7 — Q is always permissive; no restrictive-destination case.** With Q granting `['read','write']` (`:69`), the post-move read ceiling comes *solely* from `latent_ceiling`. The fixture does not discriminate a restrictive destination parent. Untested combination.

**m8 — The "concrete write" is a mediator-side effect, not a worker-originated one.** The worker only requests `write_d`; the bytes are written by the mediator process at `:143–144`. Correct for the profile (Landlock-confined worker via `l1.confine`, `l1.py:69–75`, which grants read of `/usr,/lib,/lib64,/etc/ld.so.cache` only), but "concrete write effect" should be read as *mediated host effect on request*, matching §4's mediated-use contract rather than an interior capability.

**m9 — Commit-message replay and store-corruption paths are untested.** A replayed valid `authorize_move` after a successful move is denied only incidentally (state no longer sealed); no replay test exists. A truncated/tampered current record raises uncaught `ValueError`/`json` exceptions from `load_current` (`:19–22`) rather than a controlled denial.

**m10 — Commit identity is unverifiable inside this packet.** No `.git`; `b49e1f66…`, `511a5272…`, `8277b7f3…` cannot be checked. The strongest available anchor is `daf24f8f…` binding `l5-integrated-raw.json` to `l5_integrated.py`, which I re-verified.

---

## 4. T11 / §7 support matrix

| Requirement | Source | Status | Evidence |
|---|---|---|---|
| C local read/write, P restricts to read | T11 | **Tested** | `:67–68, :101` (`P.grants=['read']`, `C.grants=['read','write']`); raw safe case `D_effective/C_effective=['read']` |
| Move **sealed** C under permissive Q | T11, §7 | **Tested** | `:83` all-sealed precondition; `:86–91` committed `authorized_sealed_whole_move`; verifier `:19` |
| After activation, read succeeds | T11 | **Tested** | safe worker read OK, sha `1462070e…` == L4 accepted x; verifier `:17–18` |
| After activation, write still fails | T11 | **Tested** | safe write DENY, `effects == []`; verifier `:23`; discriminator flip in mutant proves non-vacuity (`:25`) |
| …unless a **separate authorized grant** changes it | T11 | **Untested / unimplemented (M1)** | no grant-change operation exists; only labeled mutant `:114–116` |
| Include dependent D; D inherits restriction | T11, §7 C8 | **Tested (narrow)** | move event `included:['C','D']`; D ceiling captured; `:132`, verifier `:19–20`. D's own accepted contents untested (m4) |
| Move cannot grant new rights; preserve or narrow latent authority | §7 :560, :566–572 | **Tested** | ceilings = exact prior full-path effective (`:86–87`); `permissions()` re-intersects on every request (`:51, :138`) |
| Avoid cycles / dangling relations | §7 :560 | **Tested** | `graph_valid` `:40–45`; adversarial controls `:152–155`; verifier `:27` |
| Retain bounded contents across move | §7 :560, C5 | **Tested for C's x; partial for D** | `accepted_x_unchanged` all cases; verifier `:26`; D untested (m4) |
| Separate current authorized activation; recompute full-path constraints | §7 :561 | **Tested (with caveat m1 for positive case)** | distinct records; verifier `:21`; fresh `permissions()` per request |
| Manager authorization gates transitions | §7 :546 | **Tested, profile-bounded** | unauthorized request DENY + byte-identical state; verifier `:22`. Credential is a test shared secret, actor is a self-declared string (`:80`, disclosed `:162`) |
| Structural controls (cycle/dangling/unknown right) | §7 :585 (C4) | **Tested** | verifier `:27` |
| Full F3/F5 closure | — | **Not claimed** | `limits.does_not_claim` `:162`; I concur |

---

## 5. Tested behavior vs proven defects vs untested risks

**Tested behavior (bounded, single-holder, disposable L4-derived fixture, one worker, one write op per case):** transitive full-path permission recomputation; sealed precondition on move; latent-ceiling capture and descendant propagation; separate activation commit; unauthorized-management denial with no mutation; exact-bytes accepted-content read after move; write denial caused by the retained ceiling (discriminated by the mutant); structure validation with three adversarial rejections; accepted-object integrity/currentness re-verification at every read.

**Proven defects:** none safety-breaking within the declared profile. The findings are M1 (unimplemented T11 widening clause), M2 (self-reported, non-re-derivable raw evidence), and the minors — gaps and over-read risks, not demonstrated confinement or authorization failures.

**Untested risks (explicit):** authorized latent-ceiling raising; restrictive destination parent; D's accepted-content retention; hostile descendants, descriptor passing (SCM_RIGHTS), network ingress, alternate mounts; fsync/power-loss/rollback; record corruption → controlled denial; message replay; manager identity beyond a shared test secret; any second move or re-seal/reactivate cycle; non-vacuous positive-control authorization (m1). The generator itself discloses most of these at `:162`.

---

## 6. Model / provider provenance

- **Implementation author (per packet):** GPT-6 Luna, direct coding session. Only external implementation attempt: Codex CLI v0.157.1 / `glm-5.3-flash` via provider `pgs2`, HTTP 402, no output. No successful delegated implementation model.
- **This review:** route `opencode/mimo-v2.6-flash-free`; eligibility = distinct approved free OpenCode route, independent of the implementation model; no peer-review verdict consumed.
- **Executed locally:** Python 3.10.12 on Linux 5.15.0-184-generic, Landlock ABI 1 (per `l5-integrated-raw.json`).

---

## 7. Explicit limits of this review

1. I did not modify any file, spawn any agent, or read anything outside this packet. I did not re-run `l5_integrated.py` or any L1/L3/L4/L5 generator — only the authorized verifier.
2. Commit hashes `b49e1f66…`, `511a5272…`, `8277b7f3…` are **not verifiable** in this packet (no VCS metadata); content-level identification of T11 and §7 was used instead.
3. The verifier re-checks embedded JSON consistency and retained L4 evidence; it does not re-execute the implementation or re-derive permission math, so raw-record digests remain single-source (M2).
4. This report supports only the bounded L5 T11/§7 obligations as tabled. It does **not** establish full F3 or F5 closure, does not discharge F1/F2/F4 traces, AC/C13, D1/D2/D3 engine-loss claims, T01–T24 beyond T11, or any stronger profile in §7 of the verification plan.