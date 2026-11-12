from __future__ import annotations

import pytest

from yurli._impl.blocklist import BlocklistEncoder
from yurli.constants import DEFAULT_ALPHABET


@pytest.mark.parametrize("entry", ["bad", "curse", "offensive"])
def test_custom_blocklist_entries_never_appear_in_generated_identifiers(
    entry: str,
) -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={entry})

    identifiers = [encoder.encode(value) for value in range(1 << 16)]
    unsafe = [
        identifier
        for identifier in identifiers
        if entry.casefold() in identifier.casefold()
    ]

    assert not unsafe, f"{len(unsafe)} unsafe identifiers; first 10: {unsafe[:10]}"


def test_casefolded_substring_uses_fallback() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"a"})

    identifier = encoder.encode(5)

    assert "a" not in identifier.casefold()
    assert encoder.decode(identifier) == 5


def test_16_bit_domain_is_unique_reversible_and_blocklist_free() -> None:
    blocklist = {"0", "a"}
    encoder = BlocklistEncoder(bits=16, blocklist=blocklist)

    identifiers = [encoder.encode(value) for value in range(1 << 16)]
    unsafe = [
        identifier
        for identifier in identifiers
        if any(entry in identifier.casefold() for entry in blocklist)
    ]
    decoded_values = [encoder.decode(identifier) for identifier in identifiers]

    assert len(set(identifiers)) == 1 << 16
    assert not unsafe, f"{len(unsafe)} unsafe identifiers; first 10: {unsafe[:10]}"
    assert decoded_values == list(range(1 << 16))


def test_empty_blocklist_entry_is_rejected() -> None:
    with pytest.raises(ValueError, match="blocklist"):
        BlocklistEncoder(bits=16, blocklist=[""])


def test_blocklist_with_no_safe_alphabet_is_rejected() -> None:
    with pytest.raises(ValueError, match="insufficient"):
        BlocklistEncoder(bits=16, blocklist=set(DEFAULT_ALPHABET))


@pytest.mark.parametrize(
    ("alphabet", "blocklist", "expected"),
    [
        pytest.param(DEFAULT_ALPHABET, set(), DEFAULT_ALPHABET, id="empty-blocklist"),
        pytest.param("abcd", {"xyz"}, "abcd", id="block-out-of-domain"),
        pytest.param("abcd", {"a"}, "bcd", id="block-single-character"),
        pytest.param("abcd", {"a", "b"}, "cd", id="block-multiple-single-characters"),
        pytest.param("abcdef", {"abc", "ade"}, "bcdef", id="single-removal"),
        pytest.param("abcd", {"aaa"}, "bcd", id="repeated-character-block"),
        pytest.param("abcdef", {"abc", "def"}, "abde", id="independent-substrings"),
    ],
)
def test_alphabet_reduces(
    alphabet: str,
    blocklist: set[str],
    expected: str,
) -> None:
    result = BlocklistEncoder._prune_alphabet(16, blocklist, alphabet)
    assert result == expected


@pytest.mark.parametrize(
    ("alphabet", "blocklist", "expected_length"),
    [
        ("abcdef", {"abc", "abe", "abf"}, 5),
        ("abcdef", {"abc", "abcd"}, 5),
        ("abcdef", {"abc", "def"}, 4),
        ("abcdef", {"abc", "bcd", "cde"}, 5),
        ("abcdefgh", {"bad", "cab", "fade"}, 7),
    ],
)
def test_prune_alphabet_finds_maximum_safe_subset(
    alphabet: str,
    blocklist: set[str],
    expected_length: int,
) -> None:
    result = BlocklistEncoder._prune_alphabet(16, blocklist, alphabet)

    assert len(result) == expected_length
    assert all(char in alphabet for char in result)
    assert result == "".join(char for char in alphabet if char in result)

    available = {char.casefold() for char in result}
    assert all(not set(word.casefold()) <= available for word in blocklist)
