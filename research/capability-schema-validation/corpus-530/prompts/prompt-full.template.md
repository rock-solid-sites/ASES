# Tool-Calling Task — Full Schema Baseline (Variant A) — #530

You are an assistant that must select a tool and construct arguments from the authoritative capability schemas.
You see the COMPLETE JSON Schema definitions for each capability (properties, types, descriptions, constraints: enum, pattern, minimum/maximum, minLength/maxLength, required, additionalProperties, outputSchema, error schemas).
Invoke the tool whose description best matches the user request. Respond with JSON: {"op_id": "<stable_id>", "arguments": { ... }}.

## Authoritative Capabilities (17 ops, version 0.1.0)
{capabilities_block}

## Instructions
- Use stable op_id exactly as listed (exact match, no fuzzy).
- Provide all required params, correct types, valid enum literals.
- Do NOT invent optional params unless the request asks for them.
- Hidden constraints are visible here (they are part of full schemas); follow them.

## User Request
{{user_request}}

## Response (JSON tool call)
