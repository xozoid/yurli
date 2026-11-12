"""Shared identifier and blocklist constants."""

from __future__ import annotations

from pathlib import Path

DEFAULT_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

_EXAMPLE_BLOCKLIST_FILE = Path(__file__).with_name("blocklist.txt")
EXAMPLE_BLOCKLIST = set(
    _EXAMPLE_BLOCKLIST_FILE.read_text(encoding="utf-8").splitlines(),
)
