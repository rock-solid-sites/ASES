# Provisional environment configuration and contention model — 2026-11-01

**Status:** research design correction, not implemented or validated in the existing SQLite gate.

An execution environment is a provider-backed product with an enumerated set of supported configurations. CPU and RAM are properties of the selected configuration, **not independently purchased resource buckets**. An environment can be resized only to configurations actually available for its product, account, region and current provider constraints. Some products may offer independently adjustable CPU and memory; in those cases the valid configuration set is the provider's allowed combinations, not an unrestricted Cartesian product.

Each configuration has CPU capacity, memory capacity, storage, any genuine concurrency caps, allowance/cost identity, and transition properties (time, cost, downtime, availability). Track actual selected configuration, allowed next configurations, and transition state. A configuration change is a scheduled state transition, not an instantaneous arbitrary numeric adjustment.

Multiple jobs may run concurrently in one environment. They share CPU, RAM, disk and I/O. **CPU oversubscription is not automatically invalid**: it changes predicted throughput, latency and completion times. Memory pressure is a safety and performance constraint, with explicit headroom for OS, editors, agents, caches and background services. Only enforce hard slot limits where they exist in the actual product or operating policy.

Admission should enforce actual hard constraints: allowed environment configuration and transitions; memory and storage safety thresholds; genuine provider concurrency limits; discrete non-fungible allowances; authorization and policy revision. Optimization should estimate workload-dependent CPU contention, memory pressure, I/O interference, slowdown, completion-time uncertainty and resizing overhead. Avoid treating synthetic per-job CPU values as guaranteed exclusive cores.

**Previously reported SQLite gate results:** 60/60 tests passed against an additive per-tick CPU reservation model. Those tests do **not** establish correctness for shared-CPU environments. Reclassify CPU-overlap rejection as a model mismatch, preserve RAM and real hard-limit protection, and write red tests for permitted concurrent CPU sharing before replacing the model.

## Required tests

1. Two CPU-intensive jobs may coexist on one configuration if memory and other hard limits permit; estimated completion time changes under contention.
2. Memory-heavy overlapping jobs exceeding safe available memory are rejected or require a supported larger configuration.
3. Unsupported CPU/RAM combination and forbidden resize transition are rejected.
4. Supported resize accounts for transition latency, interruption, and cost; reservations remain safe before/during/after transition.
5. Provider account, region, period and product identities cannot be substituted.
6. Two competing plans cannot each independently assume exclusive memory or an unperformed resize.
7. Changing available configurations or permissions invalidates stale admissions atomically.
8. Valid neighboring cases pass; targeted mutations kill each guard.

Provider-specific configuration catalogs, quotas and billing semantics require authoritative evidence. No production readiness claim until implementation and red–green tests are complete.
