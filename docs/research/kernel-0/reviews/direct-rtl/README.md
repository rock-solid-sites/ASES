# Direct RTL independent review provenance

This directory preserves the post-build review inputs and returned verdict aggregates for the frozen Kernel-0 direct RTL artifact.

## Frozen target

Artifact commit: `c03bf1c470e54f51c299cb3347c547eeeae0e5ce`.

The artifact was produced by Astra. Formal review evidence was obtained from separate model families and separate reviewer contexts. Peer outputs were withheld during the review rounds. The self-contained review bundles were supplied outside the repository; they are intentionally not committed here.

## Contents

- `claim-a-prompt.md` — exact Claim A reviewer prompt.
- `claim-a-verdicts.md` — aggregate reviewer output supplied after the Claim A bundle review.
- `claim-b-prompt.md` — exact Claim B reviewer prompt.
- `claim-b-verdicts.md` — aggregate reviewer output supplied after the Claim B verification-apparatus review.

The verdict aggregates are preserved as supplied. Some sections lack an explicit reviewer label or contain reviewer progress text; this record does not infer missing provenance.

## Interpretation

The canonical synthesis is [Kernel-0 Direct RTL Independent Review](../../Kernel-0-Direct-RTL-Independent-Review.md). It distinguishes raw reviewer verdicts from the final evidence assessment and records the subsequent verifier-integrity hardening and reproduction run.

This directory is provenance, not semantic authority.
