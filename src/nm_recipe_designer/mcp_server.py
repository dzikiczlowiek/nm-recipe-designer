from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .builder import design_recipe as _design_recipe
from .contract import recipe_contract as _recipe_contract
from .convert import normalize_recipe as _normalize_recipe
from .explain import explain_recipe as _explain_recipe
from .mutate import add_mcp_tool_profile as _add_mcp_tool_profile
from .unsloth_client import validate_with_unsloth as _validate_with_unsloth
from .validate import validate_recipe as _validate_recipe

mcp = FastMCP(
    "NM Recipe Designer",
    instructions=(
        "Design and validate NVIDIA NeMo Data Designer recipes that can be imported into Unsloth Studio. "
        "Prefer local validation first; use validate_with_unsloth when an Unsloth Studio MCP endpoint is available."
    ),
)


@mcp.tool
def recipe_contract() -> dict[str, Any]:
    """Return the supported Unsloth/Data Designer recipe contract and important compatibility notes."""
    return _recipe_contract()


@mcp.tool
def design_recipe(
    description: str,
    rows: int = 100,
    response_mode: str = "auto",
    code_language: str = "auto",
    provider_name: str = "openai-compatible",
    endpoint: str = "",
    model_alias: str = "generator",
    model: str = "",
    temperature: float = 0.7,
    include_judge: bool = True,
    include_validation: bool = True,
) -> dict[str, Any]:
    """Generate a deterministic baseline Unsloth-importable recipe from a dataset description."""
    if response_mode not in {"auto", "text", "code", "structured"}:
        raise ValueError("response_mode must be auto, text, code, or structured")
    return _design_recipe(
        description,
        rows=rows,
        response_mode=response_mode,  # type: ignore[arg-type]
        code_language=code_language,
        provider_name=provider_name,
        endpoint=endpoint,
        model_alias=model_alias,
        model=model,
        temperature=temperature,
        include_judge=include_judge,
        include_validation=include_validation,
    )


@mcp.tool
def normalize_recipe(payload: dict[str, Any], rows: int | None = None, preview: bool | None = None) -> dict[str, Any]:
    """Convert raw Data Designer config or partial recipe payload into Unsloth's import payload shape."""
    return _normalize_recipe(payload, rows=rows, preview=preview)


@mcp.tool
def validate_recipe(payload: dict[str, Any]) -> dict[str, Any]:
    """Run fast local structural and reference validation against the tracked Unsloth contract."""
    return _validate_recipe(payload)


@mcp.tool
async def validate_with_unsloth(payload: dict[str, Any], url: str = "http://127.0.0.1:8888") -> dict[str, Any]:
    """Validate through a running Unsloth Studio MCP server; token comes from UNSLOTH_STUDIO_MCP_TOKEN."""
    return await _validate_with_unsloth(payload, url=url)


@mcp.tool
def add_mcp_tool_profile(
    payload: dict[str, Any],
    profile_name: str,
    provider_name: str,
    endpoint: str = "",
    command: str = "",
    args: list[str] | None = None,
    allow_tools: list[str] | None = None,
    target_columns: list[str] | None = None,
    max_tool_call_turns: int = 5,
    timeout_sec: float | None = None,
) -> dict[str, Any]:
    """Add an HTTP or stdio MCP tool profile and bind it to selected LLM columns."""
    return _add_mcp_tool_profile(
        payload,
        profile_name=profile_name,
        provider_name=provider_name,
        endpoint=endpoint,
        command=command,
        args=args,
        allow_tools=allow_tools,
        target_columns=target_columns,
        max_tool_call_turns=max_tool_call_turns,
        timeout_sec=timeout_sec,
    )


@mcp.tool
def explain_recipe(payload: dict[str, Any]) -> dict[str, Any]:
    """Summarize recipe providers, models, tool profiles and generation steps."""
    return _explain_recipe(payload)


def main() -> None:
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
