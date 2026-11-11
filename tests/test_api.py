from __future__ import annotations

from importlib.metadata import version

import pytest

from yurli import (
    EXAMPLE_BLOCKLIST,
    ConfigurationFormatVersion,
    PermutationAlgorithmVersion,
    __version__,
)
from yurli.api import Yurli


def test_example_blocklist_is_empty() -> None:
    assert set() == EXAMPLE_BLOCKLIST


def test_package_version_is_exported() -> None:
    assert __version__ == version("yurli")


def test_configuration_versions_are_integer_enums() -> None:
    assert isinstance(ConfigurationFormatVersion.V1, ConfigurationFormatVersion)
    assert isinstance(
        PermutationAlgorithmVersion.FEISTEL_4_ROUND_V1,
        PermutationAlgorithmVersion,
    )
    assert ConfigurationFormatVersion.V1 == 1
    assert PermutationAlgorithmVersion.FEISTEL_4_ROUND_V1 == 1


def test_constructor_is_a_stub() -> None:
    with pytest.raises(NotImplementedError):
        Yurli()


@pytest.mark.parametrize(
    ("method_name", "arguments"),
    [
        ("encode", (0,)),
        ("decode", ("000000000000",)),
        ("to_kwargs", ()),
        ("to_bytes", ()),
    ],
)
def test_instance_methods_are_stubs(
    method_name: str,
    arguments: tuple[object, ...],
) -> None:
    codec = object.__new__(Yurli)

    with pytest.raises(NotImplementedError):
        getattr(codec, method_name)(*arguments)


def test_from_bytes_is_a_stub() -> None:
    with pytest.raises(NotImplementedError):
        Yurli.from_bytes(b"")
