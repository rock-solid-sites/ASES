# Reviewer 1 prompt — correspondence and preservation

Independently review the frozen ingress-reduction artifact at commit `ac9d128e984dddecbbf08c810a9cfc53e9754ac9`.

Determine whether this claim is true:

The fixed protected-lane realization preserves the bounded Kernel-0 transition behavior of the frozen `c03bf1c470e54f51c299cb3347c547eeeae0e5ce` baseline while removing the caller-supplied actor label and authenticity verdict, under the stated protected-lane and synchronous realization assumptions.

Use only the frozen artifact and its governing sources/evidence. Inspect or execute the implementation and verification machinery as needed. Do not modify the artifact.

Return `supported`, `falsified`, or `not established`. If not supported, give the smallest concrete semantic mismatch or missing check. State the exact domain you established or failed to establish.
