# ASES real-code property-engine pilot (experimental)

**Object:** the existing Rust `resource-control` crate and its SQLite-backed `Store`, on branch `research/phase-ii-native-identity-lifetime-cloud-20261112`, not a fabricated Kernel-0.
Changes are limited to test/dev dependencies and CI; no runtime implementation is altered.

## Source-grounded claims
The actual `Store::reserve`, `Store::balances`, `Store::event_log` and `Store::open` are exercised. Generated histories contain 0–19 unique reservation proposals for one fresh 100-unit meter, each claiming 1–80 units. The fixture has 64 available parallel slots and all timestamp/entitlement observations are locally fresh. The independent oracle is plain integer accounting, not a call to the Store's internal admission algorithm.

Properties:
1. The first admission succeeds iff remaining allowance is at least the requested amount (within this fixture's stated limits).
2. A rejection cannot change allowance or append a durable admission event.
3. Exact-ID exact-payload replays must not consume additional resource or append events.
4. A stale catalog version must not admit or mutate state.
5. Balances and reservations must survive reopening the actual SQLite file.
6. After reopening, cancelling each accepted unlaunched reservation frees exactly its outstanding allowance; replaying cancellation is idempotent and cannot append duplicate terminal events.

The second phase iterates over accepted reservations in reverse admission order. This is a **bounded terminal lifecycle** history, not arbitrary operation interleavings, real process termination or host-crash recovery.

Two harnesses use the same oracle and source: `proptest =1.12.0` and `hegeltest =0.53.1`, 120 generated cases each. A green result is a finite checked sample, NOT proof of provider billing, full Kernel-0, hostile process confinement, crash consistency, remote execution or correct interleavings under concurrency. Input generators and shrinking algorithms are not identical across engines.

## Run
From `resource-control`: `cargo test --test resource_property_proptest -- --nocapture` and `cargo test --test resource_property_hegel -- --nocapture`. Also run existing `cargo test --test control` for regression evidence. The dedicated GitHub Actions workflow captures compile logs, test logs, resolved Cargo.lock, test versions and run metadata. Zero findings is a legitimate result; do not demand a bug to call the trial useful.

Source: `docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md`. ASES method remains provisional pending cross-project interpretation and independent review.
