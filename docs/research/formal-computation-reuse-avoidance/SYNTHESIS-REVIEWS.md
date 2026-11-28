# Synthesis review — first attempt terminal status (2026-11-28)

No reviewer verdict delivered. This is execution failure evidence, not adverse evidence about the research proposal.

Frozen [review packet](./SYNTHESIS-REVIEW-PACKET.md) commit b2e91f3b7d6585352d2c0c098202fe2168396f68; all three receipts report SHA256 32c8b4cf7f5fef139cfc8a81d4155f1a453089427bdaa1e63171f6872fe51b8d. One request per exact model; 8192 completion limit, 90s watchdog, no fallback. No tools/edits permissions intended. No paid credentials passed into native free jobs. DeepSeek used reasoning effort none (coordinator decision, not max); MiMo/HungerG default. This is not a model-quality comparison.

- HungerG [18447150545](https://gitlab.com/rock-solid-sites-group/ases-execution/-/jobs/18447150545): HTTP 200, reasoning only, 25,438 observed reasoning characters, external watchdog 90.143s, no terminal usage, no answer. No observed orphan.
- DeepSeek [18447173342](https://gitlab.com/rock-solid-sites-group/ases-execution/-/jobs/18447173342) and MiMo [18447173343](https://gitlab.com/rock-solid-sites-group/ases-execution/-/jobs/18447173343): exact native free route and dummy wire gates passed, HTTP 429 in ~0.1s after request, non-SSE 208-byte response, no inference output. Error body not retained; quota vs rate limit vs shared unauthenticated endpoint restriction not resolved. No observed orphan. No retry/fallback.
- Full GLM-5.3 (not Flash): no call; authenticated catalog and headroom verified at 05:12Z, paid-overflow flag not exposed. Earlier headroom is not current authorization. Actual billed cost unknown for attempted calls; zero authorization not evidence of zero charge. Unresolved replay meters preserved.

Closed expired permits and removed only synthesis live operations, preserving other concurrent operations, executor commit e4e285285c622c30b540edb0d77677536739d3df readback verified. No fresh model calls in status turn. Next decision: if authorized, bounded free-client 429 diagnosis (do not infer credential/capacity cause), longer HungerG watchdog and fresh GLM billing-route confirmation. Preserve the identical packet unless explicitly changing review scope. Do not treat failed reviews as rejection or acceptance.

## Exact sanitized terminal receipts

```json
[
  {
    "job": 18447150545,
    "receipt": {
      "admitted_hook_attempts": 1,
      "after": {
        "api": {
          "http": 200
        },
        "headroom_pass": true,
        "meters": {
          "monthly": {
            "percent": 14,
            "status": "ok"
          },
          "rolling": {
            "percent": 0,
            "status": "ok"
          },
          "weekly": {
            "percent": 7,
            "status": "ok"
          }
        },
        "utc": "2026-11-28T05:16:51.092824+00:00"
      },
      "answer_bytes": null,
      "answer_chunks": 0,
      "answer_sha256": null,
      "answer_status": "NO_TEXT",
      "before": {
        "api": {
          "http": 200
        },
        "headroom_pass": true,
        "meters": {
          "monthly": {
            "percent": 14,
            "status": "ok"
          },
          "rolling": {
            "percent": 0,
            "status": "ok"
          },
          "weekly": {
            "percent": 7,
            "status": "ok"
          }
        },
        "utc": "2026-11-28T05:15:20.605714+00:00"
      },
      "case": "L",
      "cli_exit": 143,
      "cost_usd": "UNKNOWN",
      "decoded_feed": {
        "counts": {
          "session.created": 1,
          "session.execution.interrupted": 1,
          "session.execution.started": 1,
          "session.reasoning.delta": 443,
          "session.reasoning.ended": 1,
          "session.reasoning.started": 1,
          "session.step.failed": 1,
          "session.step.first-token": 1,
          "session.step.started": 1,
          "session.step.streamed": 1
        },
        "exact_session_matches": 1,
        "feed_eof": true,
        "feed_error": null,
        "feed_thread_alive": false,
        "first_epoch_ms": {
          "session.created": 1795842920738,
          "session.execution.interrupted": 1795843010723,
          "session.execution.started": 1795842920797,
          "session.reasoning.delta": 1795842921994,
          "session.reasoning.ended": 1795843010723,
          "session.reasoning.started": 1795842921895,
          "session.step.failed": 1795843010723,
          "session.step.first-token": 1795842921895,
          "session.step.started": 1795842921895,
          "session.step.streamed": 1795843010723
        },
        "invalid": 0,
        "oversized": 0,
        "ready": true,
        "reasoning_delta_chars": 25524,
        "reasoning_ended_chars": 25524,
        "text_delta_chars": 0,
        "text_ended_chars": 0,
        "unmatched_session_count": 0
      },
      "elapsed_seconds": 90.143,
      "event_counts": {
        "step_start": 1
      },
      "events": [
        {
          "stage": "HOOKS_READY",
          "t_ms": 1078.146,
          "wall_ms": 1795842920075
        },
        {
          "contexts": 1,
          "kind": "primary",
          "post_effort": "ABSENT",
          "pre_effort": "ABSENT",
          "prior_native_max_tokens": 65536,
          "stage": "MODEL_PREPARED",
          "t_ms": 1794.043,
          "target": true,
          "wall_ms": 1795842920791
        },
        {
          "attempt": 1,
          "contexts": 1,
          "dry_blocked": false,
          "kind": "primary",
          "mode": "default",
          "post_effort": "ABSENT",
          "pre_effort": "ABSENT",
          "prior_native_max_tokens": 65536,
          "route_matches": true,
          "stage": "HTTP_REQUEST",
          "t_ms": 1812.734,
          "target": true,
          "wall_ms": 1795842920810,
          "wire": {
            "max_completion_tokens": 8192,
            "max_tokens": null,
            "parse_ok": true,
            "reasoning_effort": "ABSENT",
            "thinking": "ABSENT",
            "wire_model_match": true,
            "wire_stream": true
          }
        },
        {
          "attempt": 1,
          "sse_content_type": true,
          "stage": "RESPONSE_HEADERS",
          "status": 200,
          "t_ms": 2882.008,
          "wall_ms": 1795842921879
        },
        {
          "attempt": 1,
          "bytes": 768,
          "stage": "FIRST_BODY_BYTE",
          "t_ms": 2885.103,
          "wall_ms": 1795842921882
        }
      ],
      "finish": false,
      "first_event_epoch_ms": {
        "step_start": 1795842921884
      },
      "inference_cli_launched": true,
      "live_catalog": {
        "api": {
          "http": 200
        },
        "exact_model_present": true,
        "expected_price_privacy": true,
        "input_price": 0,
        "monthly_go": null,
        "output_price": 0
      },
      "max_sample_gap_ms": 2852.603,
      "model": "opencode-go/hungerg-free",
      "operator_overflow_exception": false,
      "orphan": false,
      "outcome": "FAILED_OR_PARTIAL",
      "persistence": {
        "assistant_content_source": "session_part_projection",
        "assistant_finish_messages": 1,
        "assistant_part_type_counts": {
          "reasoning": 1
        },
        "assistant_text_characters": 0,
        "idle_outcome_counts": {
          "interrupted": 1
        },
        "persistent_state_qualified": true,
        "reason": null,
        "session_match_basis": "exact_cli_session_id",
        "status": null
      },
      "prompt_bytes": 3665,
      "prompt_sha256": "32c8b4cf7f5fef139cfc8a81d4155f1a453089427bdaa1e63171f6872fe51b8d",
      "prompt_variant": "admission_v1_independent_review",
      "provider_requests_delivered": "NOT_OBSERVED",
      "provider_tokens": "SSE_REPORTED",
      "quality_grade": {
        "pass": false,
        "reason": "INCOMPLETE_NOT_SCORED"
      },
      "quality_structure": {
        "semantic_correctness": "PENDING_COORDINATOR_REVIEW"
      },
      "registry": {
        "model_api": {
          "http": 200
        },
        "model_found": true,
        "model_package": "native_chat_compatible",
        "model_settings": {
          "chunk_ms": "UNSET",
          "header_ms": "UNSET",
          "tls_present": false,
          "total_ms": "UNSET",
          "transport": "UNSET_OR_OTHER"
        },
        "provider_api": {
          "http": 200
        },
        "provider_found": true,
        "provider_package": "native_chat_compatible",
        "provider_settings": {
          "chunk_ms": "UNSET",
          "header_ms": "UNSET",
          "tls_present": false,
          "total_ms": "UNSET",
          "transport": "UNSET_OR_OTHER"
        }
      },
      "requested_completion_limit": 8192,
      "requested_reasoning_effort": "default",
      "schema": "ases-experiment-register-admission-pilot-v1",
      "server": {
        "hooks_ready": true,
        "server_exit": 0,
        "server_orphan": false
      },
      "sse_first": {
        "allowance_usd": null,
        "attempt": 1,
        "billed_cache_read": null,
        "billed_cache_write_1h": null,
        "billed_cache_write_5m": null,
        "billed_input": null,
        "billed_output": null,
        "billed_reasoning": null,
        "billing_source": null,
        "bytes": 768,
        "chunks": 1,
        "comments": 0,
        "cost_estimated": null,
        "cost_usd": null,
        "done": 0,
        "errors": 0,
        "finish_events": 0,
        "frames": 2,
        "json_frames": 2,
        "length": 0,
        "list_cost_usd": null,
        "malformed": 0,
        "other_finish": 0,
        "other_json": 0,
        "other_lines": 0,
        "parser_disabled": false,
        "reason_blocks": 0,
        "reason_repeated_blocks": 0,
        "reasoning_alias_events": 1,
        "reasoning_chars": 2,
        "reasoning_content_events": 1,
        "reasoning_details_events": 0,
        "reasoning_events": 1,
        "role_events": 2,
        "stage": "SSE_PROGRESS",
        "stop": 0,
        "t_ms": 2885.166,
        "text_blocks": 0,
        "text_chars": 0,
        "text_events": 0,
        "text_repeated_blocks": 0,
        "tool_events": 0,
        "tool_finish": 0,
        "trailing_incomplete": false,
        "unknown_delta_events": 0,
        "usage_completion_tokens": 0,
        "usage_events": 2,
        "usage_prompt_tokens": 0,
        "usage_reasoning_tokens": 0,
        "usage_total_tokens": 0,
        "wall_ms": 1795842921882
      },
      "sse_first_category": {
        "done": null,
        "errors": null,
        "finish_events": null,
        "malformed": null,
        "other_json": null,
        "parser_disabled": null,
        "reasoning_events": 2885.166,
        "text_events": null,
        "unknown_delta_events": null,
        "usage_events": 2885.166
      },
      "sse_last": {
        "allowance_usd": null,
        "attempt": 1,
        "billed_cache_read": null,
        "billed_cache_write_1h": null,
        "billed_cache_write_5m": null,
        "billed_input": null,
        "billed_output": null,
        "billed_reasoning": null,
        "billing_source": null,
        "bytes": 1162507,
        "chunks": 1248,
        "comments": 0,
        "cost_estimated": null,
        "cost_usd": null,
        "done": 0,
        "errors": 0,
        "finish_events": 0,
        "frames": 2771,
        "json_frames": 2771,
        "length": 0,
        "list_cost_usd": null,
        "malformed": 0,
        "other_finish": 0,
        "other_json": 0,
        "other_lines": 0,
        "parser_disabled": false,
        "reason_blocks": 198,
        "reason_repeated_blocks": 0,
        "reasoning_alias_events": 2770,
        "reasoning_chars": 25438,
        "reasoning_content_events": 2770,
        "reasoning_details_events": 0,
        "reasoning_events": 2770,
        "role_events": 2771,
        "stage": "SSE_PROGRESS",
        "stop": 0,
        "t_ms": 91284.65,
        "text_blocks": 0,
        "text_chars": 0,
        "text_events": 0,
        "text_repeated_blocks": 0,
        "tool_events": 0,
        "tool_finish": 0,
        "trailing_incomplete": false,
        "unknown_delta_events": 0,
        "usage_completion_tokens": 0,
        "usage_events": 2771,
        "usage_prompt_tokens": 0,
        "usage_reasoning_tokens": 0,
        "usage_total_tokens": 0,
        "wall_ms": 1795843010282
      },
      "sse_sample_count": 79,
      "stderr_truncated": false,
      "stdout_truncated": false,
      "text_characters": 0,
      "version": "2.4.2",
      "version_gate": {
        "basis": "same_job_dummy_exact_version_and_executable_digest",
        "executable_sha256": "523b1502d1d556998b0904235cef65eb1d8cf8362b4e2faa7ae7a170c9a44cd4",
        "qualified": true
      },
      "watchdog": true
    },
    "replay": [
      {
        "model": "hungerg-free",
        "classification": {
          "state": "CENSORED_REASONING_ONLY",
          "hasUsage": true,
          "quality": "NOT_PASS",
          "billing": "NOT_FREE_CLASSIFIED",
          "reported_completion": 0,
          "continuation_blocked": false
        },
        "reconciliation": {
          "meters": {
            "requests": {
              "reported": 1,
              "hold": 0,
              "release": 0,
              "overrun": 0
            },
            "completion_tokens": {
              "reported": 0,
              "hold": 0,
              "release": 8192,
              "overrun": 0
            },
            "cash_microusd": {
              "reported": null,
              "hold": 0,
              "release": 0,
              "overrun": null
            }
          },
          "unresolved": true,
          "overrun": false,
          "stop_new_admission": true
        },
        "hook_wall_ms": 1795842920810,
        "terminal_wall_ms": 1795843010282
      }
    ]
  },
  {
    "job": 18447173342,
    "receipt": {
      "admitted_hook_attempts": 1,
      "after": {
        "paid_credentials_present": false
      },
      "answer_bytes": null,
      "answer_chunks": 0,
      "answer_sha256": null,
      "answer_status": "NO_TEXT",
      "before": {
        "paid_credentials_present": false
      },
      "case": "L",
      "cli_exit": 1,
      "cost_usd": "UNKNOWN",
      "decoded_feed": {
        "counts": {
          "session.created": 1,
          "session.execution.failed": 1,
          "session.execution.started": 1,
          "session.step.failed": 1,
          "session.step.started": 1
        },
        "exact_session_matches": 1,
        "feed_eof": true,
        "feed_error": null,
        "feed_thread_alive": false,
        "first_epoch_ms": {
          "session.created": 1795842991413,
          "session.execution.failed": 1795842991602,
          "session.execution.started": 1795842991475,
          "session.step.failed": 1795842991602,
          "session.step.started": 1795842991602
        },
        "invalid": 0,
        "oversized": 0,
        "ready": true,
        "reasoning_delta_chars": 0,
        "reasoning_ended_chars": 0,
        "text_delta_chars": 0,
        "text_ended_chars": 0,
        "unmatched_session_count": 0
      },
      "elapsed_seconds": 0.55,
      "event_counts": {
        "error": 1,
        "step_start": 1
      },
      "events": [
        {
          "stage": "HOOKS_READY",
          "t_ms": 1623.453,
          "wall_ms": 1795842991048
        },
        {
          "contexts": 1,
          "kind": "primary",
          "post_effort": "none",
          "pre_effort": "ABSENT",
          "prior_native_max_tokens": 32000,
          "stage": "MODEL_PREPARED",
          "t_ms": 2042.891,
          "target": true,
          "wall_ms": 1795842991467
        },
        {
          "attempt": 1,
          "contexts": 1,
          "dry_blocked": false,
          "kind": "primary",
          "mode": "none",
          "post_effort": "none",
          "pre_effort": "ABSENT",
          "prior_native_max_tokens": 32000,
          "route_matches": true,
          "stage": "HTTP_REQUEST",
          "t_ms": 2062.376,
          "target": true,
          "wall_ms": 1795842991487,
          "wire": {
            "max_completion_tokens": 8192,
            "max_tokens": null,
            "parse_ok": true,
            "reasoning_effort": "none",
            "thinking": "ABSENT",
            "wire_model_match": true,
            "wire_stream": true
          }
        },
        {
          "attempt": 1,
          "sse_content_type": false,
          "stage": "RESPONSE_HEADERS",
          "status": 429,
          "t_ms": 2159.315,
          "wall_ms": 1795842991584
        },
        {
          "attempt": 1,
          "bytes": 208,
          "stage": "FIRST_BODY_BYTE",
          "t_ms": 2161.259,
          "wall_ms": 1795842991586
        },
        {
          "proposed_retry": false,
          "stage": "RETRY_VETO",
          "t_ms": 2163.93,
          "target": true,
          "wall_ms": 1795842991588
        }
      ],
      "finish": false,
      "first_event_epoch_ms": {
        "error": 1795842991614,
        "step_start": 1795842991589
      },
      "inference_cli_launched": true,
      "live_catalog": {
        "exact_model_present": true,
        "free_route": "native_client_free_only",
        "input_price": 0,
        "output_price": 0,
        "price_basis": "official Console model pricing, native client registry, no paid credentials",
        "provider": "opencode"
      },
      "max_sample_gap_ms": 0.2,
      "model": "opencode/deepseek-v4.1-flash-free",
      "operator_overflow_exception": false,
      "orphan": false,
      "outcome": "FAILED_OR_PARTIAL",
      "persistence": {
        "assistant_content_source": "NO_ASSISTANT_CONTENT",
        "assistant_finish_messages": 1,
        "assistant_part_type_counts": {},
        "assistant_text_characters": 0,
        "idle_outcome_counts": {
          "failed": 1
        },
        "persistent_state_qualified": true,
        "reason": null,
        "session_match_basis": "exact_cli_session_id",
        "status": null
      },
      "prompt_bytes": 3665,
      "prompt_sha256": "32c8b4cf7f5fef139cfc8a81d4155f1a453089427bdaa1e63171f6872fe51b8d",
      "prompt_variant": "admission_v1_independent_review_console_free",
      "provider_requests_delivered": "NOT_OBSERVED",
      "provider_tokens": "NOT_EXPOSED",
      "quality_grade": {
        "pass": false,
        "reason": "INCOMPLETE_NOT_SCORED"
      },
      "quality_structure": {
        "semantic_correctness": "PENDING_COORDINATOR_REVIEW"
      },
      "registry": {
        "model_api": {
          "http": 200
        },
        "model_found": true,
        "model_package": "native_chat_compatible",
        "model_settings": {
          "chunk_ms": "UNSET",
          "header_ms": "UNSET",
          "tls_present": false,
          "total_ms": "UNSET",
          "transport": "UNSET_OR_OTHER"
        },
        "provider_api": {
          "http": 200
        },
        "provider_found": true,
        "provider_package": "native_chat_compatible",
        "provider_settings": {
          "chunk_ms": "UNSET",
          "header_ms": "UNSET",
          "tls_present": false,
          "total_ms": "UNSET",
          "transport": "UNSET_OR_OTHER"
        }
      },
      "requested_completion_limit": 8192,
      "requested_reasoning_effort": "none",
      "schema": "ases-experiment-register-admission-pilot-v1",
      "server": {
        "hooks_ready": true,
        "server_exit": 0,
        "server_orphan": false
      },
      "sse_first": {
        "allowance_usd": null,
        "attempt": 1,
        "billed_cache_read": null,
        "billed_cache_write_1h": null,
        "billed_cache_write_5m": null,
        "billed_input": null,
        "billed_output": null,
        "billed_reasoning": null,
        "billing_source": null,
        "bytes": 208,
        "chunks": 1,
        "comments": 0,
        "cost_estimated": null,
        "cost_usd": null,
        "done": 0,
        "errors": 0,
        "finish_events": 0,
        "frames": 0,
        "json_frames": 0,
        "length": 0,
        "list_cost_usd": null,
        "malformed": 0,
        "other_finish": 0,
        "other_json": 0,
        "other_lines": 0,
        "parser_disabled": false,
        "reason_blocks": 0,
        "reason_repeated_blocks": 0,
        "reasoning_alias_events": 0,
        "reasoning_chars": 0,
        "reasoning_content_events": 0,
        "reasoning_details_events": 0,
        "reasoning_events": 0,
        "role_events": 0,
        "stage": "SSE_PROGRESS",
        "stop": 0,
        "t_ms": 2161.323,
        "text_blocks": 0,
        "text_chars": 0,
        "text_events": 0,
        "text_repeated_blocks": 0,
        "tool_events": 0,
        "tool_finish": 0,
        "trailing_incomplete": false,
        "unknown_delta_events": 0,
        "usage_completion_tokens": null,
        "usage_events": 0,
        "usage_prompt_tokens": null,
        "usage_reasoning_tokens": null,
        "usage_total_tokens": null,
        "wall_ms": 1795842991586
      },
      "sse_first_category": {
        "done": null,
        "errors": null,
        "finish_events": null,
        "malformed": null,
        "other_json": null,
        "parser_disabled": null,
        "reasoning_events": null,
        "text_events": null,
        "unknown_delta_events": null,
        "usage_events": null
      },
      "sse_last": {
        "allowance_usd": null,
        "attempt": 1,
        "billed_cache_read": null,
        "billed_cache_write_1h": null,
        "billed_cache_write_5m": null,
        "billed_input": null,
        "billed_output": null,
        "billed_reasoning": null,
        "billing_source": null,
        "bytes": 208,
        "chunks": 1,
        "comments": 0,
        "cost_estimated": null,
        "cost_usd": null,
        "done": 0,
        "errors": 0,
        "finish_events": 0,
        "frames": 0,
        "json_frames": 0,
        "length": 0,
        "list_cost_usd": null,
        "malformed": 0,
        "other_finish": 0,
        "other_json": 0,
        "other_lines": 0,
        "parser_disabled": false,
        "reason_blocks": 0,
        "reason_repeated_blocks": 0,
        "reasoning_alias_events": 0,
        "reasoning_chars": 0,
        "reasoning_content_events": 0,
        "reasoning_details_events": 0,
        "reasoning_events": 0,
        "role_events": 0,
        "stage": "SSE_FLUSH",
        "stop": 0,
        "t_ms": 2161.523,
        "text_blocks": 0,
        "text_chars": 0,
        "text_events": 0,
        "text_repeated_blocks": 0,
        "tool_events": 0,
        "tool_finish": 0,
        "trailing_incomplete": true,
        "unknown_delta_events": 0,
        "usage_completion_tokens": null,
        "usage_events": 0,
        "usage_prompt_tokens": null,
        "usage_reasoning_tokens": null,
        "usage_total_tokens": null,
        "wall_ms": 1795842991586
      },
      "sse_sample_count": 2,
      "stderr_truncated": false,
      "stdout_truncated": false,
      "text_characters": 0,
      "version": "2.4.2",
      "version_gate": {
        "basis": "same_job_dummy_exact_version_and_executable_digest",
        "executable_sha256": "523b1502d1d556998b0904235cef65eb1d8cf8362b4e2faa7ae7a170c9a44cd4",
        "qualified": true
      },
      "watchdog": false
    },
    "replay": [
      {
        "model": "deepseek-v4.1-flash-free",
        "classification": {
          "state": "NONTERMINAL_STREAM",
          "hasUsage": false,
          "quality": "NOT_PASS",
          "billing": "NOT_FREE_CLASSIFIED",
          "reported_completion": null,
          "continuation_blocked": false
        },
        "reconciliation": {
          "meters": {
            "requests": {
              "reported": 1,
              "hold": 0,
              "release": 0,
              "overrun": 0
            },
            "completion_tokens": {
              "reported": null,
              "hold": 8192,
              "release": 0,
              "overrun": null
            },
            "cash_microusd": {
              "reported": null,
              "hold": 0,
              "release": 0,
              "overrun": null
            }
          },
          "unresolved": true,
          "overrun": false,
          "stop_new_admission": true
        },
        "hook_wall_ms": 1795842991487,
        "terminal_wall_ms": 1795842991586
      }
    ]
  },
  {
    "job": 18447173343,
    "receipt": {
      "admitted_hook_attempts": 1,
      "after": {
        "paid_credentials_present": false
      },
      "answer_bytes": null,
      "answer_chunks": 0,
      "answer_sha256": null,
      "answer_status": "NO_TEXT",
      "before": {
        "paid_credentials_present": false
      },
      "case": "L",
      "cli_exit": 1,
      "cost_usd": "UNKNOWN",
      "decoded_feed": {
        "counts": {
          "session.created": 1,
          "session.execution.failed": 1,
          "session.execution.started": 1,
          "session.step.failed": 1,
          "session.step.started": 1
        },
        "exact_session_matches": 1,
        "feed_eof": true,
        "feed_error": null,
        "feed_thread_alive": false,
        "first_epoch_ms": {
          "session.created": 1795843007209,
          "session.execution.failed": 1795843007399,
          "session.execution.started": 1795843007264,
          "session.step.failed": 1795843007399,
          "session.step.started": 1795843007399
        },
        "invalid": 0,
        "oversized": 0,
        "ready": true,
        "reasoning_delta_chars": 0,
        "reasoning_ended_chars": 0,
        "text_delta_chars": 0,
        "text_ended_chars": 0,
        "unmatched_session_count": 0
      },
      "elapsed_seconds": 0.555,
      "event_counts": {
        "error": 1,
        "step_start": 1
      },
      "events": [
        {
          "stage": "HOOKS_READY",
          "t_ms": 1720.147,
          "wall_ms": 1795843006839
        },
        {
          "contexts": 1,
          "kind": "primary",
          "post_effort": "ABSENT",
          "pre_effort": "ABSENT",
          "prior_native_max_tokens": 32000,
          "stage": "MODEL_PREPARED",
          "t_ms": 2140.605,
          "target": true,
          "wall_ms": 1795843007259
        },
        {
          "attempt": 1,
          "contexts": 1,
          "dry_blocked": false,
          "kind": "primary",
          "mode": "default",
          "post_effort": "ABSENT",
          "pre_effort": "ABSENT",
          "prior_native_max_tokens": 32000,
          "route_matches": true,
          "stage": "HTTP_REQUEST",
          "t_ms": 2174.295,
          "target": true,
          "wall_ms": 1795843007293,
          "wire": {
            "max_completion_tokens": 8192,
            "max_tokens": null,
            "parse_ok": true,
            "reasoning_effort": "ABSENT",
            "thinking": "ABSENT",
            "wire_model_match": true,
            "wire_stream": true
          }
        },
        {
          "attempt": 1,
          "sse_content_type": false,
          "stage": "RESPONSE_HEADERS",
          "status": 429,
          "t_ms": 2261.937,
          "wall_ms": 1795843007381
        },
        {
          "attempt": 1,
          "bytes": 208,
          "stage": "FIRST_BODY_BYTE",
          "t_ms": 2264.08,
          "wall_ms": 1795843007383
        },
        {
          "proposed_retry": false,
          "stage": "RETRY_VETO",
          "t_ms": 2266.966,
          "target": true,
          "wall_ms": 1795843007386
        }
      ],
      "finish": false,
      "first_event_epoch_ms": {
        "error": 1795843007411,
        "step_start": 1795843007386
      },
      "inference_cli_launched": true,
      "live_catalog": {
        "exact_model_present": true,
        "free_route": "native_client_free_only",
        "input_price": 0,
        "output_price": 0,
        "price_basis": "official Console model pricing, native client registry, no paid credentials",
        "provider": "opencode"
      },
      "max_sample_gap_ms": 0.225,
      "model": "opencode/mimo-v2.6-flash-free",
      "operator_overflow_exception": false,
      "orphan": false,
      "outcome": "FAILED_OR_PARTIAL",
      "persistence": {
        "assistant_content_source": "NO_ASSISTANT_CONTENT",
        "assistant_finish_messages": 1,
        "assistant_part_type_counts": {},
        "assistant_text_characters": 0,
        "idle_outcome_counts": {
          "failed": 1
        },
        "persistent_state_qualified": true,
        "reason": null,
        "session_match_basis": "exact_cli_session_id",
        "status": null
      },
      "prompt_bytes": 3665,
      "prompt_sha256": "32c8b4cf7f5fef139cfc8a81d4155f1a453089427bdaa1e63171f6872fe51b8d",
      "prompt_variant": "admission_v1_independent_review_console_free",
      "provider_requests_delivered": "NOT_OBSERVED",
      "provider_tokens": "NOT_EXPOSED",
      "quality_grade": {
        "pass": false,
        "reason": "INCOMPLETE_NOT_SCORED"
      },
      "quality_structure": {
        "semantic_correctness": "PENDING_COORDINATOR_REVIEW"
      },
      "registry": {
        "model_api": {
          "http": 200
        },
        "model_found": true,
        "model_package": "native_chat_compatible",
        "model_settings": {
          "chunk_ms": "UNSET",
          "header_ms": "UNSET",
          "tls_present": false,
          "total_ms": "UNSET",
          "transport": "UNSET_OR_OTHER"
        },
        "provider_api": {
          "http": 200
        },
        "provider_found": true,
        "provider_package": "native_chat_compatible",
        "provider_settings": {
          "chunk_ms": "UNSET",
          "header_ms": "UNSET",
          "tls_present": false,
          "total_ms": "UNSET",
          "transport": "UNSET_OR_OTHER"
        }
      },
      "requested_completion_limit": 8192,
      "requested_reasoning_effort": "default",
      "schema": "ases-experiment-register-admission-pilot-v1",
      "server": {
        "hooks_ready": true,
        "server_exit": 0,
        "server_orphan": false
      },
      "sse_first": {
        "allowance_usd": null,
        "attempt": 1,
        "billed_cache_read": null,
        "billed_cache_write_1h": null,
        "billed_cache_write_5m": null,
        "billed_input": null,
        "billed_output": null,
        "billed_reasoning": null,
        "billing_source": null,
        "bytes": 208,
        "chunks": 1,
        "comments": 0,
        "cost_estimated": null,
        "cost_usd": null,
        "done": 0,
        "errors": 0,
        "finish_events": 0,
        "frames": 0,
        "json_frames": 0,
        "length": 0,
        "list_cost_usd": null,
        "malformed": 0,
        "other_finish": 0,
        "other_json": 0,
        "other_lines": 0,
        "parser_disabled": false,
        "reason_blocks": 0,
        "reason_repeated_blocks": 0,
        "reasoning_alias_events": 0,
        "reasoning_chars": 0,
        "reasoning_content_events": 0,
        "reasoning_details_events": 0,
        "reasoning_events": 0,
        "role_events": 0,
        "stage": "SSE_PROGRESS",
        "stop": 0,
        "t_ms": 2264.156,
        "text_blocks": 0,
        "text_chars": 0,
        "text_events": 0,
        "text_repeated_blocks": 0,
        "tool_events": 0,
        "tool_finish": 0,
        "trailing_incomplete": false,
        "unknown_delta_events": 0,
        "usage_completion_tokens": null,
        "usage_events": 0,
        "usage_prompt_tokens": null,
        "usage_reasoning_tokens": null,
        "usage_total_tokens": null,
        "wall_ms": 1795843007383
      },
      "sse_first_category": {
        "done": null,
        "errors": null,
        "finish_events": null,
        "malformed": null,
        "other_json": null,
        "parser_disabled": null,
        "reasoning_events": null,
        "text_events": null,
        "unknown_delta_events": null,
        "usage_events": null
      },
      "sse_last": {
        "allowance_usd": null,
        "attempt": 1,
        "billed_cache_read": null,
        "billed_cache_write_1h": null,
        "billed_cache_write_5m": null,
        "billed_input": null,
        "billed_output": null,
        "billed_reasoning": null,
        "billing_source": null,
        "bytes": 208,
        "chunks": 1,
        "comments": 0,
        "cost_estimated": null,
        "cost_usd": null,
        "done": 0,
        "errors": 0,
        "finish_events": 0,
        "frames": 0,
        "json_frames": 0,
        "length": 0,
        "list_cost_usd": null,
        "malformed": 0,
        "other_finish": 0,
        "other_json": 0,
        "other_lines": 0,
        "parser_disabled": false,
        "reason_blocks": 0,
        "reason_repeated_blocks": 0,
        "reasoning_alias_events": 0,
        "reasoning_chars": 0,
        "reasoning_content_events": 0,
        "reasoning_details_events": 0,
        "reasoning_events": 0,
        "role_events": 0,
        "stage": "SSE_FLUSH",
        "stop": 0,
        "t_ms": 2264.381,
        "text_blocks": 0,
        "text_chars": 0,
        "text_events": 0,
        "text_repeated_blocks": 0,
        "tool_events": 0,
        "tool_finish": 0,
        "trailing_incomplete": true,
        "unknown_delta_events": 0,
        "usage_completion_tokens": null,
        "usage_events": 0,
        "usage_prompt_tokens": null,
        "usage_reasoning_tokens": null,
        "usage_total_tokens": null,
        "wall_ms": 1795843007383
      },
      "sse_sample_count": 2,
      "stderr_truncated": false,
      "stdout_truncated": false,
      "text_characters": 0,
      "version": "2.4.2",
      "version_gate": {
        "basis": "same_job_dummy_exact_version_and_executable_digest",
        "executable_sha256": "523b1502d1d556998b0904235cef65eb1d8cf8362b4e2faa7ae7a170c9a44cd4",
        "qualified": true
      },
      "watchdog": false
    },
    "replay": [
      {
        "model": "mimo-v2.6-flash-free",
        "classification": {
          "state": "NONTERMINAL_STREAM",
          "hasUsage": false,
          "quality": "NOT_PASS",
          "billing": "NOT_FREE_CLASSIFIED",
          "reported_completion": null,
          "continuation_blocked": false
        },
        "reconciliation": {
          "meters": {
            "requests": {
              "reported": 1,
              "hold": 0,
              "release": 0,
              "overrun": 0
            },
            "completion_tokens": {
              "reported": null,
              "hold": 8192,
              "release": 0,
              "overrun": null
            },
            "cash_microusd": {
              "reported": null,
              "hold": 0,
              "release": 0,
              "overrun": null
            }
          },
          "unresolved": true,
          "overrun": false,
          "stop_new_admission": true
        },
        "hook_wall_ms": 1795843007293,
        "terminal_wall_ms": 1795843007383
      }
    ]
  }
]
```
