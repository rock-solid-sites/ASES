# T11 — Cost and reliability

> **This table is not a scoring input.** Latency, tokens, retries, timestamps and HTTP status are recorded for cost and reliability analysis only (`schema.md` 3.4). No threshold, ranking or verdict in any other table depends on a number in this one.

| mechanism | cells | latency min ms | median | max | input tokens | output tokens | retries | typed errors | endpoint |
|---|---|---|---|---|---|---|---|---|---|
| prior | 64 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | None=64 | none (offline) |
| rule | 64 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | None=64 | none (offline) |
| lexical | 64 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | None=64 | none (offline) |
| jev | 64 | 525.3 | 587.5 | 763.5 | 22651 | 1882 | 0 | None=64 | https://opencode.ai/zen/v1/systemone |
| general_model | 64 | 901.5 | 1163.1 | 3615.2 | 16527 | 1321 | 0 | None=63, empty_content=1 | https://opencode.ai/zen/v1/chat/completions |
