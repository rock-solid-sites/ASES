# F3 L5 — Independent Clean-Room Source Review

**Reviewer:** opencode (DeepSeek V4.1 Flash 1017), primary independent reviewer
**Review branch:** `review/f3-l5-independent-20261030195936`
**Implementation commit under review:** `fb34deca9ea8c1bf04ec808052b39d7521040290`
**Governing spec commit:** `5c03a425fd5627c3764806292b8c5cb653498f4f`
**Packet:** `research/phase-i-protected-work-unit-f3/lifecycle/l5/REVIEWER-PACKET.md` @ `1f9bcf8a128b69836afc9282d4d9b7601578ca51`

## Method and independence

- Started from a fresh worktree created directly at the implementation commit
  (`git worktree add -b review/f3-l5-independent-... <path> fb34deca...`).
- Read only the three pinned implementation artifacts, the direct dependency
  `l1.py` (for `confine()` / Landlock), and the two governing specs at the pinned
  spec commit (`git show 5c03a4...:docs/...`).
- Did **not** read `RESULT.md`, `OBSTRUCTION.md`, earlier review reports, or the
  pre-existing `f3-l5-*` audit directories before recording this verdict.
- Re-ran the verifier and re-executed the implementation in an isolated
  disposable copy under `/tmp`.
- Ran additional independent probes (a Landlock direct-write probe built from the
  same `l1.confine`, and isolated evidence-mutation checks) **without modifying
  the pinned source or the recorded `l5-write-raw.json`**.
- GLM 5.3 Flash performed a separate independent review via the Phoenix Grove
  provider (`codex-pgs2`, `https://api.pgsgrove.com/v1`). MiMo V2.6 Flash was
  quota-blocked on that provider (HTTP 402, daily Taster-plan allowance spent,
  refill 2026-11-01T00:10Z) at review time, so its independent review was run on
  the opencode free endpoint `opencode/mimo-v2.6-flash-free` (same MiMo V2.6
  Flash model, different host, cost 0). This substitution of execution route is
  disclosed here rather than concealed; the review content is an independent
  model assessment of the pinned artifacts. Reports are preserved alongside this
  one.

All checks below are labelled **executed** (actually run on the VPS) or
**reasoning-only**.

## Summary verdict

**The bounded host witness is real but narrow: `partial` overall.** The specific
P→Q mediated move scenario in one hand-built in-memory state machine is
reproducible on this host, the retained latent ceiling is the operative guard in
that exact graph, and Landlock confinement of the worker is genuine. However, the
implementation does **not** establish the general guarantees that the claim /
T11 / Closure §7 imply: no dependent D, single-hop (non-transitive) permission
computation, no cycle/dangling validation, a hardcoded rather than
authority-gated activation, immutability only asserted (never attacked), and a
verifier that detects some-but-not-all tampering. This is **not** evidence of F3
or F5 closure.

## Findings

### F1 — Verifier reproduces PASS against the recorded evidence
- **Verdict:** `supported`
- **Reference:** `verify_l5_write.py` (all 9 checks); `l5-write-raw.json`.
- **Check (executed):** `python3 verify_l5_write.py` → 9/9 PASS, exit 0. The
  source-hash check confirms `sha256(l5_write.py) == 214771793703...5015` matches
  `l5-write-raw.json:source_sha256`; verified independently with
  `sha256sum l5_write.py` → identical.
- **Limits:** The verifier checks selected fields of a JSON document; passing does
  not by itself prove those fields were produced by the pinned source (see F8).

### F2 — Implementation reproduces the recorded outcome on this host
- **Verdict:** `supported`
- **Reference:** `l5_write.py` `main()` / `run_case()`; `l5-write-raw.json`.
- **Check (executed):** Copied `lifecycle/` to `/tmp/l5repro`, ran
  `python3 l5_write.py`. Produced `status: L5-PASS`; all 7 acceptance booleans
  true; effect SHA-256 for the positive case `8732b8a0...0bd06` and mutant
  `fc614537...7b83` matched the recorded values; worker read x
  (`46332d6c...0a`) in all cases.
- **Limits:** This shows the recorded observation is reproducible on this kernel
  (5.15.0-184, Landlock ABI 1). It is one host profile.

### F3 — The post-move write denial is attributable to `latent_ceiling`
- **Verdict:** `supported` (for this constructed graph)
- **Reference:** `l5_write.py` `permissions()` =
  `set(C.grants) & set(P.grants) & set(latent_ceiling)`, invoked at line 54
  (`effect in permissions(st)`).
- **Check (executed + reasoning):** In the `latent_preserved` case, after the move
  `C.parent == 'Q'` and `Q.grants == ['read','write']`. My probe recomputed the
  intersection: with the real parents+latent, effective = `['read']`; if latent
  were dropped (mutant), effective = `['read','write']`. Because the only
  remaining restriction is `latent_ceiling == ['read']`, the denial is provably
  attributable to the latent ceiling, and not to the destination parent.
- **Limits:** Attribution holds only for this two-node graph. `permissions()` does
  not walk ancestors beyond the immediate parent (see F6), so the claim does not
  generalise to deeper containment.

### F4 — Positive control demonstrates a genuine concretely committed effect
- **Verdict:** `supported`
- **Reference:** `l5_write.py` positive case write branch (atomic
  `os.replace` into `effects/`), `effects[].committed_before_ack`.
- **Check (executed):** Rerun produced exactly one effect file with bytes
  `authorized-positive` and a matching SHA-256; `committed_before_ack == true`.
- **Limits:** The effect is mediated and performed by the authority; it does not
  demonstrate the worker itself writing (see F5).

### F5 — Worker-side filesystem write is not exercised by the harness, but the confinement is real
- **Verdict:** `partial`
- **Reference:** `l5_write.py` WORKER script (only calls `ask('write', ...)` over
  the socketpair; never `open(...,'w')`); `l1.py` `confine()` allowing rules only
  for `/usr,/lib,/lib64,/etc/ld.so.cache`.
- **Check (executed):** I built an independent probe using the identical
  `l1.confine` and, inside a confined child, attempted (a) read the accepted
  object, (b) read `/usr/bin/env`, (c) write into a scratch dir, (d) write into
  `/tmp`. Result: accepted-object read `denied:13`, `/usr` read `ALLOWED`, scratch
  write `denied:13`, `/tmp` write `denied:13`.
- **Interpretation:** The worker **cannot** write directly and **cannot** read the
  accepted object directly — so "`write` DENY" is not the whole story; the harness
  simply never offers the worker a direct write route. The write decision is a
  mediator policy decision, not a demonstration that a malicious worker is unable
  to bypass it.
- **Limits:** The probe does not cover descriptor inheritance, `/proc`, or other
  syscall-level bypasses; there is no explicit bypass-attempt case in the recorded
  evidence as F3's route inventory asks for.

### F6 — `permissions()` is single-hop; no transitive ancestor, cycle, or dangling checks
- **Verdict:** `unsupported` (as a general guarantee)
- **Reference:** `l5_write.py` `permissions()` — `p = state.get(c['parent'])`;
  intersects only the immediate parent. The move branch sets
  `state['C']['parent']='Q'` with no cycle/dangling validation and no governing-
  permission check on P or Q.
- **Check (reasoning-only):** Reading the function shows a single parent hop.
  Closure §7 ("Ancestor restrictions constrain descendants", C3/C8) and T11's
  descendant expectation are not represented. No P→Q→… chain, cycle, or dangling
  parent is tested.
- **Follow-up:** Add a multi-level ancestor intersection and structural
  validation, plus a trace where an ancestor restriction must still bind after a
  move.

### F7 — T11 "Include D" (dependent) is not exercised
- **Verdict:** `unsupported`
- **Reference:** T11 row (Phase-I-Verification.md) requires "Include D."
  `l5_write.py` defines only C/P/Q; grep finds no `D`, dependent, or descendant
  handling.
- **Check (executed grep + reasoning):** No D state, no dependent confinement, no
  dependent disposition, no descendant protection across the move.
- **Follow-up:** Add a dependent D whose protection must survive the C move and
  activation, with a negative case where dropping D's restriction exposes it.

### F8 — Activation is a hardcoded state mutation, not an authorized event
- **Verdict:** `unsupported` (as "separately authorized activation")
- **Reference:** `l5_write.py` moves branch lines setting
  `state['active']=True; state['current_ingress']='W1'` and committing an event
  labelled `fresh_authorized_activation` with `actor:'initial-manager'`.
- **Check (reasoning-only + executed inspection):** No authority identity,
  credential, challenge, or protocol gate is checked; the "authorized" activation
  is simply the literal assignment executed inside `run_case`. The label is
  descriptive only.
- **Limits:** Closure §7 requires activation to be "a separate current authorized
  event"; the witness shows the state can be made active, not that an
  unauthorized actor is excluded.

### F9 — Accepted-content immutability is asserted, not tested
- **Verdict:** `partial`
- **Reference:** `l5_write.py` `accepted_x_bytes_unchanged = content.read_bytes()==X`;
  `accepted_x_mutation: 'none'` in `routes`.
- **Check (reasoning-only):** The object file
  `l4/lab/protected/objects/146207...061.bin` is read before and compared after,
  but **no case attempts** to write, rename, unlink, or replace it — by worker or
  mediator. "The accepted content must remain unchanged" is satisfied only
  because nothing ever tries to change it.
- **Follow-up:** Add a case that attempts to mutate accepted x (worker direct, and
  via a forged write request) and show it is rejected with the bytes intact.

### F10 — Verifier detects several syntactic mutations but not all tampering
- **Verdict:** `partial`
- **Reference:** `verify_l5_write.py` checks fixed fields and a source hash; no
  signature, no independent recomputation of the protected object from disk.
- **Check (executed):** In isolated copies I mutated the raw evidence:
  - M1 (safe `C.parent` → `P`): caught (FAIL on "whole move records C under Q").
  - M2 (delete `latent_ceiling`): caught, but by a **KeyError crash** rather than
    a clean verdict (fragile — an unexpected input aborts rather than reporting a
    targeted failure).
  - M3 (safe write result `DENY` → `COMMITTED` with no effect): caught.
  - M4 (flip a mediator `allowed` flag): caught.
  - M5 (mutant write `COMMITTED` → `DENY`, effects emptied): caught.
- **Interpretation:** The verifier is a useful consistency checker, not
  tamper-evident. A pre-tampered JSON that keeps every checked field mutually
  consistent (e.g. altering unchecked metadata or the `routes` prose) would pass.
- **Follow-up:** Recompute the object SHA-256 from disk in the verifier and add a
  signed/Merkle binding between the raw JSON and the executed source.

### F11 — Mutant distinction is meaningful but minimal
- **Verdict:** `supported`
- **Reference:** `run_case(..., mutant=True)` sets
  `latent_ceiling=['read','write']`, allowing the previously forbidden write; the
  safe case keeps `['read']`.
- **Check (executed):** Mutant produced one effect with bytes
  `post-move-forbidden`; safe produced none. The distinction between "restriction
  retained" and "restriction dropped" is observable.
- **Limits:** Only one weakening axis (the latent ceiling) is mutated. Other
  independent weakenings the spec lists (ancestor checking, source binding,
  recoverable-before-ack, complete-domain checking, access-control ordering) are
  not exercised here.

## What the evidence establishes vs. does not

**Established (observed, this host, bounded graph):**
- A mediated read of accepted x succeeds before and after the move.
- With `latent_ceiling=['read']` retained across a P→Q move, a post-move
  post-activation write request is denied and no effect is produced; the denial is
  attributable to the latent ceiling.
- A positive control can perform a `write` that commits a concrete byte effect
  before acknowledgement.
- Dropping the latent ceiling allows the previously forbidden write (mutant).
- The worker process is genuinely Landlock-confined (cannot write, cannot read the
  accepted object directly).
- Accepted x bytes are unchanged at the end of all three cases.

**Not established:**
- Any dependent D behaviour (T11 "Include D").
- Transitive ancestor restrictions, cycle/dangling validation, governing-
  permission checks on the move.
- A real authority-gated activation (it is a literal state assignment).
- Worker-initiated direct write attempts / a concrete bypass attempt per F3's
  route-inventory requirement.
- Immutability under an actual mutation attempt.
- Tamper-evident evidence, or verifier robustness to malformed input.
- Cold recovery, disposal, external-effect contracts, D1/D2 engine-loss
  behaviour, or anything beyond this single in-memory profile.
- Any inference toward full F3 or F5 closure.

## Smallest follow-up needed

1. Add a dependent D case whose protection survives the C move and is exposed when
   its restriction is dropped (T11 "Include D").
2. Make `permissions()` intersect the full ancestor chain and validate
   cycles/dangling parents; add a multi-level case.
3. Replace the hardcoded activation with an actual gated event (authority
   identity + credential) and add a negative case for an unauthorized activation.
4. Add a worker direct-write bypass attempt and an accepted-x mutation attempt;
   show both denied with bytes intact.
5. Make the verifier recompute the object digest from disk and fail cleanly (not
   crash) on malformed evidence; bind the raw JSON to the source cryptographically.

## Additional reviewers

Independent reports are included as `F3-L5-INDEPENDENT-REVIEW-GLM.md` (GLM 5.3
Flash, Phoenix Grove provider) and `F3-L5-INDEPENDENT-REVIEW-MIMO.md` (MiMo V2.6
Flash, executed via `opencode/mimo-v2.6-flash-free` because the Phoenix Grove
subscription daily allowance was exhausted at review time). All three reviewers
independently returned an overall verdict of `partial` on the bounded claim and
independently identified the same core gaps (no dependent D, single-hop
permissions, hardcoded activation, untested immutability, non-tamper-evident
evidence).
