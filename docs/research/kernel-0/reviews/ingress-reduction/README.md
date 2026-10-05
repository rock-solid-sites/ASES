# Ingress-reduction independent review provenance

This directory preserves the two independent post-build review prompts and returned verdicts for the frozen ingress-reduction artifact.

## Frozen target

Ingress-reduction artifact: `ac9d128e984dddecbbf08c810a9cfc53e9754ac9`.

Direct-RTL baseline: `c03bf1c470e54f51c299cb3347c547eeeae0e5ce`.

The ingress artifact was produced by Astra. The two review runs were executed in separate contexts using different non-Astra model families. Peer outputs were not supplied between reviewers.

## Contents

- `reviewer-1-prompt.md` — correspondence/preservation claim.
- `reviewer-1-verdict.md` — Muse Spark 1.3 output as supplied.
- `reviewer-2-prompt.md` — reduction/hidden-assumption claim.
- `reviewer-2-verdict.md` — Space Bunny output as supplied.

The verdict files are preserved as supplied, including tool/runtime annotations.

The canonical synthesis is [Kernel-0 Ingress Reduction Independent Review](../../Kernel-0-Ingress-Reduction-Independent-Review.md).

This directory is provenance, not semantic authority.
