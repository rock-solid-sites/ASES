# Independent published-cut receipt-loss check

## Result

The single assigned receipt-loss probe produced three supported, correlated cases under the selected live witness/current-root setup. The lost-reply case shows the witness successfully advanced its CAS revision and current cut to the actual `receipt-z` journal before suppressing the reply. The sink observed a transport failure and returned 503 with `local_control_committed=true`; a later fresh-nonce check of that current journal succeeded, and same-file recovery plus a second cold recovery retained the earlier ACK, z, and later accepted event.

The delivered-rejection control stayed at its old witness revision/cut. It retained z locally while returning 503, blocked the later append, and refused startup without changing the file. The ordinary positive control validated a delivered publication and returned 201.

## Independent audit

`audit.py` reads only the captured raw JSON. It correlates exact request/nonce/root, witness response and PID, CAS/current revision, local byte digest and event records, sink transport/caller outcome, subsequent fresh check, prior ACK retention, same-file process/recovery order, source manifest and source commit hashes, and all 11 owned child lifecycles. It caps observed concurrency at two. Missing evidence maps to `INCOMPLETE`; contradictory evidence maps to `VIOLATION`. The captured outcomes are all `SUPPORTED`.

The producer checker was run only after the independent verdict, against this same raw capture. It independently reported all three cases supported, missing witness evidence as incomplete, and a deliberately contradicted revision as a violation.

## Commands and identities

Execution branch: `review/autonomy-20261105-published-cut-receipt`
Execution/source commit: `9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9`

Probe command, run exactly once:

```sh
python3 research/phase-i-t18-sink-order-20261103/published-cut/receipt-loss/probe.py > evidence/published-cut-receipt/raw.json
```

Independent audit:

```sh
python3 evidence/published-cut-receipt/audit.py evidence/published-cut-receipt/raw.json > evidence/published-cut-receipt/audit.json
```

Secondary producer check:

```sh
python3 research/phase-i-t18-sink-order-20261103/published-cut/receipt-loss/check.py evidence/published-cut-receipt/raw.json > evidence/published-cut-receipt/producer-check.json
```

The raw records 11 unique owned children with maximum observed concurrency 2 and the probe's 256 MiB address-space cap. Raw source hashes match the recorded execution commit; the original sink process source digest matches the captured `cut_sink.py` digest.

## Evidence file digests (SHA-256)

a9c112ca4b2e82ed917dd4fd0086773cd0fd6356c6ed5391ed0e96f19004a216  evidence/published-cut-receipt/source-prediction.md
fe9e3b6d3007b20d05f1d607f08f042ba5ce72444a307d8b2b6489f381daf620  evidence/published-cut-receipt/raw.json
77c0e5c334f2f85e1aa34d423d70cd54038d14bcc3976ba84478a826f2b6302a  evidence/published-cut-receipt/audit.py
aebebc8f78ceef809d589f324ccdea344ee3f51c3d14d31e0ddc69a14adeecee  evidence/published-cut-receipt/audit.json
1049ea046bb1f8867ea29745422c3ce8bfc098df1b8723d48698654471362e4c  evidence/published-cut-receipt/producer-check.json
