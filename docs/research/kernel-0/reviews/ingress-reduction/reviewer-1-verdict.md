supported

Exact domain established: all legal invariant-satisfying states per profile (independent 8,449 / coupled 6,337 / exclusive 1,921, including 19 unreachable-but-legal states) × the 148 authentic catalog templates — 1,250,452 + 937,876 + 284,308 = 2,472,636 oracle/RTL comparisons, all PASS in frozen results.json and independently reproduced for integrity, universal mapping, and the independent profile (1,250,452 comparisons, 943 cells).

Also established within the same bounded scope: universal input mapping over all 2^60 lane/payload combinations (SAT SUCCESS), raw attack domain of 2,048 payloads × 5 lanes per profile with 0 stale-lane commits, 206 clocked cycles per profile (618 total), 3 boundary proofs, 3 synthesis-equivalence proofs (132/132 cells), 5 detected mutants with counterexample assignments, 22 authoritative state bits / 24 total registers, combinational-only selector reusing unchanged kernel0.v (direct-rtl diff vs c03bf1c4 empty, manifest PASS, baseline rerun 4,945,272 vectors PASS).

Caller-supplied actor label and authentic verdict inputs are absent from the new 60-bit lane interface (fixed_ingress.v:5-27: actor from one-hot lane, authentic hardwired 1); false-authenticity variants have no new-interface representation by design and remain covered only by the baseline rerun. Physical lane isolation and async/timing behavior are stated premises, not proved — consistent with the claimed protected-lane and synchronous assumptions. Artifact unmodified (worktree clean at ac9d128e).

Build · Muse Spark 1.3 Free · OpenCode Zen · tools unverified (unprobed) · free stale 6.2d · 38.9s · 109.8 tok/s
