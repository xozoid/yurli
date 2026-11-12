"""Collision-free, blocklist-safe fixed-width identifier encoding."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, override

from yurli._impl.encoding import AlphabetEncoder
from yurli.constants import DEFAULT_ALPHABET

if TYPE_CHECKING:
    from collections.abc import Iterable

    from yurli.types import IntegerWidth


class BlocklistEncoder(AlphabetEncoder):
    """Encode values with an alphabet that excludes blocked substrings.

    The encoder removes alphabet characters until every relevant blocked word
    requires at least one unavailable character. It then uses
    :class:`~yurli._impl.encoding.AlphabetEncoder` unchanged. Consequently,
    every emitted identifier is blocklist-safe without a fallback namespace.

    Alphabet reduction can increase the fixed identifier length. A blocklist
    that leaves fewer than two characters cannot encode the configured domain.
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
            blocklist: Non-empty, case-insensitive substrings that generated
                identifiers must not contain.
            alphabet: Ordered candidate digits to reduce and then use for
                positional encoding.
            length: Optional fixed ID length. Pruning can increase it when the
                reduced alphabet needs more characters for the domain.

        Raises:
            ValueError: If the explicitly supplied length is too short for the
                original alphabet.
        """
        self._validate_alphabet(alphabet)
        minimum_length = self._required_length(bits, len(alphabet))
        if length is not None and length < minimum_length:
            msg = f"length must be at least {minimum_length} for the configured domain"
            raise ValueError(msg)
        normalized_blocklist = self._normalize_blocklist(blocklist)
        reduced_alphabet = self._prune_alphabet(
            bits,
            normalized_blocklist,
            alphabet,
            length,
        )
        effective_length = max(
            length or 0,
            self._required_length(bits, len(reduced_alphabet)),
        )
        super().__init__(
            bits,
            reduced_alphabet,
            length=effective_length,
        )
        self._blocklist = frozenset(
            word for word in normalized_blocklist if len(word) <= self._length
        )

    @staticmethod
    def _normalize_blocklist(blocklist: Iterable[str]) -> set[str]:
        """Return non-empty ASCII entries normalized for matching.

        Raises:
            ValueError: If an entry is empty or non-ASCII, or no entry is supplied.
        """
        normalized_blocklist: set[str] = set()
        for word in blocklist:
            if not word:
                msg = "blocklist must contain at least one non-empty entry"
                raise ValueError(msg)
            if not word.isascii():
                msg = "blocklist entries must contain only ASCII characters"
                raise ValueError(msg)
            normalized_blocklist.add(word.lower())

        if not normalized_blocklist:
            msg = "blocklist must contain at least one non-empty entry"
            raise ValueError(msg)
        return normalized_blocklist

    @property
    def blocklist(self) -> frozenset[str]:
        """Normalized blocked substrings that fit within an identifier."""
        return self._blocklist

    @classmethod
    def _prune_alphabet(
        cls,
        bits: IntegerWidth,
        blocklist: set[str],
        alphabet: str,
        length: int | None = None,
    ) -> str:
        """Return an ordered alphabet in which no relevant word is spellable.

        Repeatedly remove the case-insensitive character that occurs in the
        greatest number of currently spellable blocked words. Ties use the
        lexicographically greatest lowercase character. Words longer than the
        greater of the configured and minimum identifier lengths cannot occur
        and do not affect removal.

        Returns:
            The surviving characters in their original order.

        """

        def prune(alphabet_set: set[str]) -> set[str]:
            alphabet_len = len(alphabet_set)
            if alphabet_len <= 1:
                msg = "blocklist leaves insufficient alphabet characters"
                raise ValueError(msg)

            effective_length = max(
                length or 0,
                cls._required_length(bits, alphabet_len),
            )

            alphabet_lower = {c.lower() for c in alphabet_set}
            counts: dict[str, int] = defaultdict(int)
            for word in blocklist:
                if len(word) > effective_length:
                    continue
                word_alphabet = set(word)
                if word_alphabet <= alphabet_lower:
                    for c in word_alphabet:
                        counts[c] += 1

            if not counts:
                return alphabet_set

            remove = max(counts, key=lambda c: (counts[c], c))
            alphabet_set = {c for c in alphabet_set if c.lower() != remove}
            return prune(alphabet_set)

        reduced_alphabet = prune(set(alphabet))
        return "".join(c for c in alphabet if c in reduced_alphabet)
