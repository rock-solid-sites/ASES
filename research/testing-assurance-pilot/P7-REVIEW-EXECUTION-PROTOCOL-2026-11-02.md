---
title: P7 — Separate Reviewer Execution Protocol
status: Dispatch-ready; no model reviewers invoked
date: 2026-11-02
authority: Experimental
---
# P7 independent reviewer execution protocol

**Important: packets and scoring code are ready; no human or independent model has yet performed these reviews.** The syntax heuristic in P7 is only a cheap deterministic control, *not* an ordinary agent reviewer. Authorial reconstruction of P5 through Python code is not model-family independence.

## Three actual model-review routes to compare, without mixing context

**A. Ordinary review comparator.** Route the same case packet(s) to a fresh model with a generic bounded instruction such as: “Read the supplied requirements and artifact. Identify materially incorrect claims or mappings, supported by excerpts; otherwise report no material issue within the supplied scope.” Give it exactly the same canonical requirements and artifacts as the corresponding specialized route, but no Ontology Design or Conformance role contract. For design cases it may see the bounded design rationale; for conformance cases it must not see builder process history. Record route/provenance and score only after output is frozen.

**B. Ontology Design Reviewer.** Supply only [three Design cases](../ontology-benchmark-p7/design-review-packet.json) and the [proposed Design role contract](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/ontology-design-reviewer.md). Allow requirements and bounded design rationale. Challenge identity, relationships, lifecycles, necessity and ownership. Do not produce new canonical policy or execute implementation changes.

**C. Ontology Conformance Reviewer.** Supply only [three corrected Conformance cases](../ontology-benchmark-p7/conformance-review-packet-v2.json) and the [proposed Conformance role contract](https://github.com/rock-solid-sites/ASES/blob/proposal/testing-and-assurance-method-2026-11-01/docs/proposals/2026-11-02-testing-debugging-ontology/ontology-conformance-reviewer.md). The packet includes fixed claims and completed excerpts, but excludes observations that reveal the planted result. Do not provide the earlier [v1 packet](../ontology-benchmark-p7/conformance-review-packet.json), its original case source, P7/P5 analysis, prior reviewer outputs or the sealed key. An independent model must not be allowed to search those adjacent materials before its first verdict.

## Dispatch / isolation record required

For **each** actual reviewer session, record: role/baseline, routed model and family **from the caller/connector, not model self-report**, who authored the artifact, prompt and packet SHA-256, input file hashes/paths, whether context was fresh, exact accessible repositories/documents, time/cost/token observations or `NOT_OBSERVED`, output and individual case verdicts, and any contamination or rerun. Different-family status is `UNVERIFIED` until actual routing metadata establishes it. The Design and Conformance reviewers must not see each other's findings before their own frozen outputs.

For P5 independent **evidence reconstruction**, use [source-first P5 reviewer packet](../testing-assurance-pilot/P5-REVIEWER-PACKET-2026-11-02.md). This is a separate exercise from detecting concealed conceptual faults; the preregistered P5 plan names its planted mutants and therefore does not constitute blinded defect discovery.

## Sealed scoring and thresholds

The **private sealed answer key** was committed before P7 execution in the private GitLab project under `evidence/p7-ontology-2026-11-02/private-sealed-key.json`; public case packets contain no scoring labels. The complete original P7 CI ZIP, including private scoring, is independently preserved in the **private** `rock-solid-sites/foundation-ASES` research branch. Do not fetch those resources into the reviewer's prompt/context. Open them only after all comparisons have emitted sealed first-pass results.

Score true detections and false positives on two clean controls; separately grade direct grounding, unnecessary proposed new entities, scope overreach, missing counterexamples, unresolved canonical ambiguity, context contamination and cost. The deterministic syntax-control baseline found **two** of four planted defects with zero false positives, but it is neither an ordinary reviewer nor an upper bound.

All actual comparative review cells currently remain `NOT_RUN`. No ontology reviewer role should be promoted as an operational gate on the strength of packet qualification alone.

## Why the Conformance packet was revised

The original case corpus supplied illustrative `observed_trace` or `relevant_trace` fields next to the finished code; these can reveal the expected result. After the initial P7 measurement, those hint fields were stripped from a **new** v2 dispatch packet without changing the originally scored data. The post-hoc packet check accepted both valid isolated packets and rejected six controlled contamination/mutation cases; the correction is not backdated into the original preregistration.

**Research decision:** compare selected reviews only when real independent reviewer calls, model provenance, clean-room input constraints and observed outputs exist. Otherwise state `NOT_RUN`.
