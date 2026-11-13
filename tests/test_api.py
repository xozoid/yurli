from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

import pytest

from yurli.api import (
    ConfigVersion,
    PermutationVersion,
    Yurli,
)

if TYPE_CHECKING:
    from yurli.api import YurliConfig

_KEYS = (0, 1, 2, 3)


@pytest.fixture
def codec() -> Yurli:
    """Return a codec with deterministic, non-default configuration."""
    return Yurli(
        bits=16,
        alphabet="0123456789abcdef",
        blocklist={"a"},
        round_keys=_KEYS,
        identifier_length=5,
    )


def test_kwargs_reconstruct_identical_codec(codec: Yurli) -> None:
    config: YurliConfig = codec.config
    restored = Yurli(**config)
    value = 12345

    assert restored.encode(value) == codec.encode(value)
    assert restored.decode(codec.encode(value)) == value
    assert "blocklist" not in config


def test_bytes_reconstruct_identical_codec(codec: Yurli) -> None:
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


def test_public_versions_are_serialized(codec: Yurli) -> None:
    config = codec.config

    assert config["format_version"] is ConfigVersion.V1
    assert config["algorithm_version"] is PermutationVersion.FEISTEL_4_ROUND_V1


@pytest.mark.parametrize("value", [0, 1, 12345, (1 << 16) - 1])
def test_encode_decode_round_trips_boundary_values(
    codec: Yurli,
    value: int,
) -> None:
    identifier = codec.encode(value)

    assert len(identifier) == 5
    assert codec.decode(identifier) == value


def test_config_contains_effective_blocklist_pruned_alphabet(
    codec: Yurli,
) -> None:
    config = codec.config

    assert config == {
        "format_version": ConfigVersion.V1,
        "algorithm_version": PermutationVersion.FEISTEL_4_ROUND_V1,
        "bits": 16,
        "round_keys": _KEYS,
        "alphabet": "0123456789bcdef",
        "identifier_length": 5,
    }


@pytest.mark.parametrize(
    ("data", "message"),
    [
        pytest.param(b"\xff", "valid UTF-8", id="invalid-utf8"),
        pytest.param(b"not json", "valid UTF-8 JSON", id="invalid-json"),
        pytest.param(b"[]", "JSON object", id="array"),
    ],
)
def test_bytes_to_dict_rejects_invalid_serialized_values(
    data: bytes,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        Yurli._bytes_to_dict(data)


def test_validate_str_rejects_non_string_value() -> None:
    with pytest.raises(ValueError, match="alphabet"):
        Yurli._validate_str({"alphabet": 1}, "alphabet")


def test_validate_round_keys_rejects_incorrect_key_count() -> None:
    with pytest.raises(ValueError, match="round_keys"):
        Yurli._validate_round_keys({"round_keys": [0, 1, 2]}, "round_keys")


def test_validate_int_rejects_boolean_value() -> None:
    with pytest.raises(ValueError, match="identifier_length"):
        Yurli._validate_int({"identifier_length": True}, "identifier_length")


def test_validate_bits_rejects_unsupported_width() -> None:
    with pytest.raises(ValueError, match="bits"):
        Yurli._validate_bits({"bits": 8}, "bits")


def test_validate_enum_rejects_unknown_version() -> None:
    with pytest.raises(ValueError, match="format_version"):
        Yurli._validate_enum({"format_version": -1}, "format_version", ConfigVersion)


def test_from_bytes_rejects_configuration_with_missing_keys() -> None:
    with pytest.raises(ValueError, match="JSON object with"):
        Yurli.from_bytes(b'{"bits": 16}')


def test_constructor_rejects_unknown_format_version() -> None:
    with pytest.raises(ValueError, match="format"):
        Yurli(format_version=cast("ConfigVersion", -1))


def test_constructor_rejects_unknown_algorithm_version() -> None:
    with pytest.raises(ValueError, match="algorithm"):
        Yurli(algorithm_version=cast("PermutationVersion", -1))
