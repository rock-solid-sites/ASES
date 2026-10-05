---
title: Kernel-0 Direct RTL Independent Review
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
depends_on:
  - Kernel-0-Direct-RTL-Experiment.md
  - Kernel-0-Direct-RTL-Result.md
  - Kernel-0-Verification-Obligations.md
consumed_by:
  - Kernel-0 ingress-reduction review
last_updated: 2026-10-05
---

# Kernel-0 Direct RTL Independent Review

## Reviewed artifact

The frozen direct RTL artifact is commit
`c03bf1c470e54f51c299cb3347c547eeeae0e5ce`.

This record does not modify or supersede that artifact. It records independent
post-build review of two bounded claims, the one concrete assurance weakness found
during review, and the later hardening/reproduction evidence.

Raw review provenance and exact prompts are preserved under
[`reviews/direct-rtl/`](./reviews/direct-rtl/).

## Claim A — transition-law correspondence

> For every valid bounded state and compared proposal in each of the three finite
> profiles, the RTL authoritative transition and outcome match the finite Kernel-0
> reference transition under the stated realization assumptions.

**Final status: SUPPORTED.**

All five substantive outputs in the supplied Claim A aggregate returned
`supported`. The strongest reviews independently executed the frozen Verilog
against the frozen Python reference rather than relying on a pre-existing
correspondence driver.

The common exhaustive domain was:

| Profile | Valid states | Compared proposals/state | Comparisons | Mismatches |
| --- | ---: | ---: | ---: | ---: |
| independent | 8,449 | 296 | 2,500,904 | 0 |
| coupled | 6,337 | 296 | 1,875,752 | 0 |
| exclusive | 1,921 | 296 | 568,616 | 0 |
| **total** | **16,707** |  | **4,945,272** | **0** |

Additional independent checks included direct Icarus execution, full reachable
wrapper closure, sweeps outside the modeled proposal alphabet, random clocked
cycles, codec/domain checks, and mutation sensitivity. These checks were not all
required by Claim A, but they reduce the risk that the null mismatch result was a
shared source-level reading error.

Claim A is therefore a bounded transition-law result. It does **not** establish
physical ingress authenticity, arbitrary concurrency, external-effect semantics,
persistence or power-loss recovery, analog timing behavior, or a universal
minimality result.

## Claim B — sufficiency of the frozen verification apparatus

> Assuming the reference model and verification tools are correct, the frozen
> verification apparatus is sufficient to establish the claimed bounded RTL
> correspondence over its declared domain.

**Final status: SUPPORTED, with one non-defeating integrity weakness found and
subsequently hardened.**

The supplied Claim B aggregate was mixed. Three substantive outputs supported the
claim, one returned `not established`, and two returned `falsified`; a trailing
reviewer label had no attached verdict and is not counted.

The negative findings were evaluated individually:

1. One objection required verification of asynchronous transport, partial-word
   arrival, wire noise, and broader executor-loss machinery. Those behaviors are
   outside this experiment's declared synchronous proposal-capture boundary and
   therefore do not defeat Claim B.
2. One proposed a `DELEGATE value=0` counterexample while also quoting the RTL
   `wellformed` condition requiring `value != 0`. The alleged proposal cannot
   pass that gate, so the counterexample is internally inconsistent.
3. One treated `BASE=00086d1722a22b481daa834b1e2b0f1a2d3e2b9e` as if it were
   required to equal the later artifact commit. In the frozen apparatus, `BASE`
   pins the governing semantic inputs; the RTL artifact was produced later at
   `c03bf1c...`. The mismatch is therefore not evidence that a different RTL was
   verified.

The positive reviews independently reproduced the exhaustive vector generation,
checked that the invariant-state and proposal enumerations covered the declared
domain, exercised the real RTL/testbenches, and challenged the SAT/equivalence
checks for vacuity.

### Real weakness found

A supported review identified a genuine assurance gap: the frozen
`SOURCES` integrity check pinned the governing semantic inputs, while
`kernel0.v`, `verify.py`, `correspondence.py`, and the testbench/formal
sources were only hashed in generated evidence. The verifier did not itself
reject a locally modified RTL or verification source before running.

This did not falsify the result at the frozen Git commit, but it weakened
self-contained reproducibility and made working-tree integrity depend on the
external commit pin.

## Hardening and reproduction

The integrity weakness was fixed in follow-up commit
`8f48b6cae4846a300c1ec9ae2c189d5d2ef4d7d1` without changing Kernel semantics
or RTL behavior.

The hardened verifier:

- protects the six semantic inputs plus the RTL, correspondence code, verifier,
  formal boundary source and testbenches;
- compares every protected working file byte-for-byte with its checked-out
  `HEAD` version before verification;
- records the exact artifact commit and protected artifact hashes in the evidence;
- snapshots protected inputs before the run and refuses to declare `PASS` if
  they change during verification.

The hardened verifier was then rerun unchanged from a clean worktree. Commit
`1756d1ba24ae4373d59a363560895e2d39c017f4` records the regenerated evidence.

The reproduction again ended with:

`PASS total_vectors=4945272`

All three profiles retained the same state/vector counts and passed exhaustive
correspondence, sequential traces, ABC-mapped synthesis equivalence,
register-boundary SAT, latch/memory-free netlist checks, and deliberate-fault
mutation probes. The reproduction changed generated `evidence/` files only; no
RTL, verifier or testbench source was changed.

The generated Yosys scripts contain absolute build paths, so rerunning from a
different worktree causes non-semantic evidence churn. This is a reproducibility
hygiene issue, not a correspondence or verifier-sufficiency defect.

## Result boundary

The independently supported result is narrow:

1. the bounded direct RTL transition law matches the finite reference over the
   declared three-profile domain; and
2. the verification apparatus is sufficient for that bounded correspondence under
   its stated reference-model and tool assumptions, with its source-integrity gap
   now hardened and successfully reproduced.

Trusted ingress/source separation and synchronous whole-proposal capture,
coherent current-state observation, and whole-state publication remain realization
assumptions. No claim is made here about physical hardware, power-loss persistence,
general concurrency, exactly-once external effects, or unbounded Kernel behavior.

## Next gate

The next independent review target is the ingress-reduction artifact at commit
`ac9d128e984dddecbbf08c810a9cfc53e9754ac9` on
`codex/kernel-0-ingress-reduction-c03bf1c`.

That review should remain separate from this baseline. Its question is whether the
dynamic caller-carried actor/authenticity premise can be replaced by fixed
protected source lanes while preserving the bounded Kernel-0 transition relation
under an explicit residual non-confusability assumption.
