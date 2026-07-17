# RQ7 — Existing engineering methodologies

## Question

What concepts from existing engineering methodologies and tools already exist and should not be reinvented? Specifically, for five named methodologies/tools — SEMAT Essence, OMG SPEM, ArchiMate, OpenProject, and Jira Advanced Roadmaps — identify their core concepts, the overlap with EDASES concepts (artefacts, versions, evidence, provenance, supersession, lifecycles), the ideas EDASES could reuse without importing the whole methodology, what each does *not* cover that EDASES needs, and what adoption practice teaches. The goal is to surface existing intellectual property EDASES should reference rather than reinvent, and to locate the gaps where EDASES has genuinely novel contributions.

## Scope

**Investigated:**
- SEMAT Essence (the OMG "Essence — Kernel & Language for Engineering Methods" standard): kernel alphas, alpha states, checklists, the kernel/practice separation, and documented adoption cases.
- OMG SPEM 2.0 (Software & Systems Process Engineering Metamodel): the Method Content vs. Process split, work products, roles, tasks, guidance, phases/iterations/milestones, and variability (base/extension).
- ArchiMate (The Open Group enterprise architecture language): the layered framework, aspects, the Motivation extension (stakeholder, driver, goal, requirement, constraint, principle), the Implementation & Migration extension (work package, deliverable, plateau, gap), and the relationship vocabulary.
- OpenProject (open-source project management): work packages, types, status workflows, versions/releases, wiki, documents, baseline comparison, work-package relations/hierarchies.
- Jira Advanced Roadmaps, now branded "Plans" (advanced planning in Jira Premium/Enterprise): plans, work-item sources, releases/versions, teams, dependencies, scenarios (sandbox), capacity, auto-schedule.

**Excluded:**
- Detailed internal metamodel formalisation beyond what is needed to map overlaps (e.g., full SPEM XMI, full ArchiMate metamodel class inventory).
- Tools not in the named set (e.g., other PM suites, other EA tools) except where cited as adoption evidence.
- Any recommendation or implementation proposal (forbidden by task rules). Systems are named only as evidence of existing concepts.
- The separate but related question of whether EDASES should *conform* to any of these (out of scope; this report only identifies what exists and what is missing).

**Framing note (assumption, labelled):** The EDASES concept set used for mapping — artefacts, versions, evidence, provenance, supersession, lifecycles — is taken from the EDASES research/execution-engine context (see e.g. RQ6, which treats "artefacts, versions, provenance, supersession links, evidence, decisions" as the recovery substrate and "reasoning as the primary artefact" as the stance). This framing is treated as given for the mapping; it is not re-derived here.

## Evidence

### E1. SEMAT Essence — kernel, alphas, states, checklists
- **Observation:** Essence is an Object Management Group (OMG) standard ("Essence — Kernel & Language for Engineering Methods"); the OMG spec page lists v1.1 and a v2.0 beta 2 published March 2026 (omg.org/spec/Essence). It is *not* an ISO/IEC 19510 standard — that number belongs to BPMN (omg.org/industries/finance.htm). The kernel was developed under the SEMAT initiative founded in 2009 (Wikipedia "SEMAT"; InfoQ "SEMAT", 2010).
- **Observation:** The Essence kernel defines seven "alphas" — Opportunity, Stakeholders, Requirements, Software System, Team, Work, Way of Working — as the elements "always prevalent in every engineering endeavor" (ACM Queue, "The Essence of Software Engineering: The SEMAT Kernel"; Wikipedia "SEMAT").
- **Observation:** Each alpha progresses through a sequence of named **states** with **checklists** of conditions that must be met to enter a state. Example documented states: Stakeholders — Recognized, Represented, Involved, In Agreement, Satisfied for Deployment, Satisfied in Use; Requirements — Conceived, Bounded, Coherent, Acceptable, Addressed, Fulfilled (ResearchGate figure "Essence kernel alphas and their states"; InfoQ Fujitsu article). Projects may fall back to earlier states or achieve several simultaneously.
- **Observation:** Essence separates a small common **kernel** from a composable **library of practices** built on top of it; practices are composed into methods (ACM Queue; Amazon book description of "The Essence of Software Engineering").
- **Interpretation (labelled):** The alpha/state/checklist structure is, in effect, a first-class *lifecycle* model where progress is tracked per persistent entity (the alpha) rather than per phase, and where state-entry is gated by explicit, inspectable criteria (the checklist). This is a reusable pattern, not a full method.

### E2. SEMAT Essence — adoption evidence and critique
- **Observation:** Documented field use includes Fujitsu UK, which used the Essence cards and alphas to "essentialize" processes and to align teams on project state via low-tech card walls (InfoQ, "Using SEMAT and Essence at Fujitsu UK", 2016).
- **Observation:** A CMU practicum field study introduced Essence to master's students to evaluate its monitoring/steering value, decomposing the study into RQs about whether and how the alpha-state approach adds value (ResearchGate, "State-Based Monitoring and Goal-Driven Project Steering: Field Study of the SEMAT Essence Framework").
- **Observation:** Early critique existed: the SEMAT call drew "heated criticisms" and at least one prominent signatory (Alistair Cockburn) withdrew; a "nothing new" critique argues Essence "has nothing new to offer in terms of content" but usefully highlights what matters (Amazon review excerpt; Formtek blog citing Cockburn).
- **Observation:** A 2013 paper (Graziotin & Abrahamsson, arXiv:1307.2075) states Essence "is yet far from reaching academic and industry adoption" and attributes this partly to "the lack of tools implementing it," presenting SematAcc as a web tool to address that gap.
- **Interpretation (labelled):** Essence has credible, if niche, adoption as a *thinking framework / common language*, but its industry footprint is limited and tooling has been a recurring barrier. The lesson for EDASES is about adoptability, not about the concepts being wrong.

### E3. OMG SPEM 2.0 — method content vs. process, work products, variability
- **Observation:** SPEM 2.0 (OMG, v2.0 April 2008; v1.0 Nov 2002) is a "process engineering metamodel as well as conceptual framework" for modelling, documenting, presenting, managing, interchanging, and enacting development methods and processes (omg.org/spec/SPEM/2.0/PDF).
- **Observation:** SPEM distinguishes two views: **Method Content** (tasks, work products, roles, guidance such as white papers/principles/best practices) and **Process** (how content is orchestrated via activities, phases, iterations, milestones) (SPEM 2.0 spec excerpt; es.mdu.se pdf on SPEM-based variability).
- **Observation:** A **Work Product** is a defined output of method content; work-product *states* can drive different responsibilities (e.g., a bug work item assigned to a developer when "open", to a tester when "resolved") (OMG SPEM 2.0 FTF open issues).
- **Observation:** SPEM provides **variability** via base/extension element pairs with relationships `na`, `contributes`, `replaces`, `extends`, `extends and replaces`, intended to speed reuse of process elements (es.mdu.se pdf). The same source notes SPEM 2.0's variability support is "intended to make faster the definition of new process elements and does not provide guidance for the reuse of process elements between similar processes" — i.e., a documented limitation.
- **Observation:** SPEM is tool-supported via the open-source EPF Composer and IBM Rational Method Composer (es.mdu.se pdf).
- **Interpretation (labelled):** SPEM's durable, reusable idea is the *separation of what is produced (work products) and who does it (roles/tasks) from how it is sequenced (process)*, plus an explicit variability mechanism. Work products are the closest SPEM analogue to EDASES artefacts, and work-product states are a weak analogue to lifecycle states.

### E4. ArchiMate — layers, aspects, Motivation and Implementation & Migration extensions
- **Observation:** ArchiMate (The Open Group) is an enterprise architecture modelling language with a Core Framework of three layers — Business, Application, Technology — extended by Strategy, Motivation, Implementation & Migration, and Physical layers/aspects (Visual Paradigm "What is ArchiMate?"; Sparx EA ArchiMate framework page; Grokipedia "ArchiMate").
- **Observation:** Within each layer, elements are categorised into aspects: active structure (e.g., actors, roles), behaviour (e.g., processes, functions), and passive structure (e.g., data objects, artefacts) (Visual Paradigm; leanix.net ArchiMate explainer).
- **Observation:** The **Motivation extension** models stakeholders, drivers, assessments, goals, outcomes, principles, requirements, and constraints (Hinkelmann slides "ArchiMate Motivation and Strategy"; Visual Paradigm motivation extension). Drivers are associated with stakeholders; assessments yield strengths/weaknesses/opportunities/threats; goals are realised by requirements.
- **Observation:** The **Implementation & Migration extension** models work packages, deliverables, plateaus, and gaps, used for transition/migration planning and gap analysis (Visual Paradigm; Bizzdesign ArchiMate Implementation and Migration elements page; Open Group blog on traceability).
- **Observation:** ArchiMate defines a rich **relationship vocabulary** — structural (composition, aggregation, specialization), dependency (serving, access, influence), dynamic (triggering, flow), and "realization" — connecting elements across layers (Visual Paradigm; leanix.net).
- **Interpretation (labelled):** ArchiMate's Motivation extension is the closest of the five methodologies to an *evidence/why* vocabulary (goals, requirements, constraints, principles as the rationale behind elements), and its relationship types (realization, trigger, flow, serving) are the closest to a *provenance/derivation* link vocabulary. The Implementation & Migration extension (deliverable → plateau → gap) is the closest to a *version/supersession/transition* model.

### E5. OpenProject — work packages, versions, status, baseline comparison
- **Observation:** OpenProject "work packages" are project items (tasks, features, risks, user stories, bugs, change requests) with a type, ID, subject, and attributes including status, assignee, priority, due date (openproject.org/docs/user-guide/work-packages).
- **Observation:** Work-package **status** is configurable (e.g., new, in progress, done, on hold, rejected, closed) and drives a workflow; the default status is "New" (openproject.org/docs/system-admin-guide/manage-work-packages/work-package-status).
- **Observation:** OpenProject has a **Versions** concept (a release, linkable from wiki as `version:"Release 1.0.0"`) and a **Baseline comparison** feature to "track work package changes over time" (work-packages docs overview; wiki link syntax).
- **Observation:** OpenProject supports **work-package relations and hierarchies** and a wiki/documents module for collaborative project documentation (work-packages docs; documents docs; wiki docs).
- **Interpretation (labelled):** OpenProject's baseline comparison is a practical, adoptable pattern for *versioning/supersession tracking* (snapshot + diff over time), and its configurable status workflows are a practical lifecycle-state pattern. Work packages are a pragmatic artefact analogue, but they carry no provenance or evidence semantics.

### E6. Jira Advanced Roadmaps ("Plans") — plans, releases, dependencies, scenarios
- **Observation:** "Advanced planning" in Jira is delivered through a feature called **Plans**; it was formerly "Portfolio for Jira" then "Advanced Roadmaps" (Atlassian advanced-planning guide; Udemy "Jira Plans (JIRA Advanced Roadmaps)"; Visor "Jira Advanced Roadmaps (Plans)"). It is available in Jira Premium/Enterprise.
- **Observation:** A Plan pulls work-item sources (boards, spaces, filters), schedules work, allocates **capacity**, maps **dependencies**, and models different **scenarios** "all within a single source of truth"; it functions "as a sandbox environment" where you plan and experiment before updating original Jira data (Atlassian advanced-planning overview).
- **Observation:** Plans operate over **releases/versions** (shown as health indicators on the timeline) and **teams** (with agile method and weekly capacity; suggested velocity from past sprints) (Atlassian/Confluence Advanced Roadmaps docs; Udemy course description).
- **Observation:** Until changes are committed via "Review changes", edits "only live in your plan" — i.e., the plan is a separate, tentative layer above the issues (Confluence Advanced Roadmaps "View your plan").
- **Interpretation (labelled):** The scenario/sandbox pattern — exploring alternative plans *before* committing them to the canonical issues — is a strong, adoptable UX/interaction pattern that maps onto EDASES's need to hold *alternative artefact versions* without prematurely superseding the current one. Releases/versions and dependency modelling are direct analogues to EDASES versioning and provenance-style links.

### E7. Cross-reference — provenance standards outside the five
- **Observation:** The W3C PROV family (PROV-DM etc.) defines a domain-independent provenance data model (entities, activities, agents, and relations such as wasGeneratedBy, wasDerivedFrom, wasAttributedTo). RQ6 already cites PROV-DM-compliant provenance as the relevant standard for agent decision/tool provenance (RQ6 evidence E8; w3.org/TR/prov-dm).
- **Interpretation (labelled):** None of the five methodologies above adopt PROV semantics. This is the central gap EDASES fills, and PROV is the existing standard EDASES should reference rather than reinvent.

## Findings

**F1 — All five already model "artefacts" and "lifecycles"; EDASES should reuse those vocabularies, not rename them.** Essence alphas (E1), SPEM work products (E3), ArchiMate elements/deliverables (E4), OpenProject work packages (E5), and Jira issues (E6) are all persistent "things we produce/track." Essence alpha states + checklists (E1), SPEM work-product states (E3), ArchiMate plateaus (E4), OpenProject status workflows (E5), and Jira statuses (E6) are all lifecycle-state models. EDASES's "artefact" and "lifecycle" concepts are therefore *not* novel at the type level; the novel part is what is attached to them (see F4–F6).

**F2 — Essence's alpha/state/checklist pattern is the strongest existing model of lifecycle-as-progress-of-a-persistent-entity.** Unlike phase-based models (SPEM phases, OpenProject Gantt), Essence tracks state *per alpha* with inspectable entry criteria (E1). This is directly reusable by EDASES as the shape of an artefact lifecycle: a typed entity advancing through named states gated by explicit, recorded criteria. EDASES need not invent "lifecycle states with entry conditions" — that already exists.

**F3 — ArchiMate supplies the richest reusable vocabulary for the two concepts the others neglect: motivation (why) and relationships (derivation).** The Motivation extension (goal/requirement/constraint/principle/stakeholder) is the closest existing vocabulary to EDASES "evidence" and "rationale" (E4). The relationship types — realization, triggering, flow, serving, influence — are the closest existing vocabulary to EDASES "provenance links" (E4). EDASES can adopt this relationship taxonomy as a starting ontology for provenance-link types rather than designing one from scratch.

**F4 — None of the five provides first-class, PROV-style provenance.** Essence checklists record *that* criteria were met, not *who/what/when/why generated* an artefact or *from what it was derived* (E1, E7). SPEM has "method content trace" dependencies but no provenance model (E3). ArchiMate relationships imply derivation but are not provenance records with agents/activities/timestamps (E4). OpenProject and Jira track status and assignments but not provenance (E5, E6). **This is the primary gap EDASES fills and the primary novel contribution** — provenance as a first-class, queryable, PROV-aligned layer (consistent with RQ6's "reasoning provenance cannot be reconstructed from state," E5 in RQ6).

**F5 — None provides a first-class "evidence" concept linking claims to supporting/contradicting artefacts.** ArchiMate's Motivation extension comes closest (requirements/constraints as rationale) but it is about *intent*, not *evidence for a claim* (E4). Essence checklists are acceptance criteria, not evidence records (E1). EDASES's evidence concept (supporting/contradicting links to specific artefact versions) is therefore novel relative to these five.

**F6 — Supersession is only weakly present; EDASES can reuse the *patterns* but must supply the *semantics*.** OpenProject baseline comparison (snapshot+diff) (E5), Jira scenario sandbox before commit (E6), and ArchiMate plateau/gap transitions (E4) all model "a later state replaces an earlier one," but none records *why* a version supersedes another with provenance of the supersession. EDASES's supersession concept (a typed link with reason + provenance) is a sharpening of patterns that already exist in practice.

**F7 — The kernel/practice and content/process separations are validated reusable architectures.** Essence's kernel-vs-practice (E1) and SPEM's method-content-vs-process (E3) are two independent confirmations that separating *stable common concepts* from *composable, context-specific practices* is a sound architecture. EDASES's own layered separation (research/methodology/execution) is consistent with this and need not be justified from first principles.

**F8 — Adoption teaches that standards without tooling and without a unique, demonstrable payoff struggle.** Essence's limited industry uptake is explicitly linked to a tooling gap (E2). SPEM is standardised and tool-supported but criticised as heavy/complex with limited variability guidance (E3). ArchiMate succeeded where it had an open reference tool (Archi) and integration with TOGAF (E4). OpenProject and Jira Plans succeeded through pragmatic, adoptable patterns (configurable workflows; scenario sandbox) (E5, E6). **Interpretation (labelled):** the lesson for EDASES is about *adoptability* — reuse proven vocabularies (F1–F3), supply the missing provenance/evidence/supersession semantics (F4–F6), and pair any standard with usable tooling — not about the conceptual content being wrong.

## Rejected options

- **Treating ISO/IEC 19510 as the Essence standard.** Rejected: the search evidence shows ISO/IEC 19510:2013 is BPMN (omg.org/industries/finance.htm). Essence is an OMG standard (v1.1; v2.0 beta 2, 2026). This correction matters because misattributing a standards body would weaken the report's credibility.
- **Claiming any of the five already covers provenance or evidence.** Rejected: the evidence (E1–E7) shows each models artefacts/lifecycles/versions but none provides PROV-style provenance or a first-class evidence concept. Overstating overlap would hide EDASES's actual novel contribution.
- **Recommending EDASES adopt a specific one of these methodologies wholesale.** Rejected per task rules (no implementation recommendation) and because the findings show the value is in *reusing specific concepts* (alphas/states, motivation vocabulary, relationship types, baseline comparison, scenario sandbox), not in importing an entire methodology.
- **Relying on vendor/marketing descriptions as primary evidence for Jira Plans / OpenProject.** Rejected where possible in favour of vendor documentation and independent guides; blog/marketplace material (e.g., Visor, Released) is used only as illustrative context for current capability, clearly labelled.

## Unknowns

- **U1.** The precise extent of *production* EDASES-relevant adoption of Essence beyond the documented Fujitsu UK and CMU cases is not established here; the 2013 paper's "far from adoption" claim may be dated by the 2026 v2.0 beta, but current adoption figures were not extracted.
- **U2.** Whether EDASES's "artefact" should be a strict superset of, or merely analogous to, SPEM work products / ArchiMate deliverables / OpenProject work packages is a modelling decision not resolved by this report (it only identifies the overlap).
- **U3.** The degree to which ArchiMate's relationship vocabulary (realization, trigger, flow, serving, influence) is sufficient as an EDASES provenance-link ontology, versus needing PROV's wasGeneratedBy/wasDerivedFrom/wasAttributedTo, is not determined here; this report flags the vocabulary as reusable starting material, not a complete provenance model.
- **U4.** Whether Jira "Plans" and OpenProject "Versions" semantics (release-oriented) map cleanly onto EDASES versioning (which is artefact-version-centric with supersession) is assumed by analogy, not verified against EDASES's exact version model.
- **U5.** The current (2026) tooling landscape for Essence (beyond the 2013 SematAcc) was not comprehensively surveyed; the "tooling gap" conclusion rests on the 2013 paper and may be partially outdated.

## Confidence

**Medium-High.**

*Justification:* The core mapping claims — that all five model artefacts and lifecycles, that Essence provides the strongest lifecycle-state pattern, that ArchiMate supplies the richest motivation/relationship vocabulary, and that none provides PROV-style provenance or a first-class evidence concept — are well-supported by primary sources (OMG/Open Group specs, vendor documentation, peer-reviewed/archived field studies and papers: E1–E7). The identification of the provenance/evidence/supersession gap as EDASES's novel contribution is consistent with RQ6's independent finding that provenance is the load-bearing, non-reconstructable recovery substrate.

Confidence is capped at Medium-High rather than High because: (a) adoption lessons (F8) rest partly on dated or single-source evidence (the 2013 Essence-adoption paper; SPEM variability critique from one paper); (b) the exact fit of ArchiMate's relationship vocabulary to an EDASES provenance ontology (U3) and the precise artefact/version mapping (U2, U4) are modelling questions not fully resolved by this evidence survey; and (c) current-state adoption data for Essence (U1, U5) was not exhaustively updated. The factual claims about *what each methodology contains* are High confidence; the *lessons and gaps* synthesis is Medium-High.

## References

1. OMG — "Essence — Kernel & Language for Engineering Methods" specification (v1.1; v2.0 beta 2, Mar 2026): https://www.omg.org/spec/Essence/
2. Jacobson, I., Ng, P.-W., McMahon, P. E., Spence, I., Lidman, S. — "The Essence of Software Engineering: The SEMAT Kernel," ACM Queue: https://queue.acm.org/detail.cfm?id=2389616
3. Wikipedia — "SEMAT": https://en.wikipedia.org/wiki/SEMAT
4. InfoQ — "SEMAT - Software Engineering Method and Theory" (2010 manifesto): https://www.infoq.com/news/2010/04/semat
5. InfoQ — "Using SEMAT and Essence at Fujitsu UK" (2016): https://www.infoq.com/articles/semat-essence-fujitsu
6. ResearchGate — "Essence kernel alphas and their states" (figure) / "State-Based Monitoring and Goal-Driven Project Steering: Field Study of the SEMAT Essence Framework": https://www.researchgate.net/figure/Essence-kernel-alphas-and-their-states_fig1_264860972
7. Graziotin, D., Abrahamsson, P. — "A Web-based modeling tool for the SEMAT Essence theory of Software Engineering," arXiv:1307.2075 (2013): https://arxiv.org/abs/1307.2075
8. Formtek blog — "Methodology: SEMAT and Next Generation Software Engineering" (notes Cockburn withdrawal / criticisms): https://formtek.com/blog/methodology-semat-and-next-generation-software-engineering
9. OMG — "Software & Systems Process Engineering Metamodel (SPEM) 2.0" specification: https://www.omg.org/spec/SPEM/2.0/PDF
10. OMG — "About SPEM 1.0": https://www.omg.org/spec/SPEM/1.0/About-SPEM
11. MDU Eskilstuna — SPEM 2.0-based variability engineering / eSPEM (notes SPEM variability limitations): https://www.es.mdu.se/pdf_publications/4510.pdf
12. Visual Paradigm — "What is ArchiMate?": https://www.visual-paradigm.com/guide/archimate/what-is-archimate/
13. Sparx Systems — "The ArchiMate Framework" (EA user guide): https://sparxsystems.com/enterprise_architect_user_guide/17.1/modeling_frameworks/archimate_framework_top.html
14. Hinkelmann, K. — "ArchiMate Motivation and Strategy" (slides): http://knut.hinkelmann.ch/lectures/ABIT2017-18/ABIT%2006-3%20ArchiMate%203%20Motivation%20and%20Strategy.pdf
15. Bizzdesign — "ArchiMate Implementation and Migration elements": https://help.bizzdesign.com/articles/#!horizzon-help/archimate-implementation-and-migration-elements
16. The Open Group blog — "Redefining traceability in Enterprise Architecture … with TOGAF 9.1 and/or ArchiMate 2.0": https://blog.opengroup.org/2013/09/12/redefining-traceability-in-enterprise-architecture-and-implementing-the-concept-with-togaf-9-1-andor-archimate-2-0/
17. OpenProject docs — "Work packages": https://www.openproject.org/docs/user-guide/work-packages/
18. OpenProject docs — "Manage work package status": https://www.openproject.org/docs/system-admin-guide/manage-work-packages/work-package-status
19. OpenProject docs — "Documents": https://www.openproject.org/docs/user-guide/documents
20. OpenProject docs — "Wiki": https://www.openproject.org/docs/user-guide/wiki
21. Atlassian — "Advanced planning guide in Jira" (Plans / formerly Advanced Roadmaps): https://www.atlassian.com/software/jira/guides/advanced-roadmaps/overview
22. Atlassian Confluence — "View your Advanced Roadmaps plan" (scenario/sandbox, Review changes): https://confluence.atlassian.com/jirasoftwareserver/view-your-advanced-roadmaps-plan-1044784216.html
23. Visor — "Jira Advanced Roadmaps (Plans) Guide": https://www.visor.us/blog/jira-advanced-roadmaps
24. Udemy — "Master Jira Advanced Roadmaps for Agile Project Planning" (notes former Portfolio / Advanced Roadmaps → Plans): https://www.udemy.com/course/advanced-roadmaps-jira
25. W3C — PROV-DM: The PROV Data Model: https://www.w3.org/TR/prov-dm/
26. EDASES RQ6 report — "Can an agent recover a task using only artefact history rather than conversation history?" (provenance-as-knowledge, PROV-DM reference): /home/claude-code/projects/ASES/research/execution-engine-ui/reports/rq6-artefact-recovery.md

---
