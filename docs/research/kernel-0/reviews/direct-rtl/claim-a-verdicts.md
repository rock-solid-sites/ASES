**\*\*supported\*\***



The RTL transition law in \`kernel0.v\` matches the finite reference transition in \`kernel0_finite_model.py\` for the enumerated valid states and proposals across the independent, coupled, and exclusive profiles.



The comparison holds at the level of:



\- state encoding (\`encode_state\` / \`decode_state\` ↔ 22-bit RTL state),

\- proposal encoding (\`encode_request\` / \`decode_request\` ↔ 15-bit RTL proposal),

\- validity/invariant checks (\`model.invariant\` ↔ RTL \`valid_state\`),

\- per-operation admissibility and whole-effect state updates (\`candidate\` / \`resolve\` ↔ RTL \`kernel0_step\`),

\- profile parameters (\`Profile.coupled\`, \`Profile.exclusive\` ↔ \`COUPLED\`, \`EXCLUSIVE\`).



No concrete mismatch was found in the checked operation set, including the inauthentic variants and the mixed composite proposal. The RTL denies exactly where the reference denies and commits exactly where the reference commits, preserving the same successor state.

Deepseek



**\*\*supported\*\***



Independent exhaustive check over the frozen bundle shows complete agreement.



Method:

\- Re-implemented \`encode_state/decode_state\`, \`encode_request/decode_request\`, \`valid_states\` exactly as in \`correspondence.py\` – enumerates **\*\*all invariant-satisfying states, including unreachable\*\***, as stated.

\- Re-implemented RTL \`kernel0_step\` transition in Python directly from \`kernel0.v\` Verilog: \`valid_state()\` (coupled check \`s[1]&&s[2]\`, exclusive check, issued-bits \`s[4+i]\`, parent subset \`r3 & \~parent_rights\`), \`wellformed\` for the 148 catalog templates, admission for ESTABLISH/GRANT/RESTRICT/REPLACE/DELEGATE/SET/FLIP/ACCEPT/RESUME/PAIR/MIXED, and \`commit = admitted && valid_state(proposed)\`.

\- Compared against reference \`kernel0_finite_model.py\` \`candidate()\` / \`resolve()\` + \`invariant()\`.



Enumeration:

\- **\*\*independent:\*\*** 8,449 valid states × 296 proposals (148 authentic + 148 forged) = 2,500,904 checks

\- **\*\*coupled (\`x+y≤1\`):\*\*** 6,337 × 296 = 1,875,752 checks

\- **\*\*exclusive (single active):\*\*** 1,921 × 296 = 568,616 checks

\- **\*\*total 4,945,272 transitions\*\***



For every case:

\- \`rtl_valid_state\` == \`model.invariant\`

\- \`rtl_commit\` == (\`py_outcome == "commit"\`)

\- \`rtl_state_out_enc\` == \`encode_state(py_out)\`; decode roundtrips.



No mismatch. Under the stated assumptions (authentic bit is trusted ingress premise, \`reset\` is trusted initialization outside executor interface, submission and resolution coincide in \`kernel0_machine\`, no independent authority-service/storage failure, parent field only for child 3), the RTL authoritative transition \`kernel0_step\` refines the finite reference.

Muse Spark



**\*\*supported\*\***



Independent exhaustive check over the frozen bundle shows complete agreement.



Method:

\- Re-implemented \`encode_state/decode_state\`, \`encode_request/decode_request\`, \`valid_states\` exactly as in \`correspondence.py\` – enumerates **\*\*all invariant-satisfying states, including unreachable\*\***, as stated.

\- Re-implemented RTL \`kernel0_step\` transition in Python directly from \`kernel0.v\` Verilog: \`valid_state()\` (coupled check \`s[1]&&s[2]\`, exclusive check, issued-bits \`s[4+i]\`, parent subset \`r3 & \~parent_rights\`), \`wellformed\` for the 148 catalog templates, admission for ESTABLISH/GRANT/RESTRICT/REPLACE/DELEGATE/SET/FLIP/ACCEPT/RESUME/PAIR/MIXED, and \`commit = admitted && valid_state(proposed)\`.

\- Compared against reference \`kernel0_finite_model.py\` \`candidate()\` / \`resolve()\` + \`invariant()\`.



Enumeration:

\- **\*\*independent:\*\*** 8,449 valid states × 296 proposals (148 authentic + 148 forged) = 2,500,904 checks

\- **\*\*coupled (\`x+y≤1\`):\*\*** 6,337 × 296 = 1,875,752 checks

\- **\*\*exclusive (single active):\*\*** 1,921 × 296 = 568,616 checks

\- **\*\*total 4,945,272 transitions\*\***



For every case:

\- \`rtl_valid_state\` == \`model.invariant\`

\- \`rtl_commit\` == (\`py_outcome == "commit"\`)

\- \`rtl_state_out_enc\` == \`encode_state(py_out)\`; decode roundtrips.



No mismatch. Under the stated assumptions (authentic bit is trusted ingress premise, \`reset\` is trusted initialization outside executor interface, submission and resolution coincide in \`kernel0_machine\`, no independent authority-service/storage failure, parent field only for child 3), the RTL authoritative transition \`kernel0_step\` refines the finite reference.

Gemini



**\*\*Supported\*\***, within the claim's stated scope.



I extracted \`kernel0.v\`, \`kernel0_finite_model.py\` and \`correspondence.py\` from the bundle and ran the RTL step module under Icarus Verilog 12. I did not use the bundle's own correspondence test, which isn't in the bundle. For each of the three profiles (independent, coupled, exclusive) I fed it every invariant-satisfying 22-bit state, including unreachable ones. Each state was paired with all 148 catalog proposals, in both authentic and inauthentic variants (296 proposals). I compared the resulting state and commit bit against \`resolve()\` in the Python reference.



\| Profile | States | Pairs compared | Mismatches |

\| --- | ---: | ---: | ---: |

\| independent | 8,449 | 2,500,904 | 0 |

\| coupled | 6,337 | 1,875,752 | 0 |

\| exclusive | 1,921 | 568,616 | 0 |



The state enumeration is a superset of the model's reachable counts (8,442, 6,332 and 1,914), so the match does not depend on reachability. As a check on the harness, I removed the delegate-cascade masking in the restrict case of a copy of the RTL. The comparison then reported 5,856 mismatches in the independent profile.



Three things bound this result:



\- **\*\*Proposal alphabet:\*\*** malformed wire words and the unmodeled rest of the 15-bit proposal space are outside the claim's "compared proposals". The RTL's \`wellformed\` gate denies them, and I did not test them.

\- **\*\*Clocked wrapper:\*\*** \`kernel0_machine\` was read, not simulated. The step module is purely combinational, and the wrapper's "state updates only when \`valid\`" behavior is simple enough to confirm by inspection. The claim's "stated realization assumptions", such as single-edge sampling and trusted reset, are taken as given.

\- **\*\*Non-state outcomes:\*\*** the check covers committed state and the commit bit. Request pending, lost acknowledgements and executor death are not modeled in the RTL.

Claude



Verdict: SUPPORTED

The claim holds. I established it by actually executing the frozen Verilog against the frozen Python reference, not by inspecting them.

How

No simulator was installed and I had no root, so I extracted Debian's iverilog 11.0 manually (dpkg-deb -x, run with -B\<ivl>) and drove the frozen kernel0_step/kernel0_machine directly. The bundle's correspondence.py ends at requests() with no RTL driver, so there was no existing test to lean on; I wrote my own testbenches and driver.

I confirmed the Python source is the frozen one: its self-reported SHA-256 matches my copy, and its own searches reproduce the documented 8,442 / 6,332 / 1,914 states and 1,249,416 / 937,136 / 283,272 edges.

Result

Check   Vectors Mismatches

Exhaustive kernel0_step vs resolve, 3 profiles  4,945,272   0

Clocked kernel0_machine, full reachable closure 2,595,088   0

Stratified sweep of all 32,768 proposal words   12,582,912  0

Random full-space pairs 2,100,000   0

Domain: 8,449 / 6,337 / 1,921 valid states × 296 proposals (148 catalog templates × authentic/forged). Non-vacuous — 310,000 commit vectors exercised. Zero X/Z outputs. Closure coverage complete (8442/8442, 6332/6332, 1914/1914), with reset and idle cycles included.

Preconditions I audited rather than trusted: valid_states() is complete (brute-forced the entire encoded domain; 0 missing); all 296 codecs round-trip; catalog size independently recounted to 148. I also verified invariant forbids parents[0..2] != -1, so the RTL's child-3-only 2-bit parent field is a complete encoding — no representation gap.

Why you can trust a null result

A clean run means nothing unless the harness can fail, so I mutation-tested it. Control clean; 14 of 17 mutants killed (dropped no-reuse witness, dropped restrict cascade, resume ignoring content, pair bit order, dropped COUPLED, dropped EXCLUSIVE, caller-asserted authenticity, denial leaking the candidate, etc.).

Three mutants survived, and all three are provably equivalent in-scope — each agrees with the original RTL on all 4,945,272 compared vectors. I confirmed this rather than assuming it, and located each difference outside the domain. For the one with a concrete witness: original RTL denies establish from state word 0x7f0; the mutant commits to 0x7f1 — but the reference codec explicitly refuses to decode that word ("noncanonical absent state").

Scope — do not overread this

The equivalence is a transition-law result on a single-proposal, single-threaded interface. The RTL is a pure function of (state, proposal): no concurrency, executor lifetime, ingress/freshness, source binding, external sink, or persistence. Kernel-0-Finite-Model.md itself says the correspondence obligation "establishes the need for a correspondence obligation; it does not discharge it." I discharged exactly the transition-law part.

Three further points worth flagging:

1\. Outside the alphabet the reference is undefined, not "deny." decode_state raises on non-canonical absent states; candidate() raises IndexError on e.g. set with target=3. So there is no reference behaviour to match there. I checked the RTL isn't more permissive anyway (0 commits outside the catalog across 14.7M vectors).

2\. The RTL has redundant guards. commit = admitted && valid_state(proposed) makes the delegate-attenuation and replace-freshness checks individually unobservable in emitted behaviour. Defence in depth, not a defect — but don't delete them expecting observable change.

3\. authentic is a wire bit in both models. The models agree, so the verdict is unaffected — but the agreement is conditional on ingress being trusted, exactly as the docs state.

Minor bundle hygiene: correspondence.py lists two absent files in SOURCES, and its BASE is 41 hex characters (not a valid 40-char SHA). BASE/SOURCES are unused in the supplied portion; no semantic impact.

Build · Space Bunny Free · OpenCode Zen · tools OK · free stale 3.8d · 27m 16s · 38.3 tok/s
