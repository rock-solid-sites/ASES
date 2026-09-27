---
name: cgrmcp-repository-research
version: 1.0
description: Research public Git repositories through cgrmcp. Use when the task is to understand, trace, compare, or inspect a public GitHub repository structurally without treating it as a local development workspace. Prefer repo_explore for code understanding and repo_read only for unsupported/non-structural files or narrow last-mile source evidence.
---

# cgrmcp Repository Research

Use cgrmcp as a read-only repository-research service. It opens public HTTPS Git repositories as immutable commit-pinned snapshots, indexes supported source with CodeGraph, and exposes bounded structural exploration plus bounded raw-file fallback.

## Core workflow

1. **Open the repository**
   - Call `repo_open(url, ref?)` with the canonical public HTTPS GitHub URL.
   - Omit `ref` to use remote HEAD, or supply a branch/tag.
   - If supplying a commit SHA, use the full 40-hex SHA. Do not shorten it.
   - Preserve the returned `snapshot_id` and exact commit.
   - If state is `indexing`, poll the same snapshot with `repo_status` or repeat the same `repo_open` call until it becomes `ready` or `failed`.

2. **Check coverage**
   - Call `repo_status(snapshot_id)` before making strong completeness claims.
   - Treat coverage and warnings as evidence about what CodeGraph could structurally inspect.
   - `partial-coverage` means absence from structural results is not proof of absence from the repository.
   - `no-indexable-files` means structural exploration is not useful; use `repo_read` for the relevant files.

3. **Explore structure first**
   - Use `repo_explore(snapshot_id, query, max_files?)` for architecture, symbols, relationships, call paths, public APIs, ownership boundaries, execution flow, blast radius, and similar code-understanding questions.
   - Start with the default/small file budget. Increase `max_files` only when the first result shows the question genuinely spans more files.
   - Prefer one well-scoped natural-language structural question over several speculative low-level queries.
   - Treat the returned source blocks as already-read evidence; do not immediately re-read the same files with `repo_read`.

4. **Use raw reads narrowly**
   - Use `repo_read(snapshot_id, path, range)` for:
     - files CodeGraph reports as unsupported/non-structural;
     - exact configuration/docs/script details needed to resolve a remaining question;
     - narrow source confirmation not supplied by `repo_explore`.
   - Keep ranges small. Do not use repo_read to recreate broad grep/read exploration.
   - Paths are repository-relative only. Never attempt arbitrary VPS/local filesystem access.

## Research semantics

A cgrmcp snapshot is a research object, not a working checkout.

- Do not assume local branches, uncommitted changes, build artifacts, or developer state are represented.
- Record the exact commit when conclusions depend on repository version.
- Reopening the same URL+commit may reuse the existing immutable snapshot.
- A changed upstream repository requires a newly resolved commit/snapshot; do not treat an old snapshot as current.

## Evidence discipline

Distinguish:
- **structural facts** directly returned by CodeGraph;
- **source facts** returned verbatim by repo_explore/repo_read;
- **semantic conclusions** inferred from those facts;
- **coverage uncertainty** reported by repo_status.

Do not convert partial coverage into a claim of repository-wide absence. If an unsupported file type could materially change the answer, inspect the specific candidate with repo_read.

For repository comparisons, open each repository independently, record both commit SHAs, ask parallel/comparable structural questions, and compare the returned evidence rather than assuming equivalent terminology implies equivalent architecture.

## Failure handling

- `ref_not_found`: verify the branch/tag or resolve and retry with a full 40-hex SHA.
- `invalid_url`: use a supported public HTTPS Git URL; do not weaken the import policy.
- `read_rejected`: treat traversal, absolute path, symlink, binary, oversize, or protected-path rejection as an enforced containment boundary, not something to bypass.
- Failed/indexing snapshots should be reported from repo_status rather than papered over with unrelated web/source guesses.
- If cgrmcp cannot cover material repository content, state that limitation and use another appropriate source only for the missing evidence.

## When not to use cgrmcp

Do not use cgrmcp as the primary tool for:
- editing a repository;
- inspecting local uncommitted workspace state;
- running builds/tests;
- private repositories not supported by the service;
- generic web research unrelated to repository structure.

For those tasks, use the appropriate workspace, GitHub, or web tooling instead.
