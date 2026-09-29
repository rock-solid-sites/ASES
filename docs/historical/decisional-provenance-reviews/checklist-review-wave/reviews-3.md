reviews-3

Gemini 3.5 Flash
Here is an adversarial review of your three checklists. Overall, these are exceptionally well-structured, pragmatically grounded (e.g., the "cannot determine" rule is excellent), and highly up-to-date for **2026** security paradigms (referencing the Jan 2026 OWASP update and late-2025 Agentic standards).

However, looking at them through an attacker's lens, there are critical gaps, logical blind spots, and architectural overlaps that could let vulnerabilities slip through the cracks.

---

## 1. Individual Checklist Evaluations

### Checklist 1: Project Safety & Code Quality Review

* **The Good:** The ground rules are phenomenal. Forcing auditors to prove execution path rather than relying on absence of evidence prevents "drive-by" greenlighting.
* **The Blindspots:**
* **Linter vs. SAST:** Static checking focuses heavily on quality (linters, type-checkers). Standard linters (like ESLint or Ruff) miss complex semantic security flaws. You need explicit AST-based security scanners (e.g., Semgrep, Bandit, Sobelow) defined here, not just "linters."
* **Policy-as-Code Ignored:** Section C assumes branch protection, IAM, and environment configurations are purely platform-level (unverifiable). However, modern setups check these in as IaC (Terraform, GitHub Actions `.github/workflows/`, Kubernetes manifests, OPA policies). If policy-as-code exists in the repo, pushing it to Section C means it won't get audited.
* **Dependency Confusion Edge Case:** You check for `@myorg/` scoping, but miss checking if the actual registry configuration file (e.g., `.npmrc`, `pip.conf`) is checked in and securely overrides the public registry for those scopes.



### Checklist 2: Application Security Audit Checklist

* **The Good:** Grounded in OWASP 2025/2026, with great specificity on dangerous patterns (e.g., non-constant-time secret comparison, `yaml.load` safe loaders).
* **The Blindspots:**
* **Race Conditions Misplaced:** You categorized Race Conditions under *Section D: Web & Client-Facing Vectors*. While client actions trigger them, race conditions are strictly backend concurrency issues (database transaction isolation levels, redis locks, state machine design). Placing them here might lead a client-focused reviewer to overlook deep database/worker thread pooling flaws.
* **The "Zero-Day" Exclusion Loophole:** Your out-of-scope rules exclude "pentest/fuzzing-only findings... 0-days". This is dangerous. If a reviewer spots a custom protocol parser or home-rolled parser logic, it shouldn't be ignored just because a public CVE doesn't exist yet.
* **API Rate-Limiting & DoS Gaps:** "Fail-open exceptions" touches on rate-limiting, but there is no explicit check for API rate-limiting configuration, query depth limits (GraphQL), or massive payload size limits.



### Checklist 3: LLM & Agentic Application Security Checklist

* **The Good:** Excellent adaptation of OWASP LLM and the Agentic Top 10. The human-agent trust exploitation (rubber-stamping) and cascading failure checks are highly mature.
* **The Blindspots:**
* **Multimodal Injection Ignored:** The prompt injection checks focus on "untrusted content... concatenated into instruction context." In 2026, most agentic systems process multimodal inputs (images, PDF documents with OCR, audio). Injecting adversarial instructions into images (visual prompt injection) is a massive vector missed here.
* **Tool Sandboxing vs. Runner Sandboxing:** Section D checks "Unexpected code execution (ASI05)" via sandboxes. But the sandbox configuration itself is often infra-level (managed in Checklist 1). There is a high risk of "not my job" exclusion here.
* **Vector DB Authorization:** Section C checks "Access control on index writes" but completely misses *read-time* access control (e.g., making sure a RAG pipeline doesn't retrieve document chunks the user isn't authorized to see).



---

## 2. Are They Properly Separated? (The Intersections)

While the three-document split makes logical sense on paper, **they are not properly separated in practice.** There are major areas of friction, overlap, and potential gaps where a reviewer will waste time or miss vulnerabilities.

### The Overlap & Gap Matrix

| Security Vector | Checklist 1 (Project Safety) | Checklist 2 (Classic AppSec) | Checklist 3 (LLM/Agentic) | Verdict & Danger |
| --- | --- | --- | --- | --- |
| **Sandboxing & Code Exec** | Section A (Docker, seccomp, IAM limits) | *None* | Section D (Agent writes/executes code in sandbox) | **Friction.** The LLM auditor checks *if* code execution is sandboxed, while the Infra auditor checks *how* the sandbox is configured. If they don't sync, you get an unconfigured, unsafe sandbox. |
| **Dependency Supply Chain** | Section B (Lockfiles, pinning, package scopes) | *None* | Section D (MCP servers, third-party plugins pinned/vetted) | **Overlap.** If an agent uses a Python tool that relies on a pip package, which checklist handles it? Standard packages vs. Agent "tools/plugins" share identical attack vectors (e.g., dependency confusion). |
| **SSRF & Outbound Connections** | Section A (Arbitrary URL fetch) | Section A (SSRF URL host/scheme allowlist) | Section B (Tool misuse - agent fetching URLs) | **Confused Boundaries.** SSRF is handled in all three under different names. An attacker targeting an agent's web-browsing tool bypasses traditional AppSec checks because "the LLM handles the tool execution logic." |
| **Secrets & Keys** | Section A (Hardcoded secrets, leaks in logging) | Section C (Custom crypto, HSM/KMS) | Section A & B (Secrets in system prompts, static tool credentials) | **Gaps.** Secrets in system prompts (Checklist 3) can be leaked via classic AppSec avenues (Checklist 2 error handlers returning debug logs) or CI/CD pipelines (Checklist 1 printing environment variables). |

---

## 3. Recommended Fixes for Clearer Separation

To ensure zero overlap and no blind spots, adjust the boundaries of your checklists using these rules:

1. **Rule of Execution vs. Infrastructure (Checklist 1 vs 3):**
* *Checklist 3* should only evaluate **what** the agent is allowed to trigger (e.g., "Is code execution dynamically generated by the LLM?").
* *Checklist 1* must handle the **technical implementation** of the sandbox (e.g., "Does the Python-runner container have `no-new-privileges` and a read-only root FS?").


2. **Consolidate Supply Chain (Checklist 1 vs 3):**
* Move all package/dependency auditing (including MCP servers, semantic plugins, and agent packages) to **Checklist 1 Section A/B**. Let the pipeline/dependency audit handle *all* static code definitions, regardless of whether a human or an agent uses the package.


3. **Redefine the "API / Tool" Boundary (Checklist 2 vs 3):**
* Ensure that **Checklist 2** treats the LLM's "Tools" exactly like any other public API endpoint. If an LLM tool executes a SQL query, it must pass Checklist 2's injection checks. **Checklist 3** should strictly focus on *how the LLM is guided into choosing and executing that tool* (goal hijacking, parameter manipulation via prompt).

ChatGPT 5.5
The three checklists are largely well-separated, but there are a few places where scope boundaries leak. Overall I'd rate the separation:

* **Project Safety & Code Quality:** 9.5/10
* **Application Security:** 9/10
* **LLM & Agentic Security:** 9/10
* **Cross-checklist separation:** 8.5/10

The biggest strength is that each checklist explicitly defines its scope and repeatedly redirects readers to the appropriate companion document. That alone prevents a large amount of duplication.

The main overlaps are below.

| Topic                                               | Current location  | Better location                                                                           |
| --------------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------- |
| `shell=True`, unrestricted FS, eval, dynamic import | Project Safety    | AppSec if reachable from untrusted input; Project Safety only for engineering-risk review |
| SSRF mention                                        | AppSec only       | Correct                                                                                   |
| Supply chain                                        | Project + LLM     | Keep Project for packages/build pipeline, LLM only for models/tools/MCP/plugins           |
| Logging secrets                                     | Project + LLM     | Project: application logging. LLM: prompt/context logging specifically                    |
| Sandbox                                             | Project + LLM     | Project: infrastructure sandbox. LLM: agent execution sandbox                             |
| Human approval                                      | LLM only          | Correct                                                                                   |
| Branch protection                                   | Project Section C | Correct                                                                                   |

The biggest issue is Section A of the Project checklist.

Items like

* `shell=True`
* `eval`
* unrestricted filesystem access
* arbitrary URL fetch

are not inherently engineering or pipeline issues. They become security findings only when attacker-controlled data reaches them.

For example:

```python
subprocess.run(["git","status"])
```

is not an AppSec finding.

```python
subprocess.run(user_cmd, shell=True)
```

is.

Your Project checklist currently says

> Dangerous/obfuscated ops: privileged syscalls, shell=True, arbitrary URL fetch from user input...

The phrase

> arbitrary URL fetch from user input

already makes this partly an application-security review.

I'd instead make Project ask

> Are dangerous primitives present? Record locations for later review.

and have AppSec determine exploitability.

---

The second overlap is secret handling.

Project says

> hardcoded secrets
> logging config
> telemetry

LLM says

> full config passed into prompt
> model request/response logging

Those are different problems, but the distinction should be sharper.

Project:

* repository secrets
* deployment secrets
* env vars
* credential exposure

LLM:

* prompt context
* retrieval context
* model transcripts
* prompt leakage

That avoids reviewers checking the same logging code twice.

---

Supply chain is separated surprisingly well.

Project covers

* npm/pip
* lockfiles
* dependency confusion
* Git dependencies
* postinstall scripts

LLM covers

* model provenance
* MCP servers
* tool plugins
* runtime model downloads

Those are genuinely different attack surfaces.

I would only rename

> Supply chain (LLM03/ASI04)

to

> Model and agent supply chain

to make that distinction immediately obvious.

---

The Project checklist's Section C is excellent.

Moving items like

* branch protection
* credential rotation
* change review
* observability

into "Needs external verification" removes one of the biggest hallucination sources in repository audits.

I'd consider doing the same in the LLM checklist for provider-specific claims:

* provider alignment
* model training provenance
* hosted-model isolation

Those are rarely repo-verifiable.

---

The AppSec checklist is also well scoped.

Keeping

* business logic
* fuzzing-only findings
* organization logging
* dependency provenance

explicitly out of scope prevents it from turning into an OWASP "everything" checklist.

The new stopping criterion

> every OWASP Top 10:2025 category covered/excluded-with-reason

is particularly strong because it makes omission measurable.

---

The LLM checklist is the cleanest of the three.

It avoids re-explaining SQL injection, XSS, authorization, etc., and instead focuses on genuinely agentic concerns:

* prompt injection
* goal hijacking
* tool validation
* memory poisoning
* excessive agency
* denial-of-wallet
* cascading failures

Those are exactly the places classical AppSec reviews tend to miss.

---

The one structural improvement I'd make is to formalize ownership of every topic. A short matrix like this at the beginning of the suite would remove virtually all ambiguity.

| Topic                 | Owner   |
| --------------------- | ------- |
| CI/CD                 | Project |
| Dependency provenance | Project |
| Secrets in repo       | Project |
| Injection             | AppSec  |
| Access control        | AppSec  |
| Sessions              | AppSec  |
| Crypto                | AppSec  |
| Prompt injection      | LLM     |
| Tool execution        | LLM     |
| Memory poisoning      | LLM     |
| Agent identity        | LLM     |
| Model provenance      | LLM     |

That lets reviewers immediately know which checklist should produce the finding.

Overall, the documents are thoughtfully partitioned. The remaining overlap is mostly around dangerous primitives (`shell=True`, filesystem access, URL fetching, `eval`) and secret handling. Tightening those ownership boundaries would make the three checklists feel almost orthogonal, with very little duplicated review effort. Жあל

GLM-5.2
This is an adversarial review of the three checklists. I will first evaluate each checklist on its own merits, identifying structural blind spots and logical flaws, and then evaluate the boundaries between them to see where issues might fall through the cracks or cause redundant confusion.

---

### Part 1: Individual Checklist Adversarial Review

#### 1. Project Safety & Code Quality Review Checklist
**Critique:** The title is a misnomer, and it struggles to justify its own existence separate from a standard AppSec checklist.
*   **Title vs. Content Disconnect:** The title says "Code Quality Review," but the content explicitly excludes app logic. "Code Quality" universally implies logic, complexity, and maintainability. By reducing "code quality" to linting/type-checking, it conflates *engineering hygiene* with *pipeline security*. It should be renamed "Pipeline & Repository Trust Checklist."
*   **Dangerous Ops Overlap:** Section A3 (Dangerous/obfuscated ops: `shell=True`, `eval`, arbitrary URL fetch) overlaps heavily with the AppSec checklist (Injection/SSRF). If an auditor finds `shell=True` in a Python script, do they log it here or in the AppSec checklist? The scoping note says "Not app logic," but `eval` and `shell=True` *are* app logic if used in the runtime application.
*   **"Configured, unverified" Loophole:** The rule `"Runs clean" only valid if execution observed` is excellent, but Section B1 asks `workflow exists? Triggers on PR?`. This is self-defeating; an auditor can easily verify a workflow triggers on a PR by reading the YAML, but this rule implies they cannot pass it without observing a PR execution. 
*   **Out-of-Scope Bloat:** Section C includes things like "Bus factor / on-call structure" and "Change review board." These are organizational compliance items, not project safety items. Including them dilutes the focus of a repository-level audit.

#### 2. Application Security Audit Checklist
**Critique:** It relies too heavily on a rigid standard and explicitly coppers out of the hardest parts of application security.
*   **The OWASP "Stopping Criterion" Fallacy:** The stopping criterion is `complete when every OWASP Top 10:2025 category is covered`. The OWASP Top 10 is an *awareness* document, not an audit standard. Using it as a stopping criterion guarantees baseline coverage but explicitly ignores vulnerabilities outside the top 10 (e.g., specific API security flaws from OWASP API Top 10, race conditions outside of check-then-act, or complex business logic).
*   **Business Logic Cop-out:** The scope explicitly excludes `business-logic abuse (~Insecure Design, needs threat model)`. This is a massive blind spot. While requiring a full threat model is out of scope, basic business logic checks (e.g., negative quantities in shopping carts, skipping payment steps) are standard AppSec audit fare. Excluding them entirely makes this checklist woefully inadequate for modern web apps.
*   **Timing/State Limitations:** Section D6 mentions `check-then-act on shared state... exploitable window`. Identifying this via static code review without a dynamic pentest is nearly impossible unless the codebase lacks transactions entirely. The checklist doesn't provide guidance on how to evaluate this statically without falling back to "Cannot determine."
*   **Missing API Surface Focus:** The checklist feels dated toward monolithic web apps. It mentions CORS and CSRF but misses modern API-specific issues like BOLA (Broken Object Level Authorization—though IDOR is covered) and excessive data exposure (returning full DB objects to the client and expecting the frontend to filter).

#### 3. LLM & Agentic Application Security Checklist
**Critique:** The most modern checklist, but it suffers from boundary confusion between what is a model problem versus what is a code problem.
*   **Output Handling Redundancy:** A3 (Improper output handling: model output → shell/SQL/eval) is a direct duplicate of AppSec Section A. If a developer writes `db.query("SELECT * FROM users WHERE name = " + llm_output)`, both checklists flag it. The LLM checklist should *only* check if the LLM output is treated as trusted input, and defer the actual sink evaluation to the AppSec checklist.
*   **Tool Misuse vs. Access Control:** B3 (Tool misuse: tool calls validated server-side) and B4 (Identity/privilege abuse) heavily overlap with AppSec Section B (Authorization). If an LLM agent invokes a tool `delete_user(user_id)`, does the auditor check the tool's authz in AppSec or the agent's invocation validation here? 
*   **Agentic Top 10 Timeliness:** Relying on "Agentic Top 10 (published Dec 9, 2025)" is inherently fragile. The agentic space is changing so rapidly that hardcoding a future standard is risky. Furthermore, concepts like ASI01 (Goal Hijack) and ASI06 (Memory Poisoning) are extremely difficult to verify via static code review; they often require runtime evaluation. The checklist acknowledges this in Section E, but Sections B and C set auditors up for failure by asking them to find these issues in code.

---

### Part 2: Evaluation of Separation & Boundaries

The checklists attempt a strict tripartite separation: **Pipeline/Repo** vs. **Classic App Code** vs. **LLM/Agent Code**. While the intent is good, the boundaries are leaky, leading to coverage gaps and audit collisions.

#### 1. The "Dangerous Sink" Collision (AppSec vs. Project Safety vs. LLM)
*   **The Issue:** If an application contains an `eval()` block or `shell=True`, it is flagged in:
    *   Project Safety A3 (Dangerous/obfuscated ops)
    *   AppSec A1 (Injection/command injection)
    *   LLM A3 (Improper output handling, if LLM feeds it)
*   **The Fix:** Project Safety A3 should be strictly limited to *build scripts, CI steps, and local developer tooling*. It must explicitly state: "Applies only to scripts executed during CI/CD or local dev setup. Runtime application code → AppSec Checklist."

#### 2. The Authorization/Tool-Calling Boundary (AppSec vs. LLM)
*   **The Issue:** Modern LLM apps use tools that are just API endpoints. If an agent calls an internal API, the LLM checklist checks the *wiring* (is the agent allowed to call it?), but AppSec checks the *endpoint* (is the endpoint secure?). 
*   **The Fix:** The LLM checklist must explicitly defer endpoint security to AppSec. LLM B3 should read: "Tool invocation validated pre-execution? *Note: The security of the tool endpoint itself → AppSec Checklist.*"

#### 3. The Infrastructure as Code (IaC) Gap
*   **The Issue:** None of the checklists explicitly own Infrastructure as Code (Terraform, CloudFormation, Pulumi). 
    *   Project Safety mentions Dockerfile/seccomp/IAM manifest, but only in the context of sandboxing the app.
    *   AppSec mentions security misconfig (debug flags, headers), but only in app config.
*   **The Gap:** If a Terraform script provisions an S3 bucket with `acl = "public-read"` or opens Security Group 0.0.0.0/0 to the world, neither checklist cleanly captures this. Project Safety should expand Section B to explicitly include "IaC static analysis (tfsec/checkov) configured and passing?"

#### 4. Supply Chain Demarcation
*   **The Issue:** Project Safety A6 covers generic supply chain (npm lockfiles, dependency confusion). LLM D1 covers model supply chain (pinned models, MCP servers). 
*   **The Boundary:** This separation is actually quite good, but needs a rule: "If the dependency is a library/package → Project Safety. If the dependency is a model, embedding, or prompt template → LLM Checklist."

### Summary Verdict

The checklists are highly rigorous and employ excellent anti-hallucination ground rules (requiring exact quotes, observed execution, and strict confidence levels). However, they suffer from **scope bleed**. 

To be properly separated, the introductions need sharper demarcation rules based on **artifact type**:
1.  **Project Safety:** Applies *only* to `.github/`, `Dockerfile`, `Makefile`, CI scripts, and dependency manifests.
2.  **AppSec:** Applies *only* to runtime application code (APIs, controllers, views, data models).
3.  **LLM:** Applies *only* to prompt construction, agent orchestration, and model I/O handling.

Until those artifact-based boundaries are explicitly stated, auditors will waste time debating which checklist an `eval()` in a Python script belongs to. Furthermore, the AppSec checklist's exclusion of business logic and reliance on the OWASP Top 10 as a ceiling (rather than a floor) is a critical weakness that must be addressed.

Kimi K2.6
Here is an adversarial review of the three checklists, evaluating each internally and then assessing their separation, overlaps, and gaps.

---

## 1. Executive Summary

The three checklists are **well-scoped at a high level** but suffer from **internal mapping errors, fuzzy boundary definitions, and unstated gaps** that create both false confidence and coverage holes. The most critical issues are:

- **Appsec checklist**: Contains **factually incorrect OWASP Top 10:2025 mappings** that will mislead auditors and likely cause categories to be missed or double-counted.
- **LLM checklist**: **ASI07 (Insecure Inter-Agent Communication)** is entirely absent from the code-reviewable sections without explicit exclusion, violating its own stopping criterion.
- **Cross-cutting**: **Supply chain** and **dangerous code execution** are checked in multiple checklists with no clear rule for which takes precedence, creating duplication or omission risk.
- **Meta-issue**: The **stopping criteria** are treated as guarantees of completeness, but the checklists exclude several OWASP categories without explicitly listing those exclusions in their section headers.

---

## 2. Checklist 1: Project Safety & Code Quality Review

### Strengths
- The **"assume deception in comments/docs"** ground rule is excellent and directly counters a common audit failure mode.
- Distinguishing **"configured, unverified"** from **"runs clean"** is operationally precise.
- Section C correctly pushes org-level platform settings (branch protection, credential rotation) out of repo-scope.

### Weaknesses

**Scope bleed into application logic**
> *"Dangerous/obfuscated ops: ... arbitrary URL fetch from user input, unrestricted FS access, string-built eval..."*

These are **application-layer sinks**, not pipeline/infrastructure concerns. The checklist explicitly says *"Not app logic — see appsec-audit-checklist.md"*, yet this item directly duplicates Appsec Section A (Injection). An auditor using this checklist will flag `eval(user_input)` here, while another auditor using the Appsec checklist will flag the same line. There is no tie-breaker rule.

**Evidence requirements are inconsistently demanding**
> *"Secrets: hardcoded/committed/in git history/test fixtures/example configs/client bundle/Docker layer?"*

Checking *"in git history"* requires access to the full commit graph, not just the current snapshot. The ground rules demand *"file/line + quoted code"*, but a secret in git history may have been deleted in the current HEAD. The checklist does not specify whether the audit scope includes `git log --all --full-history` or just the current working tree. This creates a reproducibility gap: two auditors with different git clone depths will produce different verdicts.

**"Exceeds observable functionality" is subjective**
> *"Sandbox/isolation: Dockerfile/seccomp/IAM manifest requests exceed observable functionality?"*

This is a good heuristic but is not operationalizable. "Observable functionality" depends on runtime behavior analysis, which the checklist elsewhere treats as unverifiable from repo contents (Section C). If the Dockerfile requests `CAP_SYS_ADMIN` but the app is a static file server, an auditor can flag it, but if it requests `CAP_NET_BIND_SERVICE`, is that "exceeds"? The checklist provides no severity calibration for capability grants.

**Missing: traditional dependency vulnerability scanning**
The checklist checks for lockfile presence and hash verification, but does not explicitly ask whether **known-vulnerable dependencies** are present (e.g., via `npm audit`, `safety check`, OSV). This is distinct from supply-chain poisoning (A03) and is a notable omission for a "code quality" review.

---

## 3. Checklist 2: Application Security Audit

### Strengths
- The **source-to-sink** framing (untrusted source → sink) is correct for injection and access-control analysis.
- Explicitly excluding business-logic abuse and pentest-only findings is a valid scope constraint.
- The output format requirements (file/line, quoted code, confidence) are rigorous and reduce hallucination risk.

### Critical Weaknesses

**OWASP Top 10:2025 mapping is factually wrong and inconsistent**

The official OWASP Top 10:2025 (released Jan 2026, data from 2025) is:
- **A01**: Broken Access Control (SSRF folded in)
- **A02**: Security Misconfiguration
- **A03**: Software Supply Chain Failures
- **A04**: Cryptographic Failures
- **A05**: Injection
- **A06**: Insecure Design
- **A07**: Authentication Failures
- **A08**: Software or Data Integrity Failures
- **A09**: Security Logging & Alerting Failures
- **A10**: Mishandling of Exceptional Conditions

The checklist's mappings:

| Checklist Section | Claims | Actual OWASP 2025 | Verdict |
|---|---|---|---|
| Section A — Injection | (A05, A01/SSRF) | A05 is Injection ✓, but A01 is Broken Access Control, not Injection | **Partially wrong** — SSRF is in A01, but A01 is not an injection category |
| Section B — Authorization | (A01) | A01 is Broken Access Control ✓ | Correct, but SSRF is also A01 and lives in Section A |
| Section C — Cryptography | (A04) | A04 is Cryptographic Failures ✓ | Correct |
| Section D — Web & client | (A01, A02) | A01 is Broken Access Control, A02 is Security Misconfiguration | **Wrong** — XSS is A05 (Injection), CSRF is A01, CORS/misconfig is A02. Section D mixes A01, A02, A05, and A10 without acknowledging it |

This is not a minor labeling issue. Because the **stopping criterion** is *"complete when every OWASP Top 10:2025 category is covered/excluded-with-reason"*, an auditor relying on these section headers will believe they have covered A01 in Section B and A02 in Section D, while missing that **A01 is split across three sections** (A, B, D) and **A05 is also split across A and D**. This makes completeness verification impossible.

**Missing explicit exclusions violate the stopping criterion**
The following OWASP 2025 categories are **not covered** in the sections and **not explicitly excluded with reason**:
- **A03 Software Supply Chain Failures**: Excluded by scope reference to companion doc, but not stated in the Appsec checklist sections.
- **A06 Insecure Design**: Mentioned in scope as "business-logic abuse (~Insecure Design, needs threat model)", but not explicitly mapped as excluded.
- **A07 Authentication Failures**: Only "session mgmt" is covered. Password policy, MFA, brute-force protection, credential stuffing are absent.
- **A08 Software or Data Integrity Failures**: Race conditions are covered, but this is only one CWE under A08. deserialization integrity, serialization tampering, and CI/CD integrity are missing.
- **A09 Security Logging & Alerting Failures**: Explicitly pushed to "org-level → companion Section C", but again, not listed as an excluded category in the Appsec sections.
- **A10 Mishandling of Exceptional Conditions**: Only "fail-open exceptions" is covered. Resource leaks, crash handling, null pointer dereferences, and other A10 CWEs are absent.

**Section A scope confusion**
> *"Section A — Injection & unsafe input (A05, A01/SSRF)"*

If SSRF is folded into A01 (Broken Access Control), it belongs in **Section B**, not Section A. By placing SSRF in Section A, the checklist creates a contradiction: it claims to follow OWASP categories but then splits a single category across sections based on attack vector similarity rather than OWASP taxonomy. This undermines the stopping criterion.

**Overly narrow injection coverage**
> *"Flag pattern (f"...{user_id}") even w/o demonstrated exploit."*

This is good, but the checklist does not explicitly cover **NoSQL injection**, **ORM injection**, **LDAP injection**, or **XPath injection**. These are common in modern applications and are part of A05.

**Authentication is under-covered**
Section B covers session management and AuthZ checks, but **A07 Authentication Failures** includes weak password policies, lack of MFA, brute-force protection, and credential stuffing. None of these are code-reviewable in a meaningful way from static analysis alone, but the checklist should explicitly exclude them with reason to satisfy the stopping criterion.

---

## 4. Checklist 3: LLM & Agentic Application Security

### Strengths
- Correctly identifies that this is the **fastest-moving** of the three docs and advises checking genai.owasp.org for updates.
- The distinction between **direct** and **indirect** prompt injection is operationally useful.
- Treating model output as untrusted input (LLM05) is a critical and often missed control.

### Weaknesses

**ASI07 is entirely missing without exclusion**
> *"Stopping criterion: complete when every LLM01–10 (2025) and ASI01–10 (2026) category is covered/excluded-with-reason."*

The OWASP Agentic Top 10 2026 includes:
- **ASI07: Insecure Inter-Agent Communication**

This category is **not mentioned anywhere** in the checklist sections. If the project is a single-agent system, this should be explicitly excluded with reason (e.g., "ASI07: No inter-agent communication observed in architecture — excluded"). The current checklist leaves ASI07 unaddressed, violating its own stopping criterion.

**ASI10 is under-covered and misplaced**
> *"Runtime behavioral monitoring for goal drift/anomalous tool-calls (ASI01, ASI10)"*

ASI10 is **Rogue Agents** — agents that deviate from their intended scope or act harmfully. The checklist only mentions this under **Section E (Not verifiable from repo)**. However, **code-reviewable aspects** of ASI10 exist: kill switches, scope enforcement boundaries, hardcoded agent goal constraints, and sandboxing of agent actions. By placing ASI10 entirely in "Not verifiable," the checklist misses static-analysis opportunities and does not explicitly exclude the code-reviewable aspects with reason.

**Boundary overlap with Appsec on injection sinks**
> *"Improper output handling (LLM05): model output → dangerous sink (shell/SQL/eval/template/deserializer) w/o the same validation as untrusted user input?"*

The checklist states: *"classic injection/authz once the model layer is set aside (→ appsec-audit-checklist.md Section A, not duplicated here)."* Yet LLM05 **does** duplicate the sink analysis. If a codebase uses `eval(model_output)`, both checklists will flag it. The LLM checklist should either:
1. Explicitly state that LLM05 only checks whether model output **reaches** the sink, while Appsec checks whether the sink itself is properly parameterized, OR
2. Remove the claim of non-duplication.

Currently, the boundary is **fuzzy** and will cause double-counting or, worse, one auditor assuming the other covered it.

**Boundary overlap with Project Safety on supply chain**
> *"Supply chain (LLM03/ASI04): model loaded from a pinned, integrity-verified source vs. arbitrary runtime pull? Third-party tools/plugins/MCP servers pinned+vetted..."*

If an MCP server is distributed via npm and loaded as a dependency, **both** Project Safety (supply chain section) and LLM checklist (Section D) apply. The checklists do not specify precedence. If Project Safety passes the npm package (lockfile present, SHA verified) but the LLM checklist fails it (MCP server not vetted for agent-specific risks), which verdict governs? This is undefined.

**ASI05 overlap with Project Safety dangerous ops**
> *"Unexpected code execution (ASI05): agent writes+executes code/installs deps/runs shell from its own output w/o sandbox/execution allowlist?"*

Project Safety checks for `shell=True`, `eval()`, and dynamic imports. If an agent uses these, both checklists flag them. The LLM checklist should clarify that ASI05 covers **agent-generated** code execution, while Project Safety covers **developer-written** code execution. Currently, both check for the same patterns without distinguishing the threat model.

**Missing: LLM-specific rate limiting vs. traditional DoS**
LLM10 covers unbounded token/cost consumption, but does not explicitly cover **model extraction attacks** (systematic querying to replicate model behavior) or **context flooding** (extremely long inputs to overflow context windows). These are part of LLM10:2025 per the official OWASP definition, but the checklist narrows it to "denial-of-wallet."

---

## 5. Cross-Cutting Evaluation: Separation, Overlaps, and Gaps

### Separation Assessment

| Boundary | Claimed Separation | Actual State | Risk |
|---|---|---|---|
| Project Safety ↔ Appsec | "Not app logic — see appsec-audit-checklist.md" | Project Safety includes `arbitrary URL fetch from user input`, `eval()`, and secret exfiltration via error handlers — all app logic | **Scope bleed** — duplication or omission |
| Appsec ↔ LLM | "classic injection/authz once the model layer is set aside → appsec" | LLM05 checks `model output → shell/SQL/eval` — same sinks as Appsec Section A | **Fuzzy boundary** — both may flag same line |
| Project Safety ↔ LLM | Project Safety covers "pipeline trust"; LLM covers "LLM/agent-specific" | Both check supply chain (npm lockfile vs. model source) and dangerous execution (shell=True vs. ASI05) | **Overlap without precedence rule** |

### Gaps Between Checklists

The following security domains fall into **none** of the three checklists:

| Gap | Why It Matters | Which Checklist Should Own It |
|---|---|---|
| **Cloud/Infrastructure Security** | S3 bucket permissions, IAM over-provisioning, network ACLs, VPC peering | Project Safety (as "observable infrastructure") |
| **API-specific security** | GraphQL query depth, introspection, API versioning, breaking changes | Appsec (as "Web & client-facing vectors") |
| **Data privacy / GDPR** | PII retention, right to deletion, data minimization, cross-border transfer | None currently — needs new section or Appsec extension |
| **Mobile client security** | Certificate pinning, root detection, secure storage | Appsec (Section D is web-only) |
| **Denial of Service (traditional)** | Request flooding, slowloris, connection exhaustion | Appsec (only race conditions are covered) |
| **Backup/restore security** | Backup encryption, access controls, restoration testing | Project Safety Section C mentions it but as unverifiable |
| **Business logic flaws** | Transaction reversibility, price manipulation, workflow bypass | Explicitly excluded from Appsec as "needs threat model" — but this is a major gap |

### The "Not Verifiable" Trap

All three checklists use **Section C/E** to push items out as "not verifiable from repo." This creates a **systemic blind spot**: the checklists are designed for static code review, but many high-severity controls (branch protection, credential rotation, runtime monitoring, backup testing) are only verifiable via platform APIs or runtime observation. The checklists do not provide an alternative verification method (e.g., "request screenshot from admin console" or "attach CI log URL"). This means **high-stakes items are consistently deferred to unverified trust**, which contradicts the ground rule: *"No inference from absence of red flags — check logs, fixtures, git history, not just current files."*

---

## 6. Recommendations

### Immediate Fixes

1. **Fix Appsec OWASP mappings**
   - Section A: Label as **(A05 Injection)** only. Remove A01/SSRF from this section.
   - Section B: Add SSRF explicitly under A01 Broken Access Control.
   - Section D: Correct label to **(A01, A02, A05, A10)** and add a note that it covers cross-category web vectors.
   - Add explicit exclusion statements for A03, A06, A07, A08, A09 in the section headers with reasons.

2. **Add ASI07 and ASI10 to LLM checklist**
   - ASI07: Add a section or explicit exclusion: *"ASI07 Insecure Inter-Agent Communication: Not applicable — single-agent architecture, no inter-agent messaging observed."*
   - ASI10: Move from Section E to a code-reviewable section (e.g., "Agent scope enforcement and kill switches") or explicitly exclude code-reviewable aspects with reason.

3. **Remove app-logic items from Project Safety**
   - Move `arbitrary URL fetch from user input`, `eval()`, and secret exfiltration via error handlers to Appsec. Project Safety should focus on **build-time and deployment-time** dangerous operations (e.g., `postinstall` scripts, CI pipeline `eval`).

4. **Define precedence rules for overlaps**
   - If both Project Safety and LLM flag the same `shell=True`, the rule should be: **Project Safety governs the presence of the capability; LLM/ASI governs whether the agent can autonomously trigger it.** Document this.

5. **Add "verifiable via" column to Section C/E**
   - For each "Not verifiable" item, specify what evidence would satisfy it (e.g., "Branch protection: verifiable via GitHub API `GET /repos/{owner}/{repo}/branches/{branch}/protection`").

### Structural Improvements

6. **Add a "Threat Model Exclusions" appendix**
   - Business logic flaws (A06 Insecure Design), traditional DoS, and mobile security are valid exclusions for a static checklist, but they should be **explicitly listed** so auditors know what is out of scope.

7. **Unify confidence definitions**
   - Project Safety defines High/Medium/Low confidence. Appsec uses the same. LLM caps High confidence for structural findings. This asymmetry is acceptable but should be explicitly justified.

8. **Add a "Cross-Reference Matrix"**
   - A table mapping each checklist item to the other two checklists would prevent duplication and ensure nothing falls through cracks.

---

## 7. Conclusion

The three checklists represent a **sophisticated and mostly well-scoped** security review framework. However, they currently suffer from **self-inflicted wounds**: incorrect OWASP mappings in the Appsec checklist, a missing ASI category in the LLM checklist, and undefined boundaries on supply chain and dangerous execution. These are fixable. The larger concern is the **systemic bias toward static repo analysis** that pushes runtime, platform, and organizational controls into a "not verifiable" graveyard without providing alternative verification paths. A checklist that cannot verify branch protection or credential rotation is not incomplete by design — but it must be honest about what it cannot see, and ensure that those blind spots are covered by other assurance activities.

Deepseek V4 Pro
I'll review these three checklists both individually and as a coordinated system.

## Individual Evaluations

### 1. Project Safety & Code Quality Review Checklist

**Strengths:**
- Excellent evidence standards (file/line + quoted code required, no paraphrasing allowed)
- Clear severity/confidence model with specific definitions
- Explicit anti-patterns flagged (deception in comments, "Pass" requiring execution evidence)
- Practical distinction between repo-verifiable and platform-dependent checks (Section C)
- Good supply chain depth (lockfile integrity, dependency confusion, postinstall scripts)

**Weaknesses:**
- Section A covers both static analysis config AND dangerous operations AND secrets AND supply chain AND sandboxing — creates a heterogeneous grab-bag where reviewers may lose focus
- "Cannot determine on high-stakes items → surface in summary" is good policy but Section C already exists; this creates two non-determination channels with different handling expectations
- No explicit stopping criterion (appsec checklist has OWASP Top 10 2025 completeness rule)
- "Assume deception" rule is stated but no methodology given for testing it (e.g., "check git blame for suspicious commits")

**Verdict:** Strong on evidentiary rigor, weak on structural organization. The ground rules are the best part.

---

### 2. Application Security Audit Checklist

**Strengths:**
- Explicit stopping criterion (complete OWASP Top 10 2025 coverage) — this is genuinely excellent and the other checklists should adopt this pattern
- Clean scope boundary with companions (explicitly defers pipeline/infra and LLM concerns)
- Strong specificity on dangerous patterns (f-strings in SQL templates, pickle.load with no SafeLoader, verify=False outside dev path)
- Batch authz, fail-open exceptions, race conditions — these are often-missed categories
- Recognizes 2025 edition differences (SSRF folded into A01, new A03/A10)

**Weaknesses:**
- Section E ("Not verifiable from repo") overlaps conceptually with companion doc's Section C but uses different naming. Not necessarily wrong but creates minor cognitive load switching between docs
- "Stopping criterion" references OWASP Top 10:2025 categories explicitly, but Section headers use category numbers (A05, A01) without mapping them to the named categories — reviewer must cross-reference
- Section D mixes web vectors (XSS, CSRF, CORS, cookies) with configuration (error handlers, debug flags, CSP/HSTS) — these are different threat surfaces
- "Pass w/ nearby override/exception → Pass (with exception)" is defined but companion doc uses identical language — no shared definitions doc exists

**Verdict:** Best-structured of the three, strongest scoping discipline. The OWASP 2025 anchoring with explicit exclusion rationale requirement prevents checklist drift.

---

### 3. LLM & Agentic Application Security Checklist

**Strengths:**
- Explicit freshness concern with version pinning and instruction to check genai.owasp.org — appropriate for fast-moving domain
- Covers indirect injection (retrieved docs, tool output) not just direct user input — this is where most LLM security checklists fail
- Agent-specific categories (goal hijack, rubber-stamp approval, cascading failures) that don't exist in traditional appsec
- ASI categories (2025 Agentic Top 10) integrated systematically rather than bolted on
- Confidence cap for LLM findings appropriately lower due to runtime/model dependence

**Weaknesses:**
- "Apply only if the project embeds LLM calls or agent/tool-use; otherwise not applicable, skip rather than score" — this is sensible, but no instruction in the other checklists about when to invoke this one. Should the appsec checklist tell reviewers "if LLM use detected, also apply llm-agentic-security-checklist.md"?
- Section D bundles supply chain (LLM03/ASI04), data poisoning (LLM04), code execution (ASI05), resource limits (LLM10), and cascading failures (ASI08) — this is 5 distinct concerns sharing a section header
- ASI10 (Goal & Plan Visibility) is mentioned in Section E but never appears as a reviewable category — is it only runtime-verifiable, or should logging of agent plans be a code-checkable item?
- Stopping criterion requires covering all LLM01-10 + ASI01-10, but ASI10 is absent from Sections A-D — this is a completeness gap

**Verdict:** Necessary and well-scoped for the domain, but has a missing category (ASI10) and the bundling in Section D is aggressive. The integration point with the other checklists is under-specified.

---

## Separation Analysis

### What's well-separated:
- **Supply chain** is correctly split: dependency integrity/lockfiles/pinning live in project-safety (repo infrastructure concern), while model/tool-plugin provenance lives in LLM checklist (model-specific supply chain)
- **Secrets** handling is correctly split: hardcoded secrets/committed secrets/logging exfiltration → project-safety; secrets in system prompts → LLM checklist
- **Injection** is correctly split: classic SQL/command/template injection → appsec; prompt injection → LLM
- **Access control** is correctly split: app-level authz/IDOR/tenancy → appsec; agent identity/confused deputy → LLM

### What has overlap or gaps:
- **Output handling boundaries are fuzzy:** Appsec checklist covers "user input → HTML/DOM unescaped" (XSS) and "model output → dangerous sink" is explicitly LLM territory (LLM05). But if an LLM output passes through the same rendering path as user input, the reviewer needs both checklists and must recognize the connection. Neither checklist says "if model output enters the rendering pipeline, also check appsec Section D."
- **Sandboxing split is unclear:** Project-safety has "Sandbox/isolation: Dockerfile/seccomp/IAM manifest requests exceed observable functionality?" LLM checklist has "Unexpected code execution (ASI05): agent writes+executes code... w/o sandbox/execution allowlist?" These overlap conceptually — the LLM checklist should reference the project-safety sandboxing check rather than duplicating, or explicitly say "this is the same sandbox, verify it covers code-generated-by-model as a threat source."
- **"Not verifiable from repo" sections use different labels:** Project-safety calls it "Section C — Not verifiable from repo contents"; Appsec calls it "Section E — Not verifiable from repo"; LLM calls it "Section E — Not verifiable from repo." Same concept, different section letters, slightly different naming. Not harmful but suggests they evolved independently.
- **Ground rules are referenced but not unified:** Project-safety defines the ground rules; the other two say "see companion doc, not repeated." But the appsec checklist adds "Stopping criterion" which doesn't exist in project-safety, and the LLM checklist adds "Freshness." The ground rules aren't fully centralized.
- **Confidence definitions differ slightly:** Project-safety: High = "read exact executing code"; Appsec: High = "read exact executing code" (identical); LLM: High = "structural findings (no input separation exists at all, no tool-call validation exists at all)" — this is a narrower definition. All three should either share a unified definition or the LLM one should explicitly say "overrides companion doc High definition because..."

### Structural recommendations:
1. Extract shared definitions into a 4th doc (review-standards.md?) containing ground rules, evidence standards, severity/confidence definitions, output format, and "not verifiable" handling.
2. Add cross-reference triggers: appsec should say "If LLM use detected → also apply llm-agentic-security-checklist.md"; project-safety should say "If agent code execution detected → verify sandboxing also covers ASI05 threats (see llm-agentic-security-checklist.md)."
3. LLM checklist Section D should be split or at minimum have clear subsection headers — right now it's "Supply chain, execution, resource limits" which is a signal that it's too broad.
4. Fix the ASI10 gap — either add it to a reviewable section or explicitly exclude it with rationale (e.g., "ASI10 requires runtime observation of actual agent behavior; code review can only verify that plan-visibility logging is configured — see Section E").

### Overall verdict:
The separation is conceptually correct (pipeline trust vs. app logic vs. model-specific) and the scoping statements at the top of each doc are precise. The execution has minor inconsistencies in shared infrastructure (definitions, "not verifiable" handling, confidence models) and missing cross-reference triggers that a reviewer encountering all three would need. The LLM checklist has the most structural issues but also the hardest domain. With a 4th shared-standards doc and cross-reference additions, this would be a strong coordinated set.