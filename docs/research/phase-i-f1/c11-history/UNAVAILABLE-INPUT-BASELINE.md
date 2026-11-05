# Actual missing-new-input commitment boundary

Sourced66b281: holder without observations config starts on valid current archive,
actual read returns retained old pair, then accept-one commits new content despite
no new required tuple. Consumer receives no usable response; raw diagnostic current
one remains paired with old zero metadata/archive. Next recovery correctly refuses
that incompatible state before ready. Explicit new tuple positive ACKs/recovery pass.
8 actual owned children/max1, all reaped; source hashes verified at execution pin.
This is actual runtime unavailability after legitimate recovery, beyond startup type
checks, not merely malformed input or a product defect in original parent holder.

Next authorized repair, as preregistered: original proposal under existing transaction
must yield no content-changing candidate when required new observations unavailable;
allow retained read, deny/ROLLBACK before UPDATE, keep previous accepted pair and
explicit-input positive. Conservative policy may refuse known archived reselection;
no generic availability, new wire protocol/source authority or C11 closure claim.
