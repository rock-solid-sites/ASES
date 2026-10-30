# ARIA Scaling Trust — Evidence-Based 12-Month Program and Costing Options
**Drafted 2026-10-30. Status: proposed scope; not an approved project plan or funding request.**
**Applicant:** independent individual principal investigator. Research project identity not yet selected. No affiliation with the applicant's unrelated business. Temporary AI models/subagents are development tools, **not team members**.

## Why the earlier quarterly schedule is superseded
The initial Track 2.2 draft reserved months 1–3 mostly for formal preparation, months 4–6 for a first functioning Work Unit, and months 10–12 for independent review. That sequence was not estimated from the actual program. It was a generic staffing template and should not be submitted without recalibration.

**Evidence of progress:** Kernel-0 finite semantics/recovery and realized bounded direct RTL developed substantially in late September/early October; the Oct 1 direct-RTL record passed 4,945,272 finite-profile oracle comparisons, digital SAT and synthesis correspondence subject to fixed ingress and clock assumptions. On Oct 30 the F1 branch added targeted finite witnesses; F2 added 46 abstract replays/16 useful mutants; F3 demonstrated explicit mediated revocation, then an H=M post-SIGKILL denial with 392,488 counted CPU iterations and an intentionally violated stale-mediator control. See \`EVIDENCE-LEDGER.md\` and \`F3-AUTHORITY-LOSS-ADDENDUM.md\`.

**Interpretation:** Agent-assisted incremental implementation and bounded tests often complete within hours of live work, but commit elapsed time is not total research effort. Existing specifications, orchestration, human direction, and prior tests are substantial reused inputs. General confinement, physical currentness/recovery, porting to independent environments and independent third-party assurance are still real barriers. Funding must not be used to pad first-prototype tasks across an arbitrary quarter.

## Target outcome and work funded
Deliver a permissively licensed **authority-to-effect enforcement and conformance component** usable by at least two independent agent-system integrations, with explicit supported threat profiles, failure/recovery semantics, reproducible adversarial checks, human-assessed trust assumptions, performance evidence, and publicly falsifiable limitations. Fund both useful tooling (Track 2.2) and the hardest research questions necessary to make that tooling reliable; do not promise general-purpose OS or universal agent safety.

## Milestone schedule: evidence gates rather than padded quarters
| Planned timing | Expected verifiable output | Distinguishing risk and fallback |
| --- | --- | --- |
| **Before award / ongoing (not charged as grant deliverable)** | Finish current bounded F3 lifecycle experiment as feasible; improve F1/F2 adapter; build project identity and applicant-ready case. No new resource claim until shown. | Record any failed boundary assumption rather than hiding it. |
| **Award weeks 1–4** | Reproduce existing evidence from pinned revisions; close the first selected end-to-end Work Unit profile or identify and publish precise obstruction; determine minimum stable external effect/decision interface; begin paid specialist assessment. | If host confinement/current storage blocks live recovery, define and test a narrower supported profile without changing guarantees. |
| **Months 2–3** | Open-source first third-party reproducible reference prototype and negative-control suite; independent verifier can run it on a clean isolated host; document TCB, supported effect and measurement denominator; minimum one other agent harness integration. | Basic nonvacuous task utility and adversarial failure cases must both run; a purely abstract runner is not enough. |
| **Months 4–6** | Two real integration environments, at least two deliberately chosen effect families *if viable*, a cross-platform mechanism comparison, test-execution and integration-cost benchmarks, currentness/recovery fault cuts, whole-history check for the supported cases; human security review checkpoint. | Effects and platforms are chosen by exclusion-first test and can narrow if one violates invariants; no guarantee of an extra host architecture until selected. |
| **Months 7–9** | Investigate and test one or two stronger research profiles: e.g., more complete source binding, controlled multiple-holder/fencing, external sink outcomes, or physically stronger rollback/currentness. Publish falsifiable positive results or counterexamples and cost/risk trade-offs. | Do not imply arbitrary power-loss, exactly-once sink effects, D3 bounded quiescence, or general multi-host semantics without separate proof and test scope. |
| **Months 10–12** | External clean-room human assessment and remediation of already-reviewable releases; independent reproducibility and maintainer documentation; UK research participation/workshops, integration trial feedback, published next-stage research opportunities and open code. Reviews occur **throughout**, not only here. | Do not describe conditional internal model review as independent assurance. External adoption is a target, not an existing partnership. |

### Measurement and adaptation
Observe in each month: (i) actually supported route/test denominator and untested routes; (ii) correct authorization plus successful useful tasks; (iii) demonstrated post-revocation failure avoidance with deliberate unsafe mutations; (iv) bounded formal coverage; (v) reproducibility in fresh hosts; (vi) cost/latency/memory overhead versus appropriate unprotected or standard sandbox alternatives; (vii) independently confirmed review issues and fixes. Maintain per-milestone source SHAs, commands, results and trust assumptions.

Scope schedule as a research hypothesis: revise after **two or three further integrated host verification cycles**, reporting actual human attention, compute, model expenditure and completion/counterexample outcomes. Do not extrapolate a two-hour commit burst to universal proof completion.

## Budgeting logic — three **illustrative**, unapproved scopes
No cost is automatically eligible. ARIA will fund actual supportable eligible grant costs, not an arbitrary staffing projection or profit margin. PI remuneration for an unhosted individual and any subcontractor treatment must be checked in official guidance/portal; no invented full-time salaries, contractor engagements, or overhead from a separate business. The official cost spreadsheet is required.

| Expense (GBP) | Lean £225k | Reference £300k | Expanded £420k |
| --- | ---: | ---: | ---: |
| Individual PI research compensation / direction | 70,000 | 72,000 | 78,000 |
| Targeted human formal-methods and systems integration expertise | 40,000 | 77,000 | 115,000 |
| Independent security review, adversarial test and professional assurance | 40,000 | 50,000 | 90,000 |
| AI inference and development tooling (multiple model families) | 35,000 | 48,000 | 55,000 |
| Isolated test environments, elastic compute and research equipment | 20,000 | 24,000 | 40,000 |
| UK research interaction, workshops and travel | 8,000 | 12,000 | 18,000 |
| Open documentation, accessibility, release maintenance and dissemination | 6,000 | 9,000 | 14,000 |
| Eligible accounting, individual-grant administration, licensing and advice | 6,000 | 8,000 | 10,000 |
| **Total** | **225,000** | **300,000** | **420,000** |

These are **scoping envelopes**, not invoices or assumed unit prices. Validate actual model/provider pricing and rate-card data; proportion of UK costs and engagement details require a credible plan. No undifferentiated contingency line. If cost evidence supports lower totals, submit the lower justified figure. The expanded scope is only plausible if additional UK-based technical collaboration and independent assurance resources are actually available.

### Why the £300k scenario is a more defensible working center
- Existing workflows use one human PI and temporary AI agents, not a permanent agent team. Full-time second/third engineers need proof they improve throughput or verification sufficiently.
- Prior outages and rate limits show real need for reliable **multi-provider** inference capacity, but £48k is a scenario ceiling requiring actual forecast and cost controls (e.g., £4k/month); cost per completed proof/test, not tokens purchased, should be evaluated.
- Human formal/security expertise should be paid for explicit gap closure: trusted-currentness, process/FD mediation audit, formal coverage, independent adversarial review, and external reproducibility.
- A selected small host can be tested cheaply; cloud/hardware spending grows only for necessary isolated environments and comparison experiments, not infrastructure duplication.
- UK benefit is a material evaluation requirement. Seek UK-based expert collaborations or funded contract research on a credible basis, not invented partners or a symbolic visit.
- Full-year spending supports **ambitious post-prototype work** even if the first viable narrow substrate exists before the award.

## Decisions awaiting applicant approval
1. Whether the PI would commit full-time or a defined part-time proportion and what **actual eligible compensation** basis applies.
2. Choose Track 2.2 as primary submission and revise with the latest F3 claim (narrow host witness, not closure).
3. Select a lean/reference/expanded scope only after quotes, actual costs and ARIA's individual-applicant budget treatment.
4. Settle project name/domain/accounts and UK benefit commitments without asserting partners not yet confirmed.
5. Fill official ARIA portal and budget/commercial uploads; current batch closes **31 October 2026, 14:00 GMT**. The call is rolling; late applications go to a later batch.
Sources: https://aria.org.uk/opportunity-spaces/trust-everything-everywhere/scaling-trust/funding ; https://aria.org.uk/funding-opportunities/faqs .
