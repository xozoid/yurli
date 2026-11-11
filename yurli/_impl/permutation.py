"""Reversible permutations for unsigned integer domains."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from yurli.types import IntegerWidth, RoundKeys

_SUPPORTED_BITS = (16, 32, 64)
_ROUND_COUNT = 4
_UINT64_MASK = (1 << 64) - 1
_SPLITMIX_MULTIPLIER_1 = 0xBF58476D1CE4E5B9
_SPLITMIX_MULTIPLIER_2 = 0x94D049BB133111EB


class IntegerPermutation:
    """Permute unsigned integers with a four-round balanced Feistel network.

    A permutation instance is defined by its supported width and four unsigned
    64-bit round keys. Passing explicit keys reconstructs the same mapping.
    When keys are omitted, a new configuration is generated with ``secrets``.

    The permutation provides reversible obfuscation, not cryptographic security.
    """

    __slots__ = (
        "_bits",
        "_bits_half",
        "_max_value",
        "_round_keys",
    )

    def __init__(
        self,
        bits: IntegerWidth = 64,
        round_keys: RoundKeys | None = None,
    ) -> None:
        """Create a permutation with generated or supplied round keys.

        Raises:
            ValueError: If the width or supplied round keys are invalid.
        """
        if bits not in _SUPPORTED_BITS:
            msg = "bits must be one of 16, 32, or 64"
            raise ValueError(msg)

        if round_keys is None:
            round_keys = (
                secrets.randbits(64),
                secrets.randbits(64),
                secrets.randbits(64),
                secrets.randbits(64),
            )
        self._validate_round_keys(round_keys)
        self._bits: IntegerWidth = bits
        self._bits_half = bits // 2
        self._round_keys = round_keys

        self._max_value = 1 << self._bits

    @property
    def bits(self) -> IntegerWidth:
        """Configured unsigned integer width."""
        return self._bits

    @property
    def round_keys(self) -> RoundKeys:
        """Immutable round keys needed to reconstruct this mapping."""
        return self._round_keys

    def permute(self, value: int, /) -> int:
        """Map a value to another value in the configured domain.

        Returns:
            The permuted value.
        """
        self._validate_value(value)
        half_mask = (1 << self._bits_half) - 1
        left = value >> self._bits_half
        right = value & half_mask

        for key in self._round_keys:
            left, right = right, left ^ self._round_function(right, key, half_mask)

        return (left << self._bits_half) | right

    def invert(self, value: int, /) -> int:
        """Invert a value produced by :meth:`permute`.

        Returns:
            The original value.
        """
        self._validate_value(value)
        half_mask = (1 << self._bits_half) - 1
        left = value >> self._bits_half
        right = value & half_mask

        for key in reversed(self._round_keys):
            left, right = right ^ self._round_function(left, key, half_mask), left

        return (left << self._bits_half) | right

    def _validate_value(self, value: int) -> None:
        if not 0 <= value < self._max_value:
            msg = f"value must be an integer in the unsigned {self._bits}-bit domain"
            raise ValueError(msg)

    @staticmethod
    def _validate_round_keys(round_keys: RoundKeys) -> None:
        if len(round_keys) != _ROUND_COUNT or any(
            not 0 <= key <= _UINT64_MASK for key in round_keys
        ):
            msg = "round_keys must be a tuple of four unsigned 64-bit integers"
            raise ValueError(msg)

    @staticmethod
    def _round_function(right: int, key: int, half_mask: int) -> int:
        """Mix a half-block and key with the SplitMix64 finalizer.

        Returns:
            A value masked to the half-block width.
        """
        value = (right ^ key) & _UINT64_MASK
        value = ((value ^ (value >> 30)) * _SPLITMIX_MULTIPLIER_1) & _UINT64_MASK
        value = ((value ^ (value >> 27)) * _SPLITMIX_MULTIPLIER_2) & _UINT64_MASK
        value ^= value >> 31
        return value & half_mask
