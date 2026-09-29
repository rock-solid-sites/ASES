---
title: Efficiency Architecture Evidence Ledger
program: EDASES
layer: Architecture
document_type: Research Evidence Record
status: Experimental
authority: Derived
canonical_repository: edases
crosslink_issue: 572
depends_on:
  - EDASES Work Unit Component Design
  - Phase I Processorless Core Falsification
consumed_by:
  - Efficiency Architecture Investigation Record
  - EDASES Efficiency Architecture
related_documents:
  - Efficiency Architecture Discriminating Experiments
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Evidence ledger

## Method and limits

Repository evidence is fixed by the blob manifest in [the investigation](Efficiency-Investigation.md#basis-and-independence). External evidence below was deliberately introduced on 2026-09-29. Original papers, author-hosted material and official documentation support correspondences; none measures EDASES. Published speedups, API prices and model rankings are not transferred into this architecture.

Exa discovery comprised 21 queries with 99 requested result slots, including duplicates and irrelevant results. That is a search-effort count, **not** 99 independently reviewed sources. Search angles covered incremental/materialized computation; applicability, negative knowledge and coordination; event observation and recovery; specialization and context; bounded judgment and metareasoning; and scheduling/locality/online adaptation. Queries were followed by selective full-text extraction and targeted reading. This is a purposive architectural survey, not an exhaustive systematic literature review.

The 21 entries below are the selected primary sources. Papers were read for the identified mechanisms and limits, not independently re-proved; extracts may omit other sections. Where only an abstract or author overview was checked, the entry says so. Two guessed Adapton PDF locations did not return usable content; discovery located the author-hosted paper. One OpenReview discovery result returned a browser challenge; the author's FrugalGPT PDF supplied the evidence. These access failures do not count as corroboration.

Each entry records **WHAT** was inspected and **WHY** it matters. Its certainty is **evidence-based** source interpretation unless otherwise stated. For every entry, **WHAT-NOT-TESTED** includes reproduction of the paper's experiments, formal verification of its proofs, and transfer to EDASES. Additional limits appear in the final column. Source propositions and EDASES deductions remain separate in the investigation.

## Primary evidence

| ID | Source and inspected locus | Supported correspondence; transfer limit |
| --- | --- | --- |
| E01 | Mokhov, Mitchell & Peyton Jones (2018), [Build Systems à la Carte](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/03/build-systems-a-la-carte.pdf), §§2–5, especially dynamic dependencies, early cutoff and scheduler/rebuilder separation. | Whether work must be redone is separable from execution order. Input and task identity matter. Build-task models do not establish correct authority admission or arbitrary semantic-task equivalence. |
| E02 | Hammer et al. (2014), [Adapton](http://matthewhammer.org/adapton/adapton-pldi2014.pdf), §§2–4 and demanded computation graph discussion. | Dirtying can be separated from demand-triggered repair. Tracked computation can agree with ordinary evaluation under its calculus. Arbitrary tools, unrecorded reads and probabilistic reasoning do not inherit that assurance. |
| E03 | McSherry et al. (2013), [Differential Dataflow](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf), §§3–4; difference traces, joins, aggregations and iteration. | Indexed differences over partially ordered versions support changing iterative computations. Retractions, history indexes and progress are real state. A small input delta need not have a small output impact. This is not a generic execution model for Work Units. |
| E04 | Idreos et al. (2011), [Merging What's Cracked, Cracking What's Merged](https://www.vldb.org/pvldb/vol4/p586-idreos.pdf), introduction and adaptive-indexing comparison. | Query-driven physical adaptation trades first-use overhead against convergence. It motivates incremental investment rather than a complete index built prospectively. Its relational layout and workload assumptions do not transfer to context or dependency graphs automatically. |
| E05 | Halim et al. (2012), [Stochastic Database Cracking](https://www.vldb.org/pvldb/vol5/p502_felixhalim_vldb2012.pdf), sequential-workload counterexample and robustness discussion. | Blindly adapting to each query can repeatedly reorganize large regions for little gain. “Adaptive” is not a guarantee of favorable amortized cost. No EDASES workload resembles these benchmarks by assumption. |
| E06 | Bazel, [Hermeticity](https://bazel.build/basics/hermeticity), source identity, tool isolation and non-hermetic causes. Official page retrieved 2026-09-29. | Stable source names alone do not identify a computation; tools and environment matter. Hermetic build practice is an example, not a requirement to containerize every Work Unit or retain every environment forever. |
| E07 | Bazel, [Remote Caching](https://bazel.build/remote/caching), action inputs and known issues including concurrent input modification and outside-workspace tools. Official page retrieved 2026-09-29. | Reuse requires a sound action identity and production boundary. Hashing inputs does not by itself certify an output or eliminate races. No particular command-line flag is recommended here. |
| E08 | Jones, Gomard & Sestoft (1993), [Partial Evaluation and Automatic Program Generation](https://www.itu.dk/~sestoft/pebook/jonesgomardsestoft-a4.pdf), ch.1 and specialization/binding-time definitions. | Specialization fixes known inputs of a specified program while preserving its relevant semantics. Learned habits or LLM-generated rules lack this premise. General automated verification of such rules was not studied here. |
| E09 | Andrews (1998), [RFC 2308](https://www.rfc-editor.org/rfc/rfc2308.html), §§2–5 and §7. Historical protocol example, not current DNS deployment guidance. | Name absence, type-specific absence and server failures are distinct negative answers with scoped caching behavior. A DNS lifetime rule is not proof that an EDASES negative claim remains current. Later DNS standards are outside this comparison. |
| E10 | Hellerstein & Alvaro (2020), [Keeping CALM](https://cacm.acm.org/research/keeping-calm/), monotonicity and graph examples. | Under the stated distributed-computation model, monotonicity explains when consistent outcomes can avoid coordination. Ordering, revocation, completeness and authoritative commitment are different obligations. This paper is not evidence that EDASES can decentralize its Kernel. |
| E11 | Zaharia et al. (2012), [Resilient Distributed Datasets](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf), §§2.1–2.4, lineage examples and §5.4 discussion. | Retained deterministic lineage can replace some replication; long recovery paths motivate checkpoints. Restricted transformations over available base data are essential. Unobserved external outcomes and accepted human choices cannot be replayed this way. |
| E12 | Kubernetes, [API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/), efficient change detection, resource versions, bookmarks and unavailable-history recovery. Official page retrieved 2026-09-29. | Snapshot plus resumable watch is a concrete event/reconciliation combination. Watch history can expire and require relisting. This does not establish trustworthy EDASES observations or make a bookmark an authority credential. |
| E13 | Dean & Barroso (2013), [The Tail at Scale](https://cacm.acm.org/research/the-tail-at-scale/), queueing, background work, hedged requests and cancellation. | Low mean service time is insufficient for fan-out latency; duplication can trade resource use for tail improvement. External side effects and correlated model failure make blind hedging inappropriate. No benchmark multiplier is imported. |
| E14 | Geifman & El-Yaniv (2019), [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a/geifman19a.pdf), §2 risk/coverage definitions and selective objectives. | Evaluate error among accepted answers jointly with the fraction answered. Its supervised-data assumptions do not make an LLM's self-reported confidence calibrated or provide a distribution-free correctness guarantee. |
| E15 | Chen, Zaharia & Zou (2024), [FrugalGPT](https://lingjiaochen.com/papers/2024_FrugalGPT_TMLR.pdf), router, scorer, stopping thresholds, evaluation setup and distribution-shift discussion. | A learned cascade can trade cost against quality on measured tasks. Scorer training, calibration, sequential calls and distribution shift belong in the bill. Historical API prices and paper models are not recommendations for EDASES. |
| E16 | Liu et al. (2024), [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/), published abstract and task description. | Relevant-information position affected the tested QA/retrieval models. This motivates placement and omission controls in a context experiment, not the claim that shorter context always wins or that current models share identical behavior. Full experimental tables were not audited. |
| E17 | Cousot & Cousot (1977), [Abstract Interpretation](https://www.di.ens.fr/~cousot/COUSOTpapers/POPL77.shtml), author summary and original-paper abstract. | A formal abstraction can preserve a selected property while losing other detail. This correspondence motivates distinguishing sound conservative analysis from statistical prediction. No abstract domain or sound analyzer for EDASES is supplied. |
| E18 | Necula, [Proof-Carrying Code](https://people.eecs.berkeley.edu/~necula/pcc.html), author overview, advantages and technical difficulties; [1997 original-paper record](https://dl.acm.org/doi/10.1145/263699.263712). | Separate expensive production from a scoped trusted verifier. Authentication of origin and proof of a property are different. The author overview is explicitly historical; it does not establish a cheap certificate for arbitrary semantic work. |
| E19 | Karlin et al., [Competitive Randomized Algorithms for Non-Uniform Problems](https://courses.csail.mit.edu/6.895/fall03/handouts/papers/karlin.pdf), primary conference-paper scan, abstract and online/adversary definitions. | Online rent/buy and competitive analysis illuminate uncertain future reuse. The paper's competitive ratios are **not** claimed for caches with churn, eviction, variable costs or multi-object budgets. The threshold example in this investigation is derived directly. |
| E20 | Russell & Wefald, [Principles of Metareasoning](http://iiif.library.cmu.edu/file/Newell_box00014_fld01011_doc0001/Newell_box00014_fld01011_doc0001.pdf), primary conference-version scan, introduction and utility-of-computation framing. | Deliberation is an action whose expected decision benefit must justify its cost. Unknown outcome distributions and the cost of estimating them limit application. No optimal EDASES metacontroller follows from this correspondence. |
| E21 | Eén & Sörensson, [An Extensible SAT-solver, extended version 1.2](http://www.ccs.neu.edu/%7Epete/courses/Decision-Procedures/2007-Fall/readings/Een_Sorensson_Extensible_SAT_Solver.pdf), incremental solving interface and constraint discussion. | Formal search can reuse learned information across related constrained instances. Applicability depends on the formula and assumptions. The scan's OCR is poor; no detailed solver implementation claim rests on it. The investigation's UNSAT example is independently enumerable. |

## Exclusions and counterweight

Searches also returned newer broad CALM generalizations, a recent materialized-view benchmark, product marketing, secondary summaries and duplicate mirrors. They were not used to settle EDASES claims. Known older work was preferred where the exact mechanism was already sufficient. This avoids an unsupported novelty claim; it also means the survey does not establish the latest best implementation.

Important disagreement is preserved rather than counted as consensus: E02 limits eager incremental repair through demand; E03 demonstrates a valuable stateful incremental technique under a different workload; E04 motivates adaptive investment while E05 shows its workload sensitivity. E11 supports reconstructible intermediates while also motivating checkpoints. E13 supports selective speculative duplication, which explicitly qualifies a literal “compute only demanded work” rule. E14/E15 support measured routing but not blanket cheap-first policy.

## Evidence needed beyond this pass

The [experiment protocol](Efficiency-Experiments.md) distinguishes executed finite countermodels from proposed empirical work. No EDASES cache, scheduler, Processor, model router, compression pipeline or event Observer was benchmarked. A field's formal result is evidence for a **conditional mechanism**, not validation of an EDASES realization.
