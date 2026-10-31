All reproduction and probing complete. Here is the review.

---

# Independent clean-room review — bounded F3 L5 integration (commit `b49e1f66ddd91e501794f6c9381e1e96c19b096c`)

## 1. Bounded verdict: **PARTIAL**

The T11 behavioral core is genuinely demonstrated and independently reproduces with digest-exact determinism: each of the three cases re-executes an unmodified L4 lifecycle producing real accepted storage (`l5_integrated.py:60-76`; three per-case evidence files differ only in pids/timestamps/temp-roots), the sealed whole move carries C and dependent D from read-only P beneath read/write Q via a distinct authorized record, activation is a separate authorized record, the post-activation worker read returns hash-verified accepted x from the retained protected store, write is denied with zero effects, the weakened-latent-ceiling mutant commits the forbidden write (a sensitive discriminator), the positive control proves non-vacuity, structural controls reject cycle/dangling/unknown-permission states, and the verifier passes both on the packet's raw evidence and on a fresh run. However, the review axis "move and activation are separately and *meaningfully* authorized through a management boundary" is only partially supported: the boundary is a protocol-shape check inside a single trust domain with a compile-time credential constant (disclosed), and it demonstrably does not govern the fixture's own state changes — the positive control's activation commits wholly outside the gate while its event label claims authorization, and every pre-state/mutant configuration is self-authored. Several required discriminating branches of the sealed-move contract (authorized post-move grant unlatching write, sealed-period use attempts, adversarial worker operations, L5-era route bypass probes) are untested, and a latent use-gate weakness (checks only D's own flags) was demonstrated analytically. The bounded result stands as claimed within its declared profile; the management-authorization claim and control coverage are weaker than the T11 framing implies, hence PARTIAL, not PASS.

## 2. Findings (by severity)

**F1 (Moderate-High). Management authorization is nominal, not a boundary, and does not govern the fixture's state changes; the positive control's activation bypasses the gate while claiming authorization.**
- Evidence: 
  - `research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py:77-99` — `manager_roundtrip` authorizes by comparing the request's `authorized_by`/`credential` fields to constants `authorized_by='initial-manager'` and `CREDENTIAL='test-manager-credential-not-a-production-secret'` defined at `l5_integrated.py:10` in the same file/process.
  - `l5_integrated.py:104-105` — both endpoints of the "manager" channel (`a, b = socket.socketpair()`) are created and used by the same runner process; no manager process exists.
  - `l5_integrated.py:100-116` — the entire pre-state authority configuration (P grants `['read']`, C local `['read','write']`, Q/D creation, sealing, `current_ingress=None`) is committed directly at `l4_bootstrap` (`:67-75`, event `l5-bootstrap-from-l4`) and via direct in-memory mutation + `commit` (`:101`, `:111`), never through the gate.
  - `l5_integrated.py:119-128` — the positive control commits `separately-authorized_positive_control_activation` and `positive_control_ingress_current` directly, without any manager exchange.
  - Raw corroboration: `l5/l5-integrated-raw.json` → `cases.positive.management == []` (zero manager round-trips) while `cases.positive.activation.result == 'COMMITTED'` and `cases.positive.activation_event.op == 'separately-authorized_positive_control_activation'`.
- Impact: T11's "after activation read succeeds while write remains denied absent separate authorized grant" is mediated, but "authorized" is only a validated field check inside one trust domain. Every configuration transition that is not the safe/weakened move+activation proceeds outside the boundary; by construction, an actor in that domain (exactly what the mutant does at `:114-116`) can commit arbitrary permission state. The record graph, however, presents these as authoritatively authorized events.
- Counterexample: the packet's own raw evidence — `cases.positive.management` is empty yet the activation record records an "authorized" event; the mutant commit (`unsafe_mutant_drop_latent_restrictions`, record-000009 implicit between move record-000008 and activation record-000010) is an unauthorized widening committed into the same authoritative record history.
- Disposition note: `limits.management_credential` in `l5-integrated-raw.json` discloses "test-only shared secret; no physical manager identity claim", so this is partially disclosed; the undisclosed part is the gate bypass for the positive control and fixture authoring.

**F2 (Moderate, latent — demonstrated analytically, not in the recorded run). The use-time gate checks only D's own `active`/`sealed` flags; ancestor restriction flags and policy/currentness fields are not validated, so an inconsistent state passes the gate.**
- Evidence: 
  - `l5_integrated.py:138-140` — `enabled = valid and current_ingress=='W-L5' and D.active and not D.sealed` uses only D's flags; the permission chain (`permissions`, `:46-53`) walks grants/ceilings but not sealed/active ancestry.
  - `l5_integrated.py:31-45` — `graph_valid` enforces only shape (unit set, ids, grants ⊆ {read,write}, parents, acyclicity). It ignores the `policy` key and permits contradictory state such as `C.active == True and C.sealed == True` simultaneously.
  - Counterexample (this review's probe, function-level, no packet edits): starting from the widened state recorded by the mutant commit (ceilings `['read','write']` for C and D), setting `C.sealed = True` while D remains active leaves `graph_valid = True`, `gate_enabled = True`, and `allowed(write) = True` under the verbatim source expression — a sealed parent with authority descendants exposed. The same probe shows `graph_valid` accepts a foreign `policy` value and an active+sealed C.
- Impact: Closure §7 "Narrow/revoke/seal … Ancestor restrictions constrain descendants" is only realized for grant/ceiling dimensions; if a future authorized seal event left descendants active, protected writes would continue. Not exercised because the bounded profile exposes no post-activation seal operation; classify as latent design weakness, not a demonstrated failure of the recorded evidence.

**F3 (Moderate, untested branch). T11's "write still fails *unless a separate authorized grant explicitly changes it*" is untested.**
- Evidence: `l5_integrated.py:100-161` defines only three cases (`positive`, no move; `safe`, move; `weakened`, move+unauthorized ceiling drop); none demonstrates an authorized grant that legitimately restores write after the move, and `l5-integrated-raw.json` has no such case.
- Impact: The mutant (`:114-116`) correctly proves the decision is sensitive to the ceiling and that write can commit through this machinery, but only via an *unauthorized* direct mutation. There is no evidence the denial is a legitimate latching property that a real authorized grant could lift — i.e., the "unless" side of T11's contract, and Closure §7's activation rule ("Historical grants … insufficient", implying a *current* grant suffices) is untested. Limitation of coverage, not a defect in the recorded behavior.

**F4 (Low-Moderate). Verifier weaknesses — self-consistency only, with missing cross-checks.**
- Evidence: `verify_l5_integrated.py:11-29`. Omissions, all checkable from data present in `l5-integrated-raw.json`:
  - It does not cross-check `mediator_checks[*].record_sha256` against the activation record hash (the packet's own data shows the positive case diverges: mediator record-000009 sha `2ce2b93f…` vs activation record-000008 sha `d294ecb2…`, consequence of the torn two-commit activation in F6), while the safe/weakened cases tie exactly.
  - The integrated raw contains no full final-state dump per case (unlike `l5-baseline-discriminator-raw.json`, which embeds `current_state`), so the verifier cannot independently recompute `D_effective`, `old_effective`, or the retained ceilings; it trusts the runner's derived fields (e.g., `verify_l5_integrated.py:20,25`).
  - There is no check of record-chain continuity (`CURRENT` lineage record-000006 → 000007 → 000008 → …) and no revalidation of the `policy` label after the L5 extension (`raw` embeds the L4 policy check only in `l4_raw`; `graph_valid` ignores `policy`).
- Impact: the verifier would pass a raw file whose derived permission fields were inconsistent with an actual state; cross-checks that the data already permits were left out. (Mitigating: my independent reproduction reproduced every state-derived digest exactly, see §4.)

**F5 (Low-Moderate). L5-era adversarial route/bypass coverage is inherited, not re-established.**
- Evidence: the L5 worker (`l5_integrated.py:11-17, 135`) only issues `read_x`/`write_d` over the inherited socket; it never probes the filesystem, never sends malformed/spoofed ops (e.g., `authorize_move` on the worker channel), and no old-holder activity runs during the L5 phase. Direct-path denial evidence (`errno 13`) exists only inside the embedded L4 run (`l5-integrated-l4-*.json` → `w1_missing_grant.paths`, pre-grant) and earlier phases. `limits.routes` in `l5-integrated-raw.json` discloses the narrow route scope.
- Impact: "reads come from verified accepted storage" and "complete mediation" are true for the mediated path, but the F3-style "bypass attempt for every enabled route" was not performed in the L5 phase itself; non-mediated-route claims rest on L1/L3/L4 evidence and Landlock (ABI 1) being in force at worker spawn (`preexec_fn=l1.confine`, `l5_integrated.py:135`). Scope limitation, disclosed in `limits`.

**F6 (Low). The positive control's activation is a torn two-commit transition with an inconsistent-state window.**
- Evidence: `l5_integrated.py:123-128` — commit `separately-authorized_positive_control_activation` occurs while `current_ingress` is still `None`; ingress `W-L5` is set at `:126` and persisted only by a second commit `positive_control_ingress_current` (`:128`). Corroborated in `l5-integrated-raw.json` (see F4 first bullet: activation record sha ≠ mediator-check record sha). 
- Impact: between the two commits the committed record has all units active but no current ingress; no worker runs in that window, so no effect occurred, but the "whole semantic result" of activation is split across two ungated records — inconsistent with Closure §7 "Replace … at one declared whole commitment" and with the safe case, where the gate commits ingress+activation atomically (`:95-97`).

**F7 (Low). D's accepted content reuses C's y metadata without its own acceptance event.**
- Evidence: `l5_integrated.py:70-71` — D's `accepted_contents` is `[y]`, where `y = C.accepted_contents[-1]`; the metadata's `provenance.actor` is `worker-ingress-W2`, belonging to C's acceptance (visible in `l5-integrated-l4-*.json` events). No acceptance event for D exists anywhere in the record history.
- Impact: fixture semantics only (D's read path is never used; the D write is an external effect into `root/effects` at `l5_integrated.py:144`, which is likewise a shared unit-less sink rather than a D-bounded location). No T11 property depends on it, but the imported metadata could confuse provenance claims if reused.

**F8 (Low). Misleading field naming.** `l4_record_before_l5` in the raw (`l5_integrated.py:149`, via `:76`) is record-000007, which is already the L5 extension record `l5-bootstrap-from-l4`; the actual L4 final state is record-000006, evidenced in the embedded `l4_raw.final_independent_readback.record`. Cosmetic scope mislabel.

## 3. T11 / Closure §7 support matrix

| Element | Status | Basis |
| --- | --- | --- |
| Pre-state: C local read/write, P restricts to read (T11 premise) | Supported (as fixture premise) | `l5_integrated.py:67-68, 101`; evidenced post hoc by safe `move_event.old_effective == {C:['read'], D:['read']}` in raw. Established by direct fixture commit, not the management channel (F1). |
| Sealed whole move C→Q, structural validation, no cycles/dangling | Supported | Gate preconditions `l5_integrated.py:83-91`; move record-000008 committed; structure controls raw `structural_controls` all true; reproduced deterministically (§4). |
| Descendant D represented and protected across the move | Supported | `l5_integrated.py:71, 86-90`; raw `dependent_D` parent C / depends_on C, safe `D_effective ['read']`; D ceiling recomputed before re-parent (`:86-87`). |
| Latent permission retained/narrowed, not widened (§7 move row; C8) | Supported for the gated path | Ceilings = pre-move path intersection (`:86-87`); mutant proves sensitivity (raw weakened case: write COMMIT with effect `forbidden-after-move`). Unsupported-grant-drop alternative representation not exercised; ceiling field added at move (`H7`-style policy-version pinning absent — `graph_valid` ignores `policy`). |
| Read succeeds after activation, from verified accepted storage | Supported | `verified_content` (`l5_integrated.py:23-30, 142`); raw read sha == L4-expected x sha (`1462070e…`), bytes hex == `F3-lifecycle-x-v1\n`; provenance retained; reproduced. |
| Write denied absent separate authorized grant | Supported (one-sided) | Raw safe case: DENY, effects empty, no mutation of accepted bytes. The authorized "unless" branch untested (F3). |
| Move and activation separately authorized as distinct whole records | Partially supported | Distinct committed records 000008/000009 with independent shas; but authorization is an in-process constant-credential field check, and the positive control's activation bypasses the gate entirely (F1). |
| Activation with recomputed full-path constraints at use | Supported | Per-request reload of the committed record and recomputation (`l5_integrated.py:138-146`); constraint recomputation demonstrated per use. Ancestor-`sealed`/`active` flags and policy not part of the checked view (F2). |
| Non-vacuity (positive control with real effect) | Supported | Raw positive case: write COMMIT, concrete effect bytes `authorized-positive`, sha `8732b8a0…`. |
| Denial has no protected effect; denial mutates nothing | Supported | Unauthorized management denial leaves state byte-identical (`l5_integrated.py:104-107`, raw `management_denial.state_unchanged`); safe write DENY produced no record/effect. |
| AC/C13 policy ordering, T12 races, concurrent management, old-holder exclusion in the L5 era, stronger-profile items | Unsupported / out of L5 scope | Not attempted within the packet; partly covered by L1–L4 lineage evidence embedded in `l4_raw` (`w1_after_fresh_activation` IOERROR from L4). Do not infer from this packet. |

## 4. Reproduction commands and observed results

Performed in a disposable copy; the packet tree was not modified.

```bash
# 1) disposable copy
mkdir -p /tmp/opencode/asc-l5-repro
cp -r /tmp/ases-f3-l5-review-packets-20261031/glm /tmp/opencode/asc-l5-repro/glm
cd /tmp/opencode/asc-l5-repro/glm/research/phase-i-protected-work-unit-f3/lifecycle/l5

# 2) read-only verifier on the packet's raw observations
python3 verify_l5_integrated.py                    # -> 19/19 PASS, exit 0

# 3) reproduce the runner (3 fresh L4 bootstraps + safe/weakened/positive cases)
python3 l5_integrated.py                           # -> exit 0, status L5-INTEGRATED-PASS

# 4) reproduce the L4 base and the earlier l5_write discriminator baseline
cd ../l4 && python3 l4.py                          # -> exit 0
cd ../l5 && python3 l5_write.py                    # -> exit 0
python3 verify_l5_write.py                         # -> 9/9 PASS on the fresh run (writes l5-write-raw.json in the copy)
python3 verify_l5_write.py l5-baseline-discriminator-raw.json   # -> 9/9 PASS on the packet's recorded baseline
```

Observed results:
- `verify_l5_integrated.py` on the packet raw: all 19 checks PASS (exit 0), including source digest match (`daf24f8fce53…041d21156` = sha256 of the packet's `l5_integrated.py`).
- Fresh runner run: identical status; `old/acceptance == new/acceptance` (all ten checks true); identical structural controls; **every state-derived digest identical** to the packet raw despite fresh pids/temp-roots — e.g. safe move record sha `507fdbbd13eb03d2…6688`, safe activation record sha `6cabac88a4eef1…e2c`, positive effect sha `8732b8a0…bbd06`, weakened effect sha `b4ef82a3…4cea781`, `old_effective == {C:['read'], D:['read']}` in both — records embed no pids/timestamps and the fixture is fully deterministic.
- The three per-case L4 evidence files (`l5-integrated-l4-{positive,safe,weakened}.json`) differ per diff only in pids, nanosecond timestamps, and temp roots — i.e., three genuinely independent L4 executions, matching `l5-baseline-l4-raw.json` in events and digests.
- `verify_l5_write.py` passes on both the fresh reproduce and the packet's recorded `l5-baseline-discriminator-raw.json`; `l5_write.py` sha `214771793703…4915015` matches that raw's `source_sha256`.
- Function-level probe (imports only, no packet edits): confirmed F2 — with widened ceilings and `C.sealed=True`, `D.active`, the verbatim gate expression yields `enabled=True, allowed(write)=True`; `graph_valid` accepts a foreign `policy` and `C.active ∧ C.sealed`.

## 5. Provenance / independence statement and explicit limits

- **Reviewer route:** OpenCode free route on OpenCode Zen; exact model ID `opencode/glm-5.3-flash-free` (GLM family via the OpenCode free tier), Linux host kernel `5.15.0-184-generic`, Python `3.10.12`. This route is distinct from the implementation author model.
- **Implementation provenance basis:** `IMPLEMENTATION-LAUNCH-PROVENANCE.txt` — target commit `b49e1f66ddd91e501794f6c9381e1e96c19b096c`, branch `research/f3-l5-lifecycle-integration-20261031`; directly authored in an assistant coding session on GPT-6 Luna; the only recorded delegated invocation (Codex CLI v0.157.1, `glm-5.3-flash` via Phoenix Grove provider `pgs2`) failed with HTTP 402 before producing any implementation output; no successful delegated implementation output is recorded. I did not infer implementation authorship from that failed call. I note for transparency only that my reviewer route's model shares the GLM family with the failed delegation route, but that call emitted no implementation artifacts and has no bearing on authorship or on my verdict.
- **Clean-room discipline:** this review used only the packet's source, evidence, spec (Phase-I-Verification.md at T11; Phase-I-Closure.md at §7), and provenance files. No implementation result/obstruction reports, no prior reviews, and no external repository state (e.g., the superseded `5c03a425…` commit) were consulted. No packet file was edited; the runner was reproduced only inside a disposable `/tmp` copy; the two source-level probes were written outside the packet and import it read-only.
- **What was demonstrated vs. not:** raw-recorded behavior and fresh reproduction support only the bounded T11/§7 subset enumerated in §3. Not tested and **not** covered by this verdict: any post-move authorized grant widening (T11 "unless" branch), sealed-period use attempts, spoofed/unauthorized worker operations, old-holder/new-bearer exclusion in the L5 phase, concurrent or racing management transitions (T12), power-loss/rollback durability, D3 quiescence, AC/C13 policy ordering, sibling/empty-unit and other C1–C13 family fixtures, and any general graph validator beyond the hardcoded four-unit fixture.
- **No closure inference:** this review does **not** imply full F3/F5 closure. The packet's own `limits.does_not_claim = "full F3/F5 closure"` is respected. The bounded L5 integration result is, as graded, PARTIAL: the behavioral core of T11 stands on reproduced, deterministic evidence; the management-authorization claim is materially weaker than its records' wording, and the control surface has the gaps in §2.