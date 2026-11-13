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

    def to_kwargs(self) -> YurliConfig:
        """Return all settings needed to reconstruct this codec with kwargs."""
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
            self.to_kwargs(),
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
        try:
            decoded = data.decode("utf-8")
        except (AttributeError, UnicodeDecodeError) as error:
            msg = "config must be valid UTF-8"
            raise ValueError(msg) from error
        try:
            parsed: object = json.loads(decoded)
        except json.JSONDecodeError as error:
            msg = "config must be valid UTF-8 JSON"
            raise ValueError(msg) from error

        return cls(**cls._configuration_from_json(parsed))

    @classmethod
    def _configuration_from_json(cls, raw: dict[str, object] | object) -> YurliConfig:
        """Restore a codec from :meth:`to_bytes` output.

        Returns:
            A codec with the serialized mapping.

        Raises:
            TypeError: If a config field has an invalid type.
            ValueError: If the config is malformed or unsupported.
        """
        if not isinstance(raw, dict) or frozenset(raw) != YurliConfig.__required_keys__:
            msg = f"config must be a JSON object with {YurliConfig.__required_keys__}"
            raise ValueError(msg)

        j = cast("YurliConfig", raw)

        round_keys = j.pop("round_keys")
        if not isinstance(round_keys, Sequence) or len(round_keys) != ROUND_COUNT:
            msg = f"config round_keys must be list of {ROUND_COUNT} integer values"
            raise ValueError(msg)
        try:
            j["round_keys"] = (
                int(round_keys[0]),
                int(round_keys[1]),
                int(round_keys[2]),
                int(round_keys[3]),
            )
        except (TypeError, ValueError) as error:
            msg = f"config round_keys must be list of {ROUND_COUNT} integer values"
            raise ValueError(msg) from error

        bits = j["bits"]
        if bits not in SUPPORTED_BITS:
            msg = f"config bits must be one of {SUPPORTED_BITS}"
            raise ValueError(msg)

        try:
            j["alphabet"] = str(j["alphabet"])
        except (TypeError, ValueError) as error:
            msg = "config has invalid alphabet"
            raise TypeError(msg) from error

        try:
            j["identifier_length"] = int(j["identifier_length"])
        except (TypeError, ValueError) as error:
            msg = "config has invalid identifier length"
            raise TypeError(msg) from error

        try:
            j["format_version"] = ConfigVersion(j["format_version"])
            j["algorithm_version"] = PermutationVersion(j["algorithm_version"])
        except (TypeError, ValueError) as error:
            msg = "config has invalid version"
            raise TypeError(msg) from error

        return j
