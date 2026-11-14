# yurli

[![CI][ci-badge]][ci] [![PyPI][pypi-badge]][pypi]

**Cute URLs for ugly IDs.**

yurli (/ˈjɝ.li/, “YUR-lee”) is a Python library for reversible, fixed-length, URL-safe
integer identifiers. It permutes unsigned integers and encodes them as strings. It has
no runtime dependencies and doesn't require a web framework.

## Install

```sh
python -m pip install yurli
```

## Quick start

```python
from yurli import Yurli

codec = Yurli()
identifier = codec.encode(12345)
assert codec.decode(identifier) == 12345
```

Each new codec has a random mapping. Encode and decode with the same configuration. Save
it before using identifiers outside the process; a newly created codec can't decode
identifiers made with another random mapping.

## Configure and persist

Choose a supported unsigned integer width and, optionally, an alphabet. The default
alphabet has 62 URL-safe ASCII characters.

```python
codec = Yurli(
    bits=32,
    alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
)
identifier = codec.encode(12345)
assert codec.decode(identifier) == 12345

# Store these bytes in a secret/configuration store, alongside application settings.
saved = codec.to_bytes()
restored = Yurli.from_bytes(saved)
assert restored.decode(identifier) == 12345
```

The versioned JSON bytes include the permutation keys, width, alphabet, and identifier
length. Persist them with a backup and deploy the same configuration to every process
that needs to decode an identifier. The blocklist itself isn't stored; its resulting
pruned alphabet is. Changing the alphabet, blocklist, width, or configuration creates a
different mapping. Keep the original configuration to read existing identifiers.

Supported values are `0` through `2**bits - 1` for `bits=16`, `32`, or `64`. With the
default 62-character alphabet, identifiers are 3, 6, and 11 characters respectively.
Custom alphabets and blocklist pruning can increase those lengths. Length is fixed for
each codec and is chosen to represent its entire integer domain.

## Custom blocklist

Pass the substrings your application wants to exclude. Matching is case-insensitive.
This small list is only an example; applications should choose and maintain their own
policy.

```python
codec = Yurli(blocklist=["badword", "example"])
identifier = codec.encode(12345)
assert codec.decode(identifier) == 12345
```

Blocklist pruning removes alphabet characters so blocked substrings can't be produced.
Some lists may leave too few characters for the selected width; in that case
construction raises `ValueError`.

## Examples

These examples use only yurli at runtime. Flask, FastAPI, and database integrations are
illustrative snippets; install those applications' dependencies separately.

- [Plain Python and persisted configuration](examples/python.py)
- [Flask URL parameters](examples/flask.py)
- [FastAPI route parameters](examples/fastapi.py)
- [Database primary keys](examples/database.py)

## Performance

See the [`benchmarks/`](benchmarks/) directory for benchmark methodology, results, and
instructions to reproduce the comparison.

## Security and compatibility

yurli provides reversible integer obfuscation, not encryption. It doesn't protect
sensitive information and must not be used to enforce authorization. Applications must
perform their own authentication and authorization checks.

The serialized configuration format and permutation algorithm are versioned. Retaining
the configuration preserves the mapping across process restarts and supported upgrades;
keep old configuration bytes so existing identifiers remain readable. Fresh codecs and
changed configurations produce different mappings.

The architecture and mathematical design are documented in
[`docs/architecture.md`](docs/architecture.md). The example blocklist is derived from
Sqids data; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for attribution and
license.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development environment, checks, and
release steps.

[ci]: https://github.com/xozoid/yurli/actions/workflows/ci.yml?query=branch%3Amain
[ci-badge]:
  https://github.com/xozoid/yurli/actions/workflows/ci.yml/badge.svg?branch=main
[pypi]: https://pypi.org/project/yurli
[pypi-badge]: https://img.shields.io/pypi/v/yurli.svg
