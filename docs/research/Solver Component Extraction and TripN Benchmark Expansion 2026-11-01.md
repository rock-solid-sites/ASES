# Solver component extraction and project-derived benchmark plan — 2026-11-01

Status: architecture investigation, not a demonstrated lightweight build. Supersedes any assumption that the full MiniZinc bundle must be installed on the VPS.

## Confirmed upstream architecture

- MiniZinc (`MiniZinc/libminizinc`) is a **modeling language and compiler**, compiling `.mzn` models to FlatZinc; it is not itself the Chuffed or Gecode search engine. Its README explicitly says the compiler repository does not include the IDE or solvers.
- Chuffed (`chuffed/chuffed`) has a standalone `fzn-chuffed` FlatZinc executable and a **direct C++ API/examples**. It can be invoked without the MiniZinc compiler if an already-generated FlatZinc model is supplied, or modeled directly in C++. It has assumption/nogood support relevant to diagnosing infeasibility. License: MIT.
- Gecode (`Gecode/gecode`) is a **modular C++ constraint programming toolkit** with a direct API, CMake packaging and MIT-style permissive license. Direct use does not require MiniZinc.
- MiniZinc compiler license: MPL-2.0 by default, subject to individual file headers. Separately distributing solver components requires preserving their applicable license notices.

Upstream source: https://github.com/MiniZinc/libminizinc ; https://github.com/chuffed/chuffed ; https://github.com/Gecode/gecode

## Deployment candidates to measure, not assume

1. **Reference**: invoke MiniZinc CLI with on-demand Chuffed/Gecode backend. No IDE, no resident daemon. Measure actual installed footprint, peak RSS, startup and end-to-end wall time.
2. **Precompiled FlatZinc + Chuffed**: generate `.fzn` from a **stable model** at build time, then invoke `fzn-chuffed` at runtime. Critical risk: resource graph and constraints are dynamic; FlatZinc is instance-specific, so precompilation cannot simply substitute arbitrary new JSON inputs. Measure regeneration frequency and whether a bounded/template model is feasible.
3. **Direct Gecode API**: translate ASES typed Work Unit/resource graph into native Gecode constraints. Removes MiniZinc parser/compiler, but introduces owned modeling code and maintenance. Test parity and unsupported constraints before selecting.
4. **Direct Chuffed C++ API**: plausible from upstream examples, but API stability, packaging and effort are unverified. Test only if (2) or (3) looks promising.
5. **MiniZinc compiler-only on demand**: compile to FlatZinc with a small, isolated compiler package and separate backend. Likely easier to maintain than direct solver APIs; measure binary/dependency footprint rather than assuming savings.
6. **Alternative direct CP-SAT**: retain as comparator because Python binding overhead is not representative of a native build; measure native vs Python separately if relevant.

## ASES architectural rule

Do **not** fork or copy an arbitrary subset of solver internals merely to reduce package size. First compare native upstream build options, on-demand invocation and component packaging. Prefer an adapter with a stable typed input/output contract. Fork only if measured improvement outweighs ownership and security-update burden.

Solver runs must have bounded time, memory, process lifetime and output. Keep execution out of the persistent Paseo coordination process; do not make solver-specific syntax part of the ASES Work Unit specification.

## Full TripN graph benchmark expansion

Use `docs/research/fixtures/tripn-beds24-document-derived-v0.json` (18 stages, document-derived) and `tripn-beds24-actions-observed-2026-10-26.json` (measured CI timestamps).

**Historical anchor:** GitHub Actions job 121411681468 in run 40273650126, successful on 2026-10-26. First/last log timestamps span about 79.5 seconds; combined build command about 46.5 seconds, deployment-to-success about 17.6 seconds. Five site-build invocations are sequential. These are elapsed timestamps, not isolated CPU/RAM or per-site execution times. Source: https://github.com/TripN-Chill-Zone/tripn-astro/actions/runs/40273650126

**Synthetic layer required before solver comparison**: provide distinct seeded estimates for each of the 18 stages, alternatives (VPS, Actions, Codespaces, Modal), per-environment memory/CPU, setup/cache/transfer, quota and reset, and a provenance/assumption ID for each invented value. Never silently backfill historical unknowns.

**Replanning case**: freeze completed site builds; run booking integration; discover early completion-heading defect; insert correction/review/deploy; preserve credit-card configuration verification; require post-deploy smoke test. Existing document-derived fixture is a planning DAG, not a claim about the actual historical order.

**Baseline comparisons**: (i) serial site-build chain matching observed CI order, (ii) legal parallel site builds on separate workers with transfer/setup cost, (iii) full dependency graph with one worker and with constrained parallel workers, (iv) quota reset, (v) environment outage, (vi) replan with frozen stages. The historical CI build step is a calibration anchor only for the matching build topology.

## Acceptance gates

- Same normalized work graph, domains, constraints, objective and time units across all solvers.
- Independent validator checks all precedence, memory, concurrency, budget, quota, security and frozen-stage conditions.
- Independent small-instance exact enumerator checks optimum; 18-stage case uses cross-solver agreement and certified bounds.
- Measure cold start, warm start, installed disk, total peak RSS (including subprocesses), model compilation time, solving time, wall time, objective quality and failure behavior.
- If direct API and MiniZinc disagree, reduce to a minimal counterexample and preserve it as a regression fixture.
- Do not equate smaller executable with smaller RSS or lower total engineering cost.

## Decision

**Recommendation for next implementation test:** keep MiniZinc + Chuffed as reference, compare a standalone Chuffed FlatZinc runner and direct Gecode adapter on the same TripN workload. Do not select a custom Chuffed integration before verifying its C++ API and dynamic-model ergonomics. No new comparative runtime measurement is claimed in this document.
