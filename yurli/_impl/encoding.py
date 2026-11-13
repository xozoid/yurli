"""Fixed-width encoders for unsigned integer domains."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import TYPE_CHECKING

from yurli.constants import DEFAULT_ALPHABET, SUPPORTED_BITS

if TYPE_CHECKING:
    from collections.abc import Iterable

    from yurli.types import IntegerWidth

_MINIMUM_ALPHABET_LENGTH = 2


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
        blocklist: Iterable[str] = (),
    ) -> None:
        """Create an encoder for a width and alphabet.

        Args:
            bits: Width of the unsigned integer domain to encode.
            alphabet: Ordered digits used for the positional representation.
            length: Optional emitted length. It must be large enough to encode
                the complete configured domain.
            blocklist: Case-insensitive substrings made impossible by pruning
                characters from the candidate alphabet.

        Raises:
            ValueError: If the width or alphabet is invalid.
        """
        if bits not in SUPPORTED_BITS:
            msg = "bits must be one of 16, 32, or 64"
            raise ValueError(msg)
        self._validate_alphabet(alphabet)
        self._bits: IntegerWidth = bits
        minimum_length = self._required_length(bits, len(alphabet))
        if length is not None and length < minimum_length:
            msg = f"length must be at least {minimum_length} for the configured domain"
            raise ValueError(msg)

        self._alphabet = self._prune_alphabet(
            bits,
            self._normalize_blocklist(blocklist),
            alphabet,
            length,
        )
        self._base = len(self._alphabet)
        self._digits = {c: i for i, c in enumerate(self._alphabet)}
        self._max_value = 1 << bits
        self._length = max(length or 0, self._required_length(bits, self._base))

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

    @staticmethod
    def _normalize_blocklist(blocklist: Iterable[str]) -> set[str]:
        """Return non-empty ASCII entries normalized for matching.

        Raises:
            ValueError: If an entry is empty or non-ASCII.
        """
        normalized_blocklist: set[str] = set()
        for word in blocklist:
            if not word:
                msg = "blocklist entries must be non-empty"
                raise ValueError(msg)
            if not word.isascii():
                msg = "blocklist entries must contain only ASCII characters"
                raise ValueError(msg)
            normalized_blocklist.add(word.lower())
        return normalized_blocklist

    @classmethod
    def _prune_alphabet(
        cls,
        bits: IntegerWidth,
        blocklist: set[str],
        alphabet: str,
        length: int | None = None,
    ) -> str:
        """Return an ordered alphabet in which no relevant word is spellable."""

        def prune(alphabet_set: set[str]) -> set[str]:
            if len(alphabet_set) <= 1:
                msg = "blocklist leaves insufficient alphabet characters"
                raise ValueError(msg)

            effective_length = max(
                length or 0,
                cls._required_length(bits, len(alphabet_set)),
            )
            alphabet_lower = {character.lower() for character in alphabet_set}
            counts: dict[str, int] = defaultdict(int)
            for word in blocklist:
                if len(word) > effective_length:
                    continue
                word_alphabet = set(word)
                if word_alphabet <= alphabet_lower:
                    for character in word_alphabet:
                        counts[character] += 1
            if not counts:
                return alphabet_set

            remove = max(counts, key=lambda character: (counts[character], character))
            return prune(
                {
                    character
                    for character in alphabet_set
                    if character.lower() != remove
                },
            )

        reduced_alphabet = prune(set(alphabet))
        return "".join(
            character for character in alphabet if character in reduced_alphabet
        )

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
