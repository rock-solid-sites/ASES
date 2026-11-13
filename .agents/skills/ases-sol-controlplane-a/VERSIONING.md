---
title: "Sol control-plane A — document authority and version register"
version: 0.3.6-experimental
status: experimental
authority: run-scoped
run_id: ASES-SOL-CTRL-A-20261113
---

# Document versioning and supersession

**Rule:** Every newly created or revised document in this experimental session package has a declared version, authority level and status. Never resolve a duplicate logical document/skill by filename, search rank, modified timestamp, or unverified “newer” intuition. Compare the declared identity, version, scope and supersession chain; preserve prior revisions through Git history or an explicit archive and report unresolved conflicts.

## Package documents (individually versioned)

| File | Document identity | Authority |
| --- | --- | --- |
| `SKILL.md` | `ases-sol-controlplane-a` | 0.3.2-experimental; run-scoped parent policy |
| `BRIEF.md` | session source index | 0.2.2-experimental; run-scoped |
| `PACKETS.md` | strategy-to-builder and verifier packet procedure | 0.3.1-experimental; run-scoped |
| `EVALUATION.md` | treatment A / historical baseline comparison | 0.2.0-experimental; run-scoped |
| `HANDOFF.md` | durable worker checkpoint protocol | 0.2.0-experimental; run-scoped |
| `LAUNCH.md` | fresh-session launch text | 0.3.6-experimental; run-scoped |
| `VERSIONING.md` | this resolution register | 0.3.6-experimental; run-scoped |
| `REVIEW-ROUTES.md` | external-family reviewer route proposal | 0.4.1-experimental; proposed-unverified |
| `PROVIDER-SELECTION.md` | ranked full-registry account selection | 0.3.1-experimental; ranked-preflight-required |

Documents are versioned independently; editing one does not silently increase the versions of unchanged files. `REVIEW-ROUTES.md` describes proposed routes, not completed live verification. `PROVIDER-SELECTION.md` selects from all recorded accounts and candidate/offer classes; none of its unverified model or sandbox routes is promoted to live.

The parent research branch's root `AGENTS.md` is `2026-11-13.1-experiment` and conditionally activates this run only by exact run ID. It supersedes the previous unversioned **branch source revision** `62b70f6ffcfa32a830026fd7a8b7a9ca3c465d3d` for the experiment only; it does not proclaim a new canonical version for `main`.

## Resolved duplicate logical skill

| Source | Current identity in experiment branch | Version | Status | Precedence |
| --- | --- | --- | --- | --- |
| `skills/prompt/SKILL.md` | `compact-prompt` | `0.5-draft` | current-draft | **current** |
| `skills/compact-prompt/SKILL.md` | `compact-prompt-legacy-v0-1` | `0.1-draft` | superseded | historical only |

Both files previously declared identical `name: compact-prompt`, although one is an older version. On this branch, the v0.1 file retains its historical body but declares a separate legacy identity and `superseded_by` pointer. The current v0.5 file declares `supersedes`. Workers use the exact **v0.5 path** from `PACKETS.md`, not a name-based selection of the old draft. This change is intentionally branch-scoped and is not yet a repository-wide migration.

A source document that was cited previously by path still exists at that path. A launcher that assumes `name` always equals the directory basename must be evaluated separately; the prior repository already had a v0.5 `compact-prompt` name under the `skills/prompt` directory. Do not claim that changed metadata proves Codex will expose the old or new skill until a worker checks actual discovery.

## Versioning rule for future work

1. New standalone documents: YAML frontmatter with `title` or `name`, `version`, `status`, and `authority`. For a revision, identify its prior revision or `supersedes` target and preserve prior text in Git.
2. Agent skills: a **unique** machine-readable `name` among simultaneously discoverable skills, with explicit version and supersession metadata. Do not publish two current skills under the same name. Retired skill content stays accessible with a distinct historical identity.
3. Resolve conflicts in this order: higher-level canonical contract; explicit task/run scope; declared unique identity plus authoritative supersession; semantic/content diff. A newer version does not automatically override a higher-authority canonical document.
4. If two candidate documents have no reliable version or supersession chain, leave the conflict **UNRESOLVED**, ask a cheap agent to compare meanings and provenance, and report the decision to the operator. Never silently drop either.
5. The repo contains many existing historical documents outside this package. This limited PR versions the documents it changes and resolves the **known** duplicate compact-prompt skill. A separate repository-wide inventory must find remaining collisions and unversioned active documents before claiming full compliance.

## Verification authority

Sol is the high-level **verification owner**, not a command runner. It freezes requirements before builders start, receives short **independent verifier Luna** findings (separate agent and test derivation, blinded to the builder's prediction as feasible), compares both against the frozen obligations, and decides `ACCEPT` / `REVISE` / `UNVERIFIED`. Green builder-only tests do not qualify as accepted. A same-family verifier is not a cross-family adversarial review.

## Sources and status

Repo research branch: `research/sol-controlplane-a-20261113`. Draft [PR #45](https://github.com/rock-solid-sites/ASES/pull/45). New session experiment [ASES-8](Work Notes issue ASES-8). These are experimental instructions only. No code-level component contracts, production deployment or main branch were changed.
