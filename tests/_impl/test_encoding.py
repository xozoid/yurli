from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from yurli._impl.encoding import DEFAULT_ALPHABET, AlphabetEncoder

if TYPE_CHECKING:
    from yurli.types import IntegerWidth


@pytest.mark.parametrize(
    ("bits", "expected_length"),
    [(16, 3), (32, 6), (64, 11)],
)
def test_base62_lengths_cover_each_supported_domain(
    bits: IntegerWidth,
    expected_length: int,
) -> None:
    encoder = AlphabetEncoder(bits=bits)

    assert encoder.length == expected_length


@pytest.mark.parametrize("bits", [16, 32, 64])
def test_boundary_values_round_trip(bits: IntegerWidth) -> None:
    encoder = AlphabetEncoder(bits=bits)
    values = (0, 1, (1 << bits) - 2, (1 << bits) - 1)

    decoded_values = [encoder.decode(encoder.encode(value)) for value in values]

    assert decoded_values == list(values)


def test_base62_encoding_is_canonical() -> None:
    encoder = AlphabetEncoder(bits=16)

    identifier = encoder.encode(1)

    assert identifier == "001"
    assert encoder.decode(identifier) == 1


@pytest.mark.parametrize("identifier", ["1", "0001", "00-", "00_"])
def test_malformed_identifiers_are_rejected(identifier: str) -> None:
    encoder = AlphabetEncoder(bits=16)

    with pytest.raises(ValueError, match="identifier"):
        encoder.decode(identifier)


def test_identifier_outside_the_configured_domain_is_rejected() -> None:
    encoder = AlphabetEncoder(bits=16)

    with pytest.raises(ValueError, match="unsigned"):
        encoder.decode("zzz")


@pytest.mark.parametrize("value", [-1, 1 << 16])
def test_values_outside_the_configured_domain_are_rejected(value: int) -> None:
    encoder = AlphabetEncoder(bits=16)

    with pytest.raises(ValueError, match="unsigned"):
        encoder.encode(value)


@pytest.mark.parametrize("alphabet", ["0", "001", "abca"])
def test_invalid_alphabets_are_rejected(alphabet: str) -> None:
    with pytest.raises(ValueError, match="alphabet"):
        AlphabetEncoder(bits=16, alphabet=alphabet)


def test_custom_alphabet_is_used_for_encoding_and_decoding() -> None:
    encoder = AlphabetEncoder(bits=16, alphabet="01")
    i = 37

    identifier = encoder.encode(i)

    assert identifier == f"{i:016b}"
    assert encoder.decode(identifier) == 37


def test_default_alphabet_is_base62() -> None:
    encoder = AlphabetEncoder(bits=16)

    assert encoder.alphabet == DEFAULT_ALPHABET
