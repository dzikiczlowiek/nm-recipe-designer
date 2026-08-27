from __future__ import annotations

import re
from typing import Any

from .contract import SUPPORTED_COLUMN_TYPES, VALIDATOR_CODE_LANGS
from .convert import normalize_recipe

_JINJA_REF = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)")


def validate_recipe(payload: dict[str, Any]) -> dict[str, Any]:
    """Fast local structural/semantic validation.

    This intentionally does not replace Unsloth/Data Designer validation. Use
    validate_with_unsloth for the authoritative validator when Studio is running.
    """
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    try:
        normalized = normalize_recipe(payload)
    except Exception as exc:
        return {"valid": False, "errors": [{"message": str(exc), "path": "$"}], "warnings": []}

    recipe = normalized["recipe"]
    columns = recipe.get("columns")
    if not isinstance(columns, list) or not columns:
        return {"valid": False, "errors": [{"message": "Recipe must include columns.", "path": "recipe.columns"}], "warnings": []}

    names: set[str] = set()
    model_aliases = {m.get("alias") for m in recipe.get("model_configs", []) if isinstance(m, dict) and m.get("alias")}
    provider_names = {p.get("name") for p in recipe.get("model_providers", []) if isinstance(p, dict) and p.get("name")}
    tool_aliases = {t.get("tool_alias") for t in recipe.get("tool_configs", []) if isinstance(t, dict) and t.get("tool_alias")}

    for index, model in enumerate(recipe.get("model_configs", [])):
        if not isinstance(model, dict):
            errors.append({"message": "Model config must be an object.", "path": f"recipe.model_configs[{index}]"})
            continue
        provider = model.get("provider")
        if provider and provider not in provider_names:
            errors.append({"message": f"Unknown provider '{provider}'.", "path": f"recipe.model_configs[{index}].provider"})

    for index, column in enumerate(columns):
        path = f"recipe.columns[{index}]"
        if not isinstance(column, dict):
            errors.append({"message": "Column must be an object.", "path": path})
            continue
        name = str(column.get("name") or "").strip()
        if not name:
            errors.append({"message": "Column missing name.", "path": path})
            continue
        if name in names:
            errors.append({"message": f"Duplicate column name '{name}'.", "path": f"{path}.name"})
        names.add(name)

        column_type = column.get("column_type")
        if column_type not in SUPPORTED_COLUMN_TYPES:
            errors.append({"message": f"Unsupported column_type '{column_type}'.", "path": f"{path}.column_type"})

        if isinstance(column_type, str) and column_type.startswith("llm-"):
            model_alias = column.get("model_alias")
            if model_alias not in model_aliases:
                errors.append({"message": f"Unknown model_alias '{model_alias}'.", "path": f"{path}.model_alias"})
            tool_alias = column.get("tool_alias")
            if tool_alias and tool_alias not in tool_aliases:
                errors.append({"message": f"Unknown tool_alias '{tool_alias}'.", "path": f"{path}.tool_alias"})

        if column_type == "validation":
            targets = column.get("target_columns")
            if not isinstance(targets, list) or not targets:
                errors.append({"message": "Validation requires target_columns.", "path": f"{path}.target_columns"})
            lang = (column.get("validator_params") or {}).get("code_lang") if isinstance(column.get("validator_params"), dict) else None
            if column.get("validator_type") == "code" and lang not in VALIDATOR_CODE_LANGS:
                errors.append({"message": f"Unsupported built-in validator language '{lang}'.", "path": f"{path}.validator_params.code_lang"})

    available = set(names)
    for index, column in enumerate(columns):
        if not isinstance(column, dict):
            continue
        path = f"recipe.columns[{index}]"
        strings: list[str] = []
        for key in ("prompt", "system_prompt", "expr"):
            value = column.get(key)
            if isinstance(value, str):
                strings.append(value)
        for value in strings:
            for ref in _JINJA_REF.findall(value):
                if ref not in available:
                    errors.append({"message": f"Unknown Jinja column reference '{ref}'.", "path": path})

        if column.get("column_type") == "sampler" and column.get("sampler_type") == "subcategory":
            parent = (column.get("params") or {}).get("category") if isinstance(column.get("params"), dict) else None
            if parent not in available:
                errors.append({"message": f"Unknown subcategory parent '{parent}'.", "path": f"{path}.params.category"})

        if column.get("column_type") == "llm-code" and str(column.get("code_lang", "")).lower() in {"c#", "csharp", "dotnet"}:
            warnings.append({"message": "Unsloth currently has no built-in C# code validator; use an MCP tool profile and/or LLM judge.", "path": path})

    run = normalized["run"]
    if not isinstance(run.get("rows"), int) or run["rows"] < 1:
        errors.append({"message": "run.rows must be >= 1.", "path": "run.rows"})

    return {"valid": not errors, "errors": errors, "warnings": warnings, "normalized": normalized}
