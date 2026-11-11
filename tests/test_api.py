from __future__ import annotations

from importlib.metadata import version

import pytest

from yurli import (
    EXAMPLE_BLOCKLIST,
    IntegerWidth,
    RoundKeys,
    __version__,
    types,
)
from yurli.api import Yurli


def test_example_blocklist_is_empty() -> None:
    assert set() == EXAMPLE_BLOCKLIST


def test_package_version_is_exported() -> None:
    assert __version__ == version("yurli")


@pytest.mark.parametrize(
    ("package_type", "module_type"),
    [
        (IntegerWidth, types.IntegerWidth),
        (RoundKeys, types.RoundKeys),
    ],
)
def test_public_types_are_reexported(
    package_type: object,
    module_type: object,
) -> None:
    assert package_type is module_type


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
