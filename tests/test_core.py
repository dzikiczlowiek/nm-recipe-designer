from nm_recipe_designer.builder import design_recipe
from nm_recipe_designer.convert import normalize_recipe
from nm_recipe_designer.validate import validate_recipe


def test_design_csharp_recipe_warns_but_is_valid():
    payload = design_recipe("Generate realistic .NET C# flaky test repair tasks", code_language="csharp")
    result = validate_recipe(payload)
    assert result["valid"] is True
    assert not any(c.get("column_type") == "validation" for c in payload["recipe"]["columns"])
    assert any("C#" in item["message"] for item in result["warnings"])


def test_design_python_recipe_adds_code_validation():
    payload = design_recipe("Generate Python coding exercises")
    assert any(c.get("column_type") == "validation" for c in payload["recipe"]["columns"])
    assert validate_recipe(payload)["valid"] is True


def test_normalize_raw_data_designer_config():
    payload = normalize_recipe({"columns": [{"column_type": "sampler", "name": "x", "sampler_type": "category", "params": {"values": ["a"]}}]})
    assert payload["recipe"]["columns"][0]["name"] == "x"
    assert payload["ui"]["nodes"] == []


def test_unknown_jinja_reference_is_rejected():
    payload = design_recipe("Generate support answers", response_mode="text")
    payload["recipe"]["columns"][2]["prompt"] += " {{ missing_column }}"
    result = validate_recipe(payload)
    assert result["valid"] is False
    assert any("missing_column" in error["message"] for error in result["errors"])


def test_add_mcp_tool_profile_binds_llm_column():
    from nm_recipe_designer.mutate import add_mcp_tool_profile

    payload = design_recipe("Generate support answers", response_mode="text")
    updated = add_mcp_tool_profile(
        payload,
        profile_name="docs",
        provider_name="context7",
        endpoint="https://example.invalid/mcp",
        allow_tools=["resolve-library-id", "query-docs"],
        target_columns=["response"],
    )
    assert updated["recipe"]["tool_configs"][0]["tool_alias"] == "docs"
    response = next(c for c in updated["recipe"]["columns"] if c["name"] == "response")
    assert response["tool_alias"] == "docs"
    assert validate_recipe(updated)["valid"] is True
