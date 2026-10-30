# Evidence ledger and claim boundaries — ARIA Scaling Trust application
**DRAFT, checked 2026-10-30.** Do not increase claim strength without pinned raw evidence and distinct external assurance.

| Application claim | Verified source or current reported observation | Evidence level | Must not say |
| --- | --- | --- | --- |
| ASES is exploring minimal state-dependent authority for autonomous computation | Kernel-0 abstract semantics, verification obligations and Work Unit A–L; Phase I closure | Provisional semantic candidate | universally proven execution substrate |
| Direct fixed RTL realization passed 4,945,272 finite comparisons | `docs/research/kernel-0/Kernel-0-Direct-RTL-Result.md` on A branch; 3 profiles, independent/coupled/exclusive; SAT and synthesized equivalence | Completed bounded experiment under declared ingress, reset, finite-state and synchronous assumptions | verified physical chip, general isolation, no OS/TCB |
| Protected-lane ingress reduction supported | `Kernel-0-Ingress-Reduction.md` and `ingress-reduction/` on A branch; earlier independent review record | Conditional bounded model/RTL experiment | physically unforgeable ingress proven |
| Timing experiment not complete | A @ `9d0ecf1edbb7eb00e8ace4b2a4cf3e8ae65973c2`, inherited-state checkpoint | 151-state local event/cut fixture; found stale-view mutant; torn request capture/publication unrepresented | weaker clock/timing proven |
| F1 Work Unit recovery and authority witnesses | B @ `d227a22b9bbc0732881bf58f6933ce46fddc08fa`, `Phase-I-F1-Targeted-Run.md` | Selected finite contexts; accepted x/y through two modeled losses; currentness trusted; complete C1–C13 still open | all F1 invariants proven or physically durable |
| F2 hostile histories | C @ `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`, `fixtures-f2/COVERAGE.md` | 46 *abstract-model* replays, 16 discriminating mutations; 2 prepared-only | 24 physical tests or full suite green |
| F3 mediator revocation | D @ `ad44b3ff93477cc694a5b0771c3b867afdfde620`, `exp3/RESULT.md` | One process-level disposable Landlock + mediator proof-of-mechanism; explicit revocation and read denial | complete Work Unit, fail-closed on authority holder death, physical route inventory |
| Retained FD bypass | D `exp1`/`exp3`; chmod/Landlock test variants | Bounded negative observation | revocation of already-open descriptors via mode bits or Landlock |
| Actual authority-holder death | F3 commit `04600b1b45e6510665bdc3108db9d51f6b2f8c56`, `authority-loss/REPORT.md` and pinned JSON | Selected profile: baseline read, H=M SIGKILL/reap, 392,488 counted CPU iterations, no post-loss protected read on retained socket; path/symlink/write-open denials; distinct surviving-stale-mediator control returned protected bytes as expected. Independent Luna rerun, not F5. | full lifecycle; arbitrary aliases/FD passing/descendants/sinks; source binding; cold recovery; general D2/F5 |
| F4 full-history failure injection | Phase I Verification Plan | Specified only, not completed | crash/refinement complete |
| F5 independent review | User-reported conditional review, older than latest B SHA; no clean-room final review at these heads | Preliminary conditional feedback | independently certified F1–F5 closure |

## Decision rule for new evidence
The verified selected-profile F3 authority-loss result is recorded above and separately in `F3-AUTHORITY-LOSS-ADDENDUM.md`. F2 T05 remains prepared-only pending an independent host adapter; its partial physical observations do not convert T01–T24 into a passing host suite. The next technical target is the bounded end-to-end lifecycle packet on `planning/ases-phase-i-work-unit-lifecycle-20261030`. Any additional test results must remain tied to exact source SHA, command, observation and exclusions.

## Evidence discipline
- Keep claims at the abstraction level tested.
- Separate proposed work, finite verification, observed host behavior, independent review, and future physical realization.
- Each figure needs a pinned artifact and denominator.
- The number of replays, mutants and comparisons are independent types of evidence; never sum them into a fake unified success metric.
- Explicitly disclose trusted OS/storage/currentness and physical isolation assumptions.
- “Processorless” describes the declared bounded fixed RTL authority mechanism, not the agent runtime, underlying hardware or the entire system.
