# Feature Request: `template.required_fields` for content validation

### Goal
Allow projects to declare in `.crosslink/hook-config.json` that specific fields must be present in a `crosslink issue create` description, scoped by template. Issue creation is rejected if required content is missing. This is a backward-compatible extension to the config schema requiring no new event types or hooks.

### Motivation
Issues are sometimes created without recorded rationale; the reasoning is recovered only by reconstructing from indirect evidence, which is costly and lossy. This is a common failure mode in projects relying on issue trackers for organizational memory, particularly when the creator is an agent acting on high-level direction.

Crosslink currently has no built-in mechanism to require content on `crosslink issue create`. `Template::description_prefix` is a default, not a requirement. The `kickoff` command has a similar check (`--run requires a design document`), but it is a one-off. The natural place to enforce a minimum provenance bar is at issue creation.

### Acceptance criteria
1. `crosslink config list` shows a new `template_required_fields` key.
2. `.crosslink/hook-config.json` accepts:
   ```json
   "template_required_fields": {
     "research": [{ "field": "rationale", "pattern": "(?i)\\brationale\\b", "min_chars": 200 }]
   }
   ```
3. `crosslink issue create -t research "Title" -d "Rationale: ..."` succeeds when criteria are met.
4. `crosslink issue create -t research "Title"` fails with a clear error.
5. `crosslink issue create -t research "Title" -d "short"` fails citing `min_chars`.
6. `crosslink issue create -t feature "Title"` succeeds if `feature` has no entry.
7. `Template::description_prefix` behavior is unchanged.
8. `hook-config.local.json` can override settings per-machine.
9. A `--force` flag exists to bypass checks.
10. Checks fire for `issue create`, `create`, `quick`, and `subissue`.

### Proposed implementation
Localized to `src/commands/create.rs` and `src/commands/config_registry.rs`.

1. In `config_registry.rs`, add `ConfigKey`:
   ```rust
   ConfigKey {
     key: "template_required_fields",
     config_type: ConfigType::Map,
     description: "Per-template required fields in issue descriptions.",
     group: ConfigGroup::Workflow,
     hot_swappable: false,
   }
   ```

2. In `create.rs`, add validation:
   ```rust
   if let Some(rules) = get_template_required_fields(dir, tmpl_name) {
       let desc = final_description.as_deref().unwrap_or("");
       for rule in rules {
           if !desc.contains(&rule.field) { bail!("Missing '{}'", rule.field); }
           if desc.len() < rule.min_chars { bail!("Too short"); }
           if let Some(re) = rule.pattern {
               if !re.is_match(desc) { bail!("Pattern mismatch"); }
           }
       }
   }
   ```

3. Add `--force` flag to `create`/`subissue`.
4. Add tests in `src/commands/create.rs`.

### Prior art
- `Template::description_prefix` — defaults, not requirements.
- `comment_discipline: "required"` — enforces typed comments on close.
- `kickoff` content check — existing validation pattern.
- `agent_overrides` — precedent for per-context overrides.

### Out of scope
- Validation of `issue update --description`.
- Cross-template inheritance.
- Free-form regex with capture groups.
- Programmatic validators (e.g., shell scripts).

### Example
```json
{ "template_required_fields": { "research": [{ "field": "Rationale", "min_chars": 200 }] } }
```
- `crosslink issue create "Title" -t research -d "Rationale: ..."` → succeeds.
- `crosslink issue create "Title" -t research` → fails.
- `crosslink issue create "Title" -t research -d "..." --force` → succeeds.

### Test cases
- `test_create_research_succeeds_with_required_fields`
- `test_create_research_fails_without_description`
- `test_create_research_fails_with_short_description`
- `test_create_research_force_override_succeeds`
- `test_create_research_local_config_override_relaxes_check`
- `test_create_feature_succeeds_without_required_fields`
- `test_subissue_inherits_template_required_fields`
- `test_quick_command_enforces_template_required_fields`

### Why this fits Crosslink's design philosophy
Crosslink's hook model is **configure-don't-extend**. This feature adds a config key within the existing lifecycle rather than a new plugin API. Escape hatches (`--force`, `hook-config.local.json`) preserve the "agents handle bookkeeping automatically" principle by making enforcement the default without making it absolute.
