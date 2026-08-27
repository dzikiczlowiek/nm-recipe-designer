from __future__ import annotations

from copy import deepcopy
from typing import Any

from .convert import normalize_recipe


def add_mcp_tool_profile(
    payload: dict[str, Any],
    *,
    profile_name: str,
    provider_name: str,
    endpoint: str = "",
    command: str = "",
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    allow_tools: list[str] | None = None,
    target_columns: list[str] | None = None,
    max_tool_call_turns: int = 5,
    timeout_sec: float | None = None,
) -> dict[str, Any]:
    """Attach an MCP provider/tool profile and optionally bind it to LLM columns."""
    if not profile_name.strip() or not provider_name.strip():
        raise ValueError("profile_name and provider_name are required")
    if bool(endpoint.strip()) == bool(command.strip()):
        raise ValueError("provide exactly one of endpoint or command")

    result = normalize_recipe(payload)
    recipe = deepcopy(result["recipe"])
    providers = [p for p in recipe.get("mcp_providers", []) if isinstance(p, dict) and p.get("name") != provider_name]
    if command.strip():
        provider: dict[str, Any] = {
            "provider_type": "stdio",
            "name": provider_name,
            "command": command,
            "args": list(args or []),
            "env": dict(env or {}),
        }
    else:
        provider = {
            "provider_type": "streamable_http",
            "name": provider_name,
            "endpoint": endpoint,
        }
    providers.append(provider)
    recipe["mcp_providers"] = providers

    tool_configs = [t for t in recipe.get("tool_configs", []) if isinstance(t, dict) and t.get("tool_alias") != profile_name]
    tool_config: dict[str, Any] = {
        "tool_alias": profile_name,
        "providers": [provider_name],
        "max_tool_call_turns": max_tool_call_turns,
    }
    if allow_tools:
        tool_config["allow_tools"] = list(allow_tools)
    if timeout_sec is not None:
        tool_config["timeout_sec"] = timeout_sec
    tool_configs.append(tool_config)
    recipe["tool_configs"] = tool_configs

    targets = set(target_columns or [])
    if targets:
        for column in recipe.get("columns", []):
            if isinstance(column, dict) and column.get("name") in targets:
                if not str(column.get("column_type", "")).startswith("llm-"):
                    raise ValueError(f"tool profile target '{column.get('name')}' is not an LLM column")
                column["tool_alias"] = profile_name

    result["recipe"] = recipe
    return result
