# Agent instructions

## Project structure

This repository is a Python package template. The import package currently lives in
`new_project/` (use the configured package path after initialization), tests live in
`tests/`, project and tool configuration lives in `pyproject.toml`, and GitHub Actions
workflows live in `.github/workflows/`. Keep the established architecture unless a
change is explicitly requested. Prefer focused changes and avoid unnecessary
dependencies or abstractions.

## Tooling

- Use `uv` for Python dependencies and environments. `pyproject.toml` declares Hatchling
  and `hatch-vcs`; package versions come from Git tags.
- Ruff handles Python linting, formatting, and import sorting. Its configuration is in
  `pyproject.toml`.
- `basedpyright` runs in strict mode, configured in `pyproject.toml`.
- Tests use pytest. Coverage runs with branch measurement and enforces the configured
  minimum in `pyproject.toml`.
- `tools/linters.sh`, `tools/formatters.sh`, and `tools/env.sh` provide the documented
  local workflows. `prek.toml` defines hooks, including Ruff, basedpyright,
  `sync-with-uv`, Vale, and Prettier.
- Vale is intentionally disabled for agent-facing instruction files through `.vale.ini`;
  keep other writing checks active.

## Changes and checks

When modifying code, add or update focused tests for the changed behavior. Run relevant
checks after modifications, using the commands in `CONTRIBUTING.md` and the applicable
CI jobs in `.github/workflows/ci.yml`. Update documentation when workflows or
contributor instructions change. Never silently weaken linting, type checking, or
coverage requirements.

In your report, state which checks you actually ran, their results, any failures, and
any checks you could not run.
