Verdict: supported

I reproduced the artifact's own suite end-to-end and then attacked the claim with independent machinery. I could not falsify the reduction, and I could not find a hidden runtime classifier or a residual premise beyond the one the claim names.

What the implementation actually is

docs/research/kernel-0/ingress-reduction/fixed_ingress.v (27 lines) is a combinational demultiplex: case (lane_valid) picks one of five 11-bit slices, and line 25 hard-writes proposal = valid ? {1'b1, …, actor, …} — the authenticity verdict is the literal 1'b1, and actor is the lane's bit index. No caller-supplied authority field exists anywhere in the 60 input bits. The composed machine instantiates the frozen kernel0_machine unchanged.

Independent falsification attempts (all failed to break the claim)

Probe | Result
--- | ---
My own SAT restatement (shift-based, not the artifact's ingress_spec) over all 2^60 raw inputs | valid ⟺ exactly-one-hot(lane_valid); ¬valid → proposal=0; valid → proposal[14]=1 always; valid → actor == lane index; actor==4 requires lane_valid==5'b10000; proposal is a function of the selected slice only (proved by complementing every other slice → identical output)
fixed_ingress synthesized standalone | 10 cells, 0 memories, 0 processes, 0 flip-flops — no routing table, no runtime state
Refinement equation over all 2^22 state words (not just invariant-satisfying ones) × all raw inputs, all 4 profile combinations | SUCCESS in each — stronger than the artifact's valid_state-restricted boundary proof
Sequential differential: fixed_ingress_machine vs. unchanged kernel0_machine under an independently written abstraction A, 80,485 edges × 3 profiles, raw inputs incl. exhaustive 2048-payload sweeps on every lane at live states | PASS — composed ≡ baseline ≡ frozen Python oracle; 0 stale-lane-a0 commits
10,240 raw lane words × 3 profiles from the post-replacement attack state | 0 commits on stale a0; matches frozen oracle exactly
Mutants | Concrete counterexamples retained (lane_valid=00001 impersonating lane 1; always-idle caught)
Injectivity/coverage | 148 templates ↔ 148 distinct (lane,payload) pairs; lanes 0–4 cover exactly manager + a0–a3; round-trip exact
Artifact's own suite | 41/41 commands, PASS, 2,472,636 comparisons, vector hashes bit-identical to committed evidence

Critically, the residual premise is tight, not understated: the payload bus being shared is provably harmless (noninterference), and actor is a pure function of lane_valid. So the only ingress-side thing a caller must not control is asserting another lane's valid bit — exactly "protected non-confusable source lanes."

Two disclosures that fall short of falsification

1. Strict interface subset. The 148 false-authenticity words become unreachable (verdict is a literal 1). Benign — their only baseline outcome was deny, and deny stays reachable — and the artifact discloses it explicitly.
2. Pre-existing, inherited baseline gap. For a few raw non-catalog words (e.g. restrict with other≠0, resume with target≠0, pair/set/flip with other≠0), the frozen Python oracle would commit while the frozen RTL wellformed gate denies. The artifact assumes deny for non-catalog words rather than testing the oracle there. My differential shows composed ≡ baseline on every such edge, so this is inherited from the unchanged baseline, not introduced by the reduction — but it is the one spot where the evidence substitutes an assumption for a check.

Also noted: netlist JSON hashes in the recorded evidence are not byte-stable across runs (identical cell counts/types), and three of my own harness bugs (inverted complement mask, backwards conjunct, %h/%b field width) had to be fixed before its results were usable.

Build · Space Bunny Free · OpenCode Zen · tools OK · free stale 6.2d · 23.6s · 38.4 tok/s
