# Incomplete checkpoint — Agent B (Work Unit F1)

- Branch: `research/phase-i-work-unit-f1-20261029`
- Parent/base commit: `5c03a425fd5627c3764806292b8c5cb653498f4f`
- Crosslink: issue #8
- Provider session: `dc0956f3-44f4-4088-af1a-5ded4d417d7c` (ended with HTTP 402)

## Preserved findings

`Phase-I-F1-Design.md` and `phase_i_f1_model.py` are drafts. The plan, Closure, Kernel obligations and Work Unit A-L were inspected. State-space execution did not complete. There are no verified invariant, successful witness, mutation, or counterexample results. The Codex sandbox allowed ordinary files but denied access to shared Git metadata; no protection was changed.

## Incomplete work / next operation

Read and correct the model before running it; use small, per-context bounds and one verification process at a time; save raw traces and a state-space report inside this directory; complete the C1-C13/A-L mapping and independent mutation controls. Do not claim unbounded proof.

## Artifacts

- `Phase-I-F1-Design.md`
- `phase_i_f1_model.py`
- `__pycache__` is generated test residue and should not be committed.
## 2026-10-30 continuation checkpoint



Inherited clean branch research/phase-i-work-unit-f1-20261029 at 0ebb257bf646c0bf753fe410e622369bd14af53b; origin verified at the same SHA. Recovery archive SHA-256 verified as 6783ccb452fa24d14a2a82cb2f777eb515f69078a5f4d29876ea23560da32e0c. Separate worktree: /home/claude-code/.paseo/worktrees/216s81dw/phase-i-b-work-unit-f1.



First bounded operation: syntax-check the preserved model and inspect focused state/policy sections, then run a small bounded context. No invariant, witness, mutation, or proof claim is inherited as verified.

## Bounded-run observation (2026-10-30)



The model passed Python syntax compilation. The first executable run used a 120-second process timeout and a 1,800,000-KiB virtual-memory cap, but the script explored all configured contexts in one invocation. It terminated with MemoryError in explore() before writing Phase-I-F1-Results.json. This is INCOMPLETE and establishes no invariant or witness result. No process remains running.



Next: measure a single small context with a lower explicit state ceiling; repair the exploration interface or state representation as needed before further runs. Preserve drafts; do not make a bounded or unbounded proof claim.

## 2026-10-30 targeted evidence checkpoint



Corrected two concrete draft defects: the recovery activation effect now enables image and enforcement atomically; explicit trusted initial latent ceilings permit later authorized grant events. Syntax passed. One bounded recovery context reached 16 states/78 committed transitions with zero invariant violations. Ten draft witness histories yielded seven fully committed; WT-01, WT-07 and WT-09 remain invalid/incomplete and are documented in Phase-I-F1-Targeted-Run.md. The broad combined exploration hit MemoryError under its cap and remains incomplete.



Next: repair the failed witness fixtures/ack guard, add a per-context state/time-limited runner and preserve raw outcomes; then complete C1-C13/A-L coverage and intended mutants. No proof claim.

## 2026-10-30 mapping and witness checkpoint



Added explicit status mapping for every C1-C13 and Work Unit A-L in Phase-I-F1-Targeted-Run.md. Repaired the draft management-ack guard, delegation scope check, and WT-01 full-path fixture. Retests: 10/10 witness event sequences commit; only 2/10 weakened variants discriminate intended faults (AT-02, AT-09). Several sequence promises still do not execute their negative control; coverage table and evidence note disclose this.



Next: model explicit denied uses after engine loss and latent move; repair or replace nondiscriminating mutation histories; implement missing bounded contexts for C1-C13 obligations beginning with capacity/content/recovery. All-context MemoryError remains unresolved; no proof claim.

## 2026-10-30 latent-ceiling checkpoint



Found and repaired a concrete C8 defect: move/use previously dropped an old ancestor grant restriction despite a latent record. AT-05 now denies forbidden post-move write and discriminates when latent preservation is weakened. Attack discrimination is 3/10, remaining seven invalid. A 10,000-state run of containment-and-grants exceeded its state bound and is recorded incomplete. Next: refactor bounded exploration/reporting, rerun recovery context under updated source, and continue explicit negative/witness tests.

## 2026-10-30 finite-context checkpoint



Added explicit finite horizons for management generation (4) and AC epoch (2), stopping infinite event-loop growth. Re-ran contexts: engine loss 16 states/78 commits; replacement-management 456/2086; delegation 120/502; each 0 invariant violations within its context. Containment and all contexts exceed a 10,000-state cap and remain incomplete. Ten positive event sequences commit; 3/10 mutations discriminate. Targeted deny-use checks confirm post-stop denial and the latent restriction after move. Per-context evidence is in Phase-I-F1-Targeted-Run.md.



Next: model positive use after recovery with retained accepted content, add the required negative event to WT-05/WT-08, partition containment further and complete C1-C13/A-L checks. No theorem claim.

## Continuation handoff checkpoint (2026-10-30)



Latest durable model SHA-256 83827480e6825650717a719c4d9920d16591803d7017903bdece741dce9ae8aa. Syntax passes; separate witness/mutation checks report 10/10 event admissions and 3/10 valid discriminators. Bounded completed contexts: engine-loss/recovery 16/78, replacement/management 456/2086, delegation 120/502; 0 invariant violations each. Containment and all contexts exceed 10,000 states. Management generations are capped at 4 and AC epochs at 2 for finite exploration only.



Mapping C1-C13 and A-L is explicitly status-labelled in the targeted run record. Content, reservation/capacity, sink, derivation, concurrent-order and several recovery/currentness obligations remain unimplemented; WT-05/WT-08 promises are not fully represented by their own sequences; seven mutation variants remain invalid. Therefore F1 remains INCOMPLETE and is not a proof.



Next work: add retained accepted content x with post-recovery use, distinguish preparation/commit/activation and current versus historical images, implement bounded content/capacity/sink contexts, then repair remaining mutations and test run record.

## 2026-10-30 accepted-content continuation checkpoint



Implemented accepted_x as a fixed immutable C-owned content atom and use_x as a current-authority read. Cold activate_image now restores the image and engine atomically but seals every present Work Unit; separate activation is required.



Content-continuity context completed at 600 states/3,090 committed transitions/0 invariant violations under 5,000 states, 1 GiB RSS and 120 s. Trace accepts x once before stop, recovers with x still accepted and all WUs sealed, rejects pre-activation use and stale generation-2 ingress, then accepts x under fresh management and generation-3 ingress without resubmission. Explicit trusted storage/current-image premises and C1/C5/C6/C7/C12 plus A-L mapping are recorded in Phase-I-F1-Targeted-Run.md.



F1 remains incomplete; this is finite abstract evidence only. Next: add byte/version identity and a meaningful storage/current-image discriminator or explicitly keep currentness as premise; extend accepted x to y and unaccepted z only in separately bounded fixtures; repair WT-06 to reflect sealed recovery; preserve F5 independent review as outstanding.

## Scope synchronization checkpoint



Updated SCOPE_COVERED to disclose the bounded accepted-x continuity fixture; reran the named context at 600 states/3,090 committed transitions/0 violations and syntax-checked successfully. Current source SHA is recorded in the targeted report.

## 2026-10-30 capacity-one tranche start



Resumed on branch research/phase-i-work-unit-f1-20261029 at inherited remote-verified SHA 09928adf92ff389d5e51a751b53b1f577763519f in the existing VPS worktree. Crosslink issue #8 remains open and the active local session is #3 bound to #8.



Next bounded fixture: one reservation unit supplied by P, allocation as a view assigned to C or sibling S, consumption tracked separately, two serialized competing requests, and one unrelated positive change. Planned context cap 10,000 states, memory 1,000,000 KiB, timeout 120 seconds. No aggregate context or proof claim.

## 2026-10-30 capacity-one checkpoint



Implemented capacity_reserved as the single P-owned unit assigned as a view to C or sibling S, plus separate capacity_consumed. No parent+child double counting: one non-None owner accounts for the one global unit.



The capacity-one context passes: 8 states, 10 committed transitions, 0 invariant violations under 10,000 states/1 GiB/120 s. Named sequence C reservation succeeds, S competitor denied, independent change succeeds, C consumption succeeds. Search includes both C and S as possible reservation owners. Evidence and C1/C3/A-L mapping are in Phase-I-F1-Targeted-Run.md.



Next optional bounded tranche: add the three pending-proposal cyclic-order attack and independent disjoint transition. Capacity fixture does not establish concurrent conflict ordering. F1 remains incomplete.

## 2026-10-30 cycle-order checkpoint



Added a fixed three-pending-proposal cycle fixture: 0 requires 1, 1 requires 2, 2 requires 0. All proposals are pending before commits; each commit is rejected. A disjoint management-authorized independent_change commits in the same state.



Bounded cycle-order context passed at 16 states/32 committed transitions/0 invariant violations under 10,000 states, 1 GiB, 120 s. Evidence, trace, assumptions and C2/C3/K mapping are in Phase-I-F1-Targeted-Run.md. This is a single serialized cycle witness, not general concurrency proof.



Capacity-one milestone remains recorded: P-owned unit allocated to C or S as one view, separate consumption, one competing denial and independent control; context 8 states/10 transitions/0 violations. F1 remains incomplete; continue with report/obligation accuracy, no aggregate search.

## 2026-10-30 current-versus-stale-image tranche start



Resumed existing F1 tracker on the existing worktree and branch at remote-verified SHA 2022bba53a74e9d3cc6c653027a3bb9b7aa26522; active Crosslink session is already bound to issue #8. Earlier x, capacity-one, and cycle-order fixtures are preserved and will not be rerun.



Next bounded fixture only: accept x then y; capture current and explicitly stale authentic image records (stale image omits y and carries prior epoch); after stop/recovery require current image restore sealed with x/y and reject stale restore as outside-profile. Add a currentness-check weakening and require it to admit stale data into an invariant violation. Planned cap 10,000 states, 1,000,000 KiB, 120 seconds. Currentness is a trusted external premise in the baseline, not rollback resistance.

## 2026-10-30 currentness-image checkpoint



Added the single currentness-image context with distinct x then y accepted under epoch 1, a stale authentic epoch-0 image omitting y, and an epoch-1 current image containing both.



Result: 42 states/128 committed transitions/0 reference invariant violations. Current image restores sealed with x/y; stale image is refused as outside baseline successful recovery. With currentness_check weakened, stale restore is admitted and triggers the C7 stale-image invariant counterexample. With currentness_available absent, both candidates are refused; currentness/rollback resistance remains an explicit trusted premise, not proved.



Test bounds: 10,000 states, 1 GiB RSS, 120 seconds; no aggregate search. Run record includes trace, mutation, C5/C6/C7/C12 and A-L mapping plus storage/currentness assumptions. F1 remains incomplete.

## 2026-10-30 two-loss fixture start



Inherited clean branch research/phase-i-work-unit-f1-20261029 at origin-verified SHA 657621f86ea517ab043ffaa709dc6f076179c238. Existing currentness-image, content-x/y, capacity-one, and cycle-order evidence remains intact; those contexts will not be rerun.



Next single context: two successive stop/recover/restore cycles over x/y at epoch 1; verify sealed after each current-image restore; deny use while sealed and stale generation-2 use after final explicit activation; allow current generation-3 use. Inject the authentic epoch-0 x-only image during the second recovery and run one currentness_check=False mutation to require the C7 stale-image counterexample. Cap 5,000 states, 1,000,000 KiB RSS and 120 seconds. No aggregate search.

## 2026-10-30 two-loss test checkpoint



Added and ran the separate two-loss-currentness context. Both stop events seal every Work Unit and preserve accepted x/y. Each recovery restores the epoch-1 current image sealed; use is denied while sealed, stale authentic epoch-0 x-only image is refused, and after second current restore only explicit activation permits use. Stale generation-2 evidence remains denied; current generation-3 use succeeds.



Reference context: 51 states/445 committed transitions/0 invariant violations under 5,000 states, 1 GiB RSS and 120 s; syntax passes. Weakening currentness_check admits the stale restore and triggers the intended C7 invariant counterexample. Exact trace, assumptions, and limits are in Phase-I-F1-Targeted-Run.md.



Two repeated cycles are the declared finite cutoff; deeper recovery, physical storage and rollback resistance remain unproved. No aggregate context was run. F1 remains incomplete.

## 2026-10-30 optional-sink tranche start



Inherited branch research/phase-i-work-unit-f1-20261029 at remote-verified SHA 7eb3cbe350311fb231412a3c158d52abdc96d7b1. Existing content, capacity, cycle, currentness and two-loss fixtures are preserved and will not be rerun.



The current model has no sink acceptance ledger or source reply/knowledge distinction. The next single tiny context will add an explicitly permissive abstract sink outcome plus source-visible reply state only to compare accepted/unaccepted histories, dropped/surviving message choices and duplicate possibility on blind retry. This is not a sink contract or exactly-once guarantee. Planned cap <1,000 states, 1,000,000 KiB, 90 seconds; no aggregate search.

## 2026-10-30 permissive-sink checkpoint



Added a tiny sink-outcomes context separating hidden sink_attempts from source reply knowledge. Accepted and dropped histories both project to (one attempt, unknown reply); a single common causal skeleton orders request before terminal sink outcome before reply loss.



Both dropped and surviving message choices are tested. Under the explicitly permissive no-deduplication abstraction, retry after lost reply reaches two irreversible accepted outcomes. This demonstrates duplicate possibility only; it adds no sink contract and makes no exactly-once claim.



Run: 19 states/22 committed transitions/0 invariant violations under 1,000 states, 1 GiB, 90 s; syntax passed. Evidence and C1/C10/C12/Work Unit mapping are in Phase-I-F1-Targeted-Run.md. F1 and concrete sink semantics remain incomplete.

## 2026-10-30 AT-03/AT-11 audit tranche start



Inherited branch research/phase-i-work-unit-f1-20261029 at remote-verified SHA 6b38496bcf01041e740842976bf471f7790c2670. Existing Crosslink session remains bound to #8. This tranche is restricted to AT-03/T02, AT-11/T07 and one small named invariant context.



Initial inspection: AT-03 uses A_GEN for SINK even though A_GEN is the NET ingress generation and the SINK is already at B_GEN; the old-use attempt is stale before replacement and the mutation disables ack ordering rather than old-position currentness. AT-11 attempts mgmt_ack with no pending revoke; Profile.ack_after_commit has no behavior separating prepare from recoverable commitment. Capture the before traces first; then repair only reachable history/observer coverage demanded by T02/T07.
