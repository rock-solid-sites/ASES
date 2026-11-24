---
name: ases-workflow
description: Route requests for builder prompts, agent delegation, build preparation, workflow selection and MCP connector diagnostics to the relevant ASES skill.
---
# ASES Workflow

For agent prompts use the canonical prompt skill. For workflow selection use workflow-orchestration. For substantial bounded builds use compile-build, but skip it for trivial changes. For connector setup and diagnosis use custom-mcp-connector. Canonical sources are in the repository skills directory; plugin releases contain pinned copies. Validate version status before claiming currency.
