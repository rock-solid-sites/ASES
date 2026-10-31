# Coordinator synthesis — independent F3 L5 verification

**Bounded verdict: PARTIAL.** The safe-move behavior is reproduced: L4's actual accepted x is hash-verified from protected storage, C and dependent D retain the read-only full-path ceiling after a sealed P→Q move, the safe write is denied, the positive mediated write succeeds, the weakened-ceiling case creates the forbidden effect, and the targeted cycle/dangling/unknown-right controls reject. This supports the narrow behavioral T11 discriminator. It does not fully establish an authorized lifecycle integration or all of T11 / Closure §7.

## Independent model outcomes

- GLM reviewer (`opencode/glm-5.3-flash-free`): **PARTIAL**.
- MiMo reviewer (`opencode/mimo-v2.6-flash-free`): **PASS**, bounded and profile-limited.
- Both report texts and raw OpenCode JSONL are included. Their disagreement is retained; neither report was edited to align them.
- The first MiMo attempt crossed packet boundaries and was aborted before producing a report; it is not counted as an independent verdict.

## Coordinator findings

1. **Positive-control activation bypasses the manager handler.** In `l5_integrated.py:118-128`, the positive case mutates/commits activation directly, outside `manager_roundtrip`; raw evidence confirms `cases.positive.management == []`, and the emitted activation event is not the gated activation event. The safe moved case does submit separate move and activation requests through the in-process socket handler, so its observed sequence is useful, but the positive control cannot support the broad claim that activation is always authorized through that boundary.
2. **The use-time guard ignores ancestor active/sealed state.** `graph_valid` validates graph shape and permissions but not active/sealed consistency (`l5_integrated.py:31-45`); `enabled` checks only D's active/sealed fields (`:138-140`). A structurally valid state with C sealed/inactive and D active/unsealed, a current ingress, and widened ceilings produces `allowed(write)=True`. This is a source-level adversarial counterexample, not a history recorded by the runner.
3. **The T11 grant exception is not implemented.** The safe path tests retained denial; the weakened control directly drops the ceiling (`:114-116`). No separately authorized post-move grant is exercised or implemented in this harness, so the “unless a separate authorized grant explicitly changes it” branch remains unsupported.
4. **Evidence verifier is a useful consistency verifier, not an independent state reconstruction.** It binds the source digest and retained L4 evidence, but the L5 temporary record store is deleted before returning and the raw L5 evidence omits final state records. It cannot re-hash those committed records or independently reconstruct the permission result from them.
5. **L5 authority continuity is not demonstrated.** L4 runs to completion in a subprocess before L5 state extension; L5 uses its own trusted mediator and protocol-shaped manager socket. The L4 accepted objects are real inputs, but this does not extend the live L4 H2 process.

## T11 / Closure §7 scope

**Supported by observed test:** P read-only / C local read-write premise, sealed C move under permissive Q, D retained as C's dependent, old transitive ceiling retained, post-activation verified accepted read, denied write with no effect, weakened-ceiling write effect, distinct move and activation records on the safe path, and three structural rejection controls.

**Partial or unsupported:** manager identity/authority is a test-only same-process credential check; the positive activation bypasses it; authorized latent-right widening (“unless authorized grant”) is absent; sealed/active ancestor gating is missing; D's own accepted-content lifecycle is not tested; L5-era direct-route bypasses, concurrent management, crash/rollback durability, and live-H2 continuity are untested.

The supplied governing pin was incorrect. The actual T11 and Closure §7 files at `511a5272…` and `8277b7f3…` are used here. No full F3/F5 closure is inferred.

## Verification performed by coordinator

`python3 verify_l5_integrated.py` from the fresh review worktree: **19/19 PASS**. The GLM reviewer additionally independently reproduced the runner and baseline discriminator in a disposable copy. The MiMo reviewer independently ran the read-only verifier. See each report and raw launcher transcript for exact commands/results.
