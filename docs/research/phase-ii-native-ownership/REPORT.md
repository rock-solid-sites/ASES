# Native ownership histories

The bounded native histories ran against the frozen owner, L5/L6, F1, and F4
components in the local software fixture. The final complete capture is
[`evidence/native-25/raw.json`](evidence/native-25/raw.json), SHA-256
`246859b3e5de09449d96be6e9a823ec665f05a746439c843c6a8610bf716e5a6`.

The independent raw checker reports `PASS` for 12 cases and 10 pinned source
files. It reconstructs selected F1 pairs and retained observations, checks
native CURRENT records and L6 SQLite catalog/object bytes, derives the moved D
permission path, checks journal/witness/effect sequencing, and verifies the
actual cold cleanup states. Three altered-evidence controls are rejected:
forged F1 world, a resurrected live D, and surviving data after removal.

The captures demonstrate:

- Empty issuer bootstrap, real F1 acceptance, native F3 acceptance, exact
  duplicate, and same-byte/new-world registration. A caller-supplied pair is
  refused before changing CURRENT or material.
- Actual F4 admission; stale epoch, stale selector, forged world, moved D, and
  removed-domain new-ID requests are refused without a local append. After
  replacement/activation to current F4 v2, a new request against the removed
  domain reaches the native `native-domain-not-live` guard.
- A kill after actual F4/witness publication but before the owner publication
  reply leaves one local event. Cold recovery and exact retry settle that same
  event, and the historic retry remains an observation after source disposal.
- EOF after local append but before witness publication returns 503
  `native-effect-requires-reconciliation`, with the actual local sequence 4
  retained in the owner. Cold start refuses the journal because the published
  witness cut is behind; the harness does not invent publication or retry it.
- Kills at L6 file-fsync-before-COMMIT, L6 COMMIT-before-owner-CURRENT, F3
  acceptance-selected-before-reply, owner logical disposition before L6
  disposal, L6 disposal COMMIT before unlink, and owner removal-selected before
  physical cleanup. Explicit digest-bound disposition and cold cleanup
  converge where authorized; F1 retained observations remain present.
- Both orders at the shared `prepare_candidate`/removal eligibility point.
  Creator-first leaves a durable candidate that blocks removal; remover-first
  commits removal and subsequent creation is denied. Actual competing requests
  while the opposite operation holds the native guards fail with no owner
  selection or durable-phase change.

The pre-COMMIT unknown file and after-append/witness-mismatch states remain
fail-closed until an explicit supported disposition or matching published
cut exists. These are local process/filesystem histories, not a claim of
arbitrary power-loss durability, same-owner compromise resistance, remote
cancellation, or external exactly-once delivery. Earlier failed and
instrumentation attempts are preserved under `evidence/native-01` through
`evidence/native-24`.

Reproduce the final capture with:

```sh
python3 -B docs/research/phase-ii-native-ownership/probe.py --out docs/research/phase-ii-native-ownership/evidence/NEW_CAPTURE
python3 -B docs/research/phase-ii-native-ownership/check.py docs/research/phase-ii-native-ownership/evidence/NEW_CAPTURE/raw.json
```

The output directory must be new or empty. The probe uses a private short
`/tmp` directory for AF_UNIX sockets and keeps journal, owner, F1, and raw
evidence under the requested capture directory.
