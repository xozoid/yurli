"""Collision-free, blocklist-safe fixed-width identifier encoding."""

from __future__ import annotations

from typing import TYPE_CHECKING, override
from urllib.parse import quote

from yurli._impl.encoding import DEFAULT_ALPHABET, AlphabetEncoder

if TYPE_CHECKING:
    from collections.abc import Iterable

    from yurli.types import IntegerWidth

_FALLBACK_PREFIXES = ("-", "_", "~")


class BlocklistEncoder(AlphabetEncoder):
    """Encode domain values without configured case-insensitive substrings.

    Normal alphabet identifiers are retained when allowed. Blocklisted normal
    identifiers use a fallback namespace beginning with a character outside
    the alphabet. The fallback suffix is rank/unrank encoded from the finite language
    of allowed strings, which is collision-free and always terminates after
    construction proves sufficient capacity.
    """

    @override
    def __init__(
        self,
        bits: IntegerWidth,
        blocklist: Iterable[str] = (),
        alphabet: str = DEFAULT_ALPHABET,
        fallback_prefix: str | None = None,
        length: int | None = None,
    ) -> None:
        """Create a blocklist-aware encoder.

        Args:
            bits: Width of the unsigned integer domain to encode.
            blocklist: Case-insensitive substrings that generated IDs forbid.
            alphabet: Ordered digits used for normal and fallback suffixes.
            fallback_prefix: Optional URL-safe prefix outside the alphabet.
            length: Optional fixed ID length.

        Raises:
            ValueError: If the configuration is invalid or lacks fallback capacity.
        """
        super().__init__(bits, alphabet, length=length)

        self._blocklist = self._normalize_blocklist(blocklist)
        self._states = self._build_states()
        self._transitions = self._build_transitions()

        self._fallback_prefix = self._select_fallback_prefix(
            _FALLBACK_PREFIXES if fallback_prefix is None else (fallback_prefix,),
        )
        prefix_state = self._advance("", self._fallback_prefix)
        if prefix_state is None:
            msg = "fallback_prefix contains a blocklisted substring"
            raise ValueError(msg)
        self._prefix_state = prefix_state

        self._completion_counts: dict[tuple[str, int], int] = {}
        if length is None:
            # Update length given minimum length from AlphabetEncoder
            self._length = self._find_identifier_length(self._length)
        elif (
            self._completion_count(self._prefix_state, self._suffix_length)
            < self._max_value
        ):
            # Check the provide length is sufficient
            msg = "blocklist leaves insufficient fallback identifier capacity"
            raise ValueError(msg)

    @property
    def blocklist(self) -> frozenset[str]:
        """Normalized forbidden substrings."""
        return self._blocklist

    @property
    def fallback_prefix(self) -> str:
        """Prefix that separates fallback identifiers from normal identifiers."""
        return self._fallback_prefix

    @override
    def encode(self, value: int, /) -> str:
        normal_identifier = super().encode(value)
        if self._is_allowed(normal_identifier):
            return normal_identifier
        return self._fallback_prefix + self._unrank(value)

    @override
    def decode(self, identifier: str, /) -> int:
        if len(identifier) != self._length:
            msg = f"identifier must contain exactly {self._length} characters"
            raise ValueError(msg)
        if identifier.startswith(self._fallback_prefix):
            return self._rank(identifier[1:])
        if not self._is_allowed(identifier):
            msg = "identifier contains a blocklisted substring"
            raise ValueError(msg)
        return super().decode(identifier)

    @property
    def _suffix_length(self) -> int:
        """Length of a fallback suffix after its single-character prefix."""
        return self._length - 1

    def _find_identifier_length(self, minimum_length: int) -> int:
        """Find the shortest length whose fallback language covers the domain.

        Returns:
            A fixed identifier length with sufficient fallback capacity.

        Raises:
            ValueError: If no suitable fallback length exists.
        """
        length = minimum_length
        while length <= minimum_length + self._bits + 1:
            suffix_length = length - 1
            capacity = self._completion_count(self._prefix_state, suffix_length)
            if capacity >= self._max_value:
                return length
            length += 1

        msg = "blocklist leaves insufficient fallback identifier capacity"
        raise ValueError(msg)

    def _select_fallback_prefix(self, prefixes: tuple[str, ...]) -> str:
        """Select and validate the fallback namespace prefix.

        Returns:
            A URL-safe character outside the normal alphabet namespace.

        Raises:
            ValueError: If no safe supported prefix is available.
        """
        for prefix in prefixes:
            if self._is_valid_prefix(prefix) and self._advance("", prefix) is not None:
                return prefix
        msg = "fallback_prefix must be one URL-safe character outside the alphabet"
        raise ValueError(msg)

    def _is_valid_prefix(self, prefix: str) -> bool:
        """Return whether a prefix separates the fallback namespace."""
        return (
            len(prefix) == 1
            and quote(prefix, safe="") == prefix
            and prefix not in self.alphabet
        )

    def _normalize_blocklist(self, blocklist: Iterable[str]) -> frozenset[str]:
        """Validate and casefold forbidden substrings.

        Returns:
            Deduplicated, casefolded forbidden substrings.

        Raises:
            ValueError: If an entry is empty.
        """
        normalized = frozenset(entry.casefold() for entry in blocklist)
        if "" in normalized:
            msg = "blocklist entries must not be empty"
            raise ValueError(msg)
        output_characters = frozenset(
            character.casefold()
            for character in self.alphabet + "".join(_FALLBACK_PREFIXES)
        )
        return frozenset(
            entry
            for entry in normalized
            if all(character in output_characters for character in entry)
        )

    def _build_states(self) -> frozenset[str]:
        """Build automaton states from all proper prefixes of blocked words.

        Returns:
            All suffixes that can begin a later blocked substring.
        """
        # A state is the longest ending text that could still complete a blocked word.
        states = {""}
        for word in self._blocklist:
            states.update(
                word[:prefix_length]
                for prefix_length in range(len(word))
                if word[:prefix_length] not in self._blocklist
            )
        return frozenset(states)

    def _is_allowed(self, identifier: str) -> bool:
        """Return whether an identifier contains no forbidden substring."""
        state = self._advance("", identifier)
        return state is not None

    def _build_transitions(self) -> dict[tuple[str, str], str | None]:
        """Build a transition table for every output character and state.

        Returns:
            The next state, or ``None`` where a transition completes a blocked word.
        """
        characters = frozenset(
            character.casefold()
            for character in self.alphabet + "".join(_FALLBACK_PREFIXES)
        )
        return {
            (state, character): self._next_state(state, character)
            for state in self._states
            for character in characters
        }

    def _next_state(self, state: str, character: str) -> str | None:
        """Return the next state without scanning all blocklist entries.

        Returns:
            The longest relevant suffix, or ``None`` for a blocked transition.
        """
        candidate = state + character.casefold()
        while candidate:
            if candidate in self._blocklist:
                return None
            if candidate in self._states:
                return candidate
            candidate = candidate[1:]
        return ""

    def _advance(self, state: str, characters: str) -> str | None:
        """Advance the substring automaton or return ``None`` when blocked.

        Returns:
            The next suffix state, or ``None`` for a forbidden string.
        """
        for character in characters.casefold():
            next_state = self._transitions[state, character]
            if next_state is None:
                return None
            state = next_state
        return state

    def _completion_count(self, state: str, remaining: int) -> int:
        """Count allowed suffixes from one automaton state.

        Returns:
            The count of blocklist-safe suffixes with the requested length.
        """
        key = (state, remaining)
        # This LUT holds counts by state and length, never individual fallback IDs.
        if key not in self._completion_counts:
            if remaining == 0:
                self._completion_counts[key] = 1
            else:
                self._completion_counts[key] = sum(
                    self._completion_count(next_state, remaining - 1)
                    for character in self.alphabet
                    if (next_state := self._advance(state, character)) is not None
                )
        return self._completion_counts[key]

    def _unrank(self, rank: int) -> str:
        """Return the allowed fallback suffix for one domain value.

        Returns:
            The safe suffix at the requested lexicographic rank.

        Raises:
            ValueError: If the rank exceeds fallback capacity.
        """
        state = self._prefix_state
        characters: list[str] = []
        for remaining in range(self._suffix_length, 0, -1):
            for character in self.alphabet:
                next_state = self._advance(state, character)
                if next_state is None:
                    continue
                count = self._completion_count(next_state, remaining - 1)
                if rank < count:
                    characters.append(character)
                    state = next_state
                    break
                rank -= count
            else:
                msg = "rank is outside the fallback identifier space"
                raise ValueError(msg)
        return "".join(characters)

    def _rank(self, suffix: str) -> int:
        """Return the domain value represented by an allowed fallback suffix.

        Returns:
            The suffix's lexicographic rank.

        Raises:
            ValueError: If the suffix is malformed, blocked, or outside the domain.
        """
        rank = 0
        state = self._prefix_state
        if len(suffix) != self._suffix_length:
            msg = "identifier has an invalid fallback suffix length"
            raise ValueError(msg)
        for index, character in enumerate(suffix):
            try:
                character_index = self.alphabet.index(character)
            except ValueError as error:
                msg = "identifier contains a character outside the fallback alphabet"
                raise ValueError(msg) from error
            remaining = self._suffix_length - index - 1
            for earlier_character in self.alphabet[:character_index]:
                earlier_state = self._advance(state, earlier_character)
                if earlier_state is not None:
                    rank += self._completion_count(earlier_state, remaining)
            next_state = self._advance(state, character)
            if next_state is None:
                msg = "identifier contains a blocklisted substring"
                raise ValueError(msg)
            state = next_state
        if rank >= self._max_value:
            msg = "identifier is outside the configured domain"
            raise ValueError(msg)
        return rank
