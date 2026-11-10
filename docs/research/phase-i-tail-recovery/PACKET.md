# Explicit interrupted-tail recovery under a verified published prefix

Frozen 2026-11-10. Parent retry `16e6460f`; native receipt F4 `9226cd4b`.
Reuse precedent: opt-in `recover_prefix` at `bacf8f7d`, also present in the
captured original run.py. Original managed F4 replay is strict and does not use
that simple-profile helper. This is an explicit **stronger selected profile**,
not an automatic change to original recovery or a general corruption repair.

## Question and exclusions

What can a retry-aware F4 sink do after a real new append writes only an
unterminated tail then fails? Native strict cold recovery refuses. A complete
newline-terminated local effect whose publication is missing must remain
retained and unresolved; it may never be truncated merely to match the witness.
An fsync exception after writing a complete row is not proof of noncommit.

Implement an explicit pre-start local recovery operation that holds the same
stable sink-writer lock. Only an append-only **new unterminated tail** is eligible.
Validate the entire complete prefix using the native managed transition replay
and retry duplicate-ID rules. Derive its exact authority/journal cut and freshly
ask the live witness to check it. Proceed only on exact typed root/nonce/cut
match. A supplied hash is not authority; the trusted current live witness and
current local journal are premises. Witness rollback/durability/authentication
remain unresolved; do not manufacture them.

Preserve the exact original bytes in a content-identified exclusive quarantine,
fsync it, prepare/fsync the validated prefix, then atomically select it via
same-filesystem replace. Keep crash gates at quarantine/prepared/selected. Never
discard a complete record; an invalid complete prefix, missing prefix, complete
unpublished effect or witness mismatch refuses unchanged. Ordinary startup is
still strict and never silently invokes this operation.

Reuse existing persistence helpers/mechanisms instead of inventing a second
journal or outbox. Disposable Python integration retains actual native F4
append/fsync/publication and the retry candidate. No physical power-loss or
exactly-once external-delivery claim. Same-root custody, stable lock inode,
append-only-tail fault class, all-writer participation and live witness truth
are explicit assumptions.

## Actual discriminators

- Instrument native os.write so one actual partial effect-row write succeeds,
  then a real OSError interrupts the loop. Keep raw bytes, 503 and native strict
  cold refusal. Explicit recovery selects only the previously published complete
  prefix, preserving quarantine. Cold retry can then accept the never-completed
  request once and exact further retry observes one event.
- Instrument os.fsync to fail after a complete new row is written. Local complete
  event persists; explicit tail recovery refuses it. No duplicate append.
- Real publication reply suppression: full published row is not a tail and no
  truncation occurs; ordinary retry observation still works.
- Live sink holds writer lock: explicit recovery refuses busy, changes no bytes.
- Actual kills before and after prefix selection: old tail or selected prefix
  recover consistently, quarantine remains exact; a second explicit invocation
  is safe (complete validated journal returns no-tail, never resets genesis).
- Invalid complete record plus tail, no newline prefix, mismatched witness cut,
  and a local acknowledged record later externally truncated all refuse. The
  latter is outside the supported fault class and should fail witness comparison.

Independent raw checks and altered controls. Preserve failed instrumentation
separately. No CI, review, host configuration, external target/provider, merge or
deployment; do not expand into a general recovery service.
