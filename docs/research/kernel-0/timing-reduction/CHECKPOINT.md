# Incomplete checkpoint — Agent A (Kernel-0 timing reduction)

- Branch: `research/phase-i-kernel0-timing-20261029`
- Parent/base commit: `d0c6e564d36f38ed09a37bc21e85c8df48da77b7`
- Pre-checkpoint branch HEAD: `d0c6e564d36f38ed09a37bc21e85c8df48da77b7`
- Crosslink: issue #7
- Provider session: `74352b31-39e3-4471-9838-23cbcc04f92f` (ended with Phoenix Grove HTTP 402)

## Preserved findings

The October 5 handoff/review was read and the existing RTL/oracle inputs were inspected. `timing_event_model.py` and partial run evidence exist. The last preserved correspondence progress is `independent: state-word 0/4194304, offers 0, 0.0s`. Several unbounded duplicate runs were stopped; see `evidence/process-cleanup-2026-10-29.md` and the orchestrator amendment beside it.

No timing weakening has been established. No correspondence run completed, and no counterexample or synthesis/regression result is claimed.

## Incomplete work / next operation

Review the event/cut harness for state-space and implementation defects; run one bounded profile at a time; capture raw output in this directory; only state a weaker timing contract if whole-proposal capture, coherent observation, whole-successor publication and interacting-commitment order are demonstrated with ingress unchanged.

## Artifacts

- `timing_event_model.py`
- `evidence/correspondence-run.log`
- `evidence/process-cleanup-2026-10-29.md`
- `evidence/orchestrator-cleanup-amendment.md`
## 2026-11-03 autonomy continuation — resume cursor

Branch `research/autonomy-20261103-kernel`: bounded research through `d0256e7e9`, with unexecuted ingress-hybrid preregistration `655222bc0`. That proposed wrapper run was deliberately not executed: inspection of `ingress-reduction/fixed_ingress.v` and `Kernel-0-Ingress-Reduction.md` already shows a stateless exact-one-valid selector and expressly retains the complete stable proposal premise; another hybrid count would not resolve a substantive additional question. This is an assumption boundary, not a newly demonstrated defect. No wrapper or runtime was added.

Evidence since `3b6b880e2`: two-field read coherence, bounded validation and version-wrap controls; return-before-invocation versus serial witnesses; coherent capture versus later currentness; and fixed/sequence RTL correspondence with concrete sampled hybrid control. The most substantial concrete run is `rtl-short-sequences-result-2026-11-03.md`: 432 selected length-three histories, 2,592 settled digital RTL cycles, positive and deliberately wrong expected-value controls. Tests reuse frozen oracle/codec; no global timing reduction, asynchronous implementation, full correspondence, physical behavior or unbounded proof follows. The concrete hybrid is settled at the digital edge and conforms to the documented ingress assumptions; no analog tearing is tested.

Ranked next discriminator: independent clean-room verification of the new sequential RTL harness and claimed case/cycle coverage, including oracle vector generation, first-divergence handling, negative controls, provenance, and whether preconditions match the stated claim. Then, if that holds, identify a specific consequential untested boundary in the trusted inputs or correspondence mapping before designing a bounded falsifier. Do not execute the unneeded `rtl-ingress-hybrid-preregistration-2026-11-03.md` merely to grow case counts; supersede or reactivate only with a distinct question. Source files and canonical documents are unchanged; research proposals remain provisional.

## Exclusive profile and observation dependencies — 2026-11-03 continuation

Starting from `b00d4fe0d`, exclusive profile was confirmed as an explicitly realized RTL profile and tested with 216 bounded six-action traces/1,296 cycles; see `rtl-exclusive-result-2026-11-03.md`. The independent-elaboration and corrupted-expectation controls fail as intended. This remains finite correspondence against the shared oracle and codec.

`omitted-fields-result-2026-11-03.md` supplies three reachable outcome-discriminating input pairs per profile under the rights+parents+data mask. Content and issued pairs differ only in the named field; the absent/established pair necessarily differs in content too. `established-content-result-2026-11-03.md` derives directly from the frozen invariant that content reconstructs establishment on legal typed states; finite controls support but do not prove the derivation. `exclusive-parent-result-2026-11-03.md` derives that a legal exclusive state cannot have parent links, and explains that the five-field content-bearing mask reconstructs the whole legal `State`. These are conditional encoding dependencies, not global minimality, physical-state, invalid/intermediate-state or timing claims.

Resume cursor: independently inspect the source-level proofs and legal-output closure assumptions before elevating these provisional findings. Do not infer a weaker timing contract from them. The timing-product inputs and observation boundaries have not materially changed, so further runs of the same products would add counts rather than a new discriminator. A new bounded test should begin with a specific remaining mismatch or an independently specified concrete-to-abstract boundary.
