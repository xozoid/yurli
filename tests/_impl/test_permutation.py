from __future__ import annotations

import random
from typing import cast

import pytest

from yurli._impl.permutation import IntegerPermutation, IntegerWidth, RoundKeys

_TEST_KEYS = (0, 1, 0x123456789ABCDEF0, (1 << 64) - 1)


def test_16_bit_permutation_is_exhaustively_reversible_and_unique() -> None:
    permutation = IntegerPermutation(bits=16, round_keys=_TEST_KEYS)
    outputs = [permutation.permute(value) for value in range(1 << 16)]

    assert len(set(outputs)) == 1 << 16
    assert [permutation.invert(value) for value in outputs] == list(range(1 << 16))


@pytest.mark.parametrize("bits", [32, 64])
def test_random_values_round_trip_for_larger_widths(bits: int) -> None:
    permutation = IntegerPermutation(
        bits=cast("IntegerWidth", bits),
        round_keys=_TEST_KEYS,
    )
    generator = random.Random(94731)
    values = [0, 1, (1 << bits) - 2, (1 << bits) - 1]
    values.extend(generator.randrange(1 << bits) for _ in range(1000))

    assert [
        permutation.invert(permutation.permute(value)) for value in values
    ] == values


@pytest.mark.parametrize("bits", [16, 32, 64])
def test_explicit_configuration_reconstructs_identical_mapping(bits: int) -> None:
    original = IntegerPermutation(
        bits=cast("IntegerWidth", bits),
        round_keys=_TEST_KEYS,
    )
    restored = IntegerPermutation(bits=original.bits, round_keys=original.round_keys)
    values = (0, 1, (1 << bits) // 2, (1 << bits) - 1)

    assert [restored.permute(value) for value in values] == [
        original.permute(value) for value in values
    ]
    assert [restored.invert(value) for value in values] == [
        original.invert(value) for value in values
    ]


@pytest.mark.parametrize("bits", [16, 32, 64])
def test_generated_permutation_has_four_reusable_round_keys(bits: int) -> None:
    width = cast("IntegerWidth", bits)
    original = IntegerPermutation(bits=width)
    restored = IntegerPermutation(bits=width, round_keys=original.round_keys)

    assert len(original.round_keys) == 4
    assert all(0 <= key < 1 << 64 for key in original.round_keys)
    assert restored.permute(123) == original.permute(123)


def test_values_outside_configured_domain_are_rejected() -> None:
    for bits in (16, 32, 64):
        permutation = IntegerPermutation(bits=bits, round_keys=_TEST_KEYS)
        for value in (-1, 1 << bits, True):
            with pytest.raises(ValueError, match="unsigned"):
                permutation.permute(value)


@pytest.mark.parametrize("bits", [0, 8, 128, True])
def test_unsupported_widths_are_rejected(bits: int) -> None:
    with pytest.raises(ValueError, match="bits"):
        IntegerPermutation(bits=cast("IntegerWidth", bits))


@pytest.mark.parametrize(
    "round_keys",
    [
        (),
        (1, 2, 3),
        (1, 2, 3, 4, 5),
        (1, 2, 3, -1),
        (1, 2, 3, 1 << 64),
        (1, 2, 3, True),
        [1, 2, 3, 4],
    ],
)
def test_invalid_round_keys_are_rejected(round_keys: object) -> None:
    with pytest.raises(ValueError, match="round_keys"):
        IntegerPermutation(bits=16, round_keys=cast("RoundKeys", round_keys))


def test_independently_generated_configurations_have_independent_keys() -> None:
    first = IntegerPermutation(bits=32)
    second = IntegerPermutation(bits=32)

    assert first.round_keys != second.round_keys


def test_distinct_configurations_produce_distinct_mappings() -> None:
    first = IntegerPermutation(bits=32, round_keys=(0, 0, 0, 0))
    second = IntegerPermutation(bits=32, round_keys=(1, 1, 1, 1))
    values = (0, 1, 12345, (1 << 32) - 1)

    assert [first.permute(value) for value in values] != [
        second.permute(value) for value in values
    ]
