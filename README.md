# nm-recipe-designer

Agent Skill + MCP server for designing **NVIDIA NeMo Data Designer** recipes that can be imported and edited in **Unsloth Studio/Desktop -> Data Recipes**.

The project solves the missing control-plane layer around Unsloth recipes: an agent can design a recipe from natural language, normalize raw Data Designer configs, add MCP tool profiles, validate compatibility, and optionally call Unsloth Studio's own `validate_recipe` MCP tool as the final gate.

## What is included

- `skills/nm-recipe-designer/SKILL.md` — agent workflow for high-quality recipe design.
- `nm-recipe-mcp` — FastMCP server with recipe design/validation tools.
- `nm-recipe-designer` — small CLI for design/normalize/validate workflows.
- local compatibility validator — catches aliases, Jinja refs, unsupported column types and validator-language mismatches before import.
- upstream validation — optional delegation to a running Unsloth Studio MCP endpoint.
- example C#/.NET recipe showing the important limitation that C# needs an MCP/external verifier rather than Studio's built-in code validator.

## Install

```bash
uv tool install .
# or
pip install -e .
```

Run the MCP server over stdio:

```bash
nm-recipe-mcp
```

Typical MCP client configuration:

```json
{
  "mcpServers": {
    "nm-recipe-designer": {
      "command": "uvx",
      "args": ["--from", "/path/to/nm-recipe-designer", "nm-recipe-mcp"]
    }
  }
}
```

During local development, using the repository venv is simpler:

```json
{
  "mcpServers": {
    "nm-recipe-designer": {
      "command": "/path/to/nm-recipe-designer/.venv/bin/nm-recipe-mcp"
    }
  }
}
```

## MCP tools

| Tool | Purpose |
|---|---|
| `recipe_contract` | Compatibility contract used by agents |
| `design_recipe` | Deterministic baseline from a dataset description |
| `normalize_recipe` | Wrap raw Data Designer JSON into Unsloth import shape |
| `add_mcp_tool_profile` | Add HTTP/stdio MCP provider + tool profile and bind it to LLM columns |
| `validate_recipe` | Fast local structural/reference validation |
| `validate_with_unsloth` | Call running Unsloth Studio's authoritative `validate_recipe` MCP tool |
| `explain_recipe` | Summarize an existing graph |

The **Skill** is the primary intelligent designer. The MCP's `design_recipe` intentionally provides a deterministic scaffold rather than hiding another LLM inside the server. This keeps model choice and reasoning in the caller/agent while MCP owns compatibility and validation.

## Generate a baseline

```bash
nm-recipe-designer design \
  "Generate .NET C# flaky test repair training data" \
  --language csharp \
  --rows 500 \
  -o flaky-tests.recipe.json
```

Then in Unsloth Studio:

`Data Recipes -> Import -> paste the JSON`

Studio can reconstruct the visual graph from the recipe payload; generated files deliberately keep `ui.nodes` and `ui.edges` empty.

## Validate against Unsloth itself

Enable Unsloth Studio MCP, then expose the same bearer token to this process:

```bash
export UNSLOTH_STUDIO_MCP_TOKEN='...'
```

The MCP tool `validate_with_unsloth` defaults to `http://127.0.0.1:8888/mcp` and calls Unsloth's own `validate_recipe` implementation.

## Why Skill + MCP

The two layers have different jobs:

- **Skill**: dataset architecture, diversity, prompts, schemas, judges, verification strategy.
- **MCP/core**: machine-readable contract, deterministic transformations, tool-profile wiring, compatibility validation, Unsloth validation bridge.

Trying to put all design intelligence into the MCP would require choosing and configuring another LLM inside the server and would duplicate the calling agent.

See [PLAN.md](PLAN.md), [ROADMAP.md](ROADMAP.md), and [docs/UNSLOTH-CONTRACT.md](docs/UNSLOTH-CONTRACT.md).
