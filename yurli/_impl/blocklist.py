"""Collision-free, blocklist-safe fixed-width identifier encoding."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from yurli._impl.encoding import DEFAULT_ALPHABET, AlphabetEncoder

if TYPE_CHECKING:
    from collections.abc import Iterable

    from yurli.types import IntegerWidth


class BlocklistEncoder(AlphabetEncoder):
    """Encode domain values without configured case-insensitive substrings.

    Even-parity identifiers form the normal namespace. Odd-parity identifiers
    form the fallback namespace. Both use only the configured alphabet, so
    neither namespace needs a visible prefix character.
    """

    @override
    def __init__(
        self,
        bits: IntegerWidth,
        blocklist: Iterable[str] = (),
        alphabet: str = DEFAULT_ALPHABET,
        length: int | None = None,
    ) -> None:
        """Create a blocklist-aware encoder.

        Args:
            bits: Width of the unsigned integer domain to encode.
            blocklist: Case-insensitive substrings that generated IDs forbid.
            alphabet: Ordered digits used for normal and fallback identifiers.
            length: Optional fixed ID length.

        Raises:
            ValueError: If the alphabet, blocklist, or capacity is invalid.
        """
        super().__init__(bits, alphabet, length=length)
        if self._base % 2:
            msg = "alphabet must contain an even number of characters"
            raise ValueError(msg)
        self._base_half = self._base // 2

        self._digit_parity: dict[str, int] = {}
        self._alphabet_reduced: dict[int, str] = {0: "", 1: ""}
        self._digits_reduced: dict[str, int] = {}
        for i, c in enumerate(self._alphabet):
            digit, parity = divmod(i, 2)
            self._alphabet_reduced[parity] += c
            self._digits_reduced[c] = digit
            self._digit_parity[c] = parity

        self._blocklist = self._normalize_blocklist(blocklist)

        if self._blocklist:
            if length is None:
                self._length = self._find_identifier_length(self._length)
            self._validate_capacity()

    @property
    def blocklist(self) -> frozenset[str]:
        """Normalized forbidden substrings."""
        return self._blocklist

    @override
    def encode(self, value: int, /) -> str:
        self._validate_value(value)
        value_original = value

        s = ""
        parity = 0
        for _ in range(self._length - 1):
            value, digit = divmod(value, self._base)
            s += self.alphabet[digit]
            parity ^= digit & 1
        digit = value % self._base_half
        s += self._alphabet_reduced[parity][digit]

        if self._is_blocked(s):
            return self._encode_fallback(value_original)
        return s

    @override
    def decode(self, identifier: str, /) -> int:
        self._validate_identifier(identifier)
        if self._is_blocked(identifier):
            msg = "identifier contains a blocked substring"
            raise ValueError(msg)

        # NOTE: Start with the reduced digits, then use full for remaining
        digits = self._digits_reduced
        value = 0
        parity = 0
        for character in reversed(identifier):
            try:
                digit = digits[character]
            except KeyError as error:
                msg = "identifier contains a character outside the alphabet"
                raise ValueError(msg) from error
            parity ^= self._digit_parity[character]
            value = (value * self._base) + digit
            digits = self._digits

        if parity:
            value = self._decode_fallback(identifier)

        self._validate_value(value)
        return value

    def _is_blocked(self, identifier: str) -> bool:
        identifier = identifier.casefold()
        return any(block in identifier for block in self._blocklist)

    def _find_identifier_length(self, minimum_length: int) -> int:
        raise NotImplementedError

    def _validate_capacity(self) -> None:
        """Raise when either parity namespace cannot represent the domain.

        Raises:
            ValueError: If normal or fallback capacity is insufficient.
        """
        raise NotImplementedError

    def _normalize_blocklist(self, blocklist: Iterable[str]) -> frozenset[str]:
        """Validate, casefold, and remove impossible forbidden substrings.

        Returns:
            Deduplicated forbidden substrings that can appear in an identifier.

        Raises:
            ValueError: If an entry is empty.
        """
        normalized = frozenset(entry.casefold() for entry in blocklist)
        if "" in normalized:
            msg = "blocklist entries must not be empty"
            raise ValueError(msg)
        output_characters = frozenset(
            character.casefold() for character in self.alphabet
        )
        return frozenset(
            entry
            for entry in normalized
            if all(character in output_characters for character in entry)
        )

    def _encode_fallback(self, value: int) -> str:
        raise NotImplementedError

    def _decode_fallback(self, identifier: str) -> int:
        raise NotImplementedError
