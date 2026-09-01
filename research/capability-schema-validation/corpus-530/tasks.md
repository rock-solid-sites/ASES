# Corpus 530 — 24 Tasks in 6 Classes (Tool-Calling)
Authoritative: `schemas/authoritative.json` (17 ops, 0.1.0). Minimal: `schemas/minimal.json` (stable ID + ≤20w summary + names/types + required/optional + enum literals). Hidden constraints NOT in minimal; runtime enforces.
| ID | Class | Title | Expected op | Key args |
|---|---|---|---|---|
| C1-T01 | C1 simple_scalars | Simple scalar — search users by query | `search_users` | `{"query": "alice"}` |
| C1-T02 | C1 simple_scalars | Simple scalar — get artefact by ID | `get_artefact` | `{"id": "art_abc-123"}` |
| C1-T03 | C1 simple_scalars | Simple scalar — set severity level | `set_severity` | `{"artefact_id": "art_abc-123", "level": "high"}` |
| C1-T04 | C1 simple_scalars | Simple scalar — archive artefact with reason | `archive_artefact` | `{"artefact_id": "art_abc-123", "reason": "superseded by new design for clarity"}` |
| C2-T05 | C2 enum_dependent | Enum required — create artefact type | `create_artefact` | `{"type": "spec", "title": "My Spec"}` |
| C2-T06 | C2 enum_dependent | Enum optional — create review with severity | `create_review` | `{"artefact_id": "art_abc-123", "verdict": "approve", "rationale": "This rationale has enough length to pass hidden minLength ten", "severity": "high"}` |
| C2-T07 | C2 enum_dependent | Enum multiple — link artefacts relation | `link_artefacts` | `{"source_id": "art_abc-123", "target_ids": ["art_def-456"], "relation": "depends_on"}` |
| C2-T08 | C2 enum_dependent | Enum semantically similar — set artefact state vs update status | `set_artefact_state` | `{"artefact_id": "art_abc-123", "state": "active"}` |
| C3-T09 | C3 nested_structures | Nested object — query_metrics filter | `query_metrics` | `{"filter": {"type": "spec"}}` |
| C3-T10 | C3 nested_structures | Array of objects — submit_evidence | `submit_evidence` | `{"artefact_id": "art_abc-123", "evidence_items": [{"source": "paper", "content": "evidence text from experiment"}]}` |
| C3-T11 | C3 nested_structures | Nested optional — query_metrics with optional group_by and facets | `query_metrics` | `{"filter": {"type": "review", "since": "2026-01-01T00:00:00Z"}, "group_by": "status", "include_facets": true}` |
| C3-T12 | C3 nested_structures | Nested enum — query_metrics filter with enum and group_by | `query_metrics` | `{"filter": {"type": "decision"}, "group_by": "severity"}` |
| C4-T13 | C4 required_optional_ambiguity | R/O ambiguity — omit optional cursor | `search_artefacts` | `{"query": "auth"}` |
| C4-T14 | C4 required_optional_ambiguity | R/O ambiguity — supply optional cursor | `search_artefacts` | `{"query": "spec", "limit": 5, "cursor": "cur_abc123"}` |
| C4-T15 | C4 required_optional_ambiguity | R/O ambiguity — create artefact with optional body and tags | `create_artefact` | `{"type": "decision", "title": "Trade-off", "body": "We chose X over Y because...", "tags": ["arch", "adr-12"]}` |
| C4-T16 | C4 required_optional_ambiguity | R/O ambiguity — semantically similar optional fields | `set_artefact_state` | `{"artefact_id": "art_abc-123", "state": "archived", "comment": "superseded"}` |
| C5-T17 | C5 semantically_similar_tools | Similar tools — search_users | `search_users` | `{"query": "Alice", "department": "engineering"}` |
| C5-T18 | C5 semantically_similar_tools | Similar tools — search_groups | `search_groups` | `{"query": "platform"}` |
| C5-T19 | C5 semantically_similar_tools | Similar tools — search_projects | `search_projects` | `{"query": "Atlas", "status": "active"}` |
| C5-T20 | C5 semantically_similar_tools | Similar tools — disambiguate with overlapping terms | `search_projects` | `{"query": "atlas-platform"}` |
| C6-T21 | C6 constraint_sensitive_hidden | Hidden constraint — numeric range limit 1-100 | `search_artefacts` | `{"query": "test", "limit": 20}` |
| C6-T22 | C6 constraint_sensitive_hidden | Hidden constraint — string pattern ^art_[a-z0-9-]+$ | `get_artefact` | `{"id": "art_valid-001"}` |
| C6-T23 | C6 constraint_sensitive_hidden | Hidden constraint — mutually constrained filter.type ↔ group_by | `query_metrics` | `{"filter": {"type": "spec"}, "group_by": "status"}` |
| C6-T24 | C6 constraint_sensitive_hidden | Hidden constraint — additionalProperties:false and maxLength cause ValidationFailed | `create_artefact` | `{"type": "spec", "title": "Short title"}` |
