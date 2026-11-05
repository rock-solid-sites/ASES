# Sink witness check

## Provisional source verdict, recorded before probe execution

**Question.** Does a live external-to-rollback witness that compares only an issued authority generation suffice for ordinary actual sink acceptance after an acknowledged revoke that does not change generation?

**Provisional verdict: no.** In the selected managed sink, `/revoke` durably appends `managed_revoked` and clears `granted` and `active`, while it leaves `version` unchanged. The earlier granted/active state is therefore generation 1; the post-revoke state is also generation 1. The witness wrapper's `generation` projection compares only `authority_version`, so a replayed pre-revoke sink at generation 1 should match the live witness after the revoke. The wrapper calls the ordinary sink's `eligible()` after the original local eligibility check, and on witness allow it proceeds to append the usual `effect_accepted` record and return the normal 201 ACK.

The `eligibility` projection compares `created`, `granted`, `active`, `authority_version`, and `holder`. A replayed pre-revoke candidate remains locally eligible at generation 1, but differs from the published revoked state in `granted` and `active`; source predicts a denial (409), no `x` effect append, and no ACK. The same-boot revoked sink's original local `eligible()` should also deny before any witness exchange, providing a retained-current-state control.

This prediction depends on the probe's supervisor publishing the current state after the revoke and before the subsequent sink starts, and on the local loopback witness endpoint and selected root identity being the trusted boundary. The witness is an ordinary process that outlives sink restarts; that demonstrates process liveness in this harness, not independent authentication of the endpoint, publisher, or state source. The source itself labels supervisor freshness as an external premise. The journal replay validates transition shape and selected same-root state, but cannot detect restoring an earlier, valid acknowledged prefix. This check makes no cross-family or general closure claim.

**Predicted observations:** generation profile accepts `x` after recovery from the older acknowledged prefix despite the live witness's revoked flags; eligibility profile rejects it. Both need ordinary sink HTTP response, append-only journal evidence, retained cold replay, live witness identity/status, and a request/nonce/reply exchange logged by both sides.

**Source basis at execution pin:** repository `7ee48372c38da079cfdf8aca8c186956f80a2de8`.

| Input | SHA-256 |
|---|---|
| `sink-witness/witness_sink.py` | `9dba728645bd7d49f4f1313bac4636729540dd7757da1514a6f7bdcd7835aa76` |
| `sink-witness/probe.py` | `3aebaa42a1d1c18230aeb94a3a20293af64ccdf853063aa5ddc0bbbee6b36048` |
| `sink-witness/check.py` | `fb190c25ba68de1695a9297fc41eb7c7b6697c226e61dc0a76b4295e1dc39a83` |
| `managed-revocation/managed_sink.py` | `7134618da4241942f2343748e44ae3d3e339e6d5f22c0681f539d404d0c8247f` |
| `managed-revocation/replay_probe.py` | `925df1268c9417eedc64ecd6b37649b53abb345a209899f9a6d6dbec654c2903` |
| `managed-revocation/probe.py` | `3b2b47931e9f78e49fee7fefb19b05776792691ca663091781988b8192b036e4` |
| `run.py` | `6b1d759b87b13d32bdc7c5f31a64c15d5a63296d77bc2f16ecc6b0e7795a9d59` |

## Observed result and independent raw audit

The single primary probe ran at the pinned checkout above and emitted `raw.json` with SHA-256 `a1969ac6d05cf20e857c7c7cc9107dc5ee22fcfccf9b3b9c2d3b82b28d0ec297`. The independent read-only audit in `audit.py` checked the raw process records, publication order, request and reply logs, nonce echo, effect journal, ACK sequence, and cold replay. Its output is `check.json`.

The **generation** case is a concrete counterexample to the sufficiency claim. The revoke was ACKed and recorded at version 1; the witness accepted a second publication whose current state had `granted=false` and `active=false`, still at version 1. That same witness process remained alive across all sink restarts. The recovered sink presented its rolled-back eligible version-1 tuple to that process, received an allowed reply with the matching fresh nonce, appended the `x` effect as event 5, and returned 201. A subsequent cold recovery retained that effect.

The **eligibility** case had the same actual revoke, rollback, live witness, and version. Its full tuple comparison returned a valid denial; the ordinary sink returned 409 and wrote no `x` event. The recovered journal and effect set remained stable through cold replay. A retained same-root recovery immediately after revoke also denied, showing that the acceptance required restoring the older valid acknowledged prefix.

The bundled protocol controls recorded an ordinary positive acceptance (201), denial when the witness deliberately returned a wrong nonce (409 despite `allowed=true`), acceptance after resetting that control (201), and denial after the witness process exited (409). These are protocol-fault controls in a bounded harness, not measurements of spontaneous endpoint or transport faults.

**Interpretation and certainty.** The observed actual 201/409 responses, durable event, replay, and live process/request identities support the narrow finding with high confidence for this selected implementation and synchronized-publication history. An external-to-rollback live process does not make a generation-only comparison sufficient when revoke leaves that generation unchanged. Comparing the eligibility tuple discriminates this history. The experiment does not establish source authentication or publisher authentication: `/publish` is a trusted-supervisor harness route, and the probe publishes the post-revoke state after the revoke ACK and before the recovered submission. That synchronization is an experimental premise, not a demonstrated general publication-order guarantee. Process liveness is evidenced by PID/status and lifetime records, while independent trust is not.

The probe environment was `Linux-6.18.57-x86_64-with-glibc2.41`, Python `3.12.14`, executable SHA-256 `fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7`, with a 256 MiB address-space limit. Reproduce from this checkout with:

```sh
python3 research/phase-i-t18-sink-order-20261103/sink-witness/probe.py > evidence/sink-witness/raw.json
python3 evidence/sink-witness/audit.py evidence/sink-witness/raw.json > evidence/sink-witness/check.json
```

Only the first command was run for the primary probe. The second command is the independent raw audit. No extra probe run was needed because the primary history already contained both projection profiles and the bounded nonce/reset/missing-witness controls. This is one selected family and environment; it makes no formal cross-family claim and no generic closure claim.
