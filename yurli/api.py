"""Public classes and example data for the yurli package."""

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Self, TypedDict, Unpack

if TYPE_CHECKING:
    from yurli.types import IntegerWidth, RoundKeys


class ConfigurationFormatVersion(IntEnum):
    """Version of the serialized configuration format."""

    V1 = 1


class PermutationAlgorithmVersion(IntEnum):
    """Version of the integer permutation algorithm."""

    FEISTEL_4_ROUND_V1 = 1


class YurliConfig(TypedDict, total=False):
    """Persisted settings accepted by :class:`Yurli`."""

    format_version: ConfigurationFormatVersion
    algorithm_version: PermutationAlgorithmVersion
    bits: IntegerWidth
    round_keys: RoundKeys
    blocklist: set[str]
    fallback_prefix: str
    identifier_length: int


class Yurli:
    """Create reversible, fixed-width identifiers for unsigned integers.

    A new instance generates a random permutation configuration unless all
    persisted settings are provided. Save :meth:`to_bytes` and restore it with
    :meth:`from_bytes` to decode identifiers after a process restart.

    Args:
        configuration: Optional persisted configuration fields. With no
            fields, the implementation will use a 64-bit domain and an empty
            blocklist.
    """

    def __init__(self, **configuration: Unpack[YurliConfig]) -> None:
        """Create a codec from settings or generate a new configuration."""
        raise NotImplementedError

    def encode(self, value: int, /) -> str:
        """Encode an unsigned integer as a fixed-length identifier."""
        raise NotImplementedError

    def decode(self, identifier: str, /) -> int:
        """Decode an identifier created with this codec's configuration."""
        raise NotImplementedError

    def to_kwargs(self) -> YurliConfig:
        """Return all settings needed to reconstruct this codec with kwargs."""
        raise NotImplementedError

    def to_bytes(self) -> bytes:
        """Serialize this codec's versioned configuration."""
        raise NotImplementedError

    @classmethod
    def from_bytes(cls, data: bytes, /) -> Self:
        """Restore a codec from :meth:`to_bytes` output."""
        raise NotImplementedError
