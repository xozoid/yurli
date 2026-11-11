from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def pytest_make_parametrize_id(
    config: pytest.Config,
    val: Iterable[object] | Decimal | Path | object,
    argname: str,
) -> str | None:
    if isinstance(val, dt.date):
        return val.isoformat()
    if isinstance(val, Iterable | Decimal | Path):
        return str(val)
    if callable(val):
        return val.__name__
    return None
