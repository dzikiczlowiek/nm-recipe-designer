from __future__ import annotations

from typing import Any

from .convert import normalize_recipe


def explain_recipe(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_recipe(payload)
    recipe = normalized["recipe"]
    columns = recipe.get("columns", [])
    steps = []
    for column in columns:
        if not isinstance(column, dict):
            continue
        step = {
            "name": column.get("name"),
            "type": column.get("column_type"),
            "drop": bool(column.get("drop", False)),
        }
        if column.get("model_alias"):
            step["model_alias"] = column.get("model_alias")
        if column.get("tool_alias"):
            step["tool_alias"] = column.get("tool_alias")
        if column.get("target_columns"):
            step["targets"] = column.get("target_columns")
        steps.append(step)

    return {
        "rows": normalized["run"]["rows"],
        "providers": [p.get("name") for p in recipe.get("model_providers", []) if isinstance(p, dict)],
        "models": [m.get("alias") for m in recipe.get("model_configs", []) if isinstance(m, dict)],
        "mcp_providers": [p.get("name") for p in recipe.get("mcp_providers", []) if isinstance(p, dict)],
        "tool_profiles": [t.get("tool_alias") for t in recipe.get("tool_configs", []) if isinstance(t, dict)],
        "steps": steps,
        "processors": recipe.get("processors", []),
    }
