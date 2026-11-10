# yurli

[![CI][ci-badge]][ci] [![PyPI][pypi-badge]][pypi]

Yurli is a Python package.

## Development setup

Install Git, Python 3.12 or later, [uv](https://docs.astral.sh/uv/), Node.js 24 or later
with npm, and Vale. From the repository root, run:

```sh
tools/env.sh
```

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

Versions come from Git tags through `hatch-vcs`. Publishing a GitHub Release starts the
publish workflow, which validates the package and publishes to PyPI using trusted
publishing. The workflow uses the PyPI project `yurli` and the GitHub environment `pypi`.

[ci]: https://github.com/xozoid/yurli/actions/workflows/ci.yml?query=branch%3Amain
[ci-badge]: https://github.com/xozoid/yurli/actions/workflows/ci.yml/badge.svg?branch=main
[pypi]: https://pypi.org/project/yurli
[pypi-badge]: https://img.shields.io/pypi/v/yurli.svg
