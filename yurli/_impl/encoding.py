"""Fixed-width encoders for unsigned integer domains."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from yurli.constants import DEFAULT_ALPHABET

if TYPE_CHECKING:
    from yurli.types import IntegerWidth

_MINIMUM_ALPHABET_LENGTH = 2
_SUPPORTED_BITS = (16, 32, 64)


class AlphabetEncoder:
    """Encode one configured unsigned integer domain with a fixed alphabet.

    The encoder uses a fixed length so every value has precisely one emitted
    representation. It rejects alphabet strings with duplicate characters and
    encoded strings that are outside the configured integer domain.
    """

    def __init__(
        self,
        bits: IntegerWidth,
        alphabet: str = DEFAULT_ALPHABET,
        length: int | None = None,
    ) -> None:
        """Create an encoder for a width and alphabet.

        Args:
            bits: Width of the unsigned integer domain to encode.
            alphabet: Ordered digits used for the positional representation.
            length: Optional emitted length. It must be large enough to encode
                the complete configured domain.

        Raises:
            ValueError: If the width or alphabet is invalid.
        """
        if bits not in _SUPPORTED_BITS:
            msg = "bits must be one of 16, 32, or 64"
            raise ValueError(msg)
        self._validate_alphabet(alphabet)

        self._alphabet = alphabet
        self._base = len(alphabet)
        self._bits: IntegerWidth = bits
        minimum_length = self._required_length(bits, self._base)
        if length is not None and length < minimum_length:
            msg = f"length must be at least {minimum_length} for the configured domain"
            raise ValueError(msg)

        self._digits = {c: i for i, c in enumerate(alphabet)}
        self._max_value = 1 << bits
        self._length = length or minimum_length

    @staticmethod
    def _validate_alphabet(alphabet: str) -> None:
        """Validate an ordered ASCII alphabet before any reduction.

        Raises:
            ValueError: If the alphabet is non-ASCII, too short, or duplicated.
        """
        if not alphabet.isascii():
            msg = "alphabet must contain only ASCII characters"
            raise ValueError(msg)
        if len(alphabet) < _MINIMUM_ALPHABET_LENGTH:
            msg = "alphabet must contain at least two characters"
            raise ValueError(msg)
        if len(set(alphabet)) != len(alphabet):
            msg = "alphabet must not contain duplicate characters"
            raise ValueError(msg)

    @classmethod
    def _required_length(cls, bits: IntegerWidth, base: int) -> int:
        return math.ceil(bits / math.log2(base))

    @property
    def alphabet(self) -> str:
        """Ordered alphabet used by this encoder."""
        return self._alphabet

    @property
    def bits(self) -> IntegerWidth:
        """Configured unsigned integer width."""
        return self._bits

    @property
    def length(self) -> int:
        """Canonical emitted length for this configured domain."""
        return self._length

    def encode(self, value: int, /) -> str:
        """Encode a domain value as a fixed-width canonical string.

        Returns:
            A string with exactly :attr:`length` characters.
        """
        self._validate_value(value)

        s = ""
        for _ in range(self._length):
            value, digit = divmod(value, self._base)
            s += self.alphabet[digit]
        return s

    def decode(self, identifier: str, /) -> int:
        """Decode one fixed-width canonical identifier.

        Returns:
            The decoded domain value.

        Raises:
            ValueError: If the identifier is malformed or outside the domain.
        """
        self._validate_identifier(identifier)

        value = 0
        for character in reversed(identifier):
            try:
                digit = self._digits[character]
            except KeyError as error:
                msg = "identifier contains a character outside the alphabet"
                raise ValueError(msg) from error
            value = (value * self._base) + digit

        self._validate_value(value)
        return value

    def _validate_value(self, value: int) -> None:
        if not 0 <= value < self._max_value:
            msg = f"value must be in the unsigned {self._bits}-bit domain"
            raise ValueError(msg)

    def _validate_identifier(self, identifier: str) -> None:
        if len(identifier) != self.length:
            msg = f"identifier must contain exactly {self.length} characters"
            raise ValueError(msg)
