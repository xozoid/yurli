from __future__ import annotations

import pytest

from yurli._impl.blocklist import _FALLBACK_PREFIXES, BlocklistEncoder
from yurli._impl.encoding import DEFAULT_ALPHABET, AlphabetEncoder

DEFAULT_PREFIX = _FALLBACK_PREFIXES[0]
MAX_16B = (1 << 16) - 1


def test_empty_blocklist_uses_normal_fixed_width_encoding() -> None:
    encoder = BlocklistEncoder(bits=16)

    identifier = encoder.encode(0)

    assert identifier == "0000"
    assert encoder.decode(identifier) == 0


@pytest.mark.parametrize("alphabet", ["01", "0123", "abc123"])
@pytest.mark.parametrize(
    ("id_normal", "id_fallback"),
    [
        (0, 1),
        (1, 0),
        (0, 37),
        (37, 0),
        (0, MAX_16B),
        (MAX_16B, 0),
    ],
)
def test_custom_alphabet_is_used_for_normal_and_fallback_identifiers(
    alphabet: str,
    id_normal: int,
    id_fallback: int,
) -> None:
    blocked = AlphabetEncoder(bits=16, alphabet=alphabet).encode(id_fallback)
    encoder = BlocklistEncoder(
        bits=16,
        # Pad by one because blocklist will make the length 1 longer than minimum
        blocklist={alphabet[0] + blocked},
        alphabet=alphabet,
    )

    uri_normal = encoder.encode(id_normal)
    uri_fallback = encoder.encode(id_fallback)

    assert not uri_normal.startswith(DEFAULT_PREFIX)
    assert set(uri_normal) <= set(alphabet)
    assert uri_fallback.startswith(DEFAULT_PREFIX)
    assert set(uri_fallback[1:]) <= set(alphabet)

    assert encoder.decode(uri_normal) == id_normal
    assert encoder.decode(uri_fallback) == id_fallback


def test_fallback_prefix_is_selected_outside_a_custom_alphabet() -> None:
    encoder = BlocklistEncoder(bits=16, alphabet="0" + DEFAULT_PREFIX)
    assert encoder.fallback_prefix == _FALLBACK_PREFIXES[1]


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


@pytest.mark.parametrize(
    ("i", "block"),
    [(i, f"{i:{fmt}}") for i in range(16) for fmt in ("x", "02x", "X", "02X")],
)
def test_blocklisted_hexadecimal_forms_use_fallback(i: int, block: str) -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={block})

    identifier = encoder.encode(i)

    assert identifier.startswith(DEFAULT_PREFIX)
    assert block.casefold() not in identifier.casefold()
    assert encoder.decode(identifier) == i


def test_fallback_blocks_substrings_across_the_prefix_boundary() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"0000", "-0"})

    identifier = encoder.encode(0)

    assert identifier.startswith(DEFAULT_PREFIX)
    assert "-0" not in identifier.casefold()
    assert encoder.decode(identifier) == 0


def test_fallback_namespace_is_disjoint_from_normal_base62_namespace() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"000"})

    fallback_identifier = encoder.encode(0)
    normal_identifier = encoder.encode(62)

    assert fallback_identifier.startswith(DEFAULT_PREFIX)
    assert normal_identifier[0] in DEFAULT_ALPHABET


@pytest.mark.slow
def test_16_bit_domain_is_unique_reversible_and_blocklist_free() -> None:
    blocklist = {"0", "a", "-z"}
    encoder = BlocklistEncoder(bits=16, blocklist=blocklist)

    identifiers = [encoder.encode(value) for value in range(1 << 16)]
    unsafe = [
        identifier
        for identifier in identifiers
        if any(entry in identifier.casefold() for entry in blocklist)
    ]

    assert len(set(identifiers)) == 1 << 16
    assert not unsafe, f"{len(unsafe)} unsafe identifiers; first 10: {unsafe[:10]}"
    decoded_values = [encoder.decode(identifier) for identifier in identifiers]

    assert decoded_values == list(range(1 << 16))


def test_empty_blocklist_entry_is_rejected() -> None:
    with pytest.raises(ValueError, match="blocklist"):
        BlocklistEncoder(bits=16, blocklist=[""])


@pytest.mark.parametrize("prefix", ["a", "--", "!"])
def test_invalid_fallback_prefix_is_rejected(prefix: str) -> None:
    with pytest.raises(ValueError, match="fallback_prefix"):
        BlocklistEncoder(bits=16, fallback_prefix=prefix)


def test_blocklist_with_no_safe_fallback_capacity_is_rejected() -> None:
    with pytest.raises(ValueError, match="capacity"):
        BlocklistEncoder(bits=16, blocklist=set(DEFAULT_ALPHABET))


def test_decode_rejects_blocklisted_normal_identifier() -> None:
    encoder = BlocklistEncoder(bits=16, blocklist={"000"})

    with pytest.raises(ValueError, match="blocklisted"):
        encoder.decode("0000")
