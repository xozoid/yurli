# yurli

[![CI][ci-badge]][ci] [![PyPI][pypi-badge]][pypi]

**Cute URLs for ugly IDs.**

yurli (/ˈjɝ.li/, “YUR-lee”) is a Python library for reversible, fixed-length, URL-safe
integer identifiers. It provides obfuscation, not encryption or authorization.

The architecture and mathematical design are documented in
[`docs/architecture.md`](docs/architecture.md). Create a codec, retain its serialized
configuration, and use it to encode and decode IDs:

```python
from yurli import Yurli

codec = Yurli()
identifier = codec.encode(12345)
assert codec.decode(identifier) == 12345

saved_configuration = codec.to_bytes()
restored_codec = Yurli.from_bytes(saved_configuration)
assert restored_codec.decode(identifier) == 12345
```

Use `bits=16`, `bits=32`, or `bits=64` to select an unsigned domain. The constructor
also accepts a custom alphabet and blocklist. Blocklist pruning is applied during
construction; persisted configurations retain the resulting alphabet and fixed length,
not the source blocklist. Changing any setting creates a different mapping, so retain
the original serialized configuration to decode existing identifiers.

The sorted, line-delimited example blocklist lives in
[`yurli/blocklist.txt`](yurli/blocklist.txt). It's derived from Sqids data; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for its attribution and license.
Applications choose and maintain the blocklist policy appropriate for their identifiers.

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
publishing. The workflow uses the PyPI project `yurli` and the GitHub environment
`pypi`.

[ci]: https://github.com/xozoid/yurli/actions/workflows/ci.yml?query=branch%3Amain
[ci-badge]:
  https://github.com/xozoid/yurli/actions/workflows/ci.yml/badge.svg?branch=main
[pypi]: https://pypi.org/project/yurli
[pypi-badge]: https://img.shields.io/pypi/v/yurli.svg
