from __future__ import annotations

from copy import deepcopy
from typing import Any


def _as_list(value: Any) -> list:
    return list(value) if isinstance(value, list) else []


def normalize_recipe(payload: dict[str, Any], *, rows: int | None = None, preview: bool | None = None) -> dict[str, Any]:
    """Normalize a Data Designer or Unsloth payload into an importable Unsloth payload.

    Accepted inputs:
      * full Unsloth payload: {"recipe": {...}, "run": {...}, "ui": {...}}
      * raw Data Designer config: {"columns": [...], ...}
      * common wrapper: {"data_designer": {"columns": [...]}}
    """
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")

    source = deepcopy(payload)
    if isinstance(source.get("recipe"), dict):
        recipe = deepcopy(source["recipe"])
    elif isinstance(source.get("data_designer"), dict):
        recipe = deepcopy(source["data_designer"])
    else:
        recipe = deepcopy(source)

    recipe.setdefault("model_providers", [])
    recipe.setdefault("mcp_providers", [])
    recipe.setdefault("model_configs", [])
    recipe.setdefault("tool_configs", [])
    recipe.setdefault("columns", [])
    recipe.setdefault("processors", [])

    run_in = source.get("run") if isinstance(source.get("run"), dict) else {}
    run = {
        "rows": int(rows if rows is not None else run_in.get("rows", 100)),
        "preview": bool(preview if preview is not None else run_in.get("preview", False)),
        "output_formats": _as_list(run_in.get("output_formats")) or ["jsonl"],
    }
    for key in ("execution_type", "run_config", "dataset_name", "artifact_path", "merge_batches", "run_name"):
        if key in run_in:
            run[key] = deepcopy(run_in[key])

    ui_in = source.get("ui") if isinstance(source.get("ui"), dict) else {}
    ui = deepcopy(ui_in)
    ui.setdefault("nodes", [])
    ui.setdefault("edges", [])
    ui.setdefault("layout_direction", "LR")

    return {"recipe": recipe, "run": run, "ui": ui}
