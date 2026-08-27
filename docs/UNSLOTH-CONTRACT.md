# Tracked Unsloth Data Recipe contract

This project targets the Unsloth Studio Data Recipe importer as observed on 2026-08-27.

The importer accepts either a full payload with `recipe`, `run`, and `ui`, or a raw recipe/Data Designer object whose top-level field includes `columns`. Studio parses the recipe configuration and reconstructs visual nodes and edges, so generated payloads do not need hard-coded canvas coordinates.

## Recipe root

```json
{
  "model_providers": [],
  "mcp_providers": [],
  "model_configs": [],
  "seed_config": {},
  "tool_configs": [],
  "columns": [],
  "processors": []
}
```

`seed_config` is optional. `columns` is required and must be an array.

## Column types imported by Studio

`sampler`, `expression`, `llm-text`, `llm-structured`, `llm-code`, `llm-judge`, `validation`.

## MCP providers

Studio recipe tool profiles support `streamable_http` and `stdio`. A tool config identifies providers by name and can restrict `allow_tools`, `max_tool_call_turns`, and `timeout_sec`.

## Authoritative validation

Unsloth Studio's own MCP server exposes `validate_recipe(recipe)`. Enable it on Studio and set `UNSLOTH_STUDIO_MCP_TOKEN` for this project's `validate_with_unsloth` tool. This project intentionally treats upstream validation as the final compatibility gate.

## Known validation-language constraint

The Studio built-in code validator currently recognizes Python; JavaScript/TypeScript/JSX/TSX; and SQLite/Postgres/MySQL/T-SQL/BigQuery/ANSI SQL. `llm-code` can still generate other languages, but those languages need an external verifier or judge.

## Upstream references

- Unsloth `studio/frontend/src/features/recipe-studio/utils/import/importer.ts`
- Unsloth `studio/frontend/src/features/recipe-studio/utils/import/parsers.ts`
- Unsloth `studio/frontend/src/features/recipe-studio/utils/payload/builders-llm.ts`
- Unsloth `studio/backend/mcp_server.py`
- NVIDIA NeMo Data Designer Agent Skill: `skills/data-designer/SKILL.md`
