# Malformed Recovery — 12 Cases (530)
All expected `ValidationFailed` at runtime validation before policy/execution. Each lists corrected_args for one-retry measurement. Hidden violations test constraint-sensitive class.
| ID | Category | Op | Constraint | Field |
|---|---|---|---|---|
| R01 | missing_required | `search_artefacts` | `required` | `query` |
| R02 | wrong_type | `search_artefacts` | `type` | `query` |
| R03 | invalid_enum | `create_artefact` | `enum` | `type` |
| R04 | invalid_nested_field | `query_metrics` | `type` | `filter` |
| R05 | missing_nested_required | `submit_evidence` | `required` | `evidence_items[0].content` |
| R06 | hidden_range_violation | `search_artefacts` | `maximum` | `limit` |
| R07 | invalid_combination | `query_metrics` | `mutually_constrained` | `group_by` |
| R08 | malformed_array | `link_artefacts` | `minItems` | `target_ids` |
| R09 | malformed_object | `get_artefact` | `additionalProperties` | `extra` |
| R10 | missing_required_balanced | `create_review` | `required` | `rationale` |
| R11 | invalid_enum_balanced | `set_severity` | `enum` | `level` |
| R12 | hidden_pattern_violation_balanced | `get_artefact` | `pattern` | `id` |
