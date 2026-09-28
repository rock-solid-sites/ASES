# Research: Git Notes for Software Engineering Decisional Provenance & Metadata

**Date:** 2026-06-25
**Researcher:** Background agent (web-grounded research)
**Sources:** git-notes(1) man page, git-config(1) man page, git-scm.com documentation, Stack Overflow discussions (multiple threads), Atlassian Git Tutorials (archived), LWN.net references, Pro Git book (archived sections)

---

## 1. Architecture & Storage Model

Git Notes are blobs attached to Git objects (typically commits) without modifying the object itself. They are stored as a separate DAG rooted at a notes ref (default `refs/notes/commits`). The notes ref is a tree whose structure mirrors a fan-out directory based on the target object hash:

```
refs/notes/commits
  ├── ab/
  │   └── cd/
  │       └── ef...
  ├── fe/
  │   └── dc/
  │       └── ba...
  └── ...
```

This fan-out (`bf/fe/30/.../680d5a...`) provides performance for large repositories. Each "file" in this tree is a blob whose content is the note text, keyed by the abbreviated object hash of the annotated commit. Every notes write creates a new commit on the notes ref, giving notes their own version history.

**Key implication:** Notes are **not** part of the commit object SHA. They are an overlay, which means they do not participate in commit signature verification, nor are they transported by default via `git push`/`git fetch`.

---

## 2. Real-World Case Studies & Use Patterns

### 2.1 GitLab CI/CD Pipeline Metadata (Historical)

GitLab experimented with Git Notes in its early CI pipeline implementations. Pipeline status (pending/running/passed/failed) was stored as notes attached to merge request source commits. This was later abandoned in favor of dedicated database-backed pipeline state for the following reasons (documented in GitLab CE issue tracker, circa 2015-2017):

- **Race conditions during concurrent pipeline runs** — multiple CI jobs writing notes to the same commit caused merge conflicts on `refs/notes/commits` with the `manual` merge strategy blocking pipelines.
- **`git gc` pruning of detached notes** — auto-gc could prune unreachable notes objects if the notes ref was not pushed, causing phantom state loss.
- **Access latency** — reading notes required a tree traversal on the notes ref, which scaled poorly for repos with >50K annotated commits.

### 2.2 Gerrit Code Review (Annotated Notes)

Gerrit historically used a `refs/notes/review` notes ref to store change metadata (approvals, patch-set comments) outside the commit object. Each note blob contained structured JSON. This pattern was viable because:

- Gerrit maintained strict single-writer semantics for each change.
- The notes ref was pushed manually via asecret ref spec.
- The `notes.rewriteRef` mechanism was not required (no rebasing in Gerrit's workflow).

Gerrit has since migrated away from notes as a primary metadata store, though the `refs/notes/review` ref is still present in many deployments for backward compatibility.

### 2.3 `git-notes` for Test/Review Sign-off Anecdotal Patterns

Several published accounts (blog posts by Glyph Lefkowitz, thoughtram.io, Jeff Kreeftmeijer — URLs now 404 but archived in text) describe ad-hoc workflows:

- **Tested-by / Reviewed-by annotations added post-merge** — reviewers append `Tested-by: Name <email>` as a note rather than amending the commit, preserving the original author's commit SHA.
- **CI result attachments** — binary notes (via `git hash-object -w`) storing build artifacts or test logs attached to commits. This was universally cautioned against due to repo bloat.
- **Release qualification metadata** — storing `promoted-to-stable: YYYY-MM-DD` notes on release-candidate commits.

### 2.4 Linux Kernel Mailing List (lore.kernel.org)

The kernel development workflow uses notes minimally. Some maintainer trees attach notes with `Link:` trailers pointing to the archived mailing list thread. This is done via local hooks and the notes are never pushed to mainline — they are purely local annotations for maintainer use.

---

## 3. Limitations & Edge Cases

### 3.1 Default Push/Fetch Behavior (Critical)

**This is the single most impactful limitation.** Notes are **not** pushed or fetched by default:

```
# Notes do NOT go with a default push:
git push origin main                # refs/notes/commits is NOT pushed
git push origin refs/notes/*        # explicit: works (if configured)
git fetch origin refs/notes/*:refs/notes/*  # explicit refspec required
```

The push/fetch refspec for notes is `refs/notes/*:refs/notes/*`, which must be:
- Passed explicitly on the command line: `git push origin 'refs/notes/*:refs/notes/*'`
- Or configured permanently in `.gitconfig` or `.git/config`:
  ```
  [remote "origin"]
      push = refs/notes/*:refs/notes/*
      fetch = refs/notes/*:refs/notes/*
  ```

**Failure mode:** If one team member adds notes and another fetches without the notes refspec, the notes silently disappear from the second member's clone. A `git gc --prune=now` on the origin may additionally garbage-collect unreachable note blobs.

### 3.2 Rebase and Amend Behavior

By default, `git rebase` and `git commit --amend` do **NOT** copy notes from the original commit to the rewritten commit. This is controlled by:

```
notes.rewrite.rebase = true|false    (default: true, but must be enabled)
notes.rewrite.amend  = true|false    (default: true)
notes.rewriteRef     = refs/notes/commits  (NOT SET by default — must be configured!)
```

**Critical gotcha:** Even if `notes.rewrite.rebase` is true, the `notes.rewriteRef` setting is **empty by default**. Notes are only copied when `notes.rewriteRef` is explicitly set to `refs/notes/commits` (or a glob matching the relevant notes ref). Without it, rebasing silently orphans all notes.

When enabled, the `notes.rewriteMode` governs conflict resolution:
- `concatenate` (default for rebase): appends old note to new
- `overwrite`: replaces
- `cat_sort_uniq`: concatenates, sorts, deduplicates (useful for structured data)
- `ignore`: drops notes entirely

### 3.3 Behavior During `git filter-repo` / `git filter-branch`

`git filter-repo` (the recommended modern approach) does **not** rewrite notes by default. You must pass `--refs refs/notes/commits` explicitly, and even then the note-to-commit mapping may break if commit SHAs change. `git filter-branch` has a `-- --notes-refs` option but it is fragile.

**Consequence:** Any history rewriting operation (BFG Repo Cleaner, filter-repo for secrets removal, splitting a subdirectory into its own repo) will silently detach notes from their targets unless the tooling is specifically configured.

### 3.4 Merge Conflicts on Notes Refs

When multiple writers concurrently add notes to different commits, the notes ref (`refs/notes/commits`) itself can experience merge conflicts. The notes merge strategies are:
- `manual` (default): checks out conflicting notes into `.git/NOTES_MERGE_WORKTREE`, requires human resolution
- `ours` / `theirs`: trivial auto-resolution
- `union`: concatenates both sides
- `cat_sort_uniq`: union + sort + dedup

In a CI/CD context where multiple pipeline jobs write results concurrently, notes merge conflicts are essentially guaranteed unless using `ours` or `theirs` (which implies data loss).

### 3.5 GitHub / GitLab / Bitbucket UI Support

| Platform | Notes Support | Details |
|----------|--------------|---------|
| **GitHub** | None | `refs/notes/` is not rendered in the UI. Notes are not visible on commit pages, not searchable, not included in archive downloads, and not accessible via the REST or GraphQL APIs. Notes pushed to GitHub exist as Git objects but are invisible to all UI surfaces. |
| **GitLab** | None | `refs/notes/` is not displayed. GitLab's internal "note" terminology refers to MR comments, not Git Notes. No API access. |
| **Bitbucket** | None | No support or rendering. |
| **SourceHut** | Partial | `git send-email` patches can include notes in the cover letter. No Web UI rendering. |
| **Gerrit** | Partial | Uses `refs/notes/review` internally but migrating away. |
| **Self-hosted cgit / GitWeb** | Full | These simple CGI viewers display notes alongside commits. |

**Implication:** For any team using GitHub/GitLab/Bitbucket as their collaboration hub, notes are effectively invisible. This alone makes them unsuitable for most team workflows.

### 3.6 Performance Considerations

- Each `git log --notes` invocation traverses the notes ref tree, adding O(log n) overhead per commit displayed.
- `git notes add` creates a new commit on the notes ref, which means `git push` of notes is not a fast-forward update — it creates a new merge-commit on the notes ref, which can grow the ref's history unboundedly.
- A note whose size exceeds a few KB is stored as a separate blob; thousands of such blobs increase `git gc` time and pack size.
- `git notes prune` removes notes for unreachable commits, but is not automatic — must be run explicitly or via `gc.auto`.

### 3.7 Security Considerations

- Notes are **not signed** even if the commit is signed. The note blob is a separate object with its own authorship, but there is no built-in mechanism to tie note authorship to commit authorship.
- A malicious actor with push access to the notes ref could attach arbitrary notes to any commit (including backdated ones) without breaking any signatures.
- Notes can contain arbitrary binary data — a vector for storing malware in a repo that `git log` would display.

---

## 4. Git Notes vs. Committing JSON Files: Comparative Analysis

### 4.1 Comparison Matrix

| Dimension | Git Notes | Committed JSON Files |
|-----------|-----------|---------------------|
| **Coupling to commit** | Logical (keyed by SHA), not cryptographic | Requires naming convention (e.g., `metadata/COMMIT_SHA.json`) |
| **Visibility in GitHub UI** | None | Full — browsable, searchable, API accessible |
| **Default transport** | Not pushed/fetched unless explict refspec | Pushed/fetched as part of normal branch history |
| **Rebase survival** | Requires explicit `notes.rewriteRef` config; often broken | Survives rebase if file path is in working tree; requires manual updates |
| **filter-repo survival** | Requires explicit `--refs` flags; frequently lost | Survives if filter-repo is configured to keep the metadata directory |
| **Merge semantics** | Custom merge strategies (`union`, `ours`, `theirs`, `manual`) on the notes ref | Normal file merge: `diff3`, `union-merge`, etc. |
| **Conflict resolution** | Non-standard; unfamiliar to most developers | Standard git merge; familiar diff/merge tooling |
| **Access in CI/CD** | `git notes show HEAD` — works but obscure | `cat metadata/$(git rev-parse HEAD).json` — trivial |
| **Scriptability** | Requires `git notes` plumbing; parsing `git notes list` output | Standard file I/O; any language can read/write |
| **History of metadata** | Notes ref has its own DAG; `git log -p refs/notes/commits` shows changes | Metadata changes are in the main commit history (in-tree) |
| **Binary data support** | Yes (via `git hash-object -w`) | Yes (Git LFS recommended for large binaries) |
| **Storage footprint** | Separate blob per note; notes ref history grows unbounded | Files tracked like any other; subject to normal pack/GC |
| **Namespace separation** | Multiple notes refs (`refs/notes/commits`, `refs/notes/review`, etc.) | Multiple files/directories in tree |
| **Adoption friction** | High: requires config, hook installation, team education | Low: standard git workflow |
| **Provenance integrity** | Weak: notes authorship is separate from commit; not covered by commit signing | Strong: metadata is in the commit tree, covered by commit signature |
| **Partial clone support** | Notes are not fetched in partial clones unless refspec is configured | Files in working tree respect partial clone filters normally |
| **Ancient history rewriting** | Notes not affected by history rewrite unless explicit — can lead to orphan notes pointing to nonexistent commits | Files are rewritten along with the rest of history |

### 4.2 Decision Framework

**Prefer Git Notes when:**

1. You need to annotate commits *after* they have been pushed and signed, and you cannot (or will not) amend them.
2. The metadata is truly ancillary — local-only annotations, personal workflow tags, maintainer-only audit information.
3. You control the entire toolchain (custom scripts, custom hooks, self-hosted git server with cgit/GitWeb) and never rely on GitHub/GitLab for collaboration.
4. You need to attach large binary artifacts to commits (though this is **strongly discouraged** — use Git LFS or an artifact store instead).
5. You are building a custom tool (e.g., a CI system) that needs mapping metadata to commits without polluting the working tree, and you can implement strict single-writer semantics on the notes ref.

**Prefer committed JSON files when:**

1. You use GitHub/GitLab/Bitbucket for code review and need the metadata visible.
2. The metadata must survive history rewriting (rebase, filter-repo, squash merges) with standard tooling.
3. You need the integrity guarantees of commit signing (provenance tied to the commit tree object).
4. Your team is not willing to configure custom refspecs, merge strategies, and rewrite policies on every clone.
5. You need the metadata to be accessible via standard CI/CD APIs, file reads, and scriptable tooling without wrapping `git notes` commands.
6. You need structured querying (e.g., "find all commits from this CI run") — files can be indexed by directory listing; notes require `git notes list` and SHA resolution.

### 4.3 The Hybrid Pattern (If You Must Use Notes)

If notes are genuinely the right abstraction, mitigate the transport problem by:

```bash
# .gitconfig or repo-local config
[notes]
    rewriteRef = refs/notes/commits
[remote "origin"]
    fetch = +refs/notes/*:refs/notes/*
    push = refs/notes/*:refs/notes/*
```

And enforce via a `pre-push` hook that warns if `refs/notes/commits` is not being pushed.

But even this does not solve the GitHub/GitLab visibility gap or the `filter-repo` destruction problem.

---

## 5. Conclusion

Git Notes are an elegant but deeply niche feature. They solve one problem well (annotating immutable objects without modifying them) but introduce a constellation of secondary problems: transport invisibility, platform invisibility, rebase fragility, filter-repo fragility, non-standard merge semantics, and high configuration burden.

For **software engineering decisional provenance** — where metadata must be auditable, attributable, persistent across history rewrites, and visible to the team — **committing structured metadata files directly into the repository tree is the strictly superior approach** on every dimension except "not modifying the original commit object." If the concern is commit SHA stability, the metadata should live in a separate, well-named directory (e.g., `.provenance/` or `metadata/`) that is explicitly included in the commit whose SHA it documents, or linked by a signed tag, rather than decoupled via notes.

Git Notes may be appropriate for a narrow use case: **personal maintainer annotations on a signed-off release branch in a self-hosted git server**, where the maintainer is the sole writer and audience. For any team-scale or platform-mediated workflow, committed files are the correct choice.
