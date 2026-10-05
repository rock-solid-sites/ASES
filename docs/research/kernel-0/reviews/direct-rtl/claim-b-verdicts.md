Both items closed. Final verdict.

Verdict: SUPPORTED

The frozen apparatus is sufficient to establish the bounded RTL correspondence over its declared domain.

Reproduction

verify.py ran to completion from the frozen commit: PASS total_vectors=4945272. Every profile field regenerated identically to the frozen results.json — states (8449/6337/1921), reachable, unreachable (7/5/7), vectors, commit/deny counts, sequential cycles, boundary proof, synthesis equivalence, mutation sets, and synthesis netlist hashes.

The decisive argument

Sufficiency reduces to one question: can a defect inside the declared domain pass? The exhaustive layer writes valid_states(p) × 296 vectors and the simulator must reproduce every expected successor and outcome, with assert f"PASS exhaustive vectors={edges}" forcing the count to match what was written. I established in Claim A — by brute force over the entire encoded domain, not by trusting the function — that valid_states is complete w\.r.t. the reference invariant. So that layer is provably exhaustive, not merely large. No in-domain defect can slip through. Everything else is corroboration.

Supporting layers: closure assertion (ow in encoded), an independent reachability cross-check against the reference's own reported counts, yosys synthesis equivalence, a SAT boundary proof, no-latch checks, and mutation testing that fails loudly on survivors.

Non-vacuity audits I ran myself

Check   Result

Boundary SAT proof, broken reference law    correctly fails

Boundary SAT proof, law correct only for state==0   correctly fails → genuinely covers arbitrary initial register state

equiv discrimination (gold COUPLED=0 vs gate COUPLED=1) 44 unproven cells, equiv_status -assert errors → not a vacuous string match

Truncation guard    $feof misuse would be loud, not silent

I also corrected my own first probe, which was confounded (-seq 1 checks after a clock edge) and initially gave a false reading on -set-init-def.

An error in my Claim A work

My hand-transcribed kernel0_finite_model.py hashed to f10f864e…; the frozen manifest says c9c429b0…. Cause: one missing space in a dict continuation line — 32505 vs 32506 bytes, inside direct_witnesses()'s returned metadata. Semantically inert, and verify.py's own exhaustive run on the correct file independently reproduces the same 4,945,272-vector, zero-mismatch result, so Claim A's conclusion stands on the correct bytes. I have also retracted my Claim A claim that BASE was 41 hex chars; it is 40 and resolves.

Scope — what this does not buy

\- The claim's own premises do real work: reference-model correctness, and tool correctness (iverilog 11 / yosys 0.9 / ABC — the yosys script idioms are version-sensitive).

\- The sequential layer is thin on its own (173 cycles per profile); its weight comes from the SAT boundary proof, which subsumes the register law.

\- Nothing here speaks to concurrency, executor loss, ingress authenticity, or physical timing — all explicitly out of the declared domain.

\- Sharpest residual observation, not defeating: SOURCES omits kernel0.v, verify.py, and the testbenches, so the integrity manifest does not pin the RTL under test or the machinery itself. artifact_sha256 records them but nothing ever compares it. Post-freeze edits there would go unrecorded by the apparatus — though the frozen commit pin in the bundle supplies that externally, and the claim assumes tool correctness.

Build · Space Bunny Free · OpenCode Zen · tools OK · free stale 4.0d · 1m 0s · 32.6 tok/s



Reading the bundle now; I've covered the specs and am moving to the finite model and the RTL/verification code. ξщ궁Still working: I've read the specs, RTL, and testbenches, and now I'm checking RTL against the reference model and trying to get the simulators installed. ხلकStill on it: I'm now running the full pipeline against the six frozen sources (their hashes match the manifest). ऩк&#x43B;**\*\*Supported.\*\*** I found no gap between what the apparatus checks and what the declared bounded correspondence requires.



The combinational law is checked exhaustively against \`model.resolve\`. That covers every invariant-satisfying state, including unreachable ones: 8,449, 6,337 and 1,921 states for the independent, coupled and exclusive profiles. Each state is paired with all 296 request words (148 templates, both authenticity values), 4,945,272 vectors in total. I checked that these sets are the real domain rather than a convenient subset. Enumerating all 2^22 states through the RTL's own \`valid_state\` gives exactly the model-invariant set in each profile. Enumerating all 2^15 proposal words through its \`wellformed\` gives exactly the 296 catalog words. So every RTL input that can commit is covered by the vectors, and everything else is denied.



The register wrapper is covered by the Yosys boundary proof against the same step module, from arbitrary register state. I mutated the wrapper six ways: ignore \`valid\`, drop the reset write, constant \`resolved\`, \`committed\` without \`valid\`, zero state on deny, and disable reset. The proof failed each time, so it isn't vacuous. Together with the exhaustive step check, closure under \`valid_state(proposed)\` and reset-to-initial give the all-length induction.



As an independent cross-check, I ran 300,000 random cycles per profile through the real machine. These included mid-run resets and arbitrary garbage proposal words, with out-of-catalog words expected to deny. Every cycle matched the model.



One deviation from the shipped procedure: the bundle has no git history, so I replaced \`verify.py\`'s \`git show BASE:\` comparison with a SHA-256 check against \`source-manifest.json\`. The six frozen sources match the manifest byte for byte. I also used Yosys 0.33 with \`yosys-abc\`. Everything else ran as written and passed.



The one place a skeptic could push is \`reset\`. It is an unguarded any-state-to-zero transition that isn't in the model's alphabet. The proof confirms it does exactly that, but "trusted initialization only" is a comment in \`kernel0.v\`, not something the apparatus can enforce. The \`authentic\` and actor bits arrive on the same proposal bus, and the model takes them as input premises too. If mid-run reset or caller-driven authenticity were declared inside the domain, the claim would fail. As written they are outside it, so this doesn't defeat the claim.

Claude



**\*\*not established\*\***



**### Defect Analysis**



While the combinational step logic (\`kernel0_step\` in \`kernel0.v\`) and sequential state machine (\`kernel0_machine\` in \`kernel0.v\`) correctly implement the bounded finite-model state transitions for a single synchronous step, the verification machinery in \`verify.py\` and \`exhaustive_tb.v\` tests only **\*\*1-step transition equivalence\*\*** ($\text{state} \times \text{proposal} \to \text{next\\\_state}$) and linear sequential cycle execution.



It fails to model or verify the fundamental asynchronous operational behaviors and trace requirements explicitly mandated by [Kernel-0 Direct RTL Realization Experiment]\(https\://www\.google.com/search?q=./Kernel-0-Direct-RTL-Experiment.md)[cite: 1] and [Kernel-0 Verification Obligations]\(https\://www\.google.com/search?q=./Kernel-0-Verification-Obligations.md)[cite: 1]:



1\. **\*\*Missing Asynchronous Ingress & Execution Machinery Verification:\*\***

Section *\*Required correspondence\** of the experiment specification requires verifying that *\*"no partial or intermediate hardware state may be exposed"\** and that *\*"the next resolved operation must begin from the last completed authoritative state"\**[cite: 1]. The testbench (\`exhaustive_tb.v\` / \`sequence_tb.v\`) applies instantaneous, pre-formed 15-bit proposals directly to input pins on rising clock edges[cite: 1]. It provides zero verification coverage for real-world RTL ingress mechanics (e.g., multi-cycle handshake protocols, serial/bus decoding, wire noise, or partial word arrivals) or intermediate register sampling[cite: 1].

2\. **\*\*Omission of Executor-Loss Trace Verification:\*\***

Section *\*Trace properties\** of the Verification Obligations explicitly demands verifying system behavior under \*"executor loss between validation and effect,**\*\*falsified\*\***



**### Defect / Missing Check**



The RTL step module (\`kernel0_step\` in \`docs/research/kernel-0/direct-rtl/kernel0.v\`) omits the model's mandatory non-zero check for requested delegation rights (\`v != 0\`).



In the finite Python model (\`kernel0_finite_model.py\`), \`candidate()\` checks:



\`\`\`python

elif k == "delegate":

    if a not in (0, 1, 2) or t != 3 or not rights[a] or not fresh(t) or not 1 <= v <= 7:

        return None



\`\`\`



Under this rule, a proposal attempting to delegate a rights mask of zero (\`v = 0\`) fails admission and evaluates to a \`deny\` outcome.



However, in \`kernel0.v\`, the guard condition for \`DELEGATE\` omits \`value != 0\`:



\`\`\`verilog

DELEGATE: if (actor_rights!=0 && current_rights==0 &&

              !state_in[7] && (value & \~actor_rights)==0) begin

    proposed[19:17]=value;

    proposed[21:20]=actor[1:0]+2'd1;

    proposed[7]=1;

    admitted=1;

end



\`\`\`



Because \`wellformed\` for \`DELEGATE\` allows \`value != 0\` (\`wellformed = (actor < 3 && target == 3 && value != 0 && other == 0)\`), any attempt to delegate \`value = 0\` passes wellformedness. When evaluated, \`value & \~actor_rights\` evaluates to \`0\`, causing \`admitted = 1\`.



Consequently, presenting a \`DELEGATE\` proposal with \`value = 0\` to the RTL results in a \`commit\` transition where context \`a3\` becomes active with empty rights (\`rights = 0\`), whereas the reference finite model strictly evaluates this to \`deny\` and leaves the state unchanged. The verification suite failed to detect this divergence because \`requests()\` in \`correspondence.py\` only enumerates \`value\` from 1 to 7 for delegation proposals, missing the \`value = 0\` boundary check.

Gemini



**\*\*supported\*\***



Checked the frozen apparatus in \`direct-rtl/\`:



\* **\*\*Combinational law\*\*** - \`verify.py\` builds \`vectors = { valid_states(p) × requests() }\` using \`correspondence.valid_states\` which is defined as *\*all\** invariant-satisfying states including unreachable, with \`parents[:3]==-1\` and exhaustive loops over rights/issued/parent/x/y/content. \`requests()\` = 148 catalog templates × 2 authenticity = 296. For each \`s,q\` it computes \`out,outcome = model.resolve(s,q,p)\` and \`check_edge\`, writes \`%h %h %h %h = state_in proposal expected commit\`.



\`exhaustive_tb.v\` does:



\`\`\`

\#1; if (state_out !== expected || commit !== wanted) $fatal

\`\`\`



for every vector. This directly establishes requirements 1,2,5 of \`Kernel-0-Direct-RTL-Experiment.md\` for every well-formed state/proposal in the declared finite bounds, for all three profiles (independent / coupled / exclusive). Round-trip asserts \`encode/decode\` and \`len({encode})==len(states)\` ensure codec injectivity.



\* **\*\*Register boundary\*\*** - \`boundary_formal.v\`:



\`\`\`

expected_state <= reset ? 0 : valid ? successor : state

expected_resolved <= !reset && valid

expected_committed <= !reset && valid && accept

ok = state==expected_state && ...

\`\`\`



proved with \`yosys sat -seq 2 -prove-skip 1 -prove ok\`. This is a proof for arbitrary \`state,proposal,reset,valid\`, therefore:

 - no partial/intermediate state exposed (req 3)

 - next operation begins from last completed authoritative state (req 4)

 - reset = trusted init to \`0\` only outside interface



Combined with single-step exhaustive, induction gives multi-step correspondence from reset.



\* **\*\*Synthesis/extra\*\*** - \`synthesis-equivalence\` proves \`gold == gate\` for all $2^{37}$ raw \`state/proposal\` combinations, \`boundary\` formal, \`sequence_tb\` exercises reset/idle/loss/replay/conflict traces, and mutation probes (\`always_deny\`, \`forged_authority\` (removes \`authentic\`), \`reuse\` (removes \`!issued\`), \`denied_partial\` (MIXED partial write), \`coupled_invariant\`, \`exclusive_invariant\`) are all detected by the exhaustive vectors.



No declared-domain case is omitted: invalid states (\`s==0\` only for \`!established\`) are outside the claim's domain per \`Direct-RTL-Experiment.md\` § Required correspondence "well-formed state/proposal within declared finite-model bounds". Forged proposals are included as deny-vectors.



Assuming \`kernel0_finite_model.py\` and \`correspondence.py\` and \`iverilog/yosys/abc\` are correct, the apparatus proves bounded correspondence.

Muse Spark



**\*\*falsified\*\***



Smallest concrete defect: the frozen verification apparatus is not pinned to the claimed frozen artifact commit.



\- The review bundle states:  

  **\*\*Frozen artifact commit:\*\*** \`c03bf1c470e54f51c299cb3347c547eeeae0e5ce\`



\- But \`docs/research/kernel-0/direct-rtl/correspondence.py\` defines:  

  \`BASE = "00086d1722a22b481daa834b1e2b0f1a2d3e2b9e"\`



\- And \`docs/research/kernel-0/direct-rtl/evidence/source-manifest.json\` records:  

  \`"baseline": "00086d1722a22b481daa834b1e2b0f1a2d3e2b9e"\`



\`verify.py\` uses that \`BASE\` to assert that every frozen source matches \`git show ${BASE}:...\`. Therefore, as supplied, the verification apparatus either fails against the actual frozen commit or verifies a different source snapshot. It does not bind the RTL/model/verification files to the claimed frozen artifact commit \`c03bf1c\`.



Because the same-ref rule is part of the declared experiment protocol, this mismatch is sufficient to defeat the claim that the frozen apparatus establishes the bounded RTL correspondence for the frozen artifact.

Deepseek
