# new-project

[![CI][ci-badge]][ci] [![PyPI publishing][pypi-badge]][pypi-url]

## Overview

This repository is a reusable template for Python packages. It includes Hatchling with
`hatch-vcs` for builds and Git-derived versions, pytest and coverage for tests, Ruff for
linting and formatting, `basedpyright` for type checking, and `prek` hooks for local
checks. Prettier, `Taplo`, `yamlfmt`, Vale, and `codespell` cover formatting and writing
checks. GitHub Actions runs these checks and publishes tagged releases to PyPI.

## Create a project

On GitHub, select **Use this template**, create a repository under your account or
organization, and clone that repository.

Replace `new-project` with your distribution name and `new_project` with its Python
import package name. Rename the `new_project/` directory, update the wheel package in
`[tool.hatch.build.targets.wheel]`, and adjust coverage and `basedpyright` paths in
`pyproject.toml`. Update the project metadata there, including description, keywords,
classifiers, Python support, and license as needed. Also change the npm package name in
`package.json` and the PyPI project URL in `.github/workflows/publish.yml`.

For example, for distribution `sample-tool` and import package `sample_tool`, change the
project name to `sample-tool`, rename the package directory to `sample_tool/`, and set
the wheel package to `sample_tool`. Update references in tests and workflow commands,
including the build import smoke test in `.github/workflows/ci.yml`. Review the Python
version matrix and tool versions in CI, Dependabot, `pyproject.toml`, `uv.lock`,
`prek.toml`, and `package-lock.json` for your project's needs. Configure PyPI trusted
publishing for the repository's `pypi` GitHub environment and the publishing workflow.
After creating the new repository, replace `xozoid/python-template` in the badge
definitions at the bottom with its owner and repository name.

The project initialization skill records the full upstream template commit used during
adoption in `.agents/skills/update-from-template/HISTORY.md`. Use the
`update-from-template` skill for later template updates; it preserves project-specific
changes and updates `HISTORY.md` only after the migration and checks succeed. That file
tracks the template source, applied revision, and intentionally skipped changes.

## Development setup

Install Git, Python 3.12 or later, [uv](https://docs.astral.sh/uv/), Node.js 24 or later
with npm, and Vale. From the repository root, run:

```sh
tools/env.sh
```

The script synchronizes the locked Python dependencies, installs `prek` Git hooks,
installs Vale if it's missing (using a supported system package manager), downloads Vale
styles, installs npm dependencies with `npm ci`, and creates `.env` and `.env.leave` if
absent. They're for [`autoenv`](https://github.com/hyperupcall/autoenv): `.env`
activates the project virtual environment when you enter the repository, and
`.env.leave` deactivates it when you leave. Existing files stay in place.
`tools/env.sh --upgrade` first upgrades the Python lockfile, then syncs and performs the
same setup.

Common commands:

```sh
uv run pytest
uv run coverage run -m pytest
uv run coverage report
tools/linters.sh
tools/formatters.sh
uv run prek run --all-files
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for dependency updates, checks, and release
steps.

## Releases

`hatch-vcs` uses setuptools-scm to derive versions from Git tags and history, including
development versions when a commit isn't exactly tagged. The configured `0.1.0` fallback
applies only if version detection fails. Publish a GitHub Release whose tag is a valid
version tag, optionally prefixed with `v` (for example, `v1.2.3`). Publishing the
release starts the publish workflow, which runs the CI workflow, builds the package, and
checks that the tag version matches the built package version. After validation, GitHub
Actions publishes to PyPI using trusted publishing. The workflow expects a PyPI project
matching the configured name and a GitHub environment named `pypi`.

[ci]:
  https://github.com/xozoid/python-template/actions/workflows/ci.yml?query=branch%3Amain
[ci-badge]:
  https://github.com/xozoid/python-template/actions/workflows/ci.yml/badge.svg?branch=main
[pypi-badge]: https://img.shields.io/pypi/v/new-project.svg
[pypi-url]: https://pypi.org/project/new-project/
