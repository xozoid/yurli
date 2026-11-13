from __future__ import annotations

import json
from typing import TYPE_CHECKING

from yurli.api import (
    ConfigVersion,
    PermutationVersion,
    Yurli,
)

if TYPE_CHECKING:
    from yurli.api import YurliConfig

_KEYS = (0, 1, 2, 3)


def test_kwargs_reconstruct_identical_codec() -> None:
    codec = Yurli(bits=32, blocklist={"a"}, round_keys=_KEYS)
    config: YurliConfig = codec.to_kwargs()
    restored = Yurli(**config)
    value = 12345

    assert restored.encode(value) == codec.encode(value)
    assert restored.decode(codec.encode(value)) == value
    assert "blocklist" not in config


def test_bytes_reconstruct_identical_codec() -> None:
    codec = Yurli(bits=32, blocklist={"a"}, round_keys=_KEYS)
    restored = Yurli.from_bytes(codec.to_bytes())
    value = 12345

    assert restored.encode(value) == codec.encode(value)
    assert restored.decode(codec.encode(value)) == value


def test_configuration_bytes_are_stable_json() -> None:
    codec = Yurli(bits=16, round_keys=_KEYS)

    serialized = codec.to_bytes()

    assert serialized == codec.to_bytes()
    assert json.loads(serialized) == {
        "algorithm_version": 1,
        "alphabet": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "bits": 16,
        "format_version": 1,
        "identifier_length": 3,
        "round_keys": [0, 1, 2, 3],
    }


def test_public_versions_are_serialized() -> None:
    config = Yurli(bits=16, round_keys=_KEYS).to_kwargs()

    assert config["format_version"] is ConfigVersion.V1
    assert config["algorithm_version"] is PermutationVersion.FEISTEL_4_ROUND_V1
