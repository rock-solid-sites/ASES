---
title: Projektor MCP Registration Failure and Recovery — EDASES Case 2026-11-06
program: EDASES
layer: Research
document_type: Incident Record
status: Active
authority: Derived
canonical_repository: edases
depends_on:
  - docs/research/registry/Failure-Matrix.md
related_documents:
  - docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md
  - docs/research/EDASES Review Methodology.md
  - https://github.com/rock-solid-sites/ases-plugins/blob/main/connectors/projektor/INCIDENT-2026-11-05.md
consumed_by:
  - https://github.com/rock-solid-sites/ases-plugins/blob/main/docs/CHATGPT-MCP-CONNECTION-RUNBOOK.md
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-06
---

# Projektor MCP registration failure and recovery — EDASES case

**Case ID:** EDASES-MCP-PROJEKTOR-2026-11-06  
**Observation interval:** 2026-11-05 through 2026-11-06 (UTC).  
**Status:** Operational recovery observed; comparative performance claim and complete security assurance not established.  
**Nature:** Single project observation with multiple direct technical probes, not an independently replicated benchmark.

## Original objective / acceptance oracle

Operate one private, owner-authorized Projektor project workspace from ChatGPT on both phone and laptop, with the existing Cloudflare Worker/D1 deployment unchanged by the forthcoming VPS migration. The user-facing oracle was **Projektor tools appear in ChatGPT and authenticated calls read projects, write a bounded record, and independently verify that write**. Packaging success, OAuth metadata, login screens, or backend connectivity alone were explicitly insufficient.

## Initial deviation and incorrect assumptions

The private `projektor-rss` plugin package (v0.1.0, later v0.2.0) was created and installed, but Projektor tools did not appear in ChatGPT. The investigation initially assumed the remaining fault was an OAuth/Cloudflare routing problem and proposed starting a fresh conversation. The operator supplied a previously established empirical invariant for this environment: functioning custom MCP tools appear immediately in any existing chat. Recommending a new chat had no discriminating value and was abandoned.

The **first necessary distinction** was package existence versus an actual MCP connection registered, authenticated, scanned, and exposed by ChatGPT. A package may contain a correct `mcp.json` without itself having established the client-side MCP registration. The precise missing registration step is supported by paired controls and the successful intervention, not by direct access to internal ChatGPT registration telemetry.

## Chronology and observations (preserve order, no hindsight rewriting)

1. **Package state:** Plugin Creator reported a valid private Projektor package with a remote Streamable HTTP MCP URL and OAuth DCR metadata; ChatGPT's actual available-tool registry contained no Projektor tools.
2. **Infrastructure probing:** Cloudflare Access initially redirected OAuth discovery to an interactive sign-in. Narrow protocol exceptions were configured and metadata calls began returning JSON. These intermediate passes did not expose any Projektor tools.
3. **Second fault introduced during repair:** A new dedicated MCP Cloudflare Access application used a distinct JWT audience, while the Projektor Worker trusted the original site's audience. Comparing both Access application audiences against the Worker binding directly established the mismatch. This was a **real configuration defect we introduced**, but no successful authenticated request through that application was observed; whether it materially caused an additional end-user failure is not proven.
4. **Containment/correction:** Managed OAuth was enabled on the original, owner-only Access application and the conflicting separate MCP Access application was removed. The existing browser sign-in remained protected. External unauthenticated MCP `GET` and JSON-RPC `POST tools/list` both received `401` with a Cloudflare OAuth `WWW-Authenticate` challenge; OAuth discovery returned JSON. This proves appropriate unauthenticated challenge behavior, not authorized tool use or comprehensive isolation.
5. **Paired client control:** A working `cgrmcp-current` installation used a registered app binding and exposed four tools. A different historical cgrmcp package and the Hostkey package could exist without those tools being surfaced. The Projektor package had no separate app binding. The observation localized attention to client MCP registration rather than backend software changes.
6. **Decisive user action:** The operator created and authenticated the custom Projektor MCP connection in ChatGPT. Projektor tools became available in the **existing conversation immediately**, falsifying the repeated fresh-chat explanation.
7. **Service-layer acceptance:** The ChatGPT Projektor MCP returned workspace `Projects` with role `owner`; `list_projects` returned five expected projects (ASES, ATProto, Grant Management, HMS, Trip'n); `get_issue` read ASES-4 and ASES-5. A bounded comment was written on ASES-4 and independently confirmed through `list_comments` plus `list_project_activity`. Comment ID `94ae00f0-8c73-49ea-9841-59f749e512cc` is the durable write witness.
8. **Result:** Functional authenticated ChatGPT MCP read/write acceptance passed. Negative permission-matrix tests, session revocation, cross-workspace isolation, and simultaneous phone/laptop behavior were not exhaustively tested.

## Hypothesis / probe / outcome ledger

| Hypothesis before probe | Cheapest discriminating observation | Result / inference |
| --- | --- | --- |
| Installed plugin implies MCP tools available | Inspect actual ChatGPT tool inventory; compare to plugin package metadata | **Rejected** as a general equivalence; Projektor package existed, tool absent |
| Backend is universally unreachable | Unauthenticated request to exact MCP route and OAuth discovery | **Weakened**; endpoint reached and returned expected 401 challenge; does not establish authorized call |
| ChatGPT needs a new conversation | Observe available tools after explicit MCP registration **in same chat** | **Rejected**; tools appeared immediately |
| Cloudflare authentication alone proves working plugin | Compare host-key login records with actual Projektor tool inventory | **Rejected**; other-app login did not produce Projektor tools |
| Separate Cloudflare Access app JWT is accepted by Worker | Compare Access audience and Worker trusted audience | **Rejected**; direct mismatch; intervention rolled back |
| Client MCP registration is missing critical step | Register/authenticate MCP and observe real tool inventory + read/write | **Strongly supported** by before/after evidence; platform-internal cause not separately instrumented |

## EDASES failure mechanisms

**F1 — Proxy success promoted to whole-system success:** source/package creation and OAuth metadata were treated as if they proved client registration. Required semantic: independent client-visible registration, tool discovery and original-operation acceptance.

**F2 — Fix-first changes ahead of the closest failing boundary:** repeated Cloudflare edits occurred before direct MCP registration had been conclusively checked. Required semantic: identify the nearest missing observable transition and run the cheapest paired control before mutating infrastructure.

**F3 — Remediation creates a second fault:** a new Access application changed the JWT audience without coordinating with the Worker verifier. Required semantic: map security identity/audience dependencies, preserve existing valid authority, and compare before/after values on every auth change.

**F4 — Uninformative retry recommendation:** requesting another chat did not test an unresolved variable given the operator's prior direct evidence. Required semantic: no repeated retries without a new discriminating prediction; operator-provided environment observations constrain the hypothesis set.

**F5 — Intermediate green probes mistaken for final recovery:** 401 challenge, 200 metadata, Cloudflare login logs, and D1 queries independently proved useful lower-layer properties but not `list_projects` or write persistence. Required semantic: close only at user-facing acceptance, with independent side-effect observation.

## Why this incident was a successful fast isolation exercise despite mistakes

The operator reports it as the **quickest failure → diagnosis → fix cycle in their experience by a wide margin**. That is a comparative operator observation; there are no comparable case-duration measurements in this record to support a quantitative speedup claim.

The observable efficiency mechanisms were: access to live ChatGPT plugin configurations and tool inventory, a working cgrmcp control, targeted HTTP/Cloudflare API probes, a clear decisive registration action, and cheap read/write verification without redeploying Projektor or moving infrastructure. The method made partial success and new defects visible instead of masking them. Earlier speculative edits still represent avoidable cost.

**Do not claim** that all Cloudflare edits were prerequisites for recovery or that this one case validates a universally optimal troubleshooting order. The operational plugin procedure may adopt the directly demonstrated minimal gates now, while the broader EDASES diagnostic-method proposal remains unpromoted until reconciled and evaluated.

## Downstream operational transfer (bounded authority)

Owned plugin work in `rock-solid-sites/ases-plugins` now adopts a **project-specific** MCP creation/runbook rule: package/publish and **register/scan** are separate outcomes; check real current-chat tool exposure first; use a working installed MCP as a positive control; after owner authorization prove `tools/list`, safe authenticated read, bounded authorized write and independent read-back; test unauthenticated denial. Stop speculative backend changes when registration is not yet established. The user performs only the irreducible consent/registration operation; builders perform all available technical checks.

This is a downstream tool-development acceptance profile, **not** a change to the universal ASES methodology, kernel or higher-level authorities.

## Retained primary evidence / gaps

- Project-owned incident log with chronology, release IDs, redacted Access diagnostics, misdiagnoses, configurations and rollback: [ases-plugins Projektor incident](https://github.com/rock-solid-sites/ases-plugins/blob/main/connectors/projektor/INCIDENT-2026-11-05.md).
- Projektor tracking artifact and write/read-back witness: ASES-4, comment `94ae00f0-8c73-49ea-9841-59f749e512cc`, project activity `issue_commented`.
- Live Plugin Creator metadata and Projektor MCP responses were inspected in ChatGPT on 2026-11-06. The incident log is a narrative/evidence index; independent signed client-platform telemetry and full token/audit trails were **not** archived.
- Source check was against Projektor upstream v0.9.1, not a proven digest of the deployed Worker bundle. Do not silently treat source inspection as production binary attestation.
- Replication on other private MCPs, elapsed-time benchmarks, security negative controls and dedicated mobile acceptance are **NOT TESTED**.

## Follow-up research

Replay a minimal two-condition fixture (package-only vs registered MCP) and a controlled JWT-audience mismatch with synthetic credentials where safely possible. Compare hypotheses eliminated per probe, time-to-first failing boundary, unnecessary mutations, time-to-verified-original-outcome and false-positive success claims against a fix-first baseline. Preserve independent controls before generalizing to the EDASES Failure Matrix at greater confidence.
