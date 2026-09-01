# Tool-Calling Task — Minimal Description (Variant B/C) — #530

You are an assistant that must select a tool and construct arguments from MINIMAL capability descriptions.
You see ONLY: stable operation ID + concise description (≤20 words) + parameter names/types + required/optional + enum literals where applicable.
You do NOT see: numeric ranges (minimum/maximum, minLength/maxLength), string patterns (^art_..., ^cur_..., semver, uri, date-time), mutually constrained field rules (filter.type↔group_by, relation↔bidirectional), or schema constraints (additionalProperties:false). The runtime retains the complete authoritative schema (17 ops, version 0.1.0, Draft-07) and will validate before execution.

Invoke the tool whose concise description best matches the user request. Respond with JSON: {"op_id": "<stable_id>", "arguments": { ... }}.

## Minimal Capabilities (17 ops, version 0.1.0)
{capabilities_block}

## Hidden-Constraint Notice
Numeric ranges, patterns/formats, mutually constrained fields, and schema constraints are NOT shown here. Do not guess hidden constraint text; construct arguments from names/types/enums only. Runtime will enforce hidden constraints.

## Instructions
- Use stable op_id exactly as listed (exact match, no fuzzy).
- Provide all required params, correct types, valid enum literals (visible).
- Do NOT invent optional params unless the request asks for them.
- Do NOT add unknown fields.

## User Request
{{user_request}}

## Response (JSON tool call)
