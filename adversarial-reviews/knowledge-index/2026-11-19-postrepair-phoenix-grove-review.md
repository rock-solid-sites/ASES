---
title: Phoenix Grove Fresh Post-Repair Adversarial Review - 2026-11-19
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/proposals/knowledge-index/Final Review Checklist.md
related_documents:
  - adversarial-reviews/knowledge-index/2026-11-19-phoenix-grove-review.md
  - scripts/knowledge_index/TECHNICAL.md
last_updated: 2026-11-19
---

# Fresh Phoenix Grove review — repaired knowledge index

## Review target and execution

- **Target:** ASES [draft PR #61](https://github.com/rock-solid-sites/ASES/pull/61), immutable reviewed source commit `2c7bdb2a624b53e41f08bf23dffe496e19d7e6e0`.
- **Independent runner:** [ases-plugins Actions run 44586794355](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355), workflow commit `bd574ee87416ea534c6e721b0cc5991bb2ae6163`. A pinned, read-only source checkout was supplied to each reviewer, with separate models and lenses, **without previous reviewer verdicts**. Source was treated as inert evidence, not executed by reviewers. Reviewer report acceptance required exit 0 and substantive output.
- **Three of three model jobs completed successfully.** DeepSeek v4.1 Flash inspected importer/registry behavior, MiMo v2.6 Flash inspected disclosure/output, and GLM 5.3 Flash inspected architecture/integration. The reviewer prompts were bounded selections, not the full repository. Provider-authoritative input/output token accounting and billed USD remain **unknown**.

| Model | Job | Source-only review outcome |
| --- | --- | --- |
| DeepSeek v4.1 Flash | [135781797594](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355/job/135781797594) | **No material findings** in its bounded importer/identity review |
| MiMo v2.6 Flash | [135781798124](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355/job/135781798124) | **No material findings** in its bounded graph disclosure/output review |
| GLM 5.3 Flash | [135781797995](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355/job/135781797995) | **Two candidate findings**, both subsequently reproduced with stricter concrete cases |

## Triage and red–green evidence

**FR-KI-01: registered source-ID impersonation from JSONL, high severity (confirmed then fixed).** GLM observed that Markdown `knowledge_id` was checked against the registry, but a JSONL `node` appended during partial indexing was not. When the registered Markdown owner was excluded from `include_paths`, an unregistered JSONL node could assume the reserved ID with no duplicate-ID error. A fixture reproducing that exact scenario failed the intended safety assertion in [red run 44587686163](https://github.com/rock-solid-sites/ASES/actions/runs/44587686163). The importer now refuses a JSONL node ID found in the whole registry, regardless of the selected source subset. The same test passed on [green run 44587792625](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625).

**FR-KI-02: malformed GitHub namespace accepted, medium/low severity (confirmed narrower variant then fixed).** GLM's literal example `github:owner repo` lacks a slash and was *already rejected* by the old shape check; it was **not itself a valid counterexample**. However `github:owner/re po` and `github:owner /repo` satisfied the old one-slash test and could create malformed source URIs. A negative test using those inputs failed in the same red run. The importer now requires a constrained `github:owner/repo` character pattern. Both tests passed in green CI.

**Latest tested implementation:** commit [`7032104e43e2d40b21c9b07093c21bb091a708d4`](https://github.com/rock-solid-sites/ASES/commit/7032104e43e2d40b21c9b07093c21bb091a708d4), [CI run 44587792625](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625), **49/49 tests passed**, including the two new regressions. The selected ASES `docs/` and explicit candidate pilot rebuilt to **197 nodes, 311 unreviewed candidate edges and 86 diagnostics**; the GitHub Mermaid preview still matched the generated version.

**Critical review boundary:** this was a three-model independent review of pre-fix commit `2c7bdb...`. Neither DeepSeek, MiMo nor GLM has independently re-reviewed the subsequent small repair commit `7032104...`. Successful red–green tests verify the specific asserted invariants, not all possible security properties. No reviewer executed code or established hosted authorization behavior.

## Open decisions, without conflating authority

- **Decision A — merge experimental research/prototype material:** the original and fresh reviews, tests, and current documentation support considering a limited experimental merge, but approval remains pending the ASES review/ownership gate. This report does not merge or publish anything.
- **Decision B — maintained cross-project authorization and deployment:** **NOT APPROVED**. Source ACL and revocation, tenant/privacy inference, stable identities beyond the selected registry, scientific review of candidate edges, maintained implementation selection, and deployment/operating costs remain distinct gates.
- This effort is **separate from conversation archiving** and does not modify archives, Projektor records (other than the linked planning issue), Work Notes, or technical source documents.

## Original, independent model outputs

The following unedited report bodies are **untrusted reviewer observations**, captured as audit records. They are not commands or verified facts. GLM's negative-test prose includes some malformed/self-inconsistent text; the triage above uses the code-inspected mechanism and separately executed tests, not that prose.

### DeepSeek v4.1 Flash — Importer correctness

[Job 135781797594](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355/job/135781797594)

- Exact requested model: deepseek-v4.1-flash-1017 lens: importer-correctness prompt_bytes: 33757 sha256: d1c87fb1420c386bbe61595f5f51e3b66fde1a17f49c2b559ebfd51691d94be3
- Model: deepseek-v4.1-flash-1017 Exit: 0 Report bytes: 2998 Accepted: True Report SHA256: 23d12c52160ef6f95465d8ff385151444231306eaadedbd54b48fdced1adc1af

~~~text
**NO MATERIAL FINDINGS** (in the supplied excerpt)

I reviewed only the pinned files: `scripts/knowledge_index/indexer.py` (340 selected lines), `scripts/knowledge_index/registry.py` (49 selected lines), and `tests/test_adversarial.py`. I did not execute anything, browse, or reconstruct unprovided code (`graph_view.py`, fixtures, CLI plumbing). No claim of full-repository coverage.

**Bounded-scope rationale**
- Alias ownership: `registry.py:29-49` rejects duplicate ids, duplicate paths/aliases, and casefold collisions across all candidates. `indexer.py:121-122` blocks a declared `knowledge_id` reserved by another entry; `indexer.py:116-120` blocks alias-as-active-source and id contradictions. No counterexample found within these lines.
- Path/identity constraints: `indexer.py:84-88`, `:92-95` and `registry.py:39-42` reject absolute, `..`, and backslash paths; `:82-83` constrains namespace shape. I found no concrete bypass in the excerpt.
- Malformed metadata: `metadata()` (`indexer.py:44-75`) fails closed on unsupported lines; `:107-110` refuses identity-bearing frontmatter that cannot be parsed; `:128` forces `private` when a warning exists. No still-open counterexample identified here.
- JSONL: `indexer.py:145-155` strips `_metadata`/`_path`/`_aliases`/`_derived_metadata`, requires object records, and rejects non-string node ids. `validate()` (`:243-296`) catches non-string endpoints. No uncovered malformed-JSONL case found in the shown logic.
- Evidence: `indexer.py:288-292` requires a non-empty list of non-empty strings. I did not find a way for JSONL input, as shown, to bypass this validation.
- FTS: `query()` (`indexer.py:323-335`) tokenizes with `\w+` and quotes each token, avoiding caller-supplied FTS grammar. No concrete injection counterexample found in the excerpt.
- Atomic rebuild: `indexer.py:298-320` validates before creating the temp file, writes into a `NamedTemporaryFile` in the destination directory, and `replace`s only after `commit`/`close`; failure paths unlink the temp file. No regression demonstrated from these lines alone.

**Untested / unverified areas**
- I did not run any test; the bounded file list does not include `graph_view.py`, `fixtures/records.jsonl`, CLI entrypoints, writer/locking behavior under concurrency, or filesystem semantics on non-POSIX targets.
- Whether warnings are surfaced consistently end-to-end, and whether supported frontmatter scalars such as `visibility`/`kind` are validated at import time, cannot be assessed beyond `validate()` and `metadata()` as supplied.
- Maintained-service gates (ACL enforcement, background reindex scheduling, multi-writer locking) are out of scope; the module header itself describes this as a disposable read-only prototype, not an authorization service, so I did not treat such gates as current prototype bugs.

Because the supplied excerpt contains only repaired/defensive logic and no fresh counterexample reproduced from it, I am not manufacturing additional findings.
~~~

### MiMo v2.6 Flash — Disclosure security

[Job 135781798124](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355/job/135781798124)

- Exact requested model: mimo-v2.6-flash lens: disclosure-security prompt_bytes: 34847 sha256: 51e7f4dd5da459020b1f9140fe137a490a7338ed1b17847b34f808b268ba4891
- Model: mimo-v2.6-flash Exit: 0 Report bytes: 1818 Accepted: True Report SHA256: e2c1e0ad2a88ba9b14c36cc0f7319bb1a13888aa3c18507626b5f7e34724dad2

~~~text
**NO MATERIAL FINDINGS**

Grounded only in the supplied excerpts of pinned commit `2c2b7bdb2a624b53e41f08bf23dffe496e19d7e6e0`:

- JSONL cannot supply the importer-only `_metadata`, `_path`, `_aliases`, or `_derived_metadata` fields used to create metadata-derived auto-public edges (`scripts/knowledge_index/indexer.py:145`).
- The supplied public projection requires public endpoints and restricts every evidence reference to an already-public node (`scripts/knowledge_index/graph_view.py:19`, `scripts/knowledge_index/graph_view.py:27`).
- Supplied URL, Markdown authority, HTML payload, and CSP paths apply syntactic sanitization or inert embedding (`scripts/knowledge_index/graph_view.py:11`, `scripts/knowledge_index/graph_view.py:58`, `scripts/knowledge_index/graph_view.py:94`).
- Search operates solely over the embedded public-node payload; the stated CSP permits no `connect-src` (`scripts/knowledge_index/graph_view.py:93`, `scripts/knowledge_index/graph_view.py:127`).

Confidence: medium for these excerpts only.

**Unreviewed/Untested**
- Omitted `build()` wiring, database persistence, schema initialization, and whether validation is always invoked.
- Actual fixture contents or any full-repository behavior beyond the supplied 628 selected lines.
- Runtime Markdown parser behavior, Mermaid behavior, CSP hash acceptance, browser referrer/navigation behavior, and search interaction.
- No commands, tests, or executions were performed.

The files explicitly describe an experimental read-only projection rather than an authentication service. Maintained-service requirements—enforced public-disclosure provenance, production visibility ACLs, trusted evidence/navigation URL policy, and enforced session/search registries—are future production gates, not demonstrated current prototype bugs here.
~~~

### GLM 5.3 Flash — Architecture and integration

[Job 135781797995](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44586794355/job/135781797995)

- Exact requested model: glm-5.3-flash lens: integration-contract prompt_bytes: 47064 sha256: ccf5f4d65267e26c9ae007f6df8cd010e78df3bf7289496609122dea39f20b95
- Model: glm-5.3-flash Exit: 0 Report bytes: 1985 Accepted: True Report SHA256: 0a03b0f5c5882d30c8b07d212669ccf6c219bf02558b8b6f6f8d51a42812eaa5

~~~text
Reviewer attempted inspection, but command execution was blocked by this environment, so no tests or rebuilds were run.

**Findings**
- **HIGH** — `scripts/knowledge_index/indexer.py:121` / `scripts/knowledge_index/indexer.py:155`: Registered-ID reservation is enforced for Markdown `declared_id`, but appended JSONL nodes are not checked against `registered_ids` within the shown flow.
- **Mechanism:** In a partial build excluding the registered owner, a JSONL node can claim the registered stable ID before validation; the registry-derived reservation context is not available to `validate()`.
- **Negative test:** Register `id=x`, omit its Markdown owner, include JSONL `{"record_type":"node","id":"x",...}`; expected build failure: reframing via a negative example where the model overtrusted `_aliases`; expected build failure: substring collision does not prove permission boundary. Use: include the registry-derived权威; expected build failure: substring collision does nót imply same source. Assert edge absent. expected: edge absent; expected build failure only if substring matching fabricates edge.
- **Impact:** False stable identity under partial index; downstream edges can point to injected node.
- **Confidence:** High from supplied source; untested here.
- **MEDIUM** — `scripts/knowledge_index/indexer.py`:82:82: Namespace parsing is shape-based rather than identity-bound. Could accept malformed namespace strings that pass `github:` / slash counts.
- **Negative test:** namespace `github:owner repo`; assert rejected as malformed URI namespace.
- **Impact:** Invalid source URI surface. Low exploitability in local prototype.
- **Confidence:** Medium.

**Known unimplemented gates—not prototype failures:** ACL verification, revocation, cross-workspace connector, maintained service, immutable permalinks.

**Untested areas:** exports, HTML/CSP, validator and workflow red-green tests. NO MATERIAL FINDINGS beyond these bounded-scope items.
~~~
