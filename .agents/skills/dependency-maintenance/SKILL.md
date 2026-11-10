---
name: dependency-maintenance
description: >-
  Maintains Python and npm dependencies, developer tools, lockfiles, and prek hooks. Use
  when adding, removing, or updating project dependencies, tool versions, or hook
  revisions.
---

# Dependency maintenance

Use the repository's declared dependency mechanisms and preserve consistency between
metadata, lockfiles, CI, and hooks.

- Manage Python dependencies with `uv` and declarations in `pyproject.toml`. Use
  `uv add`, `uv remove`, or an intentional metadata edit followed by `uv lock`; commit
  the resulting `uv.lock` changes.
- Manage npm dependencies through npm commands and `package.json`. Regenerate and commit
  `package-lock.json`; use `npm ci` to install the locked set.
- When changing hook revisions in `prek.toml` or relevant Python tool versions, run the
  configured `sync-with-uv` hook (`uv run prek run sync-with-uv`) and review any
  resulting lockfile updates.
- Check that versions agree across CI workflow setup, dependency declarations,
  `uv.lock`, `package-lock.json`, and `prek.toml` where applicable. Prefer the existing
  dependency-management mechanisms over duplicating version information.
- Run relevant checks after changes. See `CONTRIBUTING.md` for `uv sync --locked`,
  tests, `tools/linters.sh`, `tools/formatters.sh`, and `uv run prek run --all-files`.

Do not add dependencies or weaken checks unless the requested change requires it.
Document workflow changes in `CONTRIBUTING.md` or `README.md` as appropriate.
