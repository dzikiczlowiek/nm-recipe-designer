---
name: nm-recipe-designer
description: Design NVIDIA NeMo Data Designer synthetic-data recipes that can be imported and edited in Unsloth Studio/Desktop Data Recipes.
argument-hint: [describe the dataset or training data you want]
license: Apache-2.0
metadata:
  owner: dzikiczlowiek
---

# Goal

Turn the user's dataset intent into a high-quality, editable Unsloth Data Recipe payload. The canonical deliverable is JSON importable through **Unsloth Studio -> Data Recipes -> Import**.

# Preferred tools

When the `NM Recipe Designer` MCP server is connected, use its tools instead of inventing compatibility details:

1. `recipe_contract` when you need the current supported shape.
2. `design_recipe` for a baseline scaffold.
3. `add_mcp_tool_profile` when generation or verification needs external tools.
4. `validate_recipe` after every material edit.
5. `validate_with_unsloth` as the final gate when a running Unsloth Studio MCP endpoint is available.
6. `explain_recipe` when reviewing or presenting an existing recipe.

The user does not need the MCP server for the final recipe: a JSON payload is sufficient for Unsloth import.

# Workflow

## 1. Model the training objective

Identify:

- final training record shape;
- diversity axes worth sampling;
- which fields are generation scaffolding (`drop: true`) versus training outputs;
- whether output is text, code, or strict structured data;
- objective quality gates;
- whether an existing seed dataset is required;
- whether external MCP tools materially improve grounding or verification.

Do not add samplers merely to make the graph larger. Every sampler must create useful coverage.

## 2. Design the graph

Prefer this order unless the task requires something else:

`seed/samplers -> instruction/context -> answer/trajectory -> deterministic validation -> LLM judge -> processor/export shape`

Use `llm-structured` whenever downstream training requires a strict schema. Use `llm-code` for generated source code. Use an `llm-judge` for semantic properties that cannot be checked deterministically.

For coding data, deterministic execution/compilation is stronger evidence than an LLM judge. If Unsloth's built-in validator does not support the language, attach a suitable MCP tool profile rather than pretending the built-in validator covers it.

## 3. Unsloth compatibility rules

Supported Studio-imported column types in the tracked contract:

- `sampler`
- `expression`
- `llm-text`
- `llm-structured`
- `llm-code`
- `llm-judge`
- `validation`

Every LLM column must reference an existing `model_alias`. Tool-enabled LLM columns reference an existing `tool_alias`. Jinja references must point to existing columns.

Built-in code validation currently covers Python, JavaScript/TypeScript/JSX/TSX and SQL dialects exposed by Studio. **Do not create a built-in validation node for C#/.NET.** For C#, prefer a compiler/test MCP tool plus an LLM judge.

Unsloth reconstructs nodes and edges during import. Keep `ui.nodes` and `ui.edges` empty unless preserving intentional manual layout/notes from an existing recipe.

## 4. MCP inside a recipe

An HTTP provider has this shape:

```json
{
  "provider_type": "streamable_http",
  "name": "docs",
  "endpoint": "https://example/mcp"
}
```

A local provider has this shape:

```json
{
  "provider_type": "stdio",
  "name": "compiler",
  "command": "uv",
  "args": ["run", "compiler-mcp"]
}
```

Bind providers through a tool profile:

```json
{
  "tool_alias": "verification-tools",
  "providers": ["compiler"],
  "allow_tools": ["compile", "run_tests"],
  "max_tool_call_turns": 5
}
```

Then set `"tool_alias": "verification-tools"` on the LLM column that may call the tools.

Do not embed secrets in recipes. Use environment variables/API-key configuration in Studio.

## 5. Validation gates

A recipe is not done until:

- local structural validation passes;
- all Jinja references resolve;
- providers/models/tool aliases resolve;
- helper columns are dropped intentionally;
- quality gates match the training objective;
- final output schema is explicit;
- authoritative `validate_with_unsloth` passes when Studio is reachable.

If authoritative validation is unavailable, state that only local compatibility validation was run.

# Output

For an implementation task, create a `*.recipe.json` file containing the full payload:

```json
{
  "recipe": {
    "model_providers": [],
    "mcp_providers": [],
    "model_configs": [],
    "tool_configs": [],
    "columns": [],
    "processors": []
  },
  "run": {
    "rows": 100,
    "preview": false,
    "output_formats": ["jsonl"]
  },
  "ui": {
    "nodes": [],
    "edges": [],
    "layout_direction": "LR"
  }
}
```

Also provide a short design note describing diversity, verification, expected training shape, and any unresolved provider/model values the user must choose in Studio.
