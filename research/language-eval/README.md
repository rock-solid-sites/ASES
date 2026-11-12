# Rust–Haskell provider-admission language evaluation (research only)

This experiment measures *implementations*, not architectures. Rust and Haskell are equal candidates; neither is the predetermined production language. Python is used for test orchestration only. No provider APIs, paid resources or real account data are involved.

## Contract

Input: a JSON array of independent hypothetical admission requests (see `cases.json`).
Output: one array of `{id,accepted,reason,charge_cents}` in input order. Integer financial quantities use **cents**; `usage`/`included` are simulated chargeable units, not actual provider billing meters. `capacity`, `reserved` and `requested` are abstract discrete capacity units, not additive CPU reservations.

A candidate is admissible only if the provider is active, the account/product revision is verified, the observation is current, pricing is known, the requested capacity is positive and fits unreserved hard capacity, and all numeric fields are nonnegative.

For free and subscription modes, incremental charge = max(0, usage − included) × rate. For prepaid and postpaid, incremental charge = usage × rate. Paid charges require explicit opt-in. Prepaid additionally requires wallet ≥ charge + wallet_floor. Free overage, subscription overage and postpaid must satisfy charge + prior liability ≤ authorized spend_cap. Reject unknown modes and signed 64-bit arithmetic overflow. Denials report zero authorized charge and a stable reason code.

This is **an admission decision only**; it deliberately does not solve atomic concurrent reservations, external charging, billing resets, quantitative CPU contention, expiry, or ledger reconciliation. Those are later discriminators and must not be claimed tested by this slice.

## How to run

```sh
cargo build --manifest-path research/language-eval/rust/Cargo.toml
ghc -O0 -package aeson -odir /tmp/ases-ghc -hidir /tmp/ases-ghc -o /tmp/ases-admit-hs research/language-eval/haskell/Main.hs
python3 research/language-eval/compare.py --rust research/language-eval/rust/target/debug/ases-admit-rs --haskell /tmp/ases-admit-hs
python3 research/language-eval/wire_cases.py --rust research/language-eval/rust/target/debug/ases-admit-rs --haskell /tmp/ases-admit-hs
python3 research/language-eval/bench_repeats.py --rust research/language-eval/rust/target/debug/ases-admit-rs --haskell /tmp/ases-admit-hs
python3 research/language-eval/bench_kernel.py --rust research/language-eval/rust/target/debug/ases-admit-rs --haskell /tmp/ases-admit-hs --passes 240 --iterations 7
```

The harness checks a 24-case oracle, 1,000 deterministic generated cases, a separate Python oracle, a no-unauthorized-charge safety property, repeated deterministic output, and Rust/Haskell differential equivalence. The reference Python oracle is independent test code, **not production approval**.

## Observed results

The [2026-11-01 evidence report](RESULTS-2026-11-01.md) documents the first CI red-green correctness discoveries and independently executed GitLab development/optimized build and wire-format tests. The benchmark records cold and no-change warm compilation separately; no changed-source incremental compiler comparisons have been executed.

## Decomposing compute from transport and compile cost

**Computation-only probe:** Both binaries now support `--bench-core PASSES`. The program parses the identical JSON corpus *once*, then uses the exact admission decision function repeatedly while varying one bounded usage input, computing a strict numerical checksum rather than serializing one JSON object per decision. Native monotonic `core_ns` timing is recorded inside the process *after parsing and before checksum serialization*. The Python harness (`bench_kernel.py`) independently computes the checksum through the established oracle and repeats the measurement with warmups. This is not pure instruction counting: allocation, garbage collection, data types, and branch logic still affect results.

**End-to-end control:** `bench_repeats.py` still measures process launch, JSON parse, decisions, serialization and process exit. Its 12,300-case workload is different from the 1,025-case repeated compute probe; do **not** subtract their timings as though they were component measurements of a single identical run.

**Changed-source compile probe:** `rebuild_probe.py` modifies one real admission expression per language in a disposable CI checkout by inserting an explicit numeric type. The change preserves semantics and causes both compilers to rebuild their programs; collect cold/no-change/edited-build time and RSS separately for Rust development/release and Haskell -O0/-O2. This is only a **single-module expression edit**, not a large-project, transitive dependency, macro, or multi-module edit. It does not yet establish the benefit of Blaze or other compiler accelerators. Re-run differential and wire-format tests after the source edits to confirm unchanged behavior.

Read the result report for measured values rather than treating CI configuration as proof of success.

## CI and evidence

GitHub Actions builds/tests both variants on one runner and records compiler/runtime measurements, stdout, exit status, toolchain versions, machine details and raw test results in uploadable artifacts. GitLab is intended to independently replicate using the same pinned GitHub source revision. Shared runners are noisy: only compare runs on the same machine class and report uncertainty over repeated samples. A successful CI test does not prove provider-billing correctness or formal verification.

## Decision gates

Correctness first, including no unauthorized paid spend. Then measure cold/warm builds, developer iteration, peak memory, cold/warm runtime, footprint, verification effort, and solver ecosystem integration. Do not select a language based solely on a single synthetic workload. Study explicit state-based modeling as a *competing analytical lens*, not a requirement to adopt kernel-0 or any state-machine implementation. Tidepool composition only proceeds after baseline evidence.
