from __future__ import annotations

import pytest

from yurli._impl.blocklist import BlocklistEncoder
from yurli._impl.encoding import AlphabetEncoder
from yurli.constants import DEFAULT_ALPHABET


@pytest.mark.parametrize("entry", ["bad", "curse", "offensive"])
def test_custom_blocklist_entries_never_appear_in_generated_identifiers(
    entry: str,
) -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={entry})

    identifiers = [encoder.encode(value) for value in range(1 << 16)]
    unsafe = [
        identifier for identifier in identifiers if entry.lower() in identifier.lower()
    ]

    assert not unsafe, f"{len(unsafe)} unsafe identifiers; first 10: {unsafe[:10]}"


def test_case_insensitive_substring_is_excluded() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"A"})

    identifier = encoder.encode(5)

    assert "a" not in identifier.lower()
    assert encoder.decode(identifier) == 5


def test_16_bit_domain_is_unique_reversible_and_blocklist_free() -> None:
    blocklist = {"0", "a"}
    encoder = BlocklistEncoder(bits=16, blocklist=blocklist)

    identifiers = [encoder.encode(value) for value in range(1 << 16)]
    unsafe = [
        identifier
        for identifier in identifiers
        if any(entry in identifier.lower() for entry in blocklist)
    ]
    decoded_values = [encoder.decode(identifier) for identifier in identifiers]

    assert len(set(identifiers)) == 1 << 16
    assert not unsafe, f"{len(unsafe)} unsafe identifiers; first 10: {unsafe[:10]}"
    assert decoded_values == list(range(1 << 16))


@pytest.mark.parametrize(
    "blocklist",
    [
        pytest.param((), id="empty-iterable"),
        pytest.param(("",), id="only-empty-entry"),
        pytest.param(("bad", ""), id="mixed-empty-entry"),
    ],
)
def test_empty_blocklist_entries_are_rejected(blocklist: tuple[str, ...]) -> None:
    with pytest.raises(
        ValueError,
        match="blocklist must contain at least one non-empty entry",
    ):
        BlocklistEncoder(bits=16, blocklist=blocklist)


def test_generator_blocklist_is_supported() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist=(word for word in ("bad",)))
    assert encoder.blocklist == frozenset({"bad"})


@pytest.mark.parametrize(
    ("alphabet", "blocklist"),
    [
        pytest.param("abé", {"bad"}, id="non-ascii-alphabet"),
        pytest.param("abcd", {"café"}, id="non-ascii-blocklist"),
    ],
)
def test_non_ascii_blocklist_configuration_is_rejected(
    alphabet: str,
    blocklist: set[str],
) -> None:
    with pytest.raises(ValueError, match="ASCII"):
        BlocklistEncoder(bits=16, alphabet=alphabet, blocklist=blocklist)


def test_alphabet_encoder_rejects_non_ascii_alphabet() -> None:
    with pytest.raises(ValueError, match="alphabet must contain only ASCII characters"):
        AlphabetEncoder(bits=16, alphabet="abé")


def test_duplicate_alphabet_is_rejected_before_pruning() -> None:
    with pytest.raises(
        ValueError,
        match="alphabet must not contain duplicate characters",
    ):
        BlocklistEncoder(bits=16, alphabet="aabc", blocklist={"xyz"})


def test_mixed_case_custom_alphabet_is_preserved() -> None:
    encoder = BlocklistEncoder(bits=16, alphabet="aAbBcC", blocklist={"xyz"})

    assert encoder.alphabet == "aAbBcC"


def test_case_insensitive_pruning_removes_both_case_variants() -> None:
    encoder = BlocklistEncoder(bits=16, alphabet="dCaAbB", blocklist={"A"})

    assert encoder.alphabet == "dCbB"


@pytest.mark.parametrize(
    ("alphabet", "blocklist", "expected"),
    [
        pytest.param(
            DEFAULT_ALPHABET,
            set[str](),
            DEFAULT_ALPHABET,
            id="empty-blocklist",
        ),
        pytest.param("dCbA", {"xyz"}, "dCbA", id="irrelevant-entry"),
        pytest.param("abcd", {"a"}, "bcd", id="single-character"),
        pytest.param("abcd", {"a", "b"}, "cd", id="multiple-single-characters"),
        pytest.param("abcdef", {"abc", "ade"}, "bcdef", id="overlapping-substrings"),
        pytest.param("abcd", {"aaa"}, "bcd", id="repeated-character"),
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


def test_explicit_length_prunes_entries_that_fit_configured_identifier() -> None:
    encoder = BlocklistEncoder(
        bits=16,
        alphabet="abcd",
        blocklist={"aaaaaaaaa"},
        length=9,
    )

    assert "a" not in encoder.alphabet
    assert encoder.encode(0) != "aaaaaaaaa"
    assert encoder.length == 11


def test_entry_longer_than_actual_identifier_does_not_prune_alphabet() -> None:
    encoder = BlocklistEncoder(
        bits=16,
        alphabet="abcd",
        blocklist={"aaaaaaaaa"},
    )

    assert encoder.alphabet == "abcd"
    assert encoder.length == 8


def test_explicit_length_shorter_than_original_minimum_is_rejected() -> None:
    with pytest.raises(ValueError, match="length must be at least 8"):
        BlocklistEncoder(
            bits=16,
            alphabet="abcd",
            blocklist={"xyz"},
            length=7,
        )


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
def test_prune_alphabet_produces_safe_subset(
    alphabet: str,
    blocklist: set[str],
    expected_length: int,
) -> None:
    result = BlocklistEncoder._prune_alphabet(16, blocklist, alphabet)

    assert len(result) == expected_length
    assert all(character in alphabet for character in result)
    assert result == "".join(character for character in alphabet if character in result)

    available = {character.lower() for character in result}
    assert all(not set(word.lower()) <= available for word in blocklist)


def test_greedy_pruning_can_be_suboptimal() -> None:
    alphabet = "abcdef"
    blocklist = {"ab", "ad", "cd", "ce"}

    result = BlocklistEncoder._prune_alphabet(16, blocklist, alphabet)

    assert result == "acf"
    assert len(result) == 3
    assert all(not set(word) <= set(result) for word in blocklist)


def test_blocklist_with_no_safe_alphabet_is_rejected() -> None:
    with pytest.raises(ValueError, match="insufficient"):
        BlocklistEncoder(bits=16, blocklist=set(DEFAULT_ALPHABET))
