---
title: Kernel-0 Direct RTL Realization Result
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 575
last_updated: 2026-10-01
depends_on:
  - Kernel-0-Direct-RTL-Experiment.md
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
  - Kernel-0-Finite-Model.md
  - kernel0_finite_model.py
  - Kernel-0-Re-Minimization.md
consumed_by:
  - Kernel-0 direct realization research assessment
implements: []
implemented_by: []
---

# First direct RTL experiment

**Result: the declared bounded target has a synthesizable fixed RTL realization.**
All three profiles passed exhaustive oracle correspondence, sequential traces,
register-boundary SAT checks, and post-synthesis transition equivalence. The
protocol's first stopping condition is met. No tested behavior forced runtime
iteration, a processor, or general programmability. This is conditional on the
specified trusted ingress, initialization and synchronous holder assumptions.

## Experiment boundary

The governing packet is the six files above, all read from
`00086d1722a22b481daa834b1e2b0f1a2d3e2b9e`, the supplied head of
`codex/kernel-0-reasoning-566`. The fresh experiment branch is
`codex/kernel-0-direct-rtl-00086d17`. The [source manifest](./direct-rtl/evidence/source-manifest.json)
records their SHA-256 hashes; the reproducer checks each working file byte for
byte against that commit before testing. No semantic input was modified.

The protocol governs experiment scope. The abstract semantics and verification
obligations govern meaning. The finite model supplies the bounded target and
oracle. Re-minimization constrains mechanism claims. Historical service-oriented
directions in the finite-model narrative and stronger-profile material in
re-minimization were not adopted as requirements. Their linked architectures
were not loaded. Operational repository rules were used for branch/issue/commit
handling, not as additional semantic inputs.

The realized target is the authoritative `State`/`Request`/`resolve` system for
each of the model's three profiles: independent, coupled, and exclusive. The
separate asynchronous, content-loss, and three-bit history fixtures remain
assurance apparatus; their control state is not silently added to the hardware
state. The original fixture checks were rerun and their results retained.

## Realization and correspondence

[kernel0.v](./direct-rtl/kernel0.v) has a fixed combinational transition module
and a synchronous `kernel0_machine` wrapper. The latter is the authoritative
machine. It has one whole-proposal input and no instruction stream, interpreter,
processor, microcode, scheduler, heap, operating system, or software runtime.
Profile parameters are build-time constants. Neither proposals nor profile
inputs can redefine the transition law at runtime.

The encoded authoritative state has **22 bits**:

| Bits | Meaning and decoding |
| --- | --- |
| 0 | Established; the sole legal absent state is the all-zero word. |
| 1, 2 | Boolean work fields `x,y`. |
| 3 | Complete bounded content value 0 or 1 when established; decode absence as -1 before establishment. |
| 4–7 | Four issued-context bits, never cleared during operation. |
| 8–10, 11–13, 14–16, 17–19 | Three rights for contexts a0, a1, a2, a3 respectively. |
| 20–21 | Parent of a3: 0 means absent, 1/2/3 means a0/a1/a2. The other three parents are always absent. |

The work identity and two position associations are interpretation constants
selected by the established bit, exactly as in the bounded model. Contexts
a0–a2 share position 0; a3 belongs to position 1. The content bit retains all
information in the selected two-element payload alphabet. It is not a digest or
a reference to executor-owned storage, and does not demonstrate retention of
arbitrary external byte strings.

The **15-bit proposal** has opcode at 0–3, authority observation at 4–6
(a0–a3 = 0–3; manager = 4), target at 7–8, value at 9–11, replacement context
at 12–13, and trusted authenticity verdict at 14. Opcode order is establish,
grant, restrict, replace, delegate, set, flip, accept, resume, pair, mixed.
Only the 148 exact catalog templates and their false-authenticity variants
belong to the compared input alphabet. Other encodings are denied by the RTL,
but are not counted as model-equivalence evidence.

The codecs in [correspondence.py](./direct-rtl/correspondence.py) are explicit
encoding/decoding functions. Round-trip identity and injectivity are checked
over every valid state and each compared input. There is no generated
transition lookup table: expected successors are obtained by calling the
unchanged Python oracle, and the RTL implements the guard/effect logic separately.

For each encoded legal state `s` and catalog request `q`, the comparator checks
both output fields, including commitment stutters:

```text
(decode(step(encode(s), encode(q)).state), step(...).outcome)
    = resolve(s, q, profile)
```

The RTL computes a whole candidate from the current register, checks the
configured invariant, and selects that candidate only on commitment. A denial
selects the unchanged register word. Cascading child attenuation, replacement
withdrawal, no-reuse, mixed-proposal denial, and all rights/content effects are
in this fixed logic. Constant-bound loops elaborate into gates; they do not
iterate at runtime.

### Completion and observations

At a rising edge, trusted initialization resets the machine, or `valid=1`
presents one whole proposal and resolves it against the immediately preceding
authoritative state. Submission and resolution coincide at this boundary.
`valid=0` means no submitted proposal and preserves all authoritative state.
Thus no pending-envelope buffer or multi-cycle controller is needed in this
first realization. An unsubmitted caller may wait indefinitely.

The two additional output registers, `resolved` and `committed`, distinguish
no proposal, denial, and commitment. They are not part of the authoritative
state. The machine therefore contains **24 one-bit registers** in total. An
unobserved completion pulse does not roll back a change; a later repeated flip
is a new proposal and may commit again.

Only the registered state, sampled according to the synchronous timing
contract, is authoritative. Internal combinational candidates are not published
as Kernel transitions. Between valid edges there is no authoritative change;
at a valid edge the entire register takes one successor. The next operation
uses that register, not an earlier validation cache. This gives a common edge
order for all admitted proposals, including conflicts and acknowledged-before-
initiated precedence. Total serialization of this one small machine is a
realization choice, not a universal semantic ordering requirement.

Executor loss does not reset or power down the machine. Loss before sampling
can leave no submitted operation; loss after a correctly sampled edge cannot
remove authority or accepted content. There is no partly copied envelope after
acknowledged submission because the submission event is the whole-vector
sampling edge. The interface does not promise acceptance of simultaneous
sources or partially transmitted messages. A transport or arbiter would need
its own refinement if later introduced.

## Verification evidence

The machine-readable [results](./direct-rtl/evidence/results.json) carry the
completed status, exact counts, mutation counterexamples, tool versions,
timings, peak resident memory and implementation hashes. The
[command record](./direct-rtl/evidence/commands.json) and generated Yosys scripts
make the checks reproducible.

| Profile | All valid states | Reachable states | State/proposal/authenticity comparisons |
| --- | ---: | ---: | ---: |
| Independent | 8,449 | 8,442 | 2,500,904 |
| Coupled | 6,337 | 6,332 | 1,875,752 |
| Exclusive | 1,921 | 1,914 | 568,616 |
| Total | 16,707 | 16,688 | 4,945,272 |

The state generator enumerates every value of the bounded fields and retains
exactly those satisfying the oracle invariant. It does not use reachability
to discard inconvenient states. Each state receives the 148 authentic catalog
proposals and all 148 false-authenticity counterparts. These counterparts add
forgery-denial checks; the original authoritative alphabet itself has 148
templates. Closure and every original `check_edge` invariant are checked.
Reachability reconstructed from the resulting graph agrees with all three
original graph counts. The 19 extra valid states are deliberately retained.

The evidence layers are distinct:

1. **Oracle regression:** the unchanged model reruns its 2,469,824 reachable
   proposal edges, nine asynchronous fixtures, 4,096 history cases, content
   fixtures, loss cuts, and original deliberate mutants. These are model
   results, not hardware execution counts.
2. **Exhaustive RTL simulation:** Icarus compares complete successor words and
   outcomes with the oracle for the 4,945,272 combinations above. Generated
   vectors are hashed and reproducibly regenerated rather than committed as
   roughly 100 MB of redundant output.
3. **Clocked sequences:** the actual register wrapper executes positive
   continuation, two replacements, both race orders, revocation/replay,
   delegation/attenuation, mixed and pair effects, forgery, content retention,
   conflicting writes and competing grants. Idle cycles change source inputs
   without changing authoritative state; observations before edges test absence
   of premature publication. Per-profile traces record actual input sequences
   and expected oracle states; simulation compared the actual outputs to every
   recorded expected state/outcome. Host/executor destruction and physical failures
   are not simulated by these idle cycles.
4. **Register-boundary SAT proof:** from an arbitrary defined register state,
   one subsequent edge satisfies reset, valid-gated whole successor publication,
   idle retention, and outcome-register correspondence. The first comparison
   is skipped because monitor registers have arbitrary initial values; the
   next comparison covers every preceding state/input choice. This is a
   universal one-step transfer result, not an unbounded physical-clock proof.
5. **Post-synthesis transition SAT equivalence:** ABC-mapped transition logic
   is equivalent to the elaborated RTL for every raw 22-bit state and 15-bit
   proposal input, including encodings outside the semantic claim. This
   checks the combinational law; it does not validate FPGA placement or silicon.
6. **Checker sensitivity:** RTL mutants that always deny, trust forged
   authority, reuse issued contexts, or change state on a denied mixed
   proposal must fail the same comparator. The coupled/exclusive invariant
   removal mutants are checked in their respective profiles. Failure is
   required and its concrete mismatch is recorded, not treated as a passing run.

Codec completeness, exhaustive one-step equality, closure, and the register
transfer result support induction over arbitrarily long sequences **within
these fixed finite profiles**, with reset excluded after initialization. This
does not extend the population, delegation depth, content alphabet, ingress
trust or failure class. The separate three-bit cycle fixture is not an extra
hardware opcode or state dimension. The hardware admits no independently
cached validations: each accepted edge has the whole current view.

## Mechanism ledger and trusted assumptions

| Mechanism or distinction | Classification | Evidence / limit |
| --- | --- | --- |
| Current authoritative view, guarded whole effect, no-effect denial | Semantic requirement | Oracle correspondence checks all retained state and outcome bits. |
| Current versus old authority and trustworthy distinguishable attempts | Semantic requirement | Non-reuse and current-right checks reject stale contexts; ingress trust remains external. |
| Continuing information independent of executor lifetime | Semantic requirement | Retained state has no executor-loss input; accepted bounded content is in the register. |
| Four issued bits, twelve rights bits, two parent bits | Realization choice for the supplied finite policy | Effective distinctions are concretely retained. Fresh-context exhaustion denies; no wraparound or reclamation is added. |
| 22-bit encoding and fixed combinational guard/effect network | Realization choice | Exhaustive codec/transition checks; synthesized gates, no runtime program. No minimal-gate claim. |
| Synchronous register and sole publication edge | Realization choice with timing assumptions | Whole-state transfer checked in RTL/SAT. Clock/reset integrity and physical timing are trusted. |
| Single whole-proposal port and total edge order | Realization choice | No simultaneous-source arbiter is required by this interface. Throughput/latency are not a semantic guarantee. |
| Valid qualifier and two registered outcome bits | Realization choice | Needed to distinguish no presented proposal from resolved deny/commit. No request log, deduplication, or acknowledgement protocol. |
| Build-time profile constants | Realization choice | Three separately synthesized policies; no runtime configurable transition law. |
| Trusted management/authority observation and authenticity verdict | Realization assumption | Supplied at the hardware boundary; this experiment does not build an authenticator. A caller-controlled authenticity bit would invalidate the claim. |
| Complete stable proposal at the sampling edge | Realization assumption | Source must satisfy setup/hold and whole-envelope association. No torn/asynchronous ingress claim. |
| Surviving register, trusted initialization, clock and policy configuration | Realization assumption | Executor failure excludes failure of this holder, its clock, reset, power and retained bits. |
| Python oracle, enumeration, codecs, testbenches, SAT and synthesis tools | Assurance scaffolding | Run outside the trusted transition machine. Tool and specification correctness remain trusted for the evidence. |
| Host OS, package downloads, temporary files, logs and Git | Assurance scaffolding | Laboratory/reproducibility machinery; absent from the synthesized machine. |

Neither a caller nor an executor may assert management/authenticity by setting
ordinary request payload bits, reset the holder, or write its state register.
The encoded authority observation and authenticity verdict must come from a
trusted ingress association. Authentic/forged simulations check the transition
law's treatment of that premise; they do not prove the premise. Physical source
exclusion after obtaining genuinely new transferable evidence is not claimed.

The synchronous abstraction assumes settled sampling with setup/hold satisfied,
coherent clocking, and protected reset. Analog glitches, metastability, clock
skew, fault injection, gate delays and power loss are not covered. In particular,
the 22 output bits are not claimed to switch at the same physical instant for
an asynchronous observer. No persistent-storage, service-restart, protected
external-sink or arbitrary-content assurance was imported.

## Reproduction

On Linux with Python 3.10+, Icarus Verilog, Yosys and Berkeley ABC available,
run from the experiment checkout:

```sh
python3 docs/research/kernel-0/direct-rtl/verify.py
```

Explicit executable paths and a relocated Icarus backend directory are accepted
by `--iverilog`, `--ivl-base`, `--vvp`, `--yosys`, and `--abc`. This run used
Ubuntu packages extracted into a temporary directory because no RTL tools were
preinstalled; no system installation was needed. The command record includes
those concrete paths. They are lab locations, not dependencies of the RTL.
`--build` holds disposable vectors, binaries, mutations and netlists;
`--evidence` holds retained results. A run sets its status to INCOMPLETE before
work and emits PASS only after all three profiles and all required checks pass.
Python optimization is rejected so verification assertions remain enabled.

## Research decision

The complete machine was synthesized with Yosys 0.9 and Berkeley ABC 1.01 to
technology-independent basic gates. Each profile has 24 flip-flops, zero
latches, and zero memory blocks. The count includes all input decoding,
state-validity checks, guard/effect logic, publication gating and outcome logic.

| Profile | Combinational cells | Total cells including 24 flip-flops | Longest combinational path, cell levels | Synthesis wall time | Exhaustive simulation wall time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Independent | 873 | 897 | 29 | 3.18 s | 49.61 s |
| Coupled | 814 | 838 | 27 | 2.94 s | 37.64 s |
| Exclusive | 799 | 823 | 29 | 3.04 s | 11.09 s |

These are basic gate-cell counts, not FPGA LUT utilization, area, timing closure,
power, or a maximum clock frequency. The machine can resolve one proposal per
correctly timed clock edge; this experiment selects no physical clock period.
Vector generation took 34.19/25.84/7.51 seconds respectively; the unchanged
reference regression took 28.96 seconds. Each profile also passed 173 clocked
sequence cycles. Each boundary/equivalence SAT job finished within four seconds.
Per-command Linux `wait4` RSS measurements are retained; their 83,864 KiB peak
includes the forked Python launcher's pre-exec image, so it is a conservative
child-lifetime measurement rather than isolated Yosys/Icarus memory use.

The bounded realization is practical at this measured scale. Its state storage
is required by the continuing-view and non-reuse distinctions; its precise
register encoding is replaceable. Its edge ordering supplies coherent admission
and whole publication. No data-dependent iteration, new storage hierarchy,
buffer, arbiter, programmable controller, or general runtime program was forced
by the target. This does not prove that such mechanisms would be unnecessary
for a larger consumer, a different interface, or stronger failure claims.

The first stopping condition is satisfied: the implementation has an explicit
model mapping, exhaustive bounded correspondence, and synthesis/tractability
evidence. No obstruction or escalation condition was reached. The experiment
therefore stops here without selecting a physical substrate or broadening into
other EDASES layers.

**WHY:** fixed gates and a small retained register implement every tested
bounded successor and outcome; measured synthesis and complete enumeration are
tractable. **WHAT:** 4,945,272 direct oracle/RTL comparisons, 519 sequential
cycles, three arbitrary-state boundary proofs, three post-synthesis transition
equivalence proofs, 14 detected RTL mutation runs, the original model regression,
and recorded gate/resource measurements. **HOW CERTAIN:** evidence-based
bounded realization result, with exhaustive digital transition agreement and
SAT proofs conditional on the codecs, oracle, tools and stated trust premises;
not a universal minimality result. **WHAT-NOT-TESTED:** independent review,
physical authentication/source binding, FPGA place-and-route or board execution,
analog timing/metastability, hostile reset or state corruption, holder power
loss/restart, arbitrary content or populations, extra delegation depth,
external-effect sinks, concurrent ingress transport, fairness and exactly-once
delivery. The model's ideal ingress premise is explicitly still an assumption.
