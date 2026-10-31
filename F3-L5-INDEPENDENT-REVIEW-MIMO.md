# L5 Write/Mediated Move Witness — Bounded Claim Review

**Claim under review:** A trusted authority mediates child C's read/write. C has local read/write. Pre-move parent P permits read but not write; destination Q permits both. After sealed P→Q move + separately authorized activation: old read-only restriction still blocks writes; accepted x still readable; positive control shows mediated write can succeed; weakened restriction allows the previously forbidden write; accepted content stays unchanged.

**Overall verdict: partial**

The executed host evidence establishes the core bounded behavior for the fixed single-child C/P/Q topology: a positive control commits a mediated write under full grants; after a sealed move under read-only P the latent ceiling retains `['read']` and a post-activation write is denied by the mediator; a mutant that drops the ceiling commits the same write with a concrete effect; and post-move reads return the exact accepted x bytes/hash. These are genuine executed differential results, with write-denial attribution to `latent_ceiling` (not merely parent grants) established by the mutant. However, several general aspects of the claim and T11/F3-adjacent expectations are only partially realized or untested: activation is an inline hardcoded transition rather than a separately authority-gated event; `permissions()` intersects only the direct parent (not transitive over a full ancestor chain, no cycle-safety code); T11's dependent D is never exercised; Landlock confinement is applied but never negatively tested via a worker direct-write attempt; accepted-content immutability is asserted without any mutation attempt against the object; and evidence tamper-detection is self-consistency binding, not independent re-execution or authenticated records. F3/F5 closure is not inferred from this bounded witness.

---

## Findings

### F-L5-1. Write-denial is attributable to latent_ceiling, not another guard
- **Verdict:** supported
- **Finding:** In the safe moved case, C.grants=`['read','write']`, parent Q.grants=`['read','write']`, activation checks show active/sealed/ingress all satisfied, and the only failing membership is `'write'` not in `permissions()` result `['read']` (which equals C.grants ∩ Q.grants ∩ latent_ceiling). The mutant that sets latent_ceiling to `['read','write']` after the same move commits the write with a concrete effect hash and `allowed=true`, isolating latent_ceiling as the differential cause of denial.
- **Evidence:** `l5_write.py` — `permissions()` (lines defining intersection with `latent_ceiling`); `run_case` move branch setting `latent_ceiling` from `old_effective` vs mutant `['read','write']`; recorded `actual_checks` in `l5-write-raw.json` (`latent_preserved.actual_checks[1].allowed=false`, `effective=["read"]`; `unsafe_mutant.actual_checks[1].allowed=true`, write COMMITTED with `sha256=fc614537...`); `verify_l5_write.py` checks "weakened ceiling admits same post-move write".
- **Check type:** executed (recorded raw json + independent verify consistency checks) and reasoning (code attribution of the guard).
- **Limits:** Attribution holds for this exact single-parent topology and mediator implementation only. No alternate enforcement layer (Landlock write path, separate authority process) is differentially exercised, so "vs some other guard" is established by code inspection of `allowed` and the mutant, not by a multi-layer ablation.

### F-L5-2. Worker never attempts a direct filesystem write; all writes are mediator-side
- **Verdict:** supported
- **Finding:** The worker source only opens an inherited socketpair fd, issues `read_x`/`write` ops, and prints results. No worker code opens, creates, or replaces any file. The only filesystem write in the successful/committed paths is the mediator's atomic replace under `root/effects/` in `run_case`, after the `allowed` check. The recorded routes state `worker_direct_filesystem: "Landlock confined; no target or accepted-object fd passed"` — the "no fd passed" portion is true from `pass_fds=(schild.fileno(),)`.
- **Evidence:** `l5_write.py` — inline `WORKER` source string; mediator write branch (`target=root/'effects'/'write-effect.bin'` ... `os.replace`); `l5-write-raw.json` routes per case.
- **Check type:** executed (code path observation in recorded structure) + reasoning (static read of worker source).
- **Limits:** The worker not attempting a direct write means the claimed Landlock confinement is never negatively tested in this witness (see F-L5-7). The absence of a direct-write attempt is consistent with the design, not a demonstrated denial of one.

### F-L5-3. T11 "Include D" dependent is not exercised
- **Verdict:** unsupported
- **Finding:** T11 requires "Include D" (a dependent). The L5 state graph contains only C, P, and Q. No dependent work unit D, no descendant under C, and no second dependent effect or disposition is created, moved, or observed. The bounded claim's own text does not mention D either, but the verification-plan requirement is unmet by this witness.
- **Evidence:** `l5_write.py` — `run_case` state initialization (`'C'`, `'P'`, `'Q'` only); no `D` key or dependent lifecycle anywhere in the file or `l5-write-raw.json`.
- **Check type:** reasoning-only (absence inspection of code and raw evidence).
- **Limits:** None material for the presence of D; this is a hard gap against T11's "Include D" clause, though the core C/P/Q move property is still testable without it.

### F-L5-4. Activation is not truly authority-gated; it is a hardcoded inline transition
- **Verdict:** partial
- **Finding:** After the sealed move, `run_case` directly mutates `state['sealed']=False`, `state['active']=True`, `state['current_ingress']='W1'` and commits a `fresh_authorized_activation` event with hardcoded `actor='initial-manager'`. There is no separate control channel, no credential/authorization check, and no distinct authority process for activation — the same parent test process that performed the move also performs and "authorizes" activation in-line. The move and activation are separate commits with distinct record hashes, which satisfies "separately recorded" but not "separately authorized" in the sense of a distinct gating mechanism (contrast L1's admin socket `activate` op handled by a separate authority subprocess).
- **Evidence:** `l5_write.py` — `run_case` move branch: `state['sealed']=False; state['active']=True; state['current_ingress']='W1'` then `commit(..., {'op':'fresh_authorized_activation','actor':'initial-manager',...})`; compare `l1.py` AUTH loop with separate `ac`/admin socket for `activate`. Recorded `activation_record_sha256` distinct from `move_record_sha256` in all moved cases.
- **Check type:** executed (recorded event sequence and distinct hashes) + reasoning (static inspection of the activation code path — no authorization predicate is evaluated).
- **Limits:** Within this harness, activation is effectively guaranteed by construction, not by a tested authority gate. A regression that allowed activation without a grant would not be caught by this witness.

### F-L5-5. permissions() is not transitive over ancestors and has no cycle-safety
- **Verdict:** partial
- **Finding:** `permissions(state)` intersects C.grants with exactly one parent (`state.get(c['parent'])`) and with C's own latent_ceiling. It does not walk a full ancestor chain, does not consult grandparent or higher restrictions, and has no visited-set or acyclicity check. For the fixed topology used here (C→P or C→Q, where P and Q have no parent), this yields the correct full-path result and the move correctly captures `old_effective` as the pre-move single-level intersection. The spec's ancestor-restriction and cycle-avoidance requirements (T11 / §7 move semantics) are not implemented or tested beyond this one-level case.
- **Evidence:** `l5_write.py` — `permissions()` body (`p=state.get(c['parent']); if p is not None: path &= set(p['grants'])`); state initialization and move only reassign `parent` between `P` and `Q`; no multi-node ancestor chain or cycle appears in any recorded case.
- **Check type:** reasoning-only (static analysis of `permissions()` and state shape) with executed confirmation for the one-level case.
- **Limits:** Supported only for the bounded single-parent graph actually exercised. Deeper containment, diamond/cyclic references, and reparenting through intermediate nodes are untested and, by code inspection, would be mishandled or would loop only if parent pointers formed a chain longer than one hop (currently they do not, so no infinite recursion is triggered — there is simply no recursion).

### F-L5-6. Accepted-content immutability is weakly tested (assertion, not adversarial)
- **Verdict:** partial
- **Finding:** Content immutability is checked by (1) an `assert content.read_bytes()==X and sha256==EXPECTED` at case start against the L4 lab object path, and (2) a post-case boolean `accepted_x_bytes_unchanged` comparing the same file to the in-module constant `X`. The worker never receives a file descriptor to the accepted object or the effects directory; reads are served from the module constant `X` in the mediator without re-reading the on-disk object at request time; and no case attempts to mutate the accepted object and observes failure. The verify script confirms the hash constants match across all three cases but does not introduce a mutation attempt either.
- **Evidence:** `l5_write.py` — `assert content.read_bytes()==X...`; mediator `read_x` reply uses `X.hex()`/`EXPECTED` constants, not a file re-read; `routes.accepted_x_mutation: "none"`; `verify_l5_write.py` check "accepted x was unchanged in all cases".
- **Check type:** executed (byte/sha equality checks recorded as true in all three cases) + reasoning (no mutation attempt exists in worker or mediator code).
- **Limits:** "Unchanged" here means "not written by this harness," which is nearly vacuous given no component holds a writable path to the object. A real mutation-then-detect test is absent.

### F-L5-7. Landlock confinement is real code and applied, but never negatively tested in this witness
- **Verdict:** partial
- **Finding:** `preexec_fn=l1.confine` is used for every worker spawn; `l1.confine` creates a Landlock ruleset (`HANDLED_FS`), adds read-only rules for `/usr`, `/lib`, `/lib64`, `/etc/ld.so.cache`, sets `PR_SET_NO_NEW_PRIVS`, and calls `landlock_restrict_self`. The raw record shows `landlock_abi: 1` and kernel `5.15.0-184-generic`, indicating the syscall path executed without raising. However, unlike L1's worker (which attempted direct opens of `CURRENT`, `source/candidate-x.bin`, and a symlink and recorded denials), the L5 worker never attempts any direct filesystem access, so there is no executed proof that Landlock denies a worker-side write to `effects/` or the accepted object in this witness.
- **Evidence:** `l5_write.py` — `subprocess.Popen(..., preexec_fn=l1.confine, ...)`; `l1.py` — `confine()`/`add_rule()` Landlock implementation; `l5-write-raw.json` — `"landlock_abi": 1`; routes claim `worker_direct_filesystem: "Landlock confined;..."` without a corresponding negative observation.
- **Check type:** executed (confine invoked, abi probe returned 1) + reasoning (absence of any worker direct-access attempt in L5 code and raw json).
- **Limits:** Confinement is present and active at spawn, but the bypass-attempt obligation (F3 route inventory) is unmet for L5's worker; the "Landlock confined" route label is an assertion of configuration, not of an observed denial.

### F-L5-8. Evidence tamper-detection binds raw json to source file hash but is not independently re-executed or authenticated
- **Verdict:** partial
- **Finding:** `verify_l5_write.py` recomputes `sha256(l5_write.py)` and compares to `source_sha256` in the raw record; cross-checks effect bytes/hex/sha256 self-consistency; checks that each `actual_checks` entry's `record_sha256` equals the case's `activation_record_sha256`, that parent/ingress/worker_pid are consistent, and that move/activation event structure matches expectations. This detects accidental corruption and naive single-field edits. However, the verify script does not re-run `l5_write.py`; the record hashes are sha256 of state files whose contents are also listed/derivable inside the same json (self-referential); there is no MAC, signature, or external log; and a forger who edits case results and recomputes the internal hashes (while leaving the on-disk `l5_write.py` untouched so `source_sha256` still matches) would pass all verify checks.
- **Evidence:** `verify_l5_write.py` — first check `hashlib.sha256(Path(__file__).with_name('l5_write.py').read_bytes()).hexdigest()==d['source_sha256']`; subsequent structural/byte-consistency checks; no subprocess re-execution of the witness; `l5-write-raw.json` internal `record_sha256`/`activation_record_sha256` fields.
- **Check type:** executed (verify script's checks are specified to run against the raw json and are internally consistent with the recorded values) + reasoning (no re-execution or asymmetric integrity mechanism exists).
- **Limits:** Adequate against accidental corruption and against edits that break source-hash or byte/hash cross-links; not adequate against a coordinated forgery of the raw json.

### F-L5-9. Positive control: mediated write can succeed under full grants
- **Verdict:** supported
- **Finding:** With P.grants=`['read','write']`, C.grants=`['read','write']`, latent=`['read','write']`, and active/sealed/ingress satisfied, the mediator commits the write: one effect file with `bytes_hex` decoding to `authorized-positive`, sha256 `8732b8a0...`, `committed_before_ack: true`, and worker observation `write.result == COMMITTED`. The verify script independently confirms the positive configuration and effect byte/hash consistency.
- **Evidence:** `l5_write.py` — positive `run_case(parent_grants=['read','write'])`; `l5-write-raw.json` — `positive.effects`, `positive.worker_observation.write`; `verify_l5_write.py` — "positive configuration..." and "positive effect bytes/hash..." checks.
- **Check type:** executed.
- **Limits:** The positive control is a single request/response pair in the same harness; no concurrency, interruption, or cross-process authority variation is exercised.

### F-L5-10. Weakened restriction (dropped latent ceiling) admits the previously forbidden post-move write
- **Verdict:** supported
- **Finding:** The mutant case performs the identical sealed move (P read-only → Q read/write, same activation sequence) but sets `latent_ceiling=['read','write']` instead of the captured `old_effective=['read']`. The post-activation write is allowed, a concrete effect is committed (`sha256=fc614537...`, `committed_before_ack: true`), and the acceptance flag `mutant_forbidden_write_succeeded` is true. This demonstrates the old read-only restriction is load-bearing and that weakening it re-enables the forbidden write — the required weakened-variant detection.
- **Evidence:** `l5_write.py` — `mutant=True` path in move branch; `l5-write-raw.json` — `unsafe_mutant.current_state.C.latent_ceiling=['read','write']`, `write.result=COMMITTED`, `effects` present; `verify_l5_write.py` — "weakened ceiling admits same post-move write and concrete effect is observed"; `acceptance.mutant_effect_detected` / `mutant_forbidden_write_succeeded` both true.
- **Check type:** executed.
- **Limits:** Only one weakened variant (ceiling dropped to full read/write) is tested; no other mutation dimensions (e.g., re-activating under a different ingress, forging a grant event) are explored.

### F-L5-11. Accepted x remains readable after move + activation with exact bytes/hash
- **Verdict:** supported
- **Finding:** In the safe moved case, the worker's post-activation `read_x` returns `OK` with `bytes_hex` equal to `46332d6c6966656379636c652d782d76310a` (`b'F3-lifecycle-x-v1\\n'`) and `sha256` equal to `1462070e...`, matching the independently pinned constants in `verify_l5_write.py` and the on-disk L4 object hash. The `actual_checks` entry for the read shows `allowed=true` against the moved current record (`parent='Q'`, `record_sha256` equal to the post-move activation hash).
- **Evidence:** `l5_write.py` — `read_x` reply construction from `X`/`EXPECTED`; `l5-write-raw.json` — `latent_preserved.worker_observation.read` and `actual_checks[0]`; `verify_l5_write.py` — "fresh ingress reads exact retained x then write is denied without effect" check with pinned `x`/`xhash` constants.
- **Check type:** executed.
- **Limits:** The read is served from the module constant `X`, not by re-reading the retained object file at request time, so this demonstrates the mediator will acknowledge a matching read after move, not that the on-disk accepted object was re-fetched and re-validated post-move (see F-L5-6).

### F-L5-12. Move sequencing seals before reparenting and captures the old effective set
- **Verdict:** supported
- **Finding:** In the move path, the state is first marked `sealed=True, active=False, current_ingress=None`; `old_effective=sorted(permissions(state))` is computed under the still-old parent P; then latent_ceiling is set from that captured value (or the mutant), parent is reparented to Q, and a `sealed_whole_move` event records `from='P'`, `to='Q'`, `captured_old_effective=['read']`, and the mutant flag. Only after a separate commit is the state re-activated. Recorded events and hashes in all three cases match this sequence.
- **Evidence:** `l5_write.py` — move branch order of operations; `l5-write-raw.json` — `latent_preserved.current_state.events` (initialize → sealed_whole_move with `captured_old_effective: ["read"]`, `mutant_dropped_latent: false` → fresh_authorized_activation); distinct `move_record_sha256` vs `activation_record_sha256`; `verify_l5_write.py` "whole move records C under Q..." check.
- **Check type:** executed.
- **Limits:** Sequencing is enforced only by the linear code path in `run_case`; no race, interruption, or partial-commit recovery (T07/T12 territory) is exercised here.

### F-L5-13. Mediation model is the parent harness process, not a separate trusted authority process
- **Verdict:** partial
- **Finding:** All authorization decisions, state commits, and effect writes occur in the same `run_case` function on the parent test process (authority_pid). Unlike L1, there is no separate authority subprocess with its own socket, commit loop, and state-file discipline; the "trusted authority" of the claim is instantiated as the test harness itself. This is sufficient to observe mediated allow/deny behavior and atomic effect commits, but it weakens the independence of the "trusted authority" premise relative to a standalone authority process.
- **Evidence:** `l5_write.py` — single-process `run_case` holding state, `commit()`, permission checks, and mediator writes; authority_pid equals the parent; contrast `l1.py` `subprocess.Popen(... '--authority' ...)` with separate state/commit loop. `l5-write-raw.json` — one `authority_pid` per case, equal to the process that also produced the raw record.
- **Check type:** executed (pid fields, single-writer code path) + reasoning (process topology inspection).
- **Limits:** Acceptable for a bounded host witness of mediated semantics; does not by itself establish that an independently running authority would behave identically under loss, restart, or adversarial worker behavior.

---

## Coverage of required evaluation points

| Point | Verdict | Summary |
|---|---|---|
| (a) write-denial attributable to latent_ceiling vs other guard | supported | Mutant differential isolates latent_ceiling; active/sealed/ingress guards are satisfied in the denied case. |
| (b) worker direct filesystem write vs mediator-side only | supported | Worker only sends socket requests; sole committed writes are mediator atomic replaces under `effects/`. |
| (c) T11 "Include D" dependent exercised | unsupported | No D or any dependent exists in state, code, or raw evidence. |
| (d) activation authority-gated vs hardcoded | partial | Separate recorded activation commit exists, but the transition is inline in `run_case` with a hardcoded actor string and no authorization predicate. |
| (e) permissions() transitive over ancestors / cycle-safe | partial | One-level parent intersection only; correct for the fixed C→{P,Q} graph, no full ancestor walk, no cycle guard. |
| (f) accepted content immutability actually tested | partial | Byte/sha equality asserted and recorded; no mutation attempt, and reads are served from a module constant, not a re-read of the object. |
| (g) Landlock confinement real | partial | `confine()` applied at spawn, abi=1 recorded; no worker direct-access/denial attempt in this witness to positively confirm confinement. |
| (h) evidence tamper-detection adequate | partial | Source-hash binding and internal byte/hash/record cross-checks detect corruption and naive edits; no re-execution or authenticated record against coordinated forgery. |

## What this witness does NOT establish (explicit non-inferences)

- No claim of F3 (complete protected boundary, full route inventory with bypass attempts for every route) or F5 closure: the F3 route inventory's bypass obligation is unmet for the worker direct-write route, and no full live sequence (create → grant → accept x → replace ingress → kill authority → cold recover → move → dispose → remove) is present here.
- No general guarantee for multi-level containment, cycles, concurrent move/activation races, interrupted disposition, or engine/process loss.
- No assertion that the mediator process itself is tamper-proof, separately supervised, or recoverable across loss.
- No external-effect or network-ingress coverage.
