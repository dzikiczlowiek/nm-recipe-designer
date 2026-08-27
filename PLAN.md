# Implementation plan

## Product boundary

`nm-recipe-designer` is a recipe **design/control layer**, not another dataset-generation runtime. Unsloth Studio / NeMo Data Designer remains the execution engine.

The canonical flow is:

`user intent -> agent skill -> recipe payload -> local validation -> Unsloth validation -> JSON import -> Studio execution`

## Architecture

### Agent Skill

Owns the reasoning-heavy work: training objective, diversity axes, output schema, model/judge strategy, seed strategy and whether tools are needed. It should produce explicit, reviewable recipe JSON rather than opaque code generation.

### MCP server

Owns deterministic operations:

- expose the tracked recipe contract;
- create a baseline scaffold;
- normalize Data Designer / Unsloth payloads;
- add MCP providers and tool profiles safely;
- lint aliases and references;
- delegate final validation to Unsloth Studio;
- explain a recipe to an agent or human.

### Validation strategy

Three levels:

1. **Shape/reference gate** — local, fast, no runtime required.
2. **Unsloth contract gate** — call Studio `validate_recipe` through MCP.
3. **Execution gate** — preview a small dataset in Studio and inspect failure/quality metrics. This is not automated in v0.1 because upstream Studio MCP currently validates and reads recipe jobs but does not expose a clean general-purpose create/save/run-recipe mutation.

## Design decisions

- Generate native Unsloth/Data Designer JSON instead of a custom DSL.
- Keep visual layout empty; Studio's importer reconstructs nodes/edges.
- Do not write directly into Studio IndexedDB.
- Do not embed a second LLM in the MCP server. The connected agent is the designer.
- Treat Unsloth's validator as authoritative; local validation is a useful preflight, not a replacement.
- Keep stdio MCP secrets in environment/config, never serialized into recipe files.

## Quality gates for new features

A change is accepted only when:

- unit tests cover the compatibility rule;
- generated payload passes local validation;
- an example or fixture covers new recipe syntax;
- upstream contract references are updated if compatibility changed;
- no secret-bearing fields are introduced into shareable recipe output by default.
