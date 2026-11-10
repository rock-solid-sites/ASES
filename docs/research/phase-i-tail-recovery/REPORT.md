# Explicit verified-prefix tail recovery — result

## Finding

The selected operation recovers the bounded append-only partial-row failure
when the locally replayed complete prefix exactly matches the current live
witness cut. The operation runs while holding the native stable
`sink-writer.lock`, validates the prefix through managed transition replay and
the retry request-ID index, then performs a fresh typed `/check`. It saves the
full original bytes to an exclusive content-addressed quarantine and fsyncs
that file, writes and fsyncs the prefix, and selects it with same-filesystem
replace. Ordinary `recover` startup stays strict; tail recovery requires the
separate `recover-tail` invocation.

## Observed native outcomes

The probe drove the actual managed F4 append implementation and intercepted
the journal syscalls in its child process. A partial `os.write` completed for
part of an `effect_accepted` row and then raised `OSError`. The caller received
503, ordinary recovery refused without changing the journal, and explicit
recovery selected only the previously witnessed complete prefix. The
quarantine matched the original bytes exactly. A later fresh retry accepted
one event, and an exact retry observed that same event sequence.

In the separate fsync control, the full newline-terminated effect row reached
the journal before `os.fsync` raised `OSError`. Ordinary recovery preserved the
row and refused because its cut did not match the witness. Explicit tail
recovery made the same refusal, with no quarantine or truncation. This is the
key negative discriminator: a complete local record remains unresolved when
publication is absent, even if fsync reported failure.

Recovery was killed at the quarantine, prepared-prefix and selected-prefix
gates. Each subsequent explicit invocation reached a ready sink, retained an
exact quarantine, and ended with the validated prefix selected. A concurrent
writer caused refusal without changing the journal; its busy response named
the same lock device and inode as the live writer. Invalid complete-prefix plus
tail, no complete prefix, a tail whose validated cut disagreed with the
witness, and truncation of an acknowledged record all refused unchanged.

## Evidence and limits

`run.py` records the native process histories and original syscall-fault
outcomes in `evidence/final/raw.json`. `check.py` independently checks that raw
evidence and pinned source hashes without importing candidate or recovery
code. `check_mutations.py` changes five controls and confirms the checker
rejects each altered claim. Both checker outputs are stored beside the raw
evidence.

This was a disposable local software fixture. It does not test physical power
loss, filesystem/controller behavior, witness rollback or authentication,
multiple hosts, writers that ignore the stable lock, or arbitrary corruption.
The recovery premise remains that the supplied live witness and same-root
journal are the trusted current authorities. The input is bounded by the
native 64 KiB journal limit and the journal path must be the direct child of
the supplied trusted test root.

The result supports only explicit recovery of a new unterminated append tail.
It does not support dropping complete records to obtain witness agreement or
claim general crash durability or exactly-once external delivery.
