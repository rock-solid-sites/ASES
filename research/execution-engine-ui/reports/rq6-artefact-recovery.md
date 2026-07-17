# RQ6 — Can an agent recover a task using only artefact history rather than conversation history?

## Question

Restated precisely: Is it possible for an agent (AI or human) to resume an interrupted task using **only the structured history of engineering artefacts** — versions, provenance, supersession links, evidence, decisions — without access to the original **conversation history** (the turn-by-turn dialogue, message log, or transcript that produced the work)? This tests EDASES hypothesis H3: "Explicit provenance improves interruption recovery." The question is not whether recovery is *possible in principle*, but whether the evidence shows artefact history is a *sufficient and preferable* recovery substrate compared with conversation replay.

## Scope

**Investigated:**
- Workflow engines and scientific-workflow provenance systems that recover from structured state rather than replay.
- Human–computer interaction (HCI) research on task interruption and resumption, including the role of external cues.
- Current LLM-agent state-management practice (checkpointing, durable execution, context compaction) and its relationship to conversation history.
- The emerging "reasoning provenance" literature that distinguishes computational state from reasoning provenance.
- Provenance-comprehension and reuse studies.
- Failure modes of discarding conversation history, and candidate measures beyond tokens and completion rate.

**Excluded:**
- Live empirical experimentation (this is a literature- and design-based research answer; a concrete experiment is *described*, not *run*).
- Vendor/marketing claims treated as primary evidence (used only as illustrative context).
- Tool or framework recommendations (per research constraints; systems are cited as evidence, not endorsed).
- The separate question of whether an agent can recover from *no* history at all.

## Evidence

**E1 — Workflow systems recover from provenance + checkpoints, not replay.** Ananthanarayan et al. (SSDBM 2011, "Improving Workflow Fault Tolerance through Provenance-Based Recovery") present a framework for resuming workflow execution "using only such commonly recorded provenance data," with a checkpoint extension to standard provenance models that "significantly reduce[s] the computation needed to reset the workflow to a consistent state, thus resulting in much shorter re-execution times." Earlier work ("Checkpointing for workflow recovery," SIGMOD 2006) defines rollback as restoring a saved state (checkpoint) and resuming. *Observation:* structured state/provenance recovery is an established, faster alternative to full replay in workflow systems.

**E2 — Human software engineers resume via artefact context (Mylyn).** Kersten & Murphy ("Mylar: a degree-of-interest model for IDEs," AOSD 2005; "Using Task Context to Improve Programmer Productivity," FSE 2006) built Mylyn, which captures the *task context* — the set of code artefacts (files, types, methods, fields) and their degree-of-interest — and persists it so a developer can deactivate and later reactivate a task and resume exactly where they left off. A longitudinal field study with 99 practicing developers compared pre- and post-Mylyn work logs. *Observation:* persisting artefact-level context (not the developer's "conversation" with the code) demonstrably supports interrupted-task resumption for humans.

**E3 — External cues reduce resumption lag; internal memory of interrupted tasks is unreliable.** Altmann & Trafton ("Task Interruption: Resumption Lag and the Role of Cues," 2004) measured resumption lag (time to "collect one's thoughts" and restart) as roughly double the interval between uninterrupted actions, and found that *cues available immediately before the interruption* reduced this lag. Hodgetts & Jones (2006) similarly show contextual cues aid recovery. By contrast, Ghibellini & Meier (2025, meta-analysis) find the Zeigarnik "memory advantage of unfinished tasks" lacks universal validity, while the Ovsiankina "tendency to resume" is a general effect — i.e., the *drive* to resume is reliable but the *memory* of task state is not. Mark et al. (2005) found 22.7% of interrupted office tasks were not resumed the same day. *Observation:* structured external cues (artefact state) aid recovery, whereas reliance on internal/conversational memory of an interrupted task is fragile.

**E4 — Current LLM-agent recovery bundles conversation history into state.** Production agent frameworks recover via persisted *state* that typically includes the message history. LangGraph persists checkpoints of "serialized threads — effectively capturing each agent's conversation history and execution context" (Microsoft Agent Framework issue #2144). Durable-execution systems (Temporal, DBOS) "preserve conversation history and agent state through deterministic replay" (Towards AI, 2025). *Observation:* today's agent "state-based" recovery is not artefact-only; it carries the conversation log. This is a crucial boundary: the hypothesis contrasts artefact history with conversation history, but most deployed systems do neither exclusively.

**E5 — Conversation/state does not capture the "why"; reasoning provenance cannot be faithfully reconstructed from state.** Vispute & Kadam ("Reasoning Provenance for Autonomous AI Agents," arXiv 2603.21692, 2026) formalise the distinction: *Computational State* S_k = (M_k message history, C_k channel values, T_k tool calls) — what LangGraph checkpoints — versus *Reasoning Provenance* R_k = (I_k intent, O_k observation, N_k inference, P_k plan version). They argue reasoning provenance "cannot in general be faithfully reconstructed from computational state as a stable, queryable representation." *Observation:* even full conversation history is insufficient to recover *why* an agent acted; provenance (the epistemic relationships) is a distinct, non-reconstructable layer. This both supports H3 (provenance matters) and reframes it: the relevant recovery substrate is provenance, not conversation.

**E6 — Compressing conversation loses decisions; externalised decisions prevent repeated mistakes.** Practitioner reports (e.g., zenn.dev "Recovering Lost Context," 2026) describe the failure mode where context compaction drops the premise of a rejected decision, causing the agent to re-propose the same rejected option. Storing decisions/artefacts externally and retrieving them on resume prevents this. Context-engineering guidance (tianpan.co, 2026) advises: "Reserve compaction for scenarios where conversational reasoning must be preserved — not as the primary mechanism," and to keep any state that must survive context resets in external memory (e.g., a file). *Observation:* conversation history is lossy under the finite context window ("lost-in-the-middle," context-window cliff); externalised artefact/decision state is more durable.

**E7 — Provenance aids comprehension and reuse.** Boufford et al. ("Computational Experiment Comprehension using Provenance Summarization," ACM REP'24, 2024) ran a user study comparing provenance summaries to node-link diagrams; participants extracted useful information from both, and textual provenance summaries were "particularly beneficial for scientists with low computational expertise." Nguyen et al. ("Provenance, End-User Trust and Reuse: An Empirical Investigation," 2011) note the provenance community *assumes* provenance aids trust/reuse but that little empirical work had tested it. *Observation:* there is emerging empirical support that provenance representations improve human understanding of a process — a prerequisite for recovery — though the trust/reuse claim is still under-studied.

**E8 — Semantic persistence distinguishes "resumable state" from "knowledge that outlives the run."** "Workflow as Knowledge: Semantic Persistence for LLM-Mediated Workflows" (arXiv 2607.08740, 2026) argues for retaining typed objects and relations (inference, approval, panel records) beyond execution, not merely resumable execution state. AgentSec (MDPI Data, 2026) provides a structured, PROV-DM-compliant provenance dataset targeting scenarios including "decision rollback, tool failure recovery, memory inconsistency, or provenance divergence." *Observation:* the research frontier is moving toward provenance-as-knowledge, consistent with EDASES's "reasoning is the primary artefact" stance.

## Findings

**F1 — Artefact/state-based recovery is demonstrably possible and is the dominant paradigm wherever recovery has been engineered deliberately.** Workflow provenance recovery (E1) and Mylyn task context (E2) are both real, evaluated systems that resume work from structured artefact state without replaying a "conversation." The answer to RQ6 is therefore **yes in principle and in adjacent domains**: an agent can recover from artefact history.

**F2 — Artefact history is, where measured, more efficient than replay.** Provenance-based workflow recovery explicitly yields "much shorter re-execution times" than replay (E1). HCI evidence shows external cues cut resumption lag (E3). This aligns with H3's predicted efficiency gain (fewer tokens / faster resume) and with the context-engineering finding that externalised state beats an ever-growing conversation log (E6).

**F3 — "Artefact history" must include provenance, not just versions, or recovery is shallow.** The strongest counter-evidence to a naïve "versions + supersession links suffice" reading is E5: conversation/state does not capture intent, observation, inference, or plan rationale, and that layer is not faithfully reconstructable. The practitioner failure mode (E6) — re-proposing a rejected decision after compaction — is exactly what happens when the *why* (provenance) is absent. EDASES's own framing (reasoning as primary artefact; epistemic relationships first-class) is thus not merely stylistic: provenance is the load-bearing part of artefact history for recovery.

**F4 — Most deployed LLM-agent recovery is not a clean test of the hypothesis.** Current systems persist state that *includes* the conversation log (E4). So we have evidence that state-based recovery works, but not yet direct, large-scale evidence that *artefact-history-only* (conversation excluded) recovery matches or beats it for LLM agents. The hypothesis remains partially unvalidated at the specific LLM-agent level, even though it is well-supported by workflow and HCI analogues.

**F5 — Discarding conversation history loses specific, recoverable information (see Failure modes), but the loss is often tolerable or even beneficial** because conversation is redundant with, and noisier than, the artefact it produced. The risk is not the absence of the transcript per se but the absence of the *provenance* the transcript would have implied.

## Rejected options

- **Treating current agent checkpoint systems (LangGraph, Temporal, DBOS) as evidence for artefact-only recovery.** Rejected because, on inspection (E4), their persisted state bundles the conversation history; they test state-replay, not the artefact-vs-conversation contrast H3 makes. They remain useful as the *baseline* against which artefact-only recovery would be compared.
- **Relying on vendor and blog sources as primary evidence.** Rejected in favour of peer-reviewed or preprint research (E1–E3, E5, E7) wherever available; blog material (E4, E6) is used only as illustrative context for current practice, clearly labelled.
- **Running a live empirical experiment.** Rejected as out of scope for this research deliverable; instead a concrete, runnable experiment is *designed* below. Empirical execution is left to a later validation phase.
- **Recommending a specific technology or implementation.** Explicitly excluded per research constraints; systems are named only as evidence or baselines.

## Unknowns

- **Direct LLM-agent evidence is thin.** No large-scale study was found that gives an LLM agent *artefact history with provenance and no conversation* and measures resume success vs. a conversation-history control. The claim is supported by analogy (workflows, Mylyn, HCI) and by emerging preprints (E5, E8), not by a definitive agent study.
- **Optimal provenance granularity is unknown.** How much provenance (intent? rejected alternatives? confidence? evidence links?) is necessary and sufficient for recovery is unmeasured. Too little → shallow recovery (E6); too much → token cost rivals conversation.
- **The trust/reuse payoff of provenance is under-studied** (Nguyen et al., 2011, E7) — the provenance community's core assumption lacks broad empirical confirmation.
- **Dynamic-environment recovery is untested here.** If the environment evolves during the interruption, a static artefact snapshot may be stale; HCI work (Labonté & Vachon, 2021) suggests post-interruption *reconstruction* of the environment matters, which artefact history alone may not supply.
- **Whether "recovery fidelity" can be operationalised cheaply** remains open (see Measures).

## Confidence

**Medium-High.**

*Justification:* The core claim — that an agent can recover from structured artefact history, and that this can be more efficient than conversation replay — is well-supported by independent, peer-reviewed evidence from workflow provenance recovery (E1), the Mylyn field study (E2), and HCI cue/resumption research (E3). The refinement that *provenance* (not merely versions) is the load-bearing element is strongly argued in recent preprints (E5, E8) and consistent with observed failure modes (E6). Confidence is capped at Medium-High rather than High because (a) direct empirical validation for *LLM agents specifically*, with conversation explicitly excluded, is still emerging rather than established, and (b) key parameters (provenance granularity, dynamic-environment recovery, fidelity metrics) are unknown. The hypothesis H3 is therefore *plausible and well-motivated by analogy*, with direct agent-level confirmation still pending.

## References

1. Ananthanarayan, S., et al. "Improving Workflow Fault Tolerance through Provenance-Based Recovery." *SSDBM*, 2011. (Springer: 10.1007/978-3-642-22351-8_12)
2. "Checkpointing for workflow recovery." *Proceedings of the 38th International Conference on Very Large Data Bases (VLDB)*, 2006 (SIGMOD 2006 reference, dl.acm.org/doi/10.1145/1127716.1127735).
3. Kersten, M., & Murphy, G. C. "Mylar: a degree-of-interest model for IDEs." *AOSD*, 2005 (10.1145/1052898.1052912).
4. Kersten, M., & Murphy, G. C. "Using Task Context to Improve Programmer Productivity." *FSE*, 2006 (eclipse.dev/mylyn/publications/2006-11-mylar-fse.pdf).
5. Altmann, E. M., & Trafton, J. G. "Task Interruption: Resumption Lag and the Role of Cues." *Proceedings of the Human Factors and Ergonomics Society Annual Meeting*, 2004 (10.1177/154193120404801507).
6. Hodgetts, H. M., & Jones, D. M. "Contextual cues aid recovery from interruption: the role of associative activation." *J. Exp. Psychol. Learn. Mem. Cogn.*, 32(5), 2006, 1120–1132.
7. Ghibellini, R., & Meier, B. "Interruption, recall and resumption: a meta-analysis of the Zeigarnik and Ovsiankina effects." *Humanities and Social Sciences Communications*, 12, 2025 (10.1057/s41599-025-05000-w).
8. Mark, G., Gonzalez, V. M., & Harris, J. "No task left behind? Examining the nature of fragmented work." *CHI*, 2005.
9. Vispute, N., & Kadam, A. "Reasoning Provenance for Autonomous AI Agents: Structured Behavioral Analytics Beyond State Checkpoints and Execution Traces." *arXiv:2603.21692*, 2026.
10. "AI Agents vs AI Workflows" (Temporal/DBOS durable execution summary). *Towards AI*, 2025 (pub.towardsai.net/ai-agents-vs-ai-workflows-why-95-of-production-systems-choose-workflows).
11. Microsoft Agent Framework, issue #2144, "Support mid-step checkpointing for executor state persistence," 2025 (github.com/microsoft/agent-framework/issues/2144).
12. "Recovering Lost Context: Using TiDB to Prevent AI Agents from Repeating Past Mistakes." *zenn.dev*, 2026.
13. Pan, T. "Context Engineering: Memory, Compaction, and Tool Clearing for Production Agents." *tianpan.co*, 2026.
14. Boufford, N., et al. "Computational Experiment Comprehension using Provenance Summarization." *ACM Conference on Reproducibility and Replicability (REP'24)*, 2024 (10.1145/3641525.3663617).
15. Nguyen, P., et al. "Provenance, End-User Trust and Reuse: An Empirical Investigation." *iConference*, 2011.
16. "Workflow as Knowledge: Semantic Persistence for LLM-Mediated Workflows." *arXiv:2607.08740*, 2026.
17. "A Dataset Capturing Decision Processes, Tool Interactions and Provenance Links in Autonomous AI Agents" (AgentSec). *MDPI Data*, 11(4), 2026 (10.3390/data11040066).
18. Labonté, K., & Vachon, F. "Resuming a Dynamic Task Following Increasingly Long Interruptions: The Role of Working Memory and Reconstruction." *Front. Psychol.*, 12:659451, 2021 (10.3389/fpsyg.2021.659451).

---

### Appendix — A designed (not executed) experiment for RQ6

**Design.** Prepare a realistic interrupted task (e.g., a versioned design document or code module) with explicit artefact history: ordered versions, supersession links, evidence references, and decision records (including rejected alternatives and rationale). Withhold all conversation history. Give a fresh agent the artefact history plus the original task brief and ask it to resume. Run three conditions:
- **A (artefact + provenance, no conversation):** the hypothesis condition.
- **B (artefact versions only, no provenance, no conversation):** tests whether provenance is load-bearing (per F3).
- **C (conversation history + state checkpoint, no separate artefact provenance):** the current-practice baseline (per E4).

**Success criteria.**
- *Primary (from H3):* tokens required to resume (A ≤ C expected) and task-completion rate (A ≈ C, with B expected lower if provenance matters).
- *Recovery fidelity:* does the agent resume at the correct artefact/state and take the correct next step?
- *Repetition-of-mistakes rate:* does it re-propose a decision already rejected in the artefact history? (Direct test of the E6 failure mode.)
- *Provenance-completeness score:* are the agent's resumed actions traceable to artefact entries?

**Predicted outcome under H3.** A matches C on completion while using fewer tokens; B underperforms A on fidelity and repetition-of-mistakes, isolating provenance as the active ingredient. This would convert the Medium-High confidence above into High.
