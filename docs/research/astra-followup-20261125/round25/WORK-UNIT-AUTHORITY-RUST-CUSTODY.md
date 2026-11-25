# ASES Operator Decision Packet — Work Unit Authority vs. Rust Custody (final)

**Authorship/session:** MiMo work session, same pinned route. Revised after an independent Go DeepSeek review; that review was not authored here. **Pins:** Rust `resource-control` PR **#42** head `27bcc552cecb8bbb456b9db3a0a77da1513b31ab`; evidence PR **#83** head `8de559c78272bf639a82d284572e218a14cc1269` — canonical `docs/research/kernel-0/work-unit-adequacy-result-2026-11-24.md` at #83, with task packet `docs/research/astra-prelaunch-20261123/WORK-UNIT-ADEQUACY-TEST-PACKET.md` at PR #77 head `38a61d2c28c68bb6bc43c3d0d42d2b76a575a50f`; native-owner **supporting source** PR **#38** at source commit `0bd51a34700164a5eb77efe98158fa37d1a74e23`; native test diff PR **#84** base `bfabf1d95a1f51052679ff4855a2ccc147b97584` → follow-up head `7ed5e10baf752499b6eeef6cbb8c6905782dd15d` (test-only, separate from #38). No implementation, no new Kernel primitive, no self-attested identity, no invented evidence.

**Evidence status:** W1–W4 are **historical source-pinned captures, no fresh run** this session (`docs/research/kernel-0/work-unit-adequacy-result-2026-11-24.md` lines 15 and 39). **PR #42 and the native prototype stacks are separate experimental stacks; integration is not established** (same document, line 41). **WHAT-NOT-TESTED** (same document, line 41): no end-to-end Work Unit runtime, attachment persistence, X→Y replacement, stale-execution write fencing, multi-host authority, hostile host, or independent verification.

## 1. Candidate authority-side serialization (PR #38, candidate only)

`native/docs/research/phase-ii-native-ownership/PACKET.md` keeps L5 schema1/immutable record/`CURRENT` as the single selected source for ownership, registrations, selected world, **epoch**, child lifecycle, pending effects, logical disposition (17–19); F3 acceptance publishes registration ID, pair/world, material reference, ownership, content, new epoch (49–53); `seal` increments epoch; `dispose_child(D)`/`remove` retain records in protected `disposed_units` (64–80); guards F1 `BEGIN IMMEDIATE` → L5 flock → L6 `BEGIN IMMEDIATE` (36–41).

**Review correction:** this is a **candidate only**. Registration/epoch serialize accepted **native content** state and child/content tombstones — not durable Work Unit/Attachment Point (W/P) binding, not execution identity, not X→Y execution eligibility. `disposed_units` are child/content tombstones, not historical execution evidence. The stale selector/epoch denials and the `prepare_candidate`/removal both-orders race in `native/docs/research/phase-ii-native-ownership/REPORT.md` concern content admission and removal eligibility; they are **not W5/W6**.

## 2. What Rust custody authenticates today (PR #42)

- `Store::begin_launch` (`src/resource-control/src/lib.rs:776`) — one dispatch AUTHORIZED→LAUNCHING, same `launch_id` replays, conflicting identity refused (`src/resource-control/src/lib.rs:785–809`).
- `started_process`/`observe_launch_exit` (`src/resource-control/src/lib.rs:717, 868`) require launch-bound exit evidence before `finalize` (`src/resource-control/src/lib.rs:1001`).
- `LocalSupervisor.children`/`resume` (`src/resource-control/src/local.rs:69, 360`) — lost custody → `unknown`, no PID adoption, no capacity release.
- `resume_view` (`src/resource-control/src/lib.rs:1124`) is read-only.

**W1–W4 historical acceptance citations** (result lines 21–24): `resource-control/tests/control.rs:278,366`; `resource-control/tests/native_local_cold.rs:265` (W2), **`resource-control/tests/native_local_cold.rs:178,363`** (W3 cold finalize); `resource-control/tests/native_termination.rs:263,426` (W3); `resource-control/tests/native_unlaunched_cancel.rs:319,383,444,471`. **Custody-only result stands:** bounded ledger/custody claims, not Work Unit authority.

**Native exact-replay/recovery — PR #38 local history, separate from W5/W6:** `REPORT.md`/`check.py` show exact retry after lost reply, cold recovery with retained local sequence, fail-closed mismatched witness cut, digest-bound disposition, retained F1 observations. **Limits:** local process/filesystem histories only — **not physical power-loss durability, not same-owner compromise resistance, not remote cancellation, not external exactly-once delivery**. None of it is owner-visible execution-authority proof.

## 3. Missing interface; W5/W6 NOT REPRESENTED

No real owner-visible execution proof exists. Absent an interface that (a) binds durable W/P independently of `job_id`/`launch_id` and (b) records an **owner-authenticated** current-eligibility decision (X eligible; Y after supersession), **W5 and W6 remain NOT REPRESENTED** (result lines 25–26, 34). Required first artifact: a **crosswalk** establishing durable W/P binding and the owner-authenticated X/Y eligibility decision — no assumption that #38's epoch/registration provides either. Kernel-0 requirement basis: `docs/research/kernel-0/Kernel-0-Evidence-Packet.md:49–57` at canonical pin `a02df749b4b3da88d3f88c1712623cec6ad5d963` (result line 15); see also result line 41.

## 4. Acceptance criteria (prospective, not existing evidence)

- **W5 acceptance:** after an owner decision superseding X, Y's mutations on continuing W/P are accepted; every new X mutation is refused; prior X outcomes remain readable as history.
- **W6 order 1:** the owner accepts X's mutation, then the X→Y replacement commits; X's mutation is retained and X subsequently ineligible.
- **W6 order 2:** the replacement commits first; X is refused with no mutation; Y may mutate only after the owner grants current eligibility. Ordering derives from the owner's transaction, never transcript timestamps (`docs/research/astra-prelaunch-20261123/WORK-UNIT-ADEQUACY-TEST-PACKET.md:73` at #77).

## 5. Operator options (consequences; owner selection unresolved)

- **Option A:** Keep `resource-control` custody-only; commission the crosswalk first; select the owner only after it demonstrates durable W/P binding plus owner-authenticated eligibility. *Consequence:* no authority code this round; decision deferred on evidence.
- **Option B:** **Conditionally nominate the PR #38 Owner — still a candidate, not an established authority — as the authority**, only if the crosswalk first demonstrates durable W/P binding and owner-authenticated X/Y eligibility. **PR #84 remains test-only** (a test diff at the pinned base/head above), supplies no Owner, and cannot be nominated. *Consequence:* otherwise assigns future Work Unit authority by assumption the review rejects; epoch/registration would be over-read as execution eligibility.

**Recommendation (conditional):** proceed with Option A; owner selection is explicitly **unresolved** until the crosswalk and a W5/W6-shaped acceptance run exist. If no candidate owner can express the interface, raise that as a falsifiable design decision rather than retrofitting the ledger (result line 32).

## 6. Authority boundary

Workers are **request-only**: they may request bounded checks and return source-pinned results; they supply no identity, epoch, or authority claim. Authority stays external to the executor (`docs/research/kernel-0/Kernel-0-Evidence-Packet.md:49–57` at `a02df749…`).
