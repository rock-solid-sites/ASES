# Synthesis: Documentation Process Mitigation Plan
## Resolving Context Bloat, DRY Violations, and Agent Friction in ASES

**Date:** 2026-06-23  
**Author:** OpenCode (Principal/Orchestrator Agent)  
**Type:** Integration, Analysis  
**Status:** Under Adversarial Review  
**References:** `findings/2026-06-23-beds24-plugin-evidence.md`  

---

## 1. Problem Statement & Objectives

Adversarial reviews conducted independently by **Gemini 3.1 Pro Preview** and **Zhipu GLM 5.1** exposed critical architectural debt in the ASES documentation and record-keeping processes. The four major failure surfaces identified are:
1.  **Catastrophic Context Bloat:** High-volume, natural-language, narrative historical logs (like detailed multi-page syntheses) clog the agent's context window, increasing latency and token-burn.
2.  **Procedural Overhead & Ceremony:** Manual, pre-execution essay writing (like `selection-rationale/`) simply to bypass local script audits is a process bottleneck.
3.  **Data Redundancy (DRY Violations):** Identical architectural facts (e.g., framework features and deprecation statuses) are manually duplicated across evaluations, matrices, and syntheses, risking write-drift.
4.  **Agent-Loop Friction:** Forcing high-performance compute cycles to format human-readable Markdown documents slows down execution throughput.

### Objectives:
*   Maintain **100% mathematical auditability** and decision provenance.
*   Reduce runtime context payloads by **>80%**.
*   Abolish manual, duplicate multi-file updates.
*   Eliminate prose-generation friction from the critical agent execution loop.

---

## 2. Proposed Refactoring & Mitigations

### 2.1 Refactor 1: Transition Selection Rationales to Structured JSON (`decisions.json`)
*Eliminates manual pre-execution markdown essays and bypass-ceremony.*

Instead of creating prose-heavy `selection-rationale/*.md` files, decision provenance is captured in a lightweight, single-source-of-truth JSON log: `.crosslink/decisions.json`. 

#### The JSON Schema (`.crosslink/schemas/decision.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DecisionRecord",
  "type": "object",
  "properties": {
    "id": { "type": "string", "pattern": "^DEC-\\d{4}-\\d{2}-\\d{2}-\\d{2}$" },
    "timestamp": { "type": "string", "format": "date-time" },
    "decider": { "type": "string" },
    "selection": { "type": "string" },
    "crosslink_issue": { "type": "integer" },
    "status": { "type": "string", "enum": ["Live", "Reconstructed"] },
    "rationale_factors": {
      "type": "array",
      "items": { "type": "string" }
    },
    "alternatives_considered": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "rejection_reason": { "type": "string" },
          "preferred_condition": { "type": "string" }
        },
        "required": ["name", "rejection_reason"]
      }
    },
    "evidence_expected": {
      "type": "object",
      "properties": {
        "supports_if": { "type": "array", "items": { "type": "string" } },
        "falsifies_if": { "type": "array", "items": { "type": "string" } }
      },
      "required": ["supports_if", "falsifies_if"]
    }
  },
  "required": ["id", "timestamp", "decider", "selection", "status", "rationale_factors", "alternatives_considered", "evidence_expected"]
}
```

#### Local Audit Script Integration:
The local audit script (`scripts/audit_research_issues.py`) is refactored to parse `.crosslink/decisions.json`. An issue is deemed compliant if a corresponding `crosslink_issue` entry exists in the JSON log, eliminating the fragile substring regex parsing of natural-language descriptions.

---

### 2.2 Refactor 2: Establish Single Source of Truth & Build-time Matrix Compilation (DRY)
*Resolves data redundancy and synchronicity failures.*

To permanently eliminate data duplication, we establish a strict single source of truth:
1.  **Evaluations as the Core Data Nodes:** `harness-evaluations/<Name>.md` remains the only manually authored/edited file for evaluations. It holds the observations, findings, and metadata.
2.  **Abolish Manual Matrix Updates:** The file `capability-mapping/Harness-Capability-Matrix.md` is deleted from git tracking.
3.  **Automated Matrix Compiler (`scripts/compile_matrix.py`):**
    We introduce an automated compilation script that runs during pre-commit or CI/CD gates. It:
    - Parses all `harness-evaluations/*.md` files.
    - Extracts the metadata blocks and the sectional mappings under `## 2. Architectural Alignment`.
    - Generates and writes the consolidated `Harness-Capability-Matrix.md` and the `syntheses/` timeline tables dynamically.

---

### 2.3 Refactor 3: Asynchronous Markdown Compilation & Telemetry-Only Agent Loop
*Removes prose-generation and formatting friction from the execution loop.*

Agents in the active loop must not write human-oriented Markdown reports. 
*   **Active Agent Loop:** The agent strictly executes the task (e.g., code editing, testing, API verification) and emits raw structured telemetry (JSON/YAML metrics and event blocks).
*   **Asynchronous Doc Compiler:** A background CI/CD process (or local pre-commit git hook) intercepts the JSON telemetry and compiles the polished Markdown reports, portfolios, and matrices.
*   This isolates high-performance compute cycles from formatting, indentation correction, and natural-language padding.

---

### 2.4 Refactor 4: Context-Window Eviction & Quarantine Policies
*Prevents context-window saturation and token-burn.*

To ensure that historical narratives do not bleed into the active context window, we enforce a strict file injection allowlist/denylist in our agent settings (`.claude/settings.json`):

*   **Deny-listed from active context (Quarantined):**
    - `syntheses/` (except the brief, high-level map).
    - `session-handoffs/` and historical release notes.
    - Raw text logs of previous evaluations.
*   **Allow-listed for active context (High-signal only):**
    - `.crosslink/rules/global.md` (Active constraints).
    - `.crosslink/decisions.json` (Active structured registry).
    - Compiled `STATUS.json` (Compact project-health status, updated by Crosslink).

Historical context is archived permanently in the git repository log, remaining accessible via targeted `read` queries only on direct demand, and is never proactively injected.

---

## 3. Comparative Flow Mapping

### Legacy Flow (High-Friction, Bloated Context):
```
  [Start Session] 
        │
        ▼
  (Inject heavy Syntheses & Rationale Markdown files)  <── [Context Bloat!]
        │
        ▼
  [Write Pre-Execution Selection Rationale Markdown]    <── [Overhead & Ceremony]
        │
        ▼
  [Execute Task & Implement Code]
        │
        ▼
  [Manually update evaluations, matrices, & syntheses]  <── [DRY Violations, Friction]
```

### Refactored Flow (Low-Friction, Structured & Automated):
```
  [Start Session] 
        │
        ▼
  (Inject only decisions.json & active rules)          <── [Clean Context]
        │
        ▼
  [Append Decision JSON Record to decisions.json]       <── [Instant, Schema-Validated]
        │
        ▼
  [Execute Task & Implement Code]
        │
        ▼
  [Commit & Push] 
        │
        ▼
  [CI/CD / Git Hook compiles Matrix Markdown & Docs]   <── [Asynchronous, Non-Blocking]
```
