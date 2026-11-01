# Solver selection correction — 2026-11-01

**Decision: Pumpkin is a candidate, not the selected ASES solver. No Pumpkin adapter is approved yet.** Earlier references to a Pumpkin-first implementation sequence are superseded.

First implement an authoritative typed WorkGraph/EnvironmentSnapshot, an independent feasibility gate, and a deterministic scheduling baseline. Evaluate specialized Rust scheduling, Pumpkin, Rust-native optimization alternatives, and external reference solvers using the same validated inputs. Compare solution quality, cold-start latency, peak RSS, memory-safety and maintenance costs. Historical MiniZinc results are retained as reference only.

Feasibility has three gates: input preflight, offline independent schedule acceptance, and atomic dispatch-time resource admission. The current Python reference validator is **not** a production admission controller. It must not be treated as security or capacity enforcement.

**Acceptance before selecting engine:** common 18-stage TripN fixture with explicit S-tier resource assumptions; 12/30/60 stage cases; frozen completed work; outages and quotas; independently checked feasible outputs; known optimum on small instances; actual process memory and timing; documented language/runtime risk.

Environment note: Rust toolchain unavailable in the local execution container on 2026-11-01. A Python standard-library prototype can be executed here; Rust build results must be obtained elsewhere and reported as such.

Source decisions: docs/research/Independent Feasibility Gate Requirements 2026-11-01.md and docs/research/ASES Solver Capabilities and Rust Architecture Review 2026-11-01.md.
