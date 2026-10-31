# Independent review route and launch provenance

Target implementation: `b49e1f66ddd91e501794f6c9381e1e96c19b096c`, branch `research/f3-l5-lifecycle-integration-20261031`.

## Route check

Before review dispatch, the approved VPS route was invoked non-destructively:

```sh
/home/claude-code/.opencode/bin/opencode run --format json \
  -m opencode/mimo-v2.6-flash-free \
  'Reply exactly: VPS OpenCode route check passed.' </dev/null
```

Observed response: `VPS OpenCode route check passed.` OpenCode CLI version: `1.19.4`. `opencode models` listed both approved IDs (`opencode/mimo-v2.6-flash-free`, `opencode/glm-5.3-flash-free`). Route-check JSONL is retained under `raw/`; it reports `cost: 0`. The invocation used the configured OpenCode provider route as-is. No desktop application, provider configuration, or credential was changed.

## Eligible independent review runs

- **GLM reviewer:** `opencode/glm-5.3-flash-free`, OpenCode free route, session `ses_e6fd2ce9effeeiGtOAFW84fBB9`. It reviewed an isolated packet with the implementation source, raw observations, L1/L3/L4 code, and the resolved spec documents; it did not receive result/obstruction files or the MiMo report.
- **MiMo reviewer:** `opencode/mimo-v2.6-flash-free`, OpenCode free route, successful retry session `ses_e6fc6d267ffe3v8TrBLzh05WzV`. It reviewed a separate packet and read-only ran the packet verifier. Its captured tool trace references only that packet. It did not receive the GLM report.
- **Eligibility:** the implementation was directly authored in a GPT-6 Luna coding session. The only implementation-model invocation recorded from Codex/Phoenix Grove was `glm-5.3-flash` through `pgs2`; it received HTTP 402 before producing output. MiMo is a distinct model route. GLM is the same model family as the failed attempt but a separate OpenCode free route, and the failed attempt yielded no implementation. Both successful reviewers are therefore independent of the model that authored the implementation.

## Aborted attempt and isolation handling

An earlier MiMo invocation (`ses_e6fd2ceb3ffeMB0nlbdRCfCtf2`) was stopped after its tool trace began reading the other review packet. It produced no final review, was excluded from the verdict, and its partial JSONL is retained as `raw/opencode-mimo-aborted-cross-packet.jsonl`. Only the process started for that invocation was stopped; no pre-existing session was touched. The successful MiMo retry was dispatched separately and its trace contains no cross-packet paths.

## Governing reference resolution

The user-supplied `5c03a425fd5627c3764806292b8c5cb653498f4f` is `docs: recategorize reusable decisional provenance research`, unrelated to T11/Closure §7. We resolved the source references before dispatch:

- T11: `Phase-I-Verification.md` at `511a5272e92155bd5ace7be2bb13fd2ed3730b23`.
- Closure §7: `Phase-I-Closure.md` at `8277b7f3b87347ef0c8438e1b7b73f08f37f9992`.
- Both documents are retained under `specification/` and their source commit IDs are recorded in the filenames.

No model/provider substitutions were made. The successful route outputs and stderr, exact prompts, raw JSONL, resolved spec files, and aborted invocation trace are preserved in this directory.
