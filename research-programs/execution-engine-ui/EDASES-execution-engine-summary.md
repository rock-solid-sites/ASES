# Orchestrator Prompt: Execution-Engine UI Research Programme

Paste this to the primary orchestrator agent in the EDASES repo. It assumes
you have already read `AGENTS.md`, `ARCHITECTURE.md`, and `ORIENTATION.md` —
this task inherits their rules rather than restating them, with one exception
called out below.

---

## Framing

This is EDASES-layer work: research, not implementation. The question under
investigation is whether an execution-engine frontend can be assembled
primarily from existing open-source components while preserving EDASES
methodology — not whether to build the frontend. Do not let any subagent
drift into implementation decisions, architecture proposals, or
recommendations. Per `AGENTS.md`, evidence should not be presented as
methodology, and methodology should not be presented as implementation. Every
report in this programme stops at evidence.

## Objective

Determine whether existing open-source components can be composed into a
visual execution environment that represents engineering artefacts, state,
reasoning, and version history with acceptable performance and usability,
without requiring a bespoke graph engine.

## Scope boundary

Explicitly out of scope for this research pass — do not commission
investigation into any of these, even if a subagent surfaces them as
interesting:

multi-user support, permissions, distributed execution, AI orchestration,
plugin systems, scheduler implementation, custom graph rendering, CRDTs,
event sourcing, microservices.

If a subagent's findings touch on one of these, it should note it as an
unknown/deferred item in its report rather than investigate it.

---

## Tooling and model constraints

- Do not use GLM-5.x or Kimi K2.7 Code as the orchestrator model. They may be
  assigned to individual bounded subagent tasks where no other available
  agent can be expected to complete them (for instance, a task that needs a
  very large context window or a specific coding capability those models
  are known for) — but never for planning, delegation, synthesis oversight,
  or communication back to the human.
- Use free OpenCode Zen models for the research subagents, the synthesizer,
  and the reviewer. Token cost is not a constraint on this programme; do not
  economize on subagent calls, report length, or number of sources
  investigated for that reason.
- The binding constraint is wall-clock time, not tokens. Maximize
  parallelism in the research phase, but check host resource headroom
  before a full simultaneous fan-out. There is a documented precedent in
  this org's tooling (the Crosslink evidence-gates work) of concurrent
  subagent sessions correlating with a host crash under memory pressure —
  roughly 870MB per OpenCode session on an 8GB VPS, with a hard reset
  occurring when two heavyweight scoping agents ran concurrently. If you
  cannot confirm the current host has headroom for a full wave (e.g. all
  four RQ1 investigators at once), stagger the launches in small batches
  rather than firing all of them in one message. Keep synthesis and review
  strictly serial regardless — they depend on complete inputs.
- Use whatever mechanism this repo's existing OpenCode tooling provides for
  defining and invoking subagents, rather than inventing a new one. If no
  existing pattern fits (e.g., you need a report-writing subagent with
  write access scoped only to the new research folder, and no bash or edit
  access elsewhere), set one up following the conventions already present
  in this repo's OpenCode configuration, and note in your final report to
  the human that you did so.

---

## Folder structure

Create, under the repo root:

```text
research/
    execution-engine-ui/
        README.md
        hypotheses/
        reports/
        synthesis/
        review/
        prototype/
```

`README.md` in that folder should state the objective above and link to this
prompt (or a copy of it) as the record of how the programme was commissioned.
Leave `prototype/` empty — Phase 3 does not begin until Phase 2 synthesis
passes review.

---

## Report template (mandatory, identical for every subagent)

Every research subagent produces a report in `reports/` using exactly this
structure. No recommendations. No implementation proposals.

```text
Question
Scope
Evidence
Findings
Rejected options
Unknowns
Confidence
References
```

A report that recommends a technology, proposes an implementation, or omits
a section should be rejected by the orchestrator before it ever reaches the
synthesizer — don't rely on the reviewer to catch that late.

---

## Research questions and subagent assignment

Assign subagents by question, not by technology. Where a question has
multiple candidate technologies, run one investigator per technology in
parallel, all answering the same question, so the synthesizer is comparing
like-for-like evidence rather than reconciling differently-scoped reports.

**RQ1 — Can existing graph frameworks represent engineering artefacts and
their relationships without substantial customization?**
Investigators: React Flow, Cytoscape, AntV X6, JointJS. (ElkJS and Rete.js
can be folded into whichever investigator's technology depends on or
competes with them, noted as such in that report's Evidence section.)
Each investigator addresses: expandable node content, performance at 5k+
nodes, incremental rendering, hierarchical graphs, virtualization, and
maintenance activity — as evidence toward the question, not as a checklist
to score.

**RQ2 — Can hierarchical statechart frameworks model independent artefact
lifecycles?**
Investigators: XState/Stately, SCXML-based alternatives.
Addresses: independent lifecycle per artefact, runtime state inspection,
versionable definitions, visual tooling, persistence.

**RQ3 — Can existing workflow engines be used as execution infrastructure
without imposing workflow semantics that conflict with EDASES?**
Investigators: Temporal, LangGraph, Burr, Camunda/BPMN.
Addresses: whether each is an orchestration engine or an execution engine,
which of their assumptions conflict with EDASES, which parts (if any) are
reusable. This is a gap analysis, not a fit recommendation.

Note for both RQ2 and RQ3: the current working hypothesis (see the
Execution Engine Summary in this research folder's README, once linked) is
that the engine needs statecharts *and* workflow graphs together — the
former for artefact lifecycles, the latter for execution. Don't let either
investigator frame this as XState-vs-Temporal or otherwise treat the two
questions as competing for the same slot. Each report should note, as
evidence, whether the technology it examined composes cleanly with a
separate lifecycle/execution layer or assumes it owns both.

**RQ4 — Can a graph database naturally represent artefacts, versions,
evidence, provenance, and supersession without excessive schema complexity?**
Investigators: Neo4j, Memgraph, Kuzu, PostgreSQL+pgvector, SQLite+edge
tables.

**RQ5 — Can one frontend expose four distinct views over the same
underlying data (execution, state, evidence, version history) without the
views fighting each other architecturally?**
This one is downstream of RQ1 and RQ4 findings — commission it after those
land, using their evidence as input, rather than in the first parallel wave.

**RQ6 — Can an agent recover a task using only artefact history rather than
conversation history?**
Prioritize this one. It tests EDASES's H3 (explicit provenance improves
interruption recovery) directly, and unlike RQ1–RQ5 it may be answerable
partly through direct experiment rather than only literature/library
research — if so, note the experimental method used in Scope.

Also fold in, as a lighter-weight single-investigator question:

**RQ7 — What concepts from existing engineering methodologies and
tools (SEMAT Essence, OMG SPEM, ArchiMate, OpenProject, Jira Advanced
Roadmaps) already exist and should not be reinvented?**

Bound every subagent task explicitly: state the research question, the
success criteria, the expected deliverable (a report in the template above,
saved to `reports/`), and an instruction to stop once those are satisfied.
Do not send any subagent an open-ended prompt like "research graph
libraries."

---

## Synthesis phase

One subagent, run after all reports in a wave are complete. Its
responsibility is constrained by design:

- Read all accepted reports in `reports/`.
- Do not perform additional research.
- Identify: points of agreement, disagreements, unsupported claims, and
  remaining uncertainties.
- Produce a research synthesis in `synthesis/`, in which every conclusion
  cites at least one report by filename.
- Do not answer "which technology is best." Answer which assumptions
  (referencing the H1–H7 hypotheses in the wider research plan, where
  applicable) have evidence and which don't.

## Review phase

One subagent, run after synthesis. It judges fidelity, not correctness:

- Did the synthesizer accurately represent the reports?
- Did it invent anything not present in the underlying reports?
- Did it omit conflicting evidence that was present in the reports?
- Are unsupported conclusions clearly labelled as such?

Output is PASS or FAIL only, written to `review/`, with a one-paragraph
justification per criterion above. The reviewer does not evaluate whether
the synthesizer's conclusions are true — only whether they're an honest
representation of the inputs.

On FAIL: return the synthesis and review to the synthesizer for revision,
citing the specific criterion that failed. Do not send it back for new
research — a FAIL means a misrepresentation of existing evidence, not a
gap in evidence. If the same synthesis fails review twice, stop and escalate
to the human rather than iterating further.

---

## What comes back to me

Report back only the synthesis that passed review, plus:

- which reports it drew on
- elapsed wall-clock time for the full programme
- number of subagents run in parallel at peak
- number of synthesis revisions and review failures, if any
- any scope-boundary items subagents flagged as deferred (from the Scope
  boundary section above)

Don't send me intermediate reports, draft syntheses, or a narrated log of
what each subagent did — I want the passing synthesis and the metrics above,
nothing else, unless I ask.

## One more instruction, per AGENTS.md's Continuous Improvement section

Treat this orchestration run itself as an EDASES experiment. Record the
metrics above as evidence about the orchestration methodology, not just as
a status report on this particular research programme, since this may
become the standard pattern for future EDASES research commissions.