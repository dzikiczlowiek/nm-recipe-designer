from __future__ import annotations

import os
from typing import Any


def _normalize_mcp_url(url: str) -> str:
    value = url.strip().rstrip("/")
    if not value:
        value = "http://127.0.0.1:8888"
    if not value.endswith("/mcp"):
        value += "/mcp"
    return value


async def validate_with_unsloth(payload: dict[str, Any], url: str = "http://127.0.0.1:8888") -> dict[str, Any]:
    """Call Unsloth Studio's authoritative validate_recipe MCP tool.

    The bearer token is read from UNSLOTH_STUDIO_MCP_TOKEN and is never accepted
    as a tool argument, reducing accidental secret exposure in agent transcripts.
    """
    try:
        from fastmcp import Client
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("fastmcp is required for upstream validation") from exc

    token = os.getenv("UNSLOTH_STUDIO_MCP_TOKEN")
    kwargs: dict[str, Any] = {}
    if token:
        kwargs["auth"] = token
    async with Client(_normalize_mcp_url(url), **kwargs) as client:
        result = await client.call_tool("validate_recipe", {"recipe": payload.get("recipe", payload)})
        data = result.data
        if isinstance(data, dict):
            return data
        return {"valid": False, "errors": [{"message": "Unsloth returned an unexpected validation result."}], "raw": str(data)}
