# Independent native resource occupancy check

## Verdict

**Supported for the selected adapter promise, within this same-family operational check.** In the tested Linux/Python/SQLite setup, guarded acquisition held a real loopback TCP listener before SQLite COMMIT and success acknowledgement. A committed claim alone did not establish native availability or release. A transferred reference to the same listener kept the port occupied after the original owner was killed, until the keeper closed its descriptor. After B was killed, its durable ledger row remained while its ephemeral listener was released.

This is independent operational evidence for the selected realization and same-family behavior. It is not cross-family proof, and does not show that the earlier SQL-only tests were defective; those tests answered their narrower ledger question.

## Prediction and basis

Before the sole probe run, I recorded this prediction: SQL claim/release alone would not alter a live listener; a transferred `SCM_RIGHTS` reference would keep that same listener occupied after its owner died; guarded bind/listen before COMMIT/ACK would support acquisition only after the last reference closed. Inputs were the scoped probe/check, local Python and SQLite, loopback TCP, descriptor transfer, process reaping, and bind errno. Phase-I-Closure calls resource quantities bounded, includes resource use in the ordering of validation and commitment, and permits already-granted internal resource-backed computation to survive engine loss when its realization survives. The selected mappings remain partial: C3 covers grants and ancestor restrictions but not concrete allocation/consumption; C5 concerns accepted content and continued computation, without itself proving native retention; C12 covers management revocation acknowledgement and recovery guards, without itself proving resource release. A guarded SQLite claim or release can serialize ledger state, but cannot by itself establish a bound socket, its live descriptor references, or a concrete release.

## Observation

One invocation of the repository-owned probe generated [raw.json](./raw.json). The repository's read-only `check.py` reported all three cases `SUPPORTED`; source hash, raw frame integrity, incomplete-evidence controls, contradiction control, and observed child cleanup checks passed in [check.json](./check.json). An additional independent read-only spot audit is implemented in [audit.py](./audit.py); it passed all three cases.

The release ACK in each case carried the original listener's device, inode, address, and accepting state. Its recorded `BEGIN`, `DELETE`, `COMMIT` order completed before the ACK was emitted and received. The ledger was `A` before release and empty after release, yet a ledger-only contender could commit `B` and receive its claim ACK while an actual bind to the same address failed with `EADDRINUSE`. This directly distinguishes ledger release from native release.

In the terminated-owner control, the owner was reaped before the subsequent guarded bind/listen; acquisition then succeeded. In the retained-reference control, the owner sent the listener descriptor by `SCM_RIGHTS`; the keeper observed the same device/inode/address and accepting state. After owner death, a guarded contender received `EADDRINUSE` and rolled back without committing. Closing the keeper's descriptor preceded successful guarded acquisition. Thus the observed occupancy followed the socket's remaining reference, not the owner's process lifetime or the released SQL row.

For each successful guarded acquisition, native bind/listen completed before the B `INSERT` transaction began; `COMMIT` completed before success acknowledgement. An independent bind attempt while B held the listener got `EADDRINUSE`. After B termination, the ledger still contained `B` with SQLite integrity `ok`, while a new bind to that address succeeded. This demonstrates the selected separation between a durable ownership record and an ephemeral realization; it does not imply restoration of that realization after process loss.

## Limits

The probe observes one host and one OS socket model with a loopback TCP listener and a descriptor passed using `SCM_RIGHTS`. It exercises no application traffic, credential revocation, host confinement, power loss, machine restart, durable native resource restoration, or resource families beyond this socket example. It does not test universal release semantics. The evidence supports the selected adapter behavior at the observed bind/listen and SQLite acknowledgement boundary only.
