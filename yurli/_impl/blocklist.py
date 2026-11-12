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
    every emitted identifier is blocklist-safe without a separate fallback
    representation.

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
            length: Optional fixed ID length.

        Raises:
            ValueError: If no non-empty blocked substring is supplied, or
                alphabet reduction or the parent encoder rejects the settings.
        """
        blocklist = {word.casefold() for word in blocklist if word}
        if not blocklist:
            msg = "blocklist required or something"
            raise ValueError(msg)
        super().__init__(
            bits,
            self._prune_alphabet(bits, blocklist, alphabet),
            length=length,
        )
        # Remove ones too long anyways
        self._blocklist = frozenset(
            word for word in blocklist if len(word) <= self._length
        )

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
    ) -> str:
        """Return an ordered alphabet in which no relevant word is spellable.

        Repeatedly remove the case-insensitive character that occurs in the
        greatest number of currently spellable blocked words. Ties use the
        lexicographically greatest folded character. Words longer than the
        minimum identifier length of the current alphabet cannot occur and do
        not affect removal.

        Returns:
            The surviving characters in their original order.

        """

        def prune(alphabet_set: set[str]) -> set[str]:
            if len(alphabet_set) <= 1:
                msg = "blocklist leaves insufficient alphabet characters"
                raise ValueError(msg)

            length = cls._required_length(bits, len(alphabet_set))

            alphabet_lower = {c.casefold() for c in alphabet_set}
            counts: dict[str, int] = defaultdict(int)
            for word in blocklist:
                if len(word) > length:
                    # Not an issue anyways
                    continue
                word_alphabet = set(word)
                if word_alphabet <= alphabet_lower:
                    for c in word_alphabet:
                        counts[c] += 1

            if not counts:
                return alphabet_set

            remove = max(counts, key=lambda c: (counts[c], c))
            alphabet_set = {c for c in alphabet_set if c.casefold() != remove}
            return prune(alphabet_set)

        reduced_alphabet = prune(set(alphabet))
        return "".join(c for c in alphabet if c in reduced_alphabet)
