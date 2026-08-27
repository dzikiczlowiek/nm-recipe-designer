from __future__ import annotations

SUPPORTED_COLUMN_TYPES = {
    "sampler",
    "expression",
    "llm-text",
    "llm-structured",
    "llm-code",
    "llm-judge",
    "validation",
}

SUPPORTED_SAMPLERS = {
    "category",
    "subcategory",
    "uniform",
    "gaussian",
    "bernoulli",
    "datetime",
    "timedelta",
    "uuid",
    "person",
}

VALIDATOR_CODE_LANGS = {
    "python",
    "javascript",
    "typescript",
    "jsx",
    "tsx",
    "sql:sqlite",
    "sql:postgres",
    "sql:mysql",
    "sql:tsql",
    "sql:bigquery",
    "sql:ansi",
}

DEFAULT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "minLength": 1},
    },
    "required": ["answer"],
    "additionalProperties": False,
}


def recipe_contract() -> dict:
    return {
        "target": "Unsloth Studio Data Recipes / NVIDIA NeMo Data Designer",
        "canonical_payload": {
            "recipe": {
                "model_providers": "array",
                "mcp_providers": "array",
                "model_configs": "array",
                "tool_configs": "array",
                "columns": "non-empty array",
                "processors": "array",
                "seed_config": "optional object",
            },
            "run": {
                "rows": "positive integer",
                "preview": "boolean",
                "output_formats": "array",
            },
            "ui": {
                "nodes": "optional array; Unsloth reconstructs graph if omitted/empty",
                "edges": "optional array; Unsloth reconstructs graph if omitted/empty",
                "layout_direction": "LR or TB",
            },
        },
        "column_types": sorted(SUPPORTED_COLUMN_TYPES),
        "sampler_types": sorted(SUPPORTED_SAMPLERS),
        "built_in_code_validation_languages": sorted(VALIDATOR_CODE_LANGS),
        "notes": [
            "C# is supported by llm-code generation but not by Unsloth's built-in code validator as of the tracked 2026-08 contract.",
            "Use an MCP tool profile or LLM judge for languages without a built-in validator.",
            "Raw Data Designer configs with top-level columns can be wrapped into an Unsloth import payload.",
        ],
    }
