# Roadmap

## M0 — Usable local designer — DONE

**Goal:** generate/import recipes without manually drawing graphs.

Delivered:

- Agent Skill;
- FastMCP server;
- deterministic recipe scaffold;
- Data Designer -> Unsloth normalization;
- MCP tool-profile wiring;
- local structural/reference validation;
- bridge to Unsloth's own `validate_recipe` MCP tool;
- CLI and C# example;
- tests and compatibility documentation.

**Gate:** a generated JSON imports into the current Unsloth Studio importer and local unit tests pass.

## M1 — Contract fidelity and round-trip fixtures

- Add fixtures from every current Unsloth learning recipe.
- Expand sampler/seed/expression/processor validation to mirror Studio more closely.
- Add snapshot tests for importable payloads.
- Add `doctor` command that checks FastMCP, Unsloth endpoint and contract version.
- Track upstream Unsloth changes automatically in CI.

**Gate:** all upstream learning recipes normalize and lint without false errors; contract-drift CI detects importer changes.

## M2 — Preview loop

- Add optional Studio integration for recipe preview when upstream exposes a stable run mutation, or provide a narrowly scoped adapter to the Data Recipe REST API.
- Return sample rows, generation errors and validator/judge summaries to the agent.
- Add `design -> validate -> preview -> revise` loop to the Skill.

**Gate:** agent can generate a recipe, execute 5-20 preview rows and make at least one evidence-based revision without browser interaction.

## M3 — Verifiable coding recipes

- Publish companion MCP verifier(s) for compile/test execution.
- First-class profiles for C#/.NET, Python, TypeScript and SQL.
- C# tools: compile project/snippet, run tests, capture diagnostics, mutation/flaky-test scenarios.
- Recipe templates that combine deterministic verification with LLM judging.

**Gate:** C# coding recipe can reject non-compiling outputs and failing tests deterministically before export.

## M4 — Recipe optimizer

- Analyze preview distributions and judge/validator pass rates.
- Detect collapsed samplers, redundant columns, weak judges and excessive generation cost.
- Propose recipe diffs rather than regenerating whole graphs.
- Add budget-aware model routing for generator vs judge.

**Gate:** optimizer emits an explainable diff with measured before/after preview metrics.

## M5 — Direct Studio persistence if upstream supports it

- Prefer an official `create_recipe` / `save_recipe` MCP or backend API when Unsloth exposes one.
- Only then add one-command publish into the Studio recipe list.
- Avoid browser IndexedDB manipulation as a product dependency.

**Gate:** recipe can be created, updated and reopened in Studio through a supported upstream API with round-trip equality tests.
