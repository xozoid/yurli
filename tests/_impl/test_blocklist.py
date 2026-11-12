from __future__ import annotations

import pytest

from yurli._impl.blocklist import BlocklistEncoder
from yurli._impl.encoding import DEFAULT_ALPHABET, AlphabetEncoder


def _parity(identifier: str, alphabet: str = DEFAULT_ALPHABET) -> int:
    return sum(alphabet.index(character) for character in identifier) % 2


def test_empty_blocklist_uses_even_parity_normal_identifier() -> None:
    encoder = BlocklistEncoder(bits=16)

    identifier = encoder.encode(0)

    assert identifier == "000"
    assert _parity(identifier) == 0
    assert encoder.decode(identifier) == 0


@pytest.mark.xfail(reason="blocklist not implemented")
def test_blocklisted_normal_identifier_uses_odd_parity_fallback() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"000"})

    identifier = encoder.encode(0)

    assert identifier == "001"
    assert _parity(identifier) == 1
    assert encoder.decode(identifier) == 0


@pytest.mark.xfail(reason="blocklist not implemented")
@pytest.mark.parametrize("alphabet", ["01", "0123", "abc123"])
def test_custom_even_alphabet_is_used_for_both_parity_namespaces(alphabet: str) -> None:
    normal_length = AlphabetEncoder(bits=16, alphabet=alphabet).length + 1
    encoder = BlocklistEncoder(
        bits=16,
        blocklist={alphabet[0] * normal_length},
        alphabet=alphabet,
        length=normal_length,
    )

    normal_identifier = encoder.encode(1 << 15)
    fallback_identifier = encoder.encode(0)

    assert set(normal_identifier) <= set(alphabet)
    assert _parity(normal_identifier, alphabet) == 0
    assert set(fallback_identifier) <= set(alphabet)
    assert _parity(fallback_identifier, alphabet) == 1
    assert encoder.decode(normal_identifier) == 1 << 15
    assert encoder.decode(fallback_identifier) == 0


@pytest.mark.parametrize("alphabet", ["0ab", "012"])
def test_odd_length_alphabet_is_rejected(alphabet: str) -> None:
    with pytest.raises(ValueError, match="even"):
        BlocklistEncoder(bits=16, alphabet=alphabet)


@pytest.mark.xfail(reason="blocklist not implemented")
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


@pytest.mark.xfail(reason="blocklist not implemented")
def test_casefolded_substring_uses_fallback() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"a"})

    identifier = encoder.encode(5)

    assert _parity(identifier) == 1
    assert "a" not in identifier.casefold()
    assert encoder.decode(identifier) == 5


@pytest.mark.xfail(reason="blocklist not implemented")
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


@pytest.mark.xfail(reason="blocklist not implemented")
def test_blocklist_with_no_safe_fallback_capacity_is_rejected() -> None:
    with pytest.raises(ValueError, match="capacity"):
        BlocklistEncoder(bits=16, blocklist=set(DEFAULT_ALPHABET))


@pytest.mark.xfail(reason="blocklist not implemented")
def test_decode_rejects_blocklisted_even_parity_identifier() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"000"})

    with pytest.raises(ValueError, match="blocklisted"):
        encoder.decode("000")
