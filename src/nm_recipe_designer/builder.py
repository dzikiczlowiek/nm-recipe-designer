from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

from .contract import DEFAULT_OUTPUT_SCHEMA, VALIDATOR_CODE_LANGS

ResponseMode = Literal["auto", "text", "code", "structured"]

_CODE_HINTS = {
    "c#": "csharp",
    "csharp": "csharp",
    ".net": "csharp",
    "dotnet": "csharp",
    "python": "python",
    "typescript": "typescript",
    "javascript": "javascript",
    "tsx": "tsx",
    "jsx": "jsx",
    "sql": "sql:sqlite",
    "postgres": "sql:postgres",
    "postgresql": "sql:postgres",
    "mysql": "sql:mysql",
    "tsql": "sql:tsql",
}


def _infer_code_language(description: str, requested: str) -> str:
    if requested and requested != "auto":
        return requested
    lowered = description.lower()
    for token, language in _CODE_HINTS.items():
        if token in lowered:
            return language
    return "python"


def _infer_mode(description: str, requested: ResponseMode) -> str:
    if requested != "auto":
        return requested
    lowered = description.lower()
    if any(token in lowered for token in ("json", "structured", "schema", "extract", "classification")):
        return "structured"
    if any(token in lowered for token in ("code", "coding", "program", "function", "bug", "refactor", "test", "c#", ".net", "python", "sql")):
        return "code"
    return "text"


def _validator_language(code_language: str) -> str | None:
    if code_language in VALIDATOR_CODE_LANGS:
        return code_language
    if code_language == "sql":
        return "sql:sqlite"
    return None


def design_recipe(
    description: str,
    *,
    rows: int = 100,
    response_mode: ResponseMode = "auto",
    code_language: str = "auto",
    provider_name: str = "openai-compatible",
    endpoint: str = "",
    model_alias: str = "generator",
    model: str = "",
    temperature: float = 0.7,
    include_judge: bool = True,
    include_validation: bool = True,
    output_schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a useful baseline recipe from a dataset description.

    This function is intentionally deterministic. The Agent Skill is responsible for
    richer domain-specific design; this MCP/core function gives agents a valid baseline
    that can be edited and validated.
    """
    description = description.strip()
    if not description:
        raise ValueError("description must not be empty")
    if rows < 1:
        raise ValueError("rows must be >= 1")

    mode = _infer_mode(description, response_mode)
    language = _infer_code_language(description, code_language)

    columns: list[dict[str, Any]] = [
        {
            "column_type": "sampler",
            "name": "difficulty",
            "drop": True,
            "sampler_type": "category",
            "params": {
                "values": ["basic", "intermediate", "advanced"],
                "weights": [0.2, 0.5, 0.3],
            },
        },
        {
            "column_type": "sampler",
            "name": "variation",
            "drop": True,
            "sampler_type": "category",
            "params": {
                "values": ["typical", "edge-case", "debugging", "adversarial"],
                "weights": [0.45, 0.2, 0.2, 0.15],
            },
        },
        {
            "column_type": "llm-text",
            "name": "instruction",
            "drop": False,
            "model_alias": model_alias,
            "prompt": (
                "Create one realistic training instruction for this dataset goal:\n"
                f"{description}\n\n"
                "Difficulty: {{ difficulty }}\nVariation: {{ variation }}\n"
                "Make the task concrete, self-contained and unambiguous. "
                "Do not answer it. Return only the instruction."
            ),
            "with_trace": "none",
            "extract_reasoning_content": False,
        },
    ]

    answer_prompt = (
        "Produce the ideal training answer for the task below.\n\n"
        "Dataset goal:\n" + description + "\n\n"
        "Task:\n{{ instruction }}\n\n"
        "Be correct, complete and concise. Do not mention dataset generation."
    )
    if mode == "code":
        answer: dict[str, Any] = {
            "column_type": "llm-code",
            "name": "response",
            "drop": False,
            "model_alias": model_alias,
            "prompt": answer_prompt + "\nReturn code only, without markdown fences.",
            "with_trace": "none",
            "extract_reasoning_content": False,
            "code_lang": language,
        }
    elif mode == "structured":
        answer = {
            "column_type": "llm-structured",
            "name": "response",
            "drop": False,
            "model_alias": model_alias,
            "prompt": answer_prompt + "\nReturn data matching the required JSON schema.",
            "with_trace": "none",
            "extract_reasoning_content": False,
            "output_format": deepcopy(output_schema or DEFAULT_OUTPUT_SCHEMA),
        }
    else:
        answer = {
            "column_type": "llm-text",
            "name": "response",
            "drop": False,
            "model_alias": model_alias,
            "prompt": answer_prompt,
            "with_trace": "none",
            "extract_reasoning_content": False,
        }
    columns.append(answer)

    validator_lang = _validator_language(language) if mode == "code" else None
    if include_validation and validator_lang:
        columns.append(
            {
                "column_type": "validation",
                "name": "code_validation",
                "drop": False,
                "target_columns": ["response"],
                "validator_type": "code",
                "validator_params": {"code_lang": validator_lang},
                "batch_size": 10,
            }
        )

    if include_judge:
        columns.append(
            {
                "column_type": "llm-judge",
                "name": "quality",
                "drop": False,
                "model_alias": model_alias,
                "prompt": (
                    "Evaluate the candidate answer against the instruction and dataset goal.\n\n"
                    "Dataset goal:\n" + description + "\n\n"
                    "Instruction:\n{{ instruction }}\n\nCandidate answer:\n{{ response }}"
                ),
                "with_trace": "none",
                "extract_reasoning_content": False,
                "scores": [
                    {
                        "name": "correctness",
                        "description": "The answer is factually and technically correct.",
                        "options": {"0": "wrong", "1": "partly correct", "2": "correct", "3": "excellent"},
                    },
                    {
                        "name": "instruction_following",
                        "description": "The answer follows the instruction and requested format.",
                        "options": {"0": "fails", "1": "partial", "2": "good", "3": "excellent"},
                    },
                ],
            }
        )

    provider = {
        "name": provider_name,
        "endpoint": endpoint,
        "provider_type": "openai",
        "extra_headers": {},
        "extra_body": {},
    }
    model_config = {
        "alias": model_alias,
        "model": model,
        "provider": provider_name,
        "inference_parameters": {"temperature": temperature},
    }

    return {
        "recipe": {
            "model_providers": [provider],
            "mcp_providers": [],
            "model_configs": [model_config],
            "tool_configs": [],
            "columns": columns,
            "processors": [],
        },
        "run": {"rows": rows, "preview": False, "output_formats": ["jsonl"]},
        "ui": {"nodes": [], "edges": [], "layout_direction": "LR"},
    }
