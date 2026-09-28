# Sentinel Scope: `--model` flag + Exhaustion→Triage

**Status: ✅ Implemented (2026-07-11)**

Two independent, low-risk changes to `crosslink/src/commands/sentinel/`.
No schema change, no DB migration, no new types, no new config keys.

---

## Change 1: `--model` flag on `run` / `watch`

### Files & line numbers

| File | Location | Change |
|------|----------|--------|
| `main.rs` | `2063` Run variant, `2072` Watch variant, `2107` RunDaemon variant | add `#[arg(long)] model: Option<String>` |
| `mod.rs` | `33` Run arm, `46` Watch arm, `65` RunDaemon arm | pass `model` into `dispatch_cmd` |
| `engine.rs` | `26` `run_oneshot`, `126` `process_signal_batch` | add `model_override: Option<&str>`, forward to `triage` |
| `dispatch.rs` | `44` `triage` | add `model_override: Option<&str>` |
| `watch.rs` | `17` `start`, `163` `run_watch_loop`, `191` `async_watch_loop`, `366` `run_polling_cycle`, `398` `run_webhook_cycle` | thread `model` through daemon spawn, poll cycle, **and webhook cycle** |

### Parameter threading chain

```
CLI --model
  └─> main.rs Run / Watch / RunDaemon variants   (model: Option<String>)
       └─> mod.rs dispatch_cmd                    (Run / Watch / RunDaemon arms)
            ├─> engine::run_oneshot(model_override)                         [Run]
             └─> watch::start(model)
                  └─> async_watch_loop(model)                       [Watch]
                       ├─> run_polling_cycle(model)                  [poll path]
                       │    └─> engine::run_oneshot(model_override)
                       │         └─> engine::process_signal_batch(model_override)
                       └─> run_webhook_cycle(model)                  [webhook path: watch.rs:398]
                            └─> engine::process_signal_batch(model_override)   
                                 └─> dispatch::triage(model_override)
                                     └─> dispatch::triage(model_override)
                                          └─> AgentScope.model
                                               └─> spawn_agent -> KickoffOpts.model (engine.rs:443)
```

### The one design decision: escalation scope

`--model` is a user-supplied global override. The question is whether it also
overrides the **escalation** model (attempt 2, `dispatch.rs:64`
`config.escalation.model`) or only the initial dispatch (attempt 1, `New` arm
`dispatch.rs:57-63`).

- **Recommended:** apply `--model` as a hard override *before* the `New`/`Escalate`
  match in `triage()` (i.e. at `dispatch.rs:56`), so **both** attempt 1 and
  attempt 2 use it. A user who pins a model expects every agent in that run to
  use it.
- **Alternative:** only override the `New` arm; escalation keeps
  `config.escalation.model`.

Resolution: pick one and document it; the threading is identical either way.

### Side effects (self-tuning bypass)

When `model_override` is `Some`, `tuning.model_for_label(label)`
(`dispatch.rs:59-61`) is skipped entirely — self-tuning is bypassed for that
run. This is intended (explicit user override wins over historical tuning). No
other side effects: `AgentScope`, `KickoffOpts`, DB `model_used` column, and the
posted GH comment (`collect.rs:90`) all already carry the resolved model.

---

## Change 2: Wire exhaustion to `Disposition::Triage`

### Current exhaustion flow (silent skip)

1. `collect.rs:329` `classify_status` — when status is `FAILED`/`TIMEOUT` **and**
   `attempt_number >= 2`, returns `Some("exhausted")`.
2. `collect.rs:71` outcome `"exhausted"` flows into the collect loop:
   - `collect.rs:104-110` posts the GitHub result comment (Layer 4 dedup via
     `gh_comment_already_posted`).
   - `collect.rs:112` `db.update_dispatch_outcome(dispatch.id, "exhausted", &findings)`.
3. Loop ends. The dispatch is now recorded as `exhausted`, so on the next cycle
   `SeenSet::evaluate` returns `Skip("both attempts failed")`
   (`seen_set.rs:62`) and `db_dedup_check` returns the same (`seen_set.rs:106`).
   **No crosslink issue is created for human review — the failure is silently dropped.**

### Where to intercept

In `collect.rs` `collect_completed`, **before** `collect.rs:112`
(`update_dispatch_outcome` → `"exhausted"`), branch on `outcome == "exhausted"`
and create a crosslink **Triage** issue. Creating the issue before marking
exhausted prevents a loss condition: if issue creation fails, the dispatch
remains `pending` and is safely retried on the next cycle.

**Do not** attempt to build a fake `Signal` struct — `SentinelDispatch`
(`db/sentinel.rs:24`) does not store the original signal body. Instead, extract
the core logic of `create_sentinel_issue` (`engine.rs:358`) into a generic
helper:

```rust
fn create_triage_issue(
    db: &Database,
    writer: &SharedWriter,
    reference: &str,       // e.g. "GH#42" or "signal:label"
    title: &str,
    description: &str,
    priority: &str,
    labels: &[&str],
) -> Result<i64>
```

Both `engine.rs` and `collect.rs` call this helper. For the exhaustion case,
pass the agent's `findings` (already read at `collect.rs:77-79`) as the
description, and the GH issue number as the reference.

Required threading for the intercept:
- `collect_completed` (`collect.rs:41`) currently takes
  `(db, crosslink_dir, config)`. Add `writer: Option<&SharedWriter>` so it can
  create the issue (writer is already in scope at the call site
  `engine.rs:310`).

### What the Triage disposition creates

Mirrors `engine.rs:285-305`:
- `create_sentinel_issue` → adds labels `sentinel`, `bug`, priority `medium`
  (`engine.rs:369,382-383`).
- `update_issue(issue_id, None, None, Some(&priority))` → set priority.
- `add_label` for each disposition label.

Proposed constants for exhaustion (code-side, not config):
- **priority:** `"high"`
- **labels:** `["sentinel", "agent-exhausted", "needs-human-review"]`
- **body:** reference the GH issue number, dispatch id, attempt count, and the
  agent findings already read at `collect.rs:77-79`.

### SeenSet integration (no re-trigger)

**Before the change:** the outcome was updated first, then no issue was created.
**After the change:** the Triage issue is created first, then the outcome is
updated. If issue creation fails, the dispatch remains `pending` and retries
on the next cycle. Once the outcome is `"exhausted"`, `SeenSet::evaluate`
(`seen_set.rs:62`) and `db_dedup_check` (`seen_set.rs:106`) return
`Skip("both attempts failed")`, so the signal never re-enters the dispatch
pipeline. The Triage issue is created **exactly once**. No optional safety
guard needed — the pending-filter reliably prevents re-entry.

### Testing considerations

- **Unit (`collect.rs`):** `classify_status` already returns `"exhausted"` at
  attempt 2 (`collect.rs:546,556`). Add a test that `collect_completed` creates
  a Triage issue (priority high + labels) **before** updating outcome to
  `"exhausted"` (mock `db` + `writer`). Add a test that a failed issue
  creation does **not** update the outcome, leaving the dispatch `pending`.
- **Unit (`seen_set.rs`):** exhausted → `Skip` already covered
  (`seen_set.rs:319-335`); confirm no regression.
- **Unit (`engine.rs`):** add test for the new `create_triage_issue` helper
  (accepts direct args, no Signal dependency).
- **Integration:** simulate two failed attempts → assert a crosslink issue with
  priority `high` and label `agent-exhausted` exists, and that a 3rd cycle does
  **not** create a duplicate.
- **Integration (webhook):** `sentinel watch --model X` receiving a webhook
  event → verify the dispatched agent uses model `X`.
- **Regression:** confirm the GH result comment is still posted
  (`collect.rs:104-110`, Layer 4 dedup) alongside the new Triage issue.

---

## Combined impact

### End-to-end flow

```
crosslink sentinel run --model opencode-go/deepseek-v4-flash        (or: watch --model ...)
  1. run_oneshot -> process_signal_batch(model_override)
  2. triage uses override -> AgentScope.model = override
  3. agent dispatched with that model
  4. on failure -> escalates to attempt 2 (same override model)
  5. if agent fails twice -> classify_status returns "exhausted"
         -> collect creates crosslink Triage issue (BEFORE marking exhausted)
         -> collect posts GH comment (as today)
         -> collect marks outcome = "exhausted" (SeenSet prevents re-trigger)
  6. operator reviews Triage issue, picks model, re-dispatches or closes
```

### What the operator sees and does

- As before: a GitHub comment `Could not reproduce (all attempts exhausted)`
  (or `Could not fix (all attempts exhausted)`, `collect.rs:380,444`).
- **New:** a crosslink issue (priority `high`, label `agent-exhausted`) is
  created for human triage instead of the failure being silently dropped.
- Operator reviews the issue, decides next step (manual fix, re-label, close).

### No new config keys

`--model` is a CLI flag only. Triage priority/labels are code constants. No
schema change, no DB migration, no new config keys.
