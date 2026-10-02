---
title: Kernel-0 Fixed Ingress Assumption Reduction
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 576
last_updated: 2026-10-02
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
  - Kernel-0-Direct-RTL-Experiment.md
  - Kernel-0-Direct-RTL-Result.md
  - Kernel-0-Finite-Model.md
  - Kernel-0-Re-Minimization.md
consumed_by:
  - Kernel-0 realization assumption assessment
implements: []
implemented_by: []
supersedes: []
---

# Bounded experiment protocol and result

**Result: a bounded structural reduction of ingress, conditional on protected
lane access.** Fixed wiring replaces the externally supplied authority label and
authenticity verdict. The machine preserves all 148 authentic bounded proposals
and their outcomes in all three profiles. It retains the same 22 authoritative
bits and 24 total registers, with no new sequential controller. Trustworthy
origin is not eliminated: if a stale caller can drive the current context's lane,
the recorded counterexample still commits. Synchronous timing is unchanged.

Baseline: `c03bf1c470e54f51c299cb3347c547eeeae0e5ce`, branch
`codex/kernel-0-direct-rtl-00086d17`. Work is isolated on
`codex/kernel-0-ingress-reduction-c03bf1c`. All governing inputs and the entire
direct RTL artifact remain byte-for-byte unchanged. This is a research witness,
not a new Kernel definition or execution-engine architecture.

## Decision recorded before implementation

Test one reduction: eliminate the runtime ingress authenticity verdict and
caller-carried authority label by fixed, separately protected context/management
ports. Keep the synchronous timing contract. This replaces an unspecified
per-request classifier with fixed gates and an explicit static port-access
premise. It does not eliminate trustworthy origin, prove physical isolation,
or claim a universally weaker physical trust boundary.

Before implementation, `ingress-reduction/preflight.py` tests whether removing
all trustworthy distinctions is possible. After establishment, grant a0 and
replace a0 with a1. The same work payload must deny on a0 and commit on a1.
If both callers can present the same current-authority observation, a fixed
decision cannot deliver both required outcomes. Always-deny loses the bounded
model's non-vacuity. The minimum residual requirement is one non-confusable
admission observation, here realized as exclusive access to fixed lanes.

Synchronous timing supplies whole-envelope association, current-view validation,
whole-state publication, and a common order for interacting commitments. Removing
it from the existing circuit without replacement permits a valid but wrong
intermediate state: an independent-profile pair `(0,0)->(1,1)` can expose `(1,0)`.
A torn request between pair values 0 and 3 can also encode valid value 1. Neither
is rejected merely by checking the state invariant. These are abstract cut
witnesses, not simulations of analog behavior. A global periodic clock is not a
semantic requirement; coherent completion and observation are. A clockless
replacement would need a separate whole-envelope capture/completion protocol,
retained state and timing/observation refinement. Merely adding a handshake or
independent bit synchronizers would not establish that refinement. It is not
the selected experiment.

## Boundary and stopping rule

Five input lanes are permanently associated with a0, a1, a2, a3 and manager.
Each has only an 11-bit effect payload and a valid signal. The port number does
not itself confer rights: the unchanged Kernel state still decides eligibility.
Only an exactly-one-valid edge submits a proposal. Zero or several valid lanes
means no submission, no resolution and no state change. Sources may retry;
there is no fairness, simultaneous-source service or buffering guarantee.

No processor, interpreter, program store, mutable routing table, new authority
state, scheduler, arbiter with priority, or runtime controller will be added.
Stop after explicit baseline correspondence, bounded oracle regression, clocked
attack/continuation traces, synthesis and checker-sensitivity evidence succeed;
or preserve a concrete obstruction if they fail. Physical isolation and timing
remain outside this digital experiment. Do not undertake a second reduction.

## What the two assumptions contribute

| Assumption in the frozen claim | What it supplies | What removal permits | Weakening assessment |
| --- | --- | --- | --- |
| Trusted management/context observation and authenticity verdict, bound to the whole proposal | Makes `q.evidence` and `q.authentic` meaningful inputs to the current-rights guard. The core checks freshness and rights; it cannot infer origin from caller-controlled data. | At the same post-replacement state, a stale source asserts a1 and authentic=true and obtains the current source's successful transition. An unprivileged source able to assert manager can issue authority-changing requests. Non-reuse does not repair forged current evidence. | The **external per-request verdict mechanism** can be replaced by the fixed circuit below. Non-confusable origin and the source of initial management authority remain trusted requirements. No claim that all trust has disappeared or that the physical assumptions are strictly weaker in every deployment. |
| Complete stable proposal, coherent clocking, settled observation and whole register update | Makes one request correspond to one effect, supplies the current view used by admission, and yields a common acyclic order for dependent commitments. Idle cycles retain the view; the sampled edge separates unsubmitted from resolved work. | A torn proposal can become a different well-formed proposal; a partly visible publication can satisfy `I` while violating `E`. Without any advancing edges this RTL can simply stop, losing successful histories. | Periodicity and a universal wall-clock time are not Kernel requirements. The baseline already chooses no clock period. A paused or irregular edge sequence still needs settled sampling, coherent publication and sufficient settling time. An asynchronous replacement is possible in principle only with an explicit equivalent completion/observation contract; this experiment neither constructs nor verifies one. |

The [preflight evidence](./ingress-reduction/evidence/preflight.json) records the
full before/after states, request words and the two Boolean decisions possible
when both origins have been collapsed to one observation. Required decisions
`[deny, commit]` are absent from `[deny, deny]` and `[commit, commit]`. This is a
bounded indistinguishability obstruction at the same state and same visible
input, not a cryptographic impossibility claim. Giving a hidden discriminator to
the circuit would reintroduce the missing assumption. The abstract contract can
permit denial, but the selected bounded oracle and successful-continuation
obligation prevent always-deny from being a substitute realization.

For timing, the witness uses the independent profile's permitted atomic pair
with current a1: before `(0,0)`, committed successor `(1,1)`, torn observation
`(1,0)`. The torn observation is invariant-valid but is neither endpoint of that
proposal. The two proposal words for pair values 0 and 3 also admit the bitwise
mixture encoding value 1, which the unchanged oracle commits. This demonstrates
why simply dropping the timing premise leaves the existing proof inapplicable;
it does not demonstrate that any particular fabricated circuit produces the cut.
The minimum additional requirement is a trustworthy whole-event boundary and
coherent current-state observation, not necessarily a global clock or processor.

## Realization and exact correspondence

[fixed_ingress.v](./ingress-reduction/fixed_ingress.v) contains a combinational
selector plus an instance of the **unchanged** `kernel0_machine` from
[direct-rtl/kernel0.v](./direct-rtl/kernel0.v). The selector has no state or
runtime routing configuration. Its permanent lanes are a0, a1, a2, a3, manager.
The 11-bit payload is:

```text
bits 0..3: opcode; 4..5: target; 6..8: value; 9..10: replacement context
```

At every correctly timed edge define the input abstraction `A`:

```text
exactly one lane i valid:
    baseline.valid = 1
    baseline.proposal = {authentic=1, payload.other, payload.value,
                         payload.target, actor=i, payload.opcode}
otherwise:
    baseline.valid = 0
    baseline.proposal = 0  (ignored by the idle baseline)
```

Actor 4 decodes to the oracle's manager value -1. The authoritative abstraction
is **exactly the frozen 22-bit state decoder**, including issued bits, parent
and retained content. Registered `resolved` and `committed` retain their frozen
meaning. This is a shared completion interface; it does not add per-source
acknowledgements. Sources must observe the unique-submission condition at the
sampling boundary. Collision is not a denied or committed batch: **nothing was
submitted**, and the register remains unchanged. A continuously asserted other
lane can prevent submission forever, which is within the declared no-progress
boundary. This is a concrete interface contract, not a claim to accept arbitrary
asynchronous messages or to resolve concurrent callers fairly.

For each legal `s` and catalog `q`, route the effect fields to the lane named by
`q.evidence`. The map is injective on the 148 authentic templates and recovers
the identical frozen proposal word. Consequently the claim is:

```text
decode(new_machine_edge(encode(s), lanes(q)).state), outcome
    = resolve(s, q, profile)
```

At non-submission edges it is the baseline idle step. At initialization it is
the baseline reset step. Only registered, correctly sampled output is
authoritative. Malformed lane payloads map to raw baseline encodings and are
handled by its existing decoder; they are not counted as new Kernel proposals.

The 148 false-authenticity variants remain covered by the baseline rerun, but
are **not** counted as new-interface semantic comparisons. There is no external
verdict bit to drive false or true. An attempted data-only impersonation is
instead a request on the attacker's actual lane. Driving someone else's lane
is excluded by the physical/interface premise, not detected by this circuit.
The all-input SAT proof quantifies even over the manager lane; it proves the
mapping, not that an unauthorized source cannot drive that lane.

Every positive bounded transition remains expressible, including management,
two replacements and current continuation. Potential replacement endpoints are
associated with their lanes in advance; granting a context changes rights in
the existing register, not the wiring. This fixes the finite interface and does
not realize arbitrary bearer transfer, hot reconnection or unlimited contexts.
No new exclusion claim is made about a former physical producer genuinely given
new current authority. Initial management, lane access and any later reassignment
must be accounted for by a deployment that makes a stronger claim.

## Verification and tractability evidence

The retained [results](./ingress-reduction/evidence/results.json) contain tool
versions, exact command arguments, return codes, measurements, vector hashes and
implementation/checker hashes. The [source manifest](./ingress-reduction/evidence/source-manifest.json)
checks every tracked baseline RTL/evidence file and all governing inputs against
the frozen Git objects. The checker sets INCOMPLETE before work, emits PASS only
after all required stages, and checks that its source files did not change during
the run. Generated multi-megabyte vectors and netlists are reproducible build
outputs; their hashes, not their redundant contents, are retained.

| Profile | All legal states | Authentic oracle/RTL comparisons | Raw lane attack checks | Clocked cycles | New total cells (baseline) | Registers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Independent | 8,449 | 1,250,452 | 10,240 | 206 | 943 (897) | 24 |
| Coupled | 6,337 | 937,876 | 10,240 | 206 | 1,114 (838) | 24 |
| Exclusive | 1,921 | 284,308 | 10,240 | 206 | 1,079 (823) | 24 |
| Total | 16,707 | 2,472,636 | 30,720 | 618 | — | — |

Evidence layers and their limits:

1. **Frozen baseline regression:** its unchanged reproducer passed all
   4,945,272 state/proposal/authenticity comparisons, 519 sequential cycles,
   original model checks, three boundary proofs, three transition-synthesis
   proofs and 14 detected RTL mutation runs. Its new output is kept separately
   in [baseline-rerun](./ingress-reduction/evidence/baseline-rerun/results.json).
2. **Universal input mapping:** SAT establishes the independent relation above
   for all `2^60` defined input combinations (five valids plus 55 payload bits).
   This includes every collision pattern, every malformed payload and arbitrary
   changes in inactive lanes. Since the relation depends only on the selected
   lane's payload, it also establishes inactive-payload noninterference.
3. **Direct oracle comparison:** Icarus executes the new selector composed with
   the frozen transition logic against each legal-state/authentic-template
   combination. The unchanged oracle supplies expected states and outcomes;
   `check_edge` and legal-state closure also pass. Reachability is not used to
   discard the 19 legal but unreachable states. These are digital one-step
   comparisons, not physical source authentication tests.
4. **Raw attack domain:** after a0 is replaced by a1, all 2,048 possible payloads
   on each of the five lanes are checked in each profile. **Zero** payloads on
   stale lane a0 commit. Requests using management opcodes from worker lanes
   cannot turn into manager requests. Catalog matches use oracle outcomes;
   noncatalog encodings use the frozen explicit deny contract and are counted
   separately. These checks do not assume that all malformed payloads are
   abstract Kernel proposals.
5. **Clocked correspondence:** the real wrapper runs the frozen successful,
   revocation, replacement, delegation, conflict, composite, loss/idle, content
   and replay histories, omitting false-verdict cycles that have no new input
   representation. Added histories cover every non-one-hot valid pattern,
   reset priority, retained accepted content, stale-lane denial and current
   continuation. Inputs change between edges without premature publication.
   Executor loss here means loss before submission or idle source withdrawal;
   no physical power-loss test is implied.
6. **Boundary proof:** in each profile, a universal register-transfer proof
   computes expected outputs from the independent `A` relation and frozen
   transition law at the machine's arbitrary defined current state. The first
   monitor comparison is skipped because its history registers start arbitrary.
   The subsequent comparison covers reset, all port values, idle retention,
   full successor publication and both outcome registers. Combined with legal
   initialization and closure, this supports induction over any finite number
   of correctly timed steps, with reset excluded after initialization.
7. **Post-synthesis proof:** each complete composed machine, including the
   registers, passes RTL-versus-ABC-mapped equivalence. Yosys `equiv_simple`
   alone initially left 70 register-related cells unproved; that failed attempt
   is retained as `development-simple-equivalence-unproven.log/.ys`. Adding
   `equiv_induct -seq 2` discharges all of them; all 132 equivalence cells are
   proven in each final profile. This is a repair of the proof procedure, with
   no change to the circuit or semantics, and does not prove physical timing.
8. **Checker sensitivity:** the same input-mapping proof detects five circuit
   mutants: worker becomes manager, old lane becomes current lane, wrong lane's
   payload, collision submits, and always idle. Tool failure is not sufficient:
   the checker requires the proof-failure signature. Separate runs of those
   failed proofs retain concrete satisfying counterexample assignments in the
   `counterexample-*.log` files. Always-idle detection and successful histories
   guard against a vacuous reduction.

Yosys 0.9, ABC 1.01 and Icarus 11.0 were available from the original local lab
tool extraction; no processor/runtime is synthesized. The composed machines
contain 919/1,090/1,055 combinational basic cells, 24 flip-flops, no latches and
no memory blocks. Longest paths are 34/35/36 cell levels. Synthesis took
3.17/3.31/3.29 seconds and exhaustive simulation 28.43/21.36/6.48 seconds.
Boundary proofs took at most 5.12 seconds. Maximum child-lifetime RSS was
164,196 KiB, including inherited launcher memory under the same Linux `wait4`
measurement convention as the baseline. These figures demonstrate bounded
tractability; they are not silicon area, timing closure, FPGA utilization,
minimum gate count or a safe clock period. Logic optimization varies with the
composed design, so the cell delta is a measured build result, not the isolated
area of the ingress circuit.

## Mechanism and assumption delta

| Item | Delta / classification | Residual requirement |
| --- | --- | --- |
| Kernel state, `G/E/I`, bounds, profiles and proposal semantics | Unchanged semantic target | Same provisional semantics and oracle correctness. |
| External actor field and authenticity verdict | Removed from caller-facing inputs; fixed combinational binding is a realization choice | Lane number and payload are faithfully connected by the checked circuit. |
| Unspecified dynamic trusted ingress classifier | Replaced for this interface by permanent lane wiring and exact-one-valid selection | Trusted port access/isolation remains part of the real assurance boundary. Drawing the ports outside the machine would not remove it. |
| Bootstrap manager origin | Unchanged trusted initial authority premise | Only the intended management source can drive lane 4; reset/configuration remain protected. |
| Old/current non-confusability | Existing semantic requirement realized by distinct fixed lanes plus unchanged issued/rights state | Old sources retain only old access unless explicitly given new authority. Finite context exhaustion still denies; lanes are not silently relabeled or reused. |
| Request interface | 60 input bits instead of 16 (excluding clock/reset); five fixed data lanes | More wiring and less general transport flexibility. Static separation is a trade, not evidence of lower total physical cost. |
| Extra sequencing, buffers, arbitration state, runtime programs | None introduced | Collisions can starve indefinitely; no request has been submitted in those cycles. |
| Authoritative retention | Still 22 state bits; two completion bits; no new registers | Holder survives executor loss; trusted initialization, power and register integrity unchanged. |
| Synchronous timing | Unchanged realization assumption | Whole settled sampling, coherent edge order and correctly timed observation. No asynchronous-output atomicity claim. |
| Python oracle/codecs, testbenches, SAT, synthesis, manifests and logs | Assurance scaffolding only | Their correctness is trusted for the experimental evidence; they are absent from the running circuit. |

## Reproduction and stopping decision

From this checkout, the two reproducible commands with tools on PATH are:

```sh
python3 docs/research/kernel-0/direct-rtl/verify.py --build /tmp/kernel0-ingress-baseline-build --evidence docs/research/kernel-0/ingress-reduction/evidence/baseline-rerun
python3 docs/research/kernel-0/ingress-reduction/verify.py --build /tmp/kernel0-ingress-build
```

Both accept `--iverilog`, `--ivl-base`, `--vvp`, `--yosys`, and `--abc` for the
relocated original tools. Concrete executable paths used here are retained in
the result command records. Run without Python optimization. Baseline output
must be directed to the separate evidence path above to preserve its frozen
evidence. The cheap discriminator can be run independently as
`python3 docs/research/kernel-0/ingress-reduction/preflight.py`.

The chosen single reduction has reached its stopping condition. The external
verdict/label dependency has been replaced by a tested fixed mechanism; the
minimum remaining source-separation premise has a concrete counterexample if
removed. It would be false to report complete elimination of trusted ingress.
No timing-reduction implementation, wider architecture, unbounded population,
general programmable control, new Kernel primitive, or physical deployment is
undertaken. All findings remain research evidence rather than project direction.

**WHY:** a fixed circuit derives the bounded evidence label from a protected
lane; every permitted bounded transition still matches the frozen oracle and
all publication passes through its unchanged register machine. Removing lane
separation collapses attempts requiring different outcomes. **WHAT:** the
frozen-artifact manifest and complete baseline rerun, 2,472,636 new oracle/RTL
comparisons, 30,720 raw attack cases, 618 clocked cycles, all-input mapping proof,
three boundary proofs, three complete-machine synthesis equivalence proofs,
five detected mutants and preflight counterexamples. **HOW CERTAIN:**
evidence-based bounded structural reduction, with exhaustive digital comparisons
and conditional formal proofs; not a universally minimal or trust-free ingress.
**WHAT-NOT-TESTED:** independent review, actual physical lane ownership/isolation,
board/FPGA execution, analog timing, metastability, skew or faults, hostile reset,
holder power loss/restart, arbitrary content, unbounded or dynamically rebound
contexts, asynchronous ingress, simultaneous-source service, fairness,
exactly-once delivery and protected external effects.
