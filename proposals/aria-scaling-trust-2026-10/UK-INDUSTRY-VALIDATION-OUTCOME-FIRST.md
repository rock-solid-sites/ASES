# Outcome-first plan — UK industry validation of verifiable agent authority
**Working planning document, 2026-10-30. Not a promise of an existing pilot, partner, certification, or production authorization.**
Applicant: independent individual PI. Project identity pending; separate from all unrelated businesses. Temporary AI models/subagents are tools, not team members.

## Twelve-month destination: practical infrastructure benefit
By the end of the award, produce a **reusable open-source authority-to-effect enforcement component** with (a) a specified set of actually mediated operations, (b) a reproducible test suite with nonvacuous successful tasks and adversarial negative controls, (c) integrations in at least two independent agent/host environments, and (d) an **aspirational target of two permissioned UK industry evaluations**, including **one controlled low-risk real operational workflow** if partner access and independent security gates permit it.

Public evidence should show that the component can exclude stale authority without preventing legitimate tasks; that it handles declared loss/recovery cases and unsupported routes honestly; and that UK organizations can integrate it without adopting a complete ASES orchestration stack.

### Outcomes, measured rather than asserted
| Destination | Evidence by award end | Failure / honest fallback |
|---|---|---|
| Portable reference component | Public source, versioned interface, integration documentation, list of supported resources/effects/OS/kernel profiles and TCB, two independent integration implementations | Publish a narrower confirmed profile if a second attachment or platform fails its security gates |
| Adversarial assurance | Independently re-runnable reference/host suite, independent human security assessment, reproducible stale-authority, descriptor, replay and crash-injection controls | Publish security counterexamples and explicitly withhold unsuitable deployment claims |
| Useful real work | Measured positive workflow completion; valid denied attempts and detected weakened controls; latency/throughput/compute/operational burden versus each deployment's native baseline | No-only-denials success; report actual denominator and unknown routes |
| UK industry benefit | Target 2 UK-hosted permissioned evaluations, ideally 1 controlled real operational workflow; documented adoption friction, effectiveness, UK collaborator work, open-source improvements | If partners unavailable, publish openly reproducible UK-relevant testbeds and record attempted engagement, **not** a fabricated industry trial |
| Open and sustainable research | Permissive public releases, limitations, threat-model diagrams, educational examples, accessible documentation, transfer and maintenance plan | No false certification or promise of broad market adoption |

A more ambitious external pilot is a **research target conditional on independent authorization**, not a preexisting collaborator or guaranteed release milestone.

## Two concrete test domains

### A. Software supply chain / CI–CD agent workflows (primary)
An agent works on an actual software project: read a scoped repository, propose/change code, run tests in disposable contexts, and submit a reviewable artifact. Deployment privileges, protected branch updates, signing keys, and production credentials remain **outside** its ambient authority. Evaluate temporary grants, permission attenuation and revocation during queued work, stale runners, inherited descriptors, ambiguous acknowledgments and restart; allow legitimate test and PR activity to complete. A later low-risk UK pilot could involve a noncritical UK operator's **staging pipeline**, with production changes behind existing human approvals.

Candidate integrations should use existing GitHub/GitLab/CI APIs and their native permission mechanisms; compare with native scopes, OIDC credentials, container sandboxing and existing secret storage rather than assuming a new agent-specific API is superior.

### B. Managed API / data-processing workflow (second domain)
Two principals delegate a bounded task involving a data or cloud-service API, with independent authority constraints and a request/effect audit record. Test restricted reads, approved writes to *disposable* staging objects, replacement, rollback of proposed state, stale access after revocation, lost replies, and source/recipient disagreement. Reconcile one selected external-effect policy with authoritative records; explicitly refuse exactly-once guarantees where the sink contract cannot support them. Protect real customer data and credentials by default; use synthetic/consented data and least-privilege test tenants.

A UK cloud/managed-service, software infrastructure or security-assurance operator is a logical target category, **not an identified partner**.

### Conditional C. Cyber-physical interface
ARIA identifies bounded access to sensors/actuators as an interesting open gap. A digital twin or simulated sensor/actuator adapter could assess how authority-to-effect enforcement would bind to a physical operator. Do not promise a real industrial actuator or safety-critical test this year unless a qualified partner, isolation/safety case and dedicated gate justify it. This optional bridge should not consume the primary Track 2.2 milestones.

## Backward dependencies and proposed schedule

**Months 11–12 — independent replay and transfer.** Outside security reviewers reproduce the chosen integration's attacks and positive tasks; operator receives rollback procedure, evidence manifest, supported threat/failure contract and a report containing defects and corrections. Public release updated with reproducible UK operational example and benchmark. No guarantee of independent formal certification.

**Months 9–10 — second independent industrial evaluation and first low-risk real workflow (target).** A distinct UK operator or team attempts the same API/runner integration using published instructions; compare integration hours, security coverage, overhead, recovery results and defect findings. A reviewed, reversible/approval-gated real workflow may be run only after the security and authorization gates below. Failure to recruit a second partner does not become a fictitious achievement.

**Months 7–8 — first UK partner staged pilot.** Run one approved end-to-end agent task in an isolated test tenant or staging workflow. Exercise revocation/loss tests, intentionally weakened control, replay/stale-holder and recovery faults, with partner security contact present. Observe effects with independent evidence collection, not solely component-produced PASS labels. Refine integration and report unsupported assumptions.

**Months 4–6 — productization for live integration.** Stable minimal versioned adapter and output schema; initial two integrations against publicly reproducible CI and data/API testbeds; independently reproduced adversarial suite; no unbounded security claims. Engage UK operators and specialist reviewers, with written scope and named points of contact before any partner infrastructure access. Measure baseline native security controls for comparison.

**Months 2–3 — core assurance and first usable release.** Complete selected F1–F4 host-to-model tests needed by the chosen attachment profiles and early external review; retain negative controls and TCB inventory; establish minimal integration recipe. Prototype can be useful earlier; do not inflate a bounded prototype to a three-month deliverable.

**Award first 4 weeks — reproduce and assess readiness.** Recheck pinned pre-award claims, complete or narrow the first lifecycle/accepted-content recovery experiment, select the smallest effect profile suitable for independent integration, and establish partner security/assurance contact channels. Do not charge pre-award work as a new grant deliverable.

### Before any real environment test: seven gates
1. **Written authorization, owner and scope:** operator consent, explicit tenant/workflows/dates, permissible tests, point of contact and incident protocol.
2. **Threat and route inventory:** identify APIs, credentials, FDs, IPC, host privilege, descendants, data, external effects and all out-of-scope routes; deny unsupported operations.
3. **Independent staging confirmation:** fresh isolated environment, synthetic/consented data, no production secrets or uncontrolled outbound effects.
4. **Native safety controls retained:** least privilege, limited API scopes, external approval for consequential actions, rate/resource limits, logging and rollback/disposal.
5. **No unsafe uncontrolled mutation:** hostile tests on test tenants/simulators; no intentional failure injection against public production service or critical infrastructure.
6. **External review and test results:** independent assessor signs off the *selected* risk profile for a planned pilot, not universal security.
7. **Rollback and stopping:** fail-closed disablement, abort signal and audit capture tested. Production-adjacent access permitted only when operator explicitly approves it; otherwise remain shadow/staging.

## Measurable comparison criteria
- Correct **authorized task completion** and an explicit denial-control denominator, not merely zero prohibited actions.
- Post-revocation and loss bypass attempts against every enabled in-scope route, plus mutations ensuring the evaluator detects a weakened enforcer.
- Recoverable accepted bytes and acknowledgement/effect correctness for **declared** failure classes; process death is not power-loss durability.
- Per-operation overhead: p50/p95 latency, CPU/memory, tool/model cost; baseline against native OS/cloud/CI access controls with comparable task scope.
- Operational impact: engineer time to integrate, number of manual policy changes, onboarding failure rate, reproducibility on clean hosts, maintainers' recorded defects.
- UK contribution: documented UK research/assurance work performed, tangible integration experience, reusable training/docs, public test evidence relevant to UK software and managed-service sectors.

Set explicit pass/fail performance thresholds **after** baseline measurement and real partner workload selection; any numerical success target without denominator/baseline would be invented.

## UK benefit, recruitment and spending — rationale, not invented partnerships
UK government cyber sectoral analysis (May 2026) reports increased focus on AI security, agent identity/access, runtime infrastructure and AI red teaming; NCSC guidance prioritizes lifecycle protection, access control, verifiable audit trails and secure deployment. We can deliver reusable defensive infrastructure, tests and training to this ecosystem. The later-year pilot direction also matches ARIA's October portfolio map, which leaves the digital open-source/use-case partner area open and asks for early demonstrations and enforceable bounded access.

Seek paid UK-based expertise in security audit and the integration domains, and a real UK operational test environment. Use ARIA's own teaming/community channels and normal UK industry outreach to find interested operators. **No UK institution or company has yet committed.** Contractor/day rates, access fees, live test costs, eligibility, data/IP agreements and actual PI commitment must be confirmed before budgeting.

Sources:
- ASES Phase I roadmap and verification, \`codex/execution-engine-roadmap:docs/architecture/EDASES-Execution-Engine-Roadmap.md\` and \`docs/architecture/core-substrate/Phase-I-Verification.md\`.
- F3 selected host evidence, https://github.com/rock-solid-sites/ASES/blob/04600b1b45e6510665bdc3108db9d51f6b2f8c56/research/phase-i-protected-work-unit-f3/authority-loss/REPORT.md
- ARIA portfolio priorities and gaps (Oct 7, 2026), https://scalingtrust.org.uk/blog/building-the-scaling-trust-portfolio/
- UK Government, Cyber security sectoral analysis 2026, https://www.gov.uk/government/publications/cyber-security-sectoral-analysis-2026/cyber-security-sectoral-analysis-2026
- UK NCSC, secure AI development guidelines, https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development
- UK/NCSC co-authored agentic AI adoption guidance (May 2026), https://www.ncsc.govt.nz/protect-your-organisation/careful-adoption-of-agentic-ai-services/
