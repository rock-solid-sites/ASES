---
title: ASES Documentation Inventory and Legacy Discussion Disposition
version: 1.0.0
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/ASES Task-Scoped Information and Handoff Method.md
related_documents:
  - docs/README.md
  - docs/architecture/Task-Scoped Information Architecture Decision 2026-11-21.md
last_updated: 2026-11-21
---

# ASES documentation and discussion sweep — evidence and exceptions

**Scope:** Public `rock-solid-sites/ASES` repo-owned source documentation plus Projektor ASES and Work Notes WNASES trackers. This is not a cross-project or private conversation archive sweep. It is not a claim that every active document has been semantically revalidated.

## Frozen source and first scan

The [accepted task-information architecture](../architecture/Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md) merged at commit [`2235d237`](https://github.com/rock-solid-sites/ASES/commit/2235d237044d6cb850f827d65baadd1fe3da5b34). The Git tree contains 7,934 blobs and 1,418 Markdown/MDX/YAML files, including 809 vendored Markdown files within `fork/` which are **not ASES-authored documentation**.

The initial read-only source audit [Actions 44838553266](https://github.com/rock-solid-sites/ASES/actions/runs/44838553266) found **439 in-scope owned Markdown/MDX files**, **96 declared Active or current-skill sources**, **87 active sources missing an explicit version**, **94 active sources with at least one metadata/route warning**, and **zero duplicate declared-active canonical title/program identities under this limited matcher**. These figures are for the scanned branch at the specified run, not universal proof of document semantics.

The automated scanner and ten negative-control tests are at [`scripts/docs_audit/`](../../scripts/docs_audit/inventory.py). It indexes exact owned source paths and raw metadata, flags active unversioned files, duplicate declared-active canonical identities, selected legacy markers and broken explicit Markdown links, and emits a machine-readable audit plus a generated Markdown index. Its findings are **diagnostics, not automated authority assignment**. GitHub Actions preserves the generated index and report for every relevant revision.

## Corrected misleading source routes in this sweep

- `AGENTS.md`: previously an Active/Canonical 417-line Crosslink-era root policy. Replaced with a versioned, Derived task-selection adapter that links the current canonical method and skills, preserves operator/secret/cost/evidence boundaries, and forbids treating retired launch procedures as current.
- `SESSION-START.md`, `docs/SESSION-END.md`, `docs/ORCHESTRATOR.md`: old mandatory-session and fixed-deployment instructions replaced by short **Deprecated/Derived** redirects at their original paths. No mandate to implement replacement session documents.
- `docs/methodology/Agent Model Launch Routes.md`: October 2026 IT3812/provider route table replaced by a **Deprecated** redirect to `skills/current/agent-launch`; it is not current spending authorization.
- `docs/README.md`: new human navigation entrypoint with current owner/method/skill links and exact distinctions among canonical, experimental and historical material.
- Three foundational standard files (`Documentation Standard`, `Documentation Taxonomy`, `Canonical Terminology`) gained/received repaired structured frontmatter and an **explicitly new metadata baseline revision**; the underlying normative text was not rewritten or retroactively declared historically versioned.
- Root `README.md`, `ORIENTATION.md`, `ARCHITECTURE.md` gained current routing links and explicitly dated entrypoint revisions rather than hiding the accepted task-information architecture.

The original removed Crosslink/VPS documents remain retrievable at commit `2235d237...` in Git history; **they are not current instructions** merely because an old chat, issue, wiki page or draft PR still links to the same filename. The on-disk redirect prevents those filenames from silently regaining historical authority.

## Open discussion and source classification

| Record | Disposition and reason |
| --- | --- |
| Projektor **ASES-22** / Work Notes **WNASES-22** | **Already done:** accepted task-scoped method/ADR; do not reopen a graph-first format debate |
| Projektor **ASES-11** | **Superseded discussion:** mandatory replacement session-start/end documents and `session-lifecycle` skill are not required. Close as cancelled after redirects merge |
| Work Notes **WNASES-9** | **Keep open:** exhaustive active metadata/version/identity collisions and source-dependent review are not completed by an index scanner |
| Projektor **ASES-5** | **Keep open:** optional derived document/relationship projection into Projektor must be evidence-backed and must not acquire canonical authority |
| Projektor **ASES-6** | **Keep open:** independent role/permission review; historical `docs/ORCHESTRATOR.md` must no longer be described as an Active operational contract |
| Projektor **ASES-19** / Work Notes **WNASES-16** | **Keep open:** independent experimental knowledge-index retrieval benchmark; no mandatory central graph was adopted |
| Work Notes **WNASES-18** / **WNASES-19**, draft PRs **#64/#63** | **Keep separate:** unlaunched/experimental policy publisher and OpenCode instruction-exposure pilots, not requirements to decide the accepted documentation architecture |
| Draft PR **#45** | **Potentially misleading old launch packet:** its old conditional `AGENTS.md` bootstrap, historical prompt method and provider assumptions require explicit supersession or fresh recompilation before any new autonomous run; it must not be presented as a current ready-to-dispatch package |

Other older discussions unrelated to this architectural decision (model streaming diagnostics, Resource Solver ontology, testing methods, browser trials, etc.) should **not** be closed as "resolved" by an ASES documentation decision. They retain their own evidence and owners.

## Remaining obligations and limitations

1. **Version/metadata review remains material.** Most declared-active sources in the first snapshot had no explicit version. Do **not** backfill fabricated `1.0.0` versions or silently change Active to Deprecated across broad older research.
2. **Source ownership needs verification.** Some shared EDASES documents in this repository declare `canonical_repository: edases` and old mirror/placeholder notes; distinguish mirrors from actual ASES-owned canonical sources, with explicit owner approval before changing authoritative identity.
3. **Runtime exposure is still unverified.** Static cleanup of root/legacy files does not prove which files any specific Codex/OpenCode version auto-loads. The operator-deferred fresh-chat skill-invocation test remains deferred.
4. **Index is descriptive, not enforcement.** The scanner does not prove every dependency edge, cross-project permission, duplicate logical identity outside simple matching, external link freshness or semantic quality. Projektor remains a derived projection, not a policy registry.
5. **Discussed versus completed:** architecture discussions are settled; technical doc-health issues stay open until actual reviewed repairs and source-pinned verification. Closing an obsolete discussion must link a canonical replacement or explicit separate tracking issue.

**No model or provider API invocation, payment, private-archive extraction, runtime configuration deletion or actual daemon launch was used for this sweep.**
