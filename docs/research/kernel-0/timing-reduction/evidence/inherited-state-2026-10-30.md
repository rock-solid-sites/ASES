# Inherited-state checkpoint ? Agent A timing reduction (2026-10-30)

- VPS `tripn-vps`; exact worktree `/home/claude-code/.paseo/worktrees/216s81dw/phase-i-a-kernel0-timing`; branch `research/phase-i-kernel0-timing-20261029`; starting HEAD/origin `ae50b182b2cf9ea073b45a8844e3b3843fd67dc6`; initially clean.
- Re-read timing `CHECKPOINT.md`, `timing_event_model.py`, correspondence log, cleanup record/amendment, and Oct 5 handoff commit `2a97e9dd8a6af9dc447d5d8f07009b2c0abba5b6`. Frozen Kernel semantics and ingress reduction remain separate; ingress files untouched. Do not retry the Phoenix Grove provider (prior HTTP 402).
- Inherited result remains incomplete: preserved run reports `independent: state-word 0/4194304, offers 0`; no timing-reduction conclusion.

## Harness diagnosis

`run_correspondence` enumerates the entire 22-bit encoded word domain (`4,194,304` words) independently for each profile and, for every invariant-satisfying state, visits all 148 offers. `minimal_style` adds up to six alternate oracle resolutions. There is no per-word/progress write in the harness; the time check is only after a full profile. Thus the configured deadline does not bound a profile's inner traversal and the old 0/4,194,304 marker cannot indicate a stuck state or a result. More importantly, the `STYLES` collection is not explored: each case uses `join(s, s, mask)`, exactly the original state for every mask; the reported `styles_examined=2` is hard-coded. Consequently the style correspondence checks are vacuous for missing-field observation. The module docstring advertises cut/event exploration and mutation/history phases, but the file defines only the correspondence/residue routine; no event/cut explorer is implemented here.

Partitionable units: (a) profiles; (b) contiguous state-word intervals, with resumable start/end and progress; (c) offer-kind/catalog slices within selected legal states; (d) finite event fixtures by operation family and cut location. A full scan should not be restarted until slices have an honest bound and resumable evidence.

## First bounded probe

Replay command (from worktree root): `timeout 110s bash -c 'ulimit -v 1572864; python3 -u docs/research/kernel-0/timing-reduction/evidence/first_bounded_probe.py' > docs/research/kernel-0/timing-reduction/evidence/first-bounded-probe.log 2>&1`. Source SHA-256 `04eec02dd9811e59914e3c832c92632c1f2ae90105a349edf3d3a6f3d6bed011`; log SHA-256 `e94e0e5899025704ad8155bb332aff4b48de86d3ff4164c1d1e64848fcd6ad18`. Probe built 5?6 reachable seed states/profile (17 total), covered all 148 catalog offers and all invariant-preserving one-field perturbations for touched fields: 2,061 comparisons in 0.052 s; no runtime/assertion failure. It found expected guard witnesses: changing `issued` makes grant(a0) commit ? deny; changing accepted `content` makes matching resume commit ? deny. This confirms selected fields are semantically relevant in these fixtures; it is not a proof of a minimum global style or any timing contract. Raw output: `evidence/first-bounded-probe.log`.

Assumptions/next gate: establish proposal atomicity, one coherent current-state view, whole-successor publication, and acyclic order for interacting commitments from completed correspondence evidence. Until then result is incomplete; no timing reduction is asserted.


## Projection repair (bounded fixture)

Added `project(state, mask)` in `timing_event_model.py`: it returns a named tuple containing only visible fields (hidden fields are absent rather than filled from another state/default). Replaced the old `join(s, s, mask)` calls; the legacy traversal now resolves using the complete frozen state and compares projected successor values. This fixes representation semantics, but does not make that traversal a proof of observational sufficiency: it still does not enumerate pairs/classes of legal states sharing a projection. The module docstring now says so explicitly.

Fixture: `evidence/observation_projection_test.py`. Replay: `timeout 50s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/observation_projection_test.py'`. Successful log: `evidence/observation-projection-test.log`; initial test assertion failure is preserved in `evidence/observation-projection-test-failure.log` (the test incorrectly omitted `data` while expecting it visible). Corrected test passed, showing hidden `issued` collapses when omitted, visible fields distinguish, and the empty mask projects to `()`. No complete timing contract is inferred.

SHA-256: `timing_event_model.py` `595c7ff9a4a7350476edd316e9af20a88d4ed78277f74cd82dae15dcac534fcf`; fixture `observation_projection_test.py` `ae9a8033e35deea58c9c086d4518d7a89651f82445a74b5ab0ca8f7a1a1332da`; pass log `observation-projection-test.log` `73f4269c1c8ac4b239cd48a5c411280a0a798529b64a342059677a16f390bb71`; failure log `observation-projection-test-failure.log` `c78cf016980c4d9e0ee075e138fc849d94809bb3b8c639ad55cc8cb1ad72ff13`.


## Bounded event/cut fixture

Ran existing `flight_explore` and `serial_witness` through `evidence/event_cut_fixture.py`, capped by `timeout 50s` and `ulimit -v 1048576` (1 GiB). Replay: `timeout 50s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/event_cut_fixture.py'`. Result: PASS, 151 explored states total (79 correct current-view, 70 stale-view mutant, plus two ordering permutations), below 1,000. The stale-view mutant has a concrete trace that commits `set` after revocation where fresh-current resolution denies. `serial_witness` permits set-before-revocation in an overlap, but returns no witness when revocation is constrained completed-before-set-invocation. The whole-pair fixture checks the complete `(1,1)` successor and explicitly rejects `(1,0)` as an endpoint/cut.

Concrete event/cut obstruction: the frozen `Flight` encoder stores a `Request` as a single object at `invoke/copy`, records one full `State` at observation, and changes its `state` from one complete `State` to another in a single resolve transition. It has no event representation for torn request capture or an intermediate published successor, so those physical/logical cuts are assumed atomic, not explored. The fixture therefore discriminates current-view and order claims and illustrates endpoint granularity, but cannot establish a timing reduction for capture/publication. Global correspondence and the minimum four-part contract remain unproven.

SHA-256: `event_cut_fixture.py` `1f5bcd2aa8aab31263c3d9f28862e944c647969bbb45f8e0988f2081320b01d2`; output `event-cut-fixture.log` `93cf8a3cf7dcf58c97a74dafdbedae64183d7d1d55a9d75b759ad5df95450e52`.
