You are answering a frozen classification benchmark. Do not reason aloud.

Read the file `{tasks_file}`. It contains `cases`, each with:
  - `case_id`
  - `user_message`  (the complete question you must answer)
  - `system_prompt_frozen` (the instruction you must obey)

For EACH case, produce the bare answer text that a deterministic classifier
following `system_prompt_frozen` would emit for `user_message`. That means:
  - noul   -> exactly `YES` or `NO`
  - choice -> exactly one option key
  - score  -> exactly one allowed label
No explanation, no punctuation, no quotes, no markdown, no reasoning.

Base each answer ONLY on the text inside that case's `user_message`. The file
contains no answers and you must not guess at any pattern beyond the text.

Output format: NDJSON, one line per case, nothing else before or after.
The file contains {n_cases} cases. Emit exactly one line for EVERY one of them.
Each line is a JSON object with exactly two keys:
  {{"case_id": "<id>", "content": "<answer text>"}}
Emit the lines in the same order as the cases appear in the file. No code fence.
Do not omit, merge, summarise or skip any case. Do not add a trailing summary.
