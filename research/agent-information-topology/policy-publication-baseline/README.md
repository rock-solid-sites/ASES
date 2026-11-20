# Agent information topology — policy-publication baseline

**Authority: Experimental, not an active ASES policy or approved runtime component.**

This is a **coordinator-authored deterministic baseline**, not the independent Luna/Codex execution assigned to WNASES-18. Codex Cloud reported that the selected execution environment was neither ready nor starting, and no usable execution environment was available. No Luna code, tests, branch or draft PR were produced.

**Source baseline:** ASES main commit 91817f642b1ca88c58df4bb5191d092ec2d2201d.

## Purpose

The prototype renders selected upstream policy rules into one effective project-local instruction file, with four behaviors:

- Verbatim import of approved upstream text
- Parameterized import with explicitly supplied values
- Local extension that does not shadow upstream rule IDs
- Explicit replacement of upstream text, which is **physically absent** from the published output rather than labeled superseded

It is intentionally a small standard-library script, not a new service, registry, model launcher, Resource Solver or cross-repository synchronization job.

## Run locally

The script is publish.py; tests are test_publish.py. Both require only Python 3 standard library.

The upstream JSON file uses schema ases-policy-source-v1, containing a rules array of ID/text entries. A consumer manifest uses schema ases-policy-consumer-v1, source_sha256 of the exact upstream file bytes, imports, and optional extensions.

Run publish.py with --source upstream.json, --manifest consumer.json and --output AGENTS.md, supplying exactly one of --update or --check.

The update command generates an effective file only when the upstream source SHA256 matches the declared pin. Check mode is read-only and fails if the generated file differs or is absent. Nothing silently adopts a new upstream revision.

To run the tests, invoke Python unittest discovery against this directory. The GitHub Actions workflow agent-policy-publication-baseline.yml runs the same tests on the disposable experimental branch and retains test evidence in the run summary.

## Tests

The 13 tests exercise both synthetic project variants, effective replacement without original text, deterministic generation, check/update behavior, tampering, source drift, duplicate IDs and imports, shadowing, invalid substitutions, missing upstream rules, blank overrides and unknown schema/modes.

## Limits

No active AGENTS.md, .opencode, .claude or consumer repository was modified. No model was invoked for these tests. No cross-repository rollout, approval workflow, nested instruction precedence, security boundary or task-quality measurement is claimed.

This deterministic baseline is separate from WNASES-18's still-blocked independent Codex agent experiment and from WNASES-19's independent OpenCode exposure investigation. If those independent tests resume, do not provide this code to their agents before first-pass findings are frozen.

The next design decision is whether simple hash-pinned generated instructions provide sufficient value to justify future distribution, and which actual harness instruction-loading paths must be removed to eliminate obsolete influence.
