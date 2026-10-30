---
title: Independent L5 source audit — mediated latent-write move
program: Phase I Protected Work Unit
layer: Research evidence
document_type: Independent review
status: Active
authority: Reviewer-generated
review_target: rock-solid-sites/ASES@fb34deca9ea8c1bf04ec808052b39d7521040290
review_branch: review/phase-i-f3-l5-source-audit-20261030-gemini35flash
---

# L5 independent source audit — review packet

This is an independent, read-only falsification pass over the frozen L5 witness. It does not modify target files, exp1/run/, recovery snapshots, or builder-owned raw evidence. Original committed observations remain untouched; all mutation tests used disposable copies in /tmp/opencode.

## Verdict summary

- **Overall: PARTIAL.** The bounded host witness genuinely implements the nonvacuous latent-write discriminator and positive/weakened cases. It does not establish accepted-byte *storage* provenance or historical continuity with the L4 Work Unit; those are unsupported in the current source.
- **Narrow claim (host profile only): PARTIAL with a material caveat.** Observed writes are real and discriminated; accepted x is echoed from a compile-time constant, not read from the post-move accepted object.
- Results are host/profile evidence only. They do not establish F3 or F5 completion.

## Reviewer execution and context

- **Host:** Linux IT3812, kernel `5.15.0-184-generic`, Python `3.10.12`, Landlock ABI `1`.
- **Target commit:** `fb34deca9ea8c1bf04ec808052b39d7521040290` (pinned F3 commit).
- **Review branch:** `review/phase-i-f3-l5-source-audit-20261030-gemini35flash`.
- **Materials read as framing:** the frozen packet at `l5/INDEPENDENT-SOURCE-AUDIT-PACKET.md`. Builder `RESULT.md` and `OBSTRUCTION.md` were encountered during exploratory file listing before the independent verdict; final classifications below are based on source/raw evidence and independently recomputed checks. Treat the review as technical verification, not a different-model-family F5 cross-family review.
- **External model family:** none was launched. This is an interactive technical verification.

## Hashed frozen materials

| Artifact | SHA-256 |
|---|---|
| `lifecycle/l1/l1.py` | `000359c5f40a6d560940c356f3e4b08d8ce88e88e45cdf8ba7af9e8afe8d46f2` |
| `lifecycle/l4/l4.py` | `338c8bfed66716c4364d9497e1a49dc4bafb307167ad38db55d9884b07659694` |
| `lifecycle/l5/l5_write.py` | `214771793703ad7d2cce234d166ce8c9909a5a4ada7f872c65a1b13054915015` |
| `lifecycle/l5/verify_l5_write.py` | `b1e226b7f100b3749cfbbb9f41852288c23af04e2a1491eb38d079d12031d255` |
| builder raw evidence `l5-write-raw.json` | `a03521863a6dd5ebce55eadb057467a1479e90d13ca526a4607ac2fb52f5d83b` |
| independent rerun raw evidence | `e01bb6c7de590036d645e880324d38abc82185b310a56b29ff8daa0aa133d914` (differs by PID/temp paths; logical acceptance identical) |

## Independent reproduction

Commands executed in an isolated copy (`/tmp/opencode/l5review`):

```sh
python3 -m py_compile l5_write.py verify_l5_write.py
timeout 30s bash -c 'ulimit -v 524288; python3 l5_write.py > /tmp/opencode/l5review/l5-write-raw.json'
python3 verify_l5_write.py l5-write-raw.json
```

Results: compile PASS; run `status=L5-PASS`; verifier emitted 9 `PASS` with exit status 0.

Builder raw evidence and independent rerun both report:

- `status=L5-PASS`
- acceptance: positive write, moved read, moved write denial, mutant forbidden write, mutant effect detected, content unchanged, check count all `true`.
- Landlock ABI `1`, Python `3.10.12`, kernel `5.15.0-184-generic`.
- 3 cases, 2 worker requests per case, outer timeout 20 s, VM 524288 KiB.

## Required independent checks

### 1. Nonvacuous discriminator — supported (bounded)

- Single write operation in all cases: the worker script always issues `ask('write', payload=...)` (`l5_write.py:15-17`, `WORKER` body). The mediator maps only `read_x -> read` and `write -> write` (`l5_write.py:54`).
- H authorizes the same request kind in all cases through `effect in permissions(st)` (`l5_write.py:54`).
- Safe case returns `DENY/current-effective-permission` and creates no effect file (`safe['effects'] == []`), proving the write depends on the ceiling, not on Landlock or a different API.
- Positive case commits exactly one effect with bytes `authorized-positive`, SHA `8732b8a00f4332a354a08c1713b3f31278436d3c16f2befae9095e47590bbd06`, and `committed_before_ack=true` (`l5_write.py:59-62`).
- Mutant commits one forbidden effect `post-move-forbidden`, SHA `fc614537bf8ddf4be6ccf0797898d6c2f476fea99da0fdec674d084dd9b47b83` (`l5_write.py:59-62`), proving the mutation is exercised and detected.

### 2. Accepted-byte provenance — unsupported for storage (observed equality only)

- The moved `read_x` reply is a hardcoded constant: `reply={'result':'OK','bytes_hex':X.hex(),'sha256':EXPECTED,'identity':'C-accepted-x'}` at `l5_write.py:57-58`; `X=b'F3-lifecycle-x-v1\n'` at line 9. H never opens `${protected}/objects/146207...bin` or checks state for an accepted-object reference when serving `read_x`.
- The only object assertion in the runner is `assert content.read_bytes()==X` over L4's candidate-file copy, where `content=HERE.parent/'l4'/'lab'/'protected'/'objects'/f'{EXPECTED}.bin'` (`l5_write.py:32-33`). This proves source identity/candidate equality, not that the mediator read from the post-move accepted object.
- Therefore observed equality (worker `read` has `OK`, hex `46332d6c6966656379636c652d782d76310a`, SHA `1462070e6b10a8baf625a31791cd0f4e95af638b42b1767c2aaaf8c79cdef061`) is guaranteed by code constancy. An independently lost or modified accepted-object store could leave the reply unchanged. The mutable-storage scenario was not exercised.
- `accepted_x_bytes_unchanged` is the runner's own assertion over the source candidate file (`l5_write.py:68`), not an independent post-move object reread.

### 3. Move and activation effects — partial

Source/runtime observations:

- Move capture: `old_effective=sorted(permissions(state))` before mutating containment (`l5_write.py:39`).
- P is old read-only and Q is read/write in the moved case; raw moved state has `P.grants=['read']`, `C.grants=['read','write']`, `Q.grants=['read','write']`, `C.latent_ceiling=['read']` (`latent_preserved.current_state`).
- State transitions are whole JSON objects written atomically via `os.replace(tmp, state_path)` for `initialize`, `sealed_whole_move`, and `fresh_authorized_activation` (`l5_write.py:19-24`, lines 36, 43, 45). Each worker request rereads `CURRENT.json` from disk (`l5_write.py:54`) and invokes `permissions(st)` against current parent/grants/ceiling.
- One worker P/W pair sees post-move effective permission `['read']` (safe) versus `['read','write']` when latent ceiling is weakened (`mutant`, `l5_write.py:41`).
- Activation publishes `current_ingress='W1'` only after the move (`l5_write.py:44-45`). Post-move safe check has `parent=Q`, `ingress=W1`, `record_sha256=activation_record_sha256` (`verify_l5_write.py` check 6).

Not demonstrated:

- No live concurrency: one H process performs the sealed/unsealed transitions sequentially; no observer executes across `sealed` states.
- No crash/power-loss recovery path: the writes use `os.replace` only. There is no fsync/fdatasync, joint publication marker, or recovery branch if partially read.
- No external authorization currentness separate from the single H process. `actor` fields are H-created labels (`initial-manager`).
- No demonstration of rollback or administration resistance (explicitly excluded by builder and audit).

Therefore `supported (process-observed, single-host, single authority)` and `unsupported` for crash/concurrency/authorization currentness.

### 4. Currentness and peer — partial (trusted socket assumption)

- H treats state as current by rereading `CURRENT.json` before every worker request (`l5_write.py:54`). `actual_checks` carry `record_sha256`, parent, effective permissions, ingress, result, and distinct `worker_pid` (`l5_write.py:55`), and verified as tied to the moved current record (`verify_l5_write.py` check 6).
- W1 is a static string that originates from the synthetic fixture (`'current_ingress':'W1'` on line 35 and set after activation at line 45). H binds no cryptographic or process identity to it; it tests `st['current_ingress']=='W1'` (`l5_write.py:54`).
- The worker obtains an inherited FD from `socket.socketpair` and `pass_fds=(schild.fileno(),)` (`l5_write.py:48-49`; `l1.confine` restricts direct filesystem access, but the socket FD itself is inherited one-to-one). The worker prints `pid`; H checks worker PIDs are distinct from itself and from each other.
- Any process or thread with possession of the W-side Unix socket FD, including an unwanted handoff via inherited FDs, could submit the same op JSON. H would process it subject only to `W1` and the effective state. No peer credential, SCM_CREDENTIALS, seccomp, or comparable identity proof is used.
- The trust assumption is stated explicitly by the current source. The system profile is valid only under "trusted H owns the FD and passes it only to the intended worker."

### 5. External effect ordering — partial

- Write sequence in H (`l5_write.py:59-62`): authorization first, atomic temp write, target replacement, effect record, then `COMMITTED` acknowledgement. `committed_before_ack=target.exists()` is recorded and verified (`verify_l5_write.py` check 2).
- Observed ordering is therefore process-local and exercised by both a successful positive case and a protected mutant.
- Not measured or supported: power-loss durability via fsync/fdatasync, directory sync, sink/journal contracts, asynchronous duplicate write, retried replay after lost reply, durable-vs-visible visibility, or concurrency.
- `os.replace` is atomic at filename level for an ordinary filesystem; this is necessary but not evidence of durability or cross-process visibility.

### 6. Verifier independence — supported (bounded)

Built-in verifier result after independent rerun: 9 `PASS`, exit 0.

Independent disposable-copy mutations:

| Disposable mutation | Expected behavior | Verifier result |
|---|---|---|
| source hash unchanged | pass | PASS 9/9 |
| safe route decision `allowed=true` (contradicted) | must fail | FAIL 1 (mediator checks tied to moved record) |
| safe latent ceiling dropped to `read,write` | must fail | FAIL 1 (whole move record) |
| mutant effect removed (missing effect) | must fail | FAIL 1 (weakened-ceiling admitted... no effect observed) |
| safe read bytes/hash changed | must fail | FAIL 1 (fresh ingress reads exact retained x) |
| accepted x unchanged flag false | must fail | FAIL 1 (accepted x unchanged) |
| worker PID collided with authority PID | must fail | FAIL 1 (worker IDs distinct) |
| wrong captured ceiling in move event | must fail | FAIL 1 (whole move record) |

The verifier catches all tested 8 manipulations. Caveats:

- The verifier shares implementer constants (`X`, hash `1462...`, expected worker count) and labels, so it is not maximally cross-family; it validates logical consistency rather than model-independent replay.
- It validates 9 static fields. It does not replay process execution, Landlock eligibility, route loading, clock/order, or filesystem placement.
- No mutation of worker PID source representation; only raw integer collision was tested.

### 7. Coverage and regressions — partial (new stand-alone fixture, no regression)

- L5 does not load L4's `CURRENT`, `record-000006`, work units, P/C/Q hierarchy, or accepted object. Each case instantiates a fresh synthetic `CURRENT.json` in a temporary subtree (`l5_write.py:31-35`), with C granted `read,write`, latent `[read,write]`, and P grants supplied by argument.
- The only historical link is the content assertion: `content=HERE.parent/'l4'/'lab'/'protected'/'objects'/{EXPECTED}.bin`, checked bytes equal X (`l5_write.py:32-33`). This seeds the fixture from an L4 accepted-object content value, but does not demonstrate continuation from L4's sealed record.
- This means the experiment is a clean-room L5 write/move harness seeded by the accepted `x`, rather than a continuous historical Work Unit. It tests the latent-ceiling pre-condition and warrants a "bounded L5 discriminator" only in isolation, consistent with prior obstruction note that L4 lacked the write-capable attachment.
- No previous sources were changed: L1-L4 source hashes remain as committed. The test does not rerun L1-L4 routes on this build (builder explicitly frames this as an independent harness addition). Thus no regression evidence was re-established in this run; no regression failure was observed from L1-L4 source files.
- Excluded routes remain outside the profile: worker descendants, FD passing, SCM_RIGHTS, network, credentials, shared memory/mappings, alternate mounts/aliases, other sinks, mediator losses, crash/power loss, races, rollbacks, and administrative mutation are not tested. These exclusions are honestly documented by builder (`RESULT.md`, authority/effect route boundary).

### 8. Outcome classification table

| Claimed property | Classification | Evidence or necessary limitation |
|---|---|---|
| Mediator receives one inherited socketpair FD per worker and requests permission | supported (bounded) | `socket.socketpair`; `pass_fds=(schild.fileno(),)`; worker only calls `read_x/write`; route observed. |
| H mediates all effect operations, worker has no target/object/effect FD | supported (bounded) | worker `confine` blocks direct path; actual checks concern mediator only. |
| Positive configuration allows mediated write and has observable effect | supported | positive effect bytes/hash/file `committed_before_ack=true`; verifier PASS 2. |
| Move retains old effective read-only ceiling after P becomes Q more permissive | supported (process-level) | `captured_old_effective=['read']`, `permissions` recomputes `['read']`; mutant shows write if dropped. |
| Post-move fresh activation after sealed move | supported (in-process, sequential) | event order: whole move then activation; `active=true, sealed=false, W1`. |
| Post-move read returns accepted `x` bytes and hash | supported for bytes/hash; unsupported for storage provenance | worker saw OK/exact X hash, but H echoes constant (see check 2). |
| Accepted object storage remains unchanged after move | partial | assertion is source candidate file only; no post-move retained-object recomputation in L5. |
| Post-move protected write denied in preserved config | supported | safe DENY, `safe.effects=[]`; verifier PASS 5. |
| Weakened move permits the forbidden write, detected | supported | mutant effect with distinct bytes/hash; verifier/mutation distinguishes. |
| Whole move/activation atomic publication | partial | atomic `os.replace` per state record; no crashes or concurrent readers tested. |
| Current records are reread per request | supported (process-level) | `st=json.loads(state_path.read_text())` at line 54; `record_sha256` check. |
| Current W1 ingress is authoritative/current | partial/apparent | static label; any holder of W-end FD could supply it; trusted-H assumption. |
| No reliance on worker identity beyond socket FD | supported as profile; unsupported for broader model | only PID label and requests; no credentials/peer validation. |
| External effect ordering (authorize-write-effect-ack) | supported process ordering; unsupported durability | effect exists before reply; no fsync/power-loss/concurrency. |
| Verifier can independently reject altered raw evidence | supported (bounded) | 8/8 mutation manipulations fail; 9 built-in checks. |
| Continuous historical L4 Work Unit / accepted objects | unsupported | fresh synthetic `CURRENT`; seeded only to candidate hash/content. |
| F3/F5 completion | unsupported/non-inferable | L5 remains one discriminator; profile exclusions are numerous. |

## Minimal proposed follow-ups (not repairs)

The independent audit does not repair the target. If the next authorized implementation requires stronger claims, the smallest extensions are:

1. **Accepted-byte provenance:** initialize each case by locating the L4 accepted object identified by `record-000006.json`/its accepted object hash, expose it as the post-move accepted object, and compare bytes before and after move under both an attacker-object swap and an object-loss case. Do not simply replace the current constant with any other constant.
2. **W1 authority:** document as trust assumption (already) or add bounded peer identity (e.g. `SO_PEERCRED` or an H-issued capability token). Either choice would need a threat test.
3. **Publication durability:** specify required atomicity contract and either test crash/recovery or explicitly designate L5 as process-level observed evidence only.
4. **Continuous L4 provenance if desired:** load L4's whole record and P/C initial state instead of synthesizing new grants, while keeping Q introduced as in the packet; otherwise state explicitly that L5 is a fresh fixture seeded from L4 accepted content.

## Commands and local artifacts

- Isolated full repro:

  ```sh
  python3 -m py_compile l5_write.py verify_l5_write.py
  timeout 30s bash -c 'ulimit -v 524288; python3 l5_write.py > /tmp/opencode/l5review/l5-write-raw.json'
  python3 verify_l5_write.py /tmp/opencode/l5review/l5-write-raw.json
  sha256sum l5_write.py verify_l5_write.py /tmp/opencode/l5review/l5-write-raw.json
  ```

- Mutation harness: `/tmp/opencode/mutate_raw.py`, applied to disposable copies only; original `l5-write-raw.json` hash remained `a03521863a6dd5ebce55eadb057467a1479e90d13ca526a4607ac2fb52f5d83b`.
- All verdict-relevant logical relations support the built-in verifier for baseline and fail for all eight manipulated variants above.

## Conclusion

L5 is a valid, nonvacuous, bounded hostile-profile discriminator for a mediated latent write after a sealed parent migration. It uses real write operations, effect files, hashes, retained ceilings, and full-state per-request rereading of `CURRENT.json`. It does support the narrow claim that a preserved latent `read` ceiling blocks the same write that succeeds under an explicitly weakened mutation, and that a distinct positive configuration can perform such a write.

Independent audit, however, identified a material gap: **the post-move read is a constant, not a storage read, so L5 does not establish accepted-byte provenance.** It also remains a stand-alone fixture rather than a demonstrably continuous historical continuation of L4's accepted work-unit record, and it does not test crash recovery, concurrency, or source identity.

**Command/runtime verdict:** `L5-PASS` for the host profile, subject to the limitations above.
**Independent semantic verdict:** `partial` due to absent accepted-byte provenance and declared out-of-profile route coverage.
**F3/F5 completion:** not inferred or supported.
