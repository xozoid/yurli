"""Public classes and example data for the yurli package."""

from __future__ import annotations

import json
from collections.abc import Sequence
from enum import IntEnum
from typing import TYPE_CHECKING, Self, TypedDict, cast

from yurli._impl.encoding import AlphabetEncoder
from yurli._impl.permutation import IntegerPermutation
from yurli.constants import DEFAULT_ALPHABET, ROUND_COUNT, SUPPORTED_BITS

if TYPE_CHECKING:
    from collections.abc import Iterable

    from yurli.types import IntegerWidth, RoundKeys


class ConfigVersion(IntEnum):
    """Version of the serialized configuration format."""

    V1 = 1


class PermutationVersion(IntEnum):
    """Version of the integer permutation algorithm."""

    FEISTEL_4_ROUND_V1 = 1


class YurliConfig(TypedDict):
    """Persisted settings accepted by :class:`Yurli`."""

    format_version: ConfigVersion
    algorithm_version: PermutationVersion
    bits: IntegerWidth
    round_keys: RoundKeys
    alphabet: str
    identifier_length: int


class Yurli:
    """Create reversible, fixed-width identifiers for unsigned integers.

    A new instance generates a random permutation configuration unless all
    persisted settings are provided. Save :meth:`to_bytes` and restore it with
    :meth:`from_bytes` to decode identifiers after a process restart.

    Changing any persisted setting changes the mapping. Save :meth:`to_bytes`
    and restore it with :meth:`from_bytes` to keep existing identifiers valid.
    """

    def __init__(  # ruff: ignore[too-many-arguments]
        self,
        *,
        bits: IntegerWidth = 64,
        alphabet: str = DEFAULT_ALPHABET,
        blocklist: Iterable[str] = (),
        round_keys: RoundKeys | None = None,
        identifier_length: int | None = None,
        format_version: ConfigVersion = ConfigVersion.V1,
        algorithm_version: PermutationVersion = PermutationVersion.FEISTEL_4_ROUND_V1,
    ) -> None:
        """Create a codec from settings or generate a new configuration.

        Args:
            bits: Width of the unsigned integer domain. Defaults to 64.
            alphabet: Candidate positional alphabet. It is pruned when a blocklist
                is supplied.
            blocklist: Case-insensitive substrings made impossible in generated
                identifiers. It is not persisted; the resulting alphabet is.
            round_keys: Optional permutation keys used to restore a mapping.
            identifier_length: Optional fixed identifier length.
            format_version: Serialized configuration version to accept.
            algorithm_version: Integer permutation algorithm version to accept.

        Raises:
            ValueError: If a version or delegated configuration is invalid.
        """
        if format_version is not ConfigVersion.V1:
            msg = "unsupported configuration format version"
            raise ValueError(msg)
        if algorithm_version is not PermutationVersion.FEISTEL_4_ROUND_V1:
            msg = "unsupported permutation algorithm version"
            raise ValueError(msg)

        self._permutation = IntegerPermutation(bits, round_keys)
        self._encoder = AlphabetEncoder(bits, alphabet, identifier_length, blocklist)

    def encode(self, value: int, /) -> str:
        """Encode an unsigned integer as a fixed-length identifier.

        Returns:
            The configured fixed-length identifier.
        """
        return self._encoder.encode(self._permutation.permute(value))

    def decode(self, identifier: str, /) -> int:
        """Decode an identifier created with this codec's configuration.

        Returns:
            The original unsigned integer.
        """
        return self._permutation.invert(self._encoder.decode(identifier))

    @property
    def config(self) -> YurliConfig:
        """Configuration used to construct this codec."""
        return {
            "format_version": ConfigVersion.V1,
            "algorithm_version": PermutationVersion.FEISTEL_4_ROUND_V1,
            "bits": self._permutation.bits,
            "round_keys": self._permutation.round_keys,
            "alphabet": self._encoder.alphabet,
            "identifier_length": self._encoder.length,
        }

    def to_bytes(self) -> bytes:
        """Serialize this codec's versioned configuration.

        Returns:
            Deterministic UTF-8 JSON configuration bytes.
        """
        return json.dumps(
            self.config,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()

    @classmethod
    def from_bytes(cls, data: bytes, /) -> Self:
        """Restore a codec from :meth:`to_bytes` output.

        Returns:
            A codec with the serialized mapping.

        Raises:
            ValueError: If the configuration is malformed or unsupported.
        """
        j = cls._bytes_to_dict(data)
        if frozenset(j) != YurliConfig.__required_keys__:
            msg = f"config must be a JSON object with {YurliConfig.__required_keys__}"
            raise ValueError(msg)

        return cls(
            bits=cls._validate_bits(j, "bits"),
            alphabet=cls._validate_str(j, "alphabet"),
            round_keys=cls._validate_round_keys(j, "round_keys"),
            identifier_length=cls._validate_int(j, "identifier_length"),
            format_version=cls._validate_enum(j, "format_version", ConfigVersion),
            algorithm_version=cls._validate_enum(
                j,
                "algorithm_version",
                PermutationVersion,
            ),
        )

    @classmethod
    def _bytes_to_dict(cls, data: bytes) -> dict[str, object]:
        try:
            decoded = data.decode("utf-8")
        except (AttributeError, UnicodeDecodeError) as error:
            msg = "config must be valid UTF-8"
            raise ValueError(msg) from error
        try:
            j: dict[str, object] | object = json.loads(decoded)
        except json.JSONDecodeError as error:
            msg = "config must be valid UTF-8 JSON"
            raise ValueError(msg) from error
        if not isinstance(j, dict) or not all(isinstance(k, str) for k in j):
            msg = f"config must be a JSON object with {YurliConfig.__required_keys__}"
            raise ValueError(msg)
        return j

    @staticmethod
    def _validate_bits(j: dict[str, object], key: str) -> IntegerWidth:
        value = j[key]
        if not isinstance(value, int):
            msg = f"config.{key} must be an integer"
            raise ValueError(msg)  # ruff: ignore[type-check-without-type-error]
        if value not in SUPPORTED_BITS:
            msg = f"config.{key} must be one of {SUPPORTED_BITS}"
            raise ValueError(msg)
        return value

    @staticmethod
    def _validate_str(j: dict[str, object], key: str) -> str:
        value = j[key]
        if not isinstance(value, str):
            msg = f"config.{key} must be a string"
            raise ValueError(msg)  # ruff: ignore[type-check-without-type-error]
        return value

    @staticmethod
    def _validate_round_keys(j: dict[str, object], key: str) -> RoundKeys:
        value = j[key]
        if (
            not isinstance(value, Sequence)
            or len(value) != ROUND_COUNT
            or not all(isinstance(v, int) for v in value)
        ):
            msg = f"config.{key} must be a list of {ROUND_COUNT} integer values"
            raise ValueError(msg)
        return cast("RoundKeys", tuple(value))

    @staticmethod
    def _validate_int(j: dict[str, object], key: str) -> int:
        value = j[key]
        if not isinstance(value, int):
            msg = f"config.{key} must be an integer"
            raise ValueError(msg)  # ruff: ignore[type-check-without-type-error]
        return value

    @staticmethod
    def _validate_enum[T: IntEnum](j: dict[str, object], key: str, type_: type[T]) -> T:
        value = Yurli._validate_int(j, key)
        try:
            return type_(value)
        except ValueError as error:
            msg = f"config.{key} has an unknown version"
            raise ValueError(msg) from error
