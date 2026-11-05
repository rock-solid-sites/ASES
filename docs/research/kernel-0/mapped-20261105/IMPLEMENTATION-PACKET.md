# Mapped circuit versus RTL correspondence

Freeze from `d20a6e3f144443f49e958f5fce8d16909821a63d` before implementation/execution.
Earlier source codec/step proofs and basic-cell measurements did not verify the actual
post-ABC sequential netlists. Next question: does the identical selected mapping flow
preserve each original/compact machine's synchronous state and response behavior?
This is a different boundary from original RTL versus the semantic model, not a new
Kernel contract investigation or physical timing experiment.

Reuse unchanged RTL, independent profile only (COUPLED=EXCLUSIVE=0), Yosys0.23/ABC1.01
and exact same synth -noabc / abc -g simple flow. Retain newly generated mapped Verilog
and hashes rather than treating historical disposed netlist digests as checked circuits.
One circuit per encoding; no optimization loop, new profile or RTL repair without a
concrete mismatch. Native tools already present, no new provider/installation.

For each: (1) mapped/source sequential equivalence via equiv_make/equiv_simple and
equiv_induct at depth2, require every equiv cell proved; (2) independently assembled
top-output miter SAT for reset assertion at first abstract clock step and equality at
steps2..4, arbitrary valid/proposal/reset thereafter. Yosys induction is weak convergence
after equal observable histories; it is NOT an unconditional initialization proof.
The explicit reset base is required. If linkage of induction points/base cannot be
justified, report separate tool results rather than a universal sequential proof.

Negative sensitivity: post-mapping wrapper inverts committed while valid; both designs
compile, bounded miter must exhibit a semantic difference after reset and save concrete
SAT witness, not count syntax/tool failure as a mutation kill. Shared synthesis/formal
toolchain is a trust limitation; source semantics still rely on prior evidence. No
physical delay/area/frequency, arbitrary hardware corruption, resetless initialization,
minimality or broader profile/Kernel closure.

Each tool child <=45s wall/512MiB virtual address/40s CPU. Whole runner <=180s, sequential
jobs, raw stdout/stderr/scripts/argv/exits/wait4 wall/CPU/peakRSS, source/tool/executable
identities and source pin retained. Stop on compatibility failure rather than swap
route or blindly double bounds. Source and packet committed before behavioral proof.
Next cheapest discriminator depends on any mismatch/timeout; otherwise independent
netlist audit or another genuinely unfinished obligation, not more identical profiles.
