"""Public type aliases for yurli configuration."""

from __future__ import annotations

from typing import Literal

type IntegerWidth = Literal[16, 32, 64]
type RoundKeys = tuple[int, int, int, int]
