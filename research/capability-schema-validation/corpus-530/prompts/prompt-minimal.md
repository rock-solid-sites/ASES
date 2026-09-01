# Tool-Calling Task — Minimal Description (Variant B/C) — #530

You are an assistant that must select a tool and construct arguments from MINIMAL capability descriptions.
You see ONLY: stable operation ID + concise description (≤20 words) + parameter names/types + required/optional + enum literals where applicable.
You do NOT see: numeric ranges (minimum/maximum, minLength/maxLength), string patterns (^art_..., ^cur_..., semver, uri, date-time), mutually constrained field rules (filter.type↔group_by, relation↔bidirectional), or schema constraints (additionalProperties:false). The runtime retains the complete authoritative schema (17 ops, version 0.1.0, Draft-07) and will validate before execution.

Invoke the tool whose concise description best matches the user request. Respond with JSON: {"op_id": "<stable_id>", "arguments": { ... }}.

## Minimal Capabilities (17 ops, version 0.1.0)
- search_artefacts: Search artefacts by free-text query with pagination.
    - query: string required
    - limit: integer optional
    - cursor: string optional
- get_artefact: Retrieve a single artefact by its stable identifier.
    - id: string required
- create_artefact: Create a new artefact of a given type with title, optional body, and optional tags.
    - type: string required enum=['spec', 'decision', 'evidence', 'review']
    - title: string required
    - body: string optional
    - tags: array<string> optional
- update_artefact_status: Transition an artefact to a new lifecycle status with optional reason.
    - id: string required
    - status: string required enum=['draft', 'active', 'archived']
    - reason: string optional
- create_review: Create a review verdict for an artefact with rationale and optional citations.
    - artefact_id: string required
    - verdict: string required enum=['approve', 'request_changes', 'reject']
    - severity: string optional enum=['critical', 'high', 'medium', 'low']
    - rationale: string required
    - citations: array<string> optional
- set_severity: Set the severity level for an artefact.
    - artefact_id: string required
    - level: string required enum=['critical', 'high', 'medium', 'low']
- set_artefact_state: Set the lifecycle state for an artefact.
    - artefact_id: string required
    - state: string required enum=['draft', 'active', 'archived']
    - comment: string optional
- query_metrics: Query aggregate metrics with optional grouping and faceting.
    - filter: object required nested_enums={'type': ['spec', 'decision', 'evidence', 'review']}
    - group_by: string optional enum=['type', 'status', 'severity']
    - include_facets: boolean optional
- list_reviews: List reviews with optional filtering by artefact and verdict.
    - artefact_id: string optional
    - verdict: string optional enum=['approve', 'request_changes', 'reject']
    - limit: integer optional
- get_capability_schema: Retrieve the authoritative schema for a capability by operation ID and optional version.
    - op_id: string required
    - version: string optional
- submit_evidence: Attach evidence items to an artefact.
    - artefact_id: string required
    - evidence_items: array<object> required
    - note: string optional
- link_artefacts: Create directed links between artefacts with a typed relation.
    - source_id: string required
    - target_ids: array<string> required
    - relation: string required enum=['depends_on', 'supersedes', 'relates_to']
    - bidirectional: boolean optional
- archive_artefact: Archive an artefact with a reason and optional superseding artefact reference.
    - artefact_id: string required
    - reason: string required
    - superseded_by: string optional
- validate_payload: Validate an arbitrary payload against the authoritative schema for a given operation ID.
    - op_id: string required
    - payload: object required
    - strict: boolean optional
- search_users: Search users by free-text query with pagination.
    - query: string required
    - limit: integer optional
    - cursor: string optional
    - department: string optional enum=['engineering', 'product', 'design', 'marketing']
    - include_inactive: boolean optional
- search_groups: Search groups by free-text query with pagination.
    - query: string required
    - limit: integer optional
    - cursor: string optional
    - visibility: string optional enum=['public', 'private', 'internal']
    - include_archived: boolean optional
- search_projects: Search projects by free-text query with pagination.
    - query: string required
    - limit: integer optional
    - cursor: string optional
    - status: string optional enum=['active', 'archived', 'planning']
    - include_private: boolean optional

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
