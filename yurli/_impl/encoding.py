"""Fixed-width encoders for unsigned integer domains."""

from __future__ import annotations

import math
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from yurli.types import IntegerWidth

DEFAULT_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_MINIMUM_ALPHABET_LENGTH = 2
_SUPPORTED_BITS = (16, 32, 64)


class Base62Encoder:
    """Encode one configured unsigned integer domain with a fixed alphabet.

    The encoder uses a fixed length so every value has precisely one emitted
    representation. It rejects alphabet strings with duplicate characters and
    encoded strings that are outside the configured integer domain.
    """

    def __init__(
        self,
        bits: IntegerWidth,
        alphabet: str = DEFAULT_ALPHABET,
    ) -> None:
        """Create an encoder for a width and alphabet.

        Args:
            bits: Width of the unsigned integer domain to encode.
            alphabet: Ordered digits used for the positional representation.

        Raises:
            ValueError: If the width or alphabet is invalid.
        """
        if bits not in _SUPPORTED_BITS:
            msg = "bits must be one of 16, 32, or 64"
            raise ValueError(msg)
        if len(alphabet) < _MINIMUM_ALPHABET_LENGTH:
            msg = "alphabet must contain at least two characters"
            raise ValueError(msg)
        if len(set(alphabet)) != len(alphabet):
            msg = "alphabet must not contain duplicate characters"
            raise ValueError(msg)

        self._alphabet = alphabet
        self._alphabet_base = len(alphabet)
        self._bits: IntegerWidth = bits
        self._digits = {character: index for index, character in enumerate(alphabet)}
        self._max_value = 1 << bits

    @property
    def alphabet(self) -> str:
        """Ordered alphabet used by this encoder."""
        return self._alphabet

    @property
    def bits(self) -> IntegerWidth:
        """Configured unsigned integer width."""
        return self._bits

    @cached_property
    def length(self) -> int:
        """Canonical emitted length for this configured domain."""
        return math.ceil(self._bits / math.log2(self._alphabet_base))

    def encode(self, value: int, /) -> str:
        """Encode a domain value as a fixed-width canonical string.

        Returns:
            A string with exactly :attr:`length` characters.
        """
        self._validate_value(value)
        digits = [self._alphabet[0]] * self.length

        for index in range(self.length - 1, -1, -1):
            value, digit = divmod(value, self._alphabet_base)
            digits[index] = self._alphabet[digit]

        return "".join(digits)

    def decode(self, identifier: str, /) -> int:
        """Decode one fixed-width canonical identifier.

        Returns:
            The decoded domain value.

        Raises:
            ValueError: If the identifier is malformed or outside the domain.
        """
        if len(identifier) != self.length:
            msg = f"identifier must contain exactly {self.length} characters"
            raise ValueError(msg)

        value = 0
        for character in identifier:
            try:
                digit = self._digits[character]
            except KeyError as error:
                msg = "identifier contains a character outside the alphabet"
                raise ValueError(msg) from error
            value = (value * self._alphabet_base) + digit

        self._validate_value(value)
        return value

    def _validate_value(self, value: int) -> None:
        """Raise when a value is not an integer in the configured domain.

        Raises:
            ValueError: If the value is outside the configured domain.
        """
        if not 0 <= value < self._max_value:
            msg = f"value must be in the unsigned {self._bits}-bit domain"
            raise ValueError(msg)
