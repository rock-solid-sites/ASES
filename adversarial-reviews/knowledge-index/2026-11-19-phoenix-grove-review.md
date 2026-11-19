---
title: Phoenix Grove Adversarial Review - Knowledge Index Prototype 2026-11-19
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/proposals/knowledge-index/Final Review Checklist.md
related_documents:
  - docs/proposals/knowledge-index/Design and Integration Proposal.md
  - scripts/knowledge_index/TECHNICAL.md
last_updated: 2026-11-19
---

# Phoenix Grove adversarial review — knowledge index pilot

## Execution and decision status

**Review target:** ASES [draft PR #61](https://github.com/rock-solid-sites/ASES/pull/61), immutable reviewed commit [bef2782144ca5553b1632c6f0747169d5933e1ff](https://github.com/rock-solid-sites/ASES/commit/bef2782144ca5553b1632c6f0747169d5933e1ff). This is **pre-review** source, and later documentation commits must not retroactively be treated as reviewed.

**Independent runner:** private [ases-plugins Actions run 44577774247](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44577774247), launched by one-shot workflow at runner commit 338df35bfd3df22c6ccc3cad700e1d79454b1cfd. Reviewer models were invoked through the explicit Phoenix Grove pgs2 Codex configuration, each in a separate, read-only, bounded Actions job, with no automatic retries, fallback or deployment. The reviewer processes received line-numbered, bounded **inert source text**, not a writable source checkout. The executable Codex sandbox was read-only; independent denial of *all* reviewer tool use was **not** demonstrated. The installed CLI version was pinned to 0.169.0.

| Model / lens | Evidence and exact input | Execution | Verdict |
| --- | --- | --- | --- |
| DeepSeek v4.1 Flash 1017 — identity/correctness | [Job 135749867039](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44577774247/job/135749867039); 23,837 prompt bytes; SHA-256 6ac982ed92f28ffc020825e72a0ba3ef262b8f097afc19521b882a727c77bcb0 | Exit 0; 27,835 output bytes; report SHA-256 c2e83847802a777afedc7310d4a92be33d5ef8b9c6d4b5e1ba793f75d213ba6e | **Substantive report delivered**; many exploratory observations self-retracted, so triage selectively |
| MiMo v2.6 Flash — privacy/output safety | [Job 135749866521](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44577774247/job/135749866521); 29,835 prompt bytes; SHA-256 d6ceb2f77951a74ef6a6881abdfc87832b9f1b79a6f2df3c52d0ae4bb17444a9 | Exit 124 after 250-second deadline; **0 output bytes** | **FAILED INVOCATION — NO REVIEW VERDICT**; not a clean security review |
| GLM 5.3 Flash — architecture/integration | [Job 135749867049](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44577774247/job/135749867049); 34,596 prompt bytes; SHA-256 db44ba38c8f121ade262dd3ee3c001b2e23e316400921d5e05ef769e396d30c8 | Exit 0; 4,831 output bytes; report SHA-256 5332c69b2016ad817114eb874b81e698b4420b41b92171f5477ae54971cb5f0c | **Substantive report delivered**, documentation/design-focused, explicitly did not inspect importer/graph implementation |

**Actual completed model reviews: 2/3.** This was a three-model *attempt*, not three successful reviews. The workflow run is failed overall because MiMo timed out. The runner step summaries preserve the full reports (the console excerpt may truncate long outputs). Provider-side token accounting and billed USD are **unknown**, not zero. No GitHub Actions artifact was uploaded. Model endpoint configuration and CLI invocation are recorded; the summaries do not independently attest backend model identity or provider charges.

## Triage policy

Results below are **candidate findings from independent model inspection**, not verified runtime counterexamples. The review's bounded model input did not include the entire repository or always the full tests, and neither successful model executed tests. Each defect requires a minimal red test before it is promoted to confirmed. Exclude DeepSeek passages that explicitly concluded "not a defect"; do not count the model's numbered exploratory notes as 34 independent bugs.

### High-priority code defects to falsify

**PG-KI-01 — forged metadata edge becomes public (high; DeepSeek; inspection-supported).** In scripts/knowledge_index/indexer.py, the default-visibility pass labels an edge public if its *ID starts with* "meta:" and both nodes are public, even if the edge came from user-supplied JSONL. The system promises that explicit JSONL edges default private. **Reproduction:** provide two public endpoint nodes and an explicit edge with ID "meta:forged" and no visibility field. Expected: private or rejection; current branch appears to set public. This affects relationship-existence confidentiality and the default public projection. Test first, then derive metadata provenance from the importer rather than trusting a caller-controlled prefix.

**PG-KI-02 — out-of-root JSONL ingestion (high; DeepSeek; inspection-supported).** scripts/knowledge_index/indexer.py joins unvalidated --include entries with the root directory and reads selected .jsonl files without checking their resolved path remains under the approved root. **Reproduction:** include "../outside.jsonl" containing valid records; additionally test a symlink under root pointing to an external JSONL file. Expected: controlled rejection before external content read. Markdown outside-root paths can also be read before relative-path validation. A future connector must not expose this selection surface to untrusted callers.

**PG-KI-03 — stable identity impersonation in partial indexes (high; DeepSeek; inspection-supported).** A document not registered in identities.json may declare an arbitrary frontmatter knowledge_id; the registry conflict check only applies when that **same file path** is registered. If the registered owner of that ID is outside include_paths, duplicate-node validation cannot detect the hijack. **Reproduction:** index only a new file that declares the ID of a different registered-but-excluded document. Expected: reject the reserved ID assignment. This matters even for read-only indexing because downstream edges can be misattributed.

**PG-KI-04 — quote stripping changes IDs (medium/high; DeepSeek; inspection-supported).** The limited metadata parser removes *all* leading and trailing quote characters with string.strip, not a single matching YAML quote pair. **Reproduction:** unquoted scalar knowledge_id ending in an apostrophe, or a doubly quoted value ending with an intended apostrophe. Expected: exact ID content or clearly unsupported syntax, not silent mutation. A change can trigger a false registry conflict or produce a distinct ID.

### Additional implementation and assurance findings

**PG-KI-05 — malformed JSONL crashes outside controlled validation (medium; DeepSeek).** A JSON line that is an array/number or an object with an unhashable ID reaches .get, dictionary membership, or edge logic and raises AttributeError/TypeError rather than IndexErrorData. Falsify with valid JSON values 42, [], and an object whose "id" is an array; preserve the last successful SQLite projection.

**PG-KI-06 — FTS5 syntax errors escape the query boundary (medium; DeepSeek).** Arbitrary search strings such as an unmatched double quote or unfinished Boolean expression can raise sqlite3.OperationalError. Falsify by submitting such inputs and defining whether text is treated as literal search or supported FTS grammar. This is not SQL injection (query values are parameterized); it is robustness/contract failure.

**PG-KI-07 — evidence reference integrity is under-validated (medium; DeepSeek and GLM).** The validator checks that evidence_refs is a list but not that entries are valid string IDs, that cited sources exist, or that a reviewed edge has sufficient provenance. Falsify with an edge carrying [null], an empty list, and nonexistent IDs. The public projection presently suppresses some missing evidence links, which is **not equivalent to source assertion validation**. Specify how reviewers promote candidate to reviewed status: a JSONL declaration alone is not independent approval.

**PG-KI-08 — missing identity registry silently disables stable IDs (medium; GLM; direct code behavior).** registry.read_registry returns an empty dictionary when identities.json is absent. This is appropriate for an optional experimental adapter only if explicitly indicated; it violates a future contract expecting a configured stable-ID registry. Falsify with a moved/missing registry file and a registered document. Require a deliberate optional mode or a hard error, not an ambiguous fallback.

**PG-KI-09 — registry review provenance missing (medium; GLM; design gap).** The registry records ID/path/aliases but has no reviewer, rationale, timestamp, source revision or review-approval evidence. The claim that IDs are "reviewed" is therefore a process assertion, not a mechanically enforced property. Define whose authorization confers that status and how it is audited. This is an **integration design gate**, not a demonstrated prototype corruption.

**PG-KI-10 — non-GitHub namespaces produce GitHub URLs (medium; DeepSeek; integration limitation).** source_uri construction removes a literal github: prefix and otherwise still constructs github.com. Falsify with --namespace gitlab:org/repo; source URLs are wrong. Adopt per-provider adapter semantics rather than generalizing the existing GitHub-only constructor.

**PG-KI-11 — scope-dependent ambiguity and legacy identities (medium/low; DeepSeek/GLM; review-required).** Casefold-based alias matching deliberately rejects ambiguous title/stem collisions. Exact-case distinctions may fail to resolve, and path-derived IDs change on move. The former is conservative behavior rather than a proven misconnection; the latter is a **documented limitation**, not an undisclosed defect. Define a portable identity matching and migration contract before multi-repository integration.

**PG-KI-12 — unsupported frontmatter can change identity semantics (medium; DeepSeek; conditional).** A malformed/unsupported metadata block is quarantined, but the document remains indexable with fallback identity, so a previously explicit non-registry knowledge_id could disappear. Falsify a metadata-change sequence with no edges to the node; decide whether identity-bearing frontmatter parse failures must block the build. Distinguish deliberate "keep the source searchable" behavior from identity-safety requirements.

### Explicit nonfindings, limited scope, and rejected inflation

- DeepSeek considered several candidate defects and then explicitly rejected them (e.g., duplicate IDs being detected by validate, normal missing-file checks, the purpose of alias-to-node mapping, correct positive FK enforcement, and truly atomic same-filesystem rename). **Do not include them as bugs.**
- GLM's observation that the registry path is ASES-local is true of the experimental pilot but **expected**: other repository adapters are not implemented or claimed. Record it as a roadmap/interface gate, not a regression in the current ASES-only scope.
- GLM's concern over the technical document's document_type is a low-priority taxonomy question, not a code correctness blocker.
- GLM's remarks about invalid UTF-8 or hypothetical wrappers were not backed by code-path reproduction. No finding is accepted for those without a concrete test.
- DeepSeek did not receive graph_view.py, so its non-disclosure findings cannot be treated as a completed audit of that module.
- **MiMo supplied no security verdict.** The failed invocation cannot count as reviewer agreement or disagreement.

## Recommended verification and decision gates

1. **Red test first:** PG-KI-01, -02, -03, -04; preserve failing examples as fixtures and resolve confirmed behavior. They affect explicit privacy or stable identity invariants.
2. **Input boundary tests:** PG-KI-05, -06, -07, -08 and -10; separate parser limitations from unsafe acceptance. Reject error-prone inputs predictably.
3. **Design review:** PG-KI-09, -11, -12 plus real authorization/revocation and external adapter rules from the existing [Final Review Checklist](../../docs/proposals/knowledge-index/Final%20Review%20Checklist.md).
4. **Security review coverage:** because MiMo timed out, **a dedicated independent privacy/output review remains incomplete**. A separately authorized, smaller-input retry may be considered; do not silently rerun the same paid call or substitute another model.
5. **After fixes:** review exact new commits and run the verified red→green tests. An architecture proposal can be accepted conditionally without granting production authorization.

**Decision A (merge experimental reviewable materials):** pending verified fixes/acceptance scope. **Decision B (maintained cross-project integration): NOT APPROVED.** Preserve the draft PR, source ownership and read-only archive boundary. Technical results live in ASES; ASES-19 tracks the human-facing disposition.
