# Claude Reserarch Level Classification

## Finding

The three-level model holds up structurally, but the sixteen questions don't distribute evenly across it: ten classify EDASES-primary, four ASES-primary, two Execution-primary. Two pairs are the same question asked twice rather than genuinely separate ones (E/K, J/F), three questions (C, M, and partly L) are applied instances of one master question (N), and one question (D) resists a single primary level more than any other item in the set. The sixteen compress to four fundamental tracks. The most useful missing question is one the corpus never turns on itself: how would anyone know, empirically, whether the resulting system actually produced more trustworthy software.

## Method

For each question: is this a claim about what's true independent of implementation (EDASES), a claim about how work should be conducted or who's authorized to do it (ASES), or a claim about what code, state, or protocol enforces that (Execution)? Nearly every question in the set is phrased as an open "what should X" or "can X ever be Y" hypothesis regardless of its actual content, and that interrogative register reads as EDASES by default even where the content underneath is procedural. I classified by content rather than phrasing, per the document's own instruction not to classify by current implementation — the same instruction, applied to phrasing instead of implementation.

## Classification

| # | Question | Primary | Secondary | Note |
|---|---|---|---|---|
| A | Authority Boundary Comparison | EDASES | ASES | Lens the authority cluster (B, D, G, I, O) uses — not independent |
| B | Execution Trust | EDASES | ASES | Same shape as the doc's own "completion" example, generalized to all assertions |
| C | Restart Survivability | Execution | EDASES | Applied instance of N, plus Execution-only concerns (admission control, quota parking) |
| D | Merge/Integration Authority | EDASES | ASES + Execution | Resists a single primary most; verification's non-composability shows up here |
| E | Distributed Systems + Probabilistic Participants | EDASES | — | The load-bearing hypothesis; K is how you'd test it |
| F | Skeleton Factory | ASES | EDASES + Execution | Content is ASES/Execution vocabulary; purpose is EDASES — J's discipline, applied once |
| G | Context Hydration | EDASES | ASES + Execution | Explicitly folds into A's authority track by its own closing line |
| H | Model Capability Matrix | EDASES | ASES | Reviewer/model selection is a named ASES bullet in the source document |
| I | Substrate Self-Repair | EDASES | ASES + Execution | The bootstrapping case of A — repairing what defines your own authority |
| J | Compression Discipline | ASES | EDASES | F is this, run once, against Gas Town |
| K | Distributed-Systems Prior Art | EDASES | — | E's empirical test methodology, not a separate question |
| L | Liveness and Progress | Execution | EDASES + ASES | Continuous-claim version of B — progress vs. completion, same evidence problem |
| M | Crosslink/Work Substrate | ASES | Execution | Applied instance of N; locks/worktrees/coordination are genuinely Execution content |
| N | State/Durable Execution Boundary | EDASES | ASES + Execution | The master question — C and M are worked instances of it |
| O | RPC/Process Boundary | ASES | Execution | Self-decomposes per its own closing sentence |
| P | Verification and Review Architecture | EDASES | ASES + Execution | B applied to review specifically; supplies H's "quorum" its building blocks |

## Is a level overloaded

Yes — EDASES, by a wide margin, and it's only partly a real finding. Some of it is an artifact of how the questions are written: M asks "what should the durable work substrate represent," which reads like a principle question but is actually a work-and-dependency-model spec — an ASES bullet by the document's own definitions. O asks "where should authority and state cross process boundaries," which reads the same way, but its own final sentence resolves it into an ASES/Execution split with no EDASES component stated at all. Correcting for phrasing brings the count down from what a naive pass would produce, and the skew still doesn't disappear — it lands at 10-4-2 rather than something closer to even. That remainder looks real rather than cosmetic: the research program, at this stage, is still mostly occupied with establishing what's true, and ASES hasn't yet been given open questions of its own so much as it's been receiving the second half of whatever an EDASES question leaves over. If that's accurate, ASES is the underspecified level — it needs questions generated from "how would we actually run this," not just inherited as authority and evidence questions' procedural residue.

## Clusters to combine

**E and K.** E states the hypothesis that agent systems are distributed systems with non-authoritative, probabilistic participants, and says outright it should be tested rather than assumed. K then asks exactly how you'd test it — which parts of existing systems (Temporal, Kubernetes, MapReduce) already solve the problem, and where they stop being sufficient. There's no daylight between "test this hypothesis" and "here's the prior-art comparison that tests it." Write these as one question with two parts, not two questions.

**J and F.** J asks whether "architectural compression" — demonstrating why a new mechanism can't be expressed as an existing state transition or capability restriction — should be a research hypothesis, an ASES rule, or a design discipline. F is that discipline run once, against Gas Town, producing a candidate eight-term minimal vocabulary. F doesn't need independent billing; it's J's worked example, and its output is the evidence that would actually settle J's question.

**N, C, and M.** N asks what the correct unit of durable state is. C asks what must survive an Execution Engine restart. M asks where Crosslink's responsibilities end and Execution Engine state begins. C and M are the same underlying question — what counts as enduring truth versus current execution — applied to two specific boundaries. Keep N as the open question and fold C and M in as worked cases, the way F folds into J, with one exception: C also carries a few genuinely independent operational concerns (admission control, quota parking, doom-loop prevention) that don't reduce to the state-boundary question and would still need answering even after N is settled.

**B, L, and P — a looser cluster, not a full merge.** All three ask some version of "can a claim be trusted, and what would make it trustworthy": B for completion claims generally, L for progress claims (the continuous, non-terminal version), P for the specific taxonomy of review types and what each can establish. Don't collapse these the way E/K or J/F collapse — each adds content the others don't. L's stall/loop detection is structurally about proving an absence, a different problem from evaluating a claim that's present. P's review taxonomy is a useful artifact in its own right. But write and research them as a family, with B as the general statement and L and P as its two specializations.

## Questions that decompose across levels

**D — Merge/Integration Authority.** EDASES: does verifying each change in isolation ever license treating the set as safe, or does correctness at the item level and correctness at the integration level require separate authority entirely? ASES: what evidence has to exist before a batch is allowed to merge, and who signs off on it. Execution: the actual batching and queue mechanics — Bors-style batching, merge queues, stacked-diff tooling.

**G — Context Hydration.** EDASES: is discoverability itself a form of authority — does giving an agent the ability to find something implicitly grant it the ability to use it, making scope and permission the same boundary? ASES: what a context contract looks like as a methodology object — what's promised to an agent before work starts, and what counts as going outside it. Execution: path allowlists, capability restrictions, Crosslink query-boundary mechanics. O carries the same shape of claim — is crossing a process boundary always an authority-relevant event — but never states it the way G does; I'd surface it explicitly if I were rewriting O.

**L — Liveness and Progress.** EDASES: process existence, session health, and meaningful progress are three different claims — largely already settled elsewhere in the source material ("process liveness does not imply work progress" is stated flatly as a finding, not posed as open), which is part of why L scores Execution-primary rather than EDASES-primary. ASES: the recovery policy once non-progress is suspected — how many stalled cycles before escalation, and to whom. Execution: the detection machinery itself — heartbeats, event-stream monitoring, timers, resource limits.

I and N decompose the same three ways but around a dominant EDASES center rather than an even split — see the table notes.

## Missing questions

**How would anyone know this worked.** Every other question asks about a mechanism or a boundary; none asks about the evaluation methodology for the system as a whole. The project goal names verifiably trustworthy software as the target, and EDASES's own charter includes empirical programs meant to establish or falsify general claims — but that empirical posture is never turned on the project's own success criteria. Without a benchmark, a defect-injection protocol, or a longitudinal reliability measure, there's no way to tell whether the eventual ASES methodology and Execution Engine actually reduce the failure modes in the project goal, versus just relocating them. This belongs at EDASES, and probably ranks above E in priority — it's what would let you tell whether E turned out to be true in practice.

**Where the human actually has to be.** The EDASES charter names "distinctions between human, model, methodology, and machine authority" as core subject matter, and ASES's own definition lists human/model interaction as a methodology concern — but none of A through P asks directly what the minimum viable human touchpoint is. B, D, and I all ask who or what holds authority, and every one of them frames the contrast as agent versus system substrate, never agent versus human. Given how central that distinction is to the stated charter, its absence from the question list reads like an oversight, not a deliberate exclusion.

**Coordination cost as a design input, not just a failure mode.** The project goal lists excessive token expenditure on coordination as a failure mode to avoid, and the Gas Town findings already state that orchestration should not consume unnecessary model tokens and that pathological work-graph expansion is a real failure mode. H considers model-capability differences only as a reliability lever, explicitly setting aside cost/performance routing as the lesser frame. But no question in A–P turns either finding into something to actually resolve: what is the token or compute budget for orchestration itself, and how should that budget bound work-graph complexity as it scales. Treated only as a failure mode to avoid, cost never gets promoted to a design input the way authority and evidence do.

## Reduced set of fundamental tracks

**I. Authority, trust, and evidence.** What can an agent's assertion establish on its own, and what converts an unverified claim into accepted state. Covers A (as lens), B, G's deep question, H, I, L, O's deep question, and P.

**II. State identity and durability.** What is the enduring unit of truth about a piece of work, and where does it live across process and restart boundaries. Covers N as the master question, with C and M as worked instances.

**III. Compositional correctness.** Whether an assertion verified in isolation stays true once combined with others — the one place in the corpus where a "yes, trustworthy" answer from Track I turns out not to survive composition. Covers D.

**IV. Novelty and parsimony.** Which parts of the problem are already solved by conventional distributed systems, and what discipline keeps the design from accumulating mechanism that isn't actually necessary. Covers E, K, J, and F.

Track III is the judgment call I'd flag against myself. D could fold into Track I as its hardest case rather than standing alone — I've kept it separate because "individually correct doesn't imply collectively correct" is a different kind of claim than "this individual claim may or may not be trustworthy," but a different reviewer collapsing this into three tracks instead of four wouldn't be wrong.

## The strongest argument against the three-level separation

Not the obvious one. The obvious objection is that several questions (D most of all, then G and O) won't sit at a single level — but that's a weak critique, because authority and state are cross-cutting concerns in any layered system, the same way a security policy legitimately touches architecture, coding standards, and CI configuration without that being evidence the layers are wrong. Splitting across levels is what good layering looks like, not a symptom of bad layering.

The real weakness is directional. EDASES → ASES → Execution is presented as a dependency order: what's fundamentally true, then what methodology follows from it, then what enforces the methodology — implying EDASES gets settled first and the other two levels consume its output. This document's own material contradicts that order twice over. First, by provenance: these questions exist because Gas Town and Gas City were built and failed in specific, concrete ways, and several of the "settled" Gas Town findings listed here — completion requires external evidence rather than self-report, process liveness doesn't imply progress, supervision of agents by other agents creates recursive failure modes — were extracted from Execution-level experience, not derived first and handed down to it. Second, by inconsistency: B reopens "can an agent's completion claim ever be authoritative" as a live EDASES question, even though the findings list earlier already states the answer as settled. If completion-requires-external-evidence is settled, B is asking something else and should say what; if it isn't actually settled, the findings list oversold it. Either way, the document treats the same claim as both established EDASES output and open EDASES input at once — which is exactly what you'd expect if the real dependency runs in both directions rather than one.

## Where I'd expect independent researchers to disagree most

- **D's status.** Scored here as spanning all three levels with no dominant one. A researcher who reads "authority" as the load-bearing word will likely fold D straight into Track I and miss the compositional-correctness point as something structurally distinct.
- **F's classification.** The one item where content and purpose point different directions — an ASES/Execution-shaped vocabulary proposal in service of an EDASES-shaped epistemic goal. Expect wide scatter: purely ASES from anyone reading it as a design deliverable, purely Execution from anyone reading its vocabulary (State Transition, Event, Agent Session) as implementation primitives.
- **A's status as a question at all.** Treated here as a lens the authority cluster uses rather than an independent question. A is also the most naturally EDASES-shaped item on the page — broad, comparative, principle-seeking — so other reviewers will likely keep it standalone rather than demoting it.
- **Whether E and K are really one question.** Prior-art literature review is a different research activity from hypothesis formation even in service of the same hypothesis, and a reviewer who weights activity over content will keep them apart.